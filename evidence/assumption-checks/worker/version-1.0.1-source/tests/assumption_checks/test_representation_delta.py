"""Root-authored regressions for defects found after the frozen first run."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys

import pytest

from atlas_checks import check_transfer
from atlas_checks.__main__ import main
from .helpers import b, make_payload


@pytest.mark.parametrize("value", [10 ** 5000, -(10 ** 5000)], ids=["huge-positive", "huge-negative"])
def test_huge_programmatic_conductance_is_structured_invalid(value: int) -> None:
    payload = make_payload(claim=b(True))
    payload["graph"]["edges"][0]["conductance"] = value
    result = check_transfer(payload)
    assert result["verdict"] == "invalid_input"
    assert result["errors"][0]["code"] == "rational_too_large"


@pytest.mark.parametrize("value", [10 ** 12, -(10 ** 12), "1000000000000", "1/1000000000000", "0000000000001", 10 ** 5000], ids=["integer", "negative-integer", "string", "denominator", "written-leading-zeros", "huge-integer"])
def test_literal_digit_limit_is_enforced_before_evaluation(value: int | str) -> None:
    literal = {"kind": "rational", "value": value}
    payload = make_payload(claim={"kind": "binary", "op": "eq", "left": literal, "right": literal})
    result = check_transfer(payload)
    assert result["verdict"] == "invalid_input"
    assert result["errors"][0]["code"] == "rational_too_large"


def test_twelve_digit_literal_remains_admitted() -> None:
    literal = {"kind": "rational", "value": 999999999999}
    payload = make_payload(claim={"kind": "binary", "op": "eq", "left": literal, "right": literal})
    assert check_transfer(payload)["verdict"] == "no_counterexample_in_instance"


@pytest.mark.parametrize("ident", ["unicode-π", "escaped-" + chr(0xD800)])
def test_supplied_strings_have_a_reproducible_serializable_hash(ident: str) -> None:
    payload = make_payload(claim=b(True))
    payload["id"] = ident
    result = check_transfer(payload)
    assert result["verdict"] == "no_counterexample_in_instance"
    assert result["normalized_input"]["id"] == ident
    encoded = json.dumps(result["normalized_input"], sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    assert result["normalized_input_sha256"] == hashlib.sha256(encoded).hexdigest()
    assert json.loads(json.dumps(result))["id"] == ident


@pytest.mark.parametrize("content", [b"\xff", b"1" * 5000], ids=["invalid-utf8", "huge-integer-token"])
def test_cli_decoder_failures_return_json_without_traceback(tmp_path, content: bytes) -> None:
    source = tmp_path / "invalid.json"
    source.write_bytes(content)
    completed = subprocess.run([sys.executable, "-m", "atlas_checks", str(source)], capture_output=True, text=True, encoding="utf-8", timeout=10)
    assert completed.returncode == 2
    assert json.loads(completed.stdout)["verdict"] == "invalid_input"
    assert not completed.stderr


def test_cli_parser_recursion_limit_is_reported(monkeypatch, tmp_path, capsys) -> None:
    source = tmp_path / "nested.json"
    source.write_text("[]", encoding="utf-8")
    parse = json.loads
    def limited_parser(_text):
        raise RecursionError("parser depth limit")
    monkeypatch.setattr(json, "loads", limited_parser)
    assert main([str(source)]) == 2
    result = parse(capsys.readouterr().out)
    assert result["verdict"] == "invalid_input"
    assert result["errors"][0]["code"] == "invalid_json"
