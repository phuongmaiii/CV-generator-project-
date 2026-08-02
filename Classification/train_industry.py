import config
import data_prep
import train_utils

def main():
    print("Đang load dữ liệu Kaggle (toàn bộ 24 ngành)...")
    texts, labels = data_prep.load_industry_dataset()
    print(f"Tổng số CV: {len(texts)}, số ngành: {len(set(labels))}")

    print("\nBắt đầu huấn luyện TF-IDF + SVM...\n")
    train_utils.train_and_evaluate(
        texts, labels,
        model_path=config.INDUSTRY_MODEL_PATH,
        vectorizer_path=config.INDUSTRY_VECTORIZER_PATH,
    )

if __name__ == "__main__":
    main()
