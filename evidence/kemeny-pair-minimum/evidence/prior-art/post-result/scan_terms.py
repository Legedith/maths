from __future__ import annotations

import hashlib
import json
from pathlib import Path


TERMS = [
    "Braess set",
    "minimum order",
    "smallest graph",
    "exhaustive",
    "two nonedges",
    "two non-edges",
    "E?zW",
    "1/112",
    "1/18",
    "no effect",
    "twin vertices",
    "twin pendant vertices",
    "twin pendent paths",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    source_dir = Path("sources")
    records = []
    for path in sorted(source_dir.glob("*.page-marked.txt")):
        text = path.read_text(encoding="utf-8")
        lowered = text.casefold()
        lines = text.splitlines()
        term_records = []
        for term in TERMS:
            needle = term.casefold()
            line_numbers = [
                index for index, line in enumerate(lines, start=1) if needle in line.casefold()
            ]
            term_records.append(
                {
                    "term": term,
                    "substring_count": lowered.count(needle),
                    "line_numbers": line_numbers,
                }
            )
        records.append(
            {
                "path": path.as_posix(),
                "sha256": sha256(path),
                "terms": term_records,
            }
        )
    output = {
        "schema_version": "kemeny-postresult-fulltext-term-scan-v1",
        "matching_rule": "Unicode casefolded literal substring over pypdf page-marked extraction",
        "records": records,
    }
    Path("term-scan.json").write_text(
        json.dumps(output, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({"files": len(records), "output_sha256": sha256(Path("term-scan.json"))}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
