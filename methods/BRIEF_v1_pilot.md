# Classification brief — ETH dependency atlas, pilot (50 papers)

You classify 50 research papers by whether their **own** results depend on complexity hypotheses that were recently reported as refuted. You work **only** from the title/abstract given in `pilot_input.json` and the facts below. Do **not** browse the web, do **not** use other files, do **not** invent content. Do **not** run git or any shell command that changes files, except writing the single output file named in your task.

## A0 — facts you must assume as true (reported Oct 2026, not yet independently verified)

**Refuted hypotheses:** ETH, randomized ETH, SETH, randomized SETH, Gap-ETH (deterministic and randomized), NSETH, #ETH (counting ETH); the 3SUM hypothesis (integer and real), the APSP hypothesis (integer and real), the Exact-Triangle hypothesis, the Zero-Weight k-Clique hypotheses, and the three rectangular hinted Online Matrix–Vector conjectures of van den Brand–Nanongkai–Saranurak. (MA-SETH was refuted earlier by Williams 2016.)

**NOT refuted (treat as still standing):** P ≠ NP, NP ≠ coNP, the Orthogonal Vectors Conjecture (OVC), the hypothesis "CNF-SAT with unbounded clause width has no 2^((1−δ)n)·poly(n,m) algorithm" (call it **CNF-SAT-H**), W[1] ≠ FPT, the Set Cover Conjecture, the Unique Games Conjecture, and any hypothesis not listed as refuted.

**New algorithms behind the refutations (the only sources of direct collisions):**
1. Deterministic exact counting of satisfying assignments of k-CNF (fixed k) in 2^(O(n·loglog n/√log n))·poly(n,m) time and polynomial space; for m ≤ D·n clauses in 2^(O(n/√log n)).
2. Counting independent sets and proper q-colourings of a v-vertex graph in 2^(o(v)); counting perfect matchings in 2^(o(v+e)).
3. Independent Set, Clique, Vertex Cover and Dominating Set on n-vertex graphs in O(2^(εn)) for every ε > 0.
4. 3SUM on n integers of polynomial size in O(n^1.9992); APSP with polynomially bounded integer weights in O(n^2.9995); consequences for (min,+)-product, Exact Triangle and Zero-Weight k-Clique.

**Transfer rule (important):** 2^(o(n)) running times do **not** transfer through general polynomial-time reductions. A lower bound "no 2^(o(N)) algorithm for X unless ETH fails" becomes **directly false** only if X is in the list above, or X reduces to fixed-width k-SAT (or #k-SAT) with O(N) variables, or the paper itself states an equivalence ("X in 2^(o(N)) iff ETH fails"). Lower bounds of other shapes, e.g. 2^(o(√n)), n^(o(k)), f(k)·n^(o(k)), 2^(o(tw)), 2^(o(k log k)), n^(2−ε), are normally only **unsupported**: the refutation does not by itself give matching algorithms. For APSP: if X is proven *subcubic-equivalent* to APSP, then "X has no truly subcubic algorithm" is now **false**; the equivalence theorem itself remains true.

**Known rescues (from the refutation papers):** the SETH lower bounds for Longest Common Subsequence and regular-expression matching also follow from OVC. Those for Fréchet distance, graph-diameter approximation and the treewidth dependence of Independent Set / Dominating Set also follow from CNF-SAT-H. Claim a rescue only if it is in this list **or** the abstract itself names a non-refuted source (e.g. "reduction from Orthogonal Vectors").

## Classes (one per conditional claim)

- `UNBERUEHRT` — the claim does not rely on a refuted hypothesis (e.g. it relies on P≠NP, W[1]≠FPT, OVC, or it is unconditional; or the paper only mentions ETH as context).
- `FALSCH` — the claim now directly contradicts one of the new algorithms (per the transfer rule).
- `UNGESTUETZT-RETTBAR` — relies on a refuted hypothesis, but a listed/stated non-refuted hypothesis yields the same claim.
- `UNGESTUETZT-OFFEN` — relies on a refuted hypothesis, no rescue known from the given information.
- `UNKLAR_ABSTRACT` — the abstract does not allow a decision (full text needed).

Fix types for `UNGESTUETZT-*`: `rebase` (other hypothesis), `weaken` (weaker quantitative statement under a successor hypothesis such as "3-SAT needs 2^(n/polylog n)"), `restrict` (narrow the scope), `none`. Fixes are **candidates only**.

## Output — write exactly one JSON file (UTF-8), nothing else

```json
{
  "classifier": "<your model name>",
  "papers": [
    {
      "pilot_id": "P01",
      "evidence_level": "abstract" | "fulltext_needed",
      "has_own_conditional_result": "yes" | "no" | "unclear",
      "claims": [
        {
          "quote": "<verbatim, character-exact substring of the abstract that states the conditional claim; empty string if none>",
          "hypothesis": ["ETH" | "rETH" | "SETH" | "rSETH" | "Gap-ETH" | "NSETH" | "#ETH" | "3SUM" | "APSP" | "ExactTriangle" | "ZeroKClique" | "OMv-hinted" | "other-not-refuted" | "none"],
          "result_type": "lower_bound" | "hardness_of_approx" | "fine_grained_reduction" | "crypto_assumption" | "algorithm_or_tightness" | "other",
          "class": "UNBERUEHRT" | "FALSCH" | "UNGESTUETZT-RETTBAR" | "UNGESTUETZT-OFFEN" | "UNKLAR_ABSTRACT",
          "class_reason": "<one or two sentences, referring to the transfer rule / list item used>",
          "fix_type": "rebase" | "weaken" | "restrict" | "none",
          "fix_candidate": "<short text or empty>",
          "rescue_hypothesis": "<e.g. OVC, CNF-SAT-H, or empty>"
        }
      ],
      "confidence": "high" | "medium" | "low"
    }
  ]
}
```

Rules: every one of the 50 `pilot_id`s appears exactly once, in order. The `quote` must be copied exactly from the abstract; it is checked by machine, and invented quotes invalidate the entry. Prefer `UNKLAR_ABSTRACT` over guessing.
