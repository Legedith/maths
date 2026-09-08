"""Corpus boundary regressions discovered by independent review."""
import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest

WORKSPACE = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("malformed", [[], {"nodes": "bad"}, {"edges": None}, {"nodes": [42]}, {"examples": 17}, {"nodes": [{"kind": [], "status": {}}]}, {"edges": [{"from": [], "to": {}}]}, {"sources": [{"url": "https://[bad"}]}, {"examples": [{"fixture": []}]}])
def test_malformed_collections_emit_report(tmp_path, malformed):
    corpus = tmp_path / "corpus.json"
    report = tmp_path / "report.json"
    corpus.write_text(json.dumps(malformed), encoding="utf-8")
    result = subprocess.run([sys.executable, "scripts/validate_atlas.py", str(corpus), "--output", str(report)], cwd=WORKSPACE, capture_output=True, text=True)
    assert result.returncode == 1, result.stderr
    assert json.loads(report.read_text(encoding="utf-8"))["passed"] is False
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize("mutation", ["missing-proof", "escaping-proof", "duplicate-example", "missing-fixture"])
def test_unbacked_evidence_rejected(tmp_path, mutation):
    data = copy.deepcopy(json.loads((WORKSPACE / "data/atlas.json").read_text(encoding="utf-8")))
    if mutation.endswith("proof"):
        data["edges"][0]["status"] = "formal"
        if mutation == "escaping-proof":
            outside = tmp_path / "outside.lean"
            outside.write_text("-- no proof", encoding="utf-8")
            data["edges"][0]["proof_artifact"] = str(outside)
    elif mutation == "duplicate-example":
        data["examples"].append(copy.deepcopy(data["examples"][0]))
    else:
        data["examples"][0]["fixture"] = "missing-fixture"
    corpus, report = tmp_path / "corpus.json", tmp_path / "report.json"
    corpus.write_text(json.dumps(data), encoding="utf-8")
    result = subprocess.run([sys.executable, "scripts/validate_atlas.py", str(corpus), "--output", str(report)], cwd=WORKSPACE, capture_output=True, text=True)
    assert result.returncode == 1, result.stderr
    assert json.loads(report.read_text(encoding="utf-8"))["errors"]
