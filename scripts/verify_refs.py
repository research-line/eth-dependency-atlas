"""Verify reference metadata against Crossref / arXiv / OpenAlex and measure citation-graph size for the ETH atlas.
Read-only web queries; writes JSON results to the path given as argv[1]."""
import json, re, sys, time, urllib.parse, urllib.request

UA = {"User-Agent": "research-ref-verifier/1.0"}

def get(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
                return r.read().decode("utf-8")
        except Exception as e:  # network hiccup -> retry
            err = e
            time.sleep(2 * (i + 1))
    return f"ERROR {err}"

def norm(s):
    return set(w for w in re.sub(r"[^a-z0-9 ]", " ", s.lower()).split() if len(w) > 3)

def sim(a, b):
    A, B = norm(a), norm(b)
    return round(len(A & B) / max(1, len(A | B)), 2)

def crossref_doi(doi):
    t = get("https://api.crossref.org/works/" + urllib.parse.quote(doi))
    if t.startswith("ERROR"):
        return {"error": t}
    m = json.loads(t)["message"]
    return {"title": (m.get("title") or [""])[0], "year": (m.get("issued", {}).get("date-parts") or [[None]])[0][0],
            "authors": [a.get("family", "") for a in m.get("author", [])], "venue": (m.get("container-title") or [""])[0]}

def crossref_search(q):
    t = get("https://api.crossref.org/works?rows=1&query.bibliographic=" + urllib.parse.quote(q))
    if t.startswith("ERROR"):
        return {"error": t}
    it = json.loads(t)["message"]["items"]
    if not it:
        return {"error": "no hit"}
    m = it[0]
    return {"doi": m.get("DOI"), "title": (m.get("title") or [""])[0], "year": (m.get("issued", {}).get("date-parts") or [[None]])[0][0],
            "authors": [a.get("family", "") for a in m.get("author", [])], "venue": (m.get("container-title") or [""])[0]}

def arxiv(aid):
    t = get("https://export.arxiv.org/api/query?id_list=" + aid)
    e = t.split("<entry>")[1] if "<entry>" in t else ""
    if not e or "<title>Error" in e:
        return {"error": "not found"}
    g = lambda p: (re.search(p, e, re.S) or [None, ""])[1]
    return {"title": re.sub(r"\s+", " ", g(r"<title>(.*?)</title>")), "year": g(r"<published>(\d{4})"),
            "authors": [n.split()[-1] for n in re.findall(r"<name>(.*?)</name>", e)], "id": g(r"<id>(.*?)</id>")}

# (key, project, claimed title, claimed authors, how, id)
REFS = [
    ("IP01", "ST-002", "On the Complexity of k-SAT", "Impagliazzo Paturi", "doi", "10.1006/jcss.2000.1727"),
    ("IPZ01", "ST-002", "Which Problems Have Strongly Exponential Complexity?", "Impagliazzo Paturi Zane", "doi", "10.1006/jcss.2001.1774"),
    ("CIP09", "ST-002", "The complexity of satisfiability of small depth circuits", "Calabro Impagliazzo Paturi", "doi", "10.1007/978-3-642-11269-0_6"),
    ("DHMTW14", "ST-002", "Exponential Time Complexity of the Permanent and the Tutte Polynomial", "Dell Husfeldt Marx Taslaman Wahlen", "arxiv", "1206.1775"),
    ("CCK20", "ST-002", "From Gap-Exponential Time Hypothesis to Fixed Parameter Tractable Inapproximability: Clique, Dominating Set, and More", "Chalermsook Cygan Kortsarz Laekhanukit Manurangsi Nanongkai Trevisan", "doi", "10.1137/18M1166869"),
    ("CGIMPS16", "ST-002", "Nondeterministic Extensions of the Strong Exponential Time Hypothesis and Consequences for Non-reducibility", "Carmosino Gao Impagliazzo Mihajlin Paturi Schneider", "doi", "10.1145/2840728.2840746"),
    ("VWW10", "ST-002", "Subcubic equivalences between path, matrix and triangle problems", "Vassilevska Williams Williams", "search", "Subcubic equivalences between path, matrix and triangle problems Williams"),
    ("LY22", "V3", "3.1n - o(n) circuit lower bounds for explicit functions", "Li Yang", "doi", "10.1145/3519935.3519976"),
    ("Wil13", "V3", "Improving Exhaustive Search Implies Superpolynomial Lower Bounds", "Williams", "doi", "10.1137/10080703X"),
    ("JMV15", "V3", "Local reductions", "Jahanjou Miles Viola", "arxiv", "1311.3171"),
    ("Zak83", "V3", "A Turing machine time hierarchy", "Zak", "doi", "10.1016/0304-3975(83)90015-4"),
    ("Wil14b", "V3", "Algorithms for circuits and circuits for algorithms", "Williams", "doi", "10.1109/CCC.2014.33"),
    ("LLV19", "V4", "Public-Key Cryptography in the Fine-Grained Setting", "LaVigne Lincoln Vassilevska Williams", "search", "Public-Key Cryptography in the Fine-Grained Setting LaVigne Lincoln"),
    ("BRSV17", "V4", "Average-Case Fine-Grained Hardness", "Ball Rosen Sabin Vasudevan", "search", "Average-case fine-grained hardness Ball Rosen Sabin Vasudevan"),
    ("BRSV18", "V4", "Proofs of Work from Worst-Case Assumptions", "Ball Rosen Sabin Vasudevan", "search", "Proofs of Work from Worst-Case Assumptions Ball Rosen Sabin Vasudevan"),
    ("DLV20", "V4", "New Techniques for Proving Fine-Grained Average-Case Hardness", "Dalirrooyfard Lincoln Vassilevska Williams", "arxiv", "2008.06591"),
    ("Ary22", "V5", "On an extension of the Landau-Gonek formula", "Aryan", "search", "Aryan On an extension of the Landau-Gonek formula Journal of Number Theory"),
    ("BGSTB24", "V5", "An unconditional Montgomery theorem for pair correlation of zeros of the Riemann zeta-function", "Baluyot Goldston Suriajaya Turnage-Butterbaugh", "search", "An unconditional Montgomery theorem for pair correlation of zeros of the Riemann zeta-function Acta Arithmetica"),
    ("Bom00", "V5", "Remarks on Weil's quadratic functional in the theory of prime numbers, I", "Bombieri", "search", "Bombieri Remarks on Weil's quadratic functional in the theory of prime numbers"),
    ("GS25", "V5", "Zeta zeros on the critical line", "Goldston Suriajaya", "arxiv", "2511.20059"),
    ("GS26", "V5", "Zeta zeros in a narrow vertical box", "Goldston Suriajaya", "arxiv", "2603.28104"),
    ("BGSTB25", "V5", "Pair correlation of zeros of the Riemann zeta function I: proportions of simple zeros and critical zeros", "Baluyot Goldston Suriajaya Turnage-Butterbaugh", "arxiv", "2501.14545"),
]

out = {"refs": [], "openalex": {}}
for key, proj, title, authors, how, ident in REFS:
    got = crossref_doi(ident) if how == "doi" else arxiv(ident) if how == "arxiv" else crossref_search(ident)
    s = sim(title, got.get("title", "")) if "title" in got else 0
    auth_ok = all(any(a.lower().split("-")[0] in g.lower() for g in got.get("authors", [])) for a in authors.split()[:2]) if got.get("authors") else None
    out["refs"].append({"key": key, "project": proj, "claimed_title": title, "how": how, "id": ident, "found": got,
                        "title_similarity": s, "first_authors_match": auth_ok,
                        "verdict": "OK" if s >= 0.6 and auth_ok is not False else "CHECK"})
    time.sleep(0.4)

# OpenAlex: resolve seeds, then count union of citing works (and subsets mentioning the hypotheses)
seeds = {"IP01": "doi:10.1006/jcss.2000.1727", "IPZ01": "doi:10.1006/jcss.2001.1774", "CIP09": "doi:10.1007/978-3-642-11269-0_6",
         "CCK20": "doi:10.1137/18M1166869", "CGIMPS16": "doi:10.1145/2840728.2840746"}
ids = {}
for k, d in seeds.items():
    t = get("https://api.openalex.org/works/" + d)
    if not t.startswith("ERROR"):
        j = json.loads(t)
        ids[k] = j["id"].rsplit("/", 1)[-1]
        out["openalex"][k] = {"id": ids[k], "cited_by_count": j.get("cited_by_count"), "title": j.get("title")}
t = get("https://api.openalex.org/works?per-page=1&search=" + urllib.parse.quote("Exponential Time Complexity of the Permanent and the Tutte Polynomial"))
if not t.startswith("ERROR") and json.loads(t)["results"]:
    j = json.loads(t)["results"][0]
    ids["DHMTW14"] = j["id"].rsplit("/", 1)[-1]
    out["openalex"]["DHMTW14"] = {"id": ids["DHMTW14"], "cited_by_count": j.get("cited_by_count"), "title": j.get("title")}
cites = "|".join(ids.values())
def count(extra=""):
    t = get(f"https://api.openalex.org/works?per-page=1&filter=cites:{cites}{extra}")
    return json.loads(t)["meta"]["count"] if not t.startswith("ERROR") else t
out["openalex"]["union_citing"] = count()
for label, q in [("abstract_ETH", "exponential time hypothesis"), ("abstract_SETH", "strong exponential time hypothesis"),
                 ("fulltext_ETH", "exponential time hypothesis")]:
    field = "fulltext.search" if label.startswith("fulltext") else "title_and_abstract.search"
    out["openalex"][f"union_citing_{label}"] = count(f",{field}:{urllib.parse.quote(q)}")
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=2, ensure_ascii=False)
for r in out["refs"]:
    print(r["verdict"], r["key"], r["title_similarity"], r["first_authors_match"], "|", r["found"].get("title", r["found"].get("error"))[:90], "|", r["found"].get("year"), r["found"].get("doi", ""))
print(json.dumps(out["openalex"], indent=1, ensure_ascii=False))
