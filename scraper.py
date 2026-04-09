import os
import requests
from bs4 import BeautifulSoup
from app import app, db, Job
from datetime import date

def scrape_careerviet():
    url = "https://careerviet.vn/viec-lam/it-phan-mem-c1-vi.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Lỗi khi tải trang web: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Try finding job items visually based on CareerViet structure
    job_items = soup.find_all('div', class_='job-item')
    
    jobs_added = 0
    if not job_items:
        # Fallback raw parser if DOM structure is different
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            title = link.get('title', link.text.strip())
            
            # Check if likely a job post URL
            if '/vi/tim-viec-lam/' in href and '.html' in href and len(title) > 5 and 'Tìm việc' not in title:
                # Add root URL if missing
                if not href.startswith('http'):
                    href = 'https://careerviet.vn' + href

                if Job.query.filter_by(apply_url=href).first():
                    continue
                
                # Basic cleaning
                title = title.replace('(Mới)', '').strip()
                
                new_job = Job(
                    title=title,
                    company="Top IT Company", 
                    description="Cơ hội việc làm đang mở, xem chi tiết ở đường dẫn ứng tuyển.",
                    required_skills="Software, Logic problem solving",
                    salary_range="Cạnh tranh",
                    location="Hà Nội/HCM",
                    job_type="full-time",
                    industry="IT Phần mềm",
                    application_deadline=date(2025, 12, 31),
                    apply_url=href,
                    source="CareerViet"
                )
                db.session.add(new_job)
                jobs_added += 1
                if jobs_added >= 15: 
                    break
    else:
        # Extracted precisely
        for item in job_items:
            # Usually the job link is inside an 'a' with 'job_link' class
            title_tag = item.find('a', class_='job_link') or item.find('a', class_='job-title')
            if not title_tag:
                continue
            href = title_tag.get('href')
            title = title_tag.text.strip()
            if not href.startswith('http'):
                href = 'https://careerviet.vn' + href
            
            # Additional details
            company_tag = item.find('a', class_='company-name')
            company = company_tag.text.strip() if company_tag else "Công ty công nghệ"
            
            location_tag = item.find('div', class_='location') or item.find('li', class_='location')
            location = location_tag.text.strip() if location_tag else "Hà Nội"

            salary_tag = item.find('div', class_='salary') or item.find('li', class_='salary')
            salary = salary_tag.text.strip() if salary_tag else "Thỏa thuận"

            if Job.query.filter_by(apply_url=href).first():
                continue
                
            new_job = Job(
                title=title,
                company=company,
                description="Xem chi tiết tại hệ thống cổng thông tin tuyển dụng.",
                required_skills="Thương lượng",
                salary_range=salary,
                location=location.replace('\n', '').strip(),
                job_type="full-time",
                industry="IT Phần mềm",
                application_deadline=date(2025, 12, 31),
                apply_url=href,
                source="CareerViet"
            )
            db.session.add(new_job)
            jobs_added += 1
            if jobs_added >= 15:
                break
        
    if jobs_added > 0:
        db.session.commit()
        print(f"✅ Đã cào và lưu thành công {jobs_added} công việc mới từ CareerViet!")
    else:
        print("Không có công việc mới nào cần thêm.")


if __name__ == "__main__":
    with app.app_context():
        scrape_careerviet()
