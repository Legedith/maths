"""Bounded exact checker; finite validations do not replace analytic bridges."""
import argparse,hashlib,json,platform,itertools
from pathlib import Path
import sympy as S
from strength_minimax import solve,compare,balance_candidate,encode_certificate,InconclusiveError

def multipartite():
    labels=[0]*3+[1]*4+[2]*4+[3]
    edges=[(i,j,S.Integer(1)) for i,j in itertools.combinations(range(12),2) if labels[i]!=labels[j] and (i,j)!=(0,11)]
    allowed=[(i,j) for i,j in itertools.combinations(range(12),2) if (i,j,1) not in edges]
    return edges,allowed

def direct_checks(result):
    """Grounded inverses at rational strengths; no centered inverse/update reuse."""
    n=result['n'];q=result['focus'];count=0
    for g in result['classes']:
        # Every allowed physical edge, not only class representatives.
        for edge in g['edges']:
            for t in (S.Integer(0),S.Rational(1,2)):
                L=S.zeros(n)
                for u,v,w in result['merged_edges']+[(edge[0],edge[1],t)]:
                    L[u,u]+=w;L[v,v]+=w;L[u,v]-=w;L[v,u]-=w
                G=L[:n-1,:n-1].inv()
                for j,theta in enumerate(result['interval']):
                    law=S.ones(n,1)*(1-theta)/n;law[q]+=theta
                    cov=S.diag(*law)-law*law.T
                    actual=2*(result['old_volume']+t)*S.trace(G*cov[:n-1,:n-1])
                    predicted=2*(1-theta)/n*(result['old_volume']+t)*(result['T_endpoints'][j]-t*g['s_endpoints'][j]/(1+g['r']*t))
                    assert actual==predicted
                    count+=1
    return count

def certificate():
    t,m,r,T,s=S.symbols('t m r T s',positive=True)
    f=(m+t)*(T-t*s/(1+r*t));B=r*T-s;A=T-m*s
    assert S.cancel(S.diff(f,t)-(A+B*(2*t+r*t*t))/(1+r*t)**2)==0
    assert S.cancel(S.diff(f,t,2)-2*s*(m*r-1)/(1+r*t)**3)==0
    assert S.limit(f/t,t,S.oo)==B/r
    T0,T1,s0,s1,O0,O1=S.symbols('T0 T1 s0 s1 O0 O1',positive=True)
    B0=r*T0-s0;B1=r*T1-s1
    N=(T0+B0*t)*O1-(T1+B1*t)*O0
    assert S.cancel((m+t)*(T0-t*s0/(1+r*t))/O0-(m+t)*(T1-t*s1/(1+r*t))/O1-(m+t)*N/((1+r*t)*O0*O1))==0
    balance=(T1*O0-T0*O1)/(B0*O1-B1*O0)
    assert S.cancel(N.subs(t,balance))==0
    edges,allowed=multipartite()
    main=solve(12,edges,11,(0,'1/10'),allowed)
    assert len(main['allowed_edges'])==16 and len(main['classes'])==4
    assert sum(len(g['candidates']) for g in main['classes'])==11
    assert compare(main['oracle_endpoint_f'][0],S.sqrt(112079)/33+S.Rational(5144,99))==0
    assert compare(main['oracle_endpoint_f'][1],S.sqrt(10081666)/250+S.Rational(162923,3000))==0
    assert len(main['global_actions'])==1 and main['global_actions'][0]['edge']==(0,11)
    restore=next(g for g in main['classes'] if g['edges']==[(0,11)])
    assert restore['optimum']['kinds']==['balance']
    for g in main['classes']:
        for row in g['candidates']:
            if row is not restore['optimum']:assert compare(row['worst_relative_regret'],main['global_minimax_relative_regret'])>0
    path=solve(3,[(0,1,1),(1,2,2)],1,(0,'1/10'),[(0,2)])
    assert path['classes'][0]['r']==S.Rational(3,2) and path['old_volume']==3
    cycle=solve(4,[(0,1,1),(1,2,1),(2,3,1),(3,0,1)],0,(0,0),[(0,2),(1,3)])
    assert {a['edge'] for a in cycle['global_actions']}=={(0,2),(1,3)}
    assert all(g['balance_case']=='coincident' for g in cycle['classes'])
    assert compare(cycle['global_minimax_relative_regret'])==0
    noop=solve(12,edges,11,('14/405','14/405'),[(1,2)])
    assert noop['global_actions']==[{'edge':None,'strength':S.Integer(0)}]
    assert compare(noop['global_minimax_relative_regret'])==0
    # Exact degeneracy algebra, explicitly abstract rather than graph examples.
    degeneracies=[]
    for name,Ts,Bs in [('zero',(1,1),(2,1)),('negative',(2,1),(2,1)),('parallel_no_crossing',(1,2),(1,1)),('coincident',(1,1),(1,1)),('positive',(1,2),(2,1))]:
        Ts=list(map(S.Integer,Ts));Bs=list(map(S.Integer,Bs));Os=[S.Integer(1)]*2
        kind,strength=balance_candidate(Ts,Bs,Os);assert kind==name
        if strength is not None:assert Ts[0]+Bs[0]*strength==Ts[1]+Bs[1]*strength
        degeneracies.append({'case':kind,'strength':strength,'abstract_not_graph':True})
    invalid=[(2,[(0,1,1)],0,(0,0),[(0,1)]),(3,[(0,1,1)],0,(0,0),[(0,2)]),(3,[(0,1,1),(1,2,2)],1,(0,1),[(0,2)]),(3,[(0,1,1),(1,2,2)],1,(0,0),[(0,1)]),(3,[(0,1,1),(1,2,-2)],1,(0,0),[(0,2)]),(3,[(0,1,1),(1,2,2)],1,(0,0),[]),(3,[(0,0,1),(0,1,1),(1,2,2)],1,(0,0),[(0,2)])]
    for args in invalid:
        try:solve(*args)
        except ValueError:pass
        else:raise AssertionError('invalid input accepted')
    counts={name:direct_checks(value) for name,value in [('344',main),('weighted_path',path),('cycle',cycle),('noop',noop)]}
    here=Path(__file__).resolve().parent
    # Compare frozen certificate data as inert JSON, never executable strings.
    baseline=json.loads((here/'baseline/result.json').read_text(encoding='utf-8'))
    for key,value in [('witness344',main),('weighted_path',path),('collapsed_cycle',cycle),('untouched_only_noaction',noop)]:
        assert encode_certificate(value)==baseline[key], 'original API certificate changed: '+key
    wide=solve(12,edges,11,(0,'9/10'),allowed)
    assert len(wide['allowed_edges'])==16
    base=[wide['old_volume']*tt/oo-1 for tt,oo in zip(wide['T_endpoints'],wide['oracle_endpoint_f'])]
    assert compare(base[1],base[0])>0
    bc=next(g for g in wide['classes'] if (3,4) in g['edges'])
    assert compare(bc['A_endpoints'][0])<0 and compare(bc['A_endpoints'][1])>0
    assert compare(bc['optimum']['strength'])==0
    counts['344_wide']=direct_checks(wide)
    return {'status':'PASS','wide_interval_regression':wide,'affine_crossproduct_identities':2,'original_api_certificates_byte_value_equal':4,'runtime':{'python':platform.python_version(),'sympy':S.__version__},'implementation_hashes':{name:hashlib.sha256((here/name).read_bytes()).hexdigest() for name in ('strength_minimax.py','verify_strength_minimax.py')},'symbolic_derivative_identities':3,'direct_grounded_objective_checks':counts,'invalid_inputs_rejected':len(invalid),'balance_degeneracies':degeneracies,'witness344':main,'weighted_path':path,'collapsed_cycle':cycle,'untouched_only_noaction':noop,'analytic_bridges_required':['Dirichlet test-potential mr>=4 and complete equality conditions for absent pairs.','Graph pseudoinverse and fixed iid covariance/commute reduction with actual total conductance m+t.','PSD rank n-2 establishes positive B; compact workloads and finite edges give uniform positivity/coercivity and attained oracle.','Continuum supremum commutes with two-endpoint maximum after positivity is established.','Strict convexity gives one per-edge optimum; derivative and balance candidates exhaust all minimizers.','All t0 labels are one physical no action; distinct edge locations may tie.'],'implementation_limits':['Exact rational inputs only; floating inputs rejected.','Certified radical interval arithmetic at up to320 bits and exact symbolic zero simplification; unresolved comparisons raise InconclusiveError, never return a recommendation.','No polynomial-time or all-input termination guarantee; caller should enforce wall-clock resource limit.','Finite API cases validate implementation, not universal enumeration or proof-assistant formalization.']}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists():parser.error('output already exists; choose a fresh path')
    try:result=encode_certificate(certificate())
    except InconclusiveError as exc:parser.exit(3,'INCONCLUSIVE: '+str(exc)+'\n')
    with args.output.open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'status':'PASS','witness_edges':16,'witness_candidate_entries':11}))

if __name__=='__main__':main()
