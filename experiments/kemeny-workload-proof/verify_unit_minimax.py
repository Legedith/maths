"""Exact certificates and finite illustrations for deterministic unit minimax."""
import argparse
import hashlib
import itertools
import json
import platform
from pathlib import Path
import sympy as S

def unit_policy(a,b,c,lo,hi):
    """Complete physical action set for exact rational workload endpoints."""
    if not all(isinstance(q,int) for q in (a,b,c)) or not 3<=a<=b<=c:
        raise ValueError('require integer 3<=a<=b<=c')
    lo,hi=S.Rational(lo),S.Rational(hi)
    if not 0<=lo<=hi<1: raise ValueError('require 0<=lo<=hi<1')
    n=a+b+c+1;d=n-a;e=n-c
    k=S.Rational((n-1)*(d-1),n*d)
    W=S.Rational(n*(n-1)+d*(d-1),n*n*d*d)
    R=W/k;Z=d*(d+2)*k+1
    T=sum(S.Rational(q-1,n-q) for q in (a,b,c))+S.Rational(3,n)+R
    hh=S.Rational(n-1,n*n)+1/(n*n*k)
    if a==c:
        J=(2*k+S.Rational(2,d)+R)/Z;lam=1/(n*k*Z)
        X=[(0,v) for v in range(1,a)]
    else:
        J=S.Rational(2,e*(e+2));lam=S.Integer(0)
        X=[];offset=0
        for q in (a,b,c):
            if q==c:X.extend(itertools.combinations(range(offset,offset+q),2))
            offset+=q
    restoration=[(0,n-1)]
    alpha=T-J;beta=n*hh-lam;gamma=T-R;delta=n*hh-1/(n*k)
    tau=(J-R)/(1/(n*k)-lam)
    A=lambda q:alpha+beta*q
    B=lambda q:gamma+delta*q
    assert all(f(q)>0 for f in (A,B) for q in (lo,hi))
    rx=max(A(q)/min(A(q),B(q))-1 for q in (lo,hi))
    rr=max(B(q)/min(A(q),B(q))-1 for q in (lo,hi))
    if lo==hi:
        case='collapsed';expected=X if lo<tau else restoration if lo>tau else X+restoration
    elif hi<=tau:case='X_one_sided';expected=X
    elif lo>=tau:case='R_one_sided';expected=restoration
    else:
        case='interior_crossing';px=A(lo)*A(hi);pr=B(lo)*B(hi)
        expected=X if px<pr else restoration if px>pr else X+restoration
    selected=(X if rx<=rr else [])+(restoration if rr<=rx else [])
    assert sorted(selected)==sorted(expected)
    return {'parts':[a,b,c],'interval':[str(lo),str(hi)],'tau':str(tau),'case':case,'X_edges':[list(q) for q in X],'restoration_edges':[list(q) for q in restoration],'minimax_edges':[list(q) for q in sorted(selected)],'lines':{'X':[str(alpha),str(beta)],'R':[str(gamma),str(delta)]},'endpoint_products':{'X':str(A(lo)*A(hi)),'R':str(B(lo)*B(hi))},'worst_relative_regrets':{'X':str(rx),'R':str(rr)},'minimax_value':str(min(rx,rr))}

def graph_lines(parts,strength,restoration_allowed):
    n=sum(parts)+1;hub=n-1;labels=[]
    for i,q in enumerate(parts):labels.extend([i]*q)
    labels.append(3)
    old={e for e in itertools.combinations(range(n),2) if labels[e[0]]!=labels[e[1]]}-{(0,hub)}
    missing=sorted(set(itertools.combinations(range(n),2))-old)
    if not restoration_allowed:missing.remove((0,hub))
    L=S.zeros(n);eye=S.eye(n);J=S.ones(n)/n
    def v(e):return eye[:,e[0]]-eye[:,e[1]]
    for e in sorted(old):L+=v(e)*v(e).T
    records=[]
    for e in missing:
        G=L+strength*v(e)*v(e).T;M=(G+J).inv()-J
        assert G*M==eye-J
        volume=len(old)+strength
        alpha=2*volume*S.trace(M)/n;beta=2*volume*M[hub,hub]
        assert alpha>0 and beta>=0
        records.append((e,alpha,beta))
    return len(old),records

def certificate():
    n,d,e=S.symbols('n d e',positive=True)
    k=(n-1)*(d-1)/(n*d);W=(n*(n-1)+d*(d-1))/(n*n*d*d)
    ri=2/d+1/(d*d*k);si=2/d**2+2/(d**3*k)+W/(d*d*k*k);zh=-1/(n*d*k)
    I=si/(1+ri);lam=n*zh*zh/(1+ri);C=(2/e**2)/(1+2/e)
    Z=d*(d+2)*k+1
    assert S.cancel(I-(2*k+2/d+W/k)/Z)==0
    assert S.cancel(lam-1/(n*k*Z))==0
    gap=S.cancel(C-I-lam)
    x,y,z=S.symbols('x y z',nonnegative=True);a=x+3;polys=[]
    for name,b,c in [('b_equal_a',a,a+1+z),('b_above_a',a+1+y,a+1+y+z)]:
        expr=S.cancel(gap.subs({n:a+b+c+1,d:b+c+1,e:a+b+1},simultaneous=True))
        N,D=S.fraction(expr);entry={'case':name,'polynomials':{}}
        for key,q in [('numerator',N),('denominator',D)]:
            P=S.Poly(q,x,y,z);terms=[{'powers':list(power),'coefficient':str(coef)} for power,coef in P.terms()]
            rebuilt=sum(S.Integer(row['coefficient'])*x**row['powers'][0]*y**row['powers'][1]*z**row['powers'][2] for row in terms)
            assert S.expand(rebuilt-q)==0
            assert all(coef>0 for _,coef in P.terms()) and P.eval({x:0,y:0,z:0})>0
            entry['polynomials'][key]={'terms':terms,'constant':str(P.eval({x:0,y:0,z:0})),'total_degree':P.total_degree()}
        entry['exact_identity']=str(S.factor(expr));polys.append(entry)
    # Generic derivative and positive-affine abstract examples.
    t,A,B,C0,D0=S.symbols('t A B C D')
    assert S.cancel(S.diff((A+B*t)/(C0+D0*t),t)-(B*C0-A*D0)/(C0+D0*t)**2)==0
    examples=[]
    for name,third in [('weak_domination',(S.Rational(3,2),S.Integer(1))),('oracle_inactive_compromise',(S.Rational(3,2),S.Integer(0)))]:
        lines=[(S.Integer(1),S.Integer(2)),(S.Integer(2),S.Integer(-2)),third]
        vals=[[aa+bb*q for aa,bb in lines] for q in (S.Integer(0),S.Rational(1,2))]
        regrets=[max(row[i]/min(row)-1 for row in vals) for i in range(3)]
        assert regrets==([1,1,1] if name=='weak_domination' else [1,1,S.Rational(1,2)])
        examples.append({'name':name,'abstract_not_graph_realization':True,'endpoint_values':[[str(v) for v in row] for row in vals],'worst_regrets':[str(v) for v in regrets]})
    # Illustrative policy cells from the exact accepted formulas, not a grid.
    tau=S.Rational(46,2205);r=unit_policy(3,3,3,0,S.Rational(21,500))
    aa,bb=map(S.Rational,r['lines']['X']);cc,dd=map(S.Rational,r['lines']['R'])
    tie=(cc*cc-aa*aa)/(aa*bb-cc*dd)
    assert tau<tie<1
    specifications=[('collapsed_below',0,0),('collapsed_crossing',tau,tau),('collapsed_above',(tau+1)/2,(tau+1)/2),('left_boundary_crossing',tau,(tau+1)/2),('right_boundary_crossing',0,tau),('interior_X',0,S.Rational(21,500)),('interior_product_tie',0,tie),('interior_R',0,S.Rational(1,2))]
    policy_checks=[{'name':name,'result':unit_policy(3,3,3,l,h)} for name,l,h in specifications]
    assert len(policy_checks[6]['result']['minimax_edges'])==3
    large=unit_policy(3,3,100,0,S.Rational(9,10));assert S.Rational(large['tau'])>=1
    policy_checks.append({'name':'unequal_tau_at_least_one','result':large})
    tied=unit_policy(3,4,4,0,0);assert len(tied['minimax_edges'])==12
    policy_checks.append({'name':'largest_part_ties','result':tied})
    # Every physical candidate matrix for the two frozen witnesses.
    m,lines=graph_lines((3,3,3),S.Integer(1),True);assert m==35 and len(lines)==10
    lo=S.Integer(0);hi=S.Rational(21,500);mid=(lo+hi)/2
    oracle=lambda q:min(alpha+beta*q for _,alpha,beta in lines)
    rows=[]
    for edge,alpha,beta in lines:
        regret=max((alpha+beta*q)/oracle(q)-1 for q in (lo,hi))
        rows.append({'edge':list(edge),'reduced_actual_line':[str(alpha),str(beta)],'actual_endpoint_objectives':[str((1-q)*(alpha+beta*q)) for q in (lo,hi)],'actual_midpoint_objective':str((1-mid)*(alpha+beta*mid)),'worst_relative_regret':str(regret),'endpoint_product':str((alpha+beta*lo)*(alpha+beta*hi))})
    best=min(S.Rational(row['worst_relative_regret']) for row in rows)
    winners=[row['edge'] for row in rows if S.Rational(row['worst_relative_regret'])==best]
    midbest=min(S.Rational(row['actual_midpoint_objective']) for row in rows)
    midwinners=[row['edge'] for row in rows if S.Rational(row['actual_midpoint_objective'])==midbest]
    assert winners==[[0,1],[0,2]] and midwinners==[[0,9]]
    assert best==S.Rational(23305,10372104)
    assert next(row for row in rows if row['edge']==[0,9])['worst_relative_regret']==str(S.Rational(23,10021))
    m2,lines2=graph_lines((3,3,4),S.Integer(16),False);assert m2==42 and len(lines2)==12
    theta=S.Rational(9147,9152)
    vals=[{'edge':list(edge),'reduced_actual_line':[str(alpha),str(beta)],'actual_objective':str((1-theta)*(alpha+beta*theta))} for edge,alpha,beta in lines2]
    minimum=min(S.Rational(row['actual_objective']) for row in vals)
    win=[row['edge'] for row in vals if S.Rational(row['actual_objective'])==minimum]
    cvalue=S.Rational(next(row['actual_objective'] for row in vals if row['edge']==[6,7]))
    actualgap=cvalue-minimum
    assert win==[[0,1],[0,2]] and actualgap==S.Rational(145,6815897088)
    scoregap=actualgap/(2*(m2+16)*16*(1-theta)/11)
    assert scoregap==S.Rational(1,4333056)
    return {'status':'PASS','runtime':{'python':platform.python_version(),'sympy':S.__version__},'implementation_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'unequal_unit_gap':{'formula':str(S.factor(gap)),'shifts':polys},'policy_illustrations':policy_checks,'abstract_endpoint_examples':examples,'midpoint_witness':{'parts':[3,3,3],'interval':[str(lo),str(hi)],'old_volume':m,'inserted_volume':m+1,'candidates':rows,'minimax_edges':winners,'midpoint_edges':midwinners,'formula_policy':r},'strength_scope_counterexample':{'parts':[3,3,4],'strength':'16','theta':str(theta),'restoration_allowed':False,'old_volume':m2,'inserted_volume':m2+16,'candidates':vals,'winning_edges':win,'largest_pair_minus_winner_actual':str(actualgap),'incident_minus_largest_score':str(scoregap)},'analytic_bridges_required':['Weighted commute/covariance reduction under fixed iid hub mixture, zero self hit and connected positive graphs; differing fixed action volumes remain inside their own affine lines.','Accepted inverse-action formulas and equal-family envelope; the symbolic checker does not derive the universal graph inverse.','Two disjoint integer shifts exhaust unequal sorted triples; positive constants and nonnegative coefficients prove full-domain positivity.','Largest-part untouched score ordering and strict unit incident domination imply fixed-action strict domination of every excluded physical action.','Finite positive-affine endpoint lemma follows by constant-sign quotient derivatives and commuting finite maxima; no oracle-switch grid is needed.','Strict domination at both endpoints excludes all tied minimizers; weak domination alone may preserve only value.','Complete policy uses positive lines, unique crossing, exact product comparison and all physical ties; theta1 has zero actual objectives and undefined relative regret.'],'limitations':['Universal policy requires exactly one unit insertion with restoration allowed; no action, strength optimization, randomization and adaptive actions excluded.','Two finite matrix witnesses illustrate or delimit scope, not universal enumeration.','Abstract affine examples are not asserted graph-realizable.','No generic-method novelty, priority, physical benefit or proof-assistant certification.']}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists():parser.error('output already exists; choose a fresh path')
    result=certificate()
    with args.output.open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'status':'PASS','unit_witness_candidates':10,'strength_witness_candidates':12}))

if __name__=='__main__':main()
