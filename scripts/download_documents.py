"""
Download source PDFs into app/data/documents/.

Why this exists:
- Competition-friendly reproducibility: you can rebuild the RAG store from a clean repo.
- Keeps the repo clean of copyrighted PDFs (only download locally).

Usage:
  python scripts/download_documents.py

Then:
  python app/data/vector_db.py
"""

from __future__ import annotations

import os
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "app" / "data" / "documents"


DOC_URLS = {
    "netflix_terms.pdf": "https://help.netflix.com/legal/termsofuse",
    "planet_fitness_terms.pdf": "https://www.planetfitness.co.za/terms-conditions/",
    "adobe_terms.pdf": "https://www.adobe.com/legal/subscription-terms.html",
    "spotify_terms.pdf": "https://www.spotify.com/uk/legal/end-user-agreement/",
    "amazon_terms.pdf": "https://jtkmarketing.s3.amazonaws.com/filer_public/53/b2/53b285a3-fd18-4048-a615-decdb2d0b43a/terms_and_conditions.pdf",
    "ftc_negative_option_rule.pdf": "https://www.ftc.gov/system/files/ftc_gov/pdf/p064202_negative_option_rule.pdf",
    "state_consumer_protection.pdf": "https://www.consumersinternational.org/media/2255/consumer-protection-in-nigeria-research-report-eng.pdf"
}

def download(url: str, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # Force identity encoding to avoid zstd decode issues in some environments.
    headers = {
        "Accept-Encoding": "identity",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) FiscalSentinel/1.0",
    }
    with requests.get(
        url,
        stream=True,
        timeout=60,
        headers=headers,
    ) as r:
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 256):
                if chunk:
                    f.write(chunk)


def main():
    if not DOC_URLS:
        raise SystemExit(
            "DOC_URLS is empty. Edit scripts/download_documents.py and add URLs for the PDFs you want to download."
        )

    for filename, url in DOC_URLS.items():
        out_path = DOCS_DIR / filename
        print(f"Downloading {filename} ...")
        try:
            download(url, out_path)
            print(f"Saved to {out_path}")
        except Exception as e:
            print(f"⚠️ Failed to download {filename}: {e}")

    print("\nDone. Now run: python app/data/vector_db.py")


if __name__ == "__main__":
    # Avoid proxies breaking downloads in locked-down environments.
    os.environ.setdefault("NO_PROXY", "*")
    main()
