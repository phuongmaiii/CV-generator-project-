from pydantic import BaseModel, Field

class ClassifyRequest(BaseModel):
    text: str = Field(..., description="Nội dung CV (văn bản thuần)", min_length=1)

class ClassifyResponse(BaseModel):
    predicted_label: str
    confidence: float = Field(..., description="Xác suất dự đoán cao nhất (0-1)")

class MatchRequest(BaseModel):
    cv_text: str = Field(..., description="Nội dung CV", min_length=1)
    jd_text: str = Field(..., description="Nội dung Job Description", min_length=1)

class MatchResponse(BaseModel):
    match_score: float = Field(..., description="Cosine similarity, khoảng 0-1")
    match_percent: float = Field(..., description="match_score quy về thang 0-100")
