import json
import os
import pandas as pd
import pdfplumber
import config

def load_industry_dataset() -> tuple:
    if not os.path.exists(config.KAGGLE_FULL_CSV):
        raise FileNotFoundError(
            f"Không tìm thấy {config.KAGGLE_FULL_CSV}. "
            "Chạy cv_pipeline/step1_kaggle_download.py trước (Tuần 1)."
        )

    df = pd.read_csv(config.KAGGLE_FULL_CSV)
    df.columns = [c.strip() for c in df.columns]
    df = df.dropna(subset=["Resume_str", "Category"])

    texts = df["Resume_str"].tolist()
    labels = df["Category"].tolist()
    return texts, labels

def _read_pdf_text(pdf_path: str) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)

def load_position_dataset() -> tuple:
    with open(config.SYNTHETIC_JSON, "r", encoding="utf-8") as f:
        ground_truth = json.load(f)

    texts, labels = [], []
    for cv in ground_truth:
        pdf_path = os.path.join(config.SYNTHETIC_PDF_DIR, f"{cv['cv_id']}.pdf")
        if not os.path.exists(pdf_path):
            continue
        texts.append(_read_pdf_text(pdf_path))
        labels.append(cv["job_title"])

    return texts, labels

if __name__ == "__main__":
    texts, labels = load_industry_dataset()
    print(f"[Industry] {len(texts)} CV, {len(set(labels))} ngành: {sorted(set(labels))[:5]}...")

    texts, labels = load_position_dataset()
    print(f"[Position] {len(texts)} CV, {len(set(labels))} vị trí: {sorted(set(labels))[:5]}...")
