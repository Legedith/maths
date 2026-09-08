"""Exact symbolic identities; analytic envelope bridges require separate review."""
import argparse
import hashlib
import json
import platform
from pathlib import Path

import sympy as S


def certificate():
    a, n, d, e, t, j, x = S.symbols('a n d e t j x', positive=True)
    k = (n-1)*(d-1)/(n*d)
    W = (n*(n-1)+d*(d-1))/(n**2*d**2)
    DR = k+t*(1-k)
    DU = d**2*k+t*(2*d*k+1)
    R = W/(k*DR)
    U = (2*k+2/d+W/k)/DU
    C = 2/(e*(e+2*t))
    lr, lu = 1/(n*k*DR), 1/(n*k*DU)
    checks = []
    formulas = {}

    def equal(name, lhs, rhs):
        residual = S.cancel(lhs-rhs)
        if residual != 0:
            raise AssertionError(name + ': nonzero residual ' + str(residual))
        checks.append(name)

    def formula(name, value):
        formulas[name] = str(S.factor(value))

    rr, sr, hr = (1-k)/k, W/k**2, -1/(n*k)
    ru = 2/d+1/(d**2*k)
    su = 2/d**2+2/(d**3*k)+W/(d**2*k**2)
    hu = -1/(n*d*k)
    equal('restore_score_from_r_s', sr/(1+t*rr), R)
    equal('restore_slope_from_hub', n*hr**2/(1+t*rr), lr)
    equal('incident_score_from_r_s', su/(1+t*ru), U)
    equal('incident_slope_from_hub', n*hu**2/(1+t*ru), lu)
    equal('untouched_score_from_r_s', (2/e**2)/(1+t*2/e), C)
    equal('untouched_zero_hub_slope', n*S.Integer(0)**2/(1+t*2/e), 0)
    gap = d**2-1+t*(2*d+1)
    equal('denominator_difference', DU-DR, k*gap)
    equal('unit_restore_denominator', DR.subs(t, 1), 1)
    equal('unit_incident_denominator', DU.subs(t, 1), d*(d+2)*k+1)
    E = (DU-DR)*C-DU*U+DR*R
    Eform = 2*(k*(gap/(e*(e+2*t))-1)-1/d)
    equal('E_identity', E, Eform)
    N = d**2-e**2-1+t*(2*d+1-2*e)
    equal('E_rearrangement', d*Eform/2, (n-1)*(d-1)*N/(n*e*(e+2*t))-1)
    equal('N_lower_bound_remainder', (N-(2*e+3*t)).subs(d, e+j), (j-1)*(2*e+j+1+2*t))
    equal('E_lower_bound_simplification', (n-1)*(2*e+3*t)/(n*(e+2*t))-1, ((n-2)*e+(n-3)*t)/(n*(e+2*t)))
    tau = 2*n*k*DR/(e*(e+2*t))-n*W
    equal('unequal_crossing', (C-R)/lr, tau)
    derivative = 2*n*k*(e-k*(e+2))/(e*(e+2*t)**2)
    equal('unequal_derivative', S.diff(tau, t), derivative)
    equal('unequal_derivative_upper_bound', ((d-1)-k*(d+1)).subs(n, d+a), -(a-1)*(d-1)/((d+a)*d))
    equal('unequal_derivative_bound_difference', (d-1)-k*(d+1)-(e-k*(e+2)), (d-1-e)*(1-k))
    tau0 = 2*n*k**2/e**2-n*W
    tauinf = n*k*(1-k)/e-n*W
    equal('unequal_zero_limit', S.limit(tau, t, 0), tau0)
    equal('unequal_infinity_limit', S.limit(tau, t, S.oo), tauinf)
    equal('unequal_infinity_positive_bound', (n*k*(1-k)/(d-1)-n*W).subs(n, d+a), (a-1)*(d-1)/(d**2*(d+a)))
    equal('unequal_infinity_bound_difference', tauinf-(n*k*(1-k)/(d-1)-n*W), n*k*(1-k)*(d-1-e)/(e*(d-1)))
    teq = 2*n*(k+1/d)*DR/gap-n*W
    equal('equal_candidate_crossing_general', (U-R)/(lr-lu), teq)
    eqder = 2*n*(k+1/d)*((d**2-1)-k*d*(d+2))/gap**2
    equal('equal_derivative', S.diff(teq, t), eqder)
    equal('equal_derivative_sign_bound', ((d**2-1)-k*d*(d+2)).subs(n, d+a), -(d-1)*(a-2)/(d+a))
    closed = (a-2)*(20*a**3+8*a**2*t+4*a**2-a*t-t)/((2*a+1)**2*(3*a+1)*(4*a**2+4*a*t+4*a+3*t))
    equal('equal_closed_form', teq.subs({n:3*a+1,d:2*a+1}, simultaneous=True), closed)
    eq0 = a*(a-2)*(5*a+1)/((a+1)*(2*a+1)**2*(3*a+1))
    eqinf = (a-2)*(8*a**2-a-1)/((2*a+1)**2*(3*a+1)*(4*a+3))
    complement = (12*a**4+23*a**3+32*a**2+10*a+1)/((a+1)*(2*a+1)**2*(3*a+1))
    unit = (a-2)*(10*a**2+a-1)/((2*a+1)**2*(2*a+3)*(3*a+1))
    equal('equal_zero_limit', S.limit(closed,t,0), eq0)
    equal('equal_infinity_limit', S.limit(closed,t,S.oo), eqinf)
    equal('equal_zero_complement', 1-eq0, complement)
    equal('equal_unit_reduction', closed.subs(t,1), unit)
    positive = {}
    for name, expr in [('equal_zero',eq0),('equal_infinity',eqinf),('equal_zero_complement',complement),('equal_unit',unit)]:
        numerator, denominator = S.fraction(S.cancel(expr.subs(a,x+3)))
        data = {}
        for side, polynomial in [('numerator',numerator),('denominator',denominator)]:
            poly = S.Poly(polynomial,x)
            coefficients = poly.all_coeffs()
            if not all(v>0 for v in coefficients):
                raise AssertionError(name+' '+side+' lacks strict positive coefficients')
            data[side] = {'degree':poly.degree(),'coefficients_descending':[str(v) for v in coefficients]}
        positive[name] = data
        checks.append(name+'_complete_positive_shifted_coefficients')
    for name, expr in [('k',k),('W',W),('D_R',DR),('D_U',DU),('restore_score',R),('restore_slope',lr),('incident_score',U),('incident_slope',lu),('largest_untouched_score',C),('E',Eform),('N',N),('tau_unequal',tau),('tau_unequal_derivative',derivative),('tau_unequal_zero',tau0),('tau_unequal_infinity',tauinf),('tau_equal',closed),('tau_equal_derivative',eqder),('tau_equal_zero',eq0),('tau_equal_infinity',eqinf),('one_minus_equal_zero',complement),('tau_equal_unit',unit)]:
        formula(name,expr)
    return {
        'status':'PASS', 'checks':checks, 'exact_formulas':formulas,
        'positive_shift':'a=x+3, x>=0', 'full_positive_coefficients':positive,
        'domain':'integers 3<=a<=b<=c; n=a+b+c+1, d=n-a, e=n-c; common t>0; fixed iid hub mixture 0<=theta<1',
        'analytic_bridges_required':[
            'Graph inverse/deletion action must justify input r,s,hub coordinates; identities do not derive them from adjacency.',
            'Commute/covariance identity, centering and equal candidate volume justify the affine scores for actual hitting times.',
            'Missing-edge orbit exhaustion and accepted common-positive-strength uniform ordering are independent proof inputs.',
            'Positive denominators, 0<k<1, a>=3, unequal j>=1 and d=e+j must be used to interpret factored identities as strict inequalities.',
            'Positive E and slope ordering exclude incident-u from unequal envelope; equal envelope uses positive incident slope and uniform ordering.',
            'Monotonicity, positive limits and continuity justify threshold ranges; theta=1 and t=0 are degenerate actual objectives, not strict-ranking endpoints.',
            'Ties within largest parts or incident-u orbits require symmetry; threshold>=1 gives no admitted restoration interval.',
            'Uniform old-weight scaling follows invariant transitions under global conductance scaling; not joint strength optimization or no-action comparison.'
        ],
        'limitations':['Symbolic identities alone do not certify all analytic bridges.','No graph grid, global priority, physical benefit or independent final evidence gate.'],
        'runtime':{'python':platform.python_version(),'sympy':S.__version__},
        'implementation_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True,help='New JSON file; parent must exist, existing files refused.')
    args=parser.parse_args()
    if args.output.exists():
        parser.error('output already exists; choose a fresh path')
    result=certificate()
    with args.output.open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(result,stream,indent=2,sort_keys=True)
        stream.write('\n')
    print(json.dumps({'status':result['status'],'check_count':len(result['checks'])},sort_keys=True))


if __name__=='__main__':
    main()
