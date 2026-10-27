# Lê o 2º turno (6258) do TSE e compara com o 1º turno (6257) nas mesmas urnas, só Lula (13) x Flávio (22).
# Unidades: 300 maiores municípios + "resto da UF" (UF menos esses municípios).
# Para cada unidade, f = eleitorado em seções totalizadas / eleitorado total no 2º turno.
# 1º turno equivalente = soma de f * votos do 1º turno de cada unidade.
import json, sys, os, time, urllib.request, concurrent.futures as cf
D = sys.argv[1]
B = "https://resultados.tse.jus.br/oficial/ele2026/6258/dados/"
TOPN = 300
def num(s): return 0.0 if s in (None, "") else float(str(s).replace(".", "").replace(",", "."))
def get(path):
    err = None
    for _ in range(3):
        try:
            with urllib.request.urlopen(B + path + "?t=" + str(int(time.time())), timeout=20) as r: return json.load(r)
        except Exception as e: err = e
    raise err
def parse(j):
    c = {}
    for a in j["carg"][0]["agr"]:
        for p in a["par"]:
            for k in p["cand"]: c[k["n"]] = k
    L, F = c.get("13", {}), c.get("22", {})
    return {"te": num(j["e"]["te"]), "est": num(j["e"]["est"]), "pst": num(j["s"]["pst"]),
            "L": num(L.get("vap")), "F": num(F.get("vap")), "raw": j, "cand": c}

base = json.load(open(os.path.join(D, "base1t.json"), encoding="utf-8"))
top = sorted(base["mu"].items(), key=lambda kv: -kv[1]["te"])[:TOPN]
ufs = list(base["uf"].keys())
jobs = [("br", "br/br-c0001-e006258-u.json")] + [("uf:" + u, f"{u}/{u}-c0001-e006258-u.json") for u in ufs] \
     + [("mu:" + cd, f"{m['uf']}/{m['uf']}{cd}-c0001-e006258-u.json") for cd, m in top]
res = {}
def one(t):
    k, p = t
    try: return k, parse(get(p))
    except Exception: return k, None
with cf.ThreadPoolExecutor(32) as ex:
    for k, r in ex.map(one, jobs): res[k] = r
br = res["br"]
if br is None: print("ERRO: nacional indisponível"); sys.exit(1)

# Unidades com dados de ambos os turnos
units = []  # (uf, te, est, L2, F2, L1, F1, nome|None)
for u in ufs:
    U2 = res.get("uf:" + u); U1 = base["uf"][u]
    if U2 is None: continue
    rest = {"te": U2["te"], "est": U2["est"], "L2": U2["L"], "F2": U2["F"], "L1": U1["L"], "F1": U1["F"]}
    for cd, m in top:
        if m["uf"] != u: continue
        M2 = res.get("mu:" + cd)
        if M2 is None or M2["te"] <= 0: continue
        units.append(dict(uf=u, nm=m["nm"], te=M2["te"], est=M2["est"], pst=M2["pst"], L2=M2["L"], F2=M2["F"], L1=m["L"], F1=m["F"]))
        for a, b in (("te", "te"), ("est", "est"), ("L2", "L2"), ("F2", "F2"), ("L1", "L1"), ("F1", "F1")):
            rest[a] -= units[-1][b]
    if rest["te"] > 0:
        units.append(dict(uf=u, nm=None, te=rest["te"], est=max(0.0, rest["est"]), pst=None,
                          L2=max(0.0, rest["L2"]), F2=max(0.0, rest["F2"]), L1=rest["L1"], F1=rest["F1"]))
for x in units: x["f"] = min(1.0, x["est"] / x["te"]) if x["te"] else 0.0

def share(L, F): return L / (L + F) if L + F > 0 else None
L2, F2 = br["L"], br["F"]
s2 = share(L2, F2)
L1eq = sum(x["f"] * x["L1"] for x in units); F1eq = sum(x["f"] * x["F1"] for x in units)
s1eq = share(L1eq, F1eq)
s1uf = share(sum(min(1, res["uf:" + u]["est"] / res["uf:" + u]["te"]) * base["uf"][u]["L"] for u in ufs if res.get("uf:" + u)),
             sum(min(1, res["uf:" + u]["est"] / res["uf:" + u]["te"]) * base["uf"][u]["F"] for u in ufs if res.get("uf:" + u)))
s1fin = share(base["br"]["L"], base["br"]["F"])
swing = (s2 - s1eq) if (s2 is not None and s1eq is not None) else None

# Projeção: o que falta apurar em cada unidade segue o 1º turno + a variação observada (da unidade, senão da UF, senão nacional)
def swk(L2_, F2_, L1_, F1_, f_, minv):
    if L2_ + F2_ < minv or f_ <= 0: return None
    s1 = share(f_ * L1_, f_ * F1_)
    return (share(L2_, F2_) - s1, (L2_ + F2_) / (f_ * (L1_ + F1_)))
nat = (swing, (L2 + F2) / (L1eq + F1eq)) if swing is not None and L1eq + F1eq > 0 else (0.0, 1.0)
ufsw, ufout = {}, {}
for u in ufs:
    xs = [x for x in units if x["uf"] == u]
    if not xs: continue
    a = {k: sum(x[k] for x in xs) for k in ("te", "est", "L2", "F2")}
    l1 = sum(x["f"] * x["L1"] for x in xs); f1 = sum(x["f"] * x["F1"] for x in xs)
    ufsw[u] = (share(a["L2"], a["F2"]) - share(l1, f1), (a["L2"] + a["F2"]) / (l1 + f1)) if a["L2"] + a["F2"] >= 3000 and l1 + f1 > 0 else None
    U2 = res["uf:" + u]; U1 = base["uf"][u]
    stale = a["est"] > U2["est"] + 1  # arquivo da UF mais velho que o dos municípios
    ufout[u] = {"pst": round(a["est"] / a["te"] * 100, 2) if stale else U2["pst"], "stale": stale, "L2": a["L2"], "F2": a["F2"], "s2": share(a["L2"], a["F2"]),
                "s1eq": share(l1, f1), "s1fin": share(U1["L"], U1["F"]), "te": U2["te"]}
remL = remF = 0.0
for x in units:
    sw = swk(x["L2"], x["F2"], x["L1"], x["F1"], x["f"], 1500) or ufsw.get(x["uf"]) or nat
    rem = (1 - x["f"]) * (x["L1"] + x["F1"]) * sw[1]
    s = min(1.0, max(0.0, share(x["L1"], x["F1"]) + sw[0])) if x["L1"] + x["F1"] > 0 else 0.5
    remL += rem * s; remF += rem * (1 - s)
proj = share(L2 + remL, F2 + remF) if swing is not None else None

mu = []
for x in sorted([x for x in units if x["nm"]], key=lambda x: -x["te"])[:40]:
    mu.append({"nm": x["nm"], "uf": x["uf"], "pst": x["pst"], "te": x["te"], "s2": share(x["L2"], x["F2"]),
               "s1": share(x["L1"], x["F1"]), "s1eq": share(x["f"] * x["L1"], x["f"] * x["F1"]) if x["f"] > 0 else None})

j = br["raw"]; e, v, s = j["e"], j["v"], j["s"]
def cinfo(c):
    vs = c.get("vs") or [{}]
    return {"n": c["n"], "nm": c.get("nmu") or c.get("nm"), "vice": vs[0].get("nmu") or vs[0].get("nm") or "", "e": c.get("e", ""), "st": c.get("st", "")}
hpath = os.path.join(D, "hist.json")
try: hist = json.load(open(hpath, encoding="utf-8"))
except Exception: hist = []
r4 = lambda z: None if z is None else round(z * 100, 3)
pst = num(s["pst"])
pt = [round(pst, 2), r4(s2), r4(s1eq), r4(proj), j["hg"], r4(s1uf)]
if pst > 0 and s2 is not None and (not hist or hist[-1][0] != pt[0]): hist.append(pt)
json.dump(hist, open(hpath, "w", encoding="utf-8"))
doc = {"upd": __import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds"), "dg": j["dg"], "hg": j["hg"], "and": j.get("and"), "md": j.get("md"),
       "pst": pst, "st": num(s["st"]), "ts": num(s["ts"]), "pest": num(e["pest"]), "esnt": num(e["esnt"]),
       "L2": L2, "F2": F2, "s2": r4(s2), "s1eq": r4(s1eq), "s1uf": r4(s1uf), "s1fin": r4(s1fin), "swing": r4(swing), "proj": r4(proj),
       "L1eq": round(L1eq), "F1eq": round(F1eq),
       "c": num(e["c"]), "pc": num(e["pc"]), "a": num(e["a"]), "pa": num(e["pa"]), "vb": num(v["vb"]), "pvb": num(v["pvb"]), "vn": num(v["tvn"]), "pvn": num(v["ptvn"]),
       "t1": {"pc": round(base["br"]["c"] / base["br"]["te"] * 100, 2), "L": base["br"]["L"], "F": base["br"]["F"]},
       "A": cinfo(br["cand"]["13"]), "B": cinfo(br["cand"]["22"]),
       "uf": {u: {k: (r4(val) if k in ("s2", "s1eq", "s1fin") else val) for k, val in d.items()} for u, d in ufout.items()},
       "mu": [{k: (r4(val) if k in ("s2", "s1", "s1eq") else val) for k, val in m.items()} for m in mu],
       "fails": sum(1 for r in res.values() if r is None), "hist": hist[-800:]}
json.dump(doc, open(os.path.join(D, "now.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(f"{j['hg']} pst={pst} s2={r4(s2)} s1eq={r4(s1eq)} s1uf={r4(s1uf)} swing={r4(swing)} proj={r4(proj)} fails={doc['fails']} hist={len(hist)} bytes={os.path.getsize(os.path.join(D,'now.json'))}")
