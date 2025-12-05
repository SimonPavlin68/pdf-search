import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

url = "https://www.archery-si.org/organi/"
resp = requests.get(url)
resp.raise_for_status()

soup = BeautifulSoup(resp.text, "html.parser")

pdf_links = []
for a in soup.find_all("a", href=True):
    href = a["href"]
    if href.lower().endswith(".organi"):
        full = urljoin(url, href)
        pdf_links.append(full)

# Shrani rezultate v JSON
with open("pdf_links.json", "w", encoding="utf-8") as f:
    json.dump(pdf_links, f, ensure_ascii=False, indent=2)

print(f"Najdeni {len(pdf_links)} PDF-ji. Rezultati shranjeni v pdf_links.json")
