# Collision-candidate run (2026-11-06)

- **Frame:** text prefilter over the 360 works with abstracts (ETH-type hypothesis together with a 2^{o(N)} / subexponential statement in a linear measure): 73 candidates, 12 of them already in the pilot (used for calibration).
- **Classifiers:** Claude Sonnet and Gemini 4 Argon (Medium), brief v2 with a mandatory encoding attempt. Verbatim quotes: 105/105 (A) and 109/109 (G).
- **Agreement:** 80 % exact, κ = 0.607, 89 % coarse.
  - 8 refutations agreed.
  - 9 refutations proposed only by A; the adjudicator accepted them via equivalence theorems and linear encodings.
  - 3 proposed only by G; rejected, because a 2^{n/√log n} algorithm does not beat lower bounds of the form 2^{n^{1−ε}}.
- **Result after adjudication:**
  - 17 works with a directly refuted bound, 14 distinct works after merging versions; two (P07, P45) were already listed.
  - 47 unsupported, 5 not affected, 4 unclear.
  - 1 conditional candidate (C44, range of r).
- **Status:** all refutations are *candidates* (abstract level). Next steps are the full-text check and a review by a further provider. Condition A0 applies throughout.
- **Lesson:** Gemini over-applied "2^{o(n)} exists" to sub-linear-exponent bounds; Claude Sonnet found most of the equivalence-based refutations. Brief v3 should state explicitly that a 2^{o(n)} algorithm refutes only bounds of the form 2^{Ω(n)} or "no 2^{o(n)}".
