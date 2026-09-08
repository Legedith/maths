"""Validate curated graph integrity. This checks structure, not source entailment."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from urllib.parse import urlparse


def validate(data: object) -> dict[str, object]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return {"passed": False, "errors": ["corpus must be an object"]}
    def require(ok: bool, message: str) -> None:
        if not ok:
            errors.append(message)
    def text(value: object) -> bool:
        return isinstance(value, str) and bool(value.strip())
    def strings(value: object) -> bool:
        return isinstance(value, list) and bool(value) and all(text(x) for x in value)
    def member(value: object, choices: set[str]) -> bool:
        return isinstance(value, str) and value in choices
    require(data.get("schema_version") == "1.1", "unsupported schema version")
    for field in ("title", "scope"):
        require(text(data.get(field)), f"missing {field}")
    records: dict[str, list[dict]] = {}
    identifiers: dict[str, set[str]] = {}
    for category in ("nodes", "edges", "sources", "journeys", "opportunities"):
        items = data.get(category)
        if not isinstance(items, list) or not all(isinstance(x, dict) for x in items):
            errors.append(f"{category} must be an array of objects")
            items = []
        records[category] = items
        ids = [x.get("id") for x in items]
        require(all(text(x) for x in ids), f"{category}: missing ID")
        valid_ids = [x for x in ids if isinstance(x, str)]
        require(len(valid_ids) == len(set(valid_ids)), f"{category}: duplicate ID")
        identifiers[category] = set(valid_ids)
    def evidence(item: dict, context: str) -> None:
        values = item.get("evidence")
        if not isinstance(values, list) or not values:
            errors.append(f"{context}: evidence required")
            return
        for v in values:
            require(isinstance(v, dict) and member(v.get("source"), identifiers["sources"]) and text(v.get("locator")), f"{context}: invalid source or locator")
    for s in records["sources"]:
        for key in ("title", "author", "locator", "note"):
            require(text(s.get(key)), f"source {s.get('id')}: missing {key}")
        try:
            url = urlparse(s.get("url", "") if isinstance(s.get("url"), str) else "")
            valid_url = url.scheme == "https" and bool(url.netloc)
        except ValueError:
            valid_url = False
        require(valid_url, f"source {s.get('id')}: HTTPS URL required")
        require(type(s.get("year")) is int, f"source {s.get('id')}: year must be integer")
    for n in records["nodes"]:
        context = f"node {n.get('id')}"
        require(member(n.get("kind"), {"concept", "theorem", "method", "problem", "example"}), f"{context}: invalid kind")
        require(member(n.get("status"), {"sourced", "formally_verified", "proposed"}), f"{context}: invalid status")
        for key in ("label", "summary", "explanation", "cluster", "level"):
            require(text(n.get(key)), f"{context}: missing {key}")
        for key in ("domains", "assumptions"):
            require(strings(n.get(key)), f"{context}: missing {key}")
        for key in ("x", "y"):
            value = n.get(key)
            require(type(value) in (int, float) and -1.7976931348623157e308 <= value <= 1.7976931348623157e308, f"{context}: {key} must be finite numeric metadata")
        require(isinstance(n.get("aliases"), list) and all(text(x) for x in n["aliases"]), f"{context}: invalid aliases")
        if n.get("status") == "formally_verified":
            require(text(n.get("proof_artifact")), f"{context}: formal status needs proof artifact")
        evidence(n, context)
    for e in records["edges"]:
        context = f"edge {e.get('id')}"
        require(member(e.get("from"), identifiers["nodes"]) and member(e.get("to"), identifiers["nodes"]), f"{context}: dangling endpoint")
        require(e.get("from") != e.get("to"), f"{context}: self relation requires a new schema decision")
        require(text(e.get("type")) and text(e.get("statement")), f"{context}: named relation and statement required")
        require(strings(e.get("assumptions")), f"{context}: assumptions required")
        require(member(e.get("status"), {"established", "proposed", "formal"}), f"{context}: invalid evidence status")
        if e.get("status") == "formal":
            require(text(e.get("proof_artifact")), f"{context}: formal status needs proof artifact")
        details = ("source_scope", "witness_translation", "local_boundary_case", "notation_boundaries", "curation_record")
        admitted = {f"boolean-rank-r{i}": f"R{i}" for i in range(1, 5)}
        is_admitted = isinstance(e.get("id"), str) and e["id"] in admitted
        if is_admitted:
            for key in details:
                require(key in e, f"{context}: {key} required for admitted translation")
        if "source_scope" in e:
            require(text(e["source_scope"]), f"{context}: source_scope must be nonempty text")
        if "witness_translation" in e:
            witness = e["witness_translation"]
            require(isinstance(witness, dict) and all(text(witness.get(k)) for k in ("forward", "reverse", "result")), f"{context}: complete two-way witness required")
        if "local_boundary_case" in e:
            boundary = e["local_boundary_case"]
            require(isinstance(boundary, dict) and all(text(boundary.get(k)) for k in ("case", "argument", "result")) and strings(boundary.get("adopted_conventions")) and boundary.get("evidence_basis") == "atlas_local_definition_and_proof", f"{context}: local boundary needs explicit conventions, argument, result and Atlas evidence basis")
        if "notation_boundaries" in e:
            require(strings(e["notation_boundaries"]), f"{context}: notation_boundaries must be nonempty text array")
        if "curation_record" in e:
            curation = e["curation_record"]
            require(isinstance(curation, dict), f"{context}: curation_record must be an object")
            if isinstance(curation, dict):
                require(member(curation.get("id"), {"R1", "R2", "R3", "R4"}), f"{context}: invalid curation ID")
                if is_admitted:
                    require(curation.get("id") == admitted[e["id"]], f"{context}: curation ID must match relation")
                for key in ("artifact", "independent_review"):
                    require(safe_relative_path(curation.get(key)), f"{context}: {key} must be a relative workspace path")
                    digest = curation.get(f"{key}_sha256")
                    require(isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest) is not None, f"{context}: invalid {key} SHA-256")
        evidence(e, context)
    for j in records["journeys"]:
        require(text(j.get("title")) and text(j.get("description")), f"journey {j.get('id')}: missing explanation")
        steps = j.get("steps")
        require(isinstance(steps, list) and bool(steps), f"journey {j.get('id')}: steps required")
        for s in steps if isinstance(steps, list) else []:
            require(isinstance(s, dict) and member(s.get("node"), identifiers["nodes"]) and text(s.get("prompt")), f"journey {j.get('id')}: invalid step")
    for o in records["opportunities"]:
        for key in ("title", "description", "kind", "difficulty", "status"):
            require(text(o.get(key)), f"opportunity {o.get('id')}: missing {key}")
        require(strings(o.get("acceptance")), f"opportunity {o.get('id')}: acceptance criteria required")
        require(isinstance(o.get("nodes"), list) and bool(o["nodes"]) and all(member(n, identifiers["nodes"]) for n in o["nodes"]), f"opportunity {o.get('id')}: invalid concept reference")
    examples = data.get("examples", [])
    require(isinstance(examples, list), "examples must be an array")
    example_ids = [e.get("id") for e in examples if isinstance(e, dict)] if isinstance(examples, list) else []
    require(all(text(i) for i in example_ids) and len(example_ids) == len(set(i for i in example_ids if isinstance(i, str))), "example IDs must be nonempty and unique")
    for e in examples if isinstance(examples, list) else []:
        require(isinstance(e, dict) and e.get("kind") == "example" and e.get("status") == "finite-computation" and text(e.get("fixture")) and e.get("artifact") == "fixtures/frozen.json" and isinstance(e.get("concepts"), list) and all(member(n, identifiers["nodes"]) for n in e["concepts"]), "example requires a fixture, explicit finite scope and valid concept IDs")
    return {"passed": not errors, "counts": {**{k: len(v) for k, v in records.items()}, "examples": len(examples) if isinstance(examples, list) else 0}, "errors": errors, "scope": "Structural consistency only. Independent review must establish source entailment and proof status."}


def safe_relative_path(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip()) and not any(ord(char) < 32 or char in '\\:<>"|?*' for char in value) and not PurePosixPath(value).is_absolute() and all(part not in ("..", ".") for part in value.split("/")) and all(value.split("/"))


def check_curation_files(data: dict, workspace: Path) -> list[str]:
    errors: list[str] = []
    edges = data.get("edges", [])
    for edge in edges if isinstance(edges, list) else []:
        record = edge.get("curation_record") if isinstance(edge, dict) else None
        if not isinstance(record, dict):
            continue
        for key in ("artifact", "independent_review"):
            relative = record.get(key)
            if not safe_relative_path(relative):
                continue  # Already rejected by structural validation.
            try:
                path = (workspace / relative).resolve()
                if not path.is_relative_to(workspace) or not path.is_file():
                    errors.append(f"{edge.get('id')}: {key} must resolve to a file inside the workspace")
                elif hashlib.sha256(path.read_bytes()).hexdigest() != record.get(f"{key}_sha256"):
                    errors.append(f"{edge.get('id')}: {key} hash mismatch")
            except (OSError, ValueError) as exc:
                errors.append(f"{edge.get('id')}: cannot read {key}: {type(exc).__name__}")
    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", nargs="?", default="data/atlas.json")
    parser.add_argument("--output", default="evidence/corpus/validation.json")
    args = parser.parse_args()
    data = json.loads(Path(args.corpus).read_text(encoding="utf-8"))
    report = validate(data)
    # A malformed top-level value must retain the validator report, not crash follow-up checks.
    if not isinstance(data, dict):
        data = {}
    workspace = Path.cwd().resolve()
    report["errors"].extend(check_curation_files(data, workspace))
    def safe_records(category: str) -> list[dict]:
        items = data.get(category, [])
        return [item for item in items if isinstance(item, dict)] if isinstance(items, list) else []
    for item in [*safe_records("nodes"), *safe_records("edges")]:
        if item.get("status") in ("formal", "formally_verified") and isinstance(item.get("proof_artifact"), str):
            artifact = (workspace / item["proof_artifact"]).resolve()
            if not artifact.is_relative_to(workspace) or not artifact.is_file():
                report["errors"].append(f"{item.get('id')}: proof artifact must resolve to a file inside the workspace")
    fixture_ids = {f["id"] for f in json.loads((workspace / "fixtures/frozen.json").read_text(encoding="utf-8"))["valid"]}
    for example in safe_records("examples"):
        if not isinstance(example.get("fixture"), str) or example["fixture"] not in fixture_ids:
            report["errors"].append(f"example {example.get('id')}: fixture does not exist")
    report["passed"] = not report["errors"]
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["passed"] else 1)
