import os, re, time, requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def sanitize_filename(s):
    s = re.sub(r'[^a-zA-Z0-9_-]+', '_', s)
    return s.strip('_')[:80]

def is_pdf(session, url, timeout=10):
    try:
        h = session.head(url, allow_redirects=True, timeout=timeout)
        ct = h.headers.get("Content-Type","").lower()
        return "application/pdf" in ct
    except Exception:
        return False

def crawl_pdfs_recursive(base_url, dest_root, category="generic", limit=30, delay=0.5):
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (dataset-crawler)"})
    dest_folder = os.path.join(dest_root, category)
    os.makedirs(dest_folder, exist_ok=True)

    print(f"\n→ Scansione categoria: {category}")
    print(f"  Base URL: {base_url}")

    try:
        r = session.get(base_url, timeout=15)
        r.raise_for_status()
    except Exception as e:
        print("Errore nel caricamento della pagina principale:", e)
        return

    soup = BeautifulSoup(r.text, "html.parser")
    subpages = [urljoin(base_url, a["href"]) for a in soup.find_all("a", href=True)
                if not a["href"].startswith(("mailto:", "javascript:", "#"))]

    downloaded = 0
    for sub in subpages:
        if downloaded >= limit:
            break
        try:
            r2 = session.get(sub, timeout=10)
            r2.raise_for_status()
            s2 = BeautifulSoup(r2.text, "html.parser")

            # cerca link PDF (anche senza estensione)
            pdf_links = []
            for a in s2.find_all("a", href=True):
                href = a["href"]
                full = urljoin(sub, href)
                if "pdf" in href.lower() or "pdf" in (a.get_text() or "").lower() or is_pdf(session, full):
                    pdf_links.append(full)

            for link in pdf_links:
                if downloaded >= limit:
                    break
                fname = sanitize_filename(link.split("/")[-1]) or f"file_{downloaded+1}"
                if not fname.lower().endswith(".pdf"):
                    fname += ".pdf"
                out_path = os.path.join(dest_folder, fname)
                print(f"↓ {link}")
                with session.get(link, stream=True, timeout=20) as resp:
                    resp.raise_for_status()
                    with open(out_path, "wb") as f:
                        for chunk in resp.iter_content(8192):
                            f.write(chunk)
                downloaded += 1
                time.sleep(delay)

        except Exception as e:
            print(f"Errore su {sub}: {e}")

    print(f"✅ Scaricati {downloaded} PDF in {dest_folder}\n")

if __name__ == "__main__":
    crawl_pdfs_recursive(
        base_url="https://www.unibo.it/it/ateneo/amministrazione-trasparente/bandi-di-gara-e-contratti/atti-delle-amministrazioni-aggiudicatrici-e-degli-enti-aggiudicatori-distintamente-per-ogni-procedura/acquisti-di-beni-e-servizi-fino-ai-40-000-euro/acquisti-di-beni-e-servizi-fino-ai-40-000-euro/determine/2025",
        dest_root="data/train",
        category="determine_2025",
        limit=25
    )
