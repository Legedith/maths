# Exact all-deletion orbit reduction

Status: candidate proof with independent review pending. Final orbit outcomes are recorded in ledger.json and per-case JSON files; no conclusion is licensed for a failed or uncertified case.

Let a,b,c be integers with 3<=a<=b,c. In G=K_(a,b,c) join K1 fix distinct u,v in A, and let h be the singleton universal vertex. Write r for any member of A except u,v, j for any B vertex, k for any C vertex. Every original edge belongs to exactly one of the nine endpoint categories uB,uC,rB,rC,BC,uh,rh,Bh,Ch, where u represents either u or v. Permuting within parts and swapping u,v takes any edge in a category to its chosen representative and preserves the prospective added edge uv. The B/C relabeling maps uC,rC,Ch to uB,rB,Bh with b and c interchanged. Because the parameter domain constrains b and c identically, six representative formulas cover all nine categories. This is a completeness proof, not a hypothesis of dominance.

For each representative, split out u,v,h and any other deletion endpoints as singleton cells; retain the undistinguished vertices of A,B,C as independent twin cells. Their sizes are a-2 minus 1 if r was split out, b minus 1 if j was split out, and c minus 1 if k was split out. The code constructs the neighbor-count matrix R by complete adjacency between different original parts, removes the representative edge, and adds uv precisely when e=1. Set D=diag(row sums R), L=D-R.

For positive-sized cells the cell-constant subspace is invariant under full P. Every sum-zero vector supported on any residual twin cell is mapped to zero: there are no internal edges, and each external row gives identical coefficients to all its vertices. Together these spaces decompose the full vector space. Hence K(full)=n-m+K(quotient), with m the number of cells, n=a+b+c+1.

Boundary a=3 in cases involving r gives one empty residual A cell. It is retained algebraically in the implemented quotient. Its column in R is zero and its diagonal in R is zero, so the corresponding column in D^{-1}L has diagonal 1 and all other entries zero. Deleting this virtual cell therefore removes exactly one normalized Laplacian eigenvalue 1, equivalently transition eigenvalue 0. Its artificial contribution 1 cancels the use of n-m instead of n-(m-1). Thus the same coefficient formula remains valid also at a=3. The virtual row degree is positive. No other residual cell can be empty in the admitted domain.

Connectedness holds after every single deletion because each deleted edge has an alternative path through a vertex in a third original part. All degrees are positive. Full P is reversible and similar to a real symmetric matrix, with eigenvalue 1 simple. The nontrivial normalized Laplacian eigenvalues are positive. The genuine quotient inherits this spectrum; virtual cells add positive eigenvalue 1. Accordingly, if q_e1 and q_e2 are coefficients of t and t^2 in det(L_e+tD_e), then K(full,e)=n-m+q_e2/q_e1. These coefficients are computed by finite principal-minor sums from determinant multilinearity:

q_ek=sum_{|S|=k} (product_{i in S} D_e[i,i]) det L_e[S-complement,S-complement], k=1,2.

The rational difference is canceled exactly to N/D. Each per-case certificate expands -N and D after a=3+x,b=3+x+y,c=3+x+z. If every listed nonzero coefficient is positive and each constant coefficient is positive, then -N>0 and D>0 for all x,y,z>=0. This proves strict Delta<0 for that entire orbit domain, rather than extrapolating finite tests.

The prior uh special case was already proved in a separate frozen packet; the present run recomputes it for consistency. The other five representative formulas constitute new work. Novelty, practical impact, and any strongest-deletion ordering remain unassessed.
