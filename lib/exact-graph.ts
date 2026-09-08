// Browser implementation of the bounded baseline, using exact BigInt fractions.
// It deliberately keeps tree enumeration separate from the electrical solve.
type Q = readonly [bigint, bigint];
const abs = (a: bigint) => (a < 0n ? -a : a);
function q(a: bigint | number, b: bigint = 1n): Q {
  let x = BigInt(a),
    y = b;
  if (y === 0n) throw new Error('Division by zero');
  if (y < 0n) {
    x = -x;
    y = -y;
  }
  let u = abs(x),
    v = y;
  while (v) {
    const r = u % v;
    u = v;
    v = r;
  }
  return [x / u, y / u];
}
const add = (a: Q, b: Q) => q(a[0] * b[1] + b[0] * a[1], a[1] * b[1]);
const sub = (a: Q, b: Q) => q(a[0] * b[1] - b[0] * a[1], a[1] * b[1]);
const mul = (a: Q, b: Q) => q(a[0] * b[0], a[1] * b[1]);
const div = (a: Q, b: Q) => q(a[0] * b[1], a[1] * b[0]);
const str = (a: Q) => (a[1] === 1n ? `${a[0]}` : `${a[0]}/${a[1]}`);
function solve(matrix: Q[][], rhs: Q[]): Q[] {
  const a = matrix.map((row, i) => [...row, rhs[i]]);
  for (let k = 0; k < a.length; k++) {
    const pivot = a.findIndex((row, i) => i >= k && row[k][0] !== 0n);
    if (pivot < 0) throw new Error('Singular system');
    [a[k], a[pivot]] = [a[pivot], a[k]];
    const p = a[k][k];
    a[k] = a[k].map((x) => div(x, p));
    for (let i = 0; i < a.length; i++)
      if (i !== k) {
        const factor = a[i][k];
        a[i] = a[i].map((x, j) => sub(x, mul(factor, a[k][j])));
      }
  }
  return a.map((row) => row[a.length]);
}
export type GraphInput = {
  n: number;
  edges: [number, number][];
  source: number;
  target: number;
};
function connected(n: number, edges: [number, number][]) {
  const seen = new Set([0]);
  let changed = true;
  while (changed) {
    changed = false;
    for (const [u, v] of edges)
      if (seen.has(u) !== seen.has(v)) {
        seen.add(u);
        seen.add(v);
        changed = true;
      }
  }
  return seen.size === n;
}
export function validateGraph(input: unknown): GraphInput {
  if (!input || typeof input !== 'object' || Array.isArray(input))
    throw new Error('Enter a graph object.');
  const p = input as Record<string, unknown>;
  if (Object.keys(p).sort().join(',') !== 'edges,n,source,target')
    throw new Error(
      'Use exactly n, edges, source and target. Weighted or directed graphs are outside this lab.',
    );
  if (typeof p.n !== 'number' || !Number.isInteger(p.n) || p.n < 2 || p.n > 6)
    throw new Error('Use 2 to 6 vertices.');
  const n = p.n;
  const vertex = (v: unknown): v is number =>
    typeof v === 'number' && Number.isInteger(v) && v >= 0 && v < n;
  if (!vertex(p.source) || !vertex(p.target) || p.source === p.target)
    throw new Error(
      `Choose distinct source and target vertices in 0..${n - 1}.`,
    );
  if (!Array.isArray(p.edges))
    throw new Error('Edges must be an array of vertex pairs.');
  const seen = new Set<string>();
  const edges: [number, number][] = p.edges
    .map((edge: unknown) => {
      if (
        !Array.isArray(edge) ||
        edge.length !== 2 ||
        !vertex(edge[0]) ||
        !vertex(edge[1]) ||
        edge[0] === edge[1]
      )
        throw new Error(
          'Every edge must join two distinct integer vertices. No weights or self-loops.',
        );
      const pair: [number, number] = [Math.min(...edge), Math.max(...edge)];
      if (seen.has(pair.join(',')))
        throw new Error('An undirected edge appears twice.');
      seen.add(pair.join(','));
      return pair;
    })
    .sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  if (!connected(n, edges))
    throw new Error(
      'The graph must be connected. Add edges joining the separate components.',
    );
  return { n, edges, source: p.source, target: p.target };
}
export function analyzeGraph(input: unknown) {
  const { n, edges, source, target } = validateGraph(input);
  const L = Array.from({ length: n }, () => Array<number>(n).fill(0));
  const neighbors = Array.from({ length: n }, () => [] as number[]);
  for (const [u, v] of edges) {
    L[u][u]++;
    L[v][v]++;
    L[u][v]--;
    L[v][u]--;
    neighbors[u].push(v);
    neighbors[v].push(u);
  }
  const keep = Array.from({ length: n }, (_, i) => i).filter(
    (i) => i !== target,
  );
  const voltage = solve(
    keep.map((i) => keep.map((j) => q(L[i][j]))),
    keep.map((i) => q(i === source ? 1 : 0)),
  );
  const potentials = Array<Q>(n).fill(q(0));
  keep.forEach((v, i) => {
    potentials[v] = voltage[i];
  });
  const resistance = potentials[source];
  function hit(start: number, stop: number) {
    const vertices = Array.from({ length: n }, (_, i) => i).filter(
      (i) => i !== stop,
    );
    // Independent first-step Markov equations, with a shared generic solver.
    const matrix = vertices.map((i) =>
      vertices.map((j) =>
        sub(
          q(i === j ? 1 : 0),
          neighbors[i].includes(j) ? q(1n, BigInt(neighbors[i].length)) : q(0),
        ),
      ),
    );
    return solve(
      matrix,
      vertices.map(() => q(1)),
    )[vertices.indexOf(start)];
  }
  const forward = hit(source, target),
    backward = hit(target, source),
    commute = add(forward, backward);
  const selected = edges.findIndex(
    ([u, v]) =>
      u === Math.min(source, target) && v === Math.max(source, target),
  );
  let treeCount = 0,
    edgeCount = 0;
  function enumerate(at: number, chosen: number[]) {
    if (chosen.length === n - 1) {
      if (
        connected(
          n,
          chosen.map((i) => edges[i]),
        )
      ) {
        treeCount++;
        if (chosen.includes(selected)) edgeCount++;
      }
      return;
    }
    if (at >= edges.length || chosen.length + edges.length - at < n - 1) return;
    enumerate(at + 1, [...chosen, at]);
    enumerate(at + 1, chosen);
  }
  enumerate(0, []);
  const probability =
    selected < 0 ? null : q(BigInt(edgeCount), BigInt(treeCount));
  const checks: Record<string, boolean> = {
    laplacian_row_sums_zero: L.every(
      (row) => row.reduce((a, b) => a + b, 0) === 0,
    ),
    commute_equals_2m_resistance:
      str(commute) === str(mul(q(2 * edges.length), resistance)),
    spanning_tree_count_positive: treeCount > 0,
  };
  if (probability)
    checks.edge_probability_equals_resistance =
      str(probability) === str(resistance);
  if (!Object.values(checks).every(Boolean))
    throw new Error(
      'An exact cross-check failed. This result cannot be promoted.',
    );
  return {
    n,
    edges,
    source,
    target,
    laplacian: L,
    potentials: potentials.map(str),
    resistance: str(resistance),
    hit_forward: str(forward),
    hit_backward: str(backward),
    commute: str(commute),
    spanning_tree_count: treeCount,
    tree_edge_count: selected < 0 ? null : edgeCount,
    edge_probability: probability ? str(probability) : null,
    checks,
  };
}
export type GraphResult = ReturnType<typeof analyzeGraph>;
