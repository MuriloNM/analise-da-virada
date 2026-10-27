"""Dados da página do estudo (T07, esqueleto; T08, aba Análise e números do topo).

Lê só arquivos já gerados e aprovados e grava site-analise/dados.js:
- dados/analise_estados.csv e dados/analise_municipios.csv (T03);
- dados/inferencia.json (T06, com as correções do parecer estatístico no T32; desde o T35, a estimativa por lugar é a conta por seção);
- dados/historico_2t.json (histórico da apuração ao vivo do 2º turno);
- dados/escala_partidos.csv (T05), para a tabela partido → posição de Método e fontes (T12);
- dados/dados_sociais_municipios.json (T26), os dados sociais de cada município, e os 35 testes do
  inferencia.json (T34);
- dados/exploracao.json (T33), as cinco perguntas da exploração guiada;
- os títulos das notas de docs/analise/NOTAS.md, que vão para o catálogo de textos
  (site-analise/textos/pt-BR.js, bloco das notas; T30): dados.js guarda só os códigos.

Não faz conta nova. As contagens vão inteiras; as fatias, taxas e variações das
unidades são refeitas das contagens com o valor completo e conferidas contra o
CSV do T03 (que tem 4 casas). A página arredonda uma vez, na hora de mostrar
(diário, D25). As retas desenhadas nas dispersões são conferidas contra as
versões "Brasil" do T06.

    python -I scripts/pagina_dados.py
"""
import csv
import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parent.parent
DADOS = RAIZ / "dados"
SAIDA = RAIZ / "site-analise" / "dados.js"
CATALOGO = RAIZ / "site-analise" / "textos" / "pt-BR.js"
INICIO_NOTAS, FIM_NOTAS = "// <notas sobre os dados:", "// </notas sobre os dados>"
MINUSCULAS = {"de", "da", "do", "das", "dos", "e", "di", "du"}
TOL = 6e-5  # o CSV do T03 tem 4 casas

problemas = []


def confere(ok, texto):
    print(("OK: " if ok else "ERRO: ") + texto)
    if not ok:
        problemas.append(texto)


def br(n):
    return f"{n:,}".replace(",", ".")


def nome_proprio(nome):
    """SÃO JOÃO D'ALIANÇA -> São João d'Aliança (só para exibir; igual ao ateliê)."""
    palavras = []
    for i, p in enumerate(nome.lower().split(" ")):
        partes = []
        for q in p.split("-"):
            if q.startswith("d'") and len(q) > 2:
                q = "d'" + q[2:].capitalize()
            elif not (i > 0 and q in MINUSCULAS):
                q = q.capitalize()
            partes.append(q)
        palavras.append("-".join(partes))
    return " ".join(palavras)


def derivados(L1, F1, O1, E1, C1, L2, F2, E2, C2):
    """Fórmulas da seção 4 da especificação, com o valor completo. None quando não há valor (nota N09)."""
    d = {}
    d["s1"] = 100 * L1 / (L1 + F1) if L1 + F1 else None
    d["s2"] = 100 * L2 / (L2 + F2) if L2 + F2 else None
    d["ds"] = d["s2"] - d["s1"] if d["s1"] is not None and d["s2"] is not None else None
    ganho = (L2 - L1) + (F2 - F1)
    d["cap"] = 100 * (L2 - L1) / ganho if ganho > 0 else None
    d["a1"] = 100 * (E1 - C1) / E1
    d["a2"] = 100 * (E2 - C2) / E2
    d["da"] = d["a2"] - d["a1"]
    return d


def perto(a, b, tol=TOL):
    if a is None or b in ("", None):
        return a is None and b in ("", None)
    return abs(a - float(b)) <= tol


# --- Brasil, regiões e UFs (T03) --------------------------------------------
print("## Brasil, regiões e UFs (dados/analise_estados.csv)")
estados = list(csv.DictReader(open(DADOS / "analise_estados.csv", encoding="utf-8")))
BR_DM = int(next(r for r in estados if r["nivel"] == "brasil")["var_dif"])


def unidade(r):
    i = {k: int(r[c]) for k, c in {
        "E1": "eleitorado_1t", "C1": "comparecimento_1t", "L1": "lula_1t", "F1": "flavio_1t",
        "O1": "outros_1t", "BN1": "brancos_nulos_1t", "E2": "eleitorado_2t", "C2": "comparecimento_2t",
        "L2": "lula_2t", "F2": "flavio_2t", "BN2": "brancos_nulos_2t", "M1": "dif_1t", "M2": "dif_2t",
        "dM": "var_dif", "n": "municipios"}.items()}
    d = derivados(i["L1"], i["F1"], i["O1"], i["E1"], i["C1"], i["L2"], i["F2"], i["E2"], i["C2"])
    for k, c in {"s1": "fatia_lula_1t_pct", "s2": "fatia_lula_2t_pct", "ds": "var_fatia_pp",
                 "cap": "captura_lula_pct", "a1": "taxa_abst_1t_pct", "a2": "taxa_abst_2t_pct",
                 "da": "var_taxa_abst_pp"}.items():
        if not perto(d[k], r[c]):
            problemas.append(f"{r['codigo']}: {k} refeito ({d[k]}) diferente do CSV ({r[c]})")
    peso = 100 * i["dM"] / BR_DM
    if not perto(peso, r["peso_virada_pct"], 5e-6):
        problemas.append(f"{r['codigo']}: peso refeito diferente do CSV")
    u = {"codigo": r["codigo"], "nome": r["nome"], "regiao": r["regiao"]}
    u.update(i)
    u.update({k: (round(v, 8) if v is not None else None) for k, v in d.items()})
    u["peso"] = round(peso, 8)
    return u


brasil = unidade(next(r for r in estados if r["nivel"] == "brasil"))
regioes = [unidade(r) for r in estados if r["nivel"] == "regiao"]
ufs = [unidade(r) for r in estados if r["nivel"] == "uf"]
erros_unid = [p for p in problemas]
confere(not erros_unid, "fatias, captura, taxas de abstenção e peso refeitos das contagens iguais ao CSV do T03, em todas as unidades")

esperado = {"L1": 53879538, "F1": 56104503, "L2": 64256232, "F2": 59826041,
            "M1": -2224965, "M2": 4430191, "dM": 6655156}
for k, v in esperado.items():
    confere(brasil[k] == v, f"Brasil {k} = {br(brasil[k])} (especificação, seção 2: {br(v)})")
confere(round(brasil["s1"], 3) == 48.989 and round(brasil["s2"], 3) == 51.785,
        f"fatia do Lula no Brasil {brasil['s1']:.3f}% e {brasil['s2']:.3f}% (seção 2: 48,989% e 51,785%)")
confere(round(brasil["cap"], 1) == 73.6, f"captura do Brasil {brasil['cap']:.4f}% (seção 2: 73,6%)")
confere(sum(u["dM"] for u in regioes) == brasil["dM"], "soma das regiões (com o exterior) = mudança da diferença no Brasil")
confere(sum(u["dM"] for u in ufs) == brasil["dM"], "soma das UFs (com o exterior) = mudança da diferença no Brasil")
confere(len(ufs) == 28 and len(regioes) == 6, "28 UFs e 6 regiões, contando o exterior")
# D73: de onde vieram os votos a mais (achado do Resumo e "Como calculamos"): os votos que os dois
# ganharam = aumento do comparecimento + votos dos outros no 1º turno + queda de brancos e nulos
fontes_ok = [u["codigo"] for u in [brasil, *regioes, *ufs]
             if (u["L2"] + u["F2"]) - (u["L1"] + u["F1"]) != (u["C2"] - u["C1"]) + u["O1"] + (u["BN1"] - u["BN2"])]
confere(not fontes_ok, "votos a mais dos dois = comparecimento + outros do 1º turno + queda de brancos e nulos, "
        f"no Brasil, nas regiões e nas UFs (Brasil: {br(brasil['C2'] - brasil['C1'])} + {br(brasil['O1'])} + "
        f"{br(brasil['BN1'] - brasil['BN2'])} = {br(brasil['L2'] + brasil['F2'] - brasil['L1'] - brasil['F1'])})")

# --- Municípios (T03) ---------------------------------------------------------
print("\n## Municípios (dados/analise_municipios.csv)")
mun = list(csv.DictReader(open(DADOS / "analise_municipios.csv", encoding="utf-8")))
# T34: os 7 dados sociais (T26) vão no fim de cada linha, arredondados para mostrar (1 casa nos %, o PIB por habitante em
# reais, a densidade com as 2 casas publicadas); vazio no exterior e em Boa Esperança do Norte (N20). Os testes usam o valor completo.
SOC = json.load(open(DADOS / "dados_sociais_municipios.json", encoding="utf-8"))
SOC_CAMPOS = {"p60": ("pct_60mais", 1), "alf": ("alfab_15mais", 1), "ren": ("pct_renda_ate_meio_sm", 1), "pib": ("pib_pc", 0),
              "den": ("densidade", 2), "eva": ("pct_evangelicos", 1), "ppa": ("pct_pretos_pardos", 1)}
CAMPOS_MUN = ["nome", "uf", "cap", "porte", "E1", "C1", "L1", "F1", "O1", "E2", "C2", "L2", "F2"] + list(SOC_CAMPOS)


def social(cd):
    d = SOC["municipios"].get(cd)
    out = []
    for k, (campo, casas) in SOC_CAMPOS.items():
        v = None if d is None else d.get(campo)
        out.append("" if v is None else (f"{v:.{casas}f}" if casas else str(round(v))))
    return out
linhas = []
dif_mun = 0
ident = 0
for r in mun:
    v = {k: int(r[c]) for k, c in {"E1": "eleitorado_1t", "C1": "comparecimento_1t", "L1": "lula_1t",
                                    "F1": "flavio_1t", "O1": "outros_1t", "E2": "eleitorado_2t",
                                    "C2": "comparecimento_2t", "L2": "lula_2t", "F2": "flavio_2t"}.items()}
    # a página refaz brancos e nulos e os válidos destas contagens: conferir que fecham
    if (int(r["validos_1t"]) != v["L1"] + v["F1"] + v["O1"] or int(r["validos_2t"]) != v["L2"] + v["F2"]
            or int(r["brancos_nulos_1t"]) != v["C1"] - int(r["validos_1t"])
            or int(r["brancos_nulos_2t"]) != v["C2"] - int(r["validos_2t"])):
        ident += 1
    d = derivados(v["L1"], v["F1"], v["O1"], v["E1"], v["C1"], v["L2"], v["F2"], v["E2"], v["C2"])
    for k, c in {"s1": "fatia_lula_1t_pct", "s2": "fatia_lula_2t_pct", "ds": "var_fatia_pp",
                 "cap": "captura_lula_pct", "a1": "taxa_abst_1t_pct", "a2": "taxa_abst_2t_pct",
                 "da": "var_taxa_abst_pp"}.items():
        if not perto(d[k], r[c]):
            dif_mun += 1
    cap = {"capital": "1", "interior": "0", "exterior": "0"}[r["capital_interior"]]
    linhas.append("|".join([nome_proprio(r["municipio"]), r["uf"], cap, r["porte"]]
                           + [str(v[k]) for k in CAMPOS_MUN[4:13]] + social(r["cd_tse"])))
confere(len(mun) == 5757, f"{br(len(mun))} municípios, contando os {sum(r['uf'] == 'ZZ' for r in mun)} do exterior")
confere(ident == 0, "válidos e brancos e nulos fecham com as contagens em todos os municípios")
confere(dif_mun == 0, "fatias, Δs, captura e abstenção refeitas iguais ao CSV do T03 em todos os municípios")
COLS = {"L1": "lula_1t", "F1": "flavio_1t", "L2": "lula_2t", "F2": "flavio_2t", "O1": "outros_1t",
        "C1": "comparecimento_1t", "C2": "comparecimento_2t", "E1": "eleitorado_1t", "E2": "eleitorado_2t"}
diferentes = [k for k, c in COLS.items() if sum(int(r[c]) for r in mun) != brasil[k]]
confere(not diferentes, "soma dos municípios = Brasil em votos, comparecimento e eleitorado dos dois turnos"
        + (f" (diferente em {', '.join(diferentes)})" if diferentes else ""))

# --- Inferência (T06) ---------------------------------------------------------
print("\n## Inferência (dados/inferencia.json)")
inf = json.load(open(DADOS / "inferencia.json", encoding="utf-8"))
# T35 (P28): a conta por seção, para os textos do capítulo 4, do Método e das notas N16, N21 e N22
sec = json.load(open(DADOS / "secoes_inferencia.json", encoding="utf-8"))
bra = [r for r in mun if r["uf"] != "ZZ"]


def reta(xs, ys, ws):
    """Mínimos quadrados ponderados, só para desenhar a reta da dispersão."""
    W = sum(ws)
    mx = sum(w * x for w, x in zip(ws, xs)) / W
    my = sum(w * y for w, y in zip(ws, ys)) / W
    b = sum(w * (x - mx) * (y - my) for w, x, y in zip(ws, xs, ys)) / sum(w * (x - mx) ** 2 for w, x in zip(ws, xs))
    return my - b * mx, b


ws = [int(r["eleitorado_1t"]) for r in bra]
s1 = [100 * int(r["lula_1t"]) / (int(r["lula_1t"]) + int(r["flavio_1t"])) for r in bra]
s2 = [100 * int(r["lula_2t"]) / (int(r["lula_2t"]) + int(r["flavio_2t"])) for r in bra]
ds = [b - a for a, b in zip(s1, s2)]
o = [100 * int(r["outros_1t"]) / int(r["validos_1t"]) for r in bra]
retas = {}
for h, xs in (("H1", s1), ("H3", o)):
    a, b = reta(xs, ds, ws)
    ref = next(v for v in inf["hipoteses"][h]["versoes"] if v["versao"] == f"{h} Brasil")["coef"]
    confere(abs(b - ref) < 5e-6, f"reta da dispersão do capítulo {h[1]} = versão \"{h} Brasil\" do T06 ({b:.6f} contra {ref:.6f} por ponto)")
    retas[h] = {"a": round(a, 6), "b": round(b, 6)}

for h, x in inf["hipoteses"].items():
    cont = {"confirmada": 0, "contrária": 0, "inconclusiva": 0}
    for v in x["versoes"][1:]:
        cont[v["classificacao"]] += 1
    confere(cont == x["conferencias"] and x["versoes"][0]["versao"].endswith("principal")
            and x["versoes"][0]["classificacao"] == x["classificacao"],
            f"{h}: classificação {x['classificacao']} e conferências {x['conferencias']} batem com as versões")
for c in ("federal", "estadual", "senador"):
    x = inf["H5"][c]
    cont = {"confirmada": 0, "contrária": 0, "inconclusiva": 0}
    for v in x["versoes"][1:]:
        cont[v["classificacao"]] += 1
    confere(cont == x["conferencias"] and x["versoes"][0]["classificacao"] == x["classificacao"],
            f"H5 {c}: classificação {x['classificacao']} e conferências batem com as versões")
confere(len(inf["por_lugar"]) == 33 and len(inf["nao_deu"]) == 17 and len(inf["por_lugar_municipios"]) == 33,
        f"estimativa por lugar: {len(inf['por_lugar'])} lugares e {len(inf['nao_deu'])} estimativas que não deram (T35, conta por seção, P28: 33 e 17; "
        "por município, no T32, 62; no T06, 55)")
confere(sec["por_lugar"] == inf["por_lugar"] and sec["meta"]["votos_28"] == 5246 and sec["meta"]["secoes_com_exterior"] == 499248,
        "a estimativa por lugar do inferencia.json é a do secoes_inferencia.json (T35), com os 5.246 votos do 28 e as 499.248 seções da nota N22")
confere(not any(l["modelo_nao_descreve"] for l in inf["por_lugar"])
        and inf["por_lugar"][0]["secoes"] == 497897 and inf["ecologica"]["secoes"]["C"] == {k: inf["por_lugar"][0]["fontes"]["C"][k] for k in ("lula", "lula_ic95", "flavio", "flavio_ic95")},
        "conta por seção (T35): 497.897 seções no Brasil, nenhuma estimativa fora de 0% a 100% (sem marca †), e o Brasil do capítulo 3 é o mesmo da estimativa por lugar")
confere(all(l["fontes"][c]["aviso_modelo"] == bool(l["modelo_nao_descreve"]) for l in inf["por_lugar"] if l["n"] >= 30 for c in "OCR"),
        "aviso \"o modelo não descreve bem este lugar\" em todas as fontes dos lugares com alguma fonte fora de 0% a 100% (T32, m1)")


# T32 (M5): a página mostra o intervalo do bootstrap selvagem (por inversão do teste) em "ic95" e o do erro agrupado em
# "ic95_cr1". A classificação usa os dois: confirmada = os dois intervalos inteiros do lado previsto (HIPOTESES.md, nota do T32).
def ic_da_pagina(v):
    v = dict(v)
    if v.get("ic95_selvagem"):
        v["ic95_cr1"], v["ic95"] = v["ic95"], v["ic95_selvagem"]
    v.pop("ic95_selvagem", None)
    return v


def confere_classe(v):
    if not v.get("classificacao"):
        return True
    lado = lambda ic: 1 if ic[0] > 0 else -1 if ic[1] < 0 else 0
    s_ = -1 if v["previsto"] == "negativo" else 1
    a, b = lado(v["ic95"]), lado(v["ic95_cr1"])
    esperado = "confirmada" if a == b == s_ else "contrária" if a == b == -s_ else "inconclusiva"
    return esperado == v["classificacao"]


hip_pag = {h: x | {"versoes": [ic_da_pagina(v) for v in x["versoes"]]} for h, x in inf["hipoteses"].items()}
compl_pag = {h: [ic_da_pagina(v) for v in vs] for h, vs in inf["complementos"].items()}
h5_pag = {k: (x | {"versoes": [ic_da_pagina(v) for v in x["versoes"]]}) if isinstance(x, dict) and "versoes" in x else x
          for k, x in inf["H5"].items()}
todas = [v for x in hip_pag.values() for v in x["versoes"]] + [v for c in ("federal", "estadual", "senador") for v in h5_pag[c]["versoes"]]
confere(all(confere_classe(v) for v in todas),
        f"classificação de todas as {len(todas)} versões = os dois intervalos (bootstrap e erro agrupado) do mesmo lado (T32, M5)")
confere(abs(inf["especificacoes_outros"]["principal"] - inf["ecologica"]["brasil"]["O"]["lula"]) < 1e-9,
        "as três especificações dos votos dos outros partem da mesma estimativa principal do capítulo 3")
for f in ("O", "C", "R"):
    e = inf["ecologica"]["brasil"][f]
    confere(abs(e["lula"] + e["flavio"] - 1) < 1e-6, f"regressão ecológica, Brasil, fonte {f}: Lula + Flávio = 100%")
fontes_sem_exterior = {"O": sum(int(r["outros_1t"]) for r in bra),
                       "C": sum(int(r["comparecimento_2t"]) - int(r["comparecimento_1t"]) for r in bra),
                       "R": -sum((int(r["comparecimento_2t"]) - int(r["validos_2t"])) - (int(r["comparecimento_1t"]) - int(r["validos_1t"])) for r in bra)}
confere(fontes_sem_exterior["C"] == inf["por_lugar"][0]["var_comparecimento"],
        f"variação do comparecimento sem o exterior {br(fontes_sem_exterior['C'])} = a do T06")

# a variação do Lula nos rankings e na ficha usa as mesmas contagens: conferir o funil
f = inf["funil"]["var_fatia"]
centro = 100 * sum(int(r["lula_2t"]) for r in bra) / sum(int(r["lula_2t"]) + int(r["flavio_2t"]) for r in bra) \
    - 100 * sum(int(r["lula_1t"]) for r in bra) / sum(int(r["lula_1t"]) + int(r["flavio_1t"]) for r in bra)
confere(abs(centro - f["centro_pp"]) < 1e-4, f"centro do funil da fatia {centro:.4f} = T06 ({f['centro_pp']})")


def funil(x):
    return {k: x[k] for k in ("centro_pp", "theta", "razao_votos_eleitorado", "phi", "tau2_pp2", "n",
                              "fora95", "fora998", "fora998_acima", "fora998_abaixo", "fora95_acima", "fora95_abaixo",
                              "por_porte", "curva")} | {"winsorizado": {k: x["conferencia_winsorizado"][k] for k in ("tau2_pp2", "fora95", "fora998")}} | {
        "mudam_de_lado_998": x["conferencia_votos_proprios"]["mudam_de_lado_998"]}


# --- Histórico da apuração ao vivo ---------------------------------------------
print("\n## Histórico da apuração ao vivo (dados/historico_2t.json)")
hist = json.load(open(DADOS / "historico_2t.json", encoding="utf-8"))
pontos = inf["projecao"]["pontos"]
por_apurado = {round(h[0], 2): h for h in hist}
ok_hist = len(pontos) == len(hist) - 1 and hist[-1][0] == 100.0
for p in pontos:
    h = por_apurado.get(round(p["apurado"], 2))
    if h is None or abs(h[1] - p["parcial"]) > 1e-9 or abs(h[3] - p["projecao"]) > 1e-9:
        ok_hist = False
        continue
    p["hora"] = h[4]
confere(ok_hist, f"{len(pontos)} leituras do T06 iguais ao histórico, mais a final de 100% ({hist[-1][1]}%)")
confere(abs(hist[-1][1] - round(brasil["s2"], 3)) < 1e-9, "a leitura de 100% é o resultado final (51,785%)")

# --- Dados sociais: os 35 testes (T34; HIPOTESES.md, seção 6) ---------------------
print("\n## Dados sociais (dados/dados_sociais_municipios.json e inferencia.json, T34)")
soc = inf["sociais"]
CHAVE_SOC = {campo: k for k, (campo, _) in SOC_CAMPOS.items()}
CHAVE_SOC.update({"ln_pib_pc": "pib", "ln_densidade": "den"})


def holm(ps):
    ordem = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, corrida = [0.0] * len(ps), 0.0
    for k, i in enumerate(ordem):
        corrida = max(corrida, min(1.0, (len(ps) - k) * ps[i]))
        adj[i] = corrida
    return adj


confere(len(soc["testes"]) == 35 and len({(t["variavel"], t["desfecho"]) for t in soc["testes"]}) == 35,
        "35 testes, um por variável × desfecho")
for ver in ("principal", "brasil"):
    hs = holm([t[ver]["p_selvagem"] for t in soc["testes"]])
    hc = holm([t[ver]["p_cr1"] for t in soc["testes"]])
    ok_h = all(abs(a - t[ver]["p_holm"]) < 1e-4 and abs(b - t[ver]["p_cr1_holm"]) < 1e-6
               and t[ver]["associacao"] == (a < 0.05 and b < 0.05) for t, a, b in zip(soc["testes"], hs, hc))
    confere(ok_h, f"{ver}: Holm refeito igual ao do inferencia.json e \"há associação\" = os dois valores-p corrigidos abaixo de 0,05")
n_assoc = sum(t["principal"]["associacao"] for t in soc["testes"])
confere(n_assoc == soc["com_associacao"], f"{n_assoc} de 35 com associação na versão dentro dos estados")
mun_soc = [SOC["municipios"][r["cd_tse"]] for r in bra]
com = [d for d in mun_soc if d["pct_60mais"] is not None]
confere(len(com) == 5570 == soc["municipios_com_dados"], f"{br(len(com))} municípios com dados sociais (sem Boa Esperança do Norte, N20)")


def mediana(vs):
    vs = sorted(vs)
    n = len(vs)
    return vs[n // 2] if n % 2 else (vs[n // 2 - 1] + vs[n // 2]) / 2


testes_pag = []
for t in soc["testes"]:
    pr, bx = ic_da_pagina(t["principal"]), ic_da_pagina(t["brasil"])
    larg = pr["quartis_x"][1] - pr["quartis_x"][0]  # largura entre os quartis da variável, dentro do estado
    testes_pag.append({"var": CHAVE_SOC[t["variavel"]], "desfecho": t["desfecho"], "larg_quartis": round(larg, 6),
                       **{ver: {k: v[k] for k in ("n", "grupos", "coef", "ic95", "ic95_cr1", "p_selvagem", "p_cr1", "p_holm", "p_cr1_holm",
                                                  "efeito_interquartil_pp", "associacao", "direcao", "pequena", "r2")}
                          for ver, v in (("principal", pr), ("brasil", bx))}})
# o efeito entre quartis tem o mesmo intervalo do coeficiente, multiplicado pela largura entre os quartis
confere(all(abs(t["principal"]["coef"] * t["larg_quartis"] - t["principal"]["efeito_interquartil_pp"]) < 1e-3 for t in testes_pag),
        "efeito entre quartis = coeficiente × largura entre os quartis, em todos os testes")
por = {(t["var"], t["desfecho"]): t["principal"] for t in testes_pag}
# o que a resposta curta do capítulo 8 diz (catálogo c8.resposta) tem de valer nos dados
confere(por[("ren", "cap")]["associacao"] and por[("ren", "cap")]["direcao"] == "positiva"
        and all(not por[(k, "cap")]["associacao"] for k in SOC_CAMPOS if k != "ren")
        and all(por[(k, "ds")]["pequena"] for k in SOC_CAMPOS if por[(k, "ds")]["associacao"]),
        "resposta do capítulo 8: renda × captura positiva; nas outras seis, captura sem associação e fatia só com associações pequenas")
sociais_pag = {
    "testes": testes_pag, "com_associacao": n_assoc, "municipios": soc["municipios_com_dados"], "captura_amostra": soc["captura_amostra"],
    "variaveis": {CHAVE_SOC[v]: {"ano": m["ano"], "fonte": m["fonte"], "url": m["url"]} for v, m in soc["variaveis"].items()},
    "medianas": {k: round(mediana([d[campo] for d in com]), 4) for k, (campo, _) in SOC_CAMPOS.items()},
}


# como as características andam juntas (capítulo 8, "Ver detalhes"): correlação de Pearson entre os 5.570 municípios,
# cada um contando igual, com o PIB por habitante e a densidade em logaritmo, como nos testes. Não usa a eleição.
def correlacao(a, b):
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    sab = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    return sab / (sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b)) ** 0.5


CAMPO_TESTE = [("pct_60mais"), ("alfab_15mais"), ("pct_renda_ate_meio_sm"), ("ln_pib_pc"), ("ln_densidade"), ("pct_evangelicos"),
               ("pct_pretos_pardos")]
colunas_soc = [[d[c] for d in com] for c in CAMPO_TESTE]
sociais_pag["correlacoes"] = [[round(correlacao(a, b), 4) for b in colunas_soc] for a in colunas_soc]
confere(all(abs(sociais_pag["correlacoes"][i][i] - 1) < 1e-9 for i in range(7)) and list(SOC_CAMPOS) == ["p60", "alf", "ren", "pib", "den", "eva", "ppa"],
        "correlações entre as 7 características, na ordem da página")
confere(sociais_pag["correlacoes"][2][1] < -0.5 and sociais_pag["correlacoes"][2][3] < -0.5 and sociais_pag["correlacoes"][2][6] > 0.5,
        "o que a nota do capítulo 8 diz: municípios com mais baixa renda têm menos alfabetização, PIB por habitante menor e mais pretos e pardos")
# os títulos das figuras do capítulo 8 dizem o resultado: conferir que ele vale
assoc_de = lambda d: [k for k in SOC_CAMPOS if por[(k, d)]["associacao"]]
confere(assoc_de("cap") == ["ren"] and por[("ren", "cap")]["direcao"] == "positiva", "figura 8.1, votos a mais: só a renda, a favor do Lula")
confere(por[("den", "gL")]["associacao"] and por[("den", "gF")]["associacao"]
        and por[("den", "gL")]["direcao"] == por[("den", "gF")]["direcao"] == "positiva"
        and not por[("den", "cap")]["associacao"] and not por[("den", "ds")]["associacao"],
        "figura 8.2, votos: nas mais densas, mais votos para os dois, e a parte de cada um e a fatia sem associação")
confere(all(por[(k, "ds")]["pequena"] for k in assoc_de("ds")), "figura 8.2, fatia: todas as associações pequenas")
confere(assoc_de("da") == ["ren"] and por[("ren", "da")]["pequena"] and por[("ren", "da")]["direcao"] == "positiva",
        "figura 8.2, abstenção: só a renda, pequena, abstenção maior (caiu menos ou subiu mais)")

# --- Notas sobre os dados (títulos, para a marca "ver nota N") -----------------
notas = [{"id": m.group(1), "titulo": m.group(2).strip()}
         for m in re.finditer(r"^### (N\d\d)\. (.+)$", (RAIZ / "docs" / "analise" / "NOTAS.md").read_text(encoding="utf-8"), re.M)]
confere(len(notas) >= 17 and [n["id"] for n in notas] == [f"N{i:02d}" for i in range(1, len(notas) + 1)],
        f"{len(notas)} notas, numeradas em sequência")

# --- Exploração guiada (T33; HIPOTESES.md, seção 8, rodada 1): as cinco perguntas, com o resultado de todas ---
print("\n## Exploração guiada (dados/exploracao.json, T33)")
exp = json.load(open(DADOS / "exploracao.json", encoding="utf-8"))
mu_br = [r for r in csv.DictReader(open(DADOS / "analise_municipios.csv", encoding="utf-8")) if r["uf"] != "ZZ"]
def lado_(a, b): return "Lula" if a > b else "Flávio" if b > a else "empate"
trocas = {}
for r in mu_br:
    k = f'{lado_(int(r["lula_1t"]), int(r["flavio_1t"]))} → {lado_(int(r["lula_2t"]), int(r["flavio_2t"]))}'
    trocas[k] = trocas.get(k, 0) + 1
e2 = exp["E2"]["brasil"]
confere({k: v["n"] for k, v in e2["casas"].items()} == trocas and sum(trocas.values()) == 5571,
        f"E2: as trocas de lado refeitas do analise_municipios.csv batem ({trocas.get('Flávio → Lula')} Flávio → Lula, {trocas.get('Lula → Flávio')} Lula → Flávio)")
subiu = sum(float(r["var_fatia_pp"]) > 0 for r in mu_br)
confere(e2["fatia_lula"]["subiu"]["n"] == subiu, f"E2: a fatia do Lula subiu em {subiu} municípios")
e1br = exp["E1"]["por_lugar"][0]["fontes"]
# o que a resposta curta do capítulo 9 diz (catálogo c9.resposta) tem de valer nos dados
confere(exp["E1"]["achado_brasil"].get("70") == "Lula" and exp["E1"]["achado_brasil"].get("55") == "Flávio"
        and e1br["14"]["maior_parte"] == "sem lado claro",
        "E1: no Brasil, Augusto Cury com a maior parte para o Lula, Caiado para o Flávio, Renan Santos sem lado claro (c9.resposta)")
confere(all(abs(e1br[c]["lula"] + e1br[c]["flavio"] - 1) < 1e-9 for c in e1br), "E1: as partes dos dois somam 100% em cada fonte")
confere(not any(d["achado"] for d in exp["E3"]["desfechos"].values()) and exp["E4"]["achado"] and exp["E5"]["achado"],
        "E3 sem achado; E4 e E5 com achado pela regra registrada (c9.lista)")
# as casas da E2 vão para a página com códigos (ll, ff, fl, lf; o resto, empate em algum turno): o texto fica no catálogo
CASA = {"Lula → Lula": "ll", "Flávio → Flávio": "ff", "Flávio → Lula": "fl", "Lula → Flávio": "lf"}
def casas(d, campo="n"):
    out = {"ll": 0, "ff": 0, "fl": 0, "lf": 0, "emp": 0}
    for k, v in d.items(): out[CASA.get(k, "emp")] += v[campo] if isinstance(v, dict) else v
    return out
exploracao_pag = {
    "rotulo": exp["meta"]["rotulo"], "secoes": exp["meta"]["secoes"],
    "E1": {"por_lugar": [{"lugar": l["lugar"], "nivel": l["nivel"], "fontes": {c: {k: d[k] for k in ("lula", "lula_ic95", "flavio", "flavio_ic95", "passa", "maior_parte", "motivo") if k in d}
                                                                                    | {"mantem": len(d["conferencias_mantem"])} for c, d in l["fontes"].items()}}
                         for l in exp["E1"]["por_lugar"]],
           "n_conferencias": len(exp["E1"]["conferencias"]), "achado_brasil": exp["E1"]["achado_brasil"], "votos": exp["E1"]["votos_brasil"]},
    "E2": {"casas": casas(e2["casas"]), "eleitores": casas(e2["casas"], "eleitores_1t"),
           "fatia": {k: v["n"] for k, v in e2["fatia_lula"].items()},
           "por_uf": {u: [v["casas"].get("Flávio → Lula", {"n": 0})["n"], v["casas"].get("Lula → Flávio", {"n": 0})["n"],
                          sum(x["n"] for x in v["casas"].values())] for u, v in exp["E2"]["por_uf"].items()},
           "vencedor_todos": exp["E2"]["conf_vencedor_entre_todos"],
           "secoes": casas(exp["E2"]["conf_secoes"]["casas"]), "exterior": casas(exp["E2"]["exterior"]["casas"])},
    "E3": exp["E3"], "E4": exp["E4"], "E5": exp["E5"],
}

# --- Escala dos partidos (T05), para a tabela de Método e fontes (T12) ------------
def num(v):
    return float(v) if v != "" else None


partidos = [{"numero": int(r["numero"]), "sigla": r["sigla"], "posicao": num(r["posicao"]), "categoria": r["categoria"],
             "esquerda": r["campo_esquerda"] == "sim", "regra": r["regra"],
             "especialistas": int(r["especialistas"]) if r["especialistas"] else None, "desvio": num(r["desvio_padrao"]),
             "pos_2018": num(r["conf_2018_posicao"]), "esquerda_2018": r["conf_2018_campo_esquerda"] == "sim"}
            for r in csv.DictReader(open(DADOS / "escala_partidos.csv", encoding="utf-8"))]
partidos.sort(key=lambda p: (p["posicao"] is None, p["posicao"] or 0))
confere(len(partidos) == 30 and sum(p["posicao"] is None for p in partidos) == 1
        and all(p["esquerda"] == (p["posicao"] is not None and p["posicao"] <= 4.49) for p in partidos),
        f"{len(partidos)} partidos, um sem posição, campo da esquerda = posição até 4,49")

# --- Saída ------------------------------------------------------------------------
saida = {
    "gerado": datetime.now().strftime("%d/%m/%Y %H:%M"),
    "fontes": "dados/analise_estados.csv e dados/analise_municipios.csv (T03); dados/inferencia.json (T06); "
              "dados/historico_2t.json; dados/escala_partidos.csv (T05); dados/dados_sociais_municipios.json (T26); dados/secoes_inferencia.json (T35); dados/exploracao.json (T33); docs/analise/NOTAS.md",
    "brasil": brasil,
    "regioes": regioes,
    "ufs": ufs,
    "municipios": {"campos": CAMPOS_MUN, "linhas": "\n".join(linhas)},
    "retas": retas,
    "hipoteses": hip_pag,
    "complementos": compl_pag,
    "h5": h5_pag,
    "h1_referencia": {k: (ic_da_pagina(v) if isinstance(v, dict) else v) for k, v in inf["h1_referencia"].items()},
    "poucos_grupos": {"peso_uf": inf["poucos_grupos"]["peso_uf"],
                      "g_efetivo": {h: [x["g_efetivo"] for x in g] for h, g in inf["poucos_grupos"]["g_efetivo"].items()},
                      "sem_um_estado": {h: {k: x[k] for k in ("coef_min", "coef_max", "mudam_classificacao")}
                                        | {"estados": {e["uf"]: [e["coef"], e["p_selvagem"]] for e in x["estados"]}}
                                        for h, x in inf["poucos_grupos"]["sem_um_estado"].items()}},
    "ecologica": inf["ecologica"] | {"fontes_sem_exterior": fontes_sem_exterior},
    "transicao": {k: inf["transicao"][k] for k in ("origens", "destinos", "brasil")}
                 | {"regioes": {r: {k: x[k] for k in ("outros_lula_entre_os_dois", "outros_lula_entre_os_dois_ic95")}
                                for r, x in inf["transicao"]["regioes"].items()}},
    "especificacoes_outros": inf["especificacoes_outros"],
    "limites_duncan_davis": inf["limites_duncan_davis"],
    "por_lugar": inf["por_lugar"],
    # T35 (P28): a conta por município, como conferência, ao lado da por seção na tabela do capítulo 4
    "por_lugar_municipios": [{"lugar": l["lugar"], "fontes": {c: {k: d[k] for k in ("passa", "lula", "lula_ic95", "maior_parte", "motivo") if k in d}
                                                         for c, d in l["fontes"].items()}} for l in inf["por_lugar_municipios"]],
    "nao_deu": inf["nao_deu"],
    "secoes": {"secoes": sec["meta"]["secoes"], "secoes_total": sec["meta"]["secoes_com_exterior"],
               "aptos_mudam": sec["meta"]["secoes_aptos_mudam_com_exterior"], "votos_28": sec["meta"]["votos_28"],
               "comparecimento_1t": sec["meta"]["comparecimento_1t_com_exterior"],
               "parte_comum": inf["por_lugar"][0]["parte_comum_municipio"],
               "c_mantem": sum(len(x["conferencias_mantem"]) == len(sec["conferencias"]) for x in sec["comparacao"] if x["fonte"] == "C"),
               "c_lugares": sum(x["fonte"] == "C" for x in sec["comparacao"]),
               "c_muda_de_lado": [x["lugar"] for x in sec["comparacao"] if x["fonte"] == "C" and x["classe"] == "muda de lado"]},
    "funil": {"var_fatia": funil(inf["funil"]["var_fatia"]), "var_abstencao": funil(inf["funil"]["var_abstencao"])},
    "projecao": {k: inf["projecao"][k] for k in ("resultado_final_pct", "leituras", "faixas", "geral", "pontos")},
    "notas": [{"id": n["id"]} for n in notas],
    "partidos": partidos,
    "sociais": sociais_pag,
    "exploracao": exploracao_pag,
}
SAIDA.write_text("// Gerado por scripts/pagina_dados.py. Não editar à mão.\n"
                 "window.ESTUDO = " + json.dumps(saida, ensure_ascii=False, separators=(",", ":")) + ";\n",
                 encoding="utf-8")
print(f"\n{SAIDA.relative_to(RAIZ)}: {SAIDA.stat().st_size / 1024:.0f} KB")

# --- Títulos das notas no catálogo de textos (T30): troca só o bloco entre os marcadores -------
cat = CATALOGO.read_text(encoding="utf-8")
i, f = cat.find(INICIO_NOTAS), cat.find(FIM_NOTAS)
if i < 0 or f < 0:
    problemas.append(f"marcadores do bloco das notas não encontrados em {CATALOGO.relative_to(RAIZ)}")
else:
    bloco = (INICIO_NOTAS + " gravado por scripts/pagina_dados.py a partir de docs/analise/NOTAS.md; mudar lá>\n" +
             "".join(f'"nota.{n["id"]}": {json.dumps(n["titulo"], ensure_ascii=False)},\n' for n in notas))
    novo = cat[:i] + bloco + cat[f:]
    if novo != cat:
        CATALOGO.write_text(novo, encoding="utf-8", newline="\n")
    print(f"{CATALOGO.relative_to(RAIZ)}: {len(notas)} títulos de notas")
if problemas:
    sys.exit("\nFALHOU:\n- " + "\n- ".join(problemas[:20]))
print("Resultado: tudo confere.")
