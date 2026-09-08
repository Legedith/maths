"""Exact fixed-uniform workload ranking and comparison with no insertion."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from verify_certificate import Poly, ZERO, positive, require
from verify_all_deletions import coefficient_list


RANKING_SHA256 = 'f0f6c30dfef0bc7836b5bc6feeb1999968d9a81a89330aa59c70a1b1cab9517c'
NOOP_SHA256 = 'daa02c1a3656829def24a7e81abe69d55afe77e7ffa97a7311a788c1893d280f'


def graph_expressions(a, b, c):
    """Numerator/denominator pairs derived in the audited electrical proof."""
    n = a+b+c+1
    da, db, dc = n-a, n-b, n-c
    k0 = (n-1)*(da-1)  # deletion denominator k=k0/(n*da)
    w0 = n*(n-1)+da*(da-1)  # ||L_G^+ y||^2=w0/(n^2*da^2)
    for name, value in [('n', n), ('dA', da), ('dB', db), ('dC', dc), ('k0', k0)]:
        positive(value, name)
    scores = {
        'restore': (w0, n*da*k0),
        'uv': (2*k0*k0+2*n*k0+w0, da*k0*((da+2)*k0+n)),
        'untouched_A': (Poly(2), da*(da+2)),
        'B': (Poly(2), db*(db+2)),
        'C': (Poly(2), dc*(dc+2)),
    }
    trace_den = n*da*db*dc*k0
    trace_num = (3*da*db*dc*k0+(a-1)*n*db*dc*k0
                 +(b-1)*n*da*dc*k0+(c-1)*n*da*db*k0+w0*db*dc)
    m = a*b+a*c+b*c+a+b+c-1
    positive(m, 'damaged graph edge count')
    for name, (num, den) in scores.items():
        positive(num, name+' score numerator')
        positive(den, name+' score denominator')
    positive(trace_num, 'damaged graph trace numerator')
    positive(trace_den, 'damaged graph trace denominator')
    return scores, (trace_num, trace_den), m


def difference(left, right):
    an, ad = left
    bn, bd = right
    return an*bd-bn*ad, ad*bd


def verify_ratio(name, actual, certificate, substitution):
    num = coefficient_list(certificate['numerator_terms'])
    den = coefficient_list(certificate['denominator_terms'])
    positive(num, name+' certificate numerator')
    positive(den, name+' certificate denominator')
    raw_num, raw_den = actual
    positive(raw_den, name+' reconstructed denominator')
    require(raw_num*den == num*raw_den, name+': exact polynomial identity fails')
    return {
        'comparison': name, 'substitution': substitution,
        'exact_rational_identity': True,
        'positive_numerator_and_denominator': True,
        'positive_reconstruction_denominator': True,
        'numerator_term_count': len(num.terms),
        'minimum_numerator_coefficient': min(num.terms.values()),
        'numerator_constant': num.terms[ZERO],
        'denominator_constant': den.terms[ZERO],
    }


def read_pinned(path, expected):
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    require(digest == expected, 'changed frozen uniform certificate: '+path.name)
    return json.loads(raw), digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ranking-certificate', type=Path, required=True)
    parser.add_argument('--noop-certificate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), 'use a fresh output path')
    ranking, rank_hash = read_pinned(args.ranking_certificate, RANKING_SHA256)
    noop, noop_hash = read_pinned(args.noop_certificate, NOOP_SHA256)
    require(set(ranking['comparisons']) == {'uv_minus_restore', 'uv_minus_untouchedA', 'larger_B_minus_uv'},
            'incorrect ranking comparison set')
    require(set(noop['comparisons']) == {'equal', 'one_larger', 'both_larger'},
            'incorrect no-op comparison set')
    x, y, z = [Poly.variable(i) for i in range(3)]
    results = []
    for name, left, right, sizes, substitution in [
        ('uv_minus_restore', 'uv', 'restore', (3+x, 3+x+y, 3+x+z), 'a=3+x,b=3+x+y,c=3+x+z'),
        ('uv_minus_untouchedA', 'uv', 'untouched_A', (3+x, 3+x+y, 3+x+z), 'a=3+x,b=3+x+y,c=3+x+z'),
        ('larger_B_minus_uv', 'B', 'uv', (3+x, 4+x+y, 3+x+z), 'a=3+x,b=4+x+y,c=3+x+z'),
    ]:
        scores, _, _ = graph_expressions(*sizes)
        results.append(verify_ratio(name, difference(scores[left], scores[right]),
                                    ranking['comparisons'][name], substitution))
    for name, best, sizes, substitution in [
        ('equal', 'uv', (3+x, 3+x, 3+x), 'a=b=c=3+x'),
        ('one_larger', 'B', (3+x, 4+x+y, 3+x), 'a=c=3+x,b=4+x+y'),
        ('both_larger', 'B', (3+x, 4+x+z+y, 4+x+z), 'a=3+x,c=4+x+z,b=4+x+z+y'),
    ]:
        scores, trace, m = graph_expressions(*sizes)
        score_num, score_den = scores[best]
        actual = difference(((m+1)*score_num, score_den), trace)
        results.append(verify_ratio('improvement_'+name, actual, noop['comparisons'][name], substitution))
    package = Path(__file__).parent
    result = {
        'schema_version': 'uniform-repair-six-comparisons-v1', 'pass': True,
        'ranking_certificate_sha256': rank_hash, 'noop_certificate_sha256': noop_hash,
        'implementation_sha256': {name: hashlib.sha256((package/name).read_bytes()).hexdigest()
                                 for name in ('verify_uniform_repair.py', 'verify_certificate.py', 'verify_all_deletions.py')},
        'method': 'exact sparse integer cross-products of audited electrical score and trace formulas',
        'comparisons': results,
        'proof_boundary': 'For integer 3<=a<=b,c after one minimum-part hub-edge failure, uniform independent source/target and zero self-hit: exactly all u-incident A pairs minimize if all sizes equal; otherwise exactly all internal pairs in largest original parts minimize. Restoration permission does not change this optimum, and it strictly beats no insertion. Graph-to-electrical derivation, orbit coverage, monotonic untouched scores and exhaustive integer substitutions require the accompanying independent proof audit. No weighted optimum, nonuniform workload, physical performance, Lean formalization or novelty is certified.',
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes((json.dumps(result, indent=2)+'\n').encode())
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
