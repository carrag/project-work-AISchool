import os, requests, time
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def is_pdf(session, url, timeout=10):
    try:
        h = session.head(url, allow_redirects=True, timeout=timeout)
        ct = h.headers.get("Content-Type","").lower()
        if "application/pdf" in ct:
            return True
        # fallback: prova a leggere pochi byte e cerca la firma %PDF
        with session.get(url, stream=True, timeout=timeout) as r:
            r.raise_for_status()
            chunk = next(r.iter_content(2048), b"")
            return chunk.startswith(b"%PDF")
    except Exception:
        return False

def crawl_pdfs(base_url, dest_folder, limit=20, delay=0.5):
    os.makedirs(dest_folder, exist_ok=True)
    print(f"→ Scansione: {base_url}")
    s = requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0 (dataset-crawler)"})

    r = s.get(base_url, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    candidates = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith(("mailto:", "javascript:", "#")):
            continue
        full = urljoin(base_url, href)

        # 1) priorità: testo link che contiene "pdf"
        txt = (a.get_text() or "").lower()
        looks_like_pdf = "pdf" in txt or "pdf" in href.lower()

        # 2) verifica di contenuto
        if looks_like_pdf or "acquisti.unibo.it" in full:
            if is_pdf(s, full):
                candidates.append(full)

        if len(candidates) >= limit:
            break

    if not candidates:
        print("⚠️ Nessun PDF trovato (probabile URL di lista con sottopagine).")
        return

    for i, url in enumerate(candidates[:limit], 1):
        out = os.path.join(dest_folder, f"{i:02d}.pdf")
        print(f"↓ {url}  →  {out}")
        with s.get(url, stream=True, timeout=20) as resp:
            resp.raise_for_status()
            with open(out, "wb") as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)
        time.sleep(delay)

    print(f"✅ Scaricati {len(candidates[:limit])} PDF in {dest_folder}")

if __name__ == "__main__":
    # esempio con la tua pagina UNIBO
    crawl_pdfs(
        "https://www.unibo.it/it/ateneo/amministrazione-trasparente/bandi-di-gara-e-contratti/atti-delle-amministrazioni-aggiudicatrici-e-degli-enti-aggiudicatori-distintamente-per-ogni-procedura/acquisti-di-beni-e-servizi-fino-ai-40-000-euro/acquisti-di-beni-e-servizi-fino-ai-40-000-euro/determine/2025/1487256",
        "data/train/determine",
        limit=20
    )
