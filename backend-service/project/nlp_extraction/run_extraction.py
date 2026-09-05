import json
import os
import pdfplumber
from tqdm import tqdm
import config
from extract_one import extract_cv_fields

def read_pdf_text(pdf_path: str) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)

def main():
    with open(config.GROUND_TRUTH_JSON, "r", encoding="utf-8") as f:
        ground_truth = json.load(f)

    print(f"Đã load {len(ground_truth)} CV ground-truth. Bắt đầu trích xuất...")

    all_results = []
    missing_pdfs = []

    for cv in tqdm(ground_truth):
        pdf_path = os.path.join(config.PDF_DIR, f"{cv['cv_id']}.pdf")
        if not os.path.exists(pdf_path):
            missing_pdfs.append(cv["cv_id"])
            continue

        raw_text = read_pdf_text(pdf_path)
        extracted = extract_cv_fields(raw_text)
        extracted["cv_id"] = cv["cv_id"]
        all_results.append(extracted)

    with open(config.EXTRACTED_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print(f"Đã trích xuất xong {len(all_results)}/{len(ground_truth)} CV.")
    if missing_pdfs:
        print(f"Thiếu file PDF cho {len(missing_pdfs)} CV (bỏ qua): {missing_pdfs[:10]}")
    print(f"Kết quả lưu tại: {config.EXTRACTED_JSON_PATH}")


if __name__ == "__main__":
    main()