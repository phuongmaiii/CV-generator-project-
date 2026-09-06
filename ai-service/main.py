from fastapi import FastAPI, UploadFile, File, HTTPException
from schema import BatchMatchRequest, ClassifyRequest, ClassifyResponse, MatchRequest, MatchResponse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import pdfplumber
import io
import math 
from pydantic import BaseModel
from typing import Optional
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

import requests
from bs4 import BeautifulSoup
import urllib.parse
import random

import joblib
import os

app = FastAPI(title="CV Recruitment AI Service")

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")

industry_vectorizer = joblib.load(os.path.join(MODEL_DIR, "industry_tfidf.joblib"))
industry_svm = joblib.load(os.path.join(MODEL_DIR, "industry_svm.joblib"))
position_vectorizer = joblib.load(os.path.join(MODEL_DIR, "position_tfidf.joblib"))
position_svm = joblib.load(os.path.join(MODEL_DIR, "position_svm.joblib"))

SVM_CONFIDENCE_THRESHOLD = 0.3


def classify_industry_svm(text: str):
    vec = industry_vectorizer.transform([text])
    proba = industry_svm.predict_proba(vec)[0]
    classes = industry_svm.classes_
    best_match = max(zip(classes, proba), key=lambda item: item[1])
    return str(best_match[0]), round(float(best_match[1]), 4)

def classify_position_svm(text: str):
    vec = position_vectorizer.transform([text])
    proba = position_svm.predict_proba(vec)[0]
    classes = position_svm.classes_
    best_match = max(zip(classes, proba), key=lambda item: item[1])
    return str(best_match[0]), round(float(best_match[1]), 4)


# ==========================================
# 1. CÁC HÀM HỖ TRỢ
# ==========================================

def get_position_rule_based(text: str) -> str:
    text = text.lower()
    rules = {
        "Frontend Developer": ["react", "vue", "angular", "html", "css", "javascript", "frontend", "ui/ux", "vite", "ant design"],
        "Backend Developer": ["spring boot", "spring", "node.js", "express", "django", "backend", "restful api", "microservice"],
        "Data / AI Engineer": ["machine learning", "deep learning", "pandas", "numpy", "tensorflow", "pytorch", "data scientist", "data engineer"],
        "DevOps / Cloud": ["docker", "kubernetes", "aws", "ci/cd", "jenkins", "devops"],
        "Business Analyst": ["business analyst", "business analysis", "requirement gathering", "stakeholder", "brd", "frd", "use case", "uml", "process improvement", "phân tích nghiệp vụ", "phân tích yêu cầu"],
        "QA / Tester": ["tester", "test case", "qa engineer", "manual testing", "automation testing", "selenium", "kiểm thử"],
        "Project Manager": ["project manager", "scrum master", "agile", "quản lý dự án", "pmp"],
        "Data Analyst": ["data analyst", "power bi", "tableau", "excel", "phân tích dữ liệu"],
    }
    
    best_match = "Chưa xác định"
    max_score = 0
    
    
    MIN_SCORE_THRESHOLD = 2
    
    for category, keywords in rules.items():
        score = sum(len(re.findall(r'\b' + re.escape(kw) + r'\b', text)) for kw in keywords)
        if score > max_score:
            max_score = score
            best_match = category
    
    if max_score < MIN_SCORE_THRESHOLD:
        return "Chưa xác định"
            
    return best_match

def get_industry_rule_based(text: str) -> str:
    """
    Trước đây /classify/industry và /parse-cv LUÔN trả cứng "INFORMATION-TECHNOLOGY"
    với confidence 0.99 — không có logic phân loại thật, chỉ là code giả (stub) để
    khớp với response schema. Hàm này thay thế bằng phân loại rule-based thật (cùng
    kỹ thuật đếm từ khóa theo ngưỡng tối thiểu đã dùng cho get_position_rule_based),
    KHÔNG phải model học máy — nên README mô tả đúng là "rule-based", không phải SVM.
    """
    text = text.lower()
    rules = {
        "INFORMATION-TECHNOLOGY": [
            "developer", "lập trình", "software", "programming", "react", "java",
            "python", "backend", "frontend", "database", "api", "devops", "it ",
            "công nghệ thông tin", "phần mềm",
        ],
        "FINANCE-BANKING": [
            "kế toán", "tài chính", "ngân hàng", "accounting", "finance", "banking",
            "audit", "kiểm toán", "thuế", "báo cáo tài chính",
        ],
        "MARKETING-SALES": [
            "marketing", "sales", "kinh doanh", "bán hàng", "quảng cáo", "seo",
            "content", "thương hiệu", "brand", "chăm sóc khách hàng",
        ],
        "HUMAN-RESOURCES": [
            "nhân sự", "tuyển dụng", "human resources", "recruitment", "c&b",
            "đào tạo nhân viên", "hr ",
        ],
        "EDUCATION": [
            "giáo viên", "giảng dạy", "teacher", "education", "đào tạo", "gia sư",
            "giảng viên",
        ],
        "HEALTHCARE": [
            "y tế", "bác sĩ", "điều dưỡng", "healthcare", "dược", "bệnh viện",
            "nurse", "pharmacist",
        ],
    }

    best_match = "Chưa xác định"
    max_score = 0
    MIN_SCORE_THRESHOLD = 2

    for category, keywords in rules.items():
        score = sum(len(re.findall(r'\b' + re.escape(kw) + r'\b', text)) for kw in keywords)
        if score > max_score:
            max_score = score
            best_match = category

    if max_score < MIN_SCORE_THRESHOLD:
        return "Chưa xác định"

    return best_match


def extract_contact_info(text: str):
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    phone_pattern = r'(?:(?:\+|00)84|0)\s*[1-9](?:[\s.-]*\d{2}){4,9}'
    phones = re.findall(phone_pattern, text)
    
    return {
        "email": emails[0] if emails else None,
        "phone": phones[0] if phones else None
    }

def scale_tfidf_score(raw_similarity: float) -> float:
    """
    BẢN CŨ (đã bỏ): nhân 100, lấy log10, rồi nhân hệ số 50 tuỳ chỉnh để điểm "nhìn đẹp"
    (thường rơi vào khoảng 40-90% dù CV/JD gần như không liên quan). Đây là hack thủ
    công thuần tuý để che đi việc cosine similarity của TF-IDF trên văn bản dài (CV)
    so với văn bản ngắn (JD) luôn rất nhỏ — không phải phương pháp có căn cứ.
    Hàm này được giữ lại trong file chỉ để đối chiếu, không còn được gọi ở đâu nữa.
    """
    if raw_similarity <= 0:
        return 0.0
    amplified_score = raw_similarity * 100
    log_score = math.log10(amplified_score + 1)
    final_scaled = min(log_score * 50, 99.0)
    return round(final_scaled, 2)


VIETNAMESE_STOPWORDS = {
    "và", "là", "của", "có", "được", "cho", "các", "một", "những", "trong", "với",
    "để", "này", "đã", "sẽ", "tại", "theo", "về", "như", "khi", "từ", "đến", "nếu",
    "hoặc", "nhưng", "vì", "do", "bởi", "nên", "thì", "cũng", "rất", "còn", "lại",
    "làm", "công", "việc", "người", "năm", "tháng", "ngày", "chúng", "tôi", "bạn",
    "anh", "chị", "em", "họ", "mình", "ta", "đó", "đây", "kia", "gì", "sao", "ai",
    "nào", "bao", "nhiêu", "vậy", "thế", "rồi", "nữa", "chỉ", "phải", "không",
}


def _build_combined_stopwords():
   
    return list(ENGLISH_STOP_WORDS.union(VIETNAMESE_STOPWORDS))

COMBINED_STOPWORDS = _build_combined_stopwords()


def build_vectorizer() -> TfidfVectorizer:
    """
    So với bản cũ (chỉ TfidfVectorizer(stop_words='english')):
    - ngram_range=(1, 2): tính thêm cụm 2 từ liền nhau (vd "spring boot", "phân tích
      dữ liệu"), giúp giữ được các thuật ngữ ghép thay vì tách rời từng từ đơn lẻ.
    - sublinear_tf=True: dùng 1 + log(tf) thay vì đếm tần suất thô, tránh 1 từ lặp
      lại quá nhiều lần (vd trong phần mô tả kinh nghiệm dài) áp đảo toàn bộ vector.
    - stop_words kết hợp Anh + Việt (xem COMBINED_STOPWORDS ở trên).
    """
    return TfidfVectorizer(
        stop_words=COMBINED_STOPWORDS,
        ngram_range=(1, 2),
        sublinear_tf=True,
        min_df=1,
    )


def scale_similarity(raw_similarity: float) -> float:
    """
    Thay cho hack log*50 cũ. Dùng phép biến đổi căn bậc hai (sqrt) — đây là kỹ thuật
    chuẩn để "nới" phân phối bị lệch phải (right-skewed) như cosine similarity của
    TF-IDF, thay vì nhân với 1 hệ số tuỳ chỉnh (50) không có căn cứ toán học. sqrt(x)
    tăng nhanh hơn x khi x nhỏ và tăng chậm dần khi x tiến gần 1, nên vẫn giữ đúng thứ
    tự tương đối (similarity cao hơn luôn cho điểm cao hơn) mà không "thổi phồng" các
    cặp CV/JD gần như không liên quan lên mức 40-90% như trước.
    """
    if raw_similarity <= 0:
        return 0.0
    return round(min(math.sqrt(raw_similarity) * 100, 100.0), 2)


def keyword_overlap_score(cv_text: str, job_desc: str) -> float:
    """
    Điểm "trùng từ khóa": trích các từ có nghĩa (>=3 ký tự, không phải stopword)
    xuất hiện trong JD, rồi tính bao nhiêu % trong số đó có mặt trong CV (so khớp
    theo word-boundary, dùng lại đúng cách get_position_rule_based đã làm).
    Đây là tín hiệu recruiter thực sự quan tâm ("CV có nhắc tới đúng công nghệ/kỹ
    năng JD yêu cầu không?"), độc lập với độ tương đồng câu chữ tổng thể của TF-IDF,
    nên kết hợp cả 2 sẽ cho điểm phản ánh đúng thực tế hơn là chỉ dùng 1 chỉ số.
    """
    if not job_desc or not job_desc.strip() or not cv_text or not cv_text.strip():
        return 0.0

    words = re.findall(r'[a-zA-Zà-ỹÀ-Ỹ0-9]+', job_desc.lower())
    keywords = {w for w in words if len(w) >= 3 and w not in VIETNAMESE_STOPWORDS}

    if not keywords:
        return 0.0

    cv_lower = cv_text.lower()
    matched = sum(1 for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', cv_lower))

    return round((matched / len(keywords)) * 100, 2)


def compute_match_score(cv_text: str, job_desc: str) -> float:
    """
    Điểm match cuối cùng = trung bình có trọng số của:
    - 55%: độ tương đồng TF-IDF (đã cải thiện: n-gram + stopwords VN/EN + sqrt scale)
      -> phản ánh mức độ giống nhau tổng thể về văn phong/nội dung.
    - 45%: tỉ lệ trùng từ khóa cụ thể của JD xuất hiện trong CV
      -> phản ánh mức độ CV có nhắc đúng công nghệ/kỹ năng JD cần.
    Trọng số nghiêng nhẹ về TF-IDF vì đây vẫn là tín hiệu chính, keyword overlap
    đóng vai trò "hiệu chỉnh" để tránh trường hợp JD ngắn (chỉ vài từ, như job crawl
    từ TopCV) khiến TF-IDF không đủ dữ liệu để so sánh chính xác.
    """
    if not cv_text or not cv_text.strip() or not job_desc or not job_desc.strip():
        return 0.0

    try:
        vectorizer = build_vectorizer()
        tfidf_matrix = vectorizer.fit_transform([cv_text, job_desc])
        raw_similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        tfidf_score = scale_similarity(float(raw_similarity))
    except Exception as e:
        print(f"Lỗi khi tính TF-IDF: {e}")
        tfidf_score = 0.0

    kw_score = keyword_overlap_score(cv_text, job_desc)

    final_score = round(0.55 * tfidf_score + 0.45 * kw_score, 2)
    return min(final_score, 100.0)


# ==========================================
# 2. CÁC MODELS (PYDANTIC SCHEMAS)
# ==========================================

class TopCvMatchRequest(BaseModel):
    keyword: str
    cv_text: Optional[str] = ""
    candidate_id: Optional[str] = ""

# ==========================================
# 3. CÁC ENDPOINTS
# ==========================================

@app.post("/classify/industry", response_model=ClassifyResponse)
def classify_industry(request: ClassifyRequest):
    label, confidence = classify_industry_svm(request.cv_text)
    if confidence < SVM_CONFIDENCE_THRESHOLD:
        label = get_industry_rule_based(request.cv_text)
        confidence = 0.3
    return ClassifyResponse(predicted_label=label, confidence=confidence)

@app.post("/classify/position", response_model=ClassifyResponse)
def classify_position(request: ClassifyRequest):
    label, confidence = classify_position_svm(request.cv_text)
    if confidence < SVM_CONFIDENCE_THRESHOLD:
        label = get_position_rule_based(request.cv_text)
        confidence = 0.3
    return ClassifyResponse(predicted_label=label, confidence=confidence)


@app.post("/parse-cv", tags=["Parsing"])
async def parse_cv(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=422, detail="Chỉ chấp nhận file PDF")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=422, detail="File rỗng")

    try:
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Không đọc được nội dung PDF: {e}")

    if not text.strip():
        raise HTTPException(status_code=422, detail="Không trích xuất được văn bản từ PDF")

    detected_position, position_conf = classify_position_svm(text)
    detected_industry, industry_conf = classify_industry_svm(text)

    # Fallback về rule-based nếu SVM không đủ tự tin, tránh trả nhãn vô nghĩa
    if position_conf < SVM_CONFIDENCE_THRESHOLD:
        detected_position = get_position_rule_based(text)
        position_conf = 0.3
    if industry_conf < SVM_CONFIDENCE_THRESHOLD:
        detected_industry = get_industry_rule_based(text)
        industry_conf = 0.3

    contact_info = extract_contact_info(text)

    return {
        "text": text,
        "industry": detected_industry,
        "industry_confidence": industry_conf,
        "position": detected_position,
        "position_confidence": position_conf,
        "email": contact_info["email"], 
        "phone": contact_info["phone"], 
    }

@app.post("/match-score", response_model=MatchResponse)
def calculate_match_score(request: MatchRequest):
    cv_text = getattr(request, "cv_text", "") or ""
    job_desc = getattr(request, "job_description", "") or getattr(request, "jobDescription", "") or ""
    
    if not cv_text.strip() or not job_desc.strip():
        return MatchResponse(match_score=0.0, match_percent=0.0)


    try:
        final_percent = compute_match_score(cv_text, job_desc)
        final_score = round(final_percent / 100, 4)

        return MatchResponse(match_score=final_score, match_percent=final_percent)

    except Exception as e:
        print(f"Error calculating match score: {e}")
        return MatchResponse(match_score=0.0, match_percent=0.0)


@app.post("/match-scores")
def calculate_batch_match_scores(request: BatchMatchRequest):
    """Score a dashboard page in one request to avoid provider request-rate limits."""
    if len(request.candidates) > 100:
        raise HTTPException(status_code=422, detail="Tối đa 100 CV cho mỗi lần đối sánh")

    job_desc = request.job_description or ""
    scores = []
    
    # 1. Tránh tính toán nếu không có Job Description
    if not job_desc.strip():
        for candidate in request.candidates:
            scores.append({"candidate_id": candidate.candidate_id, "match_percent": 0.0})
        return {"scores": scores}

    # ================= CẢI TIẾN QUAN TRỌNG VỀ HIỆU SUẤT =================
    # 2. Xây dựng và FIT vectorizer với Job Description CHỈ MỘT LẦN DUY NHẤT
    try:
        vectorizer = build_vectorizer()
        # Học tập các từ vựng có trong Job Description
        tfidf_job_matrix = vectorizer.fit_transform([job_desc]) 
    except Exception as e:
        print(f"Lỗi khi build TF-IDF chung cho batch: {e}")
        # Nếu lỗi, fallback về 0 cho an toàn
        for candidate in request.candidates:
            scores.append({"candidate_id": candidate.candidate_id, "match_percent": 0.0})
        return {"scores": scores}

    # 3. Lặp qua từng CV: Chỉ TRANSFORM (rất nhẹ) dựa trên từ vựng đã học, không FIT lại
    for candidate in request.candidates:
        cv_text = candidate.cv_text or ""
        
        if not cv_text.strip():
            scores.append({"candidate_id": candidate.candidate_id, "match_percent": 0.0})
            continue
            
        try:
            # Transform CV thành vector dựa trên bộ từ vựng của JD
            tfidf_cv_matrix = vectorizer.transform([cv_text])
            raw_similarity = cosine_similarity(tfidf_cv_matrix, tfidf_job_matrix)[0][0]
            tfidf_score = scale_similarity(float(raw_similarity))
        except Exception as e:
            print(f"Lỗi khi tính TF-IDF cho ứng viên {candidate.candidate_id}: {e}")
            tfidf_score = 0.0

        # Tính điểm Keyword (thuật toán này dùng Regex nên giữ nguyên, rất nhẹ)
        kw_score = keyword_overlap_score(cv_text, job_desc)

        # Tổng hợp điểm
        final_score = round(0.55 * tfidf_score + 0.45 * kw_score, 2)
        final_percent = min(final_score, 100.0)
        
        scores.append({"candidate_id": candidate.candidate_id, "match_percent": final_percent})

    return {"scores": scores}


@app.post("/match-topcv")
def match_topcv(request: TopCvMatchRequest):
    keyword = request.keyword
    cv_text = request.cv_text
    
    real_jobs = []
    is_real_crawl = False

    try:
        search_query = urllib.parse.quote_plus(keyword)
        url = f"https://www.topcv.vn/tim-viec-lam-{search_query}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            job_items = soup.select(".job-item-2") 
            
            for item in job_items[:10]:
                title_elem = item.select_one(".title a span")
                link_elem = item.select_one(".title a")
                company_elem = item.select_one(".company")
                
                if title_elem and link_elem and company_elem:
                    real_jobs.append({
                        "jobTitle": title_elem.text.strip(),
                        "companyName": company_elem.text.strip(),
                        "jobUrl": link_elem.get("href"),
                        "jobDescription": title_elem.text.strip()
                    })
            if real_jobs:
                is_real_crawl = True
    except Exception as e:
        print(f"Lỗi khi cào dữ liệu TopCV: {e}")

    if not real_jobs:
        search_link = f"https://www.topcv.vn/tim-viec-lam-{urllib.parse.quote_plus(keyword)}"
        real_jobs = [
            {
                "jobTitle": f"{keyword} Developer (Mid/Senior)",
                "companyName": "TechVina Corp",
                "jobDescription": f"Lập trình và tối ưu hệ thống với {keyword}. Yêu cầu 2 năm kinh nghiệm.",
                "jobUrl": search_link
            },
            {
                "jobTitle": f"Chuyên viên {keyword}",
                "companyName": "Tập đoàn Dữ liệu Số",
                "jobDescription": f"Phát triển backend, API cho ứng dụng mobile bằng {keyword}.",
                "jobUrl": search_link
            },
            {
                "jobTitle": f"Thực tập sinh {keyword} (Có lương)",
                "companyName": "FPT Software",
                "jobDescription": f"Được đào tạo bài bản về {keyword} và tham gia dự án thực tế.",
                "jobUrl": search_link
            }
        ]

    results = []
    for job in real_jobs:
        job_desc = job["jobDescription"]
        score_percent = 0.0 
        
        if cv_text and cv_text.strip():
            try:
                score_percent = compute_match_score(cv_text, job_desc)
            except Exception:
                pass

        results.append({
            "jobTitle": job["jobTitle"],
            "companyName": job["companyName"],
            "url": job["jobUrl"], 
            "score": score_percent,
            # Đánh dấu rõ nguồn dữ liệu: "TOPCV" = job cào thật, "DEMO" = job giả lập
            # fallback khi crawl TopCV thất bại. Trước đây 2 loại này bị trộn lẫn,
            # người dùng không có cách nào biết job đang xem có thật hay không.
            "source": "TOPCV" if is_real_crawl else "DEMO"
        })

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return {
        "status": "success",
        "keyword_searched": keyword,
        "content": results 
    }
