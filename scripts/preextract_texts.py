"""Pre-extract text from PDFs in the assets folder and cache them under assets/texts/.

Run from the repository root (or with Python path pointing here):

    python scripts/preextract_texts.py

The script requires PyPDF2 (installed via requirements.txt).
"""
from pathlib import Path
import sys

try:
    from PyPDF2 import PdfReader
except Exception as exc:
    print("PyPDF2 is required. Install with 'pip install PyPDF2' or 'pip install -r requirements.txt'")
    raise

REPO_ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = REPO_ROOT / "assets"
TEXT_DIR = ASSETS_DIR / "texts"

if not ASSETS_DIR.exists():
    print(f"Assets directory not found at {ASSETS_DIR}")
    sys.exit(1)

TEXT_DIR.mkdir(parents=True, exist_ok=True)

pdf_files = sorted([p for p in ASSETS_DIR.glob("*.pdf") if p.is_file()])
if not pdf_files:
    print("No PDF files found in assets/ to process.")
    sys.exit(0)

summary = []
for pdf in pdf_files:
    try:
        reader = PdfReader(str(pdf))
        parts = []
        for page in reader.pages:
            try:
                txt = page.extract_text() or ""
            except Exception:
                txt = ""
            parts.append(txt)
        extracted = "\n".join(parts)
    except Exception as exc:
        print(f"Failed to extract {pdf.name}: {exc}")
        extracted = ""

    out_file = TEXT_DIR / f"{pdf.stem}.txt"
    try:
        out_file.write_text(extracted, encoding="utf-8")
        print(f"WROTE: {out_file.relative_to(REPO_ROOT)} ({len(extracted)} chars)")
        summary.append((pdf.name, True, len(extracted)))
    except Exception as exc:
        print(f"Failed to write text for {pdf.name}: {exc}")
        summary.append((pdf.name, False, 0))

print("\nSummary:")
for name, ok, length in summary:
    print(f" - {name}: {'ok' if ok else 'failed'} ({length} chars)")

print(f"\nDone. Text files are under: {TEXT_DIR}")
