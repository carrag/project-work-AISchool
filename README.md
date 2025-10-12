# Accelerating Document AI for Administrative Records (AI-AR)

**Goal**
This proof-of-concept shows an end-to-end pipeline for extracting structure and information from administrative PDF documents (*determine*, contracts, testing reports).
The output is provided in interoperable **YAML** and **Markdown**, separating the *container* (layout) from the *content* (data).

---

## Overview

```
PDF → image (pdf2image)
    → OCR (Tesseract)
    → LayoutLMv3 (zero-shot inference)
    → regex
    → YAML + Markdown export
```

Tested on a A40 GPU server.

---

## How to Run

1. Pick/Place PDFs under
   `data/train/determine/`
2. Open
   `notebooks/inferenza_layoutlm.ipynb`
3. Run cells sequentially to:

   * set paths
   * convert PDF → PNG
   * perform OCR
   * run LayoutLMv3 inference
   * extract basic fields (number, date, subject)
   * export results

Results are saved in `notebooks/outputs/` as:

* `<file>.yaml` — structured content
* `<file>.md` — readable template
* `<file>_page_XXX.png` — diagnostics

---

## Environment

The environment can be recreated with:

```bash
conda env create -f notebooks/outputs/environment.yml
conda activate pw-ai
```

Dependencies:
`torch`, `transformers`, `pytesseract`, `pdf2image`, `pyyaml`, `Pillow`.

---

## Example Output

```yaml
document:
  type: determina
  header:
    numero: "125/2023"
    data: "2023-03-21"
  body:
    oggetto: "Affidamento servizio di manutenzione ordinaria"
  meta:
    pages: 3
    model: microsoft/layoutlmv3-base
```

---

## Notes

* The model (`layoutlmv3-base`) is used in **zero-shot** mode, not fine-tuned on Italian data.
* Regex retrieve common fields.

---

## Author

**Michele Carraglia**
AISchool.it – Project Work 2025
