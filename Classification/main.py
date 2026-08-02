from contextlib import asynccontextmanager
import joblib
from fastapi import FastAPI, HTTPException
import config
import matching
from schemas import ClassifyRequest, ClassifyResponse, MatchRequest, MatchResponse

_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        _models["industry_clf"] = joblib.load(config.INDUSTRY_MODEL_PATH)
        _models["industry_vec"] = joblib.load(config.INDUSTRY_VECTORIZER_PATH)
        print("Đã load industry classifier.")
    except FileNotFoundError:
        print("CẢNH BÁO: chưa có industry classifier - chạy train_industry_classifier.py trước.")

    try:
        _models["position_clf"] = joblib.load(config.POSITION_MODEL_PATH)
        _models["position_vec"] = joblib.load(config.POSITION_VECTORIZER_PATH)
        print("Đã load position classifier.")
    except FileNotFoundError:
        print("CẢNH BÁO: chưa có position classifier - chạy train_position_classifier.py trước.")

    yield  

    _models.clear()  

app = FastAPI(title=config.API_TITLE, version=config.API_VERSION, lifespan=lifespan)

def _classify(text: str, clf_key: str, vec_key: str) -> ClassifyResponse:
    if clf_key not in _models:
        raise HTTPException(
            status_code=503,
            detail=f"Model '{clf_key}' chưa được huấn luyện. Chạy script train tương ứng trước.",
        )

    vectorizer = _models[vec_key]
    clf = _models[clf_key]

    x_vec = vectorizer.transform([text])
    predicted = clf.predict(x_vec)[0]
    probs = clf.predict_proba(x_vec)[0]
    confidence = float(max(probs))

    return ClassifyResponse(predicted_label=predicted, confidence=round(confidence, 4))

@app.post("/classify/industry", response_model=ClassifyResponse, tags=["Classification"])
def classify_industry(payload: ClassifyRequest):
    return _classify(payload.text, "industry_clf", "industry_vec")

@app.post("/classify/position", response_model=ClassifyResponse, tags=["Classification"])
def classify_position(payload: ClassifyRequest):
    return _classify(payload.text, "position_clf", "position_vec")

@app.post("/match-score", response_model=MatchResponse, tags=["Matching"])
def match_score(payload: MatchRequest):
    result = matching.compute_match_score(payload.cv_text, payload.jd_text)
    return MatchResponse(**result)

@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "ok",
        "industry_model_loaded": "industry_clf" in _models,
        "position_model_loaded": "position_clf" in _models,
    }
