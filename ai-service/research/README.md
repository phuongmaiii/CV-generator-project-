# NLP Extraction Research & Experiments

Thư mục này chứa các script thử nghiệm offline phục vụ cho quá trình nghiên cứu bóc tách dữ liệu CV (NER, Regex).
Các script ở đây được dùng để huấn luyện và đánh giá mô hình, không can thiệp trực tiếp vào luồng chạy runtime của FastAPI.

- `finetune_ner.py`: Script huấn luyện mô hình nhận diện thực thể.
- `regex_extractor.py`: Bóc tách thông tin dựa trên biểu thức chính quy.
- `evaluate.py`: Đánh giá độ chính xác của quá trình trích xuất.