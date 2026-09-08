from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from pypdf import PdfReader


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdfs", nargs="+", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for pdf in args.pdfs:
        reader = PdfReader(pdf)
        chunks = []
        for page_number, page in enumerate(reader.pages, start=1):
            chunks.append(f"\n===== PDF PAGE {page_number} =====\n")
            chunks.append(page.extract_text() or "")
            chunks.append("\n")
        output = args.output_dir / f"{pdf.stem}.page-marked.txt"
        output.write_text("".join(chunks), encoding="utf-8", newline="\n")
        records.append(
            {
                "pdf": pdf.as_posix(),
                "pdf_sha256": sha256(pdf),
                "pages": len(reader.pages),
                "text": output.as_posix(),
                "text_bytes": output.stat().st_size,
                "text_sha256": sha256(output),
            }
        )
    print(json.dumps({"records": records}, sort_keys=True, separators=(",", ":")))
    return 0



if __name__ == "__main__":
    raise SystemExit(main())
