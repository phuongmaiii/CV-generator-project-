
import os
import re
import zipfile
import glob
import json
import time
import shutil
import random
import pdfplumber
from google import genai
from getpass import getpass
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT 
import pandas as pd
from dotenv import load_dotenv
from faker import Faker
from tqdm import tqdm
 
load_dotenv()
DATA_DIR = "./data"
os.makedirs(DATA_DIR, exist_ok=True)
 
print("Đã import xong thư viện, thư mục làm việc:", os.path.abspath(DATA_DIR))

#ket noi kaggle va xu ly raw data
if not os.environ.get("KAGGLE_USERNAME"):
    os.environ["KAGGLE_USERNAME"] = input("Nhập Kaggle username: ").strip()
if not os.environ.get("KAGGLE_KEY"):
    os.environ["KAGGLE_KEY"] = getpass("Nhập Kaggle API key: ").strip()
print("Đã cấu hình Kaggle API bằng biến môi trường.")

DATA_DIR = "data"
zip_path = os.path.join(DATA_DIR, "archive.zip")
extract_dir = os.path.join(DATA_DIR, "kaggle_raw")
os.makedirs(extract_dir, exist_ok=True)

with zipfile.ZipFile(zip_path, "r") as zip_ref:
    zip_ref.extractall(extract_dir)
print("Đã giải nén vào:", extract_dir)

csv_paths = glob.glob(os.path.join( extract_dir, "**", "*.csv"), recursive=True)
print("Các file CSV tìm thấy:", csv_paths)
 
df = pd.read_csv(csv_paths[0])
df.columns = [c.strip() for c in df.columns]
print(df["Category"].value_counts())

it_df = df[df["Category"].str.upper().str.contains("INFORMATION", na=False)].reset_index(drop=True)
print(f"Số CV ngành IT có trong dataset: {len(it_df)}")
 
sample_n = min(150, len(it_df))
it_sample = it_df.sample(n=sample_n, random_state=42).reset_index(drop=True)
it_sample_path = os.path.join(DATA_DIR, "kaggle_it_resumes_sample.csv")
it_sample.to_csv(it_sample_path, index=False)
print(f"Đã lưu {sample_n} CV IT mẫu vào {it_sample_path}")
print(it_sample.loc[0, "Resume_str"][:1500])

#Sinh du lieu 
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    GEMINI_API_KEY = getpass("Nhập Gemini API key (https://aistudio.google.com/app/apikey): ")
 

client = genai.Client(api_key=GEMINI_API_KEY)
print("Đã khởi tạo Gemini client.")

fake = Faker(["en_US"]) 

IT_ROLES = [
    "Backend Developer", "Frontend Developer", "Full-stack Developer",
    "Data Analyst", "Data Engineer", "Data Scientist",
    "DevOps Engineer","QA / Test Engineer", "Mobile Developer (Android)", "Mobile Developer (iOS)",
    "Machine Learning Engineer", "Cloud Engineer", "System Administrator",
    "Cybersecurity Analyst", "Business Analyst (IT)", "IT Project Manager",
    "Database Administrator", "Embedded Software Engineer", "Software Architect",
]
SENIORITY_LEVELS = ["Fresher", "Junior", "Mid-level", "Senior"]
 
TOTAL_CVS = 180
print(f"Sẽ sinh {TOTAL_CVS} CV, trải đều trên {len(IT_ROLES)} vị trí IT khác nhau.")

def build_prompt(candidate_name, role, seniority):
    """Tạo prompt yêu cầu Gemini trả về đúng 1 JSON object theo schema cố định."""
    schema_example = {
        "job_title": role,
        "seniority": seniority,
        "summary": "2-3 câu tóm tắt bản thân bằng tiếng Anh, đúng phong cách CV thật",
        "skills": ["ví dụ: Python", "Docker", "..."],
        "experience": [
            {
                "company": "Tên công ty (tự bịa, KHÔNG dùng tên công ty thật)",
                "title": "Chức danh",
                "start_date": "YYYY-MM",
                "end_date": "YYYY-MM hoặc Present",
                "description": "1-2 câu mô tả công việc/thành tựu, có số liệu cụ thể nếu hợp lý",
            }
        ],
        "education": [
            {
                "degree": "Ví dụ: B.Sc. in Computer Science",
                "school": "Tên trường (tự bịa)",
                "graduation_year": "YYYY",
            }
        ],
    }
 
    prompt = f"""Bạn là trợ lý tạo dữ liệu tổng hợp (synthetic data) cho một CV ngành Công nghệ thông tin (IT).
 
Hãy tạo nội dung CV bằng tiếng Anh cho ứng viên:
- Tên: {candidate_name}
- Vị trí ứng tuyển: {role}
- Cấp bậc kinh nghiệm: {seniority}
 
Yêu cầu:
- Số năm kinh nghiệm và số công ty trong "experience" phải hợp lý với cấp bậc {seniority}.
- "skills" phải là công nghệ/kỹ năng THẬT, phù hợp vị trí {role} (5-10 kỹ năng).
- KHÔNG dùng tên công ty hoặc trường học có thật ngoài đời — hãy bịa tên hợp lý.
- CHỈ trả về DUY NHẤT một JSON object đúng theo cấu trúc mẫu bên dưới. Không thêm giải thích, không thêm markdown code fence (không có ```).
 
Cấu trúc mẫu:
{json.dumps(schema_example, indent=2, ensure_ascii=False)}
"""
    return prompt


def generate_email_from_name(full_name):
    slug = re.sub(r'[^a-z.]', '', full_name.lower().replace(' ', '.'))
    domain = random.choice(['example.com', 'example.org', 'example.net'])
    return f"{slug}{random.randint(1, 999)}@{domain}"

def generate_one_cv(idx):
    role = random.choice(IT_ROLES)
    seniority = random.choice(SENIORITY_LEVELS)
    full_name = fake.name()
    phone = fake.phone_number()
 
    prompt = build_prompt(full_name, role, seniority)
 
    data = None
    for attempt in range(4):
        try:
            response = client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=prompt,
            )
            raw_text = response.text.strip()
            raw_text = raw_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(raw_text)
            break
        except Exception as e:
            wait = 60
            print(f"[CV {idx}] Lỗi lần {attempt + 1}: {e} -> thử lại sau {wait}s")
            time.sleep(wait)
 
    if data is None:
        return None
 

    data["full_name"] = full_name
    data["email"] = generate_email_from_name(full_name)
    data["phone"] = phone
    data["cv_id"] = f"cv_{idx:04d}"
    return data
 
synthetic_json_path = os.path.join(DATA_DIR, "synthetic_cvs.json")

# Đọc file cũ xem đã có bao nhiêu CV rồi
all_cvs = []
if os.path.exists(synthetic_json_path):
    with open(synthetic_json_path, "r", encoding="utf-8") as f:
        try:
            all_cvs = json.load(f)
            print(f"Tìm thấy tiến trình cũ. Đang tiếp tục từ CV số {len(all_cvs)}...")
        except json.JSONDecodeError:
            print("File JSON cũ bị lỗi, bắt đầu tạo lại từ đầu.")

start_idx = len(all_cvs)
for idx in tqdm(range(start_idx, TOTAL_CVS), initial=start_idx, total=TOTAL_CVS):
    cv = generate_one_cv(idx)
    if cv:
        all_cvs.append(cv)
        with open(synthetic_json_path, "w", encoding="utf-8") as f:
            json.dump(all_cvs, f, ensure_ascii=False, indent=2)  
    time.sleep(15)

synthetic_json_path = os.path.join(DATA_DIR, "synthetic_cvs.json")
with open(synthetic_json_path, "w", encoding="utf-8") as f:
    json.dump(all_cvs, f, ensure_ascii=False, indent=2)
print("Đã lưu ground-truth JSON tại", synthetic_json_path)
print(all_cvs[0] if all_cvs else "Chưa có CV nào được sinh.")
 
#render file pdf và validation
styles = getSampleStyleSheet()
name_style = ParagraphStyle("NameStyle", parent=styles["Title"], fontSize=18, alignment=TA_LEFT)
heading_style = ParagraphStyle("HeadingStyle", parent=styles["Heading2"], spaceBefore=10, spaceAfter=4)
body_style = styles["BodyText"]
 
def cv_json_to_pdf(cv, output_path):
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=1.5 * cm, bottomMargin=1.5 * cm,
    )
    story = []
 
    story.append(Paragraph(cv.get("full_name", ""), name_style))
    contact_line = f"{cv.get('email', '')} | {cv.get('phone', '')} | {cv.get('job_title', '')} ({cv.get('seniority', '')})"
    story.append(Paragraph(contact_line, body_style))
    story.append(Spacer(1, 10))
 
    if cv.get("summary"):
        story.append(Paragraph("SUMMARY", heading_style))
        story.append(Paragraph(cv["summary"], body_style))
 
    if cv.get("skills"):
        story.append(Paragraph("SKILLS", heading_style))
        story.append(Paragraph(", ".join(cv["skills"]), body_style))
 
    if cv.get("experience"):
        story.append(Paragraph("EXPERIENCE", heading_style))
        for exp in cv["experience"]:
            line = f"<b>{exp.get('title', '')}</b> - {exp.get('company', '')} ({exp.get('start_date', '')} - {exp.get('end_date', '')})"
            story.append(Paragraph(line, body_style))
            if exp.get("description"):
                story.append(Paragraph(exp["description"], body_style))
            story.append(Spacer(1, 6))
 
    if cv.get("education"):
        story.append(Paragraph("EDUCATION", heading_style))
        for edu in cv["education"]:
            line = f"{edu.get('degree', '')} - {edu.get('school', '')} ({edu.get('graduation_year', '')})"
            story.append(Paragraph(line, body_style))
 
    doc.build(story)
 
 
print("Đã định nghĩa template render PDF.")
 

pdf_dir = os.path.join(DATA_DIR, "synthetic_cv_pdfs")
os.makedirs(pdf_dir, exist_ok=True)
for cv in tqdm(all_cvs):
    out_path = os.path.join(pdf_dir, f"{cv['cv_id']}.pdf")
    cv_json_to_pdf(cv, out_path)
print(f"Đã sinh {len(all_cvs)} file PDF trong {pdf_dir}")
 
 
def check_pdf_readable(cv, pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    checks = {
        "full_name_found": cv["full_name"] in text,
        "email_found": cv["email"] in text,
        "skill_found": (cv["skills"][0] in text) if cv.get("skills") else True,
    }
    return text, checks
 
 
if all_cvs:
    sample_cv = all_cvs[0]
    sample_path = os.path.join(pdf_dir, f"{sample_cv['cv_id']}.pdf")
    text, checks = check_pdf_readable(sample_cv, sample_path)
    print(checks)
    print(text[:800])
 
success, fail = 0, []
for cv in all_cvs:
    path = os.path.join(pdf_dir, f"{cv['cv_id']}.pdf")
    try:
        text, checks = check_pdf_readable(cv, path)
        if all(checks.values()):
            success += 1
        else:
            fail.append((cv["cv_id"], checks))
    except Exception as e:
        fail.append((cv["cv_id"], str(e)))
 
print(f"Đọc lại đúng: {success}/{len(all_cvs)}")
if fail:
    print("Các CV cần kiểm tra lại:", fail[:10])
 
#đóng gói 
zip_base = os.path.join(DATA_DIR, "synthetic_cv_pdfs")
shutil.make_archive(zip_base, "zip", root_dir=DATA_DIR, base_dir="synthetic_cv_pdfs")
 
print("Hoàn tất. Các file kết quả nằm trong thư mục:", os.path.abspath(DATA_DIR))
print(" -", it_sample_path, "(CV mẫu Kaggle tham khảo)")
print(" -", synthetic_json_path, "(ground-truth JSON)")
print(" -", zip_base + ".zip", "(toàn bộ CV dạng PDF)")