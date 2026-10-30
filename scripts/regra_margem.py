# T41, exploração: chamada pela margem. M(k, X): primeiro instante da grade fina com % apurado >= X em que os métodos da regra
# concordam e |projeção - 50| >= k * s(faixa), com s (erro típico da projeção na faixa de % apurado) medido só nas disputas de treino.
# Validação deixando um cargo ou um ano inteiro de fora. Sem senador (decisão do autor, 29/10). Lê as saídas de instantes (nada é reprojetado).
# Regras: ticket T41, "Chamada pela margem (exploração)" e "Regra de duas faixas". Uso: python -I scripts/regra_margem.py   (grava dados/projecoes_outras/regra_margem.json)
import os, csv, json, math, statistics
AQUI = os.path.dirname(os.path.abspath(__file__)); DADOS = os.path.join(AQUI, "..", "dados"); SAI = os.path.join(DADOS, "projecoes_outras")
KS = (0, 0.5, 1, 1.5, 2, 2.5, 3, 4, 5)
XS = (0.5, 1, 2.5, 5, 10)
FAIXAS = (1, 2.5, 5, 10, 20, 40, 60, 80, 100)  # limites de cima: (0-1], (1-2,5], ...
REGRAS = dict(R3="bcd", R2="cd")
# regra de duas faixas F(X, k): chama com X se a margem for >= k pontos; abaixo disso, espera ESPERA % apurado (pedido do autor, 29/10)
FXS = (2.5, 5); FKS = (0.5, 1, 1.5, 2, 2.5, 3); ESPERA = 15
META = 0.01; COBERTURA = 0.9

def disputas():
    """{disputa: dict(final, cargo, ano, L=[instantes])}: as 86 disputas de 2º turno."""
    D = {}
    def ler(p, nome=None, final=None, filtro=None):
        for r in csv.DictReader(open(p, encoding="utf-8"), delimiter=";"):
            if filtro and not filtro(r): continue
            d = nome or r["disputa"]; fin = final if final is not None else float(r["final"])
            cargo, ano = d.split("_")[:2]
            D.setdefault(d, dict(final=fin, cargo=cargo, ano=ano, L=[]))["L"].append({k: float(r[k]) for k in ("pst", "b", "c", "d")})
    ler(os.path.join(DADOS, "projecoes_2t", "instantes.csv"), "presidente_2026", 51.785, lambda r: r["conjunto"] == "fino")
    for a in ("governador_2026_instantes.csv", "teste2022_instantes.csv", "teste2018_instantes.csv", "teste2024_instantes.csv"):
        ler(os.path.join(SAI, a))
    for v in D.values(): v["L"].sort(key=lambda d: d["pst"])
    return D

def faixa(pst): return next(i for i, f in enumerate(FAIXAS) if pst <= f)
def proj(d, ms): return sum(d[m] for m in ms) / len(ms)

def erro_tipico(D, nomes, ms):
    """s por faixa: raiz do erro quadrático médio, média por disputa na faixa e depois entre disputas."""
    por = [[] for _ in FAIXAS]
    for n in nomes:
        v = D[n]; acc = {}
        for d in v["L"]: acc.setdefault(faixa(d["pst"]), []).append((proj(d, ms) - v["final"]) ** 2)
        for i, e in acc.items(): por[i].append(sum(e) / len(e))
    return [math.sqrt(sum(e) / len(e)) if e else None for e in por]

def chamar(v, ms, s, k, X, modo="M"):
    """(instante da chamada ou None, instantes errados que passam pela regra). M: margem >= k*s; F: margem >= k pontos ou >= ESPERA%."""
    certo = v["final"] > 50; cham = None; errados = 0
    for d in v["L"]:
        if len({d[m] > 50 for m in ms}) != 1: continue
        p = proj(d, ms)
        if modo == "F":
            if not (d["pst"] >= ESPERA or (d["pst"] >= X and abs(p - 50) >= k)): continue
        else:
            si = s[faixa(d["pst"])]
            if d["pst"] < X or si is None or abs(p - 50) < k * si: continue
        errados += (p > 50) != certo
        if cham is None: cham = d
    return cham, errados

def medir(D, nomes, ms, s, k, X, modo="M"):
    pst, erradas, sem, inst, esp, esp_err = [], [], [], 0, [], 0
    for n in nomes:
        v = D[n]; c, e = chamar(v, ms, s, k, X, modo); inst += e
        if c is None: sem.append(n); continue
        pst.append(c["pst"]); errou = (proj(c, ms) > 50) != (v["final"] > 50)
        if errou: erradas.append(f"{n} ({c['pst']}%)")
        if c["pst"] >= ESPERA: esp.append(n); esp_err += errou
    extra = dict(esperam_15=len(esp), quais_esperam_15=esp, erradas_com_15_ou_mais=esp_err) if modo == "F" else {}
    return extra | dict(disputas=len(nomes), chamadas=len(pst), chamadas_erradas=len(erradas), quais_erradas=erradas, sem_chamada=sem,
                chamada_pst_mediana=statistics.median(pst) if pst else None, chamada_pst_max=max(pst) if pst else None,
                chamadas_ate_50=sum(p <= 50 for p in pst), instantes_errados=inst)

def wilson(x, n, z=1.959964):
    if not n: return None
    p = x / n; den = 1 + z * z / n; cen = (p + z * z / (2 * n)) / den; meia = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [round(max(0, cen - meia), 4), round(min(1, cen + meia), 4)]

def escolher(D, nomes, ms, s, ks, modo="M"):
    linhas = []
    for k in ks:
        for X in (FXS if modo == "F" else XS):
            m = medir(D, nomes, ms, s, k, X, modo)
            taxa = m["chamadas_erradas"] / m["chamadas"] if m["chamadas"] else 1
            ok = taxa <= META and m["chamadas_ate_50"] >= COBERTURA * m["disputas"]
            med = m["chamada_pst_mediana"] if m["chamada_pst_mediana"] is not None else 999
            linhas.append((not ok, m["chamadas_erradas"] if not ok else 0, med, k, X, m))
    linhas.sort(key=lambda t: t[:5])
    _, _, _, k, X, m = linhas[0]
    return dict(k=k, X=X, cumpre_meta=not linhas[0][0], treino=m)

def somar(partes):
    t = dict(disputas=0, chamadas=0, chamadas_erradas=0, quais_erradas=[], sem_chamada=[], chamadas_ate_50=0, instantes_errados=0, _pst=[])
    for p in partes:
        for c in ("disputas", "chamadas", "chamadas_erradas", "chamadas_ate_50", "instantes_errados", "esperam_15", "erradas_com_15_ou_mais"):
            if c in p: t[c] = t.get(c, 0) + p[c]
        t["quais_erradas"] += p["quais_erradas"]; t["sem_chamada"] += p["sem_chamada"]; t["_pst"] += p["_pst"]
        if "quais_esperam_15" in p: t.setdefault("quais_esperam_15", []).extend(p["quais_esperam_15"])
    pst = t.pop("_pst")
    t["chamada_pst_mediana"] = statistics.median(pst) if pst else None; t["chamada_pst_max"] = max(pst) if pst else None
    t["taxa_erro"] = round(t["chamadas_erradas"] / t["chamadas"], 4) if t["chamadas"] else None
    t["ic95_wilson"] = wilson(t["chamadas_erradas"], t["chamadas"])
    return t

def validar(D, ms, chave, ks, fixo=None, modo="M"):
    grupos = sorted({v[chave] for v in D.values()}); rodadas = {}; partes = []
    for g in grupos:
        fora = [n for n, v in D.items() if v[chave] == g]; treino = [n for n, v in D.items() if v[chave] != g]
        s = erro_tipico(D, treino, ms)
        esc = dict(k=fixo[0], X=fixo[1]) if fixo else escolher(D, treino, ms, s, ks, modo)
        m = medir(D, fora, ms, s, esc["k"], esc["X"], modo)
        m["_pst"] = [chamar(D[n], ms, s, esc["k"], esc["X"], modo)[0]["pst"] for n in fora if n not in m["sem_chamada"]]
        partes.append(m)
        rodadas[g] = dict(escolha={k: v for k, v in esc.items() if k != "treino"},
                          treino=({c: esc["treino"][c] for c in ("disputas", "chamadas", "chamadas_erradas", "chamada_pst_mediana")} if "treino" in esc else None),
                          s_treino=[round(x, 3) if x is not None else None for x in s],
                          fora={c: v for c, v in m.items() if c != "_pst"} | dict(ic95_wilson=wilson(m["chamadas_erradas"], m["chamadas"])))
    return dict(rodadas=rodadas, fora_somado=somar(partes))

def main():
    D = disputas(); todos = list(D); res = dict(disputas=len(D), faixas_ate=FAIXAS, meta=META)
    for r, ms in REGRAS.items():
        for chave, rot in (("cargo", "por_cargo"), ("ano", "por_ano")):
            res[f"{r}|{rot}|margem"] = validar(D, ms, chave, KS)
            res[f"{r}|{rot}|so_pst"] = validar(D, ms, chave, (0,))
            res[f"{r}|{rot}|X10_fixo"] = validar(D, ms, chave, (0,), fixo=(0, 10))
            res[f"{r}|{rot}|duas_faixas"] = validar(D, ms, chave, FKS, modo="F")
        res[f"{r}|duas_faixas_grade_86_dentro_da_amostra"] = {f"{k}|{X}": {c: v for c, v in medir(D, todos, ms, None, k, X, "F").items() if c in ("chamadas_erradas", "quais_erradas", "chamada_pst_mediana", "esperam_15", "erradas_com_15_ou_mais")}
                                                             for k in FKS for X in FXS}
        s = erro_tipico(D, todos, ms); esc = escolher(D, todos, ms, s, KS)
        res[f"{r}|todas_86_dentro_da_amostra"] = dict(escolha=dict(k=esc["k"], X=esc["X"], cumpre_meta=esc["cumpre_meta"]),
                                                     s=[round(x, 3) for x in s], resultado=esc["treino"],
                                                     grade={f"{k}|{X}": {c: v for c, v in medir(D, todos, ms, s, k, X).items() if c in ("chamadas", "chamadas_erradas", "chamada_pst_mediana", "chamada_pst_max", "chamadas_ate_50")}
                                                            for k in KS for X in XS})
    json.dump(res, open(os.path.join(SAI, "regra_margem.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for k, v in res.items():
        if "|" not in k: continue
        if "grade" in k:
            for g, x in v.items(): print(k, g, x)
            continue
        if "rodadas" in v:
            f = v["fora_somado"]
            print(k, {g: (x["escolha"]["k"], x["escolha"]["X"], x["fora"]["chamadas_erradas"]) for g, x in v["rodadas"].items()},
                  {c: f[c] for c in ("chamadas", "chamadas_erradas", "taxa_erro", "ic95_wilson", "chamada_pst_mediana", "chamada_pst_max", "chamadas_ate_50", "instantes_errados", "esperam_15", "erradas_com_15_ou_mais") if c in f}, f["quais_erradas"], f["sem_chamada"])
        else:
            print(k, v["escolha"], v["s"], {c: v["resultado"][c] for c in ("chamadas", "chamadas_erradas", "chamada_pst_mediana", "chamada_pst_max")})

if __name__ == "__main__":
    main()
