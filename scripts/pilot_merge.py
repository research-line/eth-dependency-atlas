"""Merge and audit the two pilot classifications: schema check, verbatim-quote check, paper-level class, agreement (Cohen's kappa)."""
import json, re, sys
from collections import Counter
from pathlib import Path

D = Path(sys.argv[1])
inp = {p["pilot_id"]: p for p in json.load(open(D / "pilot_input.json", encoding="utf-8"))["papers"]}
CLASSES = ["UNBERUEHRT", "FALSCH", "UNGESTUETZT-RETTBAR", "UNGESTUETZT-OFFEN", "UNKLAR_ABSTRACT"]
SEVERITY = {"FALSCH": 4, "UNGESTUETZT-OFFEN": 3, "UNGESTUETZT-RETTBAR": 2, "UNKLAR_ABSTRACT": 1, "UNBERUEHRT": 0}
norm = lambda s: re.sub(r"\s+", " ", (s or "")).strip().lower()

def load(path):
    d = json.load(open(path, encoding="utf-8"))
    return d.get("classifier", "?"), {p["pilot_id"]: p for p in d["papers"]}

def audit(name, papers):
    issues, quotes_total, quotes_ok, cls = [], 0, 0, {}
    missing = sorted(set(inp) - set(papers)); extra = sorted(set(papers) - set(inp))
    for pid, p in papers.items():
        claims = p.get("claims") or []
        ab = norm(inp.get(pid, {}).get("abstract", ""))
        sev = []
        for c in claims:
            if c.get("class") not in CLASSES:
                issues.append(f"{pid}: unbekannte Klasse {c.get('class')}")
                continue
            q = norm(c.get("quote"))
            if q:
                quotes_total += 1
                if q in ab:
                    quotes_ok += 1
                else:
                    issues.append(f"{pid}: Zitat nicht im Abstract: {c.get('quote')[:80]!r}")
            sev.append(c["class"])
        # paper-level class = most severe claim class; no claims -> UNBERUEHRT if no own result, else UNKLAR
        if sev:
            cls[pid] = max(sev, key=SEVERITY.get)
        else:
            cls[pid] = "UNBERUEHRT" if p.get("has_own_conditional_result") == "no" else "UNKLAR_ABSTRACT"
    return {"name": name, "missing": missing, "extra": extra, "quotes_total": quotes_total, "quotes_ok": quotes_ok,
            "issues": issues, "paper_class": cls, "dist": Counter(cls.values()),
            "fulltext_needed": sum(p.get("evidence_level") == "fulltext_needed" for p in papers.values())}

def kappa(a, b, keys):
    n = len(keys)
    po = sum(a[k] == b[k] for k in keys) / n
    ca, cb = Counter(a[k] for k in keys), Counter(b[k] for k in keys)
    pe = sum(ca[c] * cb[c] for c in CLASSES) / n ** 2
    return po, (po - pe) / (1 - pe) if pe < 1 else 1.0

# usage: pilot_merge.py <pilotdir> <label=relpath> ...   (first two labels = primary pair)
specs = [a.split("=", 1) for a in sys.argv[2:]] or [["A", "a_out/classifier_a.json"], ["B", "b_out/classifier_b.json"]]
res = {}
for label, rel in specs:
    name, papers = load(D / rel)
    res[label] = audit(f"{label} ({name})", papers)
coarse = lambda c: "betroffen" if c in ("FALSCH", "UNGESTUETZT-OFFEN", "UNGESTUETZT-RETTBAR") else c
pairs = {}
labels = [l for l, _ in specs]
for i in range(len(labels)):
    for j in range(i + 1, len(labels)):
        a, b = res[labels[i]]["paper_class"], res[labels[j]]["paper_class"]
        keys = sorted(set(a) & set(b))
        po, k = kappa(a, b, keys)
        po2 = sum(coarse(a[x]) == coarse(b[x]) for x in keys) / len(keys)
        pairs[f"{labels[i]}-{labels[j]}"] = {"n": len(keys), "exact": round(po, 3), "kappa": round(k, 3), "coarse": round(po2, 3),
                                             "disagreements": {x: [a[x], b[x]] for x in keys if a[x] != b[x]}}
rep = {"classifiers": {l: {kk: v for kk, v in r.items() if kk != "paper_class"} for l, r in res.items()},
       "paper_class": {l: r["paper_class"] for l, r in res.items()}, "pairs": pairs}
json.dump(rep, open(D / "merge_report.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False, default=dict)
for r in res.values():
    print(r["name"], "| fehlend", r["missing"], "| Zitate ok", r["quotes_ok"], "/", r["quotes_total"], "| Verteilung", dict(r["dist"]), "| fulltext_needed", r["fulltext_needed"], "| Probleme", len(r["issues"]))
    for i in r["issues"][:8]:
        print("   ", i)
for k_, v in pairs.items():
    print(k_, "| n", v["n"], "| exakt", v["exact"], "| kappa", v["kappa"], "| grob", v["coarse"], "| Abweichungen", v["disagreements"])
