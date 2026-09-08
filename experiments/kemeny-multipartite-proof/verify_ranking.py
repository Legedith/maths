"""Check the rational ranking identity exactly; domain positivity is in the proof note."""
import argparse
import hashlib
import json
from pathlib import Path

from verify_certificate import Poly, require


def cleared_brace(n, a, g, H):
    x = n - a
    S0 = g - x * a
    S1 = H - x * a**2
    M = (
        -g**2 * n * (a + 2)
        + (x - 2) * a * n * (a + 2) * g
        + 2 * S1 * a * (a + 2)
        + (x - 2) * S0 * a * n * (a + 2)
        + (n - 2) * S0**2 * (a + 2)
        + 2 * (g - a) * n * g
    )
    D = 2 * a * n * (a + 2) * g
    return M, D


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), 'use a fresh output path')
    n, a, b, g, H = [Poly.variable(i) for i in range(5)]
    Mx, Dx = cleared_brace(n, a, g, H)
    My, Dy = cleared_brace(n, b, g, H)
    C = (n - 2) * (a + b + 2) - a * b
    E = 2 * (a + 2) * (b + 2) - n
    N = g * C + a * b * E
    denominator = n * a * b * (a + 2) * (b + 2)
    require(Dx * Dy == 4 * n * g**2 * denominator, 'wrong denominator clearing')
    require(Mx * Dy - My * Dx == 4 * n * g**2 * (b - a) * N, 'ranking identity fails')
    L = a**2 + b**2 - a * b + a + b + 2 * (n - 2)
    require(C - L == a * (n - a - 3) + b * (n - b - 3), 'first positivity decomposition fails')
    require(a**2 + b**2 - a * b == (a - b)**2 + a * b, 'positive quadratic identity fails')
    require(E - (2 * a * b + 3 * a + 3 * b + 8) == a + b - n, 'second positivity decomposition fails')
    result = {
        'schema_version': 'multipartite-ranking-identity-check-v1',
        'pass': True,
        'method': 'stdlib sparse integer polynomial cross multiplication',
        'checks': {
            'denominator_clearing': True,
            'rational_difference_identity': True,
            'first_positive_bracket_decomposition': True,
            'positive_quadratic_decomposition': True,
            'second_positive_bracket_decomposition': True,
        },
        'checker_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'polynomial_module_sha256': hashlib.sha256(Path(__file__).with_name('verify_certificate.py').read_bytes()).hexdigest(),
        'boundary': 'Source brace and constraints x,y>=3 for distinct parts, g>0, and tied-size handling require the accompanying mathematical proof. This check is not a novelty certificate.',
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes((json.dumps(result, indent=2) + '\n').encode())
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
