"""Exact frozen comparisons for optimal repair of the specified hub-link failure."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from verify_certificate import Poly, ZERO, determinant, positive, require
from verify_all_deletions import coefficient_list


CERTIFICATE_SHA256 = '1f22a17478ebbfe24cbc75d557bc12a89c9c74db97dfb510cb4c99573052ae82'
COMPARISONS = [('uv', 'restore'), ('untouched_A', 'restore'), ('B', 'restore'),
               ('C', 'restore'), ('uv', 'untouched_A')]


def reduced_k(name):
    """Return numerator/denominator of K-n, with every inserted endpoint split."""
    x, y, z, t = [Poly.variable(i) for i in range(4)]
    a, b, c = 3+x, 3+x+y, 3+x+z
    if name in ('restore', 'uv'):
        sizes, parts = [1, 1, a-2, b, c, 1], [0, 0, 0, 1, 2, 3]
        inserted = (0, 1) if name == 'uv' else None
    elif name == 'untouched_A':
        sizes, parts = [1, 1, 1, a-3, b, c, 1], [0, 0, 0, 0, 1, 2, 3]
        inserted = (1, 2)
    elif name == 'B':
        sizes, parts = [1, a-1, 1, 1, b-2, c, 1], [0, 0, 1, 1, 1, 2, 3]
        inserted = (2, 3)
    elif name == 'C':
        sizes, parts = [1, a-1, b, 1, 1, c-2, 1], [0, 0, 1, 2, 2, 2, 3]
        inserted = (3, 4)
    else:
        raise ValueError('unknown intervention')
    sizes = [Poly.coerce(size) for size in sizes]
    m = len(sizes)
    R = [[sizes[j] if parts[i] != parts[j] else Poly() for j in range(m)] for i in range(m)]
    if name != 'restore':
        R[0][-1] = R[-1][0] = Poly()
    if inserted is not None:
        i, j = inserted
        require(sizes[i] == 1 and sizes[j] == 1, 'inserted endpoints must be singleton cells')
        R[i][j] = R[j][i] = Poly(1)
    degrees = [sum(row) for row in R]
    for i in range(m):
        require(all(v > 0 for v in sizes[i].terms.values()), 'negative cell size coefficient')
        positive(degrees[i], f'{name}: degree {i}')
        for j in range(m):
            require(sizes[i]*R[i][j] == sizes[j]*R[j][i], 'cell balance fails')
    F = determinant([[(1+t)*degrees[i]-R[i][j] if i == j else -R[i][j]
                      for j in range(m)] for i in range(m)])
    require(F.t_coefficient(0) == 0, 'nonzero Laplacian determinant')
    first, second = [F.t_coefficient(k) for k in (1, 2)]
    positive(first, f'{name}: ratio denominator')
    # All residual cells are independent; only zero transition modes are omitted.
    # Keeping an empty A-rest at a=3 adds a virtual zero mode, canceled by -m.
    return second-m*first, first


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--certificate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), 'use a fresh output path')
    raw = args.certificate.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    require(digest == CERTIFICATE_SHA256, 'changed frozen optimal-repair certificate')
    data = json.loads(raw)['comparisons']
    require(set(data) == {f'{a} minus {b}' for a, b in COMPARISONS}, 'comparison list mismatch')
    values = {name: reduced_k(name) for name in ('restore', 'uv', 'untouched_A', 'B', 'C')}
    results = []
    for left, right in COMPARISONS:
        key = f'{left} minus {right}'
        numerator = coefficient_list(data[key]['numerator_certificate'])
        denominator = coefficient_list(data[key]['denominator_certificate'])
        positive(numerator, key+' numerator')
        positive(denominator, key+' denominator')
        ln, ld = values[left]
        rn, rd = values[right]
        require((ln*rd-rn*ld)*denominator == numerator*ld*rd,
                key+': full rational identity fails')
        results.append({
            'comparison': key, 'exact_rational_identity': True,
            'positive_numerator_and_denominator': True,
            'numerator_term_count': len(numerator.terms),
            'numerator_constant': numerator.terms[ZERO],
            'denominator_constant': denominator.terms[ZERO],
        })
    package = Path(__file__).parent
    result = {
        'schema_version': 'optimal-hub-link-repair-frozen-certificate-v1',
        'pass': True, 'certificate_sha256': digest,
        'implementation_sha256': {name: hashlib.sha256((package/name).read_bytes()).hexdigest()
                                  for name in ('verify_optimal_repair.py', 'verify_all_deletions.py', 'verify_certificate.py')},
        'method': 'separate singleton endpoints, subset determinants modulo t^3, K-n=q2/q1-m, exact rational cross-products',
        'comparisons': results,
        'proof_boundary': 'The missing-edge orbit completeness, graph-to-quotient bridge and empty-cell boundary require independent mathematical audit. Unique optimality assumes exactly one unit-weight missing edge may be added and restoration uh is allowed. No assertion that untouched_A is the best alternative to restoration; no global novelty or practical-benefit certification.',
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes((json.dumps(result, indent=2)+'\n').encode())
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
