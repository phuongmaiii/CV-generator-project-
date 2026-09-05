import io
from fastapi import FastAPI, UploadFile, File, Form
from PyPDF2 import PdfReader
from deep_translator import GoogleTranslator
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI(title="CV Matching Engine API")

# Khởi tạo mô hình (Tự động tải về trong lần chạy đầu tiên)
# Sử dụng pre-trained model hỗ trợ tiếng Việt cực tốt (base trên kiến trúc Transformer/PhoBERT)
print("Đang tải AI Model vào bộ nhớ...")
model = SentenceTransformer('keepitreal/vietnamese-sbert')
print("Model đã sẵn sàng!")

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Trích xuất text từ file PDF"""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + " "
    return text

@app.post("/match")
async def match_cv(
    cv_file: UploadFile = File(...),
    jd_text: str = Form(...) # Yêu cầu công việc (Tiếng Việt) truyền vào từ Java Backend
):
    try:
        # 1. Trích xuất text từ CV (Data Extraction)
        cv_bytes = await cv_file.read()
        raw_cv_text = extract_text_from_pdf(cv_bytes)
        
        # 2. Xử lý ngôn ngữ tự nhiên (NLP Pipeline - Dịch thuật)
        # GoogleTranslator giới hạn ~5000 ký tự/lần, cần cắt nhỏ chunk để dịch an toàn
        translator = GoogleTranslator(source='auto', target='vi')
        chunk_size = 4500
        cv_chunks = [raw_cv_text[i:i+chunk_size] for i in range(0, len(raw_cv_text), chunk_size)]
        translated_cv = " ".join([translator.translate(chunk) for chunk in cv_chunks])
        
        # 3. Trích xuất đặc trưng vector (Vector Embedding)
        cv_vector = model.encode([translated_cv])
        jd_vector = model.encode([jd_text])
        
        # 4. Đo lường độ tương đồng (Cosine Similarity)
        similarity = cosine_similarity(cv_vector, jd_vector)[0][0]
        match_percentage = round(float(similarity) * 100, 2)
        
        # Chuẩn hóa để điểm số không vượt ngoài 0-100%
        match_percentage = max(0.0, min(100.0, match_percentage))
        
        return {
            "status": "success",
            "cv_name": cv_file.filename,
            "match_score": match_percentage
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}
        