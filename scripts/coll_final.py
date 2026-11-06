"""Adjudicate the collision-candidate run (A=Claude Sonnet, G=Gemini 4 Argon) and emit collision rows + report data."""
import csv, io, json, sys
from collections import Counter
from pathlib import Path

C = Path(sys.argv[1])
rep = json.load(open(C / "merge_report.json", encoding="utf-8"))
A, G = rep["paper_class"]["A"], rep["paper_class"]["G"]
cmap = {m["cand_id"]: m for m in json.load(open(C / "coll_map.json", encoding="utf-8"))}
inp = {p["pilot_id"]: p for p in json.load(open(C / "coll_input.json", encoding="utf-8"))["papers"]}

# Schiedsspruch (Claude Opus 5.5) für Abweichungen und für jedes FALSCH
RULING = {
    "C04": ("FALSCH", "Äquivalenz 'ETH ⇔ keine 2^{o(n)}-(1+ε)-Approximation von #3-SAT': ETH fällt (A0), zudem zählt ALG-01 #3-SAT exakt in 2^{o(n)}. Die Reduktionsresultate der Arbeit bleiben unberührt; widerlegt ist nur die abgeleitete Approximations-Untergrenze."),
    "C09": ("FALSCH", "Journal-/Konferenzfassung derselben Arbeit wie C04; gleiche Begründung."),
    "C14": ("FALSCH", "Allquantifizierte Untergrenze für Π-Vertex-Deletion. Gegenbeispiel Π = kantenlose Graphen (Vertex Cover): Variable je Knoten, Klausel je Kante, ≤ k per O(n)-Addierer → 2^{o(n)}, also auch 2^{o(n+m)}. Für Π mit unendlicher verbotener Familie offen."),
    "C20": ("FALSCH", "Parität der Homomorphismen G→H, H fest: ⌈log|H|⌉ Bits je Knoten, Kantenverträglichkeit als Klauseln fester Breite, exakte Zählung mit ALG-01, dann mod 2 → 2^{o(|V(G)|)}."),
    "C21": ("FALSCH", "Zweite Fassung derselben Arbeit wie C20; gleiche Begründung."),
    "C24": ("FALSCH", "1-Erweiterbarkeit über n+1 Berechnungen von α (Independent Set als SAT mit ≥ t-Zähler, O(n) Variablen, binäre Suche) → 2^{o(n)}."),
    "C27": ("FALSCH", "Matching Cut: Variable je Knoten, je Knoten und Nachbarpaar eine Klausel der Breite 3 ('höchstens ein Nachbar drüben'), Nichtleere durch Raten zweier Knoten → 2^{o(n)}. Perfect Matching Cut und Disconnected Perfect Matching bleiben offen (Mindestbedingung hat unbeschränkte Breite)."),
    "C53": ("FALSCH", "Matching Cut, gleiche Kodierung wie C27."),
    "C63": ("FALSCH", "Äquivalenz 'ETH ⇔ SAT({R})-2 nicht subexponentiell': ETH fällt (A0); zudem k-CNF mit n Variablen bei festem R."),
    "C34": ("UNGESTUETZT-OFFEN", "Untergrenze 2^{n^{1-ε}/r^{1+ε}} ist subexponentiell; ein 2^{O(n/√log n)}-Algorithmus unterbietet sie nicht. Kein Widerspruch, nur ungestützt (G irrte)."),
    "C54": ("UNGESTUETZT-OFFEN", "Untergrenze 2^{n^{1-ε}} für konstante Approximation; vom neuen Algorithmus nicht unterboten. Nur ungestützt (G irrte)."),
    "C44": ("UNGESTUETZT-OFFEN", "Gap-ETH-Tightness der Zeit-Approximations-Abwägung. Für konstantes r unterbietet exaktes IS in 2^{o(n)} die Schranke 2^{n/r^{1+δ}}: bedingter FALSCH-Kandidat, Bereich von r im Volltext klären."),
    "C37": ("UNGESTUETZT-OFFEN", "= Pilot P10; ETH-Schranken für Editierprobleme überwiegend parametrisiert; Volltext."),
    "C39": ("UNBERUEHRT", "Eigenes Resultat ist ein unbedingter Algorithmus; die zitierte (nm)^{o(r)}-Schranke [Arora et al. 2012] ist ungestützt, aber nicht Satz dieser Arbeit."),
    "C40": ("UNBERUEHRT", "Andere Fassung von C39; gleiche Begründung."),
}
AGREED_FALSCH_NOTE = {
    "C01": "3-Färbung auf n-Knoten-Graphen: ALG-03 zählt q-Färbungen in 2^{o(v)}.",
    "C06": "4-Färbung von Streckengraphen: ALG-03. Die Dominating-Set-Teilaussage nur im ∀ε-Sinn von ALG-05; Independent Dominating Set offen.",
    "C33": "= Pilot P07 (COL-0005).",
    "C51": "Äquivalenz 'subexponentiell lösbar ⇔ ETH falsch' (Linear Monadic NP); ETH fällt (A0).",
    "C57": "Endlicher Bereich, feste Sprache: ⌈log|D|⌉ Bits je Variable, Klauseln fester Breite → 2^{o(n)}.",
    "C65": "Variable je Knoten, 3-Klausel je induziertem P3, ≤ k per O(n)-Addierer → 2^{o(n)}.",
    "C66": "= Pilot P45 (COL-0006).",
    "C68": "wie C57 (frühere verwandte Arbeit).",
}
final = {}
for pid in sorted(A):
    if A[pid] == G[pid]:
        final[pid] = (A[pid], AGREED_FALSCH_NOTE.get(pid, "Übereinstimmung A=G"))
    else:
        final[pid] = RULING[pid]
assert {p for p in A if A[p] != G[p]} <= set(RULING)
falsch = [p for p in final if final[p][0] == "FALSCH"]
dist = Counter(v[0] for v in final.values())
out = {"final": {k: {"class": v[0], "reason": v[1], "A": A[k], "G": G[k], **cmap[k], "title": inp[k]["title"], "year": inp[k]["year"]} for k, v in final.items()},
       "falsch": falsch, "dist": dict(dist), "pair": rep["pairs"]["A-G"]}
json.dump(out, open(C / "ADJUDICATION.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(json.dumps({"dist": dict(dist), "falsch": falsch, "n_falsch": len(falsch)}, ensure_ascii=False))
