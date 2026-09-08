from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prior", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    prior = json.loads(args.prior.read_text(encoding="utf-8"))
    candidate = json.loads(args.candidate.read_text(encoding="utf-8"))

    prior_claims = {claim["id"]: claim for claim in prior["claims"]}
    candidate_claims = {claim["id"]: claim for claim in candidate["claims"]}
    rows = []
    for claim_id, old in prior_claims.items():
        new = candidate_claims[claim_id]
        old_supports = old["supports"]
        new_supports = new["supports"]
        rows.append({
            "id": claim_id,
            "type_unchanged": old["type"] == new["type"],
            "statement_unchanged": old["statement"] == new["statement"],
            "status_unchanged": old["status"] == new["status"],
            "prior_supports_preserved_as_prefix": new_supports[:len(old_supports)] == old_supports,
            "prior_support_count": len(old_supports),
            "candidate_support_count": len(new_supports),
            "added_support_count": len(new_supports) - len(old_supports),
        })

    result = {
        "schema_version": "msc-promotion-candidate-delta-v1",
        "prior": {"path": str(args.prior.resolve()), "sha256": sha256(args.prior)},
        "candidate": {"path": str(args.candidate.resolve()), "sha256": sha256(args.candidate)},
        "artifact_records_unchanged": prior["artifacts"] == candidate["artifacts"],
        "artifact_count": len(candidate["artifacts"]),
        "claim_id_set_unchanged": set(prior_claims) == set(candidate_claims),
        "claim_rows": rows,
        "all_claim_metadata_unchanged": all(
            row["type_unchanged"] and row["statement_unchanged"] and row["status_unchanged"]
            for row in rows
        ),
        "all_prior_supports_preserved_as_prefix": all(row["prior_supports_preserved_as_prefix"] for row in rows),
        "total_added_supports": sum(row["added_support_count"] for row in rows),
        "checks_unchanged": prior["checks"] == candidate["checks"],
        "limitations_unchanged": prior["limitations"] == candidate["limitations"],
    }
    result["all_pass"] = all([
        result["artifact_records_unchanged"],
        result["claim_id_set_unchanged"],
        result["all_claim_metadata_unchanged"],
        result["all_prior_supports_preserved_as_prefix"],
        result["total_added_supports"] == 12,
        result["checks_unchanged"],
        result["limitations_unchanged"],
    ])
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(args.output.resolve()),
        "output_sha256": sha256(args.output),
        "artifact_count": result["artifact_count"],
        "total_added_supports": result["total_added_supports"],
        "all_pass": result["all_pass"],
    }, indent=2))


if __name__ == "__main__":
    main()
