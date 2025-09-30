"""
Data processing utilities for text preprocessing
"""
import pandas as pd
import re
from typing import Dict, List, Tuple, Optional
from utils.validators import DataValidator, clean_text
from utils.logger import get_logger
from utils.nlp import normalize_text

class DataProcessor:
    """Main data processing class"""
    
    def __init__(self, max_content_length: int = 2000):
        self.max_content_length = max_content_length
        self.logger = get_logger("data_processor")
    
    def load_data(self, file_path: str) -> pd.DataFrame:
        """Load CSV data with validation"""
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            self.logger.info(f"Loaded {len(df)} records from {file_path}")
            
            # Validate data
            is_valid, errors = DataValidator.validate_csv_data(df)
            if not is_valid:
                raise ValueError(f"Data validation failed: {errors}")
            
            return df
            
        except Exception as e:
            self.logger.error(f"Failed to load data from {file_path}: {str(e)}")
            raise
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text"""
        if not text or pd.isna(text):
            return ""
        
        # Truncate if too long
        if len(text) > self.max_content_length:
            text = text[:self.max_content_length] + "..."

        # Clean text
        text = normalize_text(text)
        
        return text
    
    def combine_text_fields(self, title: str, description: str, content: str) -> Dict[str, str]:
        """Combine text fields with preprocessing"""
        
        # Preprocess each field
        clean_title = self.preprocess_text(title)
        clean_desc = self.preprocess_text(description)
        clean_content = self.preprocess_text(content)
        
        return {
            'title': clean_title,
            'description': clean_desc,
            'content': clean_content
        }
    
    def prepare_text_for_api(self, title: str, description: str, content: str) -> str:
        """Prepare combined text for API call (skip cleaning for high-quality crawled data)"""
        # Since data is crawled with good quality, skip text cleaning
        # Only handle null/empty values and length truncation
        clean_title = title if title and not pd.isna(title) else ""
        clean_desc = description if description and not pd.isna(description) else ""
        clean_content = content if content and not pd.isna(content) else ""
        
        # Truncate content if too long
        if len(clean_content) > self.max_content_length:
            clean_content = clean_content[:self.max_content_length] + "..."
        
        # Combine with clear structure
        combined_text = f"""TIÊU ĐỀ: {clean_title}

MÔ TẢ: {clean_desc}

NỘI DUNG: {clean_content}"""
        
        return combined_text
    
    def process_batch(self, df: pd.DataFrame, start_idx: int = 0, 
                     batch_size: int = 10) -> List[Dict]:
        """Process a batch of records"""
        batch_data = []
        end_idx = min(start_idx + batch_size, len(df))
        
        for idx in range(start_idx, end_idx):
            row = df.iloc[idx]
            
            try:
                # Validate individual record
                is_valid, errors = DataValidator.validate_text_record(
                    row.get('Tieu_de', ''),
                    row.get('Description', ''),
                    row.get('Noi_dung_tin_bai', '')
                )
                
                if not is_valid:
                    self.logger.warning(f"Record {idx} validation failed: {errors}")
                    continue
                
                # Prepare text
                combined_text = self.prepare_text_for_api(
                    row['Tieu_de'],
                    row['Description'],
                    row['Noi_dung_tin_bai']
                )
                
                batch_data.append({
                    'index': idx,
                    'title': row['Tieu_de'],
                    'description': row['Description'],
                    'content': row['Noi_dung_tin_bai'],
                    'combined_text': combined_text
                })
                
            except Exception as e:
                self.logger.error(f"Error processing record {idx}: {str(e)}")
                continue
        
        self.logger.info(f"Processed batch {start_idx}-{end_idx}: {len(batch_data)} valid records")
        return batch_data
    
    def get_processing_stats(self, df: pd.DataFrame) -> Dict:
        """Get statistics about the dataset"""
        stats = {
            'total_records': len(df),
            'avg_title_length': df['Tieu_de'].str.len().mean() if 'Tieu_de' in df else 0,
            'avg_desc_length': df['Description'].str.len().mean() if 'Description' in df else 0,
            'avg_content_length': df['Noi_dung_tin_bai'].str.len().mean() if 'Noi_dung_tin_bai' in df else 0,
            'null_titles': df['Tieu_de'].isnull().sum() if 'Tieu_de' in df else 0,
            'null_descriptions': df['Description'].isnull().sum() if 'Description' in df else 0,
            'null_content': df['Noi_dung_tin_bai'].isnull().sum() if 'Noi_dung_tin_bai' in df else 0
        }
        
        self.logger.info(f"Dataset stats: {stats}")
        return stats