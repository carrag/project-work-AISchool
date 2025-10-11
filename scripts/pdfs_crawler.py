import requests, os
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def crawl_pdfs(base_url, dest_folder, limit=20):
    os.makedirs(dest_folder, exist_ok=True)
    print(f"→ Scansione di: {base_url}")
    try:
        r = requests.get(base_url, timeout=10)
        r.raise_for_status()
    except Exception as e:
        print("Errore nel caricamento:", e)
        return
    
    soup = BeautifulSoup(r.text, "html.parser")
    pdf_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if ".pdf" in href.lower():
            full_link = urljoin(base_url, href)
            pdf_links.append(full_link)
    
    if not pdf_links:
        print("⚠️ Nessun PDF trovato. Il sito potrebbe usare JavaScript o link secondari.")
        return

    for i, link in enumerate(pdf_links[:limit]):
        filename = os.path.join(dest_folder, f"{i+1:02d}.pdf")
        print(f"Scarico: {link}")
        try:
            with requests.get(link, stream=True, timeout=10) as r:
                r.raise_for_status()
                with open(filename, "wb") as f:
                    for chunk in r.iter_content(8192):
                        f.write(chunk)
        except Exception as e:
            print(f"Errore su {link}: {e}")

    print(f"✅ Scaricati {min(limit, len(pdf_links))} PDF in {dest_folder}")

if __name__ == "__main__":
    crawl_pdfs("https://www.unibo.it/it/ateneo/amministrazione-trasparente/bandi-di-gara-e-contratti/atti-delle-amministrazioni-aggiudicatrici-e-degli-enti-aggiudicatori-distintamente-per-ogni-procedura/acquisti-di-beni-e-servizi-fino-ai-40-000-euro/acquisti-di-beni-e-servizi-fino-ai-40-000-euro/determine/2025/1487256", "data/train/determine")