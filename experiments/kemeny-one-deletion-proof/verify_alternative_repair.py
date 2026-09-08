"""Exact optimum-set comparisons when restoration of the hub edge is forbidden."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from verify_certificate import ZERO, positive, require
from verify_all_deletions import coefficient_list
from verify_optimal_repair import CERTIFICATE_SHA256 as PRIOR_SHA256, reduced_k


CERTIFICATE_SHA256 = 'ca626bd80211a00907089a877f5685c29a426f783f8df93418e2272a16e1b602'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--certificate', type=Path, required=True)
    parser.add_argument('--prior-certificate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), 'use a fresh output path')
    raw, prior_raw = args.certificate.read_bytes(), args.prior_certificate.read_bytes()
    digest, prior_digest = [hashlib.sha256(value).hexdigest() for value in (raw, prior_raw)]
    require(digest == CERTIFICATE_SHA256, 'changed frozen alternative-repair certificate')
    require(prior_digest == PRIOR_SHA256, 'changed prior optimal-repair certificate')
    data, prior = json.loads(raw), json.loads(prior_raw)
    require(data['input_sha256'] == prior_digest, 'new certificate uses a different prior input')
    require(set(data['comparisons']) == {'B', 'C'}, 'incorrect new comparison set')
    values = {name: reduced_k(name) for name in ('uv', 'untouched_A', 'B', 'C')}
    proofs = [(name, data['comparisons'][name]['numerator_terms'],
               data['comparisons'][name]['denominator_terms'], 'new') for name in ('B', 'C')]
    uv = prior['comparisons']['uv minus untouched_A']
    proofs.append(('uv', uv['numerator_certificate'], uv['denominator_certificate'], 'previously audited'))
    target_numerator, target_denominator = values['untouched_A']
    results = []
    for name, numerator_terms, denominator_terms, provenance in proofs:
        numerator, denominator = coefficient_list(numerator_terms), coefficient_list(denominator_terms)
        positive(numerator, name+' numerator')
        positive(denominator, name+' denominator')
        left_numerator, left_denominator = values[name]
        raw_numerator = left_numerator*target_denominator-target_numerator*left_denominator
        require(raw_numerator*denominator == numerator*left_denominator*target_denominator,
                name+': complete exact rational identity fails')
        results.append({
            'comparison': name+' minus untouched_A', 'provenance': provenance,
            'exact_rational_identity': True, 'positive_numerator_and_denominator': True,
            'numerator_term_count': len(numerator.terms),
            'minimum_numerator_coefficient': min(numerator.terms.values()),
            'numerator_constant': numerator.terms[ZERO],
            'denominator_constant': denominator.terms[ZERO],
        })
    package = Path(__file__).parent
    result = {
        'schema_version': 'forbidden-restoration-optimum-frozen-certificate-v1',
        'pass': True, 'certificate_sha256': digest, 'prior_certificate_sha256': prior_digest,
        'implementation_sha256': {name: hashlib.sha256((package/name).read_bytes()).hexdigest()
                                 for name in ('verify_alternative_repair.py', 'verify_optimal_repair.py',
                                              'verify_all_deletions.py', 'verify_certificate.py')},
        'method': 'reuse singleton-endpoint exact determinants; cross-multiply two new comparisons and prior uv domination',
        'comparisons': results,
        'proof_boundary': 'The orbit argument proves the optimal set is all unordered pairs in A excluding u, with binomial(a-1,2) edges and uniqueness only at a=3. This graph/domain/counting bridge is independently audited in the accompanying proof. Exactly one unit-weight insertion, restoration forbidden, stationary-target K; no fixed-workload, priority, or practical-benefit certification.',
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes((json.dumps(result, indent=2)+'\n').encode())
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
