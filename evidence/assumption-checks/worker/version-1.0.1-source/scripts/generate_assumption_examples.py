"""Create explicitly annotated teaching examples, separate from held-out data."""
from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

from atlas_checks import check_transfer

ROOT = Path(__file__).resolve().parents[1]


def quantity(name: str) -> dict:
    return {"kind": "quantity", "name": name}


def binary(op: str, left: dict, right: dict) -> dict:
    return {"kind": "binary", "op": op, "left": left, "right": right}


def unit_conductance_guard(n: int) -> dict:
    """Every off-diagonal Laplacian entry is zero (nonedge) or minus one."""
    conditions = []
    for u, v in combinations(range(n), 2):
        entry = {"kind": "entry", "arg": quantity("laplacian"), "indices": [u, v]}
        conditions.append(binary("or", binary("eq", entry, {"kind": "rational", "value": 0}), binary("eq", entry, {"kind": "rational", "value": -1})))
    result = {"kind": "boolean", "value": True}
    for condition in conditions:
        result = binary("and", result, condition)
    return result


def example(ident: str, claim: dict, *, kind: str, locator: str) -> dict:
    return {
        "id": ident,
        "graph": {"n": 3, "edges": [
            {"u": 0, "v": 1, "conductance": 2},
            {"u": 1, "v": 2, "conductance": 1},
        ]},
        "source": 0, "target": 2,
        "provenance": {
            "kind": kind,
            "source_url": "https://pages.uoregon.edu/dlevin/MARKOV/mcmt2e.pdf",
            "source_locator": locator,
            "annotation_id": ident + "-root-annotation",
            "annotator": "root-teaching-example-author",
            "interpretation": "explicit",
        },
        "assumptions": [{"id": "connected-network", "expression": quantity("connected")}],
        "claim": claim,
    }


def main() -> None:
    correct = example(
        "weighted-commute-source-formula",
        binary("eq", quantity("commute"), binary("mul", quantity("total_conductance"), quantity("resistance"))),
        kind="source_annotation", locator="Second edition, book pp. 131-132, Proposition 10.7 and equations (10.9)-(10.14); graph volume is defined on book p. 116, equation (9.1).",
    )
    wrong = example(
        "weighted-commute-synthetic-missing-weights",
        binary("eq", quantity("commute"), binary("mul", binary("mul", {"kind": "rational", "value": 2}, quantity("edge_count")), quantity("resistance"))),
        kind="synthetic", locator="Deliberate alteration of the second edition's Proposition 10.7 (book pp. 131-132): replace graph volume by twice the unweighted edge count. This is not a claim made by the source.",
    )
    guarded = json.loads(json.dumps(wrong))
    guarded["id"] = "weighted-commute-failed-unit-weight-assumption"
    guarded["provenance"]["annotation_id"] = guarded["id"] + "-root-annotation"
    guarded["provenance"]["source_locator"] = "Teaching example: the unweighted specialization is explicitly guarded by unit edge weights. The chosen weighted graph violates that guard."
    guarded["assumptions"].append({
        "id": "all-edges-unit-conductance",
        "expression": unit_conductance_guard(guarded["graph"]["n"]),
    })
    inputs = [correct, wrong, guarded]
    target = ROOT / "fixtures/assumption-checks/teaching"
    output = ROOT / "evidence/assumption-checks/teaching"
    target.mkdir(parents=True, exist_ok=True)
    output.mkdir(parents=True, exist_ok=True)
    records = []
    for payload in inputs:
        path = target / (payload["id"] + ".json")
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        result = check_transfer(payload)
        record_path = output / (payload["id"] + ".json")
        record_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        records.append({"id": payload["id"], "input": path.relative_to(ROOT).as_posix(), "output": record_path.relative_to(ROOT).as_posix(), "verdict": result["verdict"]})
    report = {"kind": "authored_teaching_examples", "independent_review": "pending", "records": records,
              "scope": "Explicit root-authored annotations; separate from the sealed 80-case suite and 24-result prospective retrieval study. The deliberately altered formula is synthetic, not an error attributed to its source."}
    (output / "manifest.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
