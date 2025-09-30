"""
Validation utilities for input data and API responses
"""
import json
import re
from typing import List, Dict, Any, Tuple, Optional
import pandas as pd
from config.labels import get_label_list, validate_labels

def _try_reconstruct_from_flat_structure(data: Dict) -> Optional[List[Dict]]:
    """Try to reconstruct array from flat structure like:
    {
        'label1': 'Biển - hải đảo', 'confidence1': 0.9,
        'label2': 'Thông tin chung', 'confidence2': 0.8
    }
    """
    try:
        labels = []
        
        # Look for numbered patterns
        i = 1
        while f'label{i}' in data and f'confidence{i}' in data:
            labels.append({
                'label': data[f'label{i}'],
                'confidence': float(data[f'confidence{i}'])
            })
            i += 1
        
        # Look for non-numbered patterns 
        if not labels:
            label_keys = [k for k in data.keys() if 'label' in k.lower()]
            conf_keys = [k for k in data.keys() if 'confidence' in k.lower() or 'conf' in k.lower()]
            
            if len(label_keys) == len(conf_keys) and len(label_keys) > 0:
                for label_key, conf_key in zip(sorted(label_keys), sorted(conf_keys)):
                    labels.append({
                        'label': data[label_key],
                        'confidence': float(data[conf_key])
                    })
        
        return labels if labels else None
        
    except (ValueError, KeyError, TypeError):
        return None

class DataValidator:
    """Validator for input data"""
    
    @staticmethod
    def validate_csv_data(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validate CSV data format and required columns"""
        errors = []
        
        # Check required columns
        required_columns = ['Tieu_de', 'Description', 'Noi_dung_tin_bai']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            errors.append(f"Missing columns: {missing_columns}")
        
        # Check for empty data
        if df.empty:
            errors.append("Dataset is empty")
            
        # Check for null values in required columns
        for col in required_columns:
            if col in df.columns:
                null_count = df[col].isnull().sum()
                if null_count > 0:
                    errors.append(f"Column '{col}' has {null_count} null values")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_text_record(title: str, description: str, content: str) -> Tuple[bool, List[str]]:
        """Validate individual text record"""
        errors = []
        
        if not title or title.strip() == "":
            errors.append("Title is empty")
        
        if not description or description.strip() == "":
            errors.append("Description is empty")
            
        if not content or content.strip() == "":
            errors.append("Content is empty")
        
        # Check for extremely short texts
        if len(title.strip()) < 5:
            errors.append("Title too short (< 5 characters)")
        
        return len(errors) == 0, errors

class ResponseValidator:
    """Validator for ChatGPT API responses"""
    
    @staticmethod
    def validate_json_response(response: str) -> Tuple[bool, Optional[List[Dict]], str]:
        """Validate JSON response format"""
        try:
            # Clean response - remove any markdown formatting
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            
            cleaned_response = cleaned_response.strip()
            
            # Parse JSON
            parsed = json.loads(cleaned_response)
            
            # Handle multiple response formats
            labels_data = None
            
            if isinstance(parsed, list):
                # Format 1: Direct array
                labels_data = parsed
                
            elif isinstance(parsed, dict):
                # Format 2: Object with array in common keys
                possible_keys = ['output', 'result', 'labels', 'data', 'classifications', 'predictions', 'items']
                
                for key in possible_keys:
                    if key in parsed and isinstance(parsed[key], list):
                        labels_data = parsed[key]
                        break
                
                # Format 3: Nested structure - search recursively  
                if labels_data is None:
                    def find_array_recursive(obj, max_depth=5):
                        if max_depth <= 0:
                            return None
                        if isinstance(obj, list) and len(obj) > 0:
                            # Check if it's array of label objects
                            first_item = obj[0]
                            if isinstance(first_item, dict) and ('label' in first_item or 'name' in first_item):
                                return obj
                        elif isinstance(obj, dict):
                            for value in obj.values():
                                result = find_array_recursive(value, max_depth - 1)
                                if result is not None:
                                    return result
                        return None
                    
                    labels_data = find_array_recursive(parsed)
                
                # Format 4: Flat structure - try to reconstruct array
                if labels_data is None:
                    labels_data = _try_reconstruct_from_flat_structure(parsed)
                    
                if labels_data is None:
                    return False, None, f"No valid label array found in response. Available keys: {list(parsed.keys())}"
            else:
                return False, None, f"Response must be JSON array or object, got {type(parsed).__name__}"
            
            # Validate each item in the list
            for i, item in enumerate(labels_data):
                if not isinstance(item, dict):
                    return False, None, f"Item {i} is not a dictionary"
                
                if 'label' not in item:
                    return False, None, f"Item {i} missing 'label' field"
                
                if 'confidence' not in item:
                    return False, None, f"Item {i} missing 'confidence' field"
                
                # Validate confidence score
                try:
                    confidence = float(item['confidence'])
                    if not (0.0 <= confidence <= 1.0):
                        return False, None, f"Item {i} confidence must be between 0.0 and 1.0"
                except (ValueError, TypeError):
                    return False, None, f"Item {i} confidence must be a number"
            
            return True, labels_data, "Valid"
            
        except json.JSONDecodeError as e:
            return False, None, f"Invalid JSON: {str(e)}"
        except Exception as e:
            return False, None, f"Validation error: {str(e)}"
    
    @staticmethod
    def validate_labels(labels_data: List[Dict]) -> Tuple[List[Dict], List[str]]:
        """Validate and clean label data"""
        valid_labels = get_label_list()
        cleaned_data = []
        warnings = []
        
        for item in labels_data:
            label = item.get('label', '').strip()
            confidence = item.get('confidence', 0.0)
            
            # Check if label exists
            if label not in valid_labels:
                warnings.append(f"Invalid label: '{label}' - skipping")
                continue
            
            # Clean confidence score
            try:
                confidence = float(confidence)
                confidence = max(0.0, min(1.0, confidence))  # Clamp to [0,1]
            except (ValueError, TypeError):
                confidence = 0.5  # Default value
                warnings.append(f"Invalid confidence for '{label}' - using default 0.5")
            
            cleaned_data.append({
                'label': label,
                'confidence': confidence
            })
        
        return cleaned_data, warnings
    
    @staticmethod
    def check_response_quality(labels_data: List[Dict], 
                             min_confidence: float = 0.5) -> Tuple[bool, List[str]]:
        """Check response quality based on confidence scores"""
        issues = []
        
        if not labels_data:
            issues.append("No labels predicted")
            return False, issues
        
        # Check confidence scores
        low_confidence_labels = [
            item['label'] for item in labels_data 
            if item['confidence'] < min_confidence
        ]
        
        if low_confidence_labels:
            issues.append(f"Low confidence labels: {low_confidence_labels}")
        
        # Check for too many labels (might indicate confusion)
        if len(labels_data) > 4:
            issues.append(f"Too many labels predicted: {len(labels_data)}")
        
        return len(issues) == 0, issues

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove special characters but keep Vietnamese characters
    text = re.sub(r'[^\w\s\u00C0-\u1EF9]', ' ', text)
    
    return text.strip()