"""
ChatGPT API client with retry logic and error handling
"""
import openai
import time
import json
from typing import Dict, List, Optional, Tuple
from retry import retry
import tiktoken

from config.settings import config
from config.prompts import PromptTemplates
from utils.logger import get_logger
from utils.cost_calculator import CostCalculator
from utils.validators import ResponseValidator

class ChatGPTClient:
    """Client for ChatGPT API interactions"""
    
    def __init__(self, model: str = None):
        self.model = model or config.DEFAULT_MODEL
        self.fallback_model = config.FALLBACK_MODEL
        self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY, base_url=config.OPENAI_BASE_URL)
        self.cost_calculator = CostCalculator(self.model)
        self.response_validator = ResponseValidator()
        self.prompt_templates = PromptTemplates()
        self.logger = get_logger("chatgpt_client")
        
        # Validate API key
        if not config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
    
    @retry(tries=3, delay=1, backoff=2, logger=None)
    def _make_api_call(self, messages: List[Dict], model: str = None) -> Dict:
        """Make API call with retry logic"""
        model_to_use = model or self.model
        
        try:
            response = self.client.chat.completions.create(
                model=model_to_use,
                messages=messages,
                temperature=config.TEMPERATURE,
                max_tokens=500,  # Reasonable limit for JSON response
                response_format={"type": "json_object"} if "gpt-4" in model_to_use else None
            )
            
            return {
                'success': True,
                'response': response,
                'model_used': model_to_use
            }
            
        except openai.RateLimitError as e:
            self.logger.warning(f"Rate limit exceeded: {str(e)}")
            time.sleep(60)  # Wait 1 minute
            raise
            
        except openai.APIError as e:
            self.logger.error(f"API error: {str(e)}")
            raise
            
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            raise
    
    def classify_text(self, title: str, description: str, content: str,
                     use_fallback: bool = False) -> Tuple[bool, Dict]:
        """Classify a single text into multiple labels"""
        
        # Choose model
        model_to_use = self.fallback_model if use_fallback else self.model
        
        # Prepare messages
        system_prompt = self.prompt_templates.get_system_prompt()
        few_shot_examples = self.prompt_templates.get_few_shot_examples()
        classification_prompt = self.prompt_templates.create_classification_prompt(
            title, description, content
        )
        validation_prompt = self.prompt_templates.get_validation_prompt()
        
        user_content = f"{few_shot_examples}\n\n{classification_prompt}\n\n{validation_prompt}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        
        try:
            # Calculate tokens for cost estimation
            input_tokens = sum([self.cost_calculator.count_tokens(msg["content"]) for msg in messages])
            
            # Make API call
            result = self._make_api_call(messages, model_to_use)
            
            if not result['success']:
                return False, {'error': 'API call failed'}
            
            # Extract response
            response_content = result['response'].choices[0].message.content
            
            # Calculate actual usage
            usage = result['response'].usage
            actual_input_tokens = usage.prompt_tokens
            actual_output_tokens = usage.completion_tokens
            
            # Calculate cost
            cost = self.cost_calculator.calculate_cost(actual_input_tokens, actual_output_tokens)
            
            # Log API call
            self.logger.info(
                f"API call successful - Model: {result['model_used']}, "
                f"Input tokens: {actual_input_tokens}, Output tokens: {actual_output_tokens}, "
                f"Cost: ${cost:.4f}"
            )
            
            # Validate and parse response
            is_valid, parsed_labels, validation_message = self.response_validator.validate_json_response(response_content)
            
            if not is_valid:
                self.logger.error(f"Invalid response format: {validation_message}")
                return False, {
                    'error': 'Invalid response format',
                    'validation_message': validation_message,
                    'raw_response': response_content
                }
            
            # Clean and validate labels
            cleaned_labels, warnings = self.response_validator.validate_labels(parsed_labels)
            
            if warnings:
                self.logger.warning(f"Label validation warnings: {warnings}")
            
            # Check response quality
            is_quality, quality_issues = self.response_validator.check_response_quality(
                cleaned_labels, config.CONFIDENCE_THRESHOLD
            )
            
            if not is_quality:
                self.logger.warning(f"Quality issues detected: {quality_issues}")
            
            return True, {
                'labels': cleaned_labels,
                'model_used': result['model_used'],
                'input_tokens': actual_input_tokens,
                'output_tokens': actual_output_tokens,
                'cost': cost,
                'warnings': warnings,
                'quality_issues': quality_issues if not is_quality else [],
                'raw_response': response_content
            }
            
        except Exception as e:
            self.logger.error(f"Classification failed: {str(e)}")
            return False, {'error': str(e)}
    
    def classify_batch(self, batch_data: List[Dict]) -> List[Dict]:
        """Classify a batch of texts"""
        results = []
        total_cost = 0.0
        
        self.logger.info(f"Starting batch classification for {len(batch_data)} records")
        
        for i, data in enumerate(batch_data):
            try:
                success, result = self.classify_text(
                    data['title'],
                    data['description'], 
                    data['content']
                )
                
                if success:
                    total_cost += result.get('cost', 0)
                    results.append({
                        'index': data['index'],
                        'success': True,
                        'labels': result['labels'],
                        'metadata': {
                            'model_used': result['model_used'],
                            'cost': result['cost'],
                            'warnings': result.get('warnings', []),
                            'quality_issues': result.get('quality_issues', [])
                        }
                    })
                else:
                    # Try with fallback model
                    self.logger.warning(f"Retrying record {data['index']} with fallback model")
                    success_fallback, result_fallback = self.classify_text(
                        data['title'],
                        data['description'],
                        data['content'],
                        use_fallback=True
                    )
                    
                    if success_fallback:
                        total_cost += result_fallback.get('cost', 0)
                        results.append({
                            'index': data['index'],
                            'success': True,
                            'labels': result_fallback['labels'],
                            'metadata': {
                                'model_used': result_fallback['model_used'],
                                'cost': result_fallback['cost'],
                                'warnings': result_fallback.get('warnings', []),
                                'quality_issues': result_fallback.get('quality_issues', []),
                                'used_fallback': True
                            }
                        })
                    else:
                        results.append({
                            'index': data['index'],
                            'success': False,
                            'error': result.get('error', 'Unknown error'),
                            'metadata': {}
                        })
                
                # Add delay to respect rate limits
                if i < len(batch_data) - 1:  # Don't sleep after last item
                    time.sleep(1)  # 1 second delay between requests
                    
            except Exception as e:
                self.logger.error(f"Batch processing error for record {data['index']}: {str(e)}")
                results.append({
                    'index': data['index'],
                    'success': False,
                    'error': str(e),
                    'metadata': {}
                })
        
        self.logger.info(f"Batch completed. Total cost: ${total_cost:.4f}")
        return results
    
    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello, this is a test."}],
                max_tokens=10
            )
            self.logger.info("API connection test successful")
            return True
            
        except Exception as e:
            self.logger.error(f"API connection test failed: {str(e)}")
            return False