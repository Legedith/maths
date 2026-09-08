from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable


Exponent = tuple[int, int, int, int]
Polynomial = dict[Exponent, int]
ZERO_EXP: Exponent = (0, 0, 0, 0)


def clean(poly: Polynomial) -> Polynomial:
    return {exp: coefficient for exp, coefficient in poly.items() if coefficient}


def constant(value: int) -> Polynomial:
    return {} if value == 0 else {ZERO_EXP: value}


def variable(index: int) -> Polynomial:
    exp = [0, 0, 0, 0]
    exp[index] = 1
    return {tuple(exp): 1}  # type: ignore[arg-type]


def add(*polys: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for poly in polys:
        for exp, coefficient in poly.items():
            result[exp] = result.get(exp, 0) + coefficient
    return clean(result)


def neg(poly: Polynomial) -> Polynomial:
    return {exp: -coefficient for exp, coefficient in poly.items()}


def sub(left: Polynomial, right: Polynomial) -> Polynomial:
    return add(left, neg(right))


def scale(value: int, poly: Polynomial) -> Polynomial:
    return clean({exp: value * coefficient for exp, coefficient in poly.items()})


def mul(*polys: Polynomial) -> Polynomial:
    result = constant(1)
    for poly in polys:
        next_result: Polynomial = {}
        for left_exp, left_coefficient in result.items():
            for right_exp, right_coefficient in poly.items():
                exp = tuple(x + y for x, y in zip(left_exp, right_exp, strict=True))
                next_result[exp] = (
                    next_result.get(exp, 0) + left_coefficient * right_coefficient
                )
        result = clean(next_result)
    return result


def square(poly: Polynomial) -> Polynomial:
    return mul(poly, poly)


def power(poly: Polynomial, exponent: int) -> Polynomial:
    if exponent < 0:
        raise ValueError("negative polynomial exponent")
    result = constant(1)
    for _ in range(exponent):
        result = mul(result, poly)
    return result


def ap_polynomial(terms: dict[tuple[int, int], int]) -> Polynomial:
    return clean({(a_exp, 0, 0, p_exp): coefficient for (a_exp, p_exp), coefficient in terms.items()})


def load_certificate(path: Path) -> tuple[dict[str, object], Polynomial]:
    raw = path.read_bytes()
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise ValueError("certificate root must be an object")
    polynomial = parsed.get("polynomial")
    if not isinstance(polynomial, dict):
        raise ValueError("polynomial must be an object")
    terms = polynomial.get("terms")
    if not isinstance(terms, list):
        raise ValueError("polynomial.terms must be a list")
    result: Polynomial = {}
    for index, row in enumerate(terms):
        if not isinstance(row, dict):
            raise ValueError(f"term {index} must be an object")
        exponents = row.get("exponents")
        coefficient = row.get("coefficient")
        if (
            not isinstance(exponents, list)
            or len(exponents) != 4
            or any(type(value) is not int or value < 0 for value in exponents)
            or type(coefficient) is not int
        ):
            raise ValueError(f"term {index} is malformed")
        exp = tuple(exponents)
        if exp in result:
            raise ValueError(f"duplicate exponent at term {index}: {exp}")
        result[exp] = coefficient
    return parsed, result


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--certificate",
        type=Path,
        default=Path(__file__).with_name("coefficient-certificate.json"),
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    certificate, certified_q = load_certificate(args.certificate)

    A, u, v, P = (variable(index) for index in range(4))
    one = constant(1)
    two = constant(2)
    three = constant(3)

    # Independently reconstruct the selected minimum part and every quantity in
    # the sourced Theorem 3.2.3 brace after the domain-covering substitution.
    x = add(three, A)
    y = add(x, u)
    z = add(x, v)
    p = add(one, P)
    n = add(x, y, z, p)
    alpha = sub(n, x)
    gamma = sub(square(n), add(square(x), square(y), square(z), p))
    s0 = add(
        mul(y, sub(n, y)),
        mul(z, sub(n, z)),
        mul(p, sub(n, one)),
    )
    s1 = add(
        mul(y, square(sub(n, y))),
        mul(z, square(sub(n, z))),
        mul(p, square(sub(n, one))),
    )

    # If B is the brace, direct denominator clearing gives
    # D2*B=M for D2=2*alpha*n*(alpha+2)*gamma. This construction follows the
    # six summands in the displayed source formula and does not use SymPy.
    alpha_plus_two = add(alpha, two)
    m = add(
        neg(mul(gamma, n, alpha_plus_two, gamma)),
        mul(sub(x, two), alpha, n, alpha_plus_two, gamma),
        scale(2, mul(s1, alpha, alpha_plus_two)),
        mul(sub(x, two), s0, alpha, n, alpha_plus_two),
        mul(sub(n, two), square(s0), alpha_plus_two),
        scale(2, mul(sub(gamma, alpha), n, gamma)),
    )
    reconstructed_q = neg(m)

    def symmetric_uv(left_power: int, right_power: int) -> Polynomial:
        first = mul(power(u, left_power), power(v, right_power))
        if left_power == right_power:
            return first
        return add(first, mul(power(u, right_power), power(v, left_power)))

    f21 = ap_polynomial(
        {(2, 0): 62, (1, 1): 61, (1, 0): 486, (0, 2): 15, (0, 1): 238, (0, 0): 940}
    )
    f20 = ap_polynomial(
        {
            (3, 0): 84, (2, 1): 123, (2, 0): 993, (1, 2): 61,
            (1, 1): 970, (1, 0): 3861, (0, 3): 10, (0, 2): 238,
            (0, 1): 1881, (0, 0): 4947,
        }
    )
    f11 = ap_polynomial(
        {
            (3, 0): 76, (2, 1): 115, (2, 0): 947, (1, 2): 60,
            (1, 1): 953, (1, 0): 3833, (0, 3): 10, (0, 2): 240,
            (0, 1): 1908, (0, 0): 5062,
        }
    )
    f10 = ap_polynomial(
        {
            (4, 0): 64, (3, 1): 132, (3, 0): 1138,
            (2, 2): 110, (2, 1): 1760, (2, 0): 7248,
            (1, 3): 40, (1, 2): 937, (1, 1): 7409, (1, 0): 19850,
            (0, 4): 5, (0, 3): 160, (0, 2): 1899, (0, 1): 10005,
            (0, 0): 19871,
        }
    )
    f00 = ap_polynomial(
        {
            (5, 0): 12, (4, 1): 36, (4, 0): 372,
            (3, 2): 52, (3, 1): 850, (3, 0): 3750,
            (2, 3): 35, (2, 2): 789, (2, 1): 6217, (2, 0): 17127,
            (1, 4): 10, (1, 3): 307, (1, 2): 3531,
            (1, 1): 18387, (1, 0): 36861,
            (0, 5): 1, (0, 4): 40, (0, 3): 630, (0, 2): 4918,
            (0, 1): 19249, (0, 0): 30474,
        }
    )
    grouped_q = add(
        scale(6, symmetric_uv(4, 1)),
        mul(scale(6, add(scale(2, A), P, constant(7))), symmetric_uv(4, 0)),
        scale(18, symmetric_uv(3, 2)),
        mul(scale(4, add(scale(19, A), scale(9, P), constant(70))), symmetric_uv(3, 1)),
        mul(
            scale(2, mul(add(scale(2, A), P, constant(7)), add(scale(20, A), scale(9, P), constant(77)))),
            symmetric_uv(3, 0),
        ),
        mul(scale(12, add(scale(10, A), scale(5, P), constant(39))), symmetric_uv(2, 2)),
        mul(scale(4, f21), symmetric_uv(2, 1)),
        mul(scale(2, f20), symmetric_uv(2, 0)),
        mul(scale(4, f11), symmetric_uv(1, 1)),
        mul(scale(2, f10), symmetric_uv(1, 0)),
        scale(2, f00),
    )

    gamma_positive_form = add(
        scale(2, mul(x, y)),
        scale(2, mul(x, z)),
        scale(2, mul(y, z)),
        scale(2, mul(p, add(x, y, z))),
        mul(p, sub(p, one)),
    )
    checks = {
        "schema": certificate.get("schema_version")
        == "kemeny-three-part-positive-coefficients-v1",
        "variable_order": certificate.get("polynomial", {}).get("variable_order")
        == ["A", "u", "v", "P"],
        "gamma_identity": gamma == gamma_positive_form,
        "coefficient_identity": certified_q == reconstructed_q,
        "grouped_display_identity": grouped_q == reconstructed_q,
        "all_coefficients_strictly_positive": bool(certified_q)
        and all(value > 0 for value in certified_q.values()),
        "term_count": len(certified_q)
        == certificate.get("polynomial", {}).get("term_count")
        == 124,
        "constant_strictness": certified_q.get(ZERO_EXP, 0)
        == certificate.get("polynomial", {}).get("constant_coefficient")
        and certified_q.get(ZERO_EXP, 0) > 0,
        "reported_extrema": min(certified_q.values())
        == certificate.get("polynomial", {}).get("minimum_coefficient")
        and max(certified_q.values())
        == certificate.get("polynomial", {}).get("maximum_coefficient"),
    }
    result: dict[str, object] = {
        "schema_version": "kemeny-three-part-certificate-check-v1",
        "certificate": {
            "path": str(args.certificate.resolve()),
            "sha256": sha256(args.certificate),
        },
        "method": "stdlib sparse integer polynomial reconstruction",
        "domain_coverage": {
            "given": "integers p>=1 and x=min(a,b,c)>=3",
            "substitution": "A=x-3, u=y-x, v=z-x, P=p-1",
            "inverse": "x=3+A, y=x+u, z=x+v, p=1+P",
            "all_new_variables_nonnegative": True,
        },
        "denominator_sign": {
            "D2": "2*alpha*n*(alpha+2)*gamma",
            "alpha": "y+z+p >= 7",
            "n": "x+y+z+p >= 10",
            "alpha_plus_two": "alpha+2 >= 9",
            "gamma": "2xy+2xz+2yz+2p(x+y+z)+p(p-1) > 0",
            "positive": True,
        },
        "checks": checks,
        "pass": all(checks.values()),
        "conclusion": (
            "D2*B=-Q<0, so B<0 and Delta=2*B/(gamma+2)<0 for an edge "
            "inside a smallest non-singleton part."
        ),
    }
    encoded = (json.dumps(result, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("utf-8")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(encoded)
    print(encoded.decode("utf-8"), end="")
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
