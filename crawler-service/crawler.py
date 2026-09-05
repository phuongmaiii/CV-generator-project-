import requests
from bs4 import BeautifulSoup
import json

def crawl_jobs(url):
    # Nâng cấp User-Agent cho giống trình duyệt thật hơn để "qua mặt" hệ thống chặn bot
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    job_list = []
    # Dùng đúng class bạn vừa tìm được
    jobs = soup.find_all('div', class_='job-item-search-result') 
    
    for job in jobs:
        try:
            # Lấy tiêu đề và link từ khối title-block
            title_block = job.find('div', class_='title-block')
            if not title_block: continue
            
            title_tag = title_block.find('a')
            title = title_tag.text.strip() if title_tag else "Không xác định"
            link = title_tag['href'] if title_tag else ""
            
            # Lấy tên công ty từ thẻ span class company-name
            company_tag = job.find('span', class_='company-name')
            company = company_tag.text.strip() if company_tag else "Không xác định"
            
            # TopCV thường ẩn yêu cầu kỹ năng ở trang chi tiết, tạm thời gán mặc định
            requirements = "Xem chi tiết trong link ứng tuyển"
            
            job_list.append({
                "title": title,
                "companyName": company,
                "requirements": requirements,
                "jobUrl": link
            })
        except Exception as e:
            continue 
            
    with open('jobs_data.json', 'w', encoding='utf-8') as f:
        json.dump(job_list, f, ensure_ascii=False, indent=4)
        
    print(f"Đã thu thập thành công {len(job_list)} công việc!")

# Chạy hàm
crawl_jobs('https://www.topcv.vn/tim-viec-lam-cong-nghe-thong-tin-cr257?type_keyword=1&sba=1&category_family=r257&saturday_status=0')