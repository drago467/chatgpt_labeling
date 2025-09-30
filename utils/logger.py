"""
Logging utilities for ChatGPT labeling system
"""
import logging
import os
from datetime import datetime
from typing import Optional

class Logger:
    """Custom logger for the project"""
    
    def __init__(self, name: str = "chatgpt_labeling", log_file: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        if log_file:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)

# Global logger instance
def get_logger(name: str = "chatgpt_labeling", log_file: Optional[str] = None) -> Logger:
    """Get logger instance"""
    return Logger(name, log_file)

def log_api_call(logger: Logger, model: str, tokens_used: int, cost: float):
    """Log API call details"""
    logger.info(f"API Call - Model: {model}, Tokens: {tokens_used}, Cost: ${cost:.4f}")

def log_processing_progress(logger: Logger, processed: int, total: int, batch_size: int):
    """Log processing progress"""
    percentage = (processed / total) * 100
    logger.info(f"Progress: {processed}/{total} ({percentage:.1f}%) - Batch size: {batch_size}")

def log_error_with_context(logger: Logger, error: Exception, context: dict):
    """Log error with additional context"""
    context_str = ", ".join([f"{k}: {v}" for k, v in context.items()])
    logger.error(f"Error: {str(error)} | Context: {context_str}")