# First region: Laplacians and networks

The enduring goal is an expanding map of mathematics and cross-domain knowledge. This first region is a foundation, not completion of that goal.

Three independent read-only proposals were compared under the same task specification: binary energies and graph cuts; Laplacians and electrical networks; and convex duality and allocation. All had strong primary sources and tractable exact finite tests. No artificial numerical ranking is claimed.

Laplacians were selected for the first region because one object yields explicit bridges among linear algebra, electrical physics, random walks, spanning trees, graph algorithms, image analysis, and resistance-based chemical graph descriptors. A small graph can be analysed by exact circuit equations, independently constructed Markov first-step equations, and a combinatorial spanning-tree enumeration oracle. These offer both accessible explanations and falsifiable implementation checks.

The alternatives are retained as expansion directions: binary energies add a condition-checked min-cut compiler; allocation and duality add economics, optimal transport and matching. They have not yet been implemented or certified.

The selected runtime contract initially covers connected simple undirected unweighted graphs with two to six vertices. Source-backed mathematical nodes can describe broader weighted results, but the UI and engine must expose the narrower runtime scope. Connections to chemistry and image analysis are modelling/application relations, not guarantees about chemical properties or segmentation accuracy. A missing entry is a corpus gap, never evidence that mathematics is unsolved.

The original workspace had almost no free space on C:. Project source and dependencies now live on D:, with a directory junction at the original workspace path. All new Python work uses uv and a D: cache/environment. Earlier failed npm installation artifacts are preserved outside this Git repository.
