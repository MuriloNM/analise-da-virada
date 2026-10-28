# T37: exploração guiada, rodada 2 (HIPOTESES.md, seção 8, "Rodada 2", registrada em 28/10/2026, 13:40, antes de qualquer conta de idade).
# Cinco perguntas escolhidas com o autor (D88): I1 comparecimento por idade no 1º turno; I2 os de 70 anos ou mais, por idade;
# I3 de quem é a abstenção; I4 idosos por gênero; I5b seções com mais inscritos de 60 anos ou mais, seções da mesma cidade.
# Lê em ../dados: perfil_idade.csv.gz e perfil_idade_instrucao.csv.gz (perfil_idade_base.py), analise_municipios.csv e
# analise_estados.csv (T03), secoes_presidente.csv.gz (T27) e tse_perfil_eleitor_secao/*.zip (perfil do eleitorado por seção).
# Grava perfil_idade.json; não mexe em nenhuma outra saída.
# Uso: python -I scripts/perfil_idade.py  (imprime o relatório em Markdown; sai com 1 se alguma conferência de código falhar)
import csv, gzip, io, json, os, sys, zlib, glob, zipfile, datetime
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")
AQUI = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(AQUI, "..", "dados")
SAI = os.path.join(DADOS, "perfil_idade.json")

# regras fixadas no HIPOTESES.md (2.4, 4.5 e 8, rodada 2)
SEMENTE, B_BOOT = 20261026, 1000
NIVEL = (1.25, 98.75)  # dois desfechos na I5b: intervalo de 97,5% (Bonferroni)
APTOS_MAX, PERFIL_MAX, PEQUENA = 5, 0.05, 0.5
REGIOES = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]
F70 = [7074, 7579, 8084, 8589, 9094, 9599, 9999]
def grupo(fx):
    if fx < 0: return "inválido"
    if fx < 1800: return "16 e 17"
    if fx < 6000: return "18 a 59"
    if fx < 7000: return "60 a 69"
    return "70 ou mais"
GRUPOS = ["16 e 17", "18 a 59", "60 a 69", "70 ou mais", "60 ou mais"]
GENERO = {2: "homens", 4: "mulheres"}

ok = True
def linha(texto, certo):
    global ok
    ok &= bool(certo); print(f"- {'OK' if certo else 'ERRO'}: {texto}")
def f(x): return f"{int(round(x)):,}".replace(",", ".")
def num(v, casas=1): return "—" if v is None else f"{v:.{casas}f}".replace(".", ",").replace("-", "−")
def r(v, casas=6): return None if v is None or not np.isfinite(v) else round(float(v), casas)
def sorteador(nome): return np.random.default_rng([SEMENTE, zlib.crc32(nome.encode())])
def quantil_pond(v, w, qs):
    o = np.argsort(v); c = np.cumsum(w[o]); c = c / c[-1]
    return [float(v[o][np.searchsorted(c, q)]) for q in qs]

with open(os.path.join(DADOS, "analise_municipios.csv"), encoding="utf-8") as fh: MU_TODOS = list(csv.DictReader(fh))
REG_UF = {l["uf"]: l["regiao"] for l in MU_TODOS if l["uf"] != "ZZ"}
with open(os.path.join(DADOS, "analise_estados.csv"), encoding="utf-8") as fh: EST = {l["codigo"]: l for l in csv.DictReader(fh) if l["nivel"] == "uf"}

# ======================= I1 a I4: perfil de comparecimento, 1º turno =======================
CAMPOS = ["aptos", "comp", "abst", "comp_fac", "abst_fac", "comp_obr", "abst_obr"]
P = {}  # (uf, faixa, genero) -> soma
with gzip.open(os.path.join(DADOS, "perfil_idade.csv.gz"), "rt", encoding="utf-8") as fh:
    for l in csv.DictReader(fh):
        if l["turno"] != "1": continue
        k = (l["uf"], int(l["faixa"]), int(l["genero"]))
        a = P.setdefault(k, np.zeros(len(CAMPOS), dtype=np.int64))
        a += np.array([int(l[c]) for c in CAMPOS], dtype=np.int64)
FAIXAS = sorted({k[1] for k in P})
def lugar_ok(lugar, uf):
    if lugar == "Brasil": return uf != "ZZ"
    if lugar == "Exterior": return uf == "ZZ"
    if lugar in REGIOES: return REG_UF.get(uf) == lugar
    return uf == lugar
LUGARES = ["Brasil"] + REGIOES + sorted(REG_UF) + ["Exterior"]
def soma(lugar, cond_faixa=lambda fx: True, cond_gen=lambda g: True):
    s = np.zeros(len(CAMPOS), dtype=np.int64)
    for (u, fx, g), v in P.items():
        if lugar_ok(lugar, u) and cond_faixa(fx) and cond_gen(g): s += v
    return s
def no_grupo(gr): return (lambda fx: grupo(fx) in ("60 a 69", "70 ou mais")) if gr == "60 ou mais" else (lambda fx: grupo(fx) == gr)
def taxa(s): return None if s[0] == 0 else 100 * s[1] / s[0]
def item(s): return {"aptos": int(s[0]), "comparecimento": int(s[1]), "abstencao": int(s[2]), "taxa_comparecimento": r(taxa(s), 4),
                     "maioria_votou": None if s[0] == 0 else bool(s[1] > s[0] / 2)}

print("# Exploração guiada, rodada 2 (T37): relatório técnico\n")
print("### Conferências das entradas\n")
tot_br = soma("Brasil"); tot_zz = soma("Exterior")
linha(f"perfil, Brasil sem o exterior: {f(tot_br[0])} aptos, {f(tot_br[1])} comparecimento; exterior {f(tot_zz[0])} e {f(tot_zz[1])}", tot_br[0] > 0)
linha("soma das faixas = total em cada lugar (aptos = comparecimento + abstenção em cada faixa)",
      all((v[0] == v[1] + v[2]) for v in P.values()))
fac_ok = {"16_17_e_70_mais_sem_obrigatorio": int(sum(v[5] + v[6] for (u, fx, g), v in P.items() if grupo(fx) in ("16 e 17", "70 ou mais")))}
fac_1869 = soma("Brasil", lambda fx: grupo(fx) in ("18 a 59", "60 a 69"))
fac_ok["18_a_69_facultativo_aptos"] = int(fac_1869[3] + fac_1869[4])
INS = {}
with gzip.open(os.path.join(DADOS, "perfil_idade_instrucao.csv.gz"), "rt", encoding="utf-8") as fh:
    for l in csv.DictReader(fh):
        if l["turno"] == "1" and l["uf"] != "ZZ" and grupo(int(l["faixa"])) in ("18 a 59", "60 a 69") and l["instrucao"] == "1":
            INS["analfabetos_18_a_69_aptos"] = INS.get("analfabetos_18_a_69_aptos", 0) + int(l["aptos"])
fac_ok.update(INS)
linha(f"16, 17 e 70 ou mais: nenhum eleitor na coluna de voto obrigatório ({f(fac_ok['16_17_e_70_mais_sem_obrigatorio'])})",
      fac_ok["16_17_e_70_mais_sem_obrigatorio"] == 0)
print(f"- Nota: 18 a 69 com voto facultativo: {f(fac_ok['18_a_69_facultativo_aptos'])} aptos; analfabetos de 18 a 69 no perfil: "
      f"{f(INS.get('analfabetos_18_a_69_aptos', 0))} (o voto do analfabeto é facultativo em qualquer idade; o registro previa a coluna obrigatória inteira).")
dif_uf = {}
for u in sorted(REG_UF) + ["ZZ"]:
    s = soma("Exterior" if u == "ZZ" else u)
    o = MU_TODOS and [l for l in MU_TODOS if l["uf"] == u]
    oa, oc = sum(int(l["eleitorado_1t"]) for l in o), sum(int(l["comparecimento_1t"]) for l in o)
    dif_uf[u] = {"aptos": int(s[0] - oa), "comparecimento": int(s[1] - oc)}
print("- Perfil − oficial (T03), por estado, aptos: " + "; ".join(f"{u} {dif_uf[u]['aptos']:+d}" for u in dif_uf))

R = {"rotulo": "exploratório, não registrado antes das contas", "semente": SEMENTE, "bootstrap": B_BOOT,
     "gerado_em": datetime.datetime.now().astimezone().isoformat(timespec="seconds"), "turnos_no_perfil": [1],
     "conferencias_entrada": {"facultativo": fac_ok, "perfil_menos_oficial_por_uf": dif_uf}}

# I1
I1 = {}
for lg in LUGARES:
    I1[lg] = {"grupos": {gr: item(soma(lg, no_grupo(gr))) for gr in GRUPOS}, "total": item(soma(lg))}
    if lg in ["Brasil", "Exterior"] + REGIOES:
        I1[lg]["faixas"] = {str(fx): item(soma(lg, lambda x, fx=fx: x == fx)) for fx in FAIXAS}
R["I1"] = I1
print("\n### I1. Comparecimento por idade, 1º turno\n")
print("| Lugar | " + " | ".join(GRUPOS) + " | Total |\n|---|" + "---|" * (len(GRUPOS) + 1))
for lg in LUGARES:
    print(f"| {lg} | " + " | ".join(num(I1[lg]["grupos"][g]["taxa_comparecimento"]) for g in GRUPOS) + f" | {num(I1[lg]['total']['taxa_comparecimento'])} |")
print("\nBrasil, por faixa do TSE: " + "; ".join(f"{fx} {num(I1['Brasil']['faixas'][str(fx)]['taxa_comparecimento'])}% ({f(I1['Brasil']['faixas'][str(fx)]['aptos'])})" for fx in FAIXAS))

# I2
I2 = {}
for lg in LUGARES:
    fx_t = [(fx, taxa(soma(lg, lambda x, fx=fx: x == fx))) for fx in F70]
    abaixo = next((fx for fx, t in fx_t if t is not None and t < 50), None)
    I2[lg] = {"faixas": {str(fx): r(t, 4) for fx, t in fx_t}, "primeira_faixa_abaixo_de_50": abaixo}
R["I2"] = I2
print("\n### I2. Os de 70 anos ou mais, por idade\n")
print("| Lugar | " + " | ".join(str(x) for x in F70) + " | Primeira abaixo de 50% |\n|---|" + "---|" * (len(F70) + 1))
for lg in LUGARES:
    print(f"| {lg} | " + " | ".join(num(I2[lg]["faixas"][str(x)]) for x in F70) + f" | {I2[lg]['primeira_faixa_abaixo_de_50']} |")

# I3
I3 = {}
for lg in ["Brasil"] + REGIOES:
    t = soma(lg); I3[lg] = {}
    for gr in GRUPOS:
        s = soma(lg, no_grupo(gr)); pa, pb = 100 * s[0] / t[0], 100 * s[2] / t[2]
        I3[lg][gr] = {"parte_dos_aptos": r(pa, 4), "parte_da_abstencao": r(pb, 4), "razao": r(pb / pa, 4), "abstencao": int(s[2])}
R["I3"] = I3
print("\n### I3. De quem é a abstenção (parte dos que faltaram × parte dos aptos)\n")
print("| Lugar | " + " | ".join(GRUPOS) + " |\n|---|" + "---|" * len(GRUPOS))
for lg in I3:
    print(f"| {lg} | " + " | ".join(f"{num(I3[lg][g]['parte_da_abstencao'])} × {num(I3[lg][g]['parte_dos_aptos'])}" for g in GRUPOS) + " |")

# I4
GENS = sorted({k[2] for k in P})
I4 = {}
for lg in ["Brasil"] + REGIOES:
    I4[lg] = {}
    for g in GENS:
        nome = GENERO.get(g, f"código {g}")
        d = {gr: item(soma(lg, no_grupo(gr), lambda x, g=g: x == g)) for gr in ["18 a 59", "60 a 69", "70 ou mais", "60 ou mais"]}
        d.update({str(fx): item(soma(lg, lambda x, fx=fx: x == fx, lambda x, g=g: x == g)) for fx in F70})
        I4[lg][nome] = d
R["I4"] = I4
print("\n### I4. Por gênero\n")
print("| Lugar | Gênero | 18 a 59 | 60 a 69 | 70 ou mais | " + " | ".join(str(x) for x in F70) + " |\n|---|---|---|---|---|" + "---|" * len(F70))
for lg in I4:
    for nome, d in I4[lg].items():
        print(f"| {lg} | {nome} | " + " | ".join(num(d[k]["taxa_comparecimento"]) for k in ["18 a 59", "60 a 69", "70 ou mais"] + [str(x) for x in F70]) + " |")

# ======================= I5b: seções com mais inscritos de 60 anos ou mais =======================
cols = {k: [] for k in ["E1", "E2", "C1", "C2", "L1", "F1", "L2", "F2", "ag"]}
uf_l, cd_l, chave = [], [], []
with gzip.open(os.path.join(DADOS, "secoes_presidente.csv.gz"), "rt", encoding="utf-8") as fh:
    for l in csv.DictReader(fh):
        if l["uf"] == "ZZ": continue
        n = lambda k: int(l[k] or 0)
        uf_l.append(l["uf"]); cd_l.append(l["cd_mun"]); chave.append((l["uf"], l["cd_mun"], int(l["zona"]), int(l["secao"])))
        for a, b in [("E1", "t1_aptos"), ("E2", "t2_aptos"), ("C1", "t1_comp"), ("C2", "t2_comp"), ("L1", "t1_13"), ("F1", "t1_22"),
                     ("L2", "t2_13"), ("F2", "t2_22")]: cols[a].append(n(b))
        cols["ag"].append(len([x for x in l["t2_agregadas"].split("/") if x.strip()]))
uf, cd = np.array(uf_l), np.array(cd_l)
V = {k: np.array(v, dtype=float) for k, v in cols.items()}
E1, E2, C1, C2, L1, F1, L2, F2 = (V[k] for k in ("E1", "E2", "C1", "C2", "L1", "F1", "L2", "F2"))
pos = {k: i for i, k in enumerate(chave)}
NT, N60, N70 = np.zeros(len(chave)), np.zeros(len(chave)), np.zeros(len(chave))
fx_perfil, sem_par, ger = {}, 0, set()
for zp in sorted(glob.glob(os.path.join(DADOS, "tse_perfil_eleitor_secao", "perfil_eleitor_secao_2026_*.zip"))):
    if zp.endswith("_ZZ.zip"): continue
    with zipfile.ZipFile(zp) as z:
        nome = [n for n in z.namelist() if n.endswith(".csv")][0]
        with z.open(nome) as bruto:
            for l in csv.DictReader(io.TextIOWrapper(bruto, encoding="latin-1", newline=""), delimiter=";"):
                fx = int(l["CD_FAIXA_ETARIA"]); q = int(l["QT_ELEITORES"]); ger.add(l["DT_GERACAO"])
                fx_perfil[fx] = l["DS_FAIXA_ETARIA"].strip()
                i = pos.get((l["SG_UF"], l["CD_MUNICIPIO"], int(l["NR_ZONA"]), int(l["NR_SECAO"])))
                if i is None: sem_par += q; continue
                NT[i] += q
                if 6000 <= fx: N60[i] += q
                if 7000 <= fx: N70[i] += q
COM = NT > 0
print("\n### I5b. Conferências das entradas\n")
linha(f"seções do Brasil: {f(len(uf))}", len(uf) == 497897)
print(f"- Faixas do perfil por seção: " + "; ".join(f"{k} {v}" for k, v in sorted(fx_perfil.items())) + f" | gerado em {sorted(ger)}")
linha(f"seções com perfil: {f(COM.sum())}; sem perfil (saem): {f((~COM).sum())}; inscritos sem seção correspondente: {f(sem_par)}", COM.sum() > 490000)
dif_pf = np.abs(NT - E1) / E1
print(f"- Inscritos no perfil × aptos do 1º turno: soma {f(NT.sum())} × {f(E1.sum())}; seções iguais: {f((NT == E1).sum())}; "
      f"a mais de 5%: {f((dif_pf > PERFIL_MAX).sum())}")

idx = {c: i for i, c in enumerate(sorted(set(cd)))}; mi = np.array([idx[c] for c in cd]); M = len(idx)
uf_m = np.empty(M, dtype=object); uf_m[mi] = uf
reg_m = np.array([REG_UF[u] for u in uf_m])
UFS = sorted(set(uf)); ui = {u: i for i, u in enumerate(UFS)}
SEM_AG, SEM_APT, SEM_PF = V["ag"] == 0, np.abs(E2 - E1) <= APTOS_MAX, dif_pf <= PERFIL_MAX
p60 = 100 * N60 / np.where(COM, NT, 1); p70 = 100 * N70 / np.where(COM, NT, 1)
da = 100 * ((E2 - C2) / E2 - (E1 - C1) / E1)
ok_s = (L1 > 0) & (F1 > 0) & (L2 > 0) & (F2 > 0)
s1 = 100 * L1 / np.where(L1 + F1 > 0, L1 + F1, 1)
ds = np.where(ok_s, 100 * (L2 / np.where(ok_s, L2 + F2, 1) - L1 / np.where(ok_s, L1 + F1, 1)), 0)
DES = {"abstencao": (da, COM), "fatia_lula": (ds, COM & ok_s)}

def tira_media(v, w, sel):
    sw = np.bincount(mi[sel], w[sel], M)
    return v - (np.bincount(mi[sel], (w * v)[sel], M) / np.where(sw > 0, sw, 1))[mi]
def reta(y, x, sel, peso=True, fe=True, ctrl=None):
    w = E1 if peso else np.ones(len(E1)); ws = np.where(sel, w, 0)
    if fe: xt, yt = tira_media(x, w, sel), tira_media(y, w, sel)
    else: xt, yt = x - np.sum(ws * x) / ws.sum(), y - np.sum(ws * y) / ws.sum()
    if ctrl is not None:  # Frisch-Waugh: tira de x a parte explicada por ctrl (já sem a média do município)
        ct = tira_media(ctrl, w, sel); xt = xt - (np.sum(ws * ct * xt) / np.sum(ws * ct * ct)) * ct
    return {"Sxx": np.bincount(mi, ws * xt * xt, M), "Sxy": np.bincount(mi, ws * xt * yt, M), "xt": xt, "yt": yt, "ws": ws}
def boot_grupos(gm, rng):
    _, gi = np.unique(gm, return_inverse=True); G = gi.max() + 1; k = np.zeros((B_BOOT, G))
    np.add.at(k, (np.repeat(np.arange(B_BOOT), G), rng.integers(0, G, size=B_BOOT * G)), 1)
    return k[:, gi]
def item_reta(S, lugar, ms, nome, sel):
    b = S["Sxy"][ms].sum() / S["Sxx"][ms].sum()
    cont = boot_grupos(uf_m[ms], sorteador(nome))
    bb = (cont @ S["Sxy"][ms]) / (cont @ S["Sxx"][ms]); lo, hi = np.percentile(bb, NIVEL)
    lm = np.zeros(M, bool); lm[ms] = True; s_ = sel & lm[mi]
    q = quantil_pond(S["xt"][s_], S["ws"][s_], [0.25, 0.75])
    return {"lugar": lugar, "municipios": len(ms), "secoes": int(s_.sum()), "b_por_10": r(10 * b, 4),
            "ic975_por_10": [r(10 * lo, 4), r(10 * hi, 4)], "efeito_interquartil_pp": r(b * (q[1] - q[0]), 4),
            "quartis_x_sem_media_do_municipio": [r(q[0], 3), r(q[1], 3)]}
def cr1_estado(S):
    b = S["Sxy"].sum() / S["Sxx"].sum(); e = S["yt"] - b * S["xt"]
    sg = np.bincount(np.array([ui[u] for u in uf]), S["ws"] * S["xt"] * e, len(UFS))
    se = np.sqrt(len(UFS) / (len(UFS) - 1) * np.sum(sg ** 2)) / S["Sxx"].sum()
    from scipy import stats
    t = stats.t.ppf(NIVEL[1] / 100, len(UFS) - 1)
    return {"b_por_10": r(10 * b, 4), "ic975_por_10": [r(10 * (b - t * se), 4), r(10 * (b + t * se), 4)]}
MS = lambda sel, lm=None: np.flatnonzero((np.bincount(mi, sel, M) > 0) & (np.ones(M, bool) if lm is None else lm))
def lado(ic): return 1 if ic[0] > 0 else -1 if ic[1] < 0 else 0

I5 = {}
for nome_d, (y, sel) in DES.items():
    S = reta(y, p60, sel)
    princ = [item_reta(S, "Brasil", MS(sel), f"I5b {nome_d} Brasil", sel)]
    princ += [item_reta(S, rg, MS(sel, reg_m == rg), f"I5b {nome_d} {rg}", sel) for rg in REGIOES]
    conf = {"sem_peso": item_reta(reta(y, p60, sel, peso=False), "Brasil", MS(sel), f"I5b {nome_d} sem peso", sel),
            "sem_agregadas": item_reta(reta(y, p60, sel & SEM_AG), "Brasil", MS(sel & SEM_AG), f"I5b {nome_d} sem agregadas", sel & SEM_AG),
            "sem_aptos_que_mudam": item_reta(reta(y, p60, sel & SEM_APT), "Brasil", MS(sel & SEM_APT), f"I5b {nome_d} sem aptos", sel & SEM_APT),
            "p70": item_reta(reta(y, p70, sel), "Brasil", MS(sel), f"I5b {nome_d} p70", sel),
            "erro_agrupado_por_estado": cr1_estado(S),
            "perfil_igual_aos_aptos": item_reta(reta(y, p60, sel & SEM_PF), "Brasil", MS(sel & SEM_PF), f"I5b {nome_d} perfil", sel & SEM_PF)}
    ctx = {"sem_efeito_de_municipio": item_reta(reta(y, p60, sel, fe=False), "Brasil", MS(sel), f"I5b {nome_d} sem efeito", sel),
           "com_fatia_do_lula_no_1t": item_reta(reta(y, p60, sel, ctrl=s1), "Brasil", MS(sel), f"I5b {nome_d} com s1", sel)}
    br = princ[0]; l0 = lado(br["ic975_por_10"])
    achado = bool(l0 != 0 and all(lado(c["ic975_por_10"]) == l0 for c in conf.values()))
    I5[nome_d] = {"principal": princ, "conferencias": conf, "contexto": ctx, "achado": achado,
                  "tamanho": "pequena" if abs(br["efeito_interquartil_pp"]) < PEQUENA else "não pequena"}
    linha(f"I5b {nome_d}: seções na conta {f(sel.sum())}", sel.sum() > 480000)
R["I5b"] = I5
R["I5b_descritivo"] = {"secoes_com_perfil": int(COM.sum()), "sem_perfil": int((~COM).sum()), "inscritos_sem_secao": int(sem_par),
                      "p60_quartis_ponderados": [r(x, 3) for x in quantil_pond(p60[COM], E1[COM], [0.25, 0.5, 0.75])],
                      "p70_quartis_ponderados": [r(x, 3) for x in quantil_pond(p70[COM], E1[COM], [0.25, 0.5, 0.75])],
                      "perfil_gerado_em": sorted(ger), "secoes_perfil_difere_mais_de_5pct": int((dif_pf > PERFIL_MAX).sum())}

print("\n### I5b. Resultado (β por 10 pontos de p60; intervalo de 97,5%)\n")
for nome_d, d in I5.items():
    print(f"**{nome_d}** — achado: {d['achado']}; tamanho: {d['tamanho']}\n")
    print("| Versão | β por 10 | Intervalo | Efeito entre quartis (p.p.) | Seções |\n|---|---|---|---|---|")
    for c in d["principal"]:
        print(f"| {c['lugar']} | {num(c['b_por_10'], 3)} | {num(c['ic975_por_10'][0], 3)} a {num(c['ic975_por_10'][1], 3)} | {num(c['efeito_interquartil_pp'], 3)} | {f(c['secoes'])} |")
    for k, c in list(d["conferencias"].items()) + [("contexto: " + k, v) for k, v in d["contexto"].items()]:
        print(f"| {k} | {num(c['b_por_10'], 3)} | {num(c['ic975_por_10'][0], 3)} a {num(c['ic975_por_10'][1], 3)} | {num(c.get('efeito_interquartil_pp'), 3)} | {f(c['secoes']) if 'secoes' in c else '—'} |")
    print()
print("p60 (quartis ponderados das seções):", R["I5b_descritivo"]["p60_quartis_ponderados"], "| p70:", R["I5b_descritivo"]["p70_quartis_ponderados"])

with open(SAI, "w", encoding="utf-8") as fh: json.dump(R, fh, ensure_ascii=False, indent=1)
print(f"\nGravado: {os.path.relpath(SAI, os.path.join(AQUI, '..'))}")
sys.exit(0 if ok else 1)
