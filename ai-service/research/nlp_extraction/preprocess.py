import re
import unicodedata
import config

def normalize_unicode(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def to_lowercase(text: str) -> str:
    return text.lower()


def tokenize(text: str, lang: str = None) -> list:
    lang = lang or config.DEFAULT_LANG

    if lang == "vi":
        from underthesea import word_tokenize
        return word_tokenize(text)
    return re.findall(r"\b[\w'-]+\b", text)


def remove_stopwords(tokens: list, lang: str = None) -> list:
    lang = lang or config.DEFAULT_LANG
    stopwords = config.VI_STOPWORDS if lang == "vi" else config.EN_STOPWORDS
    return [t for t in tokens if t.lower() not in stopwords]


def preprocess_pipeline(text: str, lang: str = None) -> dict:
    lang = lang or config.DEFAULT_LANG

    normalized = normalize_unicode(text)
    lowered = to_lowercase(normalized)
    tokens = tokenize(lowered, lang=lang)
    tokens_clean = remove_stopwords(tokens, lang=lang)

    return {
        "normalized_text": normalized,
        "lowercased_text": lowered,
        "tokens": tokens,
        "tokens_no_stopwords": tokens_clean,
        "clean_text": " ".join(tokens_clean),
    }


if __name__ == "__main__":
    sample = "Senior Cybersecurity Analyst with 8 years of experience in Splunk (SIEM) and AWS."
    result = preprocess_pipeline(sample, lang="en")
    print("Tokens:", result["tokens"][:10])
    print("Sau khi xóa stopword:", result["tokens_no_stopwords"][:10])
    print("Clean text:", result["clean_text"])