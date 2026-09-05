import regex_extractor
import ner_extractor

def extract_cv_fields(raw_text: str) -> dict:
    regex_fields = regex_extractor.extract_all(raw_text)
    entity_fields = ner_extractor.extract_all_entities(raw_text)

    full_name_guess = None
    if entity_fields["persons"]:
        full_name_guess = entity_fields["persons"][0].split("\n")[0].strip()

    return {
        "full_name": full_name_guess,
        "email": regex_fields["emails"][0] if regex_fields["emails"] else None,
        "phone": regex_fields["phones"][0] if regex_fields["phones"] else None,
        "github_usernames": regex_fields["github_usernames"],
        "linkedin_usernames": regex_fields["linkedin_usernames"],
        "skills": entity_fields["skills"],
        "job_titles": entity_fields["job_titles"],
        "orgs": entity_fields["orgs"],
        "dates": entity_fields["dates"],
    }


if __name__ == "__main__":
    import json

    sample = (
        "Dawn Berry\n"
        "dawn.berry123@example.org | 001-275-674-1329x1486 | Cybersecurity Analyst (Senior)\n\n"
        "SUMMARY\n"
        "Highly analytical Senior Cybersecurity Analyst with over 8 years of experience.\n\n"
        "SKILLS\n"
        "Splunk (SIEM), Wireshark, Vulnerability Assessment (Nessus), Cloud Security (AWS)\n\n"
        "EXPERIENCE\n"
        "Senior Cybersecurity Analyst - Aetheris Security Solutions (2020-11 - Present)\n"
    )
    print(json.dumps(extract_cv_fields(sample), indent=2, ensure_ascii=False))