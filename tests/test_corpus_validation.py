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


@pytest.mark.parametrize("mutation", [
    "old-schema", "boolean-coordinate", "infinite-coordinate", "huge-coordinate",
    "missing-witness", "one-way-witness", "invalid-witness", "missing-scope",
    "empty-scope", "invalid-boundary", "source-attributed-zero", "empty-conventions",
    "empty-notation", "invalid-curation", "wrong-curation-id", "bad-hash",
    "stale-hash", "escaping-curation", "missing-curation-file", "malformed-edge-id",
    "null-curation-path", "invalid-windows-curation-path",
])
def test_conditioned_translation_boundaries(tmp_path, mutation):
    data = json.loads((WORKSPACE / "data/atlas.json").read_text(encoding="utf-8"))
    edge = next(e for e in data["edges"] if e["id"] == "boolean-rank-r3")
    if mutation == "old-schema":
        data["schema_version"] = "1.0"
    elif mutation.endswith("coordinate"):
        data["nodes"][0]["x"] = {"boolean-coordinate": True, "infinite-coordinate": float("inf"), "huge-coordinate": 10**400}[mutation]
    elif mutation == "missing-witness":
        del edge["witness_translation"]
    elif mutation == "one-way-witness":
        del edge["witness_translation"]["reverse"]
    elif mutation == "invalid-witness":
        edge["witness_translation"] = []
    elif mutation == "missing-scope":
        del edge["source_scope"]
    elif mutation == "empty-scope":
        edge["source_scope"] = " "
    elif mutation == "invalid-boundary":
        edge["local_boundary_case"] = None
    elif mutation == "source-attributed-zero":
        edge["local_boundary_case"]["evidence_basis"] = "cited_source"
    elif mutation == "empty-conventions":
        edge["local_boundary_case"]["adopted_conventions"] = []
    elif mutation == "empty-notation":
        edge["notation_boundaries"] = []
    elif mutation == "invalid-curation":
        edge["curation_record"] = []
    elif mutation == "wrong-curation-id":
        edge["curation_record"]["id"] = "R1"
    elif mutation == "bad-hash":
        edge["curation_record"]["artifact_sha256"] = "wrong"
    elif mutation == "stale-hash":
        edge["curation_record"]["artifact_sha256"] = "0" * 64
    elif mutation == "escaping-curation":
        edge["curation_record"]["artifact"] = "../outside.json"
    elif mutation == "missing-curation-file":
        edge["curation_record"]["independent_review"] = "evidence/missing-review.json"
    elif mutation == "null-curation-path":
        edge["curation_record"]["artifact"] = "evidence/bad\x00.json"
    elif mutation == "invalid-windows-curation-path":
        edge["curation_record"]["artifact"] = 'evidence/<bad>.json'
    elif mutation == "malformed-edge-id":
        edge["id"] = []
    corpus, report = tmp_path / "corpus.json", tmp_path / "report.json"
    corpus.write_text(json.dumps(data), encoding="utf-8")
    result = subprocess.run([sys.executable, "scripts/validate_atlas.py", str(corpus), "--output", str(report)], cwd=WORKSPACE, capture_output=True, text=True)
    assert result.returncode == 1, result.stderr
    assert json.loads(report.read_text(encoding="utf-8"))["errors"]
    assert "Traceback" not in result.stderr
