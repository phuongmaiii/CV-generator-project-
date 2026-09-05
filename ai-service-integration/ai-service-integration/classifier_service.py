"""
classifier_service.py

Loads the industry and position SVM classifiers (+ their TF-IDF vectorizers)
once at import time, and exposes simple predict functions.

Model files expected at ai-service/models/:
    industry_svm.joblib      (24 industry classes, e.g. INFORMATION-TECHNOLOGY)
    industry_tfidf.joblib
    position_svm.joblib      (19 IT position classes, e.g. Backend Developer)
    position_tfidf.joblib

Drop this file into your ai-service package (next to main.py) and import
classify_industry / classify_position from it in the endpoint that currently
returns mocked results.
"""

from pathlib import Path
import joblib

MODELS_DIR = Path(__file__).parent / "models"

_industry_model = joblib.load(MODELS_DIR / "industry_svm.joblib")
_industry_vectorizer = joblib.load(MODELS_DIR / "industry_tfidf.joblib")
_position_model = joblib.load(MODELS_DIR / "position_svm.joblib")
_position_vectorizer = joblib.load(MODELS_DIR / "position_tfidf.joblib")


def _predict(model, vectorizer, text: str, top_k: int = 3) -> dict:
    """Run one classifier and return the top label plus a top_k probability
    breakdown (works because both SVCs were trained with probability=True)."""
    X = vectorizer.transform([text])
    proba = model.predict_proba(X)[0]
    classes = model.classes_
    ranked = sorted(zip(classes, proba), key=lambda kv: kv[1], reverse=True)
    return {
        "label": ranked[0][0],
        "confidence": round(float(ranked[0][1]), 4),
        "top_k": [{"label": c, "probability": round(float(p), 4)} for c, p in ranked[:top_k]],
    }


def classify_industry(text: str, top_k: int = 3) -> dict:
    """Predict which of the 24 industry categories a resume belongs to."""
    return _predict(_industry_model, _industry_vectorizer, text, top_k)


def classify_position(text: str, top_k: int = 3) -> dict:
    """Predict which of the 19 IT position categories a resume belongs to."""
    return _predict(_position_model, _position_vectorizer, text, top_k)
