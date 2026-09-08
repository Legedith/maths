from __future__ import annotations

from typing import Any


def q(value: int | str) -> dict[str, Any]:
    return {"kind": "rational", "value": value}


def b(value: bool) -> dict[str, Any]:
    return {"kind": "boolean", "value": value}


def qty(name: str) -> dict[str, Any]:
    return {"kind": "quantity", "name": name}


def binary(op: str, left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    return {"kind": "binary", "op": op, "left": left, "right": right}


def unary(op: str, arg: dict[str, Any]) -> dict[str, Any]:
    return {"kind": "unary", "op": op, "arg": arg}


def entry(arg: dict[str, Any], *indices: int) -> dict[str, Any]:
    return {"kind": "entry", "arg": arg, "indices": list(indices)}


def make_payload(
    *,
    n: int = 3,
    edges: list[dict[str, Any]] | None = None,
    source: int = 0,
    target: int = 1,
    assumptions: list[dict[str, Any]] | None = None,
    claim: dict[str, Any] | None = None,
    interpretation: str = "explicit",
    check_id: str = "development-case",
) -> dict[str, Any]:
    if edges is None:
        edges = [
            {"u": 0, "v": 1, "conductance": 1},
            {"u": 1, "v": 2, "conductance": 1},
        ]
    return {
        "id": check_id,
        "graph": {"n": n, "edges": edges},
        "source": source,
        "target": target,
        "provenance": {
            "kind": "synthetic",
            "source_url": "https://example.test/source",
            "source_locator": "development fixture",
            "annotation_id": f"annotation-{check_id}",
            "annotator": "development-worker",
            "interpretation": interpretation,
        },
        "assumptions": assumptions if assumptions is not None else [],
        "claim": claim if claim is not None else b(True),
    }


def assumption(identifier: str, expression: dict[str, Any]) -> dict[str, Any]:
    return {"id": identifier, "expression": expression}
