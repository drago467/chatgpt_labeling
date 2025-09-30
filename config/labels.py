"""
Label definitions for TNMT (Tài nguyên và Môi trường) subtopic classification
"""
from typing import List, Dict, Any

# Định nghĩa 12 nhãn chính
TNMT_LABELS = {
    1: "Biển - hải đảo",
    2: "Thông tin chung",
    3: "Môi trường", 
    4: "Địa chất - Khoáng sản",
    5: "Đất đai",
    6: "Đa dạng sinh học",
    7: "Viễn thám",
    8: "Quản lý chất thải rắn",
    9: "Đo đạc và bản đồ",
    10: "Khí tượng thủy văn - Biến đổi khí hậu",
    11: "Tài nguyên nước",
    12: "Khác"
}

# Mô tả chi tiết các nhãn
LABEL_DESCRIPTIONS = {
    "Biển - hải đảo": "Các vấn đề liên quan đến biển, đại dương, hải đảo, tài nguyên biển, kinh tế biển",
    "Thông tin chung": "Thông tin tổng hợp, chính sách, quy định chung về tài nguyên môi trường",
    "Môi trường": "Ô nhiễm môi trường, bảo vệ môi trường, môi trường sống, sinh thái",
    "Địa chất - Khoáng sản": "Khảo sát địa chất, khai thác khoáng sản, tài nguyên địa chất",
    "Đất đai": "Quản lý đất đai, quy hoạch sử dụng đất, chất lượng đất",
    "Đa dạng sinh học": "Bảo tồn thiên nhiên, động thực vật hoang dã, khu bảo tồn",
    "Viễn thám": "Ứng dụng viễn thám, ảnh vệ tinh, GIS trong tài nguyên môi trường",
    "Quản lý chất thải rắn": "Thu gom, xử lý chất thải, rác thải, tái chế",
    "Đo đạc và bản đồ": "Đo đạc địa hình, lập bản đồ, định vị GPS",
    "Khí tượng thủy văn - Biến đổi khí hậu": "Dự báo thời tiết, biến đổi khí hậu, thiên tai",
    "Tài nguyên nước": "Quản lý nguồn nước, cấp tẩm nước, xử lý nước thải",
    "Khác": "Các chủ đề khác không thuộc các danh mục trên"
}

# Keywords cho mỗi nhãn (để hỗ trợ phân loại)
LABEL_KEYWORDS = {
    "Biển - hải đảo": ["biển", "hải đảo", "đại dương", "tàu thuyền", "cảng", "thủy sản", "kinh tế biển"],
    "Thông tin chung": ["chính sách", "quy định", "luật", "nghị định", "thông tư", "hướng dẫn"],
    "Môi trường": ["ô nhiễm", "môi trường", "sinh thái", "xanh", "bảo vệ", "khí thải"],
    "Địa chất - Khoáng sản": ["địa chất", "khoáng sản", "than", "dầu khí", "khai thác", "mỏ"],
    "Đất đai": ["đất đai", "sử dụng đất", "quy hoạch đất", "chất lượng đất", "canh tác"],
    "Đa dạng sinh học": ["đa dạng sinh học", "động vật", "thực vật", "bảo tồn", "rừng", "khu bảo tồn"],
    "Viễn thám": ["viễn thám", "vệ tinh", "GIS", "ảnh vệ tinh", "bản đồ số"],
    "Quản lý chất thải rắn": ["chất thải", "rác thải", "thu gom", "xử lý rác", "tái chế"],
    "Đo đạc và bản đồ": ["đo đạc", "bản đồ", "GPS", "địa hình", "trắc địa"],
    "Khí tượng thủy văn - Biến đổi khí hậu": ["khí tượng", "thời tiết", "biến đổi khí hậu", "lũ lụt", "hạn hán"],
    "Tài nguyên nước": ["nước", "cấp nước", "nước thải", "nguồn nước", "thủy lợi"],
    "Khác": []
}

def get_label_list() -> List[str]:
    """Trả về danh sách tên các nhãn"""
    return list(TNMT_LABELS.values())

def get_label_by_id(label_id: int) -> str:
    """Lấy tên nhãn theo ID"""
    return TNMT_LABELS.get(label_id, "Unknown")

def get_label_id(label_name: str) -> int:
    """Lấy ID nhãn theo tên"""
    for id, name in TNMT_LABELS.items():
        if name == label_name:
            return id
    return -1

def validate_labels(labels: List[str]) -> List[str]:
    """Kiểm tra và làm sạch danh sách nhãn"""
    valid_labels = get_label_list()
    return [label for label in labels if label in valid_labels]