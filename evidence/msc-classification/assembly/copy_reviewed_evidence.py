"""Copy sealed MSC review artifacts without changing originals or prior copies."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path('D:/CodexWorkspaces/mathematics-atlas')
PROJECT = BASE / 'project'
TARGET = PROJECT / 'evidence/msc-classification'


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def contained(base: Path, relative: str) -> Path:
    path = (base / relative).resolve()
    if not path.is_relative_to(base.resolve()):
        raise ValueError(f'Path outside declared root: {relative}')
    return path


def copy_one(source: Path, destination: Path, records: list) -> None:
    if destination.exists():
        raise FileExistsError(destination)
    payload = source.read_bytes()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('xb') as stream:
        stream.write(payload)
    assert digest(destination) == hashlib.sha256(payload).hexdigest()
    records.append({'source': str(source), 'path': destination.relative_to(PROJECT).as_posix(), 'bytes': len(payload), 'sha256': digest(destination)})


def main() -> None:
    if TARGET.exists():
        raise FileExistsError(TARGET)
    groups = [
        ('msc-reuse-review-work', 'publication-manifest.json', '676f12cf881b414a8fe4bdbd53d4626e168920a70a0376e6ea05d2124656b505', 'source-review'),
        ('msc-import-review-work', 'publication-manifest.json', '23757db4d2d1fd8c573c8479d8af27cd2d3772ff498d8ca1437945ab4e19e5f1', 'adapter-review'),
        ('msc-import-work', 'result-manifest-v3.json', 'a3ad7a74a90e516a17173604adc87262c524ecc3d5ad000d611d90218a245f3e', 'adapter-history'),
    ]
    planned, omitted = [], []
    for source_directory, manifest_name, expected, destination_directory in groups:
        source_root = BASE / source_directory
        manifest_path = source_root / manifest_name
        assert digest(manifest_path) == expected, manifest_path
        manifest = json.loads(manifest_path.read_text(encoding='utf-8-sig'))
        for row in manifest['artifacts']:
            source = contained(source_root, row['path'])
            assert digest(source) == row['sha256'], source
            assert source.stat().st_size == row['bytes'], source
            if destination_directory == 'adapter-history' and row['path'].startswith(('run-01/', 'run-02/', 'run-03/')):
                omitted.append({'source': str(source), 'sha256': row['sha256'], 'reason': 'Retained locally; selected run-03 outputs are already published under data/msc. Earlier deterministic output versions remain represented by their sealed history hashes.'})
            else:
                planned.append((source, contained(TARGET / destination_directory, row['path'])))
        planned.append((manifest_path, TARGET / destination_directory / manifest_name))
    product_root = BASE / 'msc-product-work'
    for relative in ['preexecution-freeze.json', 'preexecution-freeze-02.json', 'check-subjects-v1.ts', 'checks-01.json', 'checks-02.json']:
        planned.append((product_root / relative, TARGET / 'product-history' / relative))
    for source in sorted((product_root / 'logs').glob('attempt-msc-*')):
        if source.is_file():
            planned.append((source, TARGET / 'product-history/logs' / source.name))
    records = []
    for source, destination in planned:
        copy_one(source, destination, records)
    report = {'schema_version': 'msc-publication-copy-v1', 'producer': 'root', 'files': records, 'omitted_duplicate_outputs': omitted, 'limitations': 'Full external research webpage snapshots remain local and are not required by the portable importer. Historical review paths retain their original locations. This byte-copy manifest does not self-certify semantic review.'}
    with (TARGET / 'publication-copy-01.json').open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'copied': len(records), 'omitted_duplicate_outputs': len(omitted), 'target': str(TARGET)}))


if __name__ == '__main__':
    main()
