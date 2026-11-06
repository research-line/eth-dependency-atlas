"""Prefilter collision candidates: abstracts with an ETH/#ETH-conditional 2^{o(N)} / 'subexponential' lower bound in a linear size measure.
Heuristic text filter only (recall over precision); classification happens afterwards."""
import json, re, sys
from pathlib import Path

frame = json.load(open(sys.argv[1], encoding="utf-8"))["frame"]
pilot = {w["openalex_id"] for w in json.load(open(sys.argv[2], encoding="utf-8"))["sample"]}
OUT = Path(sys.argv[3])

T = lambda w: (w.get("title") or "") + " " + (w.get("abstract") or "")
# subexponential in a linear measure: 2^{o(n)}, 2^o(n), 2^{o(|V|)}, 2^{o(N)}, 2^{o(m)}, 2^{o(n+m)}, "subexponential time" (unqualified)
lin = re.compile(r"2\s*\^?\s*\{?\s*o\s*\(\s*(n|N|m|\|\s*[VEG]\s*\||\|\s*[a-zA-Z]+\s*\|\s*\+?\s*\|?[a-zA-Z]*\|?|n\s*\+\s*m|v|e|\|x\||size)\s*\)", re.I)
subexp = re.compile(r"sub-?\s?exponential(?:[- ]time)?(?! parameterized)(?! in (the )?(parameter|k\b|treewidth))", re.I)
param = re.compile(r"2\s*\^?\s*\{?\s*o\s*\(\s*(k|tw|\\sqrt|sqrt|√|k\s*\\?log)", re.I)
eth = re.compile(r"\b(#?\s?ETH|exponential[- ]time hypothesis|counting exponential)", re.I)
cand = []
for w in frame:
    t = T(w)
    if not w.get("abstract") or not eth.search(t):
        continue
    hit_lin = bool(lin.search(t)); hit_sub = bool(subexp.search(t)); hit_par = bool(param.search(t))
    counting = bool(re.search(r"#ETH|counting|count the number|#P", t))
    score = 2 * hit_lin + hit_sub + counting - (1 if hit_par and not hit_lin else 0)
    if hit_lin or hit_sub:
        cand.append({"openalex_id": w["openalex_id"], "doi": w.get("doi"), "title": w["title"], "year": w["year"],
                     "in_pilot": w["openalex_id"] in pilot, "lin": hit_lin, "subexp": hit_sub, "param": hit_par,
                     "counting": counting, "score": score, "abstract": w["abstract"], "oa_url": w.get("oa_url")})
cand.sort(key=lambda c: (-c["score"], c["openalex_id"]))
json.dump({"n": len(cand), "candidates": cand}, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("Rahmen mit Abstract:", sum(1 for w in frame if w.get("abstract")), "| Kandidaten:", len(cand),
      "| davon im Pilot:", sum(c["in_pilot"] for c in cand), "| lin:", sum(c["lin"] for c in cand), "| counting:", sum(c["counting"] for c in cand))
for c in cand[:12]:
    print(c["score"], c["in_pilot"], c["year"], c["title"][:90])
