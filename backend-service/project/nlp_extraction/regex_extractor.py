import re

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

PHONE_RE = re.compile(
    r"(?:\+?\d{1,3}[\s.-]?)?"          
    r"(?:\(?\d{2,4}\)?[\s.-]?){2,4}"   
    r"\d{2,4}"
    r"(?:\s?x\d{1,6})?",              
    re.IGNORECASE,
)

GITHUB_RE = re.compile(
    r"(?:https?://)?(?:www\.)?github\.com/([A-Za-z0-9_-]+)",
    re.IGNORECASE,
)

LINKEDIN_RE = re.compile(
    r"(?:https?://)?(?:www\.)?linkedin\.com/in/([A-Za-z0-9_-]+)",
    re.IGNORECASE,
)


def extract_emails(text: str) -> list:
    return list(dict.fromkeys(EMAIL_RE.findall(text)))  # loại trùng, giữ thứ tự


def extract_phones(text: str) -> list:
    candidates = PHONE_RE.findall(text)
    results = []
    for c in candidates:
        digits = re.sub(r"\D", "", c)
        if len(digits) >= 8:
            results.append(c.strip())
    return list(dict.fromkeys(results))


def extract_github(text: str) -> list:
    return list(dict.fromkeys(GITHUB_RE.findall(text)))


def extract_linkedin(text: str) -> list:
    return list(dict.fromkeys(LINKEDIN_RE.findall(text)))


def extract_all(text: str) -> dict:
    return {
        "emails": extract_emails(text),
        "phones": extract_phones(text),
        "github_usernames": extract_github(text),
        "linkedin_usernames": extract_linkedin(text),
    }


if __name__ == "__main__":
    sample = (
        "Dawn Berry\n"
        "dawn.berry123@example.org | 001-275-674-1329x1486 | Cybersecurity Analyst\n"
        "GitHub: github.com/dawnberry-dev | LinkedIn: linkedin.com/in/dawn-berry-cyber"
    )
    print(extract_all(sample))