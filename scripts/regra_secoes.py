# T41, exploração: regra de chamada por número de seções apuradas, e não por % apurado (pedido do autor, 29/10).
# R2(N): primeiro instante com pelo menos N seções apuradas em que (c) e (d) apontam o mesmo vencedor; R3(N): o mesmo com (b), (c) e (d).
# N é escolhido deixando um grupo de fora (cada ano; e presidente+governador contra prefeito): o menor N com 0 chamadas erradas nos
# outros grupos, testado no que ficou de fora. Sem senador (decisão do autor). Mesmas fontes de regra_chamada.py; nada é reprojetado.
# Uso: python -I scripts/regra_secoes.py   (grava dados/projecoes_outras/regra_secoes.json)
import os, csv, json, math, statistics
AQUI = os.path.dirname(os.path.abspath(__file__)); DADOS = os.path.join(AQUI, "..", "dados"); SAI = os.path.join(DADOS, "projecoes_outras")
REGRAS = dict(R3="bcd", R2="cd")
NS = (10, 20, 30, 50, 75, 100, 150, 200, 300, 500, 750, 1000, 2000, 5000)

def disputas():
    D = {}
    def ler(p, nome=None, final=None, filtro=None):
        for r in csv.DictReader(open(p, encoding="utf-8"), delimiter=";"):
            if filtro and not filtro(r): continue
            d = nome or r["disputa"]; fin = final if final is not None else float(r["final"])
            D.setdefault(d, (fin, []))[1].append({k: float(r[k]) for k in ("pst", "n", "b", "c", "d")})
    ler(os.path.join(DADOS, "projecoes_2t", "instantes.csv"), "presidente_2026", 51.785, lambda r: r["conjunto"] == "fino")
    for a in ("governador_2026_instantes.csv", "teste2022_instantes.csv", "teste2018_instantes.csv", "teste2024_instantes.csv"):
        ler(os.path.join(SAI, a))
    for _, L in D.values(): L.sort(key=lambda d: d["pst"])
    return D

def chamada(final, L, ms, N):
    for d in L:
        if d["n"] >= N and len({d[m] > 50 for m in ms}) == 1: return d, (d[ms[0]] > 50) == (final > 50)
    return None, None

def wilson(k, n, z=1.96):
    if not n: return None
    p = k / n; a = 1 + z * z / n; c = p + z * z / (2 * n); s = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [round(100 * max(0, (c - s) / a), 1), round(100 * (c + s) / a, 1)]

def medir(D, ms, N):
    erradas, psts = [], []
    for nome, (final, L) in D.items():
        d, certo = chamada(final, L, ms, N)
        if d is None: continue
        psts.append(d["pst"])
        if not certo: erradas.append(f"{nome} ({d['pst']}%, {int(d['n'])} seções)")
    return dict(disputas=len(D), chamadas=len(psts), erradas=len(erradas), quais=erradas, ic95=wilson(len(erradas), len(psts)),
                pst_mediana=statistics.median(psts) if psts else None, pst_max=max(psts) if psts else None)

def main():
    D = disputas()
    grupo = lambda n: n.split("_")[1]
    grupos = {a: {k: v for k, v in D.items() if grupo(k) == a} for a in ("2018", "2022", "2024", "2026")}
    grupos["presidente_governador"] = {k: v for k, v in D.items() if not k.startswith("prefeito")}
    grupos["prefeito"] = {k: v for k, v in D.items() if k.startswith("prefeito")}
    res = dict(grade={}, deixa_um_de_fora={})
    for r, ms in REGRAS.items():
        for N in NS:
            res["grade"][f"{r}|{N}"] = {g: medir(G, ms, N) for g, G in (("tudo", D), ("presidente_governador", grupos["presidente_governador"]), ("prefeito", grupos["prefeito"]))}
        for fora in ("2018", "2022", "2024", "2026", "prefeito", "presidente_governador"):
            treino = {k: v for k, v in D.items() if k not in grupos[fora]}
            ok = [N for N in NS if medir(treino, ms, N)["erradas"] == 0]
            N = min(ok) if ok else None
            res["deixa_um_de_fora"][f"{r}|fora={fora}"] = dict(N_escolhido=N, teste=medir(grupos[fora], ms, N) if N else None)
    # T42: a chamada de cada disputa pela regra decidida (R2 e 150 seções), para a figura do capítulo 7
    res["chamadas_R2_150"] = []
    for nome, (final, L) in sorted(D.items()):
        d, certo = chamada(final, L, REGRAS["R2"], 150)
        res["chamadas_R2_150"].append(dict(disputa=nome, cargo=nome.split("_")[0], final=final,
                                           pst=d and d["pst"], secoes=d and int(d["n"]), certo=certo))
    json.dump(res, open(os.path.join(SAI, "regra_secoes.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for k, v in res["deixa_um_de_fora"].items():
        t = v["teste"]; print(k, "N =", v["N_escolhido"], t and (t["erradas"], "de", t["chamadas"], t["quais"], "pst mediana", t["pst_mediana"]))
    for k, v in res["grade"].items():
        print(k, {g: (m["erradas"], m["pst_mediana"]) for g, m in v.items()})

if __name__ == "__main__":
    main()
