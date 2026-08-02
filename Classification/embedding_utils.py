from functools import lru_cache
import config

@lru_cache(maxsize=1)
def get_embedding_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(config.E5_MODEL_NAME)

def embed_texts(texts: list, is_query: bool = False):
    model = get_embedding_model()
    prefix = "query: " if is_query else "passage: "
    prefixed = [prefix + t for t in texts]
    return model.encode(prefixed, normalize_embeddings=True)

def embed_cv(cv_text: str):
    return embed_texts([cv_text], is_query=False)[0]

def embed_jd(jd_text: str):
    return embed_texts([jd_text], is_query=True)[0]

if __name__ == "__main__":
    cv_vec = embed_cv("Backend Developer with 4 years of experience in Python, Django, PostgreSQL.")
    jd_vec = embed_jd("Looking for a Backend Developer skilled in Python and SQL databases.")
    print("Kích thước vector:", cv_vec.shape)
    print("5 giá trị đầu của CV vector:", cv_vec[:5])
