"""Exact rational-graph strength minimax with certified, bounded comparisons."""
from functools import lru_cache
from fractions import Fraction
from math import isqrt
import sympy as S

class InconclusiveError(RuntimeError):
    """An algebraic comparison was not certified within this implementation."""

def rational(value):
    if isinstance(value,(float,bool)) or isinstance(value,S.Float):
        raise ValueError('use exact rational values, not floats or booleans')
    try: q=S.Rational(value)
    except (TypeError,ValueError): raise ValueError('expected exact rational value') from None
    return q

@lru_cache(maxsize=50000)
def enclosure(expr,bits=160):
    """Closed rational bounds; no floating-point comparison."""
    expr=S.sympify(expr)
    if expr.is_Rational:
        q=Fraction(int(expr.p),int(expr.q));return q,q
    if expr.is_Add:
        bounds=[enclosure(a,bits) for a in expr.args]
        return sum(a for a,_ in bounds),sum(b for _,b in bounds)
    if expr.is_Mul:
        lo=hi=Fraction(1)
        for a in expr.args:
            left,right=enclosure(a,bits)
            vals=(lo*left,lo*right,hi*left,hi*right);lo,hi=min(vals),max(vals)
        return lo,hi
    if expr.is_Pow:
        lo,hi=enclosure(expr.base,bits);power=expr.exp
        if power==S.Rational(1,2):
            if lo<0:raise InconclusiveError('square-root interval reaches negative values')
            scale=1<<bits
            def root(q):
                k=isqrt((q.numerator*scale*scale)//q.denominator)
                return Fraction(k,scale),Fraction(k+1,scale)
            return root(lo)[0],root(hi)[1]
        if power.is_Integer:
            k=int(power)
            if k<0:
                if lo<=0<=hi:raise InconclusiveError('division interval contains zero')
                lo,hi=1/hi,1/lo;k=-k
            if k==0:return Fraction(1),Fraction(1)
            vals=(lo**k,hi**k)
            return (Fraction(0) if lo<=0<=hi and k%2==0 else min(vals)),max(vals)
    raise InconclusiveError('unsupported algebraic interval expression')

def compare(a,b=0):
    """Return exact -1/0/1, or raise; never guess from an epsilon."""
    delta=S.sympify(a)-S.sympify(b)
    if delta==0:return 0
    for bits in (80,160,320):
        try:lo,hi=enclosure(delta,bits)
        except InconclusiveError:continue
        if lo>0:return 1
        if hi<0:return -1
    # Only an exact zero identity may turn overlapping intervals into equality.
    reduced=S.simplify(delta)
    if reduced==0:return 0
    try:lo,hi=enclosure(reduced,320)
    except InconclusiveError as exc:raise InconclusiveError('comparison not certified') from exc
    if lo>0:return 1
    if hi<0:return -1
    raise InconclusiveError('comparison not certified at 320-bit rational enclosure')

def minimum(values):
    best=values[0]
    for value in values[1:]:
        if compare(value,best)<0:best=value
    return best

def maximum(values):return -minimum([-v for v in values])

def balance_candidate(T,B,O):
    """Classify equality of (T0+B0*t)/O0 and (T1+B1*t)/O1."""
    numerator=T[1]*O[0]-T[0]*O[1];denominator=B[0]*O[1]-B[1]*O[0]
    if compare(denominator)==0:
        return ('coincident' if compare(numerator)==0 else 'parallel_no_crossing'),None
    t=numerator/denominator;sgn=compare(t)
    return ('positive' if sgn>0 else 'zero' if sgn==0 else 'negative'),t

def _endpoint_min(m,r,T,s):
    B=r*T-s;A=T-m*s
    assert B>0 and s>0
    if A>=0:return S.Integer(0),m*T
    rad=s*(m*r-1)/B
    assert rad>1
    star=(S.sqrt(rad)-1)/r
    value=(B*(m*r-1)+s+2*S.sqrt(B*s*(m*r-1)))/r**2
    return star,value

def solve(n,edges,focus,interval,allowed):
    """Solve a fixed graph with rational weights/endpoints.

    edges: (u,v,weight), parallel entries are summed. allowed: absent pairs.
    Returns exact SymPy expressions; serialize with encode_certificate.
    InconclusiveError is a comparison limitation, never a recommendation.
    """
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
    m=sum(weights.values());T=[S.trace(M)+n*q*M[focus,focus] for q in (lo,hi)]
    groups={}
    for edge in pairs:
        u,v=edge;z=M*(eye[:,u]-eye[:,v]);r=z[u]-z[v]
        ss=tuple((z.T*z)[0]+n*q*z[focus]**2 for q in (lo,hi))
        assert r>0 and m*r>=4 and all(s>0 and r*t-s>0 for s,t in zip(ss,T))
        groups.setdefault((r,*ss),[]).append(edge)
    classes=[]
    for (r,s0,s1),locations in groups.items():
        ss=[s0,s1];mins=[_endpoint_min(m,r,t,s) for t,s in zip(T,ss)]
        classes.append({'edges':locations,'r':r,'s_endpoints':ss,'B_endpoints':[r*t-s for t,s in zip(T,ss)],'A_endpoints':[t-m*s for t,s in zip(T,ss)],'endpoint_stationary_strengths':[a for a,_ in mins],'endpoint_minima_f':[b for _,b in mins]})
    O=[minimum([g['endpoint_minima_f'][j] for g in classes]) for j in (0,1)]
    assert all(compare(o)>0 for o in O)
    oracle_actions=[]
    for j in (0,1):
        actions=[];noop=False
        for g in classes:
            if compare(g['endpoint_minima_f'][j],O[j])==0:
                t=g['endpoint_stationary_strengths'][j]
                if compare(t)==0:noop=True
                else:actions.extend({'edge':e,'strength':t} for e in g['edges'])
        oracle_actions.append(([{'edge':None,'strength':S.Integer(0)}] if noop else [])+actions)
    for g in classes:
        r=g['r'];B0,B1=g['B_endpoints']
        raw=[('zero',S.Integer(0))]+[(name,t) for name,t in zip(('left_stationary','right_stationary'),g['endpoint_stationary_strengths']) if compare(t)>0]
        kind,balance=balance_candidate(T,[B0,B1],O);g['balance_case']=kind
        if kind=='positive':raw.append(('balance',balance))
        entries=[]
        for name,t in raw:
            same=next((row for row in entries if compare(t,row['strength'])==0),None)
            if same is not None:same['kinds'].append(name);continue
            f=[(m+t)*(tt-t*s/(1+r*t)) for tt,s in zip(T,g['s_endpoints'])]
            regrets=[value/o-1 for value,o in zip(f,O)]
            entries.append({'kinds':[name],'strength':t,'volume':m+t,'endpoint_f':f,'actual_endpoint_objectives':[2*(1-q)*value/n for q,value in zip((lo,hi),f)],'endpoint_regrets':regrets,'worst_relative_regret':maximum(regrets)})
        best=minimum([row['worst_relative_regret'] for row in entries])
        winners=[row for row in entries if compare(row['worst_relative_regret'],best)==0]
        assert len(winners)==1,'strict convexity requires one distinct minimizing strength'
        g['candidates']=entries;g['optimum']=winners[0]
    best=minimum([g['optimum']['worst_relative_regret'] for g in classes])
    actions=[];noop=False
    for g in classes:
        if compare(g['optimum']['worst_relative_regret'],best)==0:
            t=g['optimum']['strength']
            if compare(t)==0:noop=True
            else:actions.extend({'edge':e,'strength':t} for e in g['edges'])
    return {'status':'certified','n':n,'focus':focus,'interval':[lo,hi],'old_volume':m,'merged_edges':[(u,v,w) for (u,v),w in sorted(weights.items())],'allowed_edges':pairs,'T_endpoints':T,'oracle_endpoint_f':O,'oracle_actual_endpoint_objectives':[2*(1-q)*o/n for q,o in zip((lo,hi),O)],'oracle_actions':oracle_actions,'classes':classes,'global_minimax_relative_regret':best,'global_actions':([{'edge':None,'strength':S.Integer(0)}] if noop else [])+actions}

def encode_certificate(value):
    if isinstance(value,S.Basic):
        lo,hi=enclosure(value)
        return {'exact':str(value),'rational_bounds':[str(lo),str(hi)]}
    if isinstance(value,dict):return {k:encode_certificate(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)):return [encode_certificate(v) for v in value]
    return value
