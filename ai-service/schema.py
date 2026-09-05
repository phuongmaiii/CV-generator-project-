from pydantic import BaseModel, Field
from typing import Optional, List

class ClassifyRequest(BaseModel):
    cv_text: str

class ClassifyResponse(BaseModel):
    predicted_label: str
    confidence: float

class MatchRequest(BaseModel):
    # Sử dụng alias để map tự động cvText và jobDescription từ Spring Boot
    cv_text: Optional[str] = Field(default="", alias="cvText")
    job_description: Optional[str] = Field(default="", alias="jobDescription")

    class Config:
        populate_by_name = True  # Cho phép sử dụng cả 2 chuẩn tên (camelCase và snake_case)

class MatchResponse(BaseModel):
    match_score: float
    match_percent: float

class BatchMatchItem(BaseModel):
    candidate_id: int
    cv_text: str

class BatchMatchRequest(BaseModel):
    job_description: str
    candidates: List[BatchMatchItem]
