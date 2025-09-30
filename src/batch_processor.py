"""
Main batch processor for ChatGPT labeling
"""
import pandas as pd
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from tqdm import tqdm

from src.data_processor import DataProcessor
from src.api_client import ChatGPTClient
from config.settings import config
from utils.logger import get_logger
from utils.cost_calculator import estimate_dataset_cost

class BatchProcessor:
    """Main processor for batch classification"""
    
    def __init__(self, output_dir: str = "output"):
        self.data_processor = DataProcessor()
        self.api_client = ChatGPTClient()
        self.output_dir = output_dir
        self.logger = get_logger("batch_processor")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize progress tracking
        self.checkpoint_file = os.path.join(output_dir, "checkpoint.json")
        self.results_file = os.path.join(output_dir, "classification_results.json")
    
    def estimate_cost(self, data_path: str) -> Dict:
        """Estimate processing cost for the dataset"""
        try:
            df = self.data_processor.load_data(data_path)
            
            # Get sample text for more accurate estimation
            sample_texts = []
            for i in range(min(10, len(df))):
                row = df.iloc[i]
                combined_text = self.data_processor.prepare_text_for_api(
                    row['Tieu_de'], row['Description'], row['Noi_dung_tin_bai']
                )
                sample_texts.append(combined_text)
            
            # Calculate average text length
            avg_text_length = sum(len(text) for text in sample_texts) / len(sample_texts)
            
            # Estimate cost
            cost_estimate = estimate_dataset_cost(
                len(df), 
                int(avg_text_length),
                config.DEFAULT_MODEL
            )
            
            self.logger.info(f"Cost estimate: ${cost_estimate['total_cost']:.2f}")
            return cost_estimate
            
        except Exception as e:
            self.logger.error(f"Cost estimation failed: {str(e)}")
            return {}
    
    def load_checkpoint(self) -> Dict:
        """Load processing checkpoint"""
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    checkpoint = json.load(f)
                    self.logger.info(f"Loaded checkpoint: processed {checkpoint.get('last_processed_index', 0)} records")
                    return checkpoint
            except Exception as e:
                self.logger.error(f"Failed to load checkpoint: {str(e)}")
        
        return {
            'last_processed_index': 0,
            'total_cost': 0.0,
            'start_time': datetime.now().isoformat(),
            'processed_count': 0
        }
    
    def save_checkpoint(self, checkpoint: Dict):
        """Save processing checkpoint"""
        try:
            checkpoint['last_update'] = datetime.now().isoformat()
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save checkpoint: {str(e)}")
    
    def save_results(self, results: List[Dict], append: bool = True):
        """Save classification results"""
        try:
            if append and os.path.exists(self.results_file):
                # Load existing results
                with open(self.results_file, 'r', encoding='utf-8') as f:
                    existing_results = json.load(f)
                
                # Append new results
                if isinstance(existing_results, list):
                    existing_results.extend(results)
                    results = existing_results
            
            # Save all results
            with open(self.results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Saved {len(results)} results to {self.results_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save results: {str(e)}")
    
    def process_dataset(self, data_path: str, batch_size: int = None, 
                       start_from: int = None, max_records: int = None) -> Dict:
        """Process entire dataset"""
        
        # Load data
        df = self.data_processor.load_data(data_path)
        
        # Get processing stats
        stats = self.data_processor.get_processing_stats(df)
        
        # Load checkpoint
        checkpoint = self.load_checkpoint()
        
        # Determine starting point
        start_index = start_from if start_from is not None else checkpoint['last_processed_index']
        
        # Determine batch size
        batch_size = batch_size or config.BATCH_SIZE
        
        # Determine end point
        if max_records:
            end_index = min(start_index + max_records, len(df))
        else:
            end_index = len(df)
        
        self.logger.info(f"Processing records {start_index} to {end_index} in batches of {batch_size}")
        
        # Initialize tracking
        total_processed = 0
        total_successful = 0
        total_cost = checkpoint.get('total_cost', 0.0)
        all_batch_results = []
        
        # Process in batches
        with tqdm(total=end_index - start_index, desc="Processing batches") as pbar:
            
            current_index = start_index
            
            while current_index < end_index:
                try:
                    # Prepare batch
                    actual_batch_size = min(batch_size, end_index - current_index)
                    batch_data = self.data_processor.process_batch(
                        df, current_index, actual_batch_size
                    )
                    
                    if not batch_data:
                        self.logger.warning(f"No valid data in batch starting at {current_index}")
                        current_index += actual_batch_size
                        continue
                    
                    # Process batch
                    self.logger.info(f"Processing batch {current_index}-{current_index + len(batch_data)}")
                    batch_results = self.api_client.classify_batch(batch_data)
                    
                    # Update tracking
                    successful_in_batch = sum(1 for r in batch_results if r['success'])
                    batch_cost = sum(r.get('metadata', {}).get('cost', 0) for r in batch_results if r['success'])
                    
                    total_processed += len(batch_results)
                    total_successful += successful_in_batch
                    total_cost += batch_cost
                    
                    # Save batch results
                    all_batch_results.extend(batch_results)
                    self.save_results(batch_results, append=True)
                    
                    # Update checkpoint
                    checkpoint.update({
                        'last_processed_index': current_index + len(batch_data),
                        'total_cost': total_cost,
                        'processed_count': total_processed,
                        'successful_count': total_successful
                    })
                    self.save_checkpoint(checkpoint)
                    
                    # Update progress bar
                    pbar.update(len(batch_data))
                    pbar.set_postfix({
                        'Success Rate': f"{(total_successful/total_processed)*100:.1f}%" if total_processed > 0 else "0%",
                        'Cost': f"${total_cost:.2f}"
                    })
                    
                    # Move to next batch
                    current_index += len(batch_data)
                    
                except KeyboardInterrupt:
                    self.logger.info("Processing interrupted by user")
                    break
                    
                except Exception as e:
                    self.logger.error(f"Batch processing error at index {current_index}: {str(e)}")
                    current_index += batch_size  # Skip problematic batch
                    continue
        
        # Final summary
        summary = {
            'total_records_in_dataset': len(df),
            'records_processed': total_processed,
            'successful_classifications': total_successful,
            'success_rate': (total_successful / total_processed * 100) if total_processed > 0 else 0,
            'total_cost': total_cost,
            'average_cost_per_record': total_cost / total_successful if total_successful > 0 else 0,
            'start_time': checkpoint.get('start_time'),
            'end_time': datetime.now().isoformat(),
            'batch_size_used': batch_size
        }
        
        # Save summary
        summary_file = os.path.join(self.output_dir, "processing_summary.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Processing completed. Summary: {summary}")
        return summary
    
    def create_final_csv(self, original_data_path: str) -> str:
        """Create final CSV with original data + predictions"""
        try:
            # Load original data
            df_original = pd.read_csv(original_data_path, encoding='utf-8')
            
            # Load results
            if not os.path.exists(self.results_file):
                raise FileNotFoundError("No results file found")
            
            with open(self.results_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
            
            # Create results mapping
            results_dict = {r['index']: r for r in results}
            
            # Add prediction columns
            df_original['predicted_labels'] = ''
            df_original['prediction_confidence'] = ''
            df_original['model_used'] = ''
            df_original['classification_success'] = False
            
            for idx, row in df_original.iterrows():
                if idx in results_dict:
                    result = results_dict[idx]
                    if result['success']:
                        labels = [l['label'] for l in result['labels']]
                        confidences = [l['confidence'] for l in result['labels']]
                        
                        df_original.loc[idx, 'predicted_labels'] = '; '.join(labels)
                        df_original.loc[idx, 'prediction_confidence'] = '; '.join([f"{c:.2f}" for c in confidences])
                        df_original.loc[idx, 'model_used'] = result['metadata'].get('model_used', '')
                        df_original.loc[idx, 'classification_success'] = True
            
            # Save final CSV
            output_file = os.path.join(self.output_dir, "final_results.csv")
            df_original.to_csv(output_file, index=False, encoding='utf-8')
            
            self.logger.info(f"Final results saved to {output_file}")
            return output_file
            
        except Exception as e:
            self.logger.error(f"Failed to create final CSV: {str(e)}")
            raise