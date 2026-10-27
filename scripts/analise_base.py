# T03: base unificada dos dois turnos e indicadores da seção 4 da especificação, por município, UF, região e Brasil.
# Lê as bases do 1º e do 2º turno e a lista de municípios do TSE, confere tudo e grava em ../dados:
#   analise_municipios.csv, analise_estados.csv (Brasil, regiões e UFs) e analise_compacta.json (para a página).
# Uso: python -I scripts/analise_base.py  (imprime o relatório de conferência em Markdown; sai com 1 se algo não fechar)
import json, sys, os, csv, datetime, unicodedata
sys.stdout.reconfigure(encoding="utf-8")  # o relatório tem acentos e "−", que o terminal do Windows não codifica (diário, D03)
AQUI = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(AQUI, "..", "dados")
B1, B2 = (os.path.join(DADOS, f"base_{t}_municipios.json") for t in ("1t", "2t"))
MUN = os.path.join(DADOS, "tse_config", "mun-e006258-cm.json")
SAI_MU, SAI_UF, SAI_JS = (os.path.join(DADOS, n) for n in ("analise_municipios.csv", "analise_estados.csv", "analise_compacta.json"))

# seção 2 da especificação (Brasil, resultado totalizado)
ESPEC = {"L1": 53879538, "F1": 56104503, "L2": 64256232, "F2": 59826041, "dL": 10376694, "dF": 3721538,
         "M1": -2224965, "M2": 4430191, "dM": 6655156}
ESPEC_PCT = {"s1": ("48,989", 3), "s2": ("51,785", 3), "ds": ("2,80", 2), "cap": ("73,6", 1)}
REGIOES = [("N", "Norte", "ac am ap pa ro rr to"), ("NE", "Nordeste", "al ba ce ma pb pe pi rn se"),
           ("CO", "Centro-Oeste", "df go ms mt"), ("SE", "Sudeste", "es mg rj sp"), ("S", "Sul", "pr rs sc"),
           ("EX", "Exterior", "zz")]
REG = {u: r for r, _, us in REGIOES for u in us.split()}
# código IBGE de cada UF (2 primeiros dígitos do cdi) e da região (1º dígito), para conferir a região tirada da UF
UF_IBGE = {"ro": "11", "ac": "12", "am": "13", "rr": "14", "pa": "15", "ap": "16", "to": "17", "ma": "21", "pi": "22",
           "ce": "23", "rn": "24", "pb": "25", "pe": "26", "al": "27", "se": "28", "ba": "29", "mg": "31", "es": "32",
           "rj": "33", "sp": "35", "pr": "41", "sc": "42", "rs": "43", "ms": "50", "mt": "51", "go": "52", "df": "53"}
REG_IBGE = {"1": "N", "2": "NE", "3": "SE", "4": "S", "5": "CO"}
# faixas de porte pelo eleitorado do 1º turno, fixadas no T03 (26/10/2026, 11:47) antes de ver os números por município
PORTES = [("1", "Até 5 mil", 5000), ("2", "De 5 mil a 10 mil", 10000), ("3", "De 10 mil a 50 mil", 50000),
          ("4", "De 50 mil a 200 mil", 200000), ("5", "Mais de 200 mil", None)]
def porte(uf, te1):
    if uf == "zz": return "X"
    return next(c for c, _, teto in PORTES if teto is None or te1 <= teto)

CONTAGENS = ["te1", "c1", "vv1", "L1", "F1", "te2", "c2", "vv2", "L2", "F2", "vb2", "tvn2"]
def contagens(r1, r2):
    x = {k + "1": r1[k] for k in ("te", "c", "vv", "L", "F")}
    x.update({k + "2": r2[k] for k in ("te", "c", "vv", "L", "F", "vb", "tvn")})
    for k, v in x.items():
        if v != int(v): raise ValueError(f"contagem não inteira: {k} = {v}")
        x[k] = int(v)
    return x
def soma(rs): return {k: sum(r[k] for r in rs) for k in CONTAGENS}
def razao(a, b): return a / b if b else None
def menos(a, b): return None if a is None or b is None else a - b
def indicadores(x, dM_br):  # seção 4 da especificação
    y = dict(x)
    y["O1"] = x["vv1"] - x["L1"] - x["F1"]
    y["BN1"], y["BN2"] = x["c1"] - x["vv1"], x["c2"] - x["vv2"]
    y["A1"], y["A2"] = x["te1"] - x["c1"], x["te2"] - x["c2"]
    y["dL"], y["dF"] = x["L2"] - x["L1"], x["F2"] - x["F1"]
    y["M1"], y["M2"] = x["L1"] - x["F1"], x["L2"] - x["F2"]
    y["dM"], y["dC"], y["dBN"], y["dte"] = y["M2"] - y["M1"], x["c2"] - x["c1"], y["BN2"] - y["BN1"], x["te2"] - x["te1"]
    y["res"] = (y["dL"] + y["dF"]) - (y["O1"] + y["dC"] - y["dBN"])  # identidade do saldo: tem que dar 0
    y["s1"], y["s2"] = razao(x["L1"], x["L1"] + x["F1"]), razao(x["L2"], x["L2"] + x["F2"])
    y["ds"] = menos(y["s2"], y["s1"])
    y["a1"], y["a2"] = razao(y["A1"], x["te1"]), razao(y["A2"], x["te2"])  # cada turno com o próprio eleitorado (N05)
    y["da"] = menos(y["a2"], y["a1"])
    y["peso"] = y["dM"] / dM_br
    y["cap"] = y["dL"] / (y["dL"] + y["dF"]) if y["dL"] + y["dF"] > 0 else None  # sem valor quando os dois juntos não ganharam votos
    return y

# colunas dos CSV: nome, chave, tipo (i = inteiro, p = % ou p.p. com 4 casas, w = % com 6 casas)
COLS = [("eleitorado_1t", "te1", "i"), ("comparecimento_1t", "c1", "i"), ("abstencao_1t", "A1", "i"),
        ("validos_1t", "vv1", "i"), ("brancos_nulos_1t", "BN1", "i"), ("lula_1t", "L1", "i"), ("flavio_1t", "F1", "i"),
        ("outros_1t", "O1", "i"), ("eleitorado_2t", "te2", "i"), ("comparecimento_2t", "c2", "i"), ("abstencao_2t", "A2", "i"),
        ("validos_2t", "vv2", "i"), ("brancos_2t", "vb2", "i"), ("nulos_2t", "tvn2", "i"), ("brancos_nulos_2t", "BN2", "i"),
        ("lula_2t", "L2", "i"), ("flavio_2t", "F2", "i"),
        ("fatia_lula_1t_pct", "s1", "p"), ("fatia_lula_2t_pct", "s2", "p"), ("var_fatia_pp", "ds", "p"),
        ("var_lula", "dL", "i"), ("var_flavio", "dF", "i"), ("dif_1t", "M1", "i"), ("dif_2t", "M2", "i"), ("var_dif", "dM", "i"),
        ("peso_virada_pct", "peso", "w"), ("captura_lula_pct", "cap", "p"),
        ("var_comparecimento", "dC", "i"), ("var_brancos_nulos", "dBN", "i"), ("var_eleitorado", "dte", "i"),
        ("taxa_abst_1t_pct", "a1", "p"), ("taxa_abst_2t_pct", "a2", "p"), ("var_taxa_abst_pp", "da", "p"),
        ("residuo_identidade", "res", "i")]
def fmt(v, tipo):
    if v is None: return ""
    if tipo == "i": return str(v)
    s = f"{v * 100:.{6 if tipo == 'w' else 4}f}"
    return s.lstrip("-") if float(s) == 0 else s

def f(x): return f"{int(x):,}".replace(",", ".")
def fs(x): return ("+" if x > 0 else "−" if x < 0 else "") + f(abs(x))
def pc(v, casas=3, sinal=False):
    if v is None: return "—"
    s = f"{abs(v) * 100:.{casas}f}".replace(".", ",")
    return (("+" if v > 0 else "−" if v < 0 else "") if sinal else ("−" if v < 0 else "")) + s
def pp(v, casas=3): return "—" if v is None else pc(v, casas) + "%"
def sem_acento(s): return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
ok = True
def linha(texto, certo):
    global ok
    ok &= bool(certo); print(f"- {'OK' if certo else 'ERRO'}: {texto}")

d1, d2 = (json.load(open(b, encoding="utf-8")) for b in (B1, B2))
cfg = json.load(open(MUN, encoding="utf-8"))
lista = {m["cd"]: dict(m, uf=a["cd"]) for a in cfg["abr"] for m in a["mu"]}
nome_uf = {a["cd"]: a["ds"].title().replace(" Do ", " do ").replace(" De ", " de ") for a in cfg["abr"]}
nome_uf["zz"] = "Exterior"
mu1, mu2 = d1["mu"], d2["mu"]

print("### Conferência da junção\n")
linha(f"mesmos códigos no 1º turno, no 2º turno e na lista do TSE: {f(len(lista))} na lista, {f(len(mu1))} no 1º, {f(len(mu2))} no 2º",
      set(mu1) == set(mu2) == set(lista))
dif_nome = [k for k in lista if not (mu1[k]["uf"] == mu2[k]["uf"] == lista[k]["uf"] and mu1[k]["nm"] == mu2[k]["nm"] == lista[k]["nm"])]
linha(f"mesma UF e mesmo nome nas três fontes: {len(dif_nome)} diferenças", not dif_nome)
dif_cap = [k for k in lista if not (mu1[k]["cap"] == mu2[k]["cap"] == (lista[k]["c"] == "s"))]
linha(f"capital igual nas duas bases e na lista do TSE (campo `c`): {len(dif_cap)} diferenças; "
      f"{sum(m['c'] == 's' for m in lista.values())} capitais, uma por UF do Brasil",
      not dif_cap and sorted(m["uf"] for m in lista.values() if m["c"] == "s") == sorted(UF_IBGE))
linha(f"todas as UFs com região: {len(set(m['uf'] for m in lista.values()) - set(REG))} sem região", set(m["uf"] for m in lista.values()) <= set(REG))
br_cdi = [m for m in lista.values() if m["uf"] != "zz"]
ex_cdi = [m for m in lista.values() if m["uf"] == "zz"]
cdi_ruim = [m["cd"] for m in br_cdi if not (len(m["cdi"]) == 7 and m["cdi"].isdigit() and m["cdi"][:2] == UF_IBGE[m["uf"]]
                                             and REG_IBGE[m["cdi"][0]] == REG[m["uf"]])]
linha(f"código IBGE (`cdi`) com 7 dígitos em todos os {f(len(br_cdi))} municípios do Brasil, sem repetição, começando pelo código "
      f"da UF; o 1º dígito confirma a região tirada da UF: {len(cdi_ruim)} exceções, {len(br_cdi) - len({m['cdi'] for m in br_cdi})} repetidos",
      not cdi_ruim and len({m["cdi"] for m in br_cdi}) == len(br_cdi))
linha(f"exterior sem código IBGE: {sum(not m['cdi'] for m in ex_cdi)} de {len(ex_cdi)}", all(not m["cdi"] for m in ex_cdi))

# contagens por município e somas por UF, região e Brasil
X = {k: contagens(mu1[k], mu2[k]) for k in lista}
ufs = sorted({m["uf"] for m in lista.values()})
XU = {u: soma([X[k] for k in lista if lista[k]["uf"] == u]) for u in ufs}
XR = {r: soma([XU[u] for u in ufs if REG[u] == r]) for r, _, _ in REGIOES}
XB = soma(X.values())

print("\n### Conferência das somas\n")
div_uf = [u for u in ufs if XU[u] != contagens(d1["uf"][u], d2["uf"][u])]
linha(f"soma dos municípios = arquivo de cada UF nos dois turnos ({len(ufs)} UFs, com o exterior; campos {', '.join(CONTAGENS)}): "
      f"{len(div_uf)} divergem" + (f" {div_uf}" if div_uf else ""), not div_uf and set(ufs) == set(d1["uf"]) == set(d2["uf"]))
linha("soma dos municípios = soma das UFs = soma das regiões = arquivo Brasil, nos dois turnos",
      XB == soma(XU.values()) == soma(XR.values()) == contagens(d1["br"], d2["br"]))
linha(f"cada região = soma das suas UFs = soma dos seus municípios ({len(XR)} regiões, com o exterior)",
      all(XR[r] == soma([X[k] for k in lista if REG[lista[k]["uf"]] == r]) for r in XR))

dM_br = indicadores(XB, 1)["dM"]
IB = indicadores(XB, dM_br)
IU = {u: indicadores(XU[u], dM_br) for u in ufs}
IR = {r: indicadores(XR[r], dM_br) for r in XR}
IM = {k: indicadores(X[k], dM_br) for k in lista}
todas = list(IM.values()) + list(IU.values()) + list(IR.values()) + [IB]

print("\n### Identidade do saldo: ΔL + ΔF = O1 + ΔC − ΔBN\n")
for nome, grupo in (("municípios", IM.values()), ("UFs, com o exterior", IU.values()), ("regiões, com o exterior", IR.values()), ("Brasil", [IB])):
    g = list(grupo)
    linha(f"{nome}: {f(len(g))} {'unidade' if len(g) == 1 else 'unidades'}, {sum(y['res'] != 0 for y in g)} com diferença; maior diferença em módulo {max(abs(y['res']) for y in g)}",
          all(y["res"] == 0 for y in g))
linha(f"total: diferença zero nas {f(len(todas))} unidades", all(y["res"] == 0 for y in todas))

print("\n### Coerência das contagens\n")
regras = [("comparecimento ≤ eleitorado, nos dois turnos", lambda y: y["c1"] <= y["te1"] and y["c2"] <= y["te2"]),
          ("válidos ≤ comparecimento, nos dois turnos", lambda y: y["vv1"] <= y["c1"] and y["vv2"] <= y["c2"]),
          ("Lula + Flávio ≤ válidos no 1º turno (O1 ≥ 0)", lambda y: y["O1"] >= 0),
          ("válidos = Lula + Flávio no 2º turno (sem outros)", lambda y: y["vv2"] == y["L2"] + y["F2"]),
          ("brancos + nulos do 2º turno = comparecimento − válidos", lambda y: y["vb2"] + y["tvn2"] == y["BN2"]),
          ("nenhuma contagem negativa", lambda y: min(y[k] for k in CONTAGENS) >= 0)]
for texto, regra in regras:
    linha(f"{texto}: {sum(not regra(y) for y in todas)} exceções em {f(len(todas))} unidades", all(regra(y) for y in todas))
linha(f"soma do peso na virada das UFs = 100% (soma de ΔM das UFs = ΔM do Brasil = {fs(sum(IU[u]['dM'] for u in ufs))})",
      sum(IU[u]["dM"] for u in ufs) == dM_br == sum(IR[r]["dM"] for r in IR))

print("\n### Brasil × seção 2 da especificação\n")
for k, v in ESPEC.items():
    linha(f"{k}: {fs(IB[k]) if k[0] in 'dM' else f(IB[k])} (especificação {fs(v) if k[0] in 'dM' else f(v)})", IB[k] == v)
for k, (v, casas) in ESPEC_PCT.items():
    calc = pc(IB[k], casas)
    linha(f"{k}: {calc}{' p.p.' if k == 'ds' else '%'} (especificação {v})", calc == v)

print("\n### Valores sem conta possível (tratamento, sem leitura de resultado)\n")
mus = list(IM.values())
print(f"- fatia sem valor (Lula + Flávio = 0): {sum(y['s1'] is None for y in mus)} no 1º turno, {sum(y['s2'] is None for y in mus)} no 2º")
print(f"- taxa de abstenção sem valor (eleitorado 0): {sum(y['a1'] is None or y['a2'] is None for y in mus)}")
print(f"- captura sem valor (ΔL + ΔF ≤ 0, os dois juntos não ganharam votos): {f(sum(y['cap'] is None for y in mus))} municípios "
      f"({sum(y['cap'] is None and REG[lista[k]['uf']] == 'EX' for k, y in IM.items())} no exterior); UFs: {sum(y['cap'] is None for y in IU.values())}")
print(f"- captura fora de 0% a 100% (um dos dois perdeu votos e o outro ganhou mais do que isso): {f(sum(y['cap'] is not None and not 0 <= y['cap'] <= 1 for y in mus))} municípios; "
      f"UFs: {sum(y['cap'] is not None and not 0 <= y['cap'] <= 1 for y in IU.values())}")

print("\n### Porte (eleitorado do 1º turno, faixas fixadas antes)\n")
cont_porte = {}
for k, y in IM.items(): cont_porte.setdefault(porte(lista[k]["uf"], y["te1"]), []).append(y["te1"])
print("| Faixa | Municípios | Eleitorado do 1º turno |\n|---|---|---|")
for c, nome, _ in PORTES + [("X", "Exterior", None)]:
    print(f"| {c}. {nome} | {f(len(cont_porte.get(c, [])))} | {f(sum(cont_porte.get(c, [])))} |")
linha(f"cada município em uma faixa só: {f(sum(len(v) for v in cont_porte.values()))} de {f(len(IM))}", sum(len(v) for v in cont_porte.values()) == len(IM))

# saídas
cap_txt = lambda k: "exterior" if lista[k]["uf"] == "zz" else "capital" if lista[k]["c"] == "s" else "interior"
nome_porte = {c: n for c, n, _ in PORTES} | {"X": "Exterior"}
nome_reg = {r: n for r, n, _ in REGIOES}
ordem = sorted(lista, key=lambda k: (lista[k]["uf"] == "zz", lista[k]["uf"], sem_acento(lista[k]["nm"]), k))
cab_mu = ["cd_tse", "cd_ibge", "uf", "municipio", "regiao", "capital_interior", "porte", "porte_faixa"] + [c for c, _, _ in COLS]
linhas_mu = []
for k in ordem:
    m, y = lista[k], IM[k]
    pt = porte(m["uf"], y["te1"])
    linhas_mu.append([k, m["cdi"], m["uf"].upper(), m["nm"], nome_reg[REG[m["uf"]]], cap_txt(k), pt, nome_porte[pt]]
                     + [fmt(y[ch], t) for _, ch, t in COLS])
cab_uf = ["nivel", "codigo", "nome", "regiao", "municipios"] + [c for c, _, _ in COLS]
n_mu_uf = {u: sum(lista[k]["uf"] == u for k in lista) for u in ufs}
linhas_uf = [["brasil", "BR", "Brasil", "", len(lista)] + [fmt(IB[ch], t) for _, ch, t in COLS]]
linhas_uf += [["regiao", r, n, n, sum(n_mu_uf[u] for u in ufs if REG[u] == r)] + [fmt(IR[r][ch], t) for _, ch, t in COLS] for r, n, _ in REGIOES]
linhas_uf += [["uf", u.upper(), nome_uf[u], nome_reg[REG[u]], n_mu_uf[u]] + [fmt(IU[u][ch], t) for _, ch, t in COLS]
              for u in sorted(ufs, key=lambda u: (u == "zz", u))]
for caminho, cab, lin in ((SAI_MU, cab_mu, linhas_mu), (SAI_UF, cab_uf, linhas_uf)):
    with open(caminho, "w", encoding="utf-8", newline="") as arq:
        w = csv.writer(arq); w.writerow(cab); w.writerows(lin)

agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
compacta = {
    "meta": {
        "o_que": "Análise da virada (T03): os dois turnos de presidente lado a lado, por município, UF, região e Brasil. Só contagens; os indicadores saem das fórmulas abaixo.",
        "gerado": agora + " (horário de Brasília), por scripts/analise_base.py",
        "fontes": ["TSE, eleição 6257 (1º turno), dados/base_1t_municipios.json",
                   "TSE, eleição 6258 (2º turno), dados/base_2t_municipios.json",
                   "TSE, lista de municípios dados/tse_config/mun-e006258-cm.json (capital e código IBGE)"],
        "contagens": dict(zip(CONTAGENS, ["eleitorado apto, 1º turno", "comparecimento, 1º turno", "votos válidos, 1º turno",
                                          "Lula (13), 1º turno", "Flávio (22), 1º turno", "eleitorado apto, 2º turno",
                                          "comparecimento, 2º turno", "votos válidos, 2º turno", "Lula (13), 2º turno",
                                          "Flávio (22), 2º turno", "brancos, 2º turno", "nulos, 2º turno"])),
        "mu_colunas": ["cd", "cdi", "uf", "nm", "cap", "porte"] + CONTAGENS,
        "mu_codigos": {"cd": "código TSE de 5 dígitos", "cdi": "código IBGE (vazio no exterior)",
                       "cap": "1 capital, 0 interior ou exterior (o exterior é uf 'zz')",
                       "porte": "faixa de porte pelo eleitorado do 1º turno: 1 a 5 (ver 'portes'), 0 no exterior"},
        "portes": [{"cod": int(c), "nome": n, "ate": t} for c, n, t in PORTES],
        "regioes": {r: {"nome": n, "ufs": us.split()} for r, n, us in REGIOES},
        "uf_nome": nome_uf,
        "formulas": {"O1": "vv1 − L1 − F1", "BN1": "c1 − vv1 (brancos e nulos juntos, nota N07)", "BN2": "vb2 + tvn2 = c2 − vv2",
                     "s": "L ÷ (L + F); sem valor se L + F = 0", "ds": "s2 − s1", "dL": "L2 − L1", "dF": "F2 − F1",
                     "M": "L − F", "dM": "M2 − M1", "peso": "dM da unidade ÷ dM do Brasil",
                     "captura": "dL ÷ (dL + dF); sem valor se dL + dF ≤ 0; pode passar de 100% ou ficar abaixo de 0",
                     "a": "(te − c) ÷ te, cada turno com o próprio eleitorado (nota N05)", "da": "a2 − a1",
                     "dC": "c2 − c1", "dBN": "BN2 − BN1", "identidade": "dL + dF = O1 + dC − dBN"},
        "notas": "Ver docs/analise/NOTAS.md: N05 (eleitorado muda entre os turnos), N06 (exterior), N07 (brancos e nulos no 1º turno) e as notas do T03.",
    },
    "br": [XB[c] for c in CONTAGENS],
    "rg": {r: [XR[r][c] for c in CONTAGENS] for r in XR},
    "uf": {u: [XU[u][c] for c in CONTAGENS] for u in ufs},
    "mu": [[k, lista[k]["cdi"], lista[k]["uf"], lista[k]["nm"], int(lista[k]["c"] == "s"),
            0 if lista[k]["uf"] == "zz" else int(porte(lista[k]["uf"], X[k]["te1"]))] + [X[k][c] for c in CONTAGENS] for k in ordem],
}
with open(SAI_JS, "w", encoding="utf-8") as arq: json.dump(compacta, arq, ensure_ascii=False, separators=(",", ":"))

print("\n### Conferência das saídas\n")
lidos_mu = list(csv.reader(open(SAI_MU, encoding="utf-8", newline="")))
lidos_uf = list(csv.reader(open(SAI_UF, encoding="utf-8", newline="")))
js = json.load(open(SAI_JS, encoding="utf-8"))
dM_js = indicadores(dict(zip(CONTAGENS, js["br"])), 1)["dM"]
refeito = [[fmt(indicadores(dict(zip(CONTAGENS, r[6:])), dM_js)[ch], t) for _, ch, t in COLS] for r in js["mu"]]
linha(f"`analise_municipios.csv`: {f(len(lidos_mu) - 1)} linhas e {len(cab_mu)} colunas", lidos_mu[1:] == linhas_mu and len(lidos_mu) - 1 == len(lista))
linha(f"`analise_estados.csv`: {len(lidos_uf) - 1} linhas (Brasil, {len(REGIOES)} regiões e {len(ufs)} UFs)",
      lidos_uf[1:] == [[str(c) for c in l] for l in linhas_uf] and len(lidos_uf) - 1 == 1 + len(REGIOES) + len(ufs))
linha("`analise_compacta.json`: os indicadores refeitos a partir das contagens do JSON são iguais aos do CSV, município por município",
      refeito == [l[8:] for l in linhas_mu] and [r[0] for r in js["mu"]] == [l[0] for l in linhas_mu])
for caminho in (SAI_MU, SAI_UF, SAI_JS):
    print(f"- {os.path.basename(caminho)}: {os.path.getsize(caminho) / 1024:,.0f} KB".replace(",", "."))

print("\n### Totais do Brasil\n")
print("| | 1º turno | 2º turno | Variação |\n|---|---|---|---|")
print(f"| Eleitorado | {f(IB['te1'])} | {f(IB['te2'])} | {fs(IB['dte']) or '0'} |")
print(f"| Comparecimento | {f(IB['c1'])} | {f(IB['c2'])} | {fs(IB['dC'])} |")
print(f"| Taxa de abstenção | {pc(IB['a1'])}% | {pc(IB['a2'])}% | {pc(IB['da'], sinal=True)} p.p. |")
print(f"| Válidos | {f(IB['vv1'])} | {f(IB['vv2'])} | {fs(IB['vv2'] - IB['vv1'])} |")
print(f"| Brancos e nulos | {f(IB['BN1'])} | {f(IB['BN2'])} | {fs(IB['dBN'])} |")
print(f"| Lula (13) | {f(IB['L1'])} | {f(IB['L2'])} | {fs(IB['dL'])} |")
print(f"| Flávio (22) | {f(IB['F1'])} | {f(IB['F2'])} | {fs(IB['dF'])} |")
print(f"| Outros candidatos | {f(IB['O1'])} | 0 | {fs(-IB['O1'])} |")
print(f"| Lula entre os dois | {pc(IB['s1'])}% | {pc(IB['s2'])}% | {pc(IB['ds'], 2, True)} p.p. |")
print(f"| Diferença Lula − Flávio | {fs(IB['M1'])} | {fs(IB['M2'])} | {fs(IB['dM'])} |")
print(f"\nCaptura: {pc(IB['cap'], 1)}%. Saldo: ΔL + ΔF = {fs(IB['dL'] + IB['dF'])} = O1 {f(IB['O1'])} + ΔC {fs(IB['dC'])} − ΔBN {fs(IB['dBN'])}.")

print("\n### Totais das UFs (ordem alfabética, sem comentário)\n")
print("| UF | Lula 1º | Flávio 1º | Lula 2º | Flávio 2º | s1 | s2 | Δs (p.p.) | ΔM | Peso | Captura | a1 | a2 | Δa (p.p.) | Identidade |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for u in sorted(ufs, key=lambda u: (u == "zz", u)):
    y = IU[u]
    print(f"| {u.upper() if u != 'zz' else 'Exterior'} | {f(y['L1'])} | {f(y['F1'])} | {f(y['L2'])} | {f(y['F2'])} | {pp(y['s1'], 2)} | {pp(y['s2'], 2)} "
          f"| {pc(y['ds'], 2, True)} | {fs(y['dM'])} | {pp(y['peso'], 2)} | {pp(y['cap'], 1)} | {pp(y['a1'], 2)} | {pp(y['a2'], 2)} "
          f"| {pc(y['da'], 2, True)} | {y['res']} |")

print(f"\n**Resultado: {'tudo confere' if ok else 'há divergências'}.** Gerado em {agora}.")
sys.exit(0 if ok else 1)
