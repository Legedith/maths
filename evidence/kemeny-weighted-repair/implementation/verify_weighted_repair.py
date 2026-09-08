"""Exact prescribed-conductance certificates and finite strength diagnostics."""
from __future__ import annotations
import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from verify_certificate import Poly, positive, require
from verify_uniform_repair import graph_expressions, difference, verify_ratio, read_pinned, NOOP_SHA256

WEIGHTED_SHA256 = '3b7df821e983b715b98369ea3cc2fe89196ccd17c29ede949c7058ec6d259cec'
DEPENDENCIES = {
    'verify_certificate.py': 'ef5d3b84e9f78ac3e6e4840a3be675c2806f3df7aa89efa1ef4d5b776dcc4ffd',
    'verify_all_deletions.py': '4ebde785ce3515a0d4d5284b71f5e04a5a536197dc315cae60d293435682b2f9',
    'verify_uniform_repair.py': '08d338487dda30c3e7abcae09dc70b644073adb348762f5419dc17c1eb0f4302',
}

def multiply(left, right):
    return left[0]*right[0], left[1]*right[1]

def electrical_pairs(a, b, c):
    n = a+b+c+1
    d = n-a
    k0 = (n-1)*(d-1)
    w0 = n*(n-1)+d*(d-1)
    # rho=(n+d-1)/(nd), k=k0/(nd), W=w0/(n^2 d^2).
    # Hence rho/k and W/k^2; uv expressions clear powers of nd.
    pairs = {
        'restore': ((n+d-1, k0), (w0, k0*k0)),
        'uv': ((2*k0+n, d*k0), (2*k0*k0+2*n*k0+w0, d*d*k0*k0)),
    }
    for name, q in [('untouched_A', a), ('B', b), ('C', c)]:
        dq = n-q
        pairs[name] = ((Poly(2), dq), (Poly(2), dq*dq))
    for name, rs in pairs.items():
        for label, pair in zip(('r', 's'), rs):
            for side, poly in zip(('numerator', 'denominator'), pair):
                require(all(e[3] == 0 for e in poly.terms), 'fourth variable must remain unused')
                positive(poly, name+' '+label+' '+side)
    return pairs

def evaluate(poly, values):
    require(all(e[3] == 0 for e in poly.terms), 'fourth variable in finite evaluation')
    return sum(co*values[0]**e[0]*values[1]**e[1]*values[2]**e[2]
               for e, co in poly.terms.items())

def rational(pair):
    return Fraction(evaluate(pair[0], (0, 0, 0)), evaluate(pair[1], (0, 0, 0)))

def finite_diagnostics():
    p = electrical_pairs(*map(Poly, (4, 4, 6)))
    rs = {name: tuple(map(rational, pair)) for name, pair in p.items()}
    ri, si = rs['restore']
    rj, sj = rs['untouched_A']
    slope = si*rj-sj*ri
    require(slope != 0, 'finite crossing must be isolated')
    crossing = (sj-si)/slope
    require(crossing == 12, 'finite crossing mismatch')
    at = {name: ss/(1+crossing*rr) for name, (rr, ss) in rs.items()}
    require(at['restore'] == at['untouched_A'] == at['B'], 'finite tie mismatch')
    require(all(at['C'] > v for name, v in at.items() if name != 'C'), 'finite maximum mismatch')
    p = electrical_pairs(*map(Poly, (3, 3, 3)))
    rr, ss = map(rational, p['uv'])
    _, trace, m = graph_expressions(*map(Poly, (3, 3, 3)))
    T, mm = rational(trace), evaluate(m, (0, 0, 0))
    A, B = T-mm*ss, rr*T-ss
    require(A < 0 and B > 0, 'finite strength premises fail')
    rad = ss*(mm*rr-1)/B
    derivative1 = (A+B*(2+rr))/(1+rr)**2
    require(rad == Fraction(1573160, 1037853), 'finite radicand mismatch')
    require(1/rr == Fraction(189, 59), 'finite radical prefactor mismatch')
    require(derivative1 == Fraction(66587, 538160), 'finite derivative mismatch')
    require(1 < rad < (1+rr)**2, 'finite strength not strictly between zero and one')
    return {
        'scope': 'Two finite rational diagnostics only; generic calculus and joint optimality require the accompanying independent proof.',
        'crossing_parts': [4, 4, 6], 'crossing': str(crossing),
        'scores_at_crossing': {k: str(v) for k, v in at.items()},
        'strength_parts': [3, 3, 3], 'radical_prefactor': str(1/rr),
        'radicand': str(rad), 'fprime_at_one': str(derivative1),
        'strict_zero_less_strength_less_one': True,
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--weighted-certificate', type=Path, required=True)
    parser.add_argument('--noop-certificate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), 'use a fresh output path')
    package = Path(__file__).parent
    hashes = {}
    for name, expected in DEPENDENCIES.items():
        digest = hashlib.sha256((package/name).read_bytes()).hexdigest()
        require(digest == expected, 'changed dependency: '+name)
        hashes[name] = digest
    hashes[Path(__file__).name] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    weighted, whash = read_pinned(args.weighted_certificate, WEIGHTED_SHA256)
    noop, nhash = read_pinned(args.noop_certificate, NOOP_SHA256)
    expected = {i+'>'+j+':'+mode for i, j in [('uv','restore'),('uv','untouched_A'),('B','uv')]
                for mode in ('intercept','slope')}
    require(set(weighted['comparisons']) == expected, 'incorrect weighted comparison set')
    require(set(noop['comparisons']) == {'equal','one_larger','both_larger'}, 'incorrect no-op set')
    x, y, z = (Poly.variable(i) for i in range(3))
    results = []
    for i, j, sizes, shift in [
        ('uv','restore',(3+x,3+x+y,3+x+z),'a=3+x,b=3+x+y,c=3+x+z'),
        ('uv','untouched_A',(3+x,3+x+y,3+x+z),'a=3+x,b=3+x+y,c=3+x+z'),
        ('B','uv',(3+x,4+x+y,3+x+z),'a=3+x,b=4+x+y,c=3+x+z'),
    ]:
        pairs = electrical_pairs(*sizes)
        ri, si = pairs[i]
        rj, sj = pairs[j]
        for mode, actual in [('intercept', difference(si,sj)),
                             ('slope', difference(multiply(si,rj),multiply(sj,ri)))]:
            name = i+'>'+j+':'+mode
            row = weighted['comparisons'][name]
            certificate = {'numerator_terms': row['num_terms'], 'denominator_terms': row['den_terms']}
            results.append(verify_ratio(name,actual,certificate,shift))
    for name, best, sizes, shift in [
        ('equal','uv',(3+x,3+x,3+x),'a=b=c=3+x'),
        ('one_larger','B',(3+x,4+x+y,3+x),'a=c=3+x,b=4+x+y'),
        ('both_larger','B',(3+x,4+x+z+y,4+x+z),'a=3+x,c=4+x+z,b=4+x+z+y'),
    ]:
        scores, trace, m = graph_expressions(*sizes)
        num, den = scores[best]
        results.append(verify_ratio('improvement_'+name,
            difference(((m+1)*num,den),trace),noop['comparisons'][name],shift))
    result = {
        'schema_version': 'weighted-repair-nine-comparisons-v1', 'pass': True,
        'weighted_certificate_sha256': whash, 'noop_certificate_sha256': nhash,
        'implementation_sha256': hashes, 'comparisons': results,
        'finite_diagnostics': finite_diagnostics(),
        'method': 'Exact integer polynomial cross-products; only first three variables used, so helper fourth-exponent truncation has no effect.',
        'proof_boundary': 'Certificates verify six affine-component signs and three unit-improvement premises. Connected graph reduction, weighted uniform-walk volume m+t, complete missing-edge orbits, integer-domain coverage, common-t optimum set, generic derivative and endpoint arguments, and joint global strength optimum require accompanying independently audited proofs. Finite diagnostics do not establish generic calculus. No monetary cost, physical-performance or novelty claim.',
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes((json.dumps(result,indent=2)+'\n').encode())
    print(json.dumps(result,indent=2))

if __name__ == '__main__':
    main()

