import sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import requests
from bs4 import BeautifulSoup

url = "https://careerviet.vn/viec-lam/it-phan-mem-c1-vi.html"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
}
response = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(response.text, 'html.parser')

items = soup.find_all('div', class_='job-item')
if items:
    first_item = items[0]
    print(first_item.prettify())
