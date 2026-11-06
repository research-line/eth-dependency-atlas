# Scripts

All scripts are standard-library Python 3 (no third-party packages) and take their input/output paths as arguments.

| Script | Purpose |
|---|---|
| `verify_refs.py <out.json>` | Checks reference metadata against Crossref/arXiv/OpenAlex and counts the citation graph of the seed papers |
| `pilot_sample.py <outdir>` | Fetches the OpenAlex frame (cites a seed paper and mentions ETH in title/abstract), reconstructs abstracts **locally**, draws the seeded sample (seed 20261106) |
| `collision_prefilter.py <frame_full.json> <sample.json> <out.json>` | Text prefilter for collision candidates (2^{o(N)} / subexponential claims in a linear measure) |
| `pilot_merge.py <dir> A=<file> G=<file> …` | Schema check, verbatim-quote check against the abstracts, paper-level class, pairwise Cohen's κ |
| `pilot_final.py <dir>` | Applies the documented adjudication and writes the paper-level CSV |
| `atlas_seed.py <out.csv>` | Writes the secondary seed rows taken from the OpenAI paper's related-work section |

Abstracts are **not** part of this repository (third-party copyright); the scripts re-create them locally from OpenAlex. OpenAlex cursor paging now requires an API key, so `pilot_sample.py` uses page-based paging.
