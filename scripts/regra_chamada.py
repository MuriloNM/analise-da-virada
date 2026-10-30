# T41, exploração: regra de chamada do vencedor. R3(X): primeiro instante da grade fina com % apurado >= X em que (b), (c) e (d)
# apontam o mesmo vencedor; R2(X): o mesmo só com (c) e (d). Lê as saídas de instantes das projeções (nada é reprojetado).
# Regras: ticket T41, "Regra de chamada (exploração)". Uso: python -I scripts/regra_chamada.py   (grava dados/projecoes_outras/regra_chamada.json)
import os, csv, json, statistics
AQUI = os.path.dirname(os.path.abspath(__file__)); DADOS = os.path.join(AQUI, "..", "dados"); SAI = os.path.join(DADOS, "projecoes_outras")
XS = (0.5, 1, 2.5, 5, 10)
REGRAS = dict(R3="bcd", R2="cd")

def disputas():
    """{grupo: {disputa: (final, [instantes da grade fina])}}; dentro = as 35 disputas já vistas, fora = 2024, senador = 1º turno (2022, 2018, 2026)."""
    g = dict(dentro={}, fora={}, senador={})
    def ler(p, grupo, nome=None, final=None, filtro=None):
        if not os.path.exists(p): return
        for r in csv.DictReader(open(p, encoding="utf-8"), delimiter=";"):
            if filtro and not filtro(r): continue
            d = nome or r["disputa"]; fin = final if final is not None else float(r["final"])
            g[grupo].setdefault(d, (fin, []))[1].append({k: float(r[k]) for k in ("pst", "b", "c", "d")})
    ler(os.path.join(DADOS, "projecoes_2t", "instantes.csv"), "dentro", "presidente_2026", 51.785, lambda r: r["conjunto"] == "fino")
    for a in ("governador_2026_instantes.csv", "teste2022_instantes.csv", "teste2018_instantes.csv"): ler(os.path.join(SAI, a), "dentro")
    ler(os.path.join(SAI, "teste2024_instantes.csv"), "fora")
    ler(os.path.join(SAI, "senador_instantes.csv"), "senador")
    for ano in ("2022", "2018", "2026"): g["senador_" + ano] = {d: v for d, v in g["senador"].items() if d.startswith(f"senador_{ano}_")}
    g["fora_e_senador"] = {**g["fora"], **g["senador"]}
    return g

def medir(D, ms, X):
    chamadas, erradas, inst_err, inst_conc, esperas, tarde, ate50 = [], [], 0, 0, [], 0, 0
    for nome, (final, L) in D.items():
        L = sorted((d for d in L if d["pst"] >= X), key=lambda d: d["pst"])
        certo = final > 50
        conc = [d for d in L if len({d[m] > 50 for m in ms}) == 1]
        inst_conc += len(conc); inst_err += sum((d[ms[0]] > 50) != certo for d in conc)
        if not conc: continue
        c = conc[0]; chamadas.append(c["pst"]); esperas.append(c["pst"] - X)
        tarde += c["pst"] > X + 5; ate50 += c["pst"] <= 50
        if (c[ms[0]] > 50) != certo: erradas.append(f"{nome} ({c['pst']}%)")
    n = len(D)
    return dict(disputas=n, chamadas=len(chamadas), chamadas_erradas=len(erradas), quais_erradas=erradas,
                instantes_concordando=inst_conc, instantes_errados=inst_err,
                chamada_pst_mediana=statistics.median(chamadas) if chamadas else None, chamada_pst_max=max(chamadas) if chamadas else None,
                espera_mediana=statistics.median(esperas) if esperas else None, espera_max=max(esperas) if esperas else None,
                chamadas_depois_de_X_mais_5=tarde, chamadas_ate_50=ate50,
                limite_regra_dos_tres=round(3 / n, 3) if n and not erradas else None)

def main():
    G = disputas(); res = {}
    for grupo, D in G.items():
        if not D: continue
        for r, ms in REGRAS.items():
            for X in XS: res[f"{grupo}|{r}|{X}"] = medir(D, ms, X)
    # a sustentação: menor X com 0 chamadas erradas, 0 instantes errados e chamada até 50% em >= 90% das disputas, fora da amostra
    sust = {}
    for grupo in ("fora", "senador", "fora_e_senador"):
        for r in REGRAS:
            q = lambda X: res.get(f"{grupo}|{r}|{X}")
            ok = [X for X in XS if q(X) and q(X)["chamadas_erradas"] == 0 and q(X)["instantes_errados"] == 0 and q(X)["chamadas_ate_50"] >= 0.9 * q(X)["disputas"]]
            sust[r if grupo == "fora" else f"{grupo}|{r}"] = min(ok) if ok else None
    res["_sustenta_com_X"] = sust
    json.dump(res, open(os.path.join(SAI, "regra_chamada.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for k, v in res.items():
        if k.startswith("_"): print(k, v); continue
        print(k, {c: v[c] for c in ("disputas", "chamadas", "chamadas_erradas", "instantes_concordando", "instantes_errados",
                                     "chamada_pst_mediana", "chamada_pst_max", "espera_max", "chamadas_depois_de_X_mais_5", "chamadas_ate_50")}, v["quais_erradas"])

if __name__ == "__main__":
    main()
