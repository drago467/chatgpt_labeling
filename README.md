# ChatGPT Multi-label Classification for TNMT News

🎯 **Dự án tự động gán nhãn đa danh mục cho tin tức về Tài nguyên và Môi trường (TNMT) sử dụng ChatGPT API**

## 📋 Tổng quan

Hệ thống này sử dụng ChatGPT API để tự động phân loại tin tức tiếng Việt về lĩnh vực TNMT thành 1 hoặc nhiều trong 12 danh mục chuyên ngành:

1. Biển - hải đảo
2. Thông tin chung  
3. Môi trường
4. Địa chất - Khoáng sản
5. Đất đai
6. Đa dạng sinh học
7. Viễn thám
8. Quản lý chất thải rắn
9. Đo đạc và bản đồ
10. Khí tượng thủy văn - Biến đổi khí hậu
11. Tài nguyên nước
12. Khác

## 🏗️ Kiến trúc Hệ thống

```
Input CSV → Data Processing → ChatGPT API → Response Validation → Output CSV
     ↓            ↓               ↓              ↓                ↓
  Raw Data → Text Cleaning → Multi-label → Label Validation → Final Results
```

## 📁 Cấu trúc Project

```
chatgpt_labeling/
├── config/
│   ├── settings.py       # Cấu hình chung
│   ├── labels.py         # Định nghĩa nhãn TNMT
│   └── prompts.py        # Template prompt
├── src/
│   ├── data_processor.py # Xử lý dữ liệu
│   ├── api_client.py     # Client ChatGPT API
│   └── batch_processor.py# Xử lý batch chính
├── utils/
│   ├── validators.py     # Validation functions
│   ├── cost_calculator.py# Tính toán chi phí
│   └── logger.py         # Logging system
├── notebooks/
│   └── phase1_foundation_setup.ipynb # Phân tích và setup
├── .env.example          # Template environment variables
└── main.py              # Entry point chính
```

## 🚀 Cài đặt và Cấu hình

### 1. Cài đặt Dependencies

Hệ thống sử dụng Pipenv đã được cấu hình trong workspace:

```bash
# Tất cả packages đã được cài đặt trong virtual environment
# Kiểm tra bằng cách chạy:
pip list | grep -E "(openai|tiktoken|pandas)"
```

### 2. Cấu hình API Key

**Bước 1:** Copy file cấu hình template:
```bash
cp .env.example .env
```

**Bước 2:** Chỉnh sửa file `.env`:
```bash
# OpenAI API Configuration
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
OPENAI_ORG_ID=your-org-id-here  # (optional)

# Model Configuration  
DEFAULT_MODEL=gpt-4-turbo
FALLBACK_MODEL=gpt-3.5-turbo
MAX_TOKENS=4000
TEMPERATURE=0.1

# Rate Limiting
MAX_RPM=500
MAX_TPM=30000
BATCH_SIZE=10

# Processing Configuration
CONFIDENCE_THRESHOLD=0.7
MAX_RETRIES=3
```

### 3. Chuẩn bị Dữ liệu

Đảm bảo file dataset `../data/tnmt_subtopic_data.csv` có cấu trúc:
- `Tieu_de`: Tiêu đề tin tức
- `Description`: Mô tả ngắn gọn  
- `Noi_dung_tin_bai`: Nội dung chi tiết

## 💻 Sử dụng Hệ thống

### 1. Test API Connection

```bash
python main.py test
```

### 2. Ước tính Chi phí

```bash
python main.py estimate --data ../data/tnmt_subtopic_data.csv
```

### 3. Xử lý Dataset Hoàn chỉnh

```bash
python main.py process --data ../data/tnmt_subtopic_data.csv --batch-size 10
```

### 4. Xử lý Một phần Dataset

```bash
# Xử lý 100 records đầu tiên
python main.py process --data ../data/tnmt_subtopic_data.csv --max-records 100

# Bắt đầu từ record thứ 500
python main.py process --data ../data/tnmt_subtopic_data.csv --start-from 500
```

### 5. Tiếp tục từ Checkpoint

Hệ thống tự động lưu checkpoint, chỉ cần chạy lại lệnh cũ:

```bash
python main.py process --data ../data/tnmt_subtopic_data.csv
```

## 📊 Đầu ra và Kết quả

### File Outputs

1. **`output/classification_results.json`**: Kết quả chi tiết từng record
2. **`output/final_results.csv`**: File CSV gốc + cột dự đoán
3. **`output/processing_summary.json`**: Báo cáo tổng hợp
4. **`output/checkpoint.json`**: Checkpoint để tiếp tục xử lý

### Cấu trúc Kết quả

```json
{
  "index": 0,
  "success": true,
  "labels": [
    {"label": "Môi trường", "confidence": 0.95},
    {"label": "Tài nguyên nước", "confidence": 0.78}
  ],
  "metadata": {
    "model_used": "gpt-4-turbo", 
    "cost": 0.0234,
    "warnings": [],
    "quality_issues": []
  }
}
```

## 📈 Monitoring và Logging

### Log Files
- `logs/main.log`: Log chính của hệ thống
- `logs/chatgpt_labeling.log`: Log chi tiết quá trình xử lý

### Progress Tracking
- Real-time progress bar
- Cost tracking theo thời gian thực
- Success rate monitoring
- Automatic checkpoint saving

## 💰 Quản lý Chi phí

### Ước tính Chi phí (1,269 records)

| Model | Total Cost | Cost/Record | Estimated Time |
|-------|------------|-------------|----------------|
| GPT-4 Turbo | ~$75-100 | ~$0.06-0.08 | 2-3 hours |
| GPT-3.5 Turbo | ~$15-25 | ~$0.01-0.02 | 20-30 minutes |

### Chi phí Thực tế
Hệ thống tracking chi phí real-time và hiển thị trong progress reports.

## 🔧 Customization

### Thay đổi Prompt Templates

Chỉnh sửa file `config/prompts.py`:

```python
def get_system_prompt(self) -> str:
    # Customize system prompt here
    return "Your custom system prompt..."
```

### Thêm/Sửa Nhãn

Chỉnh sửa file `config/labels.py`:

```python
TNMT_LABELS = {
    1: "Your new label category",
    # ... existing labels
}
```

### Điều chỉnh Preprocessing

Chỉnh sửa file `src/data_processor.py`:

```python
def preprocess_text(self, text: str) -> str:
    # Add custom preprocessing logic
    return processed_text
```

## 🧪 Development và Testing

### Chạy Foundation Setup Notebook

```bash
jupyter notebook notebooks/phase1_foundation_setup.ipynb
```

Notebook này bao gồm:
- Dataset analysis chi tiết
- Token và cost analysis
- Text preprocessing testing  
- Component integration testing

### Unit Testing

```bash
# Chạy từ project root
python -m pytest tests/
```

## 🚨 Xử lý Lỗi Thường gặp

### 1. API Key Issues
```
❌ Error: OPENAI_API_KEY is required
```
**Giải pháp**: Đảm bảo đã set API key trong file `.env`

### 2. Rate Limit Errors
```
❌ Rate limit exceeded
```  
**Giải pháp**: Hệ thống tự động retry với exponential backoff

### 3. Token Limit Errors
```
❌ Token limit exceeded
```
**Giải pháp**: Hệ thống tự động truncate text dài

### 4. Memory Issues
```
❌ Out of memory
```
**Giải pháp**: Giảm batch size xuống 5 hoặc thấp hơn

## 📞 Support và Đóng góp

### Báo lỗi
Tạo issue trong repository với thông tin:
- Error message chi tiết
- Environment configuration
- Sample data (nếu có thể)

### Feature Requests
- Multi-language support
- Additional output formats
- Integration with other APIs

## 📄 License

MIT License - xem file LICENSE để biết chi tiết.

---

**Phát triển bởi**: AI Team  
**Phiên bản**: 1.0  
**Cập nhật**: September 2025