# Method (v0.1)

1. **Frame.** Works citing at least one seed paper ([IP01], [IPZ01], [CIP09], [DHMTW14], [CCK20], [CGIMPS16]; verified via Crossref/arXiv) and mentioning "exponential time hypothesis" in title or abstract (OpenAlex, 2026-11-06): 536 works, 360 with a usable abstract.
2. **Classification.** Two classifiers from **different providers** receive the identical brief (`BRIEF_v1_pilot.md`, `BRIEF_v2.md`) and work from title and abstract only. Every claim must carry a verbatim quote; quotes are checked by machine against the abstract.
3. **Adjudication.** Disagreements and every `FALSCH` (directly refuted) are decided by an adjudicator with a written argument (encoding into fixed-width k-CNF with O(N) variables, or a source statement). Adjudicated collisions remain *candidates* until checked against the full text and reviewed by a further provider.
4. **Semantics.** A conditional result "no 2^{o(N)} algorithm unless ETH fails" stays formally true. *Refuted* means that the lower bound it expresses no longer holds, because an algorithm of that speed exists. *Unsupported* means that the hypothesis is gone, so the bound is neither proven nor refuted.
5. **Products.** `data/collisions.csv` (refuted bounds), `data/rescues.csv` (bounds that still follow from a non-refuted hypothesis), and `data/raw/` (flat machine classification, low depth, for orientation only).

**Condition A0.** Everything here assumes that the reported refutations are correct. They have not been independently confirmed (as of 2026-11-06).
