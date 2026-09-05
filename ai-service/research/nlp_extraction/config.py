import os

DATA_DIR = r"D:\CV-generator-project--main\CV-generator-project--main\data"
PDF_DIR = os.path.join(DATA_DIR, "synthetic_cv_pdfs")
GROUND_TRUTH_JSON = os.path.join(DATA_DIR, "synthetic_cvs.json")

OUTPUT_DIR = os.path.join(DATA_DIR, "nlp_extraction_output")
EXTRACTED_JSON_PATH = os.path.join(OUTPUT_DIR, "extracted_results.json")
EVAL_REPORT_PATH = os.path.join(OUTPUT_DIR, "evaluation_report.json")

os.makedirs(OUTPUT_DIR, exist_ok=True)

#Fine-tune NER 
FINETUNE_SAMPLE_SIZE = 70  
FINETUNE_ITERATIONS = 20
FINETUNED_MODEL_DIR = os.path.join(DATA_DIR, "ner_finetuned_model")

#spaCy
SPACY_MODEL = FINETUNED_MODEL_DIR
DEFAULT_LANG = "en"

SKILL_LEXICON = [
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust", "PHP",
    "SQL", "NoSQL", "MongoDB", "PostgreSQL", "MySQL", "Redis", "Elasticsearch",
    "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Terraform", "Ansible", "Jenkins",
    "CI/CD", "Git", "Linux", "Bash", "PowerShell",
    "React", "Angular", "Vue", "Node.js", "Django", "Flask", "Spring Boot", ".NET",
    "TensorFlow", "PyTorch", "scikit-learn", "Pandas", "NumPy",
    "Spark", "Hadoop", "Kafka", "RabbitMQ",
    "GraphQL", "REST API", "Microservices", "Agile", "Scrum",
    "Selenium", "JUnit", "Pytest",
    "Splunk", "Wireshark", "Nessus", "Penetration Testing", "Vulnerability Assessment",
    "Firewall Administration", "SIEM", "Cloud Security", "Network Security",
    "Android", "iOS", "Swift", "Kotlin", "Flutter", "React Native",
    "HTML", "CSS", "Sass", "Webpack", "Figma",
    "Jira", "Confluence", "Tableau", "Power BI", "Excel",
    "ETL", "Data Warehousing", "Machine Learning", "Deep Learning", "NLP",
    "Computer Vision", "Cybersecurity", "DevOps", "SRE",
    "Chef", "Puppet", "Logstash", "Kibana", "Prometheus", "Grafana",
    "Nginx", "Apache", "Oracle Database", "T-SQL", "PL/SQL",
]

JOB_TITLE_LEXICON = [
    "Backend Developer", "Frontend Developer", "Full-stack Developer", "Full Stack Developer",
    "Software Engineer", "Software Developer", "Software Architect",
    "Data Analyst", "Data Engineer", "Data Scientist",
    "DevOps Engineer", "Site Reliability Engineer", "SRE",
    "QA Engineer", "Test Engineer", "QA / Test Engineer",
    "Mobile Developer", "Android Developer", "iOS Developer",
    "Machine Learning Engineer", "Cloud Engineer", "System Administrator",
    "Cybersecurity Analyst", "Security Analyst", "Business Analyst",
    "IT Project Manager", "Project Manager",
    "Database Administrator", "Embedded Software Engineer",
]

#Stopwords
EN_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "so", "of", "to", "in",
    "on", "at", "for", "with", "as", "by", "is", "are", "was", "were", "be",
    "been", "being", "this", "that", "these", "those", "it", "its", "from",
    "into", "over", "under", "about", "than", "such", "not", "no", "do", "does",
    "did", "has", "have", "had", "will", "would", "can", "could", "should",
}

VI_STOPWORDS = {
    "và", "của", "là", "có", "được", "cho", "trong", "với", "các", "những",
    "một", "này", "đã", "khi", "để", "như", "về", "đến", "từ", "tại", "theo",
    "hoặc", "nhưng", "nếu", "thì", "sẽ", "đang", "bị", "do",
}