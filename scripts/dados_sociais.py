# Monta dados/dados_sociais_municipios.json (T26): as 7 variáveis da lista curta do HIPOTESES.md (seção 6; a 3 trocada em 26/10/2026, 23:41, P26)
# para os 5.571 municípios do Brasil da lista do TSE, pelo código do TSE, com o código IBGE, o ano e a fonte.
# Lê só o que sociais_baixar.py gravou em dados/sociais_fontes/ e confere: cobertura, códigos sem par
# e a soma (ou a média ponderada) dos municípios contra o valor do Brasil publicado pela própria fonte.
# Não lê nenhum resultado de eleição: os cruzamentos são do T34.
# Uso: python -I scripts/dados_sociais.py dados/sociais_fontes dados/dados_sociais_municipios.json
import sys, os, json, math, zipfile, re, time
FON, OUT = sys.argv[1], sys.argv[2]
MUN = os.path.join(os.path.dirname(__file__), "..", "dados", "tse_config", "mun-e006258-cm.json")
REG = json.load(open(os.path.join(FON, "baixados.json"), encoding="utf-8"))
erros = []
def confere(cond, msg):
    print(("ok   " if cond else "ERRO ") + msg)
    if not cond: erros.append(msg)

def sidra(nome):
    # devolve {código do lugar: {(códigos das classificações): valor}}; o Brasil fica no código "1"
    linhas = json.load(open(os.path.join(FON, nome), encoding="utf-8"))
    cab, out = linhas[0], {}
    cls = sorted(k for k in cab if k.startswith("D") and k.endswith("C") and k not in ("D1C", "D3C"))
    for l in linhas[1:]:
        v = l["V"]
        if v == "-": v = 0.0  # no SIDRA, "-" é zero absoluto
        else:
            try: v = float(v)
            except ValueError: v = None  # "..", "...", "X": não se aplica, não disponível ou sigilo
        out.setdefault(l["D1C"], {})[tuple(l[k] for k in cls)] = v
    return out

# lista do TSE: 5.571 municípios do Brasil (o exterior, "zz", fica fora; nota N06)
tse = {}
for a in json.load(open(MUN, encoding="utf-8"))["abr"]:
    if a["cd"] == "zz": continue
    for m in a["mu"]: tse[m["cd"]] = {"cdi": m["cdi"], "uf": a["cd"].upper()}
cdi2tse = {v["cdi"]: k for k, v in tse.items()}
confere(len(tse) == 5571 and len(cdi2tse) == 5571, f"lista do TSE: {len(tse)} municípios do Brasil, {len(cdi2tse)} códigos IBGE distintos")

# --- Censo 2022 ---
idade = sidra("sidra_9514_idade.json")          # chaves: (variável, sexo, idade, forma)
for c, d in sidra("sidra_9514_idade_b.json").items(): idade.setdefault(c, {}).update(d)
m15 = sidra("sidra_9514_15mais.json")
alf = sidra("sidra_9543_alfabetizacao.json")
dens = sidra("sidra_4714_densidade.json")
rel = sidra("sidra_9537_religiao.json")
cor = sidra("sidra_9605_cor_raca.json")
renda = sidra("sidra_10296_renda.json")
G60 = ["93095", "93096", "93097", "93098", "49108", "49109", "60040", "60041", "6653"]
def soma(d, f):
    vs = [v for k, v in d.items() if f(k)]
    return None if not vs or any(v is None for v in vs) else sum(vs)
def var_censo(c):
    r = {}
    i = idade.get(c, {})
    pop = soma(i, lambda k: k[2] == "100362")
    p60 = soma(i, lambda k: k[2] in G60)
    r["pop"] = pop; r["pop60"] = p60
    r["pct_60mais"] = 100 * p60 / pop if pop and p60 is not None else None
    a = alf.get(c, {})
    r["alfab_15mais"] = next(iter(a.values())) if a else None
    m = m15.get(c, {})
    menos15 = soma(m, lambda k: True)
    r["pop15"] = pop - menos15 if pop is not None and menos15 is not None else None
    d = dens.get(c, {})
    r["area_km2"] = d.get(("6318",)); r["densidade"] = d.get(("614",)); r["pop_4714"] = d.get(("93",))
    r["ln_densidade"] = math.log(r["densidade"]) if r["densidade"] else None
    g = rel.get(c, {})
    tot10 = soma(g, lambda k: k[1] == "95278"); ev = soma(g, lambda k: k[1] == "95277")
    r["pop10"] = tot10; r["evangelicos10"] = ev
    r["pct_evangelicos"] = 100 * ev / tot10 if tot10 and ev is not None else None
    k = cor.get(c, {})
    tot = soma(k, lambda x: x[1] == "95251")
    pp = soma(k, lambda x: x[1] in ("2777", "2779"))
    r["pop_cor"] = tot; r["pretos_pardos"] = pp
    r["pct_pretos_pardos"] = 100 * pp / tot if tot and pp is not None else None
    n = renda.get(c, {})
    tr = soma(n, lambda x: x[-1] == "9680")
    ate = soma(n, lambda x: x[-1] in ("9681", "9682", "9692"))
    r["pop_renda"] = tr; r["ate_meio_sm"] = ate
    r["pct_ate_meio_sm"] = 100 * ate / tr if tr and ate is not None else None
    return r

# --- PIB dos Municípios 2023 (o PIB per capita é o publicado pelo IBGE) ---
# O txt é de largura fixa e sem cabeçalho (layout no PDF do mesmo zip). Os números de cada linha são, em mil reais,
# o valor adicionado por atividade e total, os impostos e o PIB, e por fim o PIB per capita em reais. Em 2023 só vêm
# preenchidos o PIB e o PIB per capita: são os dois últimos números da linha.
z = zipfile.ZipFile(os.path.join(FON, "pib_municipios_2010_2023_txt.zip"))
texto = z.read([n for n in z.namelist() if n.lower().endswith(".txt")][0]).decode("latin-1")
pib, fora = {}, 0
for l in texto.splitlines():
    if not l.startswith("2023 "): continue
    cod = re.search(r"\s(\d{7})\s", l).group(1)
    n = [float(x) for x in re.findall(r"(?<![\w.])-?\d+\.\d+(?![\w.])", l)]
    fora += len(n) not in (2, 8)
    pib[cod] = {"pib_mil": n[-2], "pib_pc": n[-1]}
confere(fora == 0 and len(pib) == len({k for k in pib}), f"PIB 2023: {len(pib)} municípios lidos; linhas fora do padrão: {fora}")

# --- junta pelo código IBGE ---
mun = {}
for cd in sorted(tse):
    cdi = tse[cd]["cdi"]
    c = var_censo(cdi)
    p = pib.get(cdi, {})
    pc = p.get("pib_pc")
    mun[cd] = {
        "cdi": cdi, "uf": tse[cd]["uf"],
        "pct_60mais": c["pct_60mais"], "alfab_15mais": c["alfab_15mais"], "pct_renda_ate_meio_sm": c["pct_ate_meio_sm"],
        "pib_pc": pc, "ln_pib_pc": math.log(pc) if pc else None,
        "densidade": c["densidade"], "ln_densidade": c["ln_densidade"],
        "pct_evangelicos": c["pct_evangelicos"], "pct_pretos_pardos": c["pct_pretos_pardos"],
        "pop": c["pop"], "pop15": c["pop15"], "pop10": c["pop10"], "area_km2": c["area_km2"], "pib_mil": p.get("pib_mil"),
        "_c": c,
    }

# --- conferências ---
VARS = ["pct_60mais", "alfab_15mais", "pct_renda_ate_meio_sm", "pib_pc", "densidade", "pct_evangelicos", "pct_pretos_pardos"]
sem = {v: sorted(cd for cd, m in mun.items() if m[v] is None) for v in VARS}
for v, l in sem.items():
    confere(len(l) <= 1, f"{v}: {5571 - len(l)} de 5.571 com valor; sem valor: {[tse[x]['cdi'] for x in l]}")
# códigos sem par: lugar da fonte que não está na lista do TSE, e o contrário
for nome, d in [("9514", idade), ("9543", alf), ("4714", dens), ("9537", rel), ("9605", cor), ("10296", renda), ("PIB", pib)]:
    fonte = {k for k in d if len(k) == 7}
    sobra = sorted(fonte - set(cdi2tse)); falta = sorted(set(cdi2tse) - fonte)
    confere(not sobra and len(falta) <= 1, f"{nome}: {len(fonte)} municípios na fonte; sem par no TSE: {sobra}; do TSE sem par na fonte: {falta}")
def br(d, f): return soma(d.get("1", {}), f)
def tot(campo): return sum(m["_c"][campo] for m in mun.values() if m["_c"][campo] is not None)
P = br(idade, lambda k: k[2] == "100362")
confere(P == tot("pop") == br(dens, lambda k: k == ("93",)) == 203080756, f"população: soma dos municípios {tot('pop'):,.0f} = Brasil na 9514 {P:,.0f} = 4714 = 203.080.756 (publicado)")
P60 = br(idade, lambda k: k[2] in G60)
confere(P60 == tot("pop60"), f"60 anos ou mais: soma {tot('pop60'):,.0f} = Brasil {P60:,.0f} ({100*P60/P:.2f}%)")
A = br(dens, lambda k: k == ("6318",))
# a área do Brasil inclui as lagoas Mirim (4300001) e dos Patos (4300002), no RS, que não são de nenhum município
# (Áreas Territoriais 2022 do IBGE, ibge_areas_territoriais_2022.ods): 2.884,340 + 10.201,524 km²
LAGOAS = 2884.340 + 10201.524
confere(abs(tot("area_km2") + LAGOAS - A) < 0.01, f"área: soma dos municípios {tot('area_km2'):,.3f} + lagoas {LAGOAS:,.3f} = {tot('area_km2') + LAGOAS:,.3f} km² × Brasil {A:,.3f} km²; densidade do Brasil {br(dens, lambda k: k == ('614',))}")
ab = br(alf, lambda k: True); pond = sum(m["alfab_15mais"] * m["_c"]["pop15"] for m in mun.values() if m["alfab_15mais"] is not None) / tot("pop15")
confere(abs(pond - ab) < 0.05, f"alfabetização: média dos municípios pesada pela população de 15+ {pond:.2f}% × Brasil {ab:.2f}%")
E10, EV = br(rel, lambda k: k[1] == "95278"), br(rel, lambda k: k[1] == "95277")
confere(abs(tot("pop10") - E10) <= 0.001 * E10 and abs(tot("evangelicos10") - EV) <= 0.001 * EV, f"religião: 10+ soma {tot('pop10'):,.0f} × Brasil {E10:,.0f}; evangélicos soma {tot('evangelicos10'):,.0f} × Brasil {EV:,.0f} ({100*EV/E10:.2f}%)")
CT = br(cor, lambda x: x[1] == "95251"); CP = br(cor, lambda x: x[1] in ("2777", "2779"))
confere(CT == tot("pop_cor") and CP == tot("pretos_pardos"), f"cor ou raça: total soma {tot('pop_cor'):,.0f} = Brasil {CT:,.0f}; pretos e pardos {tot('pretos_pardos'):,.0f} = {CP:,.0f} ({100*CP/CT:.2f}%)")
RT, RA = br(renda, lambda x: x[-1] == "9680"), br(renda, lambda x: x[-1] in ("9681", "9682", "9692"))
confere(abs(tot("pop_renda") - RT) <= 0.001 * RT and abs(tot("ate_meio_sm") - RA) <= 0.001 * RA, f"renda: soma {tot('pop_renda'):,.0f} × Brasil {RT:,.0f}; até 1/2 SM {tot('ate_meio_sm'):,.0f} × {RA:,.0f} ({100*RA/RT:.2f}%)")
PB = sidra("sidra_5938_pib_brasil.json")["1"][("37",)] if os.path.exists(os.path.join(FON, "sidra_5938_pib_brasil.json")) else None
SP = sum(p["pib_mil"] for p in pib.values() if p["pib_mil"])
confere(PB is not None and abs(SP - PB) <= 0.0005 * PB, f"PIB 2023: soma dos municípios R$ {SP/1e9:,.3f} tri × Brasil no SIDRA R$ {(PB or 0)/1e9:,.3f} tri (mil reais)")

# --- grava ---
FONTE = {
    "pct_60mais": {"nome": "% da população com 60 anos ou mais", "fonte": "IBGE, Censo Demográfico 2022, SIDRA tabela 9514", "ano": 2022, "arquivo": "sidra_9514_idade.json", "universo": "população residente"},
    "alfab_15mais": {"nome": "Taxa de alfabetização, 15 anos ou mais (%)", "fonte": "IBGE, Censo Demográfico 2022, SIDRA tabela 9543", "ano": 2022, "arquivo": "sidra_9543_alfabetizacao.json", "universo": "pessoas de 15 anos ou mais"},
    "pct_renda_ate_meio_sm": {"nome": "% de moradores com rendimento domiciliar per capita de até 1/2 salário mínimo, incluindo os sem rendimento (variável 3; no lugar da pobreza do CadÚnico, MDS, 2026, cuja fonte saiu do ar: P26, 26/10/2026, 23:41)", "fonte": "IBGE, Censo Demográfico 2022, rendimento (amostra), SIDRA tabela 10296", "ano": 2022, "arquivo": "sidra_10296_renda.json", "universo": "moradores em domicílios particulares permanentes ocupados, exceto pensionista e empregado doméstico e parentes"},
    "pib_pc": {"nome": "PIB por habitante (R$ correntes; o teste usa ln_pib_pc)", "fonte": "IBGE, PIB dos Municípios 2010-2023 (base de dados), valor per capita publicado", "ano": 2023, "arquivo": "pib_municipios_2010_2023_txt.zip", "universo": "população usada pelo IBGE no PIB dos Municípios"},
    "densidade": {"nome": "Densidade demográfica (hab./km²; o teste usa ln_densidade)", "fonte": "IBGE, Censo Demográfico 2022, SIDRA tabela 4714", "ano": 2022, "arquivo": "sidra_4714_densidade.json", "universo": "população residente e área territorial"},
    "pct_evangelicos": {"nome": "% de evangélicos", "fonte": "IBGE, Censo Demográfico 2022, religiões (amostra), SIDRA tabela 9537", "ano": 2022, "arquivo": "sidra_9537_religiao.json", "universo": "pessoas de 10 anos ou mais"},
    "pct_pretos_pardos": {"nome": "% de pretos e pardos", "fonte": "IBGE, Censo Demográfico 2022, SIDRA tabela 9605", "ano": 2022, "arquivo": "sidra_9605_cor_raca.json", "universo": "população residente"},
}
for v, f in FONTE.items():
    if f["arquivo"]: f["url"] = REG[f["arquivo"]]["url"]; f["baixado_em"] = REG[f["arquivo"]]["baixado_em"]
for m in mun.values(): del m["_c"]
saida = {
    "meta": {
        "gerado_em": time.strftime("%d/%m/%Y %H:%M"), "script": "scripts/dados_sociais.py", "ticket": "T26",
        "chave": "código de 5 dígitos do município no TSE; cdi = código IBGE de 7 dígitos (lista do TSE)",
        "municipios": len(mun), "exterior": "fora (nota N06)",
        "variaveis": FONTE,
        "sem_valor": {v: l for v, l in sem.items() if l},
        "conferencias_com_erro": erros,
        "aviso": "Só dados dos municípios. Nenhum cruzamento com a eleição: os testes são do T34 (HIPOTESES.md, seção 6).",
    },
    "municipios": mun,
}
json.dump(saida, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("gravado", OUT, os.path.getsize(OUT), "bytes;", "ERROS: " + str(len(erros)) if erros else "sem erro nas conferências")
sys.exit(1 if erros else 0)
