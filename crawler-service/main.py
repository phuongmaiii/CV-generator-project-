from fastapi import FastAPI, UploadFile, File, Form
import PyPDF2
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json

app = FastAPI()

print("Đang tải AI Model...")
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
print("Tải Model thành công!")

@app.post("/match")
async def match_cv_to_jobs(cv_file: UploadFile = File(...), jobs_data: str = Form(...)):
    pdf_reader = PyPDF2.PdfReader(cv_file.file)
    cv_text = ""
    for page in pdf_reader.pages:
        cv_text += page.extract_text() or ""
        
    if not cv_text.strip():
        return {"error": "Không thể đọc văn bản từ CV này."}
        
    try:
        jobs = json.loads(jobs_data)
        if not isinstance(jobs, list):
            jobs = [{"id": 1, "requirements": jobs_data}]
    except:
        jobs = [{"id": 1, "requirements": jobs_data}]
    
    cv_vector = model.encode([cv_text])
    results = []
    for job in jobs:
        req_text = job.get('requirements', '') if isinstance(job, dict) else str(job)
        if not req_text:
            continue
        job_vector = model.encode([req_text])
        sim_score = cosine_similarity(cv_vector, job_vector)[0][0]
        final_score = max(0, min(100, round(float(sim_score) * 100 + 15, 1))) 
        results.append({
            "jobId": job.get('id', 1),
            "matchScore": final_score
        })
        
    results.sort(key=lambda x: x["matchScore"], reverse=True)
    
    # Đảm bảo trả về cấu trúc có chứa match_score để Java đọc được
    best_score = results[0]["matchScore"] if results else 0.0
    return {
        "match_score": best_score,
        "results": results
    }