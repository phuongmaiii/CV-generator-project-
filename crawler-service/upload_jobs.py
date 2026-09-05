import requests
import json

with open('jobs_data.json', 'r', encoding='utf-8') as f:
    jobs = json.load(f)

for job in jobs:
    if "description" not in job:
        job["description"] = "Xem chi tiết mô tả công việc tại link gốc."
    
    if "postedBy" not in job:
        job["postedBy"] = 1 

url = "http://localhost:8080/api/jobs/bulk"
response = requests.post(url, json=jobs)

if response.status_code == 200:
    print("Đã bơm thành công toàn bộ công việc vào Database!")
else:
    print("Lỗi:", response.text)