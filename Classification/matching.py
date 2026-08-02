import numpy as np
import embedding_utils

def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    return float(np.dot(vec_a, vec_b))

def compute_match_score(cv_text: str, jd_text: str) -> dict:
    cv_vec = embedding_utils.embed_cv(cv_text)
    jd_vec = embedding_utils.embed_jd(jd_text)

    score = cosine_similarity(cv_vec, jd_vec)
    return {
        "match_score": round(score, 4),
        "match_percent": round(score * 100, 2),
    }

def rank_cvs_for_jd(cv_texts: dict, jd_text: str) -> list:
    jd_vec = embedding_utils.embed_jd(jd_text)

    results = []
    for cv_id, text in cv_texts.items():
        cv_vec = embedding_utils.embed_cv(text)
        score = cosine_similarity(cv_vec, jd_vec)
        results.append({"cv_id": cv_id, "match_score": round(score, 4)})

    return sorted(results, key=lambda x: x["match_score"], reverse=True)

if __name__ == "__main__":
    cv = "Backend Developer with 4 years of experience in Python, Django, PostgreSQL, Docker."
    jd_good = "Hiring a Backend Developer skilled in Python, Django, and relational databases."
    jd_bad = "Hiring a Senior Graphic Designer skilled in Photoshop and Illustrator."

    print("Match với JD phù hợp:", compute_match_score(cv, jd_good))
    print("Match với JD không phù hợp:", compute_match_score(cv, jd_bad))
