from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


EXPECTED_SOURCE_PINS_SHA256 = "a54738f15cdc11aa383a452e7a464be80aafe9eb3ad609e2313f65dfaa4b2b87"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    staging_root = Path(__file__).resolve().parent
    package_root = staging_root / "experiments/kemeny-pair-minimum"
    output = package_root / "preexecution-freeze.json"
    if output.exists():
        raise FileExistsError(f"refusing to overwrite {output}")

    pins_raw = (package_root / "source-pins.json").read_bytes()
    if sha256_bytes(pins_raw) != EXPECTED_SOURCE_PINS_SHA256:
        raise RuntimeError("source-pins.json does not match its frozen hash")
    pins = json.loads(pins_raw)
    pin_lookup = {record["path"]: record for record in pins["files"]}
    for relative_path, expected in pin_lookup.items():
        raw = (package_root / relative_path).read_bytes()
        if len(raw) != expected["bytes"] or sha256_bytes(raw) != expected["sha256"]:
            raise RuntimeError(f"pinned file mismatch: {relative_path}")

    files = []
    for path in sorted(package_root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(package_root)
        if ".venv" in relative.parts or "__pycache__" in relative.parts:
            continue
        raw = path.read_bytes()
        relative_text = relative.as_posix()
        files.append(
            {
                "path": relative_text,
                "bytes": len(raw),
                "sha256": sha256_bytes(raw),
                "role": pin_lookup.get(relative_text, {}).get(
                    "role", "portable_adapter_or_documentation"
                ),
            }
        )

    manifest = {
        "schema_version": "kemeny-portable-preexecution-freeze-v1",
        "status": "frozen_before_portable_integration_census",
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "package_root": "experiments/kemeny-pair-minimum",
        "source_pins_sha256": EXPECTED_SOURCE_PINS_SHA256,
        "file_count_excluding_this_manifest_and_environments": len(files),
        "files": files,
        "excluded": ["**/.venv/**", "**/__pycache__/**", "preexecution-freeze.json"],
        "limitations": [
            "This is an author-generated packaging freeze; independent adapter audit remains pending.",
            "The portable integration replay does not alter the chronology or ownership of earlier runs.",
        ],
    }
    output.write_bytes(
        (json.dumps(manifest, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode(
            "utf-8"
        )
    )
    print(
        json.dumps(
            {
                "path": output.as_posix(),
                "bytes": output.stat().st_size,
                "sha256": sha256_bytes(output.read_bytes()),
                "file_count": len(files),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
