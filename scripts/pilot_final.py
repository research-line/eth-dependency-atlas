"""Adjudicate A (Claude Sonnet) vs G (Gemini 4 Argon), build paper-level pilot atlas CSV and metrics."""
import csv, io, json, math, sys
from collections import Counter
from pathlib import Path

D = Path(sys.argv[1])
rep = json.load(open(D / "merge_report.json", encoding="utf-8"))
A, G = rep["paper_class"]["A"], rep["paper_class"]["G"]
inp = {p["pilot_id"]: p for p in json.load(open(D / "sample.json", encoding="utf-8"))["sample"]}
CA = {p["pilot_id"]: p for p in json.load(open(D / "a_out/classifier_a.json", encoding="utf-8"))["papers"]}
CG = {p["pilot_id"]: p for p in json.load(open(D / "g_out/classifier_g.json", encoding="utf-8"))["papers"]}

RULING = {  # Schiedsspruch Claude Opus 5.5 (eigene Herleitung, Fremdreview ausstehend)
    "P07": ("FALSCH", "Grad ≤ 4: jeder Knoten liegt in ≤ 6 Dreiecken; Variablen je Dreieck (O(n)), Bedingung genau-eins je Knoten als CNF der Breite ≤ 6 → 2^{o(n)} nach OAI-ETH/ANT-ETH. Die bedingte Untergrenze ist widerlegt.", "abstract"),
    "P09": ("UNGESTUETZT-OFFEN", "2^{o(k)}·poly-Schranke nur ungestützt. FALSCH-Kandidat: 2^{o(|G|)}-Schranke, falls |G| = n+m. Variablen je Kante, Diamant-Freiheit je 4-Menge (Breite ≤ 6), Budget ≤ k per O(m)-Zählschaltung + Tseitin. Definition von |G| im Volltext prüfen.", "fulltext_needed"),
    "P10": ("UNGESTUETZT-OFFEN", "Dissertation; die ETH-Schranken für Editierprobleme sind überwiegend parametrisiert (2^{o(k)}). Einzelne 2^{o(n)}-Aussagen wären FALSCH-Kandidaten → Volltext.", "fulltext_needed"),
    "P27": ("UNGESTUETZT-OFFEN", "2^{o(n)} für gewichtete Min-Power-Konnektivität: keine O(n)-Variablen-Kodierung fester Breite ersichtlich (Kantenwahl ~m Variablen, Konnektivität braucht Hilfsvariablen).", "abstract"),
    "P39": ("UNBERUEHRT", "Tutorial ohne eigene bedingte Sätze; als Saatquelle für weitere Einträge vormerken.", "abstract"),
    "P45": ("FALSCH", "POLSAT über einer 2-elementigen Algebra mit fester Signatur: Tseitin über die Termgatter ergibt O(N) Variablen und Klauseln der Breite ≤ Stelligkeit+1 → 2^{o(N)}. Annahme: „sub-exponential“ bezieht sich auf die Eingabegröße (die Reduktion misst linear in der Größe).", "abstract"),
    "P50": ("UNGESTUETZT-OFFEN", "SETH-bedingte Trennung (Ringe vs. idempotente Halbringe); keine Rettung genannt; Details im Volltext.", "fulltext_needed"),
}
final, how = {}, {}
for pid in sorted(inp):
    if A[pid] == G[pid]:
        final[pid], how[pid] = A[pid], "Übereinstimmung A=G"
    else:
        final[pid], how[pid] = RULING[pid][0], "Schiedsspruch"
assert set(RULING) == {p for p in inp if A[p] != G[p]}

def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return round(100 * (c - h), 1), round(100 * (c + h), 1)

dist = Counter(final.values()); n = len(final)
affected = sum(final[p] in ("FALSCH", "UNGESTUETZT-OFFEN", "UNGESTUETZT-RETTBAR") for p in final)
metrics = {"n": n, "dist": dict(dist), "affected": affected, "affected_pct": round(100 * affected / n, 1),
           "affected_ci95": wilson(affected, n), "falsch_ci95": wilson(dist.get("FALSCH", 0), n),
           "fulltext_needed_final": sum((RULING.get(p, (0, 0, None))[2] == "fulltext_needed") or
                                        (p not in RULING and (CA[p].get("evidence_level") == "fulltext_needed" or CG[p].get("evidence_level") == "fulltext_needed"))
                                        for p in final),
           "pair_A_G": rep["pairs"]["A-G"], "rettbar_papers": [p for p in final if final[p] == "UNGESTUETZT-RETTBAR"],
           "falsch_papers": [p for p in final if final[p] == "FALSCH"]}

def first_quote(X, pid, cls):
    for c in X[pid]["claims"]:
        if c["class"] == cls and c.get("quote"):
            return c["quote"], c.get("hypothesis"), c.get("rescue_hypothesis", ""), c.get("fix_type", ""), c.get("fix_candidate", "")
    for c in X[pid]["claims"]:
        if c.get("quote"):
            return c["quote"], c.get("hypothesis"), c.get("rescue_hypothesis", ""), c.get("fix_type", ""), c.get("fix_candidate", "")
    return "", [], "", "", ""

FIELDS = ["atlas_id", "work_id", "title", "year", "statement_ref", "statement_quote", "quote_origin", "hypothesis", "result_type",
          "class", "class_reason", "rescue_hypothesis", "rescue_ref", "classifier_a", "classifier_b", "agreement", "condition_A0",
          "fix_type", "fix_candidate", "evidence_level", "openalex_id"]
buf = io.StringIO(); w = csv.writer(buf, delimiter=";", lineterminator="\n"); w.writerow(FIELDS)
for i, pid in enumerate(sorted(final), 1):
    meta = inp[pid]
    q, hyp, resc, ftype, fcand = first_quote(CA, pid, final[pid])
    reason = RULING[pid][1] if pid in RULING else next((c["class_reason"] for c in CA[pid]["claims"] if c["class"] == final[pid]), "")
    ev = RULING[pid][2] if pid in RULING else ("fulltext_needed" if "fulltext_needed" in (CA[pid].get("evidence_level"), CG[pid].get("evidence_level")) else "abstract")
    w.writerow([f"ATL-P-{i:03d}", meta.get("doi") or meta["openalex_id"], meta["title"], meta["year"], "Abstract", q,
                "Abstract (OpenAlex), maschinell als wörtlich geprüft", "|".join(hyp or []), "", final[pid], reason, resc, "",
                f"A: claude-sonnet → {A[pid]}", f"G: Gemini 4 Argon (Medium) → {G[pid]}",
                "yes" if pid not in RULING else "resolved (Schiedsspruch Claude Opus 5.5)", "true", ftype, fcand, ev, meta["openalex_id"]])
(D / "atlas_pilot_2026-11-06.csv").write_bytes(buf.getvalue().encode("utf-8"))
json.dump({"rulings": {k: {"class": v[0], "reason": v[1], "evidence": v[2], "A": A[k], "G": G[k]} for k, v in RULING.items()},
           "final": final, "how": how, "metrics": metrics}, open(D / "ADJUDICATION.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(json.dumps(metrics, indent=1, ensure_ascii=False))
