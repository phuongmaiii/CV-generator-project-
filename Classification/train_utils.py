import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import config

def train_and_evaluate(texts: list, labels: list, model_path: str, vectorizer_path: str,
                        test_size: float = 0.2) -> dict:
    x_train, x_test, y_train, y_test = train_test_split(
        texts, labels, test_size=test_size, random_state=42, stratify=labels
    )

    vectorizer = TfidfVectorizer(
        max_features=config.TFIDF_MAX_FEATURES,
        ngram_range=config.TFIDF_NGRAM_RANGE,
        stop_words="english",
    )
    x_train_vec = vectorizer.fit_transform(x_train)
    x_test_vec = vectorizer.transform(x_test)

    clf = SVC(kernel=config.SVM_KERNEL, C=config.SVM_C, probability=True)
    clf.fit(x_train_vec, y_train)

    y_pred = clf.predict(x_test_vec)
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)

    print(classification_report(y_test, y_pred, zero_division=0))

    joblib.dump(clf, model_path)
    joblib.dump(vectorizer, vectorizer_path)
    print(f"Đã lưu model tại: {model_path}")
    print(f"Đã lưu vectorizer tại: {vectorizer_path}")

    return report
