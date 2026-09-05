import re
from functools import lru_cache
import config
import spacy

@lru_cache(maxsize=1)
def get_spacy_model():
    try:
        return spacy.load(config.SPACY_MODEL)
    except OSError as e:
        raise RuntimeError(
            f"Chưa cài model '{config.SPACY_MODEL}'. Chạy lệnh:\n"
            f"    python -m spacy download {config.SPACY_MODEL}"
        ) from e


def extract_spacy_entities(text: str) -> dict:
    nlp = get_spacy_model()
    doc = nlp(text)

    result = {
        "persons": [], "orgs": [], "dates": [], "gpes": [],
        "skills_spacy": [], "job_titles_spacy": [],
    }
    label_map = {
        "PERSON": "persons", "ORG": "orgs", "DATE": "dates", "GPE": "gpes",
        "SKILL": "skills_spacy", "JOB_TITLE": "job_titles_spacy",
    }

    for ent in doc.ents:
        key = label_map.get(ent.label_)
        if key and ent.text not in result[key]:
            result[key].append(ent.text)

    return result


def _build_lexicon_pattern(lexicon: list) -> re.Pattern:
    sorted_terms = sorted(lexicon, key=len, reverse=True)
    escaped = [re.escape(term) for term in sorted_terms]
    pattern = r"(?<![\w])(" + "|".join(escaped) + r")(?![\w])"
    return re.compile(pattern, re.IGNORECASE)


_SKILL_PATTERN = _build_lexicon_pattern(config.SKILL_LEXICON)
_JOB_TITLE_PATTERN = _build_lexicon_pattern(config.JOB_TITLE_LEXICON)


def extract_skills_rulebased(text: str) -> list:
    matches = _SKILL_PATTERN.findall(text)
    seen, result = set(), []
    for m in matches:
        key = m.lower()
        if key not in seen:
            seen.add(key)
            result.append(m)
    return result


def extract_job_titles_rulebased(text: str) -> list:
    matches = _JOB_TITLE_PATTERN.findall(text)
    seen, result = set(), []
    for m in matches:
        key = m.lower()
        if key not in seen:
            seen.add(key)
            result.append(m)
    return result


def _merge_dedupe(items: list) -> list:
    seen, result = set(), []
    for item in items:
        key = item.lower().strip()
        if key and key not in seen:
            seen.add(key)
            result.append(item)
    return result


def extract_all_entities(text: str) -> dict:
    spacy_result = extract_spacy_entities(text)

    skills = _merge_dedupe(
        extract_skills_rulebased(text) + spacy_result["skills_spacy"]
    )
    job_titles = _merge_dedupe(
        extract_job_titles_rulebased(text) + spacy_result["job_titles_spacy"]
    )

    return {
        "persons": spacy_result["persons"],
        "orgs": spacy_result["orgs"],
        "dates": spacy_result["dates"],
        "gpes": spacy_result["gpes"],
        "skills": skills,
        "job_titles": job_titles,
    }


if __name__ == "__main__":
    sample = (
        "Dawn Berry\n"
        "Senior Cybersecurity Analyst with experience at Aetheris Security Solutions.\n"
        "Skills: Splunk (SIEM), Wireshark, Cloud Security (AWS), Python (Security Automation)."
    )
    import json
    print(json.dumps(extract_all_entities(sample), indent=2, ensure_ascii=False))