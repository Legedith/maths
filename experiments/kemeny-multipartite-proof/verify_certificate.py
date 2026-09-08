"""Exact arithmetic for one frozen proof; see PROOF.md for its source/domain bridge."""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path


VARIABLES = ('A', 'R', 'P', 'u1', 'u2', 'u3', 'u4', 'u5')
ZERO = (0,) * len(VARIABLES)
CERTIFICATE_SHA256 = 'b264e53aa98bb9171fcb327cb82cd01ec31e4c67eecbf30af6752545c078804c'


class Poly:
    def __init__(self, value=0):
        self.terms = ({ZERO: value} if value else {}) if isinstance(value, int) else {
            exponent: coefficient for exponent, coefficient in value.items() if coefficient
        }

    @staticmethod
    def coerce(value):
        return value if isinstance(value, Poly) else Poly(value)

    @staticmethod
    def variable(index):
        exponent = tuple(int(i == index) for i in range(len(VARIABLES)))
        return Poly({exponent: 1})

    def __add__(self, other):
        result = dict(self.terms)
        for exponent, coefficient in self.coerce(other).terms.items():
            result[exponent] = result.get(exponent, 0) + coefficient
        return Poly(result)

    __radd__ = __add__

    def __neg__(self):
        return Poly({exponent: -coefficient for exponent, coefficient in self.terms.items()})

    def __sub__(self, other):
        return self + -self.coerce(other)

    def __rsub__(self, other):
        return self.coerce(other) + -self

    def __mul__(self, other):
        result = defaultdict(int)
        for left, a in self.terms.items():
            for right, b in self.coerce(other).terms.items():
                exponent = tuple(x + y for x, y in zip(left, right, strict=True))
                result[exponent] += a * b
        return Poly(result)

    __rmul__ = __mul__

    def __pow__(self, exponent):
        if type(exponent) is not int or exponent < 0:
            raise ValueError('polynomial power must be a nonnegative integer')
        result = Poly(1)
        for _ in range(exponent):
            result = result * self
        return result

    def __eq__(self, other):
        return self.terms == self.coerce(other).terms


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_certificate(path):
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    require(digest == CERTIFICATE_SHA256, 'certificate differs from the accepted frozen input')
    data = json.loads(raw)
    require(type(data) is dict and set(data) == {'variables', 'terms'}, 'unexpected certificate fields')
    require(data['variables'] == list(VARIABLES), 'incorrect variable order')
    require(type(data['terms']) is list, 'terms must be a list')
    terms = {}
    for item in data['terms']:
        require(type(item) is list and len(item) == 2, 'each term needs an exponent and coefficient')
        exponent, coefficient = item
        require(type(exponent) is list and len(exponent) == len(VARIABLES), 'incorrect exponent arity')
        require(all(type(v) is int and v >= 0 for v in exponent), 'exponents must be nonnegative integers')
        require(type(coefficient) is int and coefficient > 0, 'coefficients must be positive integers')
        key = tuple(exponent)
        require(key not in terms, 'duplicate exponent')
        terms[key] = coefficient
    return Poly(terms), digest


def reconstruct():
    A, R, P, *gaps = [Poly.variable(i) for i in range(len(VARIABLES))]
    x, k, p = 3 + A, 2 + R, 1 + P
    U = sum(gaps)
    V = sum(gap**2 for gap in gaps)
    W = sum(gap**3 for gap in gaps)

    # Moments of OTHER parts: k nonsingletons x+u_i and p singletons.
    other_first = k * x + U + p
    other_second = k * x**2 + 2 * x * U + V + p
    other_third = k * x**3 + 3 * x**2 * U + 3 * x * V + W + p
    n, alpha = x + other_first, other_first
    S0 = n * other_first - other_second
    S1 = n**2 * other_first - 2 * n * other_second + other_third
    gamma = x * alpha + S0

    # Each numerator/denominator is one term in the sourced brace B.
    source_terms = (
        (-gamma, 2 * alpha),
        (x - 2, Poly(2)),
        (S1, gamma * n),
        ((x - 2) * S0, 2 * gamma),
        ((n - 2) * S0**2, 2 * gamma * n * alpha),
        (gamma - alpha, alpha * (alpha + 2)),
    )
    D = 2 * alpha * n * (alpha + 2) * gamma
    complements = (
        n * (alpha + 2) * gamma,
        alpha * n * (alpha + 2) * gamma,
        2 * alpha * (alpha + 2),
        alpha * n * (alpha + 2),
        alpha + 2,
        2 * n * gamma,
    )
    for index, ((_, denominator), complement) in enumerate(zip(source_terms, complements, strict=True), 1):
        require(denominator * complement == D, f'incorrect denominator complement {index}')
    Q = -sum(numerator * complement for (numerator, _), complement in zip(source_terms, complements, strict=True))

    # The expanded denominators are positive on A,R,P,u_i>=0.
    for name, factor in (('n', n), ('alpha', alpha), ('alpha+2', alpha + 2), ('gamma', gamma)):
        require(factor.terms.get(ZERO, 0) > 0, f'{name} has no positive constant')
        require(all(v > 0 for v in factor.terms.values()), f'{name} has a negative coefficient')

    # Adjacent transpositions generate all permutations of the five gaps.
    for left in range(3, 7):
        swapped = {}
        for exponent, coefficient in Q.terms.items():
            values = list(exponent)
            values[left], values[left + 1] = values[left + 1], values[left]
            swapped[tuple(values)] = coefficient
        require(swapped == Q.terms, f'gap symmetry fails at {left}')
    require(max(sum(exponent[3:]) for exponent in Q.terms) <= 5, 'gap degree exceeds five')
    return Q


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--certificate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), 'use a fresh output path; previous evidence is retained')
    certificate, digest = read_certificate(args.certificate)
    computed = reconstruct()
    require(computed == certificate, 'frozen certificate does not equal independently reconstructed -D*B')
    require(all(coefficient > 0 for coefficient in computed.terms.values()), 'Q has a nonpositive coefficient')
    require(computed.terms.get(ZERO, 0) > 0, 'Q lacks a strictly positive constant')
    partitions = {tuple(sorted((v for v in exponent[3:] if v), reverse=True)) for exponent in computed.terms}
    result = {
        'schema_version': 'multipartite-frozen-polynomial-check-v1',
        'pass': True,
        'certificate_sha256': digest,
        'checker_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'method': 'stdlib sparse integer polynomial reconstruction from six sourced rational terms',
        'term_count': len(computed.terms),
        'gap_partition_count': len(partitions),
        'max_gap_degree': max(sum(exponent[3:]) for exponent in computed.terms),
        'constant_coefficient': computed.terms[ZERO],
        'checks': {
            'frozen_input_identity': True,
            'exact_coefficient_identity': True,
            'six_denominator_complements': True,
            'positive_denominator_factors': True,
            'positive_coefficients_and_constant': True,
            'gap_permutation_symmetry': True,
            'gap_degree_at_most_five': True,
        },
        'proof_boundary': 'The source transcription, full-domain substitutions, finite-support lemma for arbitrary gap counts, and vertex relabelling require the accompanying mathematical proof and independent audit. This is not Lean formalization or novelty certification.',
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes((json.dumps(result, indent=2) + '\n').encode())
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
