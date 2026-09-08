"""Restore auditor-read PDFs locally without distributing full papers in Git."""
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "evidence/symmetry/independent"
sources = json.loads((AUDIT / "primary-source-verification.json").read_text(encoding="utf-8"))["sources"]
results = []
for source in sources:
    target = (AUDIT / source["pdf_path"]).resolve()
    if not target.is_relative_to(AUDIT.resolve()):
        raise ValueError("Source path escapes audit folder")
    record = {"id": source["id"], "url": source["url"], "expected_sha256": source["pdf_sha256"]}
    try:
        if target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest() == source["pdf_sha256"]:
            record.update(status="verified_local", sha256=source["pdf_sha256"])
        else:
            request = Request(source["url"], headers={"User-Agent": "MathematicsAtlas-source-reproduction/1.0"})
            with urlopen(request, timeout=30) as response:
                body = response.read(20_000_001)
            if len(body) > 20_000_000:
                raise ValueError("Source exceeds the 20 MB retrieval bound")
            digest = hashlib.sha256(body).hexdigest()
            if digest != source["pdf_sha256"]:
                raise ValueError(f"Source changed: retrieved SHA-256 {digest}")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(body)
            record.update(status="downloaded_and_verified", sha256=digest)
    except Exception as error:
        record.update(status="failed", error=str(error))
    results.append(record)
report = {"passed": all(r["status"] != "failed" for r in results), "records": results,
          "scope": "Byte-identical PDF restoration only. Semantic audit and extracted-text line locators remain in the independent reports."}
destination = ROOT / "work/audit-source-restoration.json"
destination.parent.mkdir(parents=True, exist_ok=True)
destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
raise SystemExit(0 if report["passed"] else 1)
