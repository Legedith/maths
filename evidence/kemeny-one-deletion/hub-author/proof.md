# Universal sign certificate for the specified deletion

Status: author-produced exact certificate; independent semantic verification required before promotion.

For integers 3<=a<=b,c, let H=(K_(a,b,c) join K_1)-uh, with u,v in the a-part and h universal before deletion. Then K(H+uv)-K(H)<0. This conclusion concerns only this specified deletion and addition. It implies neither worst-deletion dominance nor robustness for other deletion types. Publication novelty and practical impact have not been assessed.

## Exact reduction
Order cells as {u},{v},A-rest,B,C,{h}; their sizes are (1,1,a-2,b,c,1). Let e=0 for H and e=1 for H+uv. The neighbor-count matrix is

    0   e   0     b c 0
    e   0   0     b c 1
    0   0   0     b c 1
    1   1   a-2   0 c 1
    1   1   a-2   b 0 1
    0   1   a-2   b c 0

Call it R_e, let D_e be the diagonal of its row sums and L_e=D_e-R_e. The six-cell transition matrix is Q_e=D_e^{-1}R_e. Cell-constant vectors form an invariant subspace of the full transition matrix. For each of the three nonsingleton cells, vectors supported there with coordinate sum zero are mapped to zero: there are no within-cell edges, all vertices outside the cell see either every vertex of it or none, and each outside transition row is constant on that cell. These subspaces and the cell-constant subspace are a direct sum of the full vertex space. Hence the omitted transition eigenvalues are exactly n-6 zeros, where n=a+b+c+1; each contributes 1 to stationary-target Kemeny K. Their contribution cancels in Delta. This argument also covers a=3, when A-rest is a singleton and its zero-mode space has dimension zero.

The graph is connected and undirected. Its transition operator is similar to a real symmetric matrix; its eigenvalue 1 is simple and all other eigenvalues are less than 1. The quotient inherits these properties via its invariant subspace. Write F_e(t)=det(L_e+tD_e). If q_e1=[t]F_e and q_e2=[t^2]F_e, its factorization into normalized Laplacian eigenvalues gives q_e2/q_e1=sum_{i=2}^6 1/(1-lambda_i(Q_e)). Therefore K_e=n-6+q_e2/q_e1 and Delta=N/(q_11*q_01), where N=q_12*q_01-q_02*q_11. Both denominator factors are strictly positive by the eigenvalue factorization and positive determinant D_e.

For an independently reproducible definition of the four coefficients, for k=1,2 use

    q_ek = sum_{S subset {0,...,5}, |S|=k} (product_{i in S} D_e[i,i]) det L_e[S-complement,S-complement].

This follows by determinant multilinearity in the diagonal t entries. batch1.py performs exactly these finite minor sums over the integers a,b,c. symbolic.json stores all four coefficient polynomials, N, and a full coefficient-list certificate.

## Sign certificate
Set a=3+x, b=3+x+y, c=3+x+z. The allowed domain gives x,y,z>=0. Exact expansion of -N after this substitution has 284 nonzero monomials, all with strictly positive integer coefficients; its smallest coefficient is 6, constant coefficient is 1784916000, and total degree is 10. The complete list is symbolic.json:negative_N_shift_terms, with each entry [[power_x,power_y,power_z],coefficient]. Thus -N>=1784916000>0 throughout the whole domain. Together with the positive denominator this proves strict negative Delta. The certificate even proves the rational quotient inequality on the corresponding continuous real domain; only integer sizes are interpreted as graphs.

batch2.py reconstitutes the stored list and checks its exact identity with the stored N after substitution, and checks every coefficient is positive. Its full-matrix construction is independent of the quotient adjacency construction: it assigns vertices to parts, adds every cross-part edge, removes uh, and optionally adds uv. It evaluates K=trace((I-P+1*pi)^(-1))-1 using exact rational matrices. All six graph checks agree with quotient K plus n-6. The three exact differences are:

- (3,3,3): -787/41664
- (3,4,5): -89013391/6289074792
- (4,4,6): -3360439/385735350

These finite checks validate the implementation on declared instances; the coefficient certificate supplies the full-domain sign argument.

## Reproduction and limits
Use uv with UV_CACHE_DIR set inside this stage and .venv/Scripts/python.exe (Python 3.13.7, SymPy 1.14.0, mpmath 1.3.0). Commands/ranges were frozen in plan.md and batch2-plan.md. Both executed batches ended with exit code 0 (batch1.rc, batch2.rc). Raw stdout/stderr are batch1.log and batch2.log. The uv --no-project warning is retained and is not a mathematical or execution failure. No symbolic retries, additional parameter sweep, or third batch occurred. Independent review must rerun or inspect these artifacts and cannot be replaced by this author's assertions.
