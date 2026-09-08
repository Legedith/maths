"""Command-line interface: python -m atlas_checks input.json"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from .api import check_transfer, invalid_input_result


def _cli_error(code: str, path: str, message: str) -> dict[str, Any]:
    return invalid_input_result(None, {"code": code, "path": path, "message": message})


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if len(arguments) != 1:
        print(json.dumps(_cli_error("cli_usage", "$", "usage: python -m atlas_checks input.json"), sort_keys=True))
        return 2
    try:
        if arguments[0] == "-":
            text = sys.stdin.read()
        else:
            text = Path(arguments[0]).read_text(encoding="utf-8")
    except OSError as exc:
        print(json.dumps(_cli_error("input_read_error", "$", str(exc)), sort_keys=True))
        return 2
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        print(
            json.dumps(
                _cli_error("invalid_json", "$", f"{exc.msg} at line {exc.lineno}, column {exc.colno}"),
                sort_keys=True,
            )
        )
        return 2
    print(json.dumps(check_transfer(payload), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
