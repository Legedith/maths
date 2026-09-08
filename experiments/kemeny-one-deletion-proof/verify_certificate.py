"""Exact six-cell determinant check for one frozen edge-deletion theorem."""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path


ZERO = (0, 0, 0, 0)  # x, y, z, t; arithmetic is modulo t**3.
CERTIFICATE_SHA256 = 'a5a096223ad9fdd3744a08d5fcfbd9643a5090431eadd501d13ead449cab2940'


def require(condition, message):
    if not condition:
        raise ValueError(message)


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
        return Poly({tuple(int(i == index) for i in range(4)): 1})

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
                if left[3] + right[3] <= 2:
                    result[tuple(x + y for x, y in zip(left, right, strict=True))] += a * b
        return Poly(result)

    __rmul__ = __mul__

    def __eq__(self, other):
        return self.terms == self.coerce(other).terms

    def t_coefficient(self, degree):
        return Poly({exponent[:3] + (0,): coefficient
                     for exponent, coefficient in self.terms.items() if exponent[3] == degree})


def determinant(matrix):
    """Leibniz determinant grouped by used columns, in Z[x,y,z,t]/(t**3)."""
    n = len(matrix)
    partial = {0: Poly(1)}
    for mask in range(1 << n):
        row = mask.bit_count()
        if row == n:
            continue
        for column in range(n):
            if mask & (1 << column):
                continue
            # New inversions are previously used columns greater than column.
            sign = -1 if (mask >> (column + 1)).bit_count() % 2 else 1
            next_mask = mask | (1 << column)
            partial[next_mask] = partial.get(next_mask, Poly()) + sign * partial[mask] * matrix[row][column]
    return partial[(1 << n) - 1]


def positive(poly, name):
    require(poly.terms.get(ZERO, 0) > 0, f'{name} has no positive constant')
    require(all(c > 0 for c in poly.terms.values()), f'{name} has a nonpositive coefficient')


def quotient_coefficients(edge):
    x, y, z, t = [Poly.variable(i) for i in range(4)]
    a, b, c = 3 + x, 3 + x + y, 3 + x + z
    sizes = [Poly(1), Poly(1), a - 2, b, c, Poly(1)]
    # {u}, {v}, A-rest, B, C, {h}; uh is absent in both graphs.
    rows = [
        [0, edge, 0, b, c, 0],
        [edge, 0, 0, b, c, 1],
        [0, 0, 0, b, c, 1],
        [1, 1, a - 2, 0, c, 1],
        [1, 1, a - 2, b, 0, 1],
        [0, 1, a - 2, b, c, 0],
    ]
    R = [[Poly.coerce(value) for value in row] for row in rows]
    degrees = [sum(row) for row in R]
    for i in range(6):
        positive(sizes[i], f'cell size {i}')
        positive(degrees[i], f'degree {i}')
        for j in range(6):
            require(sizes[i] * R[i][j] == sizes[j] * R[j][i], 'undirected cell balance fails')
    matrix = [[(1 + t) * degrees[i] - R[i][j] if i == j else -R[i][j]
               for j in range(6)] for i in range(6)]
    polynomial = determinant(matrix)
    require(polynomial.t_coefficient(0) == 0, 'Laplacian determinant constant must vanish')
    first, second = [polynomial.t_coefficient(i) for i in (1, 2)]
    positive(first, f't coefficient for edge={edge}')
    return first, second


def read_certificate(path):
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    require(digest == CERTIFICATE_SHA256, 'certificate differs from frozen proof input')
    # Polynomial-expression strings are historical author data: never evaluated.
    items = json.loads(raw)['negative_N_shift_terms']
    require(type(items) is list, 'term list required')
    terms = {}
    for exponent, text in items:
        require(type(exponent) is list and len(exponent) == 3, 'incorrect exponent arity')
        require(all(type(v) is int and v >= 0 for v in exponent), 'invalid exponent')
        require(type(text) is str and text.isascii() and text.isdecimal(), 'positive integer coefficient required')
        coefficient = int(text)
        require(coefficient > 0, 'nonpositive coefficient')
        key = tuple(exponent) + (0,)
        require(key not in terms, 'duplicate exponent')
        terms[key] = coefficient
    return Poly(terms), digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--certificate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), 'use a fresh output path to retain prior evidence')
    certificate, digest = read_certificate(args.certificate)
    before_first, before_second = quotient_coefficients(0)
    after_first, after_second = quotient_coefficients(1)
    negative_numerator = before_second * after_first - after_second * before_first
    require(negative_numerator == certificate, 'full determinant coefficient identity fails')
    positive(negative_numerator, 'negative numerator')
    result = {
        'schema_version': 'one-deletion-frozen-certificate-v1',
        'pass': True,
        'certificate_sha256': digest,
        'checker_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'method': 'integer subset determinant in Z[x,y,z,t]/(t^3), retaining coefficients of t and t^2',
        'term_count': len(negative_numerator.terms),
        'minimum_coefficient': min(negative_numerator.terms.values()),
        'constant_coefficient': negative_numerator.terms[ZERO],
        'total_degree': max(sum(exponent) for exponent in negative_numerator.terms),
        'checks': {
            'frozen_input_identity': True,
            'positive_cell_sizes_and_degrees': True,
            'undirected_cell_balance': True,
            'zero_laplacian_determinants': True,
            'positive_ratio_denominators': True,
            'full_negative_numerator_identity': True,
            'strict_coefficient_positivity': True,
        },
        'proof_boundary': 'The graph-to-quotient spectral reduction, coefficient-ratio interpretation, domain substitution, and vertex relabelling require the accompanying proof and independent audit. This checks only deletion of uh and addition of uv. No Lean formalization, global novelty, or practical benefit is certified.',
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes((json.dumps(result, indent=2) + '\n').encode())
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
