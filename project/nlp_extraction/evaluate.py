import json
import re
import config

def normalize_digits(s: str) -> str:
    return re.sub(r"\D", "", s or "")

def digits_match(pred: str, truth: str) -> bool:
    if not pred or not truth:
        return False
    p, t = normalize_digits(pred), normalize_digits(truth)
    if not p or not t:
        return False
    return p in t or t in p

def text_match(pred: str, truth: str) -> bool:
    if not pred or not truth:
        return False
    p, t = pred.lower().strip(), truth.lower().strip()
    return p in t or t in p

def evaluate_single_value_field(pairs, match_fn):
    """pairs: list các tuple (predicted, ground_truth) - mỗi CV 1 giá trị."""
    tp = fp = fn = 0
    for pred, truth in pairs:
        if truth is None:
            continue
        if pred is not None and match_fn(pred, truth):
            tp += 1
        elif pred is not None and truth is not None:
            fp += 1
            fn += 1
        elif pred is None:
            fn += 1
    return tp, fp, fn


def evaluate_set_field(pairs, match_fn):
    """pairs: list các tuple (predicted_list, ground_truth_list) - mỗi CV 1 tập hợp."""
    tp = fp = fn = 0
    for pred_list, truth_list in pairs:
        pred_list = pred_list or []
        truth_list = truth_list or []
        matched_truth_idx = set()

        for pred in pred_list:
            found = False
            for i, truth in enumerate(truth_list):
                if i in matched_truth_idx:
                    continue
                if match_fn(pred, truth):
                    matched_truth_idx.add(i)
                    found = True
                    break
            if found:
                tp += 1
            else:
                fp += 1

        fn += len(truth_list) - len(matched_truth_idx)

    return tp, fp, fn


def precision_recall_f1(tp, fp, fn):
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return round(precision, 4), round(recall, 4), round(f1, 4)


def main():
    with open(config.GROUND_TRUTH_JSON, "r", encoding="utf-8") as f:
        ground_truth = json.load(f)
    with open(config.EXTRACTED_JSON_PATH, "r", encoding="utf-8") as f:
        extracted = json.load(f)

    gt_by_id = {cv["cv_id"]: cv for cv in ground_truth}
    pred_by_id = {cv["cv_id"]: cv for cv in extracted}

    common_ids = [cid for cid in gt_by_id if cid in pred_by_id]
    print(f"Đánh giá trên {len(common_ids)}/{len(gt_by_id)} CV có đủ cả ground-truth và kết quả trích xuất.\n")

    email_pairs, phone_pairs = [], []
    skill_pairs, job_title_pairs = [], []

    for cid in common_ids:
        gt, pred = gt_by_id[cid], pred_by_id[cid]

        email_pairs.append((pred.get("email"), gt.get("email")))
        phone_pairs.append((pred.get("phone"), gt.get("phone")))

        skill_pairs.append((pred.get("skills"), gt.get("skills")))

        gt_titles = [gt.get("job_title")] + [e.get("title") for e in gt.get("experience", [])]
        gt_titles = [t for t in gt_titles if t]
        job_title_pairs.append((pred.get("job_titles"), gt_titles))

    report = {}

    for field_name, tp_fp_fn in [
        ("email", evaluate_single_value_field(email_pairs, text_match)),
        ("phone", evaluate_single_value_field(phone_pairs, digits_match)),
        ("skills", evaluate_set_field(skill_pairs, text_match)),
        ("job_titles", evaluate_set_field(job_title_pairs, text_match)),
    ]:
        tp, fp, fn = tp_fp_fn
        precision, recall, f1 = precision_recall_f1(tp, fp, fn)
        report[field_name] = {
            "TP": tp, "FP": fp, "FN": fn,
            "precision": precision, "recall": recall, "f1": f1,
        }

    # --- In bảng kết quả ---
    print(f"{'Trường':<12}{'TP':>6}{'FP':>6}{'FN':>6}{'Precision':>12}{'Recall':>10}{'F1':>8}")
    print("-" * 60)
    for field_name, m in report.items():
        print(f"{field_name:<12}{m['TP']:>6}{m['FP']:>6}{m['FN']:>6}"
              f"{m['precision']:>12.2%}{m['recall']:>10.2%}{m['f1']:>8.2%}")

    with open(config.EVAL_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\nĐã lưu báo cáo chi tiết tại: {config.EVAL_REPORT_PATH}")
    print("\nLưu ý: github/linkedin chưa có ground-truth nên không đánh giá được ở bước này.")


if __name__ == "__main__":
    main()