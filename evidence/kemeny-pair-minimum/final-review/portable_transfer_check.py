from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path("D:/CodexWorkspaces/mathematics-atlas")
SOURCE = ROOT / "kemeny-portable-work"
STUDY_COPY = ROOT / "kemeny-study-work/portable"
PROJECT = ROOT / "project"
PROJECT_PACKAGE = PROJECT / "experiments/kemeny-pair-minimum"
TRANSFER = ROOT / "kemeny-study-work/evidence/portable-transfer.json"
OUTPUT = ROOT / "kemeny-final-review-work/raw/portable-transfer-check.json"

EXPECTED_TRANSFER_SHA256 = "a9f24df57d0ae0fa764db60c32925e2d8f00f18824b280e64cb0f393ffa60131"
EXPECTED_SOURCE_MANIFEST_SHA256 = "d5bbdd58126de29f2db378c08a287ac4d28272569ee386aa2347fbc6f898f420"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def publishable_package_files(root: Path) -> set[str]:
    result = set()
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if ".venv" in relative.parts or "__pycache__" in relative.parts or path.suffix == ".pyc":
            continue
        result.add(relative.as_posix())
    return result


def main() -> None:
    assert sha256(TRANSFER) == EXPECTED_TRANSFER_SHA256
    transfer = json.loads(TRANSFER.read_text(encoding="utf-8"))
    assert transfer["schema_version"] == "kemeny-portable-exact-transfer-v1"
    assert transfer["status"] == "exact_copy_pending_independent_adapter_review"
    assert transfer["source_manifest_sha256"] == EXPECTED_SOURCE_MANIFEST_SHA256
    records = transfer["copied"]
    assert len({item["path"] for item in records}) == len(records)

    study_count = 0
    project_count = 0
    for item in records:
        source = SOURCE / item["source_path"]
        destination = Path(item["path"])
        assert source.is_file() and destination.is_file()
        assert source.stat().st_size == destination.stat().st_size == item["bytes"]
        assert sha256(source) == sha256(destination) == item["sha256"]
        assert source.read_bytes() == destination.read_bytes()
        try:
            destination.relative_to(STUDY_COPY)
        except ValueError:
            destination.relative_to(PROJECT_PACKAGE)
            project_count += 1
        else:
            study_count += 1
    assert study_count == 85
    assert project_count == 33

    source_package = SOURCE / "experiments/kemeny-pair-minimum"
    source_files = publishable_package_files(source_package)
    project_files = publishable_package_files(PROJECT_PACKAGE)
    assert len(source_files) == len(project_files) == 33
    assert source_files == project_files
    for relative in sorted(source_files):
        assert (source_package / relative).read_bytes() == (PROJECT_PACKAGE / relative).read_bytes()

    workflow = PROJECT / ".github/workflows/kemeny-pair.yml"
    workflow_text = workflow.read_text(encoding="utf-8")
    required_workflow_fragments = (
        "runs-on: ubuntu-latest",
        "timeout-minutes: 70",
        "permissions:\n  contents: read",
        "actions/checkout@11d5960a326750d5838078e36cf38b85af677262",
        "astral-sh/setup-uv@d0d8abe699bfb85fec6de9f7adb5ae17292296ff",
        "version: '0.8.19'",
        "python-version: '3.12.11'",
        "uv run --project experiments/kemeny-pair-minimum/independent --frozen python experiments/kemeny-pair-minimum/reproduce.py --output-dir work/kemeny-pair-ci",
        "if: always()",
        "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02",
        "path: work/kemeny-pair-ci/",
        "retention-days: 30",
    )
    assert all(fragment in workflow_text for fragment in required_workflow_fragments)
    gitignore = (PROJECT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert "/work/" in gitignore
    assert "**/.venv/" in gitignore
    assert "*.pyc" in gitignore

    report = {
        "schema_version": "kemeny-portable-transfer-independent-check-v1",
        "auditor": "/root/sol_symmetry_audit",
        "status": "pass",
        "inputs": {
            "transfer": {"path": str(TRANSFER), "bytes": TRANSFER.stat().st_size, "sha256": sha256(TRANSFER)},
            "portable_result_manifest_sha256": sha256(SOURCE / "result-manifest.json"),
            "workflow": {"path": str(workflow), "bytes": workflow.stat().st_size, "sha256": sha256(workflow)},
        },
        "exact_transfer": {
            "study_evidence_file_count": study_count,
            "project_package_file_count": project_count,
            "all_recorded_sources_and_destinations_byte_identical": True,
            "project_package_file_set_exactly_matches_frozen_staging_package": True,
        },
        "ci_workflow_static_review": {
            "status": "pass_pending_first_remote_run",
            "ubuntu_latest": True,
            "job_timeout_minutes": 70,
            "uv_version": "0.8.19",
            "python_version": "3.12.11",
            "same_portable_command": True,
            "actions_pinned_by_commit": True,
            "permissions_contents_read": True,
            "raw_outputs_uploaded_even_after_failure": True,
        },
        "limitations": [
            "This check proves byte-exact local transfer and reviews the workflow text. The Ubuntu run is future CI evidence and is not represented as already observed.",
            "The 70-minute job limit is compatible with two sequential 1800-second child limits plus runner overhead, but an actual platform run remains the operational check.",
        ],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": "pass", "output": str(OUTPUT), "sha256": sha256(OUTPUT)}, sort_keys=True))


if __name__ == "__main__":
    main()
