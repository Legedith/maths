import sympy as S,json
from pathlib import Path
a=S.symbols('a',positive=True);n=3*a+1;d=2*a+1;m=3*a*a+3*a-1;k=(n-1)*(d-1)/(n*d);W=(n*(n-1)+d*(d-1))/(n*n*d*d);R=W/k;Z=d*(d+2)*k+1;U=(2*k+2/d+R)/Z;T=3*(a-1)/d+3/n+R;hh=(n-1)/n**2+1/(n*n*k);tau=(a-2)*(10*a*a+a-1)/((2*a+1)**2*(2*a+3)*(3*a+1))
# n times improvement after removing2(1-theta)
FR0=(m+1)*R-T;FRs=(m+1)/(n*k)-n*hh;FU0=(m+1)*U-T;FUs=(m+1)/(n*k*Z)-n*hh
cross=S.factor(FR0+tau*FRs);assert S.factor(cross-(FU0+tau*FUs))==0
result={'equal_switch_margin':str(cross),'restore_intercept':str(S.factor(FR0)),'restore_slope':str(S.factor(FRs)),'uv_intercept':str(S.factor(FU0)),'uv_slope':str(S.factor(FUs)),'restore_zero':str(S.factor(-FR0/FRs)),'uv_zero':str(S.factor(-FU0/FUs))}
Path(__file__).with_name('batch2.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
