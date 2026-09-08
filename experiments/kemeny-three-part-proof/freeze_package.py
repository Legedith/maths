from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
STATIC_FILES = (
    ".python-version",
    "ATTRIBUTION.md",
    "README.md",
    "build_publication_manifest.py",
    "coefficient-certificate.json",
    "contract-v1.md",
    "freeze_package.py",
    "proposal.json",
    "proposal.md",
    "pyproject.toml",
    "run_logged.py",
    "selection-v1.json",
    "uv.lock",
    "verify_coefficient_certificate.py",
)
EXPECTED_FROZEN_COPIES = {
    "coefficient-certificate.json": "540ea590fb2e3d671e95102ab8ac5b80a22752f85354c7ded4aa84a4848fb8a9",
    "contract-v1.md": "563d11151e21d31a21804e7871db6979996bc2cbe4dc0ed3673563975b1d2aba",
    "proposal.json": "6a821c189ce481d4138c4d7cda5a223332bf3317a0b91c0d84c63887d69c2c5d",
    "proposal.md": "53c78f650397b3a791dd6b2a715f2294c564bcb9440feabce7327ceb4dcfa3e4",
    "run_logged.py": "b6f4c329387705b2adf67f7dd3f806bbcd0a5906d476f5214fe8278d5ea5bfa6",
    "selection-v1.json": "c750ff018cc7e04db9d9b964486d71a0e5f9b5a42ea93e9de25b68c73632b996",
    "verify_coefficient_certificate.py": "08aee29b87793cb288eaa7dfe54dd748b169972c32e46ed6e1b5bb2e1f3327f5",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=PACKAGE / "package-freeze.json")
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit(f"refusing to overwrite freeze: {output}")

    files = []
    for relative in STATIC_FILES:
        path = PACKAGE / relative
        if not path.is_file():
            raise SystemExit(f"missing static package file: {relative}")
        digest = sha256(path)
        expected = EXPECTED_FROZEN_COPIES.get(relative)
        if expected is not None and digest != expected:
            raise SystemExit(
                f"frozen-copy mismatch for {relative}: expected {expected}, got {digest}"
            )
        files.append({"path": relative, "bytes": path.stat().st_size, "sha256": digest})

    record = {
        "schema_version": "kemeny-three-part-portable-freeze-v1",
        "status": "frozen_before_first_portable_checker_run",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": {"version": sys.version, "implementation": platform.python_implementation()},
        "selection_sha256": EXPECTED_FROZEN_COPIES["selection-v1.json"],
        "contract_sha256": EXPECTED_FROZEN_COPIES["contract-v1.md"],
        "selected_checker_sha256": EXPECTED_FROZEN_COPIES["verify_coefficient_certificate.py"],
        "selected_certificate_sha256": EXPECTED_FROZEN_COPIES["coefficient-certificate.json"],
        "files": files,
        "file_count": len(files),
        "independent_final_proof_gate": "pending",
    }
    output.write_bytes(
        (json.dumps(record, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("utf-8")
    )
    print(json.dumps({"output": str(output), "file_count": len(files)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
