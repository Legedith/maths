"""Exact frozen certificates for insertion after any one original edge fails."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from verify_certificate import Poly, ZERO, determinant, positive, require


CASES = {'uB': ('u', 'j'), 'rB': ('r', 'j'), 'BC': ('j', 'k'),
         'uh': ('u', 'h'), 'rh': ('r', 'h'), 'Bh': ('j', 'h')}
# Filled from the frozen author files by the release assembler; no generated input is accepted.
CERTIFICATE_HASHES = {
    "uB": "766cbf6c546f790d34cfa23a88e065bc5407c70369192b0bba63f7edf33f3be5",
    "rB": "100fbbed6fe0ec9a36359e51df4202b27ee7476553f2e67b04e2cce2d2687351",
    "BC": "da05aedc95d3cf4fd65f0616acd9cf6e89d6e296342be0169cfcfe420c8062a4",
    "uh": "ce69a5f4a70d7286831ec17ebb184af41a74a1f5f0b7f864ea0f816cce0aaaac",
    "rh": "1e2292ed4ac5ea20bc159aeb0144cc5eb1cb1e296b25c7fb84ab9cc6e2ae0c53",
    "Bh": "c6666bdac52e000d971cc47cf66901d21c3f3ae4d2c86b3040038d4dc4e1fe12"
}


def coefficient_list(items):
    require(type(items) is list, 'term list required')
    terms = {}
    for exponent, text in items:
        require(type(exponent) is list and len(exponent) == 3, 'incorrect exponent arity')
        require(all(type(v) is int and v >= 0 for v in exponent), 'invalid exponent')
        require(type(text) is str and text.isascii() and text.isdecimal(), 'positive decimal coefficient required')
        coefficient = int(text)
        require(coefficient > 0, 'nonpositive coefficient')
        key = tuple(exponent) + (0,)
        require(key not in terms, 'duplicate exponent')
        terms[key] = coefficient
    return Poly(terms)


def coefficients(case, edge):
    x, y, z, t = [Poly.variable(i) for i in range(4)]
    a, b, c = 3 + x, 3 + x + y, 3 + x + z
    removed = frozenset(CASES[case])
    labels = ['u', 'v'] + [label for label in ('r', 'j', 'k') if label in removed] + ['A', 'B', 'C', 'h']
    part = {'u': 0, 'v': 0, 'r': 0, 'A': 0, 'j': 1, 'B': 1, 'k': 2, 'C': 2, 'h': 3}
    sizes = {label: Poly(1) for label in labels}
    sizes.update(A=a-2-int('r' in removed), B=b-int('j' in removed), C=c-int('k' in removed))
    n = len(labels)
    rows = [[Poly() for _ in labels] for _ in labels]
    for i, left in enumerate(labels):
        require(all(v > 0 for v in sizes[left].terms.values()), 'negative cell size coefficient')
        # A may have size x=0 on the boundary; the proof handles its artificial zero mode.
        for j, right in enumerate(labels):
            pair = frozenset((left, right))
            adjacent = part[left] != part[right] and pair != removed
            if pair == frozenset(('u', 'v')):
                adjacent = bool(edge)
            if adjacent:
                rows[i][j] = sizes[right]
    degrees = [sum(row) for row in rows]
    for i, left in enumerate(labels):
        positive(degrees[i], f'{case}: degree {left}')
        for j, right in enumerate(labels):
            require(sizes[left] * rows[i][j] == sizes[right] * rows[j][i], 'cell balance fails')
    matrix = [[(1+t)*degrees[i] - rows[i][j] if i == j else -rows[i][j]
               for j in range(n)] for i in range(n)]
    F = determinant(matrix)
    require(F.t_coefficient(0) == 0, 'nonzero Laplacian determinant')
    first, second = [F.t_coefficient(k) for k in (1, 2)]
    positive(first, f'{case}: ratio denominator edge={edge}')
    return first, second, labels


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--certificates', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), 'use a fresh output path')
    require(set(CERTIFICATE_HASHES) == set(CASES), 'frozen certificate manifest incomplete')
    results = []
    for case in CASES:
        raw = (args.certificates / f'{case}.json').read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        require(digest == CERTIFICATE_HASHES[case], f'{case}: changed frozen certificate')
        data = json.loads(raw)
        require(data['case'] == case, 'case label mismatch')
        numerator = coefficient_list(data['negative_numerator_terms'])
        denominator = coefficient_list(data['denominator_terms'])
        positive(numerator, f'{case}: certificate negative numerator')
        positive(denominator, f'{case}: certificate denominator')
        before_first, before_second, labels = coefficients(case, 0)
        after_first, after_second, _ = coefficients(case, 1)
        raw_negative_numerator = before_second*after_first - after_second*before_first
        raw_denominator = before_first*after_first
        require(raw_negative_numerator*denominator == numerator*raw_denominator,
                f'{case}: exact rational certificate identity fails')
        results.append({
            'case': case, 'certificate_sha256': digest, 'cells': labels,
            'exact_rational_identity': True, 'positive_numerator_and_denominator': True,
            'numerator_term_count': len(numerator.terms),
            'denominator_term_count': len(denominator.terms),
            'numerator_constant': numerator.terms[ZERO],
            'denominator_constant': denominator.terms[ZERO],
        })
    result = {
        'schema_version': 'all-single-deletions-frozen-certificate-v1',
        'pass': True,
        'checker_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'arithmetic_sha256': hashlib.sha256(Path(__file__).with_name('verify_certificate.py').read_bytes()).hexdigest(),
        'method': 'subset determinants modulo t^3 and exact cross-multiplication of six rational certificates',
        'cases': results,
        'proof_boundary': 'Nine deletion orbits, B/C relabelling, zero-mode corrections including the empty A cell at a=3, and graph interpretation require the accompanying independent proof audit. Exactly one original edge deletion; no optimality, multi-failure, novelty, or practical-benefit certification.',
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes((json.dumps(result, indent=2) + '\n').encode())
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
