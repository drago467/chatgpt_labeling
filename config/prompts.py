"""
Prompt templates for ChatGPT multi-label classification
"""
from typing import List, Dict, Any
from config.labels import TNMT_LABELS, LABEL_DESCRIPTIONS, get_label_list

class PromptTemplates:
    """Container for all prompt templates"""
    
    @staticmethod
    def get_system_prompt() -> str:
        """System prompt định nghĩa vai trò và nhiệm vụ"""
        labels_text = "\n".join([f"{i}. {label}" for i, label in enumerate(get_label_list(), 1)])
        
        return f"""Bạn là một chuyên gia phân loại văn bản trong lĩnh vực Tài nguyên và Môi trường (TNMT) của Việt Nam.

NHIỆM VỤ: Phân loại multi-label cho bài báo tiếng Việt vào một hoặc nhiều trong 12 danh mục sau:

{labels_text}

QUY TẮC PHÂN LOẠI:
1. Mỗi bài báo có thể thuộc 1 hoặc nhiều danh mục (multi-label)
2. Phân tích cẩn thận tiêu đề, mô tả và nội dung
3. Ưu tiên các nhãn chính xác và cụ thể nhất
4. Chỉ sử dụng nhãn "Khác" khi không phù hợp với 11 danh mục khác
5. Đánh giá độ tin cậy cho mỗi nhãn (0.0-1.0)

ĐỊNH DẠNG OUTPUT: JSON array với format:
[
  {{"label": "tên nhãn", "confidence": 0.85}},
  {{"label": "tên nhãn khác", "confidence": 0.75}}
]"""

    @staticmethod
    def get_few_shot_examples() -> str:
        """Ví dụ few-shot cho multi-label classification"""
        return """
VÍ DỤ:

Ví dụ 1:
Tiêu đề: "Ô nhiễm nguồn nước do chất thải công nghiệp tại TP.HCM"
Mô tả: "Tình trạng ô nhiễm nguồn nước ngày càng nghiêm trọng"
Nội dung: "Các nhà máy xả thải trực tiếp xuống sông, ảnh hưởng đến chất lượng nước sinh hoạt..."

Output: [
  {"label": "Môi trường", "confidence": 0.95},
  {"label": "Tài nguyên nước", "confidence": 0.90}
]

Ví dụ 2:  
Tiêu đề: "Ứng dụng viễn thám giám sát rừng tự nhiên"
Mô tả: "Sử dụng ảnh vệ tinh để theo dõi diện tích rừng"
Nội dung: "Công nghệ viễn thám giúp phát hiện sớm các khu vực bị phá rừng, bảo vệ đa dạng sinh học..."

Output: [
  {"label": "Viễn thám", "confidence": 0.98},
  {"label": "Đa dạng sinh học", "confidence": 0.85}
]

Ví dụ 3:
Tiêu đề: "Quy hoạch sử dụng đất nông nghiệp tỉnh An Giang"
Mô tả: "Kế hoạch sử dụng đất giai đoạn 2021-2025"
Nội dung: "Quy hoạch chi tiết việc sử dụng đất cho sản xuất nông nghiệp, bảo đảm hiệu quả kinh tế..."

Output: [
  {"label": "Đất đai", "confidence": 0.92}
]
"""

    @staticmethod
    def create_classification_prompt(title: str, description: str, content: str) -> str:
        """Tạo prompt hoàn chỉnh cho phân loại"""
        # Truncate content if too long
        max_content_length = 2000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
            
        return f"""Phân loại bài báo sau vào các danh mục phù hợp:

TIÊU ĐỀ: {title}

MÔ TẢ: {description}

NỘI DUNG: {content}

Hãy phân tích và trả về kết quả theo định dạng JSON đã yêu cầu:"""

    @staticmethod
    def get_validation_prompt() -> str:
        """Prompt để validate response format"""
        return """
QUAN TRỌNG: 
- Chỉ trả về JSON array hợp lệ
- Không giải thích thêm
- Confidence score từ 0.0 đến 1.0
- Tên nhãn phải chính xác theo danh sách đã cho
"""