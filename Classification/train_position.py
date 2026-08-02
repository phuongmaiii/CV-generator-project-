import config
import data_prep
import train_utils

def main():
    print("Đang load dữ liệu CV tổng hợp ngành IT...")
    texts, labels = data_prep.load_position_dataset()
    print(f"Tổng số CV: {len(texts)}, số vị trí: {len(set(labels))}")

    if len(texts) < 40:
        print(
            "CẢNH BÁO: số lượng CV khá ít cho việc train/test split ổn định. "
            "Kết quả chỉ mang tính minh họa."
        )

    print("\nBắt đầu huấn luyện TF-IDF + SVM...\n")
    train_utils.train_and_evaluate(
        texts, labels,
        model_path=config.POSITION_MODEL_PATH,
        vectorizer_path=config.POSITION_VECTORIZER_PATH,
    )

if __name__ == "__main__":
    main()
