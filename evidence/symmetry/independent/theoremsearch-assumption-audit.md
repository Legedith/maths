# Independent audit: TheoremSearch commute-time slogan

Date of live response: 2026-09-08 00:55:25 GMT (HTTP `Date` header).

## Reproduction

Request:

`curl.exe --fail --silent --show-error -X POST 'https://api.theoremsearch.com/search' -H 'Content-Type: application/json' --data-binary '{"query":"effective resistance random walk commute time","n_results":3}'`

The live response returned HTTP 200.  Its third result has slogan ID `5481547`,
theorem ID `20543909`, paper `1807.07167v1`, and Proposition 2.4.  The precise
body is

`E_a[H_z] + E_z[H_a] = R(a <-> z) * sum_{x in V} pi(x)`.

Its separate slogan field says the multiplier is the sum of the "stationary
probabilities" over all vertices.

Raw artifacts:

* `theoremsearch-response.json`, SHA-256
  `f4a22b723d697c7f620e304ca5cead8af300dc893f56ef486c916896517541fe`;
* `theoremsearch-response.headers.txt`, SHA-256
  `fafbf309bb6c04a9f800ba33ad9e72c9d731554e99507b795739856a44dabd2b`.

The TheoremSearch homepage states that each theorem's separate natural-language
"slogan" is model-generated for search.  Thus the defect assessed here belongs
to the generated slogan, not to the retrieved theorem body.

## Original-source check

Daniel Kious, Bruno Schapira, and Arvind Singh, *Once reinforced random walk on
Z x Gamma*, arXiv:1807.07167v1, section 2.2:
https://arxiv.org/html/1807.07167v1

The original defines

`pi(x) := sum_{y adjacent to x} c({x,y})`

and explicitly calls `pi` a reversible **measure**.  It does not call these
values stationary probabilities.  Proposition 2.4 then states the same formula
as the API's precise body.  For a finite network, the normalized stationary
distribution would instead be

`pi_hat(x) = pi(x) / sum_y pi(y)`.

The paper is internally correct: its unnormalized measure supplies the scaling
factor required by the commute-time identity.

## Exact separating witness

Take `K2` with one unit-conductance edge.  The walk crosses the edge at every
step, so

`H(0,1)=1`, `H(1,0)=1`, and commute `C=2`.

The effective resistance is `R=1`.  The paper's measure is
`pi(0)=pi(1)=1`, so `sum pi=2` and `R * sum pi=2`, agreeing with `C`.

The normalized stationary probabilities are `1/2,1/2`, whose sum is `1`.
Reading the slogan conventionally therefore gives `R * 1=1`, contradicting
the exact commute value `2`.  The machine-readable witness is retained in
`theoremsearch-k2-witness.json`.

There is also a general scaling diagnostic: multiplying every conductance by a
positive constant leaves the random walk and normalized stationary
probabilities unchanged but divides effective resistance by that constant.  The
product with the unnormalized reversible measure remains invariant; the product
with normalized probabilities does not.

## Finding and impact

This is a real slogan/body normalization mismatch.  "Stationary probabilities"
normally denotes a probability distribution and therefore sums to one.  A user
who reasons only from the slogan is led to the false identity `commute =
effective resistance`.  The result remains relevant to the search query, and
the API's precise theorem body faithfully matches the source.

Safer slogan wording would be: "The commute time equals the effective
resistance times the total reversible measure, where `pi(x)` is the total
conductance incident to `x`."  For an unweighted graph this total is `2|E|`.

This audit does not allege an error in Proposition 2.4 or in its paper.  It is a
bounded, reproducible data-quality finding in an externally reused service and
an example of why retrieved summaries require source-definition checking.
