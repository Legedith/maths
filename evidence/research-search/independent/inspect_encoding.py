from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"D:/CodexWorkspaces/mathematics-atlas/project")
OUTPUT = Path(r"D:/CodexWorkspaces/mathematics-atlas/retrieval-study-work/ui-audit/encoding-check.json")
FILES = [
    PROJECT / "lib/research-search.ts",
    PROJECT / "components/research-search.tsx",
    PROJECT / "lib/use-atlas-tools.ts",
    PROJECT / "docs/research-search.md",
    PROJECT / "evidence/research-search/webmcp-observations.json",
]


records: list[dict[str, object]] = []
for path in FILES:
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    suspicious = []
    for number, line in enumerate(text.splitlines(), start=1):
        if any(token in line for token in ("â", "Â", "�")):
            suspicious.append({"line": number, "repr": repr(line)})
    non_ascii = []
    for number, line in enumerate(text.splitlines(), start=1):
        if any(ord(character) > 127 for character in line):
            non_ascii.append(
                {
                    "line": number,
                    "repr": repr(line),
                    "codepoints": [f"U+{ord(character):04X}" for character in line if ord(character) > 127],
                }
            )
    records.append(
        {
            "path": path.relative_to(PROJECT).as_posix(),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "utf8_decode": "pass",
            "suspicious_mojibake_tokens": suspicious,
            "non_ascii_lines": non_ascii,
        }
    )

OUTPUT.write_text(json.dumps({"files": records}, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
print(OUTPUT)
