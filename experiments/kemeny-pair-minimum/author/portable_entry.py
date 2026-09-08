from __future__ import annotations

import argparse
import hashlib
import importlib.util
from pathlib import Path
from types import ModuleType


EXPECTED_CONTRACT_SHA256 = "1ff78636c4dcadc7d8f9d6a3a36c144e193e5f90cbb970ab846c877cdf0c6ac6"
EXPECTED_CENSUS_SHA256 = "6560176884fc4ce67b8da38465867f0a89491f087794258c7bd627225b5d6341"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_frozen_author(source_path: Path) -> ModuleType:
    if sha256_file(source_path) != EXPECTED_CENSUS_SHA256:
        raise RuntimeError("frozen author census.py hash mismatch")
    spec = importlib.util.spec_from_file_location("frozen_kemeny_author_census", source_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not construct import specification for census.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Portable path adapter for the byte-identical frozen author census."
    )
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--contract-path", required=True, type=Path)
    args = parser.parse_args()

    source_path = Path(__file__).resolve().with_name("census.py")
    contract_path = args.contract_path.resolve()
    if sha256_file(contract_path) != EXPECTED_CONTRACT_SHA256:
        raise RuntimeError("local contract hash mismatch")
    module = load_frozen_author(source_path)

    # This is the sole mutation of a frozen module global: replace its original
    # machine-specific contract path with the byte-identical packaged contract.
    module.CONTRACT_PATH = contract_path
    return module.run_census(args.input_dir.resolve(), args.output_dir.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
