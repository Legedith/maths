from __future__ import annotations

import json
import subprocess
import sys

from .helpers import b, make_payload


def test_module_cli_emits_structured_json(tmp_path) -> None:
    source = tmp_path / "input.json"
    source.write_text(json.dumps(make_payload(claim=b(False))), encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, "-m", "atlas_checks", str(source)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0
    result = json.loads(completed.stdout)
    assert result["verdict"] == "counterexample"
    assert result["id"] == "development-case"


def test_module_cli_reports_invalid_json(tmp_path) -> None:
    source = tmp_path / "bad.json"
    source.write_text("{", encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, "-m", "atlas_checks", str(source)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 2
    result = json.loads(completed.stdout)
    assert result["verdict"] == "invalid_input"
    assert result["errors"][0]["code"] == "invalid_json"
