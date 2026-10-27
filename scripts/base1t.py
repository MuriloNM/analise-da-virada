# Baixa o resultado final do 1º turno (6257) por UF e por município: só Lula (13) e Flávio (22).
import json, sys, urllib.request, concurrent.futures as cf, os
D = sys.argv[1]
B = "https://resultados.tse.jus.br/oficial/ele2026/6257/dados/"
def num(s): return 0 if not s else float(str(s).replace(".", "").replace(",", "."))
def get(path):
    for _ in range(4):
        try:
            with urllib.request.urlopen(B + path, timeout=30) as r: return json.load(r)
        except Exception as e: err = e
    raise err
def h2h(j):
    v = {}
    for a in j["carg"][0]["agr"]:
        for p in a["par"]:
            for c in p["cand"]: v[c["n"]] = num(c["vap"])
    return {"te": num(j["e"]["te"]), "c": num(j["e"]["c"]), "vv": num(j["v"]["vv"]), "L": v.get("13", 0), "F": v.get("22", 0)}
# lista de municípios do TSE (config/mun-e006258-cm.json), copiada em dados/tse_config/
MUN = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), "..", "dados", "tse_config", "mun-e006258-cm.json")
mun = json.load(open(MUN, encoding="utf-8"))
ufs = [a["cd"] for a in mun["abr"]]
out = {"br": h2h(get("br/br-c0001-e006257-u.json")), "uf": {}, "mu": {}}
for u in ufs: out["uf"][u] = h2h(get(f"{u}/{u}-c0001-e006257-u.json"))
jobs = [(a["cd"], m["cd"], m["nm"], m["c"]) for a in mun["abr"] for m in a["mu"]]
def one(t):
    u, cd, nm, cap = t
    try: r = h2h(get(f"{u}/{u}{cd}-c0001-e006257-u.json"))
    except Exception as e: return t, None
    r.update(uf=u, nm=nm, cap=cap == "s"); return t, r
fails = 0
with cf.ThreadPoolExecutor(24) as ex:
    for t, r in ex.map(one, jobs):
        if r is None: fails += 1
        else: out["mu"][t[1]] = r
json.dump(out, open(os.path.join(D, "base1t.json"), "w", encoding="utf-8"), ensure_ascii=False)
print("ufs", len(out["uf"]), "muns", len(out["mu"]), "fails", fails)
