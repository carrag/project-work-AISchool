import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

base = "https://www.urp.cnr.it/documenti/dipartimentiistituti"
html = requests.get(base, headers={"User-Agent": "Mozilla/5.0"}).text
soup = BeautifulSoup(html, "html.parser")

links = []
for a in soup.find_all("a", href=True):
    href = a["href"]
    text = a.get_text(strip=True).lower()
    if "documento" in href and "apri" in text:
        full = urljoin(base, href)
        links.append(full)

print(f"Trovati {len(links)} link di secondo livello:")
for l in links:
    print("→", l)
