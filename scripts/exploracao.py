# T33: exploração guiada, rodada 1 (HIPOTESES.md, seção 8, "Rodada 1", registrada em 27/10/2026, 10:40, antes de qualquer conta).
# Cinco perguntas escolhidas com o autor (D60): E1 votos de cada um dos outros candidatos; E2 municípios em que um passou o outro;
# E3 abstenção nos estados com 2º turno para governador; E4 comparecimento × força de cada um, seções da mesma cidade;
# E5 cada um cresceu mais onde era mais fraco, seções da mesma cidade (com a correção do acaso).
# Lê em ../dados: secoes_presidente.csv.gz (T27), analise_municipios.csv (T03), tse_6259_uf/ (T01), inferencia.json (T06/T32/T35)
# e secoes_inferencia.json (T35, para a conferência de código da E1). Grava exploracao.json; não mexe em nenhuma outra saída.
# Uso: python -I scripts/exploracao.py  (imprime o relatório em Markdown; sai com 1 se alguma conferência falhar)
import csv, gzip, json, os, sys, zlib, glob, datetime, itertools
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")  # o relatório tem acentos e "−" (diário, D03)
AQUI = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(AQUI, "..", "dados")
SAI = os.path.join(DADOS, "exploracao.json")

# regras fixadas no HIPOTESES.md (2.4, 4.2, 4.5 e 8)
SEMENTE, B_BOOT, B_SELV = 20261026, 1000, 9999
MIN_MUN, MEIA_LARGURA, APTOS_MAX, PEQUENA = 30, 0.10, 5, 0.5
REGIOES = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]
RESTO = ["30", "80", "16", "27", "21", "35", "29"]  # E1: os outros sete, juntos (o 28 fica fora dos válidos, N21)
FONTES_E1 = [("70", "Avante (70)"), ("14", "Missão (14)"), ("55", "PSD (55)"), ("resto", "os outros sete, juntos"),
             ("C", "variação do comparecimento"), ("R", "queda de brancos e nulos")]

ok = True
def linha(texto, certo):
    global ok
    ok &= bool(certo); print(f"- {'OK' if certo else 'ERRO'}: {texto}")
def f(x): return f"{int(round(x)):,}".replace(",", ".")
def num(v, casas=1): return "—" if v is None else f"{v:.{casas}f}".replace(".", ",").replace("-", "−")
def p1(v): return num(None if v is None else 100 * v)
def r(v, casas=6): return None if v is None or not np.isfinite(v) else round(float(v), casas)
def sorteador(nome): return np.random.default_rng([SEMENTE, zlib.crc32(nome.encode())])
def quantil_pond(v, w, qs):
    o = np.argsort(v); c = np.cumsum(w[o]); c = c / c[-1]
    return [float(v[o][np.searchsorted(c, q)]) for q in qs]

# ---------- dados por seção (as mesmas do T35) ----------
with open(os.path.join(DADOS, "analise_municipios.csv"), encoding="utf-8") as fh: MU_TODOS = list(csv.DictReader(fh))
MU = [l for l in MU_TODOS if l["uf"] != "ZZ"]
REG = {l["cd_tse"]: l["regiao"] for l in MU}
CAND1 = ["13", "14", "16", "21", "22", "27", "28", "29", "30", "35", "55", "70", "80"]
cols = {k: [] for k in ["uf", "cd", "inst1", "inst2", "E1", "E2", "C1", "C2", "L1", "F1", "L2", "F2", "BN1", "BN2", "ag",
                        "V70", "V14", "V55", "Vresto", "maior_outro"]}
with gzip.open(os.path.join(DADOS, "secoes_presidente.csv.gz"), "rt", encoding="utf-8") as fh:
    for l in csv.DictReader(fh):
        if l["uf"] == "ZZ": continue  # exterior fora (2.1)
        n = lambda k: int(l[k] or 0)
        cols["uf"].append(l["uf"]); cols["cd"].append(l["cd_mun"])
        cols["inst1"].append(l["t1_instalada"] == "1"); cols["inst2"].append(l["t2_instalada"] == "1")
        for a, b in [("E1", "t1_aptos"), ("E2", "t2_aptos"), ("C1", "t1_comp"), ("C2", "t2_comp"), ("L1", "t1_13"), ("F1", "t1_22"),
                     ("L2", "t2_13"), ("F2", "t2_22"), ("V70", "t1_70"), ("V14", "t1_14"), ("V55", "t1_55")]: cols[a].append(n(b))
        cols["Vresto"].append(sum(n("t1_" + c) for c in RESTO))
        cols["maior_outro"].append(max(n("t1_" + c) for c in CAND1 if c not in ("13", "22", "28")))
        cols["BN1"].append(n("t1_brancos") + n("t1_nulos") + n("t1_28")); cols["BN2"].append(n("t2_brancos") + n("t2_nulos"))
        cols["ag"].append(len([x for x in l["t2_agregadas"].split("/") if x.strip()]))
uf, cd = np.array(cols.pop("uf")), np.array(cols.pop("cd"))
V = {k: np.array(v, dtype=bool if k in ("inst1", "inst2") else float) for k, v in cols.items()}
E1, E2, C1, C2, L1, F1, L2, F2, BN1, BN2 = (V[k] for k in ("E1", "E2", "C1", "C2", "L1", "F1", "L2", "F2", "BN1", "BN2"))
O1 = V["V70"] + V["V14"] + V["V55"] + V["Vresto"]
dL, dF, dC, R = L2 - L1, F2 - F1, C2 - C1, BN1 - BN2
idx = {c: i for i, c in enumerate(sorted(set(cd)))}; mi = np.array([idx[c] for c in cd]); M = len(idx)
uf_m = np.empty(M, dtype=object); uf_m[mi] = uf
reg_m = np.array([REG[c] for c in sorted(idx)])
SEM_AG, SEM_APT = V["ag"] == 0, np.abs(E2 - E1) <= APTOS_MAX

print("### Conferência das entradas\n")
linha(f"seções do Brasil: {f(len(uf))}, todas instaladas e com aptos nos dois turnos",
      len(uf) == 497897 and (V["inst1"] & V["inst2"] & (E1 > 0) & (E2 > 0)).all())
linha("identidade ΔL + ΔF = (Avante + Missão + PSD + resto) + ΔC + R em todas as seções", np.all(dL + dF == O1 + dC + R))

def tira_media(v, w, sel):  # média ponderada de cada município (efeito fixo), só com as seções da versão
    sw = np.bincount(mi[sel], w[sel], M)
    return v - (np.bincount(mi[sel], (w * v)[sel], M) / np.where(sw > 0, sw, 1))[mi]
def boot_grupos(gm, rng):  # gm: o grupo de cada município do lugar; reamostra grupos inteiros
    _, gi = np.unique(gm, return_inverse=True); G = gi.max() + 1; k = np.zeros((B_BOOT, G))
    np.add.at(k, (np.repeat(np.arange(B_BOOT), G), rng.integers(0, G, size=B_BOOT * G)), 1)
    return k[:, gi]
def boot_estratos(estr, rng):  # reamostra municípios dentro de cada estado, a mesma quantidade de cada um
    cont = np.zeros((B_BOOT, len(estr)))
    for s in np.unique(estr):
        pos = np.flatnonzero(estr == s); k = len(pos)
        np.add.at(cont, (np.repeat(np.arange(B_BOOT), k), pos[rng.integers(0, k, size=B_BOOT * k)]), 1)
    return cont
def lugares(com_uf):
    out = [("brasil", "Brasil", np.ones(M, bool))] + [("regiao", rg, reg_m == rg) for rg in REGIOES]
    return out + ([("uf", u, uf_m == u) for u in sorted(set(uf_m))] if com_uf else [])
def contagens(nivel, ms, rng, intervalo):  # pesos de reamostragem dos municípios do lugar
    if nivel == "uf": return boot_grupos(ms, rng)
    return boot_grupos(uf_m[ms], rng) if intervalo == "estados" else boot_estratos(uf_m[ms], rng)

# ======================= E1 =======================
def e1_versao(nome, sel, peso=True, intervalo="estados", fontes=None):
    fontes = fontes or [V["V70"], V["V14"], V["V55"], V["Vresto"]]
    w = E1 if peso else np.ones(len(E1))
    X = np.column_stack([v / E1 for v in fontes] + [dC / E1, R / E1]); k = X.shape[1]
    X = np.column_stack([tira_media(X[:, j], w, sel) for j in range(k)]); y = tira_media(dL / E1, w, sel)
    ws = np.where(sel, w, 0)
    A = np.stack([np.bincount(mi, ws * X[:, i] * X[:, j], M) for i in range(k) for j in range(k)], 1)
    b = np.stack([np.bincount(mi, ws * X[:, i] * y, M) for i in range(k)], 1)
    res = lambda AA, bb: np.linalg.solve(AA.reshape(bb.shape[:-1] + (k, k)), bb[..., None])[..., 0]
    rots = FONTES_E1 if k == 6 else [("O", "outros"), ("C", ""), ("R", "")]
    out = []
    for nivel, lugar, lm in lugares(False):
        ms = np.flatnonzero(lm & (np.bincount(mi, sel, M) > 0))
        est = res(A[ms].sum(0), b[ms].sum(0))
        cont = contagens(nivel, ms, sorteador(f"E1 {nome} {lugar}"), intervalo)
        bb = res(cont @ A[ms], cont @ b[ms]); lo, hi = np.percentile(bb, [2.5, 97.5], axis=0)
        fora = [c for j, (c, _) in enumerate(rots) if not 0 <= est[j] <= 1]
        item = {"nivel": nivel, "lugar": lugar, "n": len(ms), "secoes": int((sel & lm[mi]).sum()), "fontes": {}, "modelo_nao_descreve": fora}
        for j, (c, rot) in enumerate(rots):
            meia = (hi[j] - lo[j]) / 2
            d = {"fonte": rot, "lula": r(est[j]), "lula_ic95": [r(lo[j]), r(hi[j])], "flavio": r(1 - est[j]),
                 "flavio_ic95": [r(1 - hi[j]), r(1 - lo[j])], "meia_largura": r(meia), "aviso_modelo": bool(fora)}
            if c in fora: d.update(passa=False, motivo="estimativa fora de 0% a 100%")
            elif meia > MEIA_LARGURA: d.update(passa=False, motivo="resultados muito dispersos")
            else: d.update(passa=True, maior_parte="Lula" if lo[j] > 0.5 else "Flávio" if hi[j] < 0.5 else "sem lado claro")
            item["fontes"][c] = d
        out.append(item)
    return out
def leitura(d): return d.get("maior_parte") if d["passa"] else "não deu"

todas = np.ones(len(E1), bool)
print("\n### E1 · conferências de código\n")
E1_JUNTOS = e1_versao("juntos", todas, fontes=[O1])
with open(os.path.join(DADOS, "secoes_inferencia.json"), encoding="utf-8") as fh: SI = json.load(fh)
dif_t35 = max(abs(E1_JUNTOS[i]["fontes"][c]["lula"] - SI["por_lugar"][i]["fontes"][c]["lula"]) for i in range(6) for c in ("O", "C", "R"))
linha(f"com os outros numa fonte só, a conta reproduz o T35 no Brasil e nas 5 regiões (maior diferença {dif_t35:.1e})", dif_t35 < 1e-6)
E1_PRINC = e1_versao("principal", todas)
E1_CONF = {"sem_peso": e1_versao("sem peso", todas, peso=False),
           "municipios_dentro_do_estado": e1_versao("municípios dentro do estado", todas, intervalo="estratos"),
           "sem_agregadas": e1_versao("sem agregadas", SEM_AG),
           "sem_aptos_que_mudam": e1_versao("sem aptos que mudam", SEM_APT)}
# refeita com ΔF, a parte do Flávio é 1 − a do Lula (Brasil)
_w = E1; _X = np.column_stack([tira_media(v / E1, _w, todas) for v in (V["V70"], V["V14"], V["V55"], V["Vresto"], dC, R)])
_bF = np.linalg.lstsq(_X * np.sqrt(_w)[:, None], tira_media(dF / E1, _w, todas) * np.sqrt(_w), rcond=None)[0]
linha("Brasil: refeita com ΔF, a parte do Flávio é 1 − a do Lula nas seis fontes",
      np.allclose(_bF, [E1_PRINC[0]["fontes"][c]["flavio"] for c, _ in FONTES_E1], atol=1e-6))
for l in E1_PRINC:
    for c, _ in FONTES_E1:
        d = l["fontes"][c]; lp = leitura(d)
        d["conferencias_mantem"] = [k for k, v in E1_CONF.items() if leitura(next(x for x in v if x["lugar"] == l["lugar"])["fontes"][c]) == lp]
BR1 = E1_PRINC[0]["fontes"]
E1_ACHADO = {c: leitura(BR1[c]) for c, _ in FONTES_E1[:4]
             if leitura(BR1[c]) in ("Lula", "Flávio") and len(BR1[c]["conferencias_mantem"]) == len(E1_CONF)}
E1_OPOSTOS = len(set(E1_ACHADO.values())) == 2

# ======================= E2 =======================
def lado(a, b): return "Lula" if a > b else "Flávio" if b > a else "empate"
def e2_conta(linhas):
    casas, delta = {}, {"subiu": [0, 0], "caiu": [0, 0], "igual": [0, 0]}
    for L1_, F1_, L2_, F2_, E_ in linhas:
        k = f"{lado(L1_, F1_)} → {lado(L2_, F2_)}"; c = casas.setdefault(k, [0, 0]); c[0] += 1; c[1] += E_
        s1 = L1_ / (L1_ + F1_) if L1_ + F1_ else None; s2 = L2_ / (L2_ + F2_) if L2_ + F2_ else None
        if s1 is None or s2 is None: continue
        dd = delta["subiu" if s2 > s1 else "caiu" if s2 < s1 else "igual"]; dd[0] += 1; dd[1] += E_
    return {"casas": {k: {"n": v[0], "eleitores_1t": int(v[1])} for k, v in sorted(casas.items())},
            "fatia_lula": {k: {"n": v[0], "eleitores_1t": int(v[1])} for k, v in delta.items()}}
def linhas_mu(lst): return [(int(l["lula_1t"]), int(l["flavio_1t"]), int(l["lula_2t"]), int(l["flavio_2t"]), int(l["eleitorado_1t"])) for l in lst]
RES_E2 = {"brasil": e2_conta(linhas_mu(MU)), "por_uf": {u: e2_conta(linhas_mu([l for l in MU if l["uf"] == u])) for u in sorted({l["uf"] for l in MU})},
      "com_exterior": e2_conta(linhas_mu(MU_TODOS)), "exterior": e2_conta(linhas_mu([l for l in MU_TODOS if l["uf"] == "ZZ"]))}
# conferência (a): vencedor do 1º turno entre todos os candidatos, pelas seções somadas por município
Vm = {k: np.bincount(mi, V[k], M) for k in ("L1", "F1", "V70", "V14", "V55")}
VRm = {c: np.zeros(M) for c in RESTO}
# votos de cada outro candidato por município (o resto, candidato a candidato, para achar o mais votado)
with gzip.open(os.path.join(DADOS, "secoes_presidente.csv.gz"), "rt", encoding="utf-8") as fh:
    acc = {c: {} for c in RESTO}
    for l in csv.DictReader(fh):
        if l["uf"] == "ZZ": continue
        for c in RESTO: acc[c][l["cd_mun"]] = acc[c].get(l["cd_mun"], 0) + int(l["t1_" + c] or 0)
for c in RESTO:
    for m_, v in acc[c].items(): VRm[c][idx[m_]] = v
outros_m = np.column_stack([Vm["V70"], Vm["V14"], Vm["V55"]] + [VRm[c] for c in RESTO])
venc_todos = np.where(outros_m.max(1) > np.maximum(Vm["L1"], Vm["F1"]), "outro", np.where(Vm["L1"] > Vm["F1"], "Lula", np.where(Vm["F1"] > Vm["L1"], "Flávio", "empate")))
RES_E2["conf_vencedor_entre_todos"] = {k: int((venc_todos == k).sum()) for k in ("Lula", "Flávio", "outro", "empate")}
linha("E2: as somas das seções dão os mesmos votos de Lula e Flávio no 1º turno que a base municipal",
      all(int(Vm["L1"][idx[l["cd_tse"]]]) == int(l["lula_1t"]) and int(Vm["F1"][idx[l["cd_tse"]]]) == int(l["flavio_1t"]) for l in MU))
# conferência (b): por seção
RES_E2["conf_secoes"] = e2_conta(zip(L1, F1, L2, F2, E1))

# ======================= E3 =======================
GOV2T = []
for fn in sorted(glob.glob(os.path.join(DADOS, "tse_6259_uf", "*-c0003-e006259-u.json"))):
    with open(fn, encoding="utf-8") as fh: dgov = json.load(fh)
    sts = []
    def anda(o):
        if isinstance(o, dict):
            if "st" in o and "nmu" in o: sts.append(o["st"])
            for v in o.values(): anda(v)
        elif isinstance(o, list):
            for v in o: anda(v)
    anda(dgov)
    if any("turno" in s.lower() for s in sts): GOV2T.append(os.path.basename(fn)[:2].upper())
linha(f"E3: estados com 2º turno para governador, pela situação no 1º turno: {', '.join(GOV2T)}", GOV2T == ["AC", "AM", "DF", "ES", "RN", "TO"])
UFS = sorted({l["uf"] for l in MU}); ui = {u: i for i, u in enumerate(UFS)}
mu_uf = np.array([ui[l["uf"]] for l in MU]); mu_E = np.array([float(l["eleitorado_1t"]) for l in MU])
mu_da = np.array([float(l["var_taxa_abst_pp"]) for l in MU]); mu_ds = np.array([float(l["var_fatia_pp"]) for l in MU])
reg_uf = np.array([next(l["regiao"] for l in MU if l["uf"] == u) for u in UFS])
g_obs = np.array([u in GOV2T for u in UFS])
COMB = np.array(list(itertools.combinations(range(27), 6)))
def e3_b(y, w, ufs_ok, combos, fe_regiao=False):
    """b da regressão y = a (+ efeito de região) + b × g, peso w, para cada escolha de estados tratados (linhas de combos, índices em ufs_ok)."""
    W = np.bincount(mu_uf, w, 27)[ufs_ok]; m = (np.bincount(mu_uf, w * y, 27)[ufs_ok]) / W  # a regressão com g por estado é a das médias
    G = np.zeros((len(combos), len(ufs_ok))); G[np.repeat(np.arange(len(combos)), combos.shape[1]), combos.ravel()] = 1
    if not fe_regiao:
        t = (G * W).sum(1); return (G * W * m).sum(1) / t - ((1 - G) * W * m).sum(1) / (W.sum() - t)
    rg = reg_uf[ufs_ok]; Gd = G.copy(); md = m.copy()
    for x in np.unique(rg):
        s = rg == x; Gd[:, s] -= ((G[:, s] * W[s]).sum(1) / W[s].sum())[:, None]; md[s] -= (W[s] * m[s]).sum() / W[s].sum()
    den = (Gd ** 2 * W).sum(1); return np.where(den > 0, (Gd * W * md).sum(1) / np.where(den > 0, den, 1), np.nan)
def e3_perm(y, w, sem_df=False, fe_regiao=False):
    ufs_ok = np.array([i for i, u in enumerate(UFS) if not (sem_df and u == "DF")])
    trat = np.array([j for j, i in enumerate(ufs_ok) if g_obs[i]])
    combos = np.array(list(itertools.combinations(range(len(ufs_ok)), len(trat)))) if sem_df else COMB
    obs = e3_b(y, w, ufs_ok, trat[None, :], fe_regiao)[0]; todas_b = e3_b(y, w, ufs_ok, combos, fe_regiao)
    p = float(np.mean(np.abs(todas_b[np.isfinite(todas_b)]) >= abs(obs) - 1e-12))
    return {"b_pp": r(obs, 4), "p_permutacao": r(p, 5), "permutacoes": int(np.isfinite(todas_b).sum())}
def e3_selvagem(y, w):  # erro agrupado por estado (CR1) e bootstrap selvagem com a nula imposta (Webb, 9.999)
    g = g_obs[mu_uf].astype(float); X = np.column_stack([np.ones(len(y)), g])
    H = np.zeros((27, 2, 2)); np.add.at(H, mu_uf, (w[:, None, None] * X[:, :, None] * X[:, None, :]))
    Hi = np.linalg.inv(H.sum(0)); beta = Hi @ (X * (w * y)[:, None]).sum(0); e = y - X @ beta
    S = np.zeros((27, 2)); np.add.at(S, mu_uf, X * (w * e)[:, None]); Gn = 27
    se = np.sqrt((Hi @ (S.T @ S) @ Hi)[1, 1] * Gn / (Gn - 1)); t_obs = beta[1] / se
    ybar = np.sum(w * y) / w.sum(); u = y - ybar  # nula imposta: b = 0
    S0 = np.zeros((27, 2)); np.add.at(S0, mu_uf, X * w[:, None]); Su = np.zeros((27, 2)); np.add.at(Su, mu_uf, X * (w * u)[:, None])
    rng = sorteador("E3 selvagem " + str(round(float(y.sum()), 3)))
    webb = np.array([-np.sqrt(1.5), -1, -np.sqrt(0.5), np.sqrt(0.5), 1, np.sqrt(1.5)]); v = webb[rng.integers(0, 6, size=(B_SELV, 27))]
    C = S0[None] * ybar + v[:, :, None] * Su[None]  # (B, 27, 2): X'W y* por estado
    bs = C.sum(1) @ Hi.T; Sg = C - np.einsum("gij,bj->bgi", H, bs)
    V_ = np.einsum("ij,bjk,kl->bil", Hi, np.einsum("bgi,bgj->bij", Sg, Sg), Hi)
    t_b = bs[:, 1] / np.sqrt(V_[:, 1, 1] * Gn / (Gn - 1))
    from scipy import stats
    return {"b_pp": r(beta[1], 4), "erro_padrao": r(se, 4), "ic95_cr1": [r(beta[1] - stats.t.ppf(0.975, Gn - 1) * se, 4), r(beta[1] + stats.t.ppf(0.975, Gn - 1) * se, 4)],
            "p_cr1": r(2 * stats.t.sf(abs(t_obs), Gn - 1), 5), "p_selvagem": r(float(np.mean(np.abs(t_b) >= abs(t_obs))), 5)}
E3 = {"estados_2t_governador": GOV2T, "desfechos": {}}
for nome, y in (("var_abstencao_pp", mu_da), ("var_fatia_lula_pp", mu_ds)):
    E3["desfechos"][nome] = {"principal": e3_perm(y, mu_E), "sem_peso": e3_perm(y, np.ones(len(y))),
                             "sem_df": e3_perm(y, mu_E, sem_df=True), "efeito_de_regiao": e3_perm(y, mu_E, fe_regiao=True),
                             "selvagem": e3_selvagem(y, mu_E),
                             "medias_pp": {"com_2t": r(np.sum((mu_E * y)[g_obs[mu_uf]]) / mu_E[g_obs[mu_uf]].sum(), 4),
                                           "sem_2t": r(np.sum((mu_E * y)[~g_obs[mu_uf]]) / mu_E[~g_obs[mu_uf]].sum(), 4)}}
ps = sorted((v["principal"]["p_permutacao"], k) for k, v in E3["desfechos"].items())  # Holm sobre os dois desfechos
for i, (p, k) in enumerate(ps): E3["desfechos"][k]["p_holm"] = r(min(1, max(p * (2 - j) for j, (p, _) in enumerate(ps[: i + 1]))), 5)
for k, d in E3["desfechos"].items():
    sinais = {np.sign(d[c]["b_pp"]) for c in ("principal", "sem_peso", "sem_df", "efeito_de_regiao")}
    d["achado"] = bool(d["p_holm"] < 0.05 and len(sinais) == 1)
    d["tamanho"] = "pequena" if abs(d["principal"]["b_pp"]) < PEQUENA else "não pequena"
with open(os.path.join(DADOS, "inferencia.json"), encoding="utf-8") as fh: INF = json.load(fh)
lista = INF["funil"]["var_abstencao"]["lista_fora998"]
acima = [x for x in lista if "acima" in x["lado"]]
n_mun_2t = sum(1 for l in MU if l["uf"] in GOV2T)
E3["funil_acima_998"] = {"total": len(acima), "nos_6_estados": sum(1 for x in acima if x["uf"] in GOV2T),
                         "esperado_pelo_numero_de_municipios": r(len(acima) * n_mun_2t / len(MU), 2), "municipios_nos_6": n_mun_2t,
                         "por_uf": {u: sum(1 for x in acima if x["uf"] == u) for u in sorted({x["uf"] for x in acima})}}

# ======================= E4 e E5: uma reta por seção, com efeito de município =======================
def reta(y, x, sel, peso=True, fe=True, extra=None):
    """Somas por município de Σw x̃², Σw x̃ ỹ (e de Σw·extra, para a correção da E5), já com o efeito de município tirado."""
    w = E1 if peso else np.ones(len(E1)); ws = np.where(sel, w, 0)
    xt, yt = (tira_media(x, w, sel), tira_media(y, w, sel)) if fe else (x - np.sum(ws * x) / ws.sum(), y - np.sum(ws * y) / ws.sum())
    out = {"Sxx": np.bincount(mi, ws * xt * xt, M), "Sxy": np.bincount(mi, ws * xt * yt, M), "W": np.bincount(mi, ws, M), "xt": xt, "yt": yt, "ws": ws}
    if extra is not None: out["Sex"] = np.bincount(mi, ws * extra, M)
    return out
def ajusta(S, ms, corr=False): return (S["Sxy"][ms].sum() + (S["Sex"][ms].sum() if corr else 0)) / S["Sxx"][ms].sum()
def boot(S, nivel, ms, nome, corr=False, intervalo="estados"):
    cont = contagens(nivel, ms, sorteador(nome), intervalo)
    bb = (cont @ S["Sxy"][ms] + (cont @ S["Sex"][ms] if corr else 0)) / (cont @ S["Sxx"][ms])
    return [float(x) for x in np.percentile(bb, [2.5, 97.5])]
def cr1_estado(S, b):  # erro agrupado por estado (CR1), t com G − 1; o efeito de município fica dentro do grupo
    e = S["yt"] - b * S["xt"]; sg = np.bincount(np.array([ui[u] for u in uf]), S["ws"] * S["xt"] * e, 27)
    se = np.sqrt(27 / 26 * np.sum(sg ** 2)) / S["Sxx"].sum()
    from scipy import stats
    return [r(10 * (b - stats.t.ppf(0.975, 26) * se), 4), r(10 * (b + stats.t.ppf(0.975, 26) * se), 4)]
def iq(S, sel):  # quartis ponderados de x depois de tirar a média de cada município
    q = quantil_pond(S["xt"][sel], S["ws"][sel], [0.25, 0.75]); return q[1] - q[0]
def item_reta(S, nivel, lugar, ms, nome, sel, corr=False, intervalo="estados"):
    b = ajusta(S, ms, corr); lo, hi = boot(S, nivel, ms, nome, corr, intervalo)
    lm = np.zeros(M, bool); lm[ms] = True; s_ = sel & lm[mi]
    return {"nivel": nivel, "lugar": lugar, "n": len(ms), "secoes": int(s_.sum()), "b_por_10": r(10 * b, 4),
            "ic95_por_10": [r(10 * lo, 4), r(10 * hi, 4)], "efeito_interquartil_pp": r(b * iq(S, s_), 4)}

# E4: Δa da seção contra a fatia do Lula no 1º turno
da = 100 * ((E2 - C2) / E2 - (E1 - C1) / E1); s1 = np.where(L1 + F1 > 0, 100 * L1 / np.where(L1 + F1 > 0, L1 + F1, 1), np.nan)
s1_val = 100 * L1 / np.where(L1 + F1 + O1 > 0, L1 + F1 + O1, 1)
sel4 = (L1 > 0) & (F1 > 0)
def e4_lugares(S, nome, sel, com_uf=True, intervalo="estados"):
    out = []
    for nivel, lugar, lm in lugares(com_uf):
        ms = np.flatnonzero(lm & (np.bincount(mi, sel, M) > 0))
        if len(ms) >= MIN_MUN: out.append(item_reta(S, nivel, lugar, ms, f"E4 {nome} {lugar}", sel, intervalo=intervalo))
    return out
x4 = np.nan_to_num(s1)
S4 = reta(da, x4, sel4)
E4 = {"principal": e4_lugares(S4, "principal", sel4)}
MS_BR = lambda sel: np.flatnonzero(np.bincount(mi, sel, M) > 0)
def e4_br(S, nome, sel): return item_reta(S, "brasil", "Brasil", MS_BR(sel), f"E4 {nome} Brasil", sel)
E4["conferencias"] = {"sem_peso": e4_br(reta(da, x4, sel4, peso=False), "sem peso", sel4),
                      "sem_agregadas": e4_br(reta(da, x4, sel4 & SEM_AG), "sem agregadas", sel4 & SEM_AG),
                      "sem_aptos_que_mudam": e4_br(reta(da, x4, sel4 & SEM_APT), "sem aptos que mudam", sel4 & SEM_APT),
                      "fatia_entre_validos": e4_br(reta(da, s1_val, sel4), "fatia entre válidos", sel4)}
E4["conferencias"]["erro_agrupado_por_estado"] = {"b_por_10": E4["principal"][0]["b_por_10"], "ic95_por_10": cr1_estado(S4, ajusta(S4, MS_BR(sel4)))}
E4["contexto_sem_efeito_de_municipio"] = e4_br(reta(da, x4, sel4, fe=False), "sem efeito de município", sel4)
br4 = E4["principal"][0]; lado4 = np.sign(br4["b_por_10"])
E4["achado"] = bool((br4["ic95_por_10"][0] > 0 or br4["ic95_por_10"][1] < 0)
                    and all(np.sign(c["b_por_10"]) == lado4 for c in E4["conferencias"].values())
                    and all((c["ic95_por_10"][0] > 0 or c["ic95_por_10"][1] < 0) for k, c in E4["conferencias"].items()))
E4["tamanho"] = "pequena" if abs(br4["efeito_interquartil_pp"]) < PEQUENA else "não pequena"
linha("E4: seções com votos para os dois no 1º turno: " + f(sel4.sum()), sel4.sum() > 480000)

# E5: Δs da seção contra s1, com a correção do acaso (variância binomial da fatia do 1º turno)
sel5 = (L1 + F1 > 0) & (L2 + F2 > 0)
s1_5 = 100 * L1 / np.where(L1 + F1 > 0, L1 + F1, 1); s2_5 = 100 * L2 / np.where(L2 + F2 > 0, L2 + F2, 1); ds5 = s2_5 - s1_5
vare = s1_5 * (100 - s1_5) / np.where(L1 + F1 > 0, L1 + F1, 1)  # p.p.²
CAPT = INF["h1_referencia"]["captura_brasil_sem_exterior"]
S_tot = dL + dF; ds_ref = 100 * (L1 + CAPT * S_tot) / np.where(L2 + F2 > 0, L2 + F2, 1) - s1_5  # L1 + F1 + S = L2 + F2
def e5(nome, sel, peso=True, corr=True):
    S = reta(ds5, s1_5, sel, peso=peso, extra=vare); ms = MS_BR(sel)
    return item_reta(S, "brasil", "Brasil", ms, f"E5 {nome}", sel, corr=corr)
E5 = {"principal": e5("principal", sel5)}
E5["correcao_por_10"] = r(E5["principal"]["b_por_10"] - e5("bruta", sel5, corr=False)["b_por_10"], 4)
S5b, S5r = reta(ds5, s1_5, sel5), reta(ds_ref, s1_5, sel5); ms5 = MS_BR(sel5)
cont5 = contagens("brasil", ms5, sorteador("E5 referência"), "estados")
bo, br_ = (cont5 @ S5b["Sxy"][ms5]) / (cont5 @ S5b["Sxx"][ms5]), (cont5 @ S5r["Sxy"][ms5]) / (cont5 @ S5r["Sxx"][ms5])
E5["conferencias"] = {"bruta": e5("bruta", sel5, corr=False),
                      "divisao_igual": {"esperada_por_10": r(10 * ajusta(S5r, ms5), 4), "observada_bruta_por_10": r(10 * ajusta(S5b, ms5), 4),
                                        "diferenca_por_10": r(10 * (ajusta(S5b, ms5) - ajusta(S5r, ms5)), 4),
                                        "diferenca_ic95_por_10": [r(10 * x, 4) for x in np.percentile(bo - br_, [2.5, 97.5])],
                                        "captura": CAPT},
                      "pelo_menos_200_votos": e5("200 votos", sel5 & (L1 + F1 >= 200)),
                      "sem_peso": e5("sem peso", sel5, peso=False),
                      "sem_agregadas": e5("sem agregadas", sel5 & SEM_AG)}
b5 = E5["principal"]; lado5 = np.sign(b5["b_por_10"])
conf5 = [E5["conferencias"][k]["b_por_10"] for k in ("pelo_menos_200_votos", "sem_peso", "sem_agregadas")]
E5["achado"] = bool((b5["ic95_por_10"][0] > 0 or b5["ic95_por_10"][1] < 0) and all(np.sign(x) == lado5 for x in conf5)
                    and np.sign(E5["conferencias"]["divisao_igual"]["diferenca_por_10"]) != 0)
E5["h1_municipios_por_10"] = r(10 * next(v["coef"] for v in INF["hipoteses"]["H1"]["versoes"] if v["versao"] == "H1 principal"), 4)
# limite: a correção usa a variância binomial como se o acaso de cada turno fosse independente; a parte dela que zera a inclinação
E5["fracao_da_correcao_que_zera"] = r(-E5["conferencias"]["bruta"]["b_por_10"] / (E5["principal"]["b_por_10"] - E5["conferencias"]["bruta"]["b_por_10"]), 3)
E5["secoes"] = int(sel5.sum())

with open(SAI, "w", encoding="utf-8") as fh:
    json.dump({"meta": {"gerado": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"), "script": "scripts/exploracao.py",
                        "registro": "docs/analise/HIPOTESES.md, seção 8, \"Rodada 1\" (27/10/2026, 10:40)",
                        "rotulo": "exploratório, não registrado antes das contas", "semente": SEMENTE, "bootstrap": B_BOOT,
                        "secoes": int(len(E1)), "municipios": M},
               "E1": {"por_lugar": E1_PRINC, "conferencias": E1_CONF, "achado_brasil": E1_ACHADO, "lados_opostos": E1_OPOSTOS,
                      "votos_brasil": {"70": int(V["V70"].sum()), "14": int(V["V14"].sum()), "55": int(V["V55"].sum()), "resto": int(V["Vresto"].sum()),
                                       "C": int(dC.sum()), "R": int(R.sum())}},
               "E2": RES_E2, "E3": E3, "E4": E4, "E5": E5}, fh, ensure_ascii=False, indent=1)

# ---------- relatório ----------
print("\n### E1 · parte do Lula, em saldo, de cada fonte (intervalo de 95%; conferências que mantêm a leitura, de 4)\n")
print("| Lugar | " + " | ".join(r_ for _, r_ in FONTES_E1) + " |\n|---|" + "---|" * len(FONTES_E1))
for l in E1_PRINC:
    cel = lambda d: f"{p1(d['lula'])} ({p1(d['lula_ic95'][0])}–{p1(d['lula_ic95'][1])}) {leitura(d)} [{len(d['conferencias_mantem'])}]"
    print(f"| {l['lugar']} | " + " | ".join(cel(l["fontes"][c]) for c, _ in FONTES_E1) + " |")
print(f"\nAchado no Brasil (mantido nas 4 conferências): {E1_ACHADO or 'nenhum'}; lados opostos: {E1_OPOSTOS}")
print("\n### E2 · municípios do Brasil (5.571)\n")
for k, v in RES_E2["brasil"]["casas"].items(): print(f"- {k}: {f(v['n'])} municípios ({f(v['eleitores_1t'])} eleitores do 1º turno)")
for k, v in RES_E2["brasil"]["fatia_lula"].items(): print(f"- fatia do Lula {k}: {f(v['n'])} municípios")
print(f"- conferência (a), vencedor do 1º turno entre todos: {RES_E2['conf_vencedor_entre_todos']}")
print(f"- conferência (b), seções: " + "; ".join(f"{k} {f(v['n'])}" for k, v in RES_E2["conf_secoes"]["casas"].items()))
print(f"- conferência (c), com o exterior: " + "; ".join(f"{k} {f(v['n'])}" for k, v in RES_E2["com_exterior"]["casas"].items()))
print("- trocas por estado (Flávio → Lula / Lula → Flávio): " + "; ".join(
    f"{u} {v['casas'].get('Flávio → Lula', {'n': 0})['n']}/{v['casas'].get('Lula → Flávio', {'n': 0})['n']}" for u, v in RES_E2["por_uf"].items()))
print("\n### E3 · estados com 2º turno para governador (" + ", ".join(GOV2T) + ")\n")
for k, d in E3["desfechos"].items():
    print(f"- {k}: médias {num(d['medias_pp']['com_2t'], 2)} (com) × {num(d['medias_pp']['sem_2t'], 2)} (sem); b = {num(d['principal']['b_pp'], 2)} p.p., "
          f"p da permutação {num(d['principal']['p_permutacao'], 4)} (Holm {num(d['p_holm'], 4)}); sem peso {num(d['sem_peso']['b_pp'], 2)} "
          f"(p {num(d['sem_peso']['p_permutacao'], 4)}); sem DF {num(d['sem_df']['b_pp'], 2)} (p {num(d['sem_df']['p_permutacao'], 4)}); "
          f"região {num(d['efeito_de_regiao']['b_pp'], 2)} (p {num(d['efeito_de_regiao']['p_permutacao'], 4)}); "
          f"selvagem p {num(d['selvagem']['p_selvagem'], 4)}, CR1 p {num(d['selvagem']['p_cr1'], 4)}; achado: {d['achado']} ({d['tamanho']})")
fa = E3["funil_acima_998"]
print(f"- funil da abstenção, acima da faixa de 99,8%: {fa['total']}, dos quais {fa['nos_6_estados']} nos 6 estados (esperado pelo número de municípios: {num(fa['esperado_pelo_numero_de_municipios'])})")
print("\n### E4 · variação da abstenção (p.p.) a cada 10 pontos a mais do Lula no 1º turno, seções da mesma cidade\n")
for x in E4["principal"]:
    if x["nivel"] != "uf": print(f"- {x['lugar']}: {num(x['b_por_10'], 2)} ({num(x['ic95_por_10'][0], 2)} a {num(x['ic95_por_10'][1], 2)}); interquartil {num(x['efeito_interquartil_pp'], 2)} p.p.")
ufs4 = [x for x in E4["principal"] if x["nivel"] == "uf"]
print(f"- estados: {sum(x['ic95_por_10'][1] < 0 for x in ufs4)} com o intervalo abaixo de zero, {sum(x['ic95_por_10'][0] > 0 for x in ufs4)} acima, {sum(x['ic95_por_10'][0] <= 0 <= x['ic95_por_10'][1] for x in ufs4)} com zero (de {len(ufs4)})")
for k, c in E4["conferencias"].items(): print(f"- {k}: {num(c['b_por_10'], 2)} ({num(c['ic95_por_10'][0], 2)} a {num(c['ic95_por_10'][1], 2)})")
c = E4["contexto_sem_efeito_de_municipio"]; print(f"- contexto, sem efeito de município: {num(c['b_por_10'], 2)} ({num(c['ic95_por_10'][0], 2)} a {num(c['ic95_por_10'][1], 2)})")
print(f"- achado: {E4['achado']} ({E4['tamanho']})")
print("\n### E5 · variação da fatia (p.p.) a cada 10 pontos a mais no 1º turno, seções da mesma cidade\n")
print(f"- principal, corrigida: {num(b5['b_por_10'], 3)} ({num(b5['ic95_por_10'][0], 3)} a {num(b5['ic95_por_10'][1], 3)}); correção {num(E5['correcao_por_10'], 3)}")
for k, c in E5["conferencias"].items():
    if k == "divisao_igual": print(f"- divisão igual: esperada {num(c['esperada_por_10'], 3)}, observada (bruta) {num(c['observada_bruta_por_10'], 3)}, diferença {num(c['diferenca_por_10'], 3)} ({num(c['diferenca_ic95_por_10'][0], 3)} a {num(c['diferenca_ic95_por_10'][1], 3)})")
    else: print(f"- {k}: {num(c['b_por_10'], 3)} ({num(c['ic95_por_10'][0], 3)} a {num(c['ic95_por_10'][1], 3)})")
print(f"- H1 por município: {E5['h1_municipios_por_10']}; achado: {E5['achado']}")
print(f"\nGravado em `dados/exploracao.json`. Conferências: {'todas OK' if ok else 'COM ERRO'}")
sys.exit(0 if ok else 1)
