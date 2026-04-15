import sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import requests
from bs4 import BeautifulSoup

url = "https://careerviet.vn/vi/tim-viec-lam/senior-talent-acquisition-specialist.35C70D3D.html"
headers = {"User-Agent": "Mozilla/5.0"}
resp = requests.get(url, headers=headers)
soup = BeautifulSoup(resp.text, 'html.parser')

desc, req = "N/A", "N/A"
for row in soup.find_all('div', class_='detail-row'):
    h3 = row.find('h3')
    if h3:
        txt = h3.text.strip().lower()
        if "mô tả" in txt:
            desc = row.text.replace(h3.text, '').strip()[:100]
        elif "yêu cầu" in txt:
            req = row.text.replace(h3.text, '').strip()[:100]

print("DESC:", desc)
print("REQ:", req)
