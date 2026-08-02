import os

DATA_DIR = r"D:\CV-generator-project--main\CV-generator-project--main\data"

KAGGLE_FULL_CSV = os.path.join(DATA_DIR,"kaggle_raw","Resume","Resume.csv")
SYNTHETIC_JSON = os.path.join(DATA_DIR,"synthetic_cvs.json")
SYNTHETIC_PDF_DIR=os.path.join(DATA_DIR,"synthetic_cv_pdfs")

MODEL_DIR = os.path.join(DATA_DIR,"models")
os.makedirs(MODEL_DIR,exist_ok=True)

INDUSTRY_MODEL_PATH = os.path.join(MODEL_DIR,"industry_svm.joblib")
INDUSTRY_VECTORIZER_PATH = os.path.join(MODEL_DIR,"industry_tfidf.joblib")

POSITION_MODEL_PATH = os.path.join(MODEL_DIR,"position_svm.joblib")
POSITION_VECTORIZER_PATH= os.path.join(MODEL_DIR,"position_tfidf.joblib")

TFIDF_MAX_FEATURES= 5000
TFIDF_NGRAM_RANGE = (1,2)

SVM_KERNEL = "linear"
SVM_C=1.0

E5_MODEL_NAME= "intfloat/multilingual-e5-base"

API_TITLE ="CV Classification & Matching"
API_VERSION= "1.0.0"