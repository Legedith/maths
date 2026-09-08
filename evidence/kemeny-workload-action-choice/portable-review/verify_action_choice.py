"""Exact action-choice certificates; analytic bridges are explicit in output."""
import argparse
import hashlib
import itertools
import json
import platform
from pathlib import Path
import sympy as S

def sqrt_bounds(q):
    assert q >= 0
    lo, hi = S.Rational(0), max(S.Rational(1), q)
    for _ in range(80):
        mid = (lo+hi)/2
        if mid*mid <= q: lo = mid
        else: hi = mid
    assert lo*lo <= q <= hi*hi
    return lo, hi

def certificate():
    a,x=S.symbols('a x', positive=True)
    n=3*a+1;d=2*a+1;m=3*a*a+3*a-1
    k=(n-1)*(d-1)/(n*d);w=(n*(n-1)+d*(d-1))/(n*n*d*d)
    T=3*(a-1)/d+3/n+w/k;hh=(n-1)/n**2+1/(n*n*k)
    R=w/k;Z=d*(d+2)*k+1;U=(2*k+2/d+R)/Z
    tau=(a-2)*(10*a*a+a-1)/((2*a+1)**2*(2*a+3)*(3*a+1))
    FR0=(m+1)*R-T;FRs=(m+1)/(n*k)-n*hh
    FU0=(m+1)*U-T;FUs=(m+1)/(n*k*Z)-n*hh
    cross=(18*a**6+531*a**5+306*a**4+39*a**3-15*a*a-8*a-1)/(3*a*a*(2*a+1)**2*(2*a+3)*(3*a+1)**2)
    rs=(18*a**4+15*a**3+12*a*a-2*a-1)/(6*a*a*(3*a+1))
    minus_us=(216*a**6+342*a**5+105*a**4+51*a**3+12*a*a+5*a+1)/(6*a*a*(3*a+1)*(12*a**3+18*a*a+3*a+1))
    assert all(S.cancel(z)==0 for z in (FR0+tau*FRs-cross,FU0+tau*FUs-cross,FRs-rs,FUs+minus_us))
    positive={}
    for name,expr in [('switch_margin',cross),('restore_slope',rs),('negative_incident_slope',minus_us),('threshold',tau),('threshold_complement',1-tau)]:
        num,den=S.fraction(S.cancel(expr.subs(a,x+3)))
        lists={key:[str(z) for z in S.Poly(poly,x).all_coeffs()] for key,poly in [('numerator',num),('denominator',den)]}
        assert all(int(z)>0 for vals in lists.values() for z in vals)
        positive[name]={'formula':str(S.factor(expr)),'shift':'a=x+3, x>=0','coefficients_descending':lists}
    # Direct graph reconstruction, independent of the compact family formulas.
    n=12;h=11;m=50;labels=[0]*3+[1]*4+[2]*4+[3]
    edges={e for e in itertools.combinations(range(n),2) if labels[e[0]]!=labels[e[1]]}-{(0,h)}
    missing=sorted(set(itertools.combinations(range(n),2))-edges)
    assert len(edges)==m and len(missing)==16
    def v(e): return S.eye(n)[:,e[0]]-S.eye(n)[:,e[1]]
    L=S.zeros(n)
    for e in sorted(edges): L+=v(e)*v(e).T
    J=S.ones(n)/n;M=(L+J).inv()-J
    assert L*M==S.eye(n)-J
    T=S.trace(M);hh=M[h,h]
    assert T==S.Rational(985,792) and hh==S.Rational(269,3168)
    theta=S.Symbol('theta');tau=S.Rational(14,405);lo=S.Rational(124,4035);hi=S.Rational(59,1662)
    FC=S.Rational(31,990)-S.Rational(269,264)*theta
    FR=-S.Rational(59,396)+S.Rational(277,66)*theta
    assert 0<lo<tau<hi<1 and FC.subs(theta,lo)==FR.subs(theta,hi)==0
    assert FC.subs(theta,tau)==FR.subs(theta,tau)==-S.Rational(19,4860)
    factor=2*(1-tau)/n;Ttheta=T+n*tau*hh
    assert Ttheta==S.Rational(12431,9720)
    t,r,s,V,vol=S.symbols('t r s V vol', positive=True)
    f=(vol+t)*(V-t*s/(1+r*t));A=V-vol*s;B=r*V-s
    assert S.cancel(S.diff(f,t)-(A+B*(2*t+r*t*t))/(1+r*t)**2)==0
    assert S.limit(f/t,t,S.oo)==B/r
    rows=[];winner_edges=[];winner_bounds=None;other_bounds=[]
    for e in missing:
        N=(L+v(e)*v(e).T+J).inv()-J
        assert (L+v(e)*v(e).T)*N==S.eye(n)-J
        unit=S.expand(n*(m*(T/n+theta*hh)-(m+1)*(S.trace(N)/n+theta*N[h,h])))
        iswinner=labels[e[0]] in (1,2)
        if e==(0,h): assert unit==FR
        elif iswinner: assert unit==FC
        else:
            assert all((FC-unit).subs(theta,q)>0 for q in (0,tau))
            assert all((FR-unit).subs(theta,q)>0 for q in (tau,1))
        z=M*v(e);rr=(v(e).T*z)[0];ss=(z.T*z)[0]+n*tau*z[h]**2
        aa=Ttheta-m*ss;bb=rr*Ttheta-ss
        assert rr>0 and bb>0
        ft=(m+t)*(Ttheta-t*ss/(1+rr*t))
        assert S.cancel(S.diff(ft,t)-(aa+bb*(2*t+rr*t*t))/(1+rr*t)**2)==0
        assert S.cancel(ft.subs(t,1)-((m+1)*(S.trace(N)+n*tau*N[h,h])))==0
        if aa<0:
            q=ss*(m*rr-1)/bb;assert q>1
            star=(S.sqrt(q)-1)/rr
            assert S.simplify(aa+bb*(2*star+rr*star**2))==0
            qlo,qhi=sqrt_bounds(q);assert 0<(qlo-1)/rr<(qhi-1)/rr<1
            rad=bb*ss*(m*rr-1);rl,rh=sqrt_bounds(rad)
            bounds=[factor*(bb*(m*rr-1)+ss+2*u)/rr**2 for u in (rl,rh)]
            minimum=factor*(bb*(m*rr-1)+ss+2*S.sqrt(rad))/rr**2
            assert S.simplify(factor*ft.subs(t,star)-minimum)==0
            strength_bounds=[(qlo-1)/rr,(qhi-1)/rr]
        else:
            star=S.Integer(0);q=None;minimum=factor*m*Ttheta
            bounds=[minimum,minimum];strength_bounds=[star,star]
        if iswinner:
            assert rr==S.Rational(1,4) and q==S.Rational(27945,22432)
            winner_edges.append(e)
            if winner_bounds is None:winner_bounds=bounds
            assert bounds==winner_bounds
        else:other_bounds.append(bounds)
        rows.append({'edge':e,'unit_margin':str(unit),'r':str(rr),'s_theta':str(ss),'A':str(aa),'B':str(bb),'radicand':str(q) if q is not None else None,'tstar':str(star),'strength_bounds':[str(u) for u in strength_bounds],'minimum':str(minimum),'minimum_bounds':[str(u) for u in bounds],'infinite_linear_coefficient':str(factor*bb/rr)})
    baseline=factor*m*Ttheta
    assert len(winner_edges)==12 and winner_bounds[1]<baseline
    assert all(winner_bounds[1]<b[0] for b in other_bounds)
    win=rows[next(i for i,row in enumerate(rows) if tuple(row['edge'])==winner_edges[0])]
    half=factor*(m+S.Rational(1,2))*(Ttheta-S.Rational(1,2)*S.Rational(win['s_theta'])/(1+S.Rational(1,2)*S.Rational(win['r'])))
    assert baseline-half==S.Rational(117691,11809800)
    unitbest=factor*(m+1)*(Ttheta-S.Rational(1,40))
    assert unitbest-baseline==S.Rational(7429,11809800)
    return {'status':'PASS','runtime':{'python':platform.python_version(),'sympy':S.__version__},'implementation_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'equal_family':positive,'unit_policy':{'L':str(lo),'tau':str(tau),'R0':str(hi),'F_C':str(FC),'F_R':str(FR),'cells':['[0,L): all12 B/C pairs','L: B/C pairs and no action','(L,R0): no action only','R0: restoration and no action','(R0,1): restoration only'],'theta1':'all17 actions have zero objective'},'finite_graph':{'parts':[3,4,4],'theta':str(tau),'old_volume':m,'candidate_volume':'m+t','trace':str(T),'hub_diagonal':str(hh),'Ttheta':str(Ttheta),'factor':str(factor),'baseline':str(baseline),'unit_best':str(unitbest),'unit_excess':str(unitbest-baseline),'half_strength_objective':str(half),'half_strength_improvement':str(baseline-half),'candidates':rows,'optimal_edges':winner_edges,'optimal_strength':'4*(sqrt(27945/22432)-1)'},'analytic_bridges_required':['Known weighted commute identity and iid covariance reduction with zero self hitting.','Equal-family inverse formulas and complete accepted unit insertion envelope, including all ties.','Positive shifted coefficients imply positivity for every a>=3; opposite slopes make the common switch the worst selected margin.','Finite theta policy follows from affine signs and positive factor for theta<1; theta1 is degenerate.','On t>=0 positive B makes derivative numerator strictly increasing; A>=0 gives boundary minimum, A<0 unique positive global minimum.','Positive B/r excludes infinity; t0 labels all represent the same no action.','Rational square-root enclosures and strict disjoint minimum bounds establish global edge ordering.'],'limitations':['Fixed344 strength rescue only; no universal unequal no-action policy.','No intervention cost, physical benefit, generic-method novelty or formal proof-assistant certification.']}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists():parser.error('output already exists; choose a fresh path')
    result=certificate()
    with args.output.open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'status':'PASS','candidate_count':16,'winning_edges':12}))

if __name__=='__main__':main()
