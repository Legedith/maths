import argparse,json,hashlib,platform
from pathlib import Path
import sympy as S
from source_target_minimax import solve,roots,value,compare,encode_certificate,InconclusiveError

def check():
    path=[(0,1,1),(1,2,2)];allowed=[(0,2)]
    cases=[solve(3,path,1,(x,x),allowed) for x in ('99/100','98/101')]
    cases += [solve(3,path,1,(0,'99/100'),allowed),solve(4,[(0,1,1),(1,2,1),(2,3,1),(3,0,1)],0,(0,0),[(0,2),(1,3)])]
    assert cases[0]['classes'][0]['curvature_numerators'][0]<0
    assert cases[1]['classes'][0]['curvature_numerators'][0]==0
    assert all(c['global_actions']==[{'edge':None,'strength':S.Integer(0)}] for c in cases[:2])
    assert {a['edge'] for a in cases[3]['global_actions']}=={(0,2),(1,3)}
    count=0
    for case in cases:
        n=case['n'];q=case['focus']
        for g in case['classes']:
            for t in (S.Integer(0),S.Rational(1,2),S.Integer(2)):
                W=S.zeros(n)
                for u,v,w in case['edges']+[(g['edge'][0],g['edge'][1],t)]:W[u,v]+=w;W[v,u]+=w
                d=W*S.ones(n,1);P=S.diag(*[1/x for x in d])*W;F=[]
                for target in range(n):
                    idx=[i for i in range(n) if i!=target]
                    hits=(S.eye(n-1)-P.extract(idx,idx)).inv()*S.ones(n-1,1)
                    F.append(sum(hits)/n)
                for j,theta in enumerate(case['interval']):
                    actual=(1-theta)*sum(F)/n+theta*F[q]
                    assert S.cancel(actual-value(g['coefficients'][j],g['r'],t))==0
                    count+=1
    degeneracies=[]
    for coeff,kind in [([0,0,0],'identically_zero'),([1,0,0],'constant'),([-1,1,0],'linear'),([1,-2,1],'quadratic_repeated'),([1,0,1],'quadratic_no_real'),([0,1,1],'quadratic_two_real'),([-2,1,1],'quadratic_two_real')]:
        rr=roots(coeff);assert rr['case']==kind
        for t in rr['real_roots']:assert S.simplify(sum(S.Integer(c)*t**k for k,c in enumerate(coeff)))==0
        degeneracies.append(rr)
    t,r,a,b,c=S.symbols('t r a b c');f=(a+b*t+c*t*t)/(1+r*t)
    assert S.cancel(S.diff(f,t)-(b-r*a+2*c*t+r*c*t*t)/(1+r*t)**2)==0
    assert S.cancel(S.diff(f,t,2)-2*(c-r*b+r*r*a)/(1+r*t)**3)==0
    # Formal directed rank-one expansion, independently regrouped.
    m,Mq,Md,Mw,zq,zd,zw=S.symbols('m Mq Md Mw zq zd zw');D=1+r*t
    expanded=2*(m+t)*(Mq-t*zq*zq/D)-(Md+t*Mw-t*zq*(zd+t*zw)/D)
    F0=2*m*Mq-Md;F1=2*Mq-Mw;P1=zq*(zd-2*m*zq);P2=zq*(zw-2*zq)
    assert S.cancel(expanded-(F0+(r*F0+F1+P1)*t+(r*F1+P2)*t*t)/D)==0
    invalid=[(3,path,1,(0,1),allowed),(3,path,1,(0,0),[(0,1)]),(3,path,1,(0,0),[]),(3,[(0,1,0),(1,2,2)],1,(0,0),allowed),(3,[(0,1,1)],1,(0,0),allowed),(3,path,1,(0.0,0),allowed),(3,path,1,(0,0),allowed*2)]
    for args in invalid:
        try:solve(*args)
        except ValueError:pass
        else:raise AssertionError('malformed input accepted')
    return {'status':'PASS','model':'uniform-source-independent-mixed-target','runtime':{'python':platform.python_version(),'sympy':S.__version__},'cases':cases,'direct_first_step_comparisons':count,'symbolic_identities':3,'root_degeneracies':degeneracies,'invalid_rejections':len(invalid),'analytic_bridges':['Directed first-step identity and rank-one coefficient derivation.','h<1 uniform component gives positive coercive objectives and attained same-action-set oracles.','Positive affine endpoint ratio lemma for continuum comparator actions.','Strict quasiconvexity, not strict convexity, yields unique edge strength and quadratic candidate completeness.'],'limits':['Partial exact radical comparator; unresolved comparisons raise InconclusiveError.','Generic simplify can be expensive: enforce an external process-tree-aware wall limit.','Finite validation is not exhaustive graph proof; no novelty, physical benefit or release approval.']}

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():p.error('output already exists')
    here=Path(__file__).resolve().parent
    assert hashlib.sha256((here/'exact_support.py').read_bytes()).hexdigest()=='0057aae1dc61cfcb69c43bd2fcb5b43674e66a252c409a857b71a069eef82980'
    try:result=check();result['module_hashes']={name:hashlib.sha256((here/name).read_bytes()).hexdigest() for name in ('source_target_minimax.py','exact_support.py','verify_source_target.py')};out=encode_certificate(result)
    except InconclusiveError as exc:p.exit(3,'INCONCLUSIVE: '+str(exc)+'\n')
    with args.output.open('x',encoding='utf-8',newline='\n') as stream:json.dump(out,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'status':'PASS','direct_first_step_comparisons':result['direct_first_step_comparisons']}))
if __name__=='__main__':main()
