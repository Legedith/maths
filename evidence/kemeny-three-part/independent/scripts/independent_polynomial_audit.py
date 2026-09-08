"""Independent exact audit of the selected three-part Kemeny certificate.

This implementation was written from Theorem 3.2.3 as displayed in the pinned
Hu--Kirkland manuscript.  It uses only Python's standard library and does not
import or execute the selected author's checker.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Iterable, Mapping


NVAR = 4
ZERO_EXP = (0, 0, 0, 0)
VARIABLE_ORDER = ("A", "u", "v", "P")


def is_exact_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


@dataclass(frozen=True)
class Poly:
    coefficients: Mapping[tuple[int, int, int, int], int]

    def __post_init__(self) -> None:
        normalized: dict[tuple[int, int, int, int], int] = {}
        for exponent, coefficient in self.coefficients.items():
            if len(exponent) != NVAR or any(not is_exact_int(e) or e < 0 for e in exponent):
                raise TypeError(f"invalid exponent {exponent!r}")
            if not is_exact_int(coefficient):
                raise TypeError(f"invalid coefficient {coefficient!r}")
            if coefficient:
                normalized[tuple(exponent)] = coefficient
        object.__setattr__(self, "coefficients", normalized)

    @staticmethod
    def constant(value: int) -> "Poly":
        if not is_exact_int(value):
            raise TypeError("polynomial constants must be exact integers")
        return Poly({ZERO_EXP: value})

    @staticmethod
    def variable(index: int) -> "Poly":
        exponent = [0] * NVAR
        exponent[index] = 1
        return Poly({tuple(exponent): 1})

    @staticmethod
    def monomial(coefficient: int, exponent: tuple[int, int, int, int]) -> "Poly":
        return Poly({exponent: coefficient})

    def __add__(self, other: object) -> "Poly":
        right = as_poly(other)
        answer = dict(self.coefficients)
        for exponent, coefficient in right.coefficients.items():
            answer[exponent] = answer.get(exponent, 0) + coefficient
            if answer[exponent] == 0:
                del answer[exponent]
        return Poly(answer)

    def __radd__(self, other: object) -> "Poly":
        return self + other

    def __neg__(self) -> "Poly":
        return Poly({exponent: -coefficient for exponent, coefficient in self.coefficients.items()})

    def __sub__(self, other: object) -> "Poly":
        return self + (-as_poly(other))

    def __rsub__(self, other: object) -> "Poly":
        return as_poly(other) - self

    def __mul__(self, other: object) -> "Poly":
        right = as_poly(other)
        answer: dict[tuple[int, int, int, int], int] = {}
        for left_exp, left_coeff in self.coefficients.items():
            for right_exp, right_coeff in right.coefficients.items():
                exponent = tuple(a + b for a, b in zip(left_exp, right_exp, strict=True))
                answer[exponent] = answer.get(exponent, 0) + left_coeff * right_coeff
        return Poly(answer)

    def __rmul__(self, other: object) -> "Poly":
        return self * other

    def __pow__(self, power: int) -> "Poly":
        if not is_exact_int(power) or power < 0:
            raise ValueError("polynomial powers must be nonnegative integers")
        base = self
        answer = Poly.constant(1)
        remaining = power
        while remaining:
            if remaining & 1:
                answer = answer * base
            base = base * base
            remaining >>= 1
        return answer

    def evaluate(self, values: tuple[int, int, int, int]) -> int:
        if len(values) != NVAR or any(not is_exact_int(value) for value in values):
            raise TypeError("evaluation requires four exact integers")
        return sum(
            coefficient
            * values[0] ** exponent[0]
            * values[1] ** exponent[1]
            * values[2] ** exponent[2]
            * values[3] ** exponent[3]
            for exponent, coefficient in self.coefficients.items()
        )


def as_poly(value: object) -> Poly:
    if isinstance(value, Poly):
        return value
    if is_exact_int(value):
        return Poly.constant(value)
    return NotImplemented


def monomial(coefficient: int, a: int = 0, u: int = 0, v: int = 0, p: int = 0) -> Poly:
    return Poly.monomial(coefficient, (a, u, v, p))


def sum_poly(items: Iterable[Poly]) -> Poly:
    answer = Poly.constant(0)
    for item in items:
        answer = answer + item
    return answer


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def symmetric_pair(u: Poly, v: Poly, i: int, j: int) -> Poly:
    require(i >= j >= 0, "symmetric-pair indices must satisfy i >= j >= 0")
    if i == j:
        return u**i * v**j
    return u**i * v**j + u**j * v**i


def candidate_grouped_polynomial(A: Poly, u: Poly, v: Poly, P: Poly) -> Poly:
    """Expand the eleven displayed groups in the selected proposal."""

    f21 = (
        62 * A**2 + 61 * A * P + 486 * A + 15 * P**2 + 238 * P + 940
    )
    f20 = (
        84 * A**3 + 123 * A**2 * P + 993 * A**2 + 61 * A * P**2
        + 970 * A * P + 3861 * A + 10 * P**3 + 238 * P**2
        + 1881 * P + 4947
    )
    f11 = (
        76 * A**3 + 115 * A**2 * P + 947 * A**2 + 60 * A * P**2
        + 953 * A * P + 3833 * A + 10 * P**3 + 240 * P**2
        + 1908 * P + 5062
    )
    f10 = (
        64 * A**4 + 132 * A**3 * P + 1138 * A**3 + 110 * A**2 * P**2
        + 1760 * A**2 * P + 7248 * A**2 + 40 * A * P**3
        + 937 * A * P**2 + 7409 * A * P + 19850 * A + 5 * P**4
        + 160 * P**3 + 1899 * P**2 + 10005 * P + 19871
    )
    f00 = (
        12 * A**5 + 36 * A**4 * P + 372 * A**4 + 52 * A**3 * P**2
        + 850 * A**3 * P + 3750 * A**3 + 35 * A**2 * P**3
        + 789 * A**2 * P**2 + 6217 * A**2 * P + 17127 * A**2
        + 10 * A * P**4 + 307 * A * P**3 + 3531 * A * P**2
        + 18387 * A * P + 36861 * A + P**5 + 40 * P**4
        + 630 * P**3 + 4918 * P**2 + 19249 * P + 30474
    )

    s = lambda i, j: symmetric_pair(u, v, i, j)
    return (
        6 * s(4, 1)
        + 6 * (2 * A + P + 7) * s(4, 0)
        + 18 * s(3, 2)
        + 4 * (19 * A + 9 * P + 70) * s(3, 1)
        + 2 * (2 * A + P + 7) * (20 * A + 9 * P + 77) * s(3, 0)
        + 12 * (10 * A + 5 * P + 39) * s(2, 2)
        + 4 * f21 * s(2, 1)
        + 2 * f20 * s(2, 0)
        + 4 * f11 * s(1, 1)
        + 2 * f10 * s(1, 0)
        + 2 * f00
    )


def parse_certificate(path: Path) -> tuple[dict, dict[tuple[int, int, int, int], int]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), "certificate root must be an object")
    require(
        set(data) == {"schema_version", "source_formula", "target", "domain_substitution", "polynomial"},
        "certificate top-level fields are malformed",
    )
    require(data["schema_version"] == "kemeny-three-part-positive-coefficients-v1", "wrong schema")

    expected_source = {
        "locator": "PDF page 12, Theorem 3.2.3, Case 1",
        "pdf_sha256": "c896d263c6bec602274f84a29c30492f99e85e3bde654f3e61dcf5aa10718c77",
        "work": "Hu and Kirkland (2019), Complete multipartite graphs and Braess edges",
    }
    require(data["source_formula"] == expected_source, "source metadata differs from the pinned source")
    expected_target = {
        "brace": "The expression inside the positive factor 2/(gamma+2)",
        "denominator": "D2=2*alpha*n*(alpha+2)*gamma",
        "identity": "D2*brace=-Q(A,u,v,P)",
    }
    require(data["target"] == expected_target, "target metadata is malformed")
    expected_domain = {
        "constraints": "A,u,v,P are nonnegative integers",
        "other_non_singleton_parts": ["y=x+u", "z=x+v"],
        "selected_part": "x=3+A",
        "singleton_count": "p=1+P",
        "variables": ["A", "u", "v", "P"],
    }
    require(data["domain_substitution"] == expected_domain, "domain substitution metadata is malformed")

    polynomial = data["polynomial"]
    require(isinstance(polynomial, dict), "polynomial must be an object")
    require(
        set(polynomial)
        == {"constant_coefficient", "maximum_coefficient", "minimum_coefficient", "term_count", "term_order", "terms", "variable_order"},
        "polynomial metadata fields are malformed",
    )
    require(polynomial["variable_order"] == list(VARIABLE_ORDER), "wrong variable order")
    require(polynomial["term_order"] == "SymPy lexicographic descending monomials", "wrong term-order label")
    require(isinstance(polynomial["terms"], list), "terms must be an array")

    coefficients: dict[tuple[int, int, int, int], int] = {}
    previous: tuple[int, int, int, int] | None = None
    for index, term in enumerate(polynomial["terms"]):
        require(isinstance(term, dict) and set(term) == {"coefficient", "exponents"}, f"malformed term {index}")
        coefficient = term["coefficient"]
        exponents = term["exponents"]
        require(is_exact_int(coefficient), f"term {index} coefficient is not an exact integer")
        require(
            isinstance(exponents, list)
            and len(exponents) == NVAR
            and all(is_exact_int(e) and e >= 0 for e in exponents),
            f"term {index} exponent vector is malformed",
        )
        exponent = tuple(exponents)
        require(exponent not in coefficients, f"duplicate monomial at term {index}")
        if previous is not None:
            require(previous > exponent, f"terms are not in strict descending lexicographic order at {index}")
        previous = exponent
        coefficients[exponent] = coefficient

    for field in ("constant_coefficient", "maximum_coefficient", "minimum_coefficient", "term_count"):
        require(is_exact_int(polynomial[field]), f"{field} must be an exact integer")
    return data, coefficients


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--source-pdf", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-certificate-sha256", required=True)
    parser.add_argument("--expected-source-pdf-sha256", required=True)
    args = parser.parse_args()

    certificate = args.certificate.resolve(strict=True)
    source_pdf = args.source_pdf.resolve(strict=True)
    certificate_hash = sha256_file(certificate)
    source_hash = sha256_file(source_pdf)
    require(certificate_hash == args.expected_certificate_sha256, "certificate byte hash mismatch")
    require(source_hash == args.expected_source_pdf_sha256, "source PDF byte hash mismatch")

    A, u, v, P = (Poly.variable(index) for index in range(NVAR))
    x = 3 + A
    y = x + u
    z = x + v
    p = 1 + P
    n = x + y + z + p
    alpha = n - x

    # Directly reconstruct gamma and the j>=2 source sums.  The weight p
    # represents the p distinct singleton parts, each with k_j=1.
    other_parts = ((y, n - y), (z, n - z), (p, n - 1))
    gamma = x * (n - x) + sum_poly(weight * part_alpha for weight, part_alpha in other_parts)
    s0 = sum_poly(weight * part_alpha for weight, part_alpha in other_parts)
    s1 = sum_poly(weight * part_alpha**2 for weight, part_alpha in other_parts)
    require(s0 == gamma - x * alpha, "singleton-inclusive S0 identity failed")

    D = 2 * alpha * n * (alpha + 2) * gamma

    # Six rational terms after distributing Theorem 3.2.3's outer 1/gamma.
    source_terms = (
        (-gamma, 2 * alpha),
        ((x - 2) * gamma, 2 * gamma),
        (s1, gamma * n),
        ((x - 2) * s0, 2 * gamma),
        ((n - 2) * s0 * (gamma - x * alpha), 2 * gamma * n * alpha),
        (gamma - alpha, alpha * (alpha + 2)),
    )
    complements = (
        n * (alpha + 2) * gamma,
        alpha * n * (alpha + 2),
        2 * alpha * (alpha + 2),
        alpha * n * (alpha + 2),
        alpha + 2,
        2 * n * gamma,
    )
    for index, ((_, denominator), complement) in enumerate(zip(source_terms, complements, strict=True), start=1):
        require(denominator * complement == D, f"clearing complement {index} is wrong")
    m_direct = sum_poly(numerator * complement for (numerator, _), complement in zip(source_terms, complements, strict=True))

    m_grouped_terms = (
        -gamma * n * (alpha + 2) * gamma,
        (x - 2) * alpha * n * (alpha + 2) * gamma,
        2 * s1 * alpha * (alpha + 2),
        (x - 2) * s0 * alpha * n * (alpha + 2),
        (n - 2) * s0**2 * (alpha + 2),
        2 * (gamma - alpha) * n * gamma,
    )
    M = sum_poly(m_grouped_terms)
    require(m_direct == M, "direct source clearing and six-term M disagree")
    Q = -M

    data, certificate_coefficients = parse_certificate(certificate)
    require(Q.coefficients == certificate_coefficients, "certificate polynomial does not equal independently reconstructed -M")
    grouped_Q = candidate_grouped_polynomial(A, u, v, P)
    require(grouped_Q == Q, "the eleven-group display does not expand to independently reconstructed -M")

    computed_coefficients = list(Q.coefficients.values())
    require(computed_coefficients, "Q unexpectedly has no terms")
    term_count = len(computed_coefficients)
    minimum = min(computed_coefficients)
    maximum = max(computed_coefficients)
    constant = Q.coefficients.get(ZERO_EXP, 0)
    require(all(coefficient > 0 for coefficient in computed_coefficients), "Q has a nonpositive coefficient")
    require(term_count == data["polynomial"]["term_count"] == 124, "term-count metadata mismatch")
    require(minimum == data["polynomial"]["minimum_coefficient"] == 2, "minimum-coefficient metadata mismatch")
    require(maximum == data["polynomial"]["maximum_coefficient"] == 73722, "maximum-coefficient metadata mismatch")
    require(constant == data["polynomial"]["constant_coefficient"] == 60948, "constant-coefficient metadata mismatch")

    # Diagnostics exercise both substitution directions and the u/v symmetry.
    diagnostic_points = ((0, 0, 0, 0), (0, 2, 5, 0), (3, 0, 0, 4), (5, 7, 1, 8))
    diagnostics = []
    for point in diagnostic_points:
        swapped = (point[0], point[2], point[1], point[3])
        q_value = Q.evaluate(point)
        require(q_value == grouped_Q.evaluate(point), f"grouped diagnostic mismatch at {point}")
        require(q_value == Q.evaluate(swapped), f"u/v symmetry failed at {point}")
        require(q_value >= constant > 0, f"strict positivity diagnostic failed at {point}")
        diagnostics.append({"A_u_v_P": list(point), "Q": q_value})

    output = {
        "schema_version": "independent-kemeny-polynomial-audit-v1",
        "status": "PASS",
        "inputs": {
            "certificate": {"path": str(certificate), "sha256": certificate_hash},
            "source_pdf": {"path": str(source_pdf), "sha256": source_hash},
        },
        "source_reconstruction": {
            "total_parts": "R=3+p",
            "singleton_aggregation": "p copies of (k_j,alpha_j)=(1,n-1)",
            "six_rational_terms": len(source_terms),
            "all_clearing_complements_exact": True,
            "direct_and_grouped_M_identical": True,
        },
        "polynomial": {
            "identity": "2*alpha*n*(alpha+2)*gamma*B = M = -Q",
            "variable_order": list(VARIABLE_ORDER),
            "term_count": term_count,
            "minimum_coefficient": minimum,
            "maximum_coefficient": maximum,
            "constant_coefficient": constant,
            "all_coefficients_strictly_positive": True,
            "certificate_exact_match": True,
            "eleven_group_display_exact_match": True,
        },
        "domain": {
            "forward": "x=3+A, y=x+u, z=x+v, p=1+P for A,u,v,P>=0",
            "inverse": "A=x-3, u=y-x, v=z-x, P=p-1 for x>=3, y,z>=x, p>=1",
            "covers_every_relabelled_minimum_part": True,
        },
        "strictness": {
            "reason": "Q is a positive-coefficient polynomial in nonnegative variables",
            "uniform_lower_bound_for_Q": constant,
        },
        "diagnostics_only": diagnostics,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
