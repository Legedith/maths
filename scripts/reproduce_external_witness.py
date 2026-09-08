"""Run the frozen two-case replay and the independent arithmetic certificate."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True,
                        help='A new output directory; existing evidence is never overwritten.')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    experiment = root / 'experiments/external-witness-replay'
    evidence = root / 'evidence/external-witness'
    freeze = json.loads((evidence / 'author/preexecution-freeze-attempt02.json').read_text(encoding='utf-8'))
    for record in freeze['files']:
        data = (experiment / record['path']).read_bytes()
        if len(data) != record['bytes'] or hashlib.sha256(data).hexdigest() != record['sha256']:
            raise ValueError(f"Frozen input changed: {record['path']}")
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    commands = [
        ['uv', 'run', '--project', str(experiment), '--frozen', 'python',
         str(experiment / 'replay.py'), '--output-dir', str(output / 'replay')],
        [sys.executable, str(evidence / 'independent/direct_certificate_check.py'),
         '--encoding', str(experiment / 'encoding.json'),
         '--results', str(output / 'replay/results'), '--output', str(output / 'direct-certificate.json')],
    ]
    observations = []
    for index, command in enumerate(commands, 1):
        started = datetime.now(timezone.utc).isoformat()
        try:
            result = subprocess.run(command, cwd=root, capture_output=True, timeout=180)
            stdout, stderr, code = result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired as exc:
            stdout, stderr, code = exc.stdout or b'', exc.stderr or b'', 124
        (output / f'command-{index}.stdout.log').write_bytes(stdout)
        (output / f'command-{index}.stderr.log').write_bytes(stderr)
        observations.append({'argv': command, 'cwd': str(root), 'started_at': started,
                             'ended_at': datetime.now(timezone.utc).isoformat(), 'exit_code': code,
                             'timeout_seconds': 180})
        (output / 'commands.json').write_text(json.dumps(observations, indent=2) + '\n', encoding='utf-8')
        if code:
            print(json.dumps({'passed': False, 'failed_command': index, 'exit_code': code}))
            return code
    summary = json.loads((output / 'replay/results/result-summary.json').read_text(encoding='utf-8'))
    certificate = json.loads((output / 'direct-certificate.json').read_text(encoding='utf-8'))
    passed = summary['author_expected_checks_pass'] is True and certificate['all_pass'] is True
    comparisons = []
    for record in json.loads((evidence / 'author/result-freeze.json').read_text(encoding='utf-8'))['files']:
        relative = Path(record['path']).relative_to('run-01')
        if relative.name == 'command.json':
            continue
        actual = hashlib.sha256((output / 'replay' / relative).read_bytes()).hexdigest()
        comparisons.append({'path': relative.as_posix(), 'sha256': actual,
                            'matches_author_bytes': actual == record['sha256']})
    report = {'passed': passed, 'known_case_count': summary['known_case_count'],
              'direct_certificate_pass': certificate['all_pass'],
              'output_byte_observations': comparisons,
              'scope': 'Two disclosed finite cases only. Byte equality is reported separately; exact certificate checks decide success.'}
    (output / 'integration-result.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'passed': passed, 'known_case_count': summary['known_case_count'],
                      'byte_identical_non_command_outputs': sum(row['matches_author_bytes'] for row in comparisons)}))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
