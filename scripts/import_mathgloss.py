"""Portable explicit-input adapter for the unchanged audited importer core."""
import argparse
import json
from pathlib import Path

from mathgloss_import import import_csv_bytes, write_bundle

EXPECTED_BUNDLE = {
    "MATHGLOSS-LICENSE": "5dc6b930900926814fc7bb9ff45dfcceae3aa33780eb010c83e6df58493594e7",
    "candidate-index.json": "282ed1fd858595b782c856fbd2c96964a0b6ff3850fedf21105ca9bbb7edb4da",
    "import-ledger.jsonl": "14d8e9cc972a83ac4267d4b168d9510f74c65abbae509e7149012ba653c4ad61",
    "summary.json": "0102f6fca4237d80d3e4e167c476f118d5cfaff41b5b325882bc784eecfa6e58",
}

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-csv", type=Path, required=True)
    parser.add_argument("--source-license", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = import_csv_bytes(args.source_csv.read_bytes())
    hashes = write_bundle(result, args.output_dir, args.source_license.read_bytes())
    if hashes != EXPECTED_BUNDLE:
        raise RuntimeError("Reproduction differs from the independently audited export.")
    print(json.dumps({"files": hashes, "summary": result.summary}, indent=2))

if __name__ == "__main__":
    main()
