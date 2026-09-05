import json
import os
import random
import pdfplumber
from tqdm import tqdm
import config

def read_pdf_text(pdf_path: str) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)


def _find_span(text: str, phrase: str, label: str):
    if not phrase:
        return None
    idx = text.find(phrase)
    if idx != -1:
        return (idx, idx + len(phrase), label)

    core = phrase.split("(")[0].strip()
    if core and core != phrase:
        idx = text.find(core)
        if idx != -1:
            return (idx, idx + len(core), label)
    return None

def _remove_overlaps(spans: list) -> list:
    spans = sorted(spans, key=lambda s: s[0])
    result, last_end = [], -1
    for start, end, label in spans:
        if start >= last_end:
            result.append((start, end, label))
            last_end = end
    return result

def build_training_data(ground_truth: list, sample_size: int) -> list:
    sample = ground_truth[:sample_size]  # 50-80 CV đầu tiên theo yêu cầu
    training_data = []

    print(f"Đang chuẩn bị dữ liệu huấn luyện từ {len(sample)} CV...")
    for cv in tqdm(sample):
        pdf_path = os.path.join(config.PDF_DIR, f"{cv['cv_id']}.pdf")
        if not os.path.exists(pdf_path):
            continue
        text = read_pdf_text(pdf_path)

        spans = []
        for skill in cv.get("skills", []):
            span = _find_span(text, skill, "SKILL")
            if span:
                spans.append(span)

        titles = [cv.get("job_title")] + [e.get("title") for e in cv.get("experience", [])]
        for title in titles:
            span = _find_span(text, title, "JOB_TITLE") if title else None
            if span:
                spans.append(span)

        spans = _remove_overlaps(spans)
        if spans:
            training_data.append((text, {"entities": spans}))

    print(f"Đã tạo được {len(training_data)} training example (có ít nhất 1 nhãn).")
    return training_data


def finetune(training_data: list):
    import spacy
    from spacy.training import Example
    from spacy.util import minibatch

    nlp = spacy.load(config.SPACY_MODEL)
    ner = nlp.get_pipe("ner")
    for _, annotations in training_data:
        for _, _, label in annotations["entities"]:
            ner.add_label(label)

    other_pipes = [p for p in nlp.pipe_names if p != "ner"]
    with nlp.disable_pipes(*other_pipes):
        optimizer = nlp.resume_training()
        for it in range(config.FINETUNE_ITERATIONS):
            random.shuffle(training_data)
            losses = {}
            for batch in minibatch(training_data, size=8):
                examples = []
                for text, annotations in batch:
                    doc = nlp.make_doc(text)
                    examples.append(Example.from_dict(doc, annotations))
                nlp.update(examples, drop=0.35, losses=losses, sgd=optimizer)
            print(f"  Iteration {it + 1}/{config.FINETUNE_ITERATIONS} - losses: {losses}")

    os.makedirs(config.FINETUNED_MODEL_DIR, exist_ok=True)
    nlp.to_disk(config.FINETUNED_MODEL_DIR)
    print(f"Đã lưu model fine-tune tại: {config.FINETUNED_MODEL_DIR}")


def main():
    with open(config.GROUND_TRUTH_JSON, "r", encoding="utf-8") as f:
        ground_truth = json.load(f)

    training_data = build_training_data(ground_truth, config.FINETUNE_SAMPLE_SIZE)
    if not training_data:
        print("Không tạo được dữ liệu huấn luyện nào - kiểm tra lại đường dẫn PDF.")
        return

    finetune(training_data)
    print(
        "\nHoàn tất. Để dùng model đã fine-tune, sửa trong config.py:\n"
        "    SPACY_MODEL = FINETUNED_MODEL_DIR\n"
        "rồi chạy lại run_extraction.py + evaluate.py để so sánh kết quả trước/sau."
    )


if __name__ == "__main__":
    main()