# Baixa o resultado final do 2º turno (6258) por UF e por município: Lula (13), Flávio (22), brancos e nulos.
# Mesma estrutura do base1t.py (br, uf, mu), mais vb (brancos) e tvn (total de nulos): c - vv = vb + tvn.
# Devagar: 3 consultas por vez (o base1t.py usava 24), pausa entre elas e espera geral no 429.
# Uso: python base2t.py [saida.json] [mun-e006258-cm.json]
import json, sys, os, gzip, time, threading, urllib.request, urllib.error, concurrent.futures as cf
AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "..", "dados", "base_2t_municipios.json")
# lista de municípios do TSE (config/mun-e006258-cm.json), copiada em dados/tse_config/
MUN = sys.argv[2] if len(sys.argv) > 2 else os.path.join(AQUI, "..", "dados", "tse_config", "mun-e006258-cm.json")
B = "https://resultados.tse.jus.br/oficial/ele2026/6258/dados/"
PARALELO, PAUSA, TETO = 3, 0.3, 100 * 2**20  # consultas simultâneas, segundos entre consultas, teto de 100 MB
trava = threading.Lock()
st = {"bytes": 0, "consultas": 0, "n429": 0, "espera_ate": 0.0, "gerado": set(), "parcial": [], "identidade": []}
def num(s): return 0 if not s else float(str(s).replace(".", "").replace(",", "."))
def get(path):
    err = None
    for t in range(8):
        with trava:
            if st["bytes"] > TETO: raise RuntimeError("passou de 100 MB")
            espera = st["espera_ate"] - time.time()
        if espera > 0: time.sleep(espera)
        try:
            req = urllib.request.Request(B + path, headers={"Accept-Encoding": "gzip"})
            with urllib.request.urlopen(req, timeout=30) as r:
                corpo, gz = r.read(), r.headers.get("Content-Encoding") == "gzip"
            with trava: st["bytes"] += len(corpo); st["consultas"] += 1
            time.sleep(PAUSA)
            return json.loads(gzip.decompress(corpo) if gz else corpo)
        except urllib.error.HTTPError as e:
            err = e
            if e.code in (429, 503):  # todos esperam: 15 s, 30 s, 60 s, 120 s... ou o Retry-After
                p = float(e.headers.get("Retry-After") or 15 * 2 ** min(t, 4))
                with trava: st["n429"] += e.code == 429; st["espera_ate"] = max(st["espera_ate"], time.time() + p)
                print(f"{e.code} em {path}: esperando {p:.0f} s", flush=True)
            else: time.sleep(2 ** t)
        except (urllib.error.URLError, OSError) as e: err = e; time.sleep(2 ** t)
    raise err
def h2h(j, nome):
    v = {}
    for a in j["carg"][0]["agr"]:
        for p in a["par"]:
            for c in p["cand"]: v[c["n"]] = num(c["vap"])
    e, w = j["e"], j["v"]
    r = {"te": num(e["te"]), "c": num(e["c"]), "vv": num(w["vv"]), "L": v.get("13", 0), "F": v.get("22", 0),
         "vb": num(w["vb"]), "tvn": num(w["tvn"])}
    with trava:  # conferências de cada arquivo: totalização final e c - vv = vb + tvn
        st["gerado"].add(j["dg"] + " " + j["hg"])
        if j["s"]["pst"] != "100,00" or j["tf"] != "s": st["parcial"].append(nome)
        if r["c"] - r["vv"] != r["vb"] + r["tvn"]: st["identidade"].append(nome)
    return r
mun = json.load(open(MUN, encoding="utf-8"))
ufs = [a["cd"] for a in mun["abr"]]
out = {"br": h2h(get("br/br-c0001-e006258-u.json"), "br"), "uf": {}, "mu": {}}
for u in ufs: out["uf"][u] = h2h(get(f"{u}/{u}-c0001-e006258-u.json"), u)
jobs = [(a["cd"], m["cd"], m["nm"], m["c"]) for a in mun["abr"] for m in a["mu"]]
def one(t):
    u, cd, nm, cap = t
    try: r = h2h(get(f"{u}/{u}{cd}-c0001-e006258-u.json"), u + cd)
    except Exception as e: return t, None
    r.update(uf=u, nm=nm, cap=cap == "s"); return t, r
inicio, falhas = time.time(), []
with cf.ThreadPoolExecutor(PARALELO) as ex:
    for i, (t, r) in enumerate(ex.map(one, jobs), 1):
        if r is None: falhas.append(t)
        else: out["mu"][t[1]] = r
        if i % 250 == 0: print(f"{i}/{len(jobs)} municípios, {st['bytes'] / 2**20:.1f} MB, {time.time() - inicio:.0f} s", flush=True)
for t in list(falhas):  # segunda chance, uma por vez
    if st["bytes"] > TETO: break
    t2, r = one(t)
    if r is not None: out["mu"][t[1]] = r; falhas.remove(t)
if st["bytes"] > TETO: sys.exit("parado: passou de 100 MB. Pedir aprovação antes de continuar.")
json.dump(out, open(SAIDA, "w", encoding="utf-8"), ensure_ascii=False)
g = sorted(st["gerado"], key=lambda s: (s[6:10], s[3:5], s[:2], s[11:]))
print("ufs", len(out["uf"]), "muns", len(out["mu"]), "falhas", len(falhas), [t[0] + t[1] for t in falhas])
print("consultas", st["consultas"], "MB", round(st["bytes"] / 2**20, 2), "429", st["n429"], "s", round(time.time() - inicio))
print("gerados de", g[0], "a", g[-1], "| não finais", st["parcial"], "| c-vv != vb+tvn", st["identidade"])
