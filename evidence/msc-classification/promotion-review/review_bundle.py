from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strict_equal(actual: Any, expected: Any) -> bool:
    return type(actual) is type(expected) and actual == expected


def pointer(value: Any, raw: str) -> Any:
    if raw == "":
        return value
    if not raw.startswith("/"):
        raise ValueError(f"invalid JSON pointer: {raw}")
    current = value
    for token in raw[1:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        if isinstance(current, list):
            current = current[int(token)]
        elif isinstance(current, dict):
            current = current[token]
        else:
            raise TypeError(f"cannot traverse {token!r} through {type(current).__name__}")
    return current


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", type=Path, required=True)
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    draft = json.loads(args.draft.read_text(encoding="utf-8"))
    project = args.project.resolve()

    artifacts: list[dict[str, Any]] = []
    artifact_by_id: dict[str, dict[str, Any]] = {}
    for entry in draft["artifacts"]:
        rel = PurePosixPath(entry["path"])
        structural_safe = not rel.is_absolute() and ".." not in rel.parts and str(rel) == entry["path"]
        target = (project / Path(*rel.parts)).resolve()
        within_project = target == project or project in target.parents
        exists = target.is_file()
        actual = sha256(target) if exists else None
        result = {
            "id": entry["id"],
            "path": entry["path"],
            "kind": entry["kind"],
            "producer": entry["producer"],
            "structural_safe": structural_safe,
            "within_project": within_project,
            "exists": exists,
            "expected_sha256": entry["sha256"],
            "actual_sha256": actual,
            "hash_match": exists and actual == entry["sha256"],
        }
        artifacts.append(result)
        artifact_by_id[entry["id"]] = {"declared": entry, "path": target, "result": result}

    claim_results: list[dict[str, Any]] = []
    claim_status = {claim["id"]: claim.get("status") for claim in draft["claims"]}
    for claim in draft["claims"]:
        support_results = []
        for support in claim["supports"]:
            if "claim_id" in support:
                actual = claim_status.get(support["claim_id"])
                support_results.append({
                    "kind": "claim",
                    "claim_id": support["claim_id"],
                    "actual_status": actual,
                    "pass": actual == "supported",
                })
                continue
            artifact = artifact_by_id[support["artifact_id"]]
            locator = support["locator"]
            row: dict[str, Any] = {"kind": "artifact", "artifact_id": support["artifact_id"], "locator": locator}
            try:
                if locator.startswith("json:"):
                    parsed = json.loads(artifact["path"].read_text(encoding="utf-8"))
                    actual = pointer(parsed, locator.removeprefix("json:"))
                    expected = support["expected"]
                    passed = strict_equal(actual, expected)
                    row.update({"expected": expected, "actual": actual, "pass": passed})
                elif locator.startswith("contains:"):
                    needle = locator.removeprefix("contains:")
                    text = artifact["path"].read_text(encoding="utf-8")
                    count = text.count(needle)
                    row.update({"needle": needle, "occurrences": count, "pass": count > 0})
                else:
                    raise ValueError(f"unsupported locator: {locator}")
            except Exception as exc:
                row.update({"pass": False, "error": f"{type(exc).__name__}: {exc}"})
            support_results.append(row)
        claim_results.append({
            "id": claim["id"],
            "type": claim["type"],
            "declared_status": claim["status"],
            "statement": claim["statement"],
            "supports": support_results,
            "all_declared_support_locators_pass": all(item["pass"] for item in support_results),
        })

    ids = [item["id"] for item in draft["artifacts"]]
    paths = [item["path"] for item in draft["artifacts"]]
    claims = [item["id"] for item in draft["claims"]]
    artifact_digest_rows = [f'{row["id"]}\0{row["path"]}\0{row["actual_sha256"]}' for row in artifacts]
    result = {
        "schema_version": "1.0",
        "review_role": "independent promotion evidence reviewer; not importer, browser, test, or bundle author",
        "inputs": {
            "draft": {"path": str(args.draft.resolve()), "sha256": sha256(args.draft)},
            "project": str(project),
        },
        "structural_checks": {
            "artifact_count": len(artifacts),
            "claim_count": len(claim_results),
            "artifact_ids_unique": len(ids) == len(set(ids)),
            "artifact_paths_unique": len(paths) == len(set(paths)),
            "claim_ids_unique": len(claims) == len(set(claims)),
            "all_paths_structurally_safe": all(row["structural_safe"] and row["within_project"] for row in artifacts),
        },
        "artifact_summary": {
            "exists": sum(row["exists"] for row in artifacts),
            "hash_matches": sum(row["hash_match"] for row in artifacts),
            "all_match": all(row["hash_match"] for row in artifacts),
            "canonical_actual_inventory_sha256": hashlib.sha256("\n".join(artifact_digest_rows).encode("utf-8")).hexdigest(),
        },
        "artifacts": artifacts,
        "claim_summary": {
            "locator_checks": sum(len(row["supports"]) for row in claim_results),
            "claims_with_all_declared_locators_passing": sum(row["all_declared_support_locators_pass"] for row in claim_results),
            "all_declared_locators_pass": all(row["all_declared_support_locators_pass"] for row in claim_results),
        },
        "claims": claim_results,
        "scope_limit": "Mechanical support-locator success does not establish that a locator is sufficient for every semantic clause. That is reviewed separately.",
    }
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(args.output.resolve()),
        "output_sha256": sha256(args.output),
        "artifact_summary": result["artifact_summary"],
        "claim_summary": result["claim_summary"],
        "structural_checks": result["structural_checks"],
    }, indent=2))


if __name__ == "__main__":
    main()