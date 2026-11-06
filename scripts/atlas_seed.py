"""ST2-A05: write the first atlas seed rows (secondary descriptions from OpenAI ETH paper §1.1), schema per _data/ATLAS_SCHEMA.md."""
import csv, io, os, sys
from pathlib import Path

OUT = Path(sys.argv[1])
FIELDS = ["atlas_id", "work_id", "title", "year", "statement_ref", "statement_quote", "quote_origin", "hypothesis",
          "result_type", "class", "class_reason", "rescue_hypothesis", "rescue_ref", "classifier_a", "classifier_b",
          "agreement", "condition_A0"]
SRC = "OAI-ETH §1.1 (Sekundärbeschreibung; Originalsatz noch nicht gelesen)"
CA = "claude-opus-5.5 (vorläufig, nur aus OAI-ETH §1.1)"
rows = [
    ("CHKX06", "ETH-based reductions yielded lower bounds for the dependence on solution size in Clique", "ETH", "lower_bound", "UNGESTUETZT-OFFEN", "A2 nein: ETH-Widerlegung liefert keinen f(k)n^{o(k)}-Clique-Algorithmus (Reduktion läuft SAT→Clique)", "", ""),
    ("Marx10", "and on treewidth in constraint satisfaction and partitioned subgraph isomorphism", "ETH", "lower_bound", "UNGESTUETZT-OFFEN", "A2 nein; A3 offen", "", ""),
    ("CDL16", "SETH supported sharp exponential bounds for Hitting Set and Set Splitting", "SETH", "lower_bound", "UNGESTUETZT-OFFEN", "A3 offen; laut OAI-ETH bekommt Set Splitting mit Mengengröße ≤ k neue Algorithmen (Reduktion auf feste Breite) — Teilaussage dort ggf. FALSCH, prüfen", "", ""),
    ("LMS18", "and for Independent Set and Dominating Set parameterized by treewidth", "SETH", "lower_bound", "UNGESTUETZT-RETTBAR", "A3 ja laut Quelle", "CNF-SAT-H (unbeschränkte Breite)", "OAI-ETH §1.1: 'also follow from the hypothesis that unrestricted CNF-SAT admits no 2^{(1-δ)n}poly(n,m)-time algorithm'"),
    ("ABHS19", "It also gave bounds on possible speedups of pseudopolynomial algorithms for Subset Sum and Bicriteria Path", "SETH", "lower_bound", "UNGESTUETZT-OFFEN", "A3 offen", "", ""),
    ("BackursIndyk18", "SETH was used to rule out polynomial-factor speedups over quadratic running times for edit distance", "SETH", "fine_grained_reduction", "UNGESTUETZT-OFFEN", "A3 offen (OV-basierter Beweis? im Original prüfen)", "", ""),
    ("BK15-LCS", "longest common subsequence", "SETH", "fine_grained_reduction", "UNGESTUETZT-RETTBAR", "A3 ja laut Quelle", "OVC", "OAI-ETH §1.1: 'the lower bounds for longest common subsequence and regular-expression matching follow from the Orthogonal Vectors Conjecture'"),
    ("BK15-DTW", "and dynamic time warping", "SETH", "fine_grained_reduction", "UNGESTUETZT-OFFEN", "A3 in der Quelle nicht genannt", "", ""),
    ("Bri14", "Fréchet distance", "SETH", "fine_grained_reduction", "UNGESTUETZT-RETTBAR", "A3 ja laut Quelle", "CNF-SAT-H (unbeschränkte Breite)", "OAI-ETH §1.1"),
    ("BI16", "regular-expression matching", "SETH", "fine_grained_reduction", "UNGESTUETZT-RETTBAR", "A3 ja laut Quelle", "OVC", "OAI-ETH §1.1"),
    ("RV13", "Other applications concerned approximating graph diameter", "SETH", "hardness_of_approx", "UNGESTUETZT-RETTBAR", "A3 ja laut Quelle", "CNF-SAT-H (unbeschränkte Breite)", "OAI-ETH §1.1"),
    ("AW14", "and maintaining reachability counts or the size of the largest strongly connected component under graph updates", "SETH", "lower_bound", "UNGESTUETZT-OFFEN", "A3 offen", "", ""),
    ("Din16", "It has been used to prove hardness of approximating Label Cover", "Gap-ETH", "hardness_of_approx", "UNGESTUETZT-OFFEN", "A3 offen", "", ""),
    ("MR17", "and dense constraint satisfaction problems", "Gap-ETH", "hardness_of_approx", "UNGESTUETZT-OFFEN", "A3 offen", "", ""),
    ("CCK20", "It also rules out nontrivial fixed-parameter approximations for Clique and Dominating Set", "Gap-ETH", "hardness_of_approx", "UNGESTUETZT-OFFEN", "A3 offen", "", ""),
    ("Cur18", "Under #ETH, Curticapean rules out deterministic 2^{o(v)}-time algorithms for counting perfect matchings even in unweighted bipartite graphs with v vertices and O(v) edges", "#ETH", "lower_bound", "FALSCH", "A2 ja: OAI-ETH Cor. cor:graph-counting zählt perfekte Matchings in 2^{o(v+e)}, bei e=O(v) also 2^{o(v)}", "", ""),
    ("CGIMPS16", "NSETH has been used to establish barriers to deterministic fine-grained reductions from SAT to problems such as 3SUM and All-Pairs Shortest Paths", "NSETH", "fine_grained_reduction", "UNGESTUETZT-OFFEN", "Barriere entfällt mit NSETH; ob solche Reduktionen existieren, ist offen", "", ""),
    ("Li21", "and to delineate SETH-based lower bounds for approximating directed graph diameter", "NSETH", "hardness_of_approx", "UNGESTUETZT-OFFEN", "A3 offen", "", ""),
]
buf = io.StringIO()
w = csv.writer(buf, delimiter=";", quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
w.writerow(FIELDS)
for i, (key, quote, hyp, rtype, cls, reason, rescue, rref) in enumerate(rows, 1):
    w.writerow([f"ATL-{i:04d}", f"OAI-bib:{key}", "", "", "OAI-ETH §1.1", quote, SRC, hyp, rtype, cls, reason, rescue, rref, CA, "", "pending", "true"])
data = buf.getvalue().encode("utf-8")
tmp = OUT.with_name(OUT.name + ".tmp"); tmp.write_bytes(data); os.replace(tmp, OUT)
print("rows", len(rows), {c: sum(r[4] == c for r in rows) for c in ("FALSCH", "UNGESTUETZT-RETTBAR", "UNGESTUETZT-OFFEN")})
