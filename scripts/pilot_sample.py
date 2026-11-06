"""ST2-A03 pilot: fetch the 536-work frame from OpenAlex, reconstruct abstracts, draw a seeded sample of 50."""
import json, random, sys, time, urllib.parse, urllib.request
from pathlib import Path

OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
SEEDS = ["W1985572324", "W1995725694", "W1576180980", "W3044099633", "W2294619171", "W2021372200"]
FILTER = "cites:" + "%7C".join(SEEDS) + ",title_and_abstract.search:" + urllib.parse.quote("exponential time hypothesis")
UA = {"User-Agent": "research-atlas-pilot/1.0"}

def get(url):
    for i in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            last = e; print("retry", i, getattr(e, "code", ""), (e.read()[:200] if hasattr(e, "read") else "")); time.sleep(3 * (i + 1))
    raise last

def abstract(inv):
    if not inv:
        return ""
    pos = sorted((p, w) for w, ps in inv.items() for p in ps)
    return " ".join(w for _, w in pos)

frame, page = [], 1
while True:
    j = get(f"https://api.openalex.org/works?per-page=200&page={page}&filter={FILTER}"
            "&select=id,doi,title,publication_year,type,authorships,abstract_inverted_index,primary_location,open_access,cited_by_count")
    for w in j["results"]:
        frame.append({
            "openalex_id": w["id"].rsplit("/", 1)[-1], "doi": w.get("doi"), "title": w.get("title"),
            "year": w.get("publication_year"), "type": w.get("type"), "cited_by_count": w.get("cited_by_count"),
            "authors": [a["author"]["display_name"] for a in (w.get("authorships") or [])][:6],
            "venue": ((w.get("primary_location") or {}).get("source") or {}).get("display_name"),
            "oa_url": (w.get("open_access") or {}).get("oa_url"),
            "abstract": abstract(w.get("abstract_inverted_index")),
        })
    if len(j["results"]) < 200 or page >= 10:
        break
    page += 1
with_abs = [w for w in frame if len(w["abstract"].split()) >= 30]
rng = random.Random(20261106)
sample = sorted(rng.sample(with_abs, 50), key=lambda w: w["openalex_id"])
for i, w in enumerate(sample, 1):
    w["pilot_id"] = f"P{i:02d}"
meta = {"query_filter": FILTER, "frame_total": len(frame), "frame_with_abstract_ge30_words": len(with_abs),
        "seed": 20261106, "sample_size": len(sample), "date": "2026-11-06"}
json.dump({"meta": meta, "sample": sample}, open(OUT / "sample.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
json.dump({"meta": meta, "frame_ids": [w["openalex_id"] for w in frame]}, open(OUT / "frame_ids.json", "w", encoding="utf-8"), indent=1)
json.dump({"meta": meta, "frame": frame}, open(OUT / "frame_full.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(json.dumps(meta, indent=1))
print("years", sorted(w["year"] for w in sample)[:3], "...", sorted(w["year"] for w in sample)[-3:])
print("types", {t: sum(w["type"] == t for w in sample) for t in set(w["type"] for w in sample)})
