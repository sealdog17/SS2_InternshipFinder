import os
import sys
import io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
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
        print(f"Error loading website: {e}")
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
                    description="Job opportunity open, see details at the application link.",
                    required_skills="Software, Logic problem solving",
                    salary_range="Competitive",
                    location="Hanoi/HCM",
                    job_type="full-time",
                    industry="Softwave IT",
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
            company = company_tag.text.strip() if company_tag else "Tech Company"
            
            location_tag = item.find('div', class_='location') or item.find('li', class_='location')
            location = location_tag.text.strip() if location_tag else "Hanoi"

            salary_tag = item.find('div', class_='salary') or item.find('li', class_='salary')
            salary = salary_tag.text.strip() if salary_tag else "Negotiable"

            if Job.query.filter_by(apply_url=href).first():
                continue
                
            # Cào dữ liệu chi tiết
            description = "Job details are being updated."
            required_skills = "Job requirements have not been provided."
            try:
                detail_resp = requests.get(href, headers=headers, timeout=10)
                if detail_resp.status_code == 200:
                    detail_soup = BeautifulSoup(detail_resp.text, 'html.parser')
                    detail_rows = detail_soup.find_all('div', class_='detail-row')
                    
                    for row in detail_rows:
                        heading = row.find(['h2', 'h3', 'h4'])
                        if heading:
                            heading_text = heading.text.strip().lower()
                            heading.extract() # Remove heading from the row element
                            content = row.text.strip()
                            content = ' '.join(content.split())
                            
                            if 'description' in heading_text:
                                description = content[:1500] if len(content) > 5 else description
                            elif 'requirement' in heading_text:
                                required_skills = content[:1000] if len(content) > 5 else required_skills
            except Exception as e:
                pass
                
            new_job = Job(
                title=title,
                company=company,
                description=description,
                required_skills=required_skills,
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
        print(f"[SUCCESS] Successfully scraped and saved {jobs_added} new jobs from CareerViet!")
    else:
        print("No new jobs to add.")


if __name__ == "__main__":
    with app.app_context():
        scrape_careerviet()
