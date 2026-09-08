import sympy as S
from exact_support import rational,compare,minimum,encode_certificate,InconclusiveError

def solve(n,edges,focus,interval,allowed):
    if type(n) is not int or n<3 or type(focus) is not int or not 0<=focus<n:
        raise ValueError('require n>=3 and a valid integer focus')
    if len(interval)!=2:raise ValueError('require two interval endpoints')
    lo,hi=map(rational,interval)
    if not 0<=lo<=hi<1:raise ValueError('require 0<=lo<=hi<1')
    weights={}
    for row in edges:
        if len(row)!=3:raise ValueError('edge needs two vertices and weight')
        u,v,w=row
        if type(u) is not int or type(v) is not int or not 0<=u<n or not 0<=v<n or u==v:
            raise ValueError('invalid edge or self loop')
        w=rational(w)
        if w<=0:raise ValueError('present weights must be positive')
        pair=tuple(sorted((u,v)));weights[pair]=weights.get(pair,0)+w
    reach={0}
    while True:
        enlarged=reach|{v for u,v in weights if u in reach}|{u for u,v in weights if v in reach}
        if enlarged==reach:break
        reach=enlarged
    if len(reach)!=n:raise ValueError('graph must be connected')
    pairs=[]
    for pair in allowed:
        if len(pair)!=2:raise ValueError('allowed edge needs two vertices')
        u,v=pair
        if type(u) is not int or type(v) is not int or not 0<=u<n or not 0<=v<n or u==v:
            raise ValueError('invalid allowed edge')
        pair=tuple(sorted((u,v)))
        if pair in weights or pair in pairs:raise ValueError('allowed pairs must be distinct and absent')
        pairs.append(pair)
    pairs=sorted(pairs)
    if not pairs:raise ValueError('allowed set must be nonempty')
    L=S.zeros(n);eye=S.eye(n);J=S.ones(n)/n
    for (u,v),w in sorted(weights.items()):
        z=eye[:,u]-eye[:,v];L+=w*z*z.T
    M=(L+J).inv()-J
    assert L*M==eye-J
    m=sum(weights.values());d=L.diagonal().T;T=S.trace(M);classes=[]
    for edge in pairs:
        u,v=edge;z=M*(eye[:,u]-eye[:,v]);w=eye[:,u]+eye[:,v]
        r=z[u]-z[v];s=(z.T*z)[0];q=focus
        F0=2*m*M[q,q]-(M*d)[q];F1=2*M[q,q]-(M*w)[q]
        P1=z[q]*((z.T*d)[0]-2*m*z[q]);P2=z[q]*((z.T*w)[0]-2*z[q])
        uniform=[2*m*T/n,2*(T+m*r*T-m*s)/n,2*(r*T-s)/n]
        focused=[F0,r*F0+F1+P1,r*F1+P2]
        coeff=[[S.factor((1-theta)*a+theta*b) for a,b in zip(uniform,focused)] for theta in (lo,hi)]
        assert r>0 and all(a[0]>0 and a[2]>0 for a in coeff)
        stationary=[roots([a[1]-r*a[0],2*a[2],r*a[2]]) for a in coeff]
        endpoints=[]
        for a,rs in zip(coeff,stationary):
            ts=[S.Integer(0)]+rs['positive']
            values=[value(a,r,t) for t in ts];best=minimum(values)
            endpoints.append({'strengths':[t for t,f in zip(ts,values) if compare(f,best)==0],'objective':best})
        classes.append({'edge':edge,'r':r,'coefficients':coeff,'uniform_coefficients':uniform,'focus_coefficients':focused,'stationary':stationary,'endpoint_minima':endpoints,'curvature_numerators':[2*(a[2]-r*a[1]+r*r*a[0]) for a in coeff]})
    O=[minimum([g['endpoint_minima'][j]['objective'] for g in classes]) for j in (0,1)]
    assert all(compare(o)>0 for o in O)
    oracle=[]
    for j in (0,1):
        actions=[]
        for g in classes:
            if compare(g['endpoint_minima'][j]['objective'],O[j])==0:
                for t in g['endpoint_minima'][j]['strengths']:add_action(actions,g['edge'],t)
        oracle.append(actions)
    for g in classes:
        aa=g['coefficients'];r=g['r']
        cross=[aa[0][k]*O[1]-aa[1][k]*O[0] for k in range(3)]
        balance=roots(cross);g['balance']=balance
        raw=[('boundary',S.Integer(0))]
        for j in (0,1):raw += [('stationary_'+str(j),t) for t in g['stationary'][j]['positive']]
        raw += [('balance',t) for t in balance['positive']]
        entries=[]
        for kind,t in raw:
            old=next((row for row in entries if compare(row['strength'],t)==0),None)
            if old is not None:old['kinds'].append(kind);continue
            objectives=[value(a,r,t) for a in aa];regrets=[f/o-1 for f,o in zip(objectives,O)]
            order=0 if kind=='balance' or balance['case']=='identically_zero' else compare(cross[0]+cross[1]*t+cross[2]*t*t)
            entries.append({'kinds':[kind],'strength':t,'volume':m+t,'objectives':objectives,'regrets':regrets,'worst_regret':regrets[0] if order>=0 else regrets[1]})
        best=minimum([row['worst_regret'] for row in entries]);winners=[row for row in entries if compare(row['worst_regret'],best)==0]
        assert len(winners)==1,'strict quasiconvexity requires unique strength'
        g['candidates']=entries;g['optimum']=winners[0]
    best=minimum([g['optimum']['worst_regret'] for g in classes]);actions=[]
    for g in classes:
        if compare(g['optimum']['worst_regret'],best)==0:add_action(actions,g['edge'],g['optimum']['strength'])
    return {'status':'certified','model':'uniform-source-independent-mixed-target','n':n,'focus':focus,'interval':[lo,hi],'old_volume':m,'edges':[(u,v,w) for (u,v),w in sorted(weights.items())],'allowed':pairs,'oracle_objectives':O,'oracle_actions':oracle,'classes':classes,'global_regret':best,'global_actions':actions}

def value(a,r,t):return (a[0]+a[1]*t+a[2]*t*t)/(1+r*t)

def add_action(actions,edge,t):
    action={'edge':None if compare(t)==0 else edge,'strength':t}
    if action not in actions:actions.append(action)

def roots(coeff):
    c,b,a=map(S.sympify,coeff);allroots=[]
    if compare(a)==0:
        if compare(b)==0:case='identically_zero' if compare(c)==0 else 'constant'
        else:case='linear';allroots=[-c/b]
    else:
        disc=b*b-4*a*c;sign=compare(disc)
        if sign<0:case='quadratic_no_real'
        elif sign==0:case='quadratic_repeated';allroots=[-b/(2*a)]
        else:case='quadratic_two_real';allroots=[(-b-S.sqrt(disc))/(2*a),(-b+S.sqrt(disc))/(2*a)]
    signs=[compare(t) for t in allroots]
    return {'case':case,'coefficients':[c,b,a],'real_roots':allroots,'root_signs':signs,'positive':[t for t,sgn in zip(allroots,signs) if sgn>0]}
