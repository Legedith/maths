import json
import subprocess
import sys
from pathlib import Path

from atlas_engine.evaluator import run_evaluation


def test_canonical_evaluator(tmp_path):
    summary = run_evaluation(tmp_path)
    assert summary["passed"] is True
    assert summary["counts_by_n"] == {"2": 1, "3": 4, "4": 38, "5": 728}
    assert summary["exhaustive_graph_count"] == 771
    assert summary["named_6_vertex_fixture_count"] == 1
    assert summary["record_count"] == 772
    assert len((tmp_path / "records.jsonl").read_text(encoding="utf-8").splitlines()) == 772


def test_analyze_cli(tmp_path):
    input_path = tmp_path / "input.json"
    input_path.write_text(
        json.dumps({"n": 2, "edges": [[0, 1]], "source": 0, "target": 1}),
        encoding="utf-8",
    )
    completed = subprocess.run(
        [sys.executable, "-m", "atlas_engine", "analyze", str(input_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0
    assert json.loads(completed.stdout)["resistance"] == "1"

