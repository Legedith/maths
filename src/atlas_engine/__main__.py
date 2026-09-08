"""Command-line interface for exact analysis and canonical evaluation."""

import argparse
import json
import sys
from pathlib import Path

from .analysis import analyze_graph
from .evaluator import run_evaluation
from .validation import InputValidationError


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m atlas_engine")
    commands = parser.add_subparsers(dest="command", required=True)
    analyze = commands.add_parser("analyze", help="analyze one graph JSON payload")
    analyze.add_argument("path", type=Path)
    evaluate = commands.add_parser("evaluate", help="run the frozen canonical evaluator")
    evaluate.add_argument("--output-dir", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    try:
        if args.command == "analyze":
            payload = json.loads(args.path.read_text(encoding="utf-8"))
            print(json.dumps(analyze_graph(payload), indent=2, sort_keys=True))
            return 0
        summary = run_evaluation(args.output_dir)
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0 if summary["passed"] else 1
    except (OSError, json.JSONDecodeError, InputValidationError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

