"""
Cost calculation utilities for ChatGPT API calls
"""
import tiktoken
from typing import Dict, Tuple
from config.settings import config

# Model pricing (as of September 2025)
# Third-party API pricing: $0.15 per 1M tokens = $0.00015 per 1K tokens
MODEL_PRICING = {
    config.DEFAULT_MODEL: {
        "input": 0.00015,  # per 1K tokens ($0.15 per 1M tokens)
        "output": 0.00015  # per 1K tokens ($0.15 per 1M tokens)
    },
    config.FALLBACK_MODEL: {
        "input": 0.00015,  # per 1K tokens ($0.15 per 1M tokens)
        "output": 0.00015  # per 1K tokens ($0.15 per 1M tokens)
    }
}

class CostCalculator:
    """Calculator for API costs"""
    
    def __init__(self, model: str = config.DEFAULT_MODEL):
        self.model = model
        
        # Try to get encoder for model, fallback to gpt-4 for unknown models
        try:
            self.encoder = tiktoken.encoding_for_model(model)
        except KeyError:
            # Fallback to gpt-4 encoding for unknown models
            print(f"Warning: Using gpt-4 encoding for unknown model: {model}")
            self.encoder = tiktoken.encoding_for_model("gpt-4")
        
        # For third-party API models, use estimated pricing if not in our pricing table
        if model not in MODEL_PRICING:
            print(f"Warning: Using estimated pricing for third-party model: {model}")
            # Add the model with third-party pricing
            MODEL_PRICING[model] = {
                "input": 0.00015,  # per 1K tokens ($0.15 per 1M tokens)
                "output": 0.00015  # per 1K tokens ($0.15 per 1M tokens)
            }
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoder.encode(text))
    
    def estimate_prompt_tokens(self, system_prompt: str, user_prompt: str) -> int:
        """Estimate total input tokens"""
        return self.count_tokens(system_prompt) + self.count_tokens(user_prompt)
    
    def estimate_response_tokens(self, num_labels: int = 3) -> int:
        """Estimate output tokens for JSON response"""
        # Rough estimate: each label takes ~50 tokens in JSON format
        return num_labels * 50 + 20  # +20 for JSON structure
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate total cost for API call"""
        pricing = MODEL_PRICING[self.model]
        
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        
        return input_cost + output_cost
    
    def estimate_batch_cost(self, texts: list, system_prompt: str, avg_labels: int = 2) -> Dict:
        """Estimate cost for a batch of texts"""
        total_input_tokens = 0
        total_output_tokens = 0
        
        for text in texts:
            input_tokens = self.count_tokens(system_prompt) + self.count_tokens(text)
            output_tokens = self.estimate_response_tokens(avg_labels)
            
            total_input_tokens += input_tokens
            total_output_tokens += output_tokens
        
        total_cost = self.calculate_cost(total_input_tokens, total_output_tokens)
        
        return {
            "total_records": len(texts),
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_cost": total_cost,
            "cost_per_record": total_cost / len(texts) if texts else 0,
            "model": self.model
        }
    
    def get_model_comparison(self, input_tokens: int, output_tokens: int) -> Dict:
        """Compare costs across different models"""
        comparison = {}
        
        for model in MODEL_PRICING:
            pricing = MODEL_PRICING[model]
            input_cost = (input_tokens / 1000) * pricing["input"]
            output_cost = (output_tokens / 1000) * pricing["output"]
            total_cost = input_cost + output_cost
            
            comparison[model] = {
                "input_cost": input_cost,
                "output_cost": output_cost,
                "total_cost": total_cost
            }
        
        return comparison

def estimate_dataset_cost(dataset_size: int, avg_text_length: int = 2000, 
                         model: str = config.DEFAULT_MODEL) -> Dict:
    """Quick estimate for entire dataset processing"""
    calculator = CostCalculator(model)
    
    # Estimate tokens per record
    system_prompt_tokens = 500  # Rough estimate
    avg_text_tokens = calculator.count_tokens("a" * avg_text_length)
    avg_input_tokens = system_prompt_tokens + avg_text_tokens
    avg_output_tokens = calculator.estimate_response_tokens(2)
    
    total_input_tokens = avg_input_tokens * dataset_size
    total_output_tokens = avg_output_tokens * dataset_size
    total_cost = calculator.calculate_cost(total_input_tokens, total_output_tokens)
    
    return {
        "dataset_size": dataset_size,
        "avg_input_tokens": avg_input_tokens,
        "avg_output_tokens": avg_output_tokens,
        "total_cost": total_cost,
        "cost_per_record": total_cost / dataset_size,
        "model": model,
        "estimated": True
    }