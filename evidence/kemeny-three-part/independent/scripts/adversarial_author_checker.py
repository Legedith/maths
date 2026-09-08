"""Replay the selected checker and probe certificate-corruption rejection."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys


EXPECTED_CHECKER = "08aee29b87793cb288eaa7dfe54dd748b169972c32e46ed6e1b5bb2e1f3327f5"
EXPECTED_CERTIFICATE = "540ea590fb2e3d671e95102ab8ac5b80a22752f85354c7ded4aa84a4848fb8a9"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checker", type=Path, required=True)
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--log-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    checker = args.checker.resolve(strict=True)
    certificate = args.certificate.resolve(strict=True)
    if sha256(checker) != EXPECTED_CHECKER:
        raise RuntimeError("selected checker hash mismatch")
    if sha256(certificate) != EXPECTED_CERTIFICATE:
        raise RuntimeError("selected certificate hash mismatch")

    original = json.loads(certificate.read_text(encoding="utf-8"))
    mutations: dict[str, tuple[str, dict | None]] = {
        "original": ("must_accept", None),
        "coefficient_plus_one": ("must_reject_core_corruption", deepcopy(original)),
        "three_exponents": ("must_reject_malformed_term", deepcopy(original)),
        "duplicate_exponent": ("must_reject_malformed_term", deepcopy(original)),
        "missing_schema": ("must_reject_checked_metadata", deepcopy(original)),
        "wrong_variable_order": ("must_reject_checked_metadata", deepcopy(original)),
        "missing_source_formula": ("probe_unchecked_provenance", deepcopy(original)),
        "wrong_target_identity": ("probe_unchecked_provenance", deepcopy(original)),
        "wrong_domain_substitution": ("probe_unchecked_provenance", deepcopy(original)),
        "unknown_top_level_field": ("probe_unchecked_provenance", deepcopy(original)),
    }
    mutations["coefficient_plus_one"][1]["polynomial"]["terms"][0]["coefficient"] += 1
    mutations["three_exponents"][1]["polynomial"]["terms"][0]["exponents"] = [5, 0, 0]
    mutations["duplicate_exponent"][1]["polynomial"]["terms"].append(
        deepcopy(mutations["duplicate_exponent"][1]["polynomial"]["terms"][0])
    )
    mutations["missing_schema"][1].pop("schema_version")
    mutations["wrong_variable_order"][1]["polynomial"]["variable_order"] = ["u", "A", "v", "P"]
    mutations["missing_source_formula"][1].pop("source_formula")
    mutations["wrong_target_identity"][1]["target"]["identity"] = "D2*brace=Q(A,u,v,P)"
    mutations["wrong_domain_substitution"][1]["domain_substitution"]["selected_part"] = "x=2+A"
    mutations["unknown_top_level_field"][1]["unexpected"] = "accepted-or-rejected"

    args.artifact_dir.mkdir(parents=True, exist_ok=True)
    args.log_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for name, (classification, mutation) in mutations.items():
        if mutation is None:
            input_path = certificate
        else:
            input_path = args.artifact_dir / f"{name}.json"
            input_path.write_text(json.dumps(mutation, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")

        output_path = args.artifact_dir / f"{name}.checker-output.json"
        command = [
            sys.executable,
            str(checker),
            "--certificate",
            str(input_path),
            "--output",
            str(output_path),
        ]
        completed = subprocess.run(command, capture_output=True, check=False)
        stdout_path = args.log_dir / f"{name}.stdout.bin"
        stderr_path = args.log_dir / f"{name}.stderr.bin"
        stdout_path.write_bytes(completed.stdout)
        stderr_path.write_bytes(completed.stderr)
        results.append(
            {
                "case": name,
                "classification": classification,
                "command_argv": command,
                "input": {"path": str(input_path), "sha256": sha256(input_path)},
                "returncode": completed.returncode,
                "accepted": completed.returncode == 0,
                "output_created": output_path.is_file(),
                "output_sha256": sha256(output_path) if output_path.is_file() else None,
                "stdout": {"path": str(stdout_path), "bytes": len(completed.stdout), "sha256": sha256(stdout_path)},
                "stderr": {"path": str(stderr_path), "bytes": len(completed.stderr), "sha256": sha256(stderr_path)},
            }
        )

    by_name = {item["case"]: item for item in results}
    required_behavior = {
        "original_accepted": by_name["original"]["accepted"],
        "coefficient_corruption_rejected": not by_name["coefficient_plus_one"]["accepted"],
        "wrong_exponent_count_rejected": not by_name["three_exponents"]["accepted"],
        "duplicate_exponent_rejected": not by_name["duplicate_exponent"]["accepted"],
        "missing_schema_rejected": not by_name["missing_schema"]["accepted"],
        "wrong_variable_order_rejected": not by_name["wrong_variable_order"]["accepted"],
    }
    accepted_provenance_mutations = [
        item["case"]
        for item in results
        if item["classification"] == "probe_unchecked_provenance" and item["accepted"]
    ]
    report = {
        "schema_version": "selected-author-checker-adversarial-audit-v1",
        "checker": {"path": str(checker), "sha256": sha256(checker)},
        "certificate": {"path": str(certificate), "sha256": sha256(certificate)},
        "fresh_python": {"executable": sys.executable, "version": sys.version},
        "required_behavior": required_behavior,
        "required_behavior_pass": all(required_behavior.values()),
        "accepted_provenance_mutations": accepted_provenance_mutations,
        "interpretation": (
            "The selected checker rejects coefficient corruption and malformed core term arrays, "
            "but it is not a full provenance-schema validator if accepted_provenance_mutations is nonempty."
        ),
        "cases": results,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["required_behavior_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
