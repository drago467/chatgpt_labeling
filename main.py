"""
Main entry point for ChatGPT labeling system
"""
import argparse
import sys
import os
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.batch_processor import BatchProcessor
from src.api_client import ChatGPTClient
from config.settings import config
from utils.logger import get_logger

def test_api_connection():
    """Test API connection"""
    print("Testing API connection...")
    client = ChatGPTClient()
    if client.test_connection():
        print("API connection successful")
        return True
    else:
        print("API connection failed")
        return False

def estimate_cost(data_path: str):
    """Estimate processing cost"""
    print(f"Estimating cost for dataset: {data_path}")
    processor = BatchProcessor()
    
    try:
        estimate = processor.estimate_cost(data_path)
        if estimate:
            print(f"\n  Cost Estimation:")
            print(f"   Dataset size: {estimate['dataset_size']} records")
            print(f"   Model: {estimate['model']}")
            print(f"   Estimated total cost: ${estimate['total_cost']:.2f}")
            print(f"   Cost per record: ${estimate['cost_per_record']:.4f}")
            print(f"   Avg input tokens: {estimate['avg_input_tokens']}")
            print(f"   Avg output tokens: {estimate['avg_output_tokens']}")
        else:
            print(" Cost estimation failed")
    except Exception as e:
        print(f" Error during cost estimation: {str(e)}")

def process_dataset(data_path: str, batch_size: int, start_from: int, 
                   max_records: int, output_dir: str):
    """Process the dataset"""
    print(f"Starting dataset processing...")
    print(f"   Data path: {data_path}")
    print(f"   Batch size: {batch_size}")
    print(f"   Start from: {start_from}")
    print(f"   Max records: {max_records or 'All'}")
    print(f"   Output directory: {output_dir}")
    
    processor = BatchProcessor(output_dir)
    
    try:
        summary = processor.process_dataset(
            data_path=data_path,
            batch_size=batch_size,
            start_from=start_from,
            max_records=max_records
        )
        
        print(f"\n🎉 Processing completed!")
        print(f"   Records processed: {summary['records_processed']}")
        print(f"   Successful classifications: {summary['successful_classifications']}")
        print(f"   Success rate: {summary['success_rate']:.1f}%")
        print(f"   Total cost: ${summary['total_cost']:.2f}")
        print(f"   Average cost per record: ${summary['average_cost_per_record']:.4f}")
        
        # Create final CSV
        print("\nCreating final CSV...")
        final_csv = processor.create_final_csv(data_path)
        print(f" Final results saved to: {final_csv}")
        
    except Exception as e:
        print(f" Processing failed: {str(e)}")
        raise

def main():
    parser = argparse.ArgumentParser(description="ChatGPT Multi-label Classification System")
    
    parser.add_argument('command', choices=['test', 'estimate', 'process'], 
                       help='Command to execute')
    
    default_data_path = os.path.join(project_root, 'data', 'tnmt_subtopic_data.csv')
    parser.add_argument('--data', type=str, default=default_data_path,
                       help='Path to input CSV file')
    
    parser.add_argument('--batch-size', type=int, default=10,
                       help='Batch size for processing')
    
    parser.add_argument('--start-from', type=int, default=0,
                       help='Start processing from this index')
    
    parser.add_argument('--max-records', type=int, default=None,
                       help='Maximum number of records to process')
    
    parser.add_argument('--output-dir', type=str, default='output',
                       help='Output directory for results')
    
    args = parser.parse_args()
    
    # Setup logging
    os.makedirs('logs', exist_ok=True)
    logger = get_logger("main", "logs/main.log")
    
    try:
        # Validate configuration
        config.validate_config()
        logger.info("Configuration validated successfully")
        
        if args.command == 'test':
            test_api_connection()
            
        elif args.command == 'estimate':
            estimate_cost(args.data)
            
        elif args.command == 'process':
            # Test connection first
            if not test_api_connection():
                print("  Cannot proceed without API connection")
                return
            
            # Show cost estimate
            estimate_cost(args.data)
            
            # # Ask for confirmation
            # response = input("\nProceed with processing? (y/N): ")
            # if response.lower() != 'y':
            #     print("Processing cancelled")
            #     return
            
            # Process dataset
            process_dataset(
                args.data,
                args.batch_size,
                args.start_from,
                args.max_records,
                args.output_dir
            )
        
    except KeyboardInterrupt:
        print("\n  Operation cancelled by user")
    except Exception as e:
        print(f"  Error: {str(e)}")
        logger.error(f"Main error: {str(e)}")
        raise

if __name__ == "__main__":
    main()