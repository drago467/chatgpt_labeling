"""
Configuration settings for ChatGPT labeling system
"""
import os
from dotenv import load_dotenv
from typing import List, Dict, Any

# Load environment variables
load_dotenv()

class Config:
    """Main configuration class"""
    
    # API Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL')
    
    # Model Settings
    DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'gpt-4o-mini-2024-07-18')
    FALLBACK_MODEL = os.getenv('FALLBACK_MODEL', 'gpt-4o-mini')
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', 4000))
    TEMPERATURE = float(os.getenv('TEMPERATURE', 0.1))
    
    # Rate Limiting
    MAX_RPM = int(os.getenv('MAX_RPM', 500))
    MAX_TPM = int(os.getenv('MAX_TPM', 30000))
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', 10))
    
    # Paths
    DATA_PATH = os.getenv('DATA_PATH', '../data/tnmt_subtopic_data.csv')
    OUTPUT_PATH = os.getenv('OUTPUT_PATH', './output/')
    
    # Processing Configuration
    CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', 0.7))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
    RETRY_DELAY = int(os.getenv('RETRY_DELAY', 1))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', './logs/chatgpt_labeling.log')
    
    @classmethod
    def validate_config(cls):
        """Validate configuration settings"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        
        if not cls.OPENAI_BASE_URL:
            raise ValueError("OPENAI_BASE_URL is required")

        if cls.MAX_TOKENS <= 0:
            raise ValueError("MAX_TOKENS must be positive")
            
        if not (0 <= cls.TEMPERATURE <= 2):
            raise ValueError("TEMPERATURE must be between 0 and 2")
            
        return True

# Initialize configuration
config = Config()