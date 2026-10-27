# T06: regressões, intervalos, funil e erro da projeção, pelas regras do docs/analise/HIPOTESES.md (aprovado em 26/10/2026, 12:43).
# Lê em ../dados: analise_municipios.csv (T03), esquerda_1t_municipios.csv (T05) e historico_2t.csv; grava inferencia.json.
# Uso: python -I scripts/inferencia.py  (imprime o relatório em Markdown; sai com 1 se alguma conferência falhar)
# Só numpy e scipy: mínimos quadrados ponderados, erro agrupado por UF (CR1), bootstrap selvagem por grupo (Webb) e bootstrap por municípios.
# T32 (correções do parecer estatístico de 26/10/2026; notas datadas em "Mudanças depois da aprovação" do HIPOTESES.md): intervalo do
# bootstrap selvagem por inversão do teste, número efetivo de grupos e um estado de fora por vez (M5); referência da divisão igual na H1
# (M4); estados inteiros no intervalo da ecológica do Brasil e das regiões (M2); matriz de transição (M1); "fora de 0% a 100%" antes da
# precisão, com aviso em todas as fontes do lugar (m1); limites de Duncan e Davis (m3); funil sem winsorizar, conferido por porte (M3).
# T35: a estimativa por lugar (4.2) vem da conta por seção (dados/secoes_inferencia.json, P28); a por município fica como conferência.
# T34: os 35 testes dos dados sociais (seção 6 do HIPOTESES.md), com dados/dados_sociais_municipios.json (T26) e Holm.
import csv, json, os, sys, zlib, datetime
import numpy as np
from scipy import stats
sys.stdout.reconfigure(encoding="utf-8")  # o relatório tem acentos e "−", que o terminal do Windows não codifica (diário, D03)
AQUI = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(AQUI, "..", "dados")
ENT_MU, ENT_ESQ, ENT_HIST = (os.path.join(DADOS, n) for n in ("analise_municipios.csv", "esquerda_1t_municipios.csv", "historico_2t.csv"))
ENT_SEC_INF = os.path.join(DADOS, "secoes_inferencia.json")  # T35: a conta por seção, principal da 4.2 desde a P28
ENT_SOC = os.path.join(DADOS, "dados_sociais_municipios.json")  # T26; os 35 testes da seção 6 (T34)
SAI = os.path.join(DADOS, "inferencia.json")

# regras fixadas no HIPOTESES.md (seções 2 e 4)
SEMENTE = 20261026
B_SELVAGEM, B_BOOT = 9999, 1000
WEBB = np.array([-np.sqrt(1.5), -1, -np.sqrt(0.5), np.sqrt(0.5), 1, np.sqrt(1.5)])
LIMIAR_PEQUENA = 0.5          # p.p.: efeito interquartil abaixo disso é "pequeno" (2.6)
MIN_MUN, MEIA_LARGURA = 30, 0.10  # critério de precisão por lugar (4.2)
SENADO_MIN_ESQ = 5.0          # senador: fora os estados com campo da esquerda abaixo de 5% (H5)
SJ_MAX = 0.05                 # conferência: sem municípios com sub judice acima de 5% de (válidos + sub judice) (5.4)
Z95, Z998 = stats.norm.ppf(0.975), stats.norm.ppf(0.999)
S2_FINAL = 64256232 / (64256232 + 59826041) * 100  # 51,785%, resultado final do 2º turno (especificação, seção 2)

ok = True
def linha(texto, certo):
    global ok
    ok &= bool(certo); print(f"- {'OK' if certo else 'ERRO'}: {texto}")
def f(x): return f"{int(round(x)):,}".replace(",", ".")
def n_(v, casas=2, sinal=False):
    if v is None or not np.isfinite(v): return "—"
    s = f"{abs(v):.{casas}f}".replace(".", ",")
    if float(f"{abs(v):.{casas}f}") == 0: return s
    return ("+" if sinal and v > 0 else "−" if v < 0 else "") + s
def r(v, casas=6): return None if v is None or not np.isfinite(v) else round(float(v), casas)
def sorteador(nome): return np.random.default_rng([SEMENTE, zlib.crc32(nome.encode())])  # mesma semente por teste, em qualquer ordem

# ---------- dados ----------
with open(ENT_MU, encoding="utf-8") as fh: mu = [l for l in csv.DictReader(fh) if l["uf"] != "ZZ"]  # exterior fora (2.1)
def col(k, tipo=float): return np.array([tipo(l[k]) for l in mu])
cd, uf, reg, nome = (np.array([l[k] for l in mu]) for k in ("cd_tse", "uf", "regiao", "municipio"))
porte = np.array([int(l["porte"]) for l in mu])
E1, E2, C1, C2, vv1 = (col(k) for k in ("eleitorado_1t", "eleitorado_2t", "comparecimento_1t", "comparecimento_2t", "validos_1t"))
L1, F1, L2, F2, O1 = (col(k) for k in ("lula_1t", "flavio_1t", "lula_2t", "flavio_2t", "outros_1t"))
BN1, BN2 = col("brancos_nulos_1t"), col("brancos_nulos_2t")
dL, dF, dC, R = L2 - L1, F2 - F1, C2 - C1, BN1 - BN2  # R = −ΔBN, a queda de brancos e nulos (4.1)
s1, s2 = 100 * L1 / (L1 + F1), 100 * L2 / (L2 + F2)
ds = s2 - s1
o = 100 * O1 / vv1
a1, a2 = 100 * (E1 - C1) / E1, 100 * (E2 - C2) / E2
da = a2 - a1
Lvv, Fvv = 100 * L1 / vv1, 100 * F1 / vv1  # fatias sobre os válidos do 1º turno (P14)
gL, gF = 100 * dL / E1, 100 * dF / E1      # votos ganhos por eleitor do 1º turno
N = len(mu)
ind = {c: i for i, c in enumerate(cd)}

print("### Conferência das entradas\n")
linha(f"municípios do Brasil em `analise_municipios.csv`: {f(N)} (o exterior fica fora das contas do T06)", N == 5571)
linha("identidade do saldo ΔL + ΔF = O1 + ΔC + R em todos: maior diferença em módulo "
      f"{f(np.abs(dL + dF - (O1 + dC + R)).max())}", np.all(dL + dF == O1 + dC + R) and all(l["residuo_identidade"] == "0" for l in mu))
dif = max(np.abs(s1 - col("fatia_lula_1t_pct")).max(), np.abs(s2 - col("fatia_lula_2t_pct")).max(),
          np.abs(ds - col("var_fatia_pp")).max(), np.abs(da - col("var_taxa_abst_pp")).max())
linha(f"fatias, Δs e Δa refeitos das contagens iguais aos do T03 (maior diferença {dif:.6f} ponto, arredondamento do CSV)", dif < 1e-4)
linha(f"27 UFs e 5 regiões: {len(set(uf))} UFs, {len(set(reg))} regiões", len(set(uf)) == 27 and len(set(reg)) == 5)

with open(ENT_ESQ, encoding="utf-8") as fh: esq_linhas = list(csv.DictReader(fh))
CARGOS = [("federal", "Deputado federal", ("6",)), ("estadual", "Deputado estadual (distrital no DF)", ("7", "8")), ("senador", "Senador", ("5",))]
CAMPOS = ["vv", "esq", "pct_esq", "sem_posicao", "pct_sem_posicao", "escala", "lula_1t", "fatia_lula_1t", "vantagem", "sj", "pct_esq_com_sj",
          "conf_2018_pct_esq"]
ESQ, ESQ_UF = {}, {}
for chave, _, codigos in CARGOS:
    m = {k: np.full(N, np.nan) for k in CAMPOS}
    vistos = 0
    for l in esq_linhas:
        if l["cargo"] not in codigos: continue
        if l["nivel"] == "uf": ESQ_UF.setdefault(chave, {})[l["uf"].upper()] = float(l["pct_esq"])
        if l["nivel"] != "mu": continue
        i = ind[l["cd"].zfill(5)]
        vistos += 1
        for k in CAMPOS: m[k][i] = float(l[k]) if l[k] != "" else np.nan
    ESQ[chave] = m
    linha(f"{chave}: {f(vistos)} municípios do T05 casados com o T03 pelo código do TSE", vistos == N and np.isfinite(m["pct_esq"]).all())
    linha(f"{chave}: votos do Lula no 1º turno iguais nos dois arquivos", np.array_equal(m["lula_1t"], L1))
    linha(f"{chave}: fatia do Lula e vantagem do T05 iguais às refeitas (maior diferença "
          f"{max(np.abs(m['fatia_lula_1t'] - s1).max(), np.abs(m['vantagem'] - (m['pct_esq'] - s1)).max()):.6f})",
          np.abs(m["fatia_lula_1t"] - s1).max() < 1e-3 and np.abs(m["vantagem"] - (m["pct_esq"] - s1)).max() < 1e-3)

# ---------- regressão ponderada com erro agrupado ----------
def grupos(g):
    _, gi = np.unique(g, return_inverse=True); return gi, gi.max() + 1
def tira_media(v, g, w):  # tira a média ponderada de cada UF (efeito fixo, pelo teorema de Frisch-Waugh-Lovell)
    gi, G = grupos(g); v2 = v.reshape(len(v), -1); sw = np.bincount(gi, w, G)
    m = np.stack([np.bincount(gi, w * v2[:, j], G) for j in range(v2.shape[1])], 1) / sw[:, None]
    return (v2 - m[gi]).reshape(v.shape)
def prepara(y, xs, w, g, fe):
    X = np.column_stack(xs); bom = np.isfinite(y) & np.isfinite(X).all(1)
    y, X, w, g = y[bom], X[bom], w[bom], g[bom]
    if fe:  # UF com um município só (o DF) não tem comparação dentro do estado e sai, como no reghdfe
        gi, G = grupos(g); manter = np.bincount(gi, minlength=G)[gi] > 1
        y, X, w, g = y[manter], X[manter], w[manter], g[manter]
        return tira_media(y, g, w), tira_media(X, g, w), w, g
    return y, np.column_stack([np.ones(len(y)), X]), w, g
def mqp(y, X, w, gi, G):  # mínimos quadrados ponderados e variância agrupada CR1 (efeito fixo aninhado na UF não conta em k)
    n, k = X.shape
    Bi = np.linalg.inv(X.T @ (X * w[:, None]))
    b = Bi @ (X.T @ (w * y)); u = y - X @ b
    S = np.zeros((G, k)); np.add.at(S, gi, X * (w * u)[:, None])
    c = G / (G - 1) * (n - 1) / (n - k)
    return b, c * Bi @ S.T @ S @ Bi, u, Bi, c
def selvagem(y, X, w, gi, G, Bi, c, j, t_obs, rng):
    # bootstrap selvagem por grupo com a hipótese nula imposta (β_j = 0), pesos de Webb; devolve o valor-p bilateral
    Xr = np.delete(X, j, 1)
    br = np.linalg.solve(Xr.T @ (Xr * w[:, None]), Xr.T @ (w * y)); ur = y - Xr @ br
    Sr = np.zeros((G, X.shape[1])); np.add.at(Sr, gi, X * (w * ur)[:, None])
    C = Bi @ Sr.T                       # efeito de cada grupo nos coeficientes
    a = Bi[:, j]
    Ha = np.zeros((G, X.shape[1])); np.add.at(Ha, gi, X * (w * (X @ a))[:, None])
    p, Q = Sr @ a, Ha @ C
    v = WEBB[rng.integers(0, 6, size=(B_SELVAGEM, G))]
    bj = v @ C[j]
    T = v * p[None, :] - v @ Q.T        # a' × (escore de cada grupo) em cada repetição
    t = bj / np.sqrt(c * (T ** 2).sum(1))
    return float(np.mean(np.abs(t) >= abs(t_obs)))
def inverte(y, X, w, gi, G, Bi, c, j, b, ep, nome):
    # intervalo de 95% do próprio bootstrap selvagem (M5): os valores b0 de β_j que o teste com a nula β_j = b0 não rejeita a 5%.
    # Mesmos sorteios em todo b0 (mesma semente); bissecção em cada lado até 1/2^18 do passo inicial.
    def p(b0): return selvagem(y - b0 * X[:, j], X, w, gi, G, Bi, c, j, (b - b0) / ep, sorteador(nome))
    lims = []
    for lado in (-1, 1):
        a, z = b, b + lado * 4 * ep
        while p(z) >= 0.05: a, z = z, z + lado * 4 * ep
        for _ in range(18):
            m_ = (a + z) / 2
            if p(m_) >= 0.05: a = m_
            else: z = m_
        lims.append((a + z) / 2)
    return lims
def quantis(x, w, qs):
    o_ = np.argsort(x); x, w = x[o_], w[o_]; cw = (np.cumsum(w) - 0.5 * w) / w.sum()
    return np.interp(qs, cw, x)
def classifica(ic, p, sinal):
    lado = 1 if ic[0] > 0 else -1 if ic[1] < 0 else 0
    if lado == 0 or p >= 0.05: return "inconclusiva"
    return "confirmada" if lado == sinal else "contrária"
def regressao(nome, y, xs, nomes, w, fe, sinal=None, g=uf, testar=True, inverter=True):
    yy, X, ww, gg = prepara(y, xs, w, g, fe)
    gi, G = grupos(gg)
    b, V, u, Bi, c = mqp(yy, X, ww, gi, G)
    j = 0 if fe else 1
    ep = np.sqrt(V[j, j]); gl = G - 1; tc = stats.t.ppf(0.975, gl)
    ic = (b[j] - tc * ep, b[j] + tc * ep)
    ym = np.sum(ww * yy) / ww.sum()
    q = quantis(X[:, j], ww, [0.25, 0.75])
    p = selvagem(yy, X, ww, gi, G, Bi, c, j, b[j] / ep, sorteador(nome)) if testar else None
    ics = inverte(yy, X, ww, gi, G, Bi, c, j, b[j], ep, nome) if testar and inverter else None
    res = {"versao": nome, "efeito_fixo_uf": fe, "peso": "eleitorado do 1º turno" if np.ptp(w) > 0 else "nenhum",
           "variavel": nomes[0], "controles": nomes[1:], "n": int(len(yy)), "grupos": int(G),
           "coef": r(b[j]), "erro_padrao": r(ep), "ic95": [r(ic[0]), r(ic[1])], "gl": int(gl),
           "ic95_selvagem": None if ics is None else [r(ics[0]), r(ics[1])],
           "p_cr1": r(2 * stats.t.sf(abs(b[j] / ep), gl), 6), "p_selvagem": r(p, 4),
           "r2": r(1 - np.sum(ww * u ** 2) / np.sum(ww * (yy - ym) ** 2), 4), "r2_tipo": "dentro dos estados" if fe else "comum",
           "quartis_x": [r(q[0], 4), r(q[1], 4)], "efeito_interquartil_pp": r(b[j] * (q[1] - q[0]), 4),
           "controles_coef": {nm: r(b[k + (0 if fe else 1)]) for k, nm in enumerate(nomes) if k > 0}}
    if sinal is not None:
        res["previsto"] = "positivo" if sinal > 0 else "negativo"
        res["classificacao"] = classifica(ic, p, sinal)
        res["pequena"] = bool(abs(res["efeito_interquartil_pp"]) < LIMIAR_PEQUENA)
    return res

um = np.ones(N)
def hipotese(cod, y, x, nx, sinal, conj):  # H1, H3, H4: principal dentro dos estados, versão Brasil, sem peso e modelo conjunto
    vs = [regressao(f"{cod} principal", y, [x], [nx], E1, True, sinal),
          regressao(f"{cod} Brasil", y, [x], [nx], E1, False, sinal),
          regressao(f"{cod} sem peso, dentro dos estados", y, [x], [nx], um, True, sinal),
          regressao(f"{cod} sem peso, Brasil", y, [x], [nx], um, False, sinal),
          regressao(f"{cod} conjunto, dentro dos estados", y, [x] + conj[0], [nx] + conj[1], E1, True, sinal),
          regressao(f"{cod} conjunto, Brasil", y, [x] + conj[0], [nx] + conj[1], E1, False, sinal)]
    return vs
H = {}
H["H1"] = hipotese("H1", ds, s1, "s1", -1, ([o, da], ["o", "Δa"]))
H["H3"] = hipotese("H3", ds, o, "o", +1, ([s1, da], ["s1", "Δa"]))
H["H4"] = hipotese("H4", ds, da, "Δa", -1, ([s1, o], ["s1", "o"]))
COMPL = {"H1": [regressao("H1 complemento Lula", gL, [s1], ["s1"], E1, True),
                regressao("H1 complemento Lula, Brasil", gL, [s1], ["s1"], E1, False),
                regressao("H1 complemento Flávio", gF, [100 - s1], ["fatia do Flávio no 1º turno"], E1, True),
                regressao("H1 complemento Flávio, Brasil", gF, [100 - s1], ["fatia do Flávio no 1º turno"], E1, False)],
         "H4": [regressao("H4 complemento Lula", gL, [da], ["Δa"], E1, True),
                regressao("H4 complemento Lula, Brasil", gL, [da], ["Δa"], E1, False),
                regressao("H4 complemento Flávio", gF, [da], ["Δa"], E1, True),
                regressao("H4 complemento Flávio, Brasil", gF, [da], ["Δa"], E1, False)]}

# ---------- H1 contra a divisão igual (M4; exploratória, depois do resultado) ----------
# Se o saldo S = ΔL + ΔF se dividisse em todo município na proporção do Brasil (captura sem o exterior), a fatia do 2º turno seria
# (L1 + a × S) ÷ (L1 + F1 + S). A mesma regressão da H1 nesse Δs do modelo dá a inclinação esperada sem mudança de comportamento.
S_ = dL + dF
CAPT_BR = dL.sum() / S_.sum()
ds_mod = 100 * (L1 + CAPT_BR * S_) / (L1 + F1 + S_) - s1
H1_REF = {"captura_brasil_sem_exterior": r(CAPT_BR, 6),
          "esperada": regressao("H1 divisão igual", ds_mod, [s1], ["s1"], E1, True, testar=False),
          "esperada_brasil": regressao("H1 divisão igual, Brasil", ds_mod, [s1], ["s1"], E1, False, testar=False),
          "diferenca": regressao("H1 observada menos divisão igual", ds - ds_mod, [s1], ["s1"], E1, True),
          "diferenca_brasil": regressao("H1 observada menos divisão igual, Brasil", ds - ds_mod, [s1], ["s1"], E1, False)}
linha(f"H1, divisão igual: inclinação esperada {n_(10 * H1_REF['esperada']['coef'], 2, True)} por 10, observada "
      f"{n_(10 * H['H1'][0]['coef'], 2, True)}; a diferença é a da regressão de Δs − Δs do modelo",
      abs(H["H1"][0]["coef"] - H1_REF["esperada"]["coef"] - H1_REF["diferenca"]["coef"]) < 1e-9)

# ---------- poucos grupos (M5): peso de cada estado, número efetivo de grupos e um estado de fora por vez ----------
PESO_UF = {u: r(E1[uf == u].sum() / E1.sum(), 4) for u in sorted(set(uf), key=lambda u: -E1[uf == u].sum())}
def g_efetivo(x):  # Carter, Schnepel e Steigerwald (2017), versão principal, Ω_g = D½((1 − ρ)I + ρ11')D½
    yy, X, ww, gg = prepara(x, [x], E1, uf, True); gi, G = grupos(gg); Bi_ = 1 / (X[:, 0] @ (ww * X[:, 0]))
    out = []
    for var_nome, dv in (("variância igual", np.ones(len(ww))), ("variância ∝ 1/eleitorado", 1 / ww)):
        for rho in (0.0, 0.5, 1.0):
            gam = np.zeros(G)
            for k in range(G):
                m_ = gi == k; z_ = Bi_ * ww[m_] * X[m_, 0] * np.sqrt(dv[m_])
                gam[k] = (1 - rho) * np.sum(z_ ** 2) + rho * np.sum(z_) ** 2
            out.append({"variancia": var_nome, "rho": rho, "g_efetivo": r(G / (1 + np.mean((gam - gam.mean()) ** 2) / gam.mean() ** 2), 2)})
    return out
POUCOS = {"peso_uf": PESO_UF, "g_efetivo": {}, "sem_um_estado": {}}
for cod, x, sinal in (("H1", s1, -1), ("H3", o, +1), ("H4", da, -1)):
    POUCOS["g_efetivo"][cod] = g_efetivo(x)
    pr = H[cod][0]; vs_ = []
    for u in sorted(set(uf) - {"DF"}):
        v_ = regressao(f"{cod} sem {u}", np.where(uf != u, ds, np.nan), [x], [pr["variavel"]], E1, True, sinal, inverter=False)
        vs_.append({"uf": u, "coef": v_["coef"], "ic95": v_["ic95"], "p_selvagem": v_["p_selvagem"], "classificacao": v_["classificacao"]})
    cs = np.array([v_["coef"] for v_ in vs_])
    POUCOS["sem_um_estado"][cod] = {"coef_min": r(cs.min()), "coef_max": r(cs.max()),
                                     "mudam_classificacao": [v_["uf"] for v_ in vs_ if v_["classificacao"] != pr["classificacao"]], "estados": vs_}

# ---------- H5: voto dividido, por cargo ----------
H5, H5_FORA = {}, {}
for chave, rotulo, _ in CARGOS:
    m = ESQ[chave]
    sel = np.ones(N, bool)
    if chave == "senador":
        fora = sorted(u for u, p in ESQ_UF["senador"].items() if p < SENADO_MIN_ESQ)
        H5_FORA[chave] = {u: r(ESQ_UF["senador"][u], 4) for u in fora}
        sel = ~np.isin(uf, fora)
    def so(v): return np.where(sel, v, np.nan)
    pe = m["pct_esq"]
    V_b, V_a = pe - Lvv, pe - s1
    V_B = 100 * m["esq"] / (m["vv"] - m["sem_posicao"]) - Lvv               # Missão pela regra B (N11)
    V_sj = m["pct_esq_com_sj"] - Lvv
    pesado_sj = m["sj"] / (m["vv"] + m["sj"]) > SJ_MAX
    V_18 = m["conf_2018_pct_esq"] - Lvv
    V_F = (100 - pe - m["pct_sem_posicao"]) - Fvv                           # espelho: campo da direita − fatia do Flávio sobre os válidos
    y, yf = so(ds), so(-ds)
    nx = "vantagem potencial (fatia sobre os válidos)"
    vs = [regressao(f"H5 {chave} principal", y, [V_b, Lvv], [nx, "fatia do Lula sobre os válidos"], E1, True, +1),
          regressao(f"H5 {chave} Brasil", y, [V_b, Lvv], [nx, "fatia do Lula sobre os válidos"], E1, False, +1),
          regressao(f"H5 {chave} sem peso", y, [V_b, Lvv], [nx, "fatia do Lula sobre os válidos"], um, True, +1),
          regressao(f"H5 {chave} escala contínua", y, [m["escala"], Lvv], ["escala contínua", "fatia do Lula sobre os válidos"], E1, True, -1),
          regressao(f"H5 {chave} fatia entre os dois", y, [V_a, s1], ["vantagem potencial (fatia entre os dois)", "s1"], E1, True, +1),
          regressao(f"H5 {chave} Missão pela regra B", y, [V_B, Lvv], [nx + ", regra B", "fatia do Lula sobre os válidos"], E1, True, +1),
          regressao(f"H5 {chave} com sub judice", y, [V_sj, Lvv], [nx + ", com sub judice", "fatia do Lula sobre os válidos"], E1, True, +1),
          regressao(f"H5 {chave} sem sub judice acima de 5%", np.where(pesado_sj, np.nan, y), [V_b, Lvv],
                    [nx, "fatia do Lula sobre os válidos"], E1, True, +1),
          regressao(f"H5 {chave} com os outros no controle", y, [V_b, Lvv, o], [nx, "fatia do Lula sobre os válidos", "o"], E1, True, +1),
          regressao(f"H5 {chave} rodada de 2018", y, [V_18, Lvv], [nx + ", escala de 2018", "fatia do Lula sobre os válidos"], E1, True, +1),
          regressao(f"H5 {chave} espelho Flávio", yf, [V_F, Fvv], ["vantagem potencial do Flávio", "fatia do Flávio sobre os válidos"],
                    E1, True, +1)]
    vs[7]["municipios_fora_sub_judice"] = int(np.sum(pesado_sj & sel))
    H5[chave] = {"cargo": rotulo, "versoes": vs}

# ---------- dados sociais (seção 6; T34): 7 variáveis × 5 desfechos, Holm nos 35 de dentro dos estados ----------
# Regras de operação na nota de 26/10/2026, 23:56, do HIPOTESES.md, escritas antes de rodar.
SOC_VARS = ["pct_60mais", "alfab_15mais", "pct_renda_ate_meio_sm", "ln_pib_pc", "ln_densidade", "pct_evangelicos", "pct_pretos_pardos"]
with open(ENT_SOC, encoding="utf-8") as fh: soc_json = json.load(fh)
SOC = {k: np.array([np.nan if soc_json["municipios"][c][k] is None else soc_json["municipios"][c][k] for c in cd], float) for k in SOC_VARS}
com_soc = np.isfinite(np.column_stack(list(SOC.values()))).all(1)
linha(f"dados sociais: {f(com_soc.sum())} de {f(N)} municípios com as 7 variáveis; sem dados: "
      + ", ".join(f"{nome[i]} ({uf[i]})" for i in np.flatnonzero(~com_soc)), com_soc.sum() == 5570 and list(cd[~com_soc]) == ["73709"])
cap_mun = np.where((E1 > 10000) & (S_ > 0), 100 * dL / np.where(S_ > 0, S_, 1), np.nan)  # captura só onde vale (N09; seção 6)
SOC_DESF = [("ds", "Δs", ds), ("gL", "ΔL ÷ E1", gL), ("gF", "ΔF ÷ E1", gF), ("cap", "captura", cap_mun), ("da", "Δa", da)]
def holm(ps):
    ps = np.asarray(ps, float); o_ = np.argsort(ps); m_ = len(ps); adj = np.empty(m_); run = 0.0
    for k, i in enumerate(o_): run = max(run, min(1.0, (m_ - k) * ps[i])); adj[i] = run
    return adj
SOCIAIS = {"variaveis": {k: soc_json["meta"]["variaveis"].get(k, soc_json["meta"]["variaveis"].get(k[3:], {})) for k in SOC_VARS},
           "desfechos": {c: rot for c, rot, _ in SOC_DESF}, "municipios_com_dados": int(com_soc.sum()),
           "captura_amostra": int(np.sum(np.isfinite(cap_mun) & com_soc)), "testes": []}
for v_ in SOC_VARS:
    x_ = np.where(com_soc, SOC[v_], np.nan)
    for c, rot, y_ in SOC_DESF:
        SOCIAIS["testes"].append({"variavel": v_, "desfecho": c,
                                  "principal": regressao(f"S {v_} {c} principal", y_, [x_], [v_], E1, True),
                                  "brasil": regressao(f"S {v_} {c} Brasil", y_, [x_], [v_], E1, False)})
for ver in ("principal", "brasil"):
    ts_ = SOCIAIS["testes"]
    hs, hc = holm([t[ver]["p_selvagem"] for t in ts_]), holm([t[ver]["p_cr1"] for t in ts_])
    for t, a_, b_ in zip(ts_, hs, hc):
        t[ver]["p_holm"], t[ver]["p_cr1_holm"] = r(a_, 4), r(b_, 6)
        t[ver]["associacao"] = bool(a_ < 0.05 and b_ < 0.05)
        t[ver]["direcao"] = None if not t[ver]["associacao"] else ("positiva" if t[ver]["coef"] > 0 else "negativa")
        t[ver]["pequena"] = bool(abs(t[ver]["efeito_interquartil_pp"]) < LIMIAR_PEQUENA)
SOCIAIS["com_associacao"] = sum(t["principal"]["associacao"] for t in SOCIAIS["testes"])
linha(f"dados sociais: {len(SOCIAIS['testes'])} testes (7 × 5); com associação depois de Holm, dentro dos estados: {SOCIAIS['com_associacao']}",
      len(SOCIAIS["testes"]) == 35)
linha("dados sociais: municípios na versão dentro dos estados = 5.569 (sem o DF) em Δs, ΔL ÷ E1, ΔF ÷ E1 e Δa",
      all(t["principal"]["n"] == 5569 for t in SOCIAIS["testes"] if t["desfecho"] != "cap"))
linha(f"dados sociais: captura com {f(SOCIAIS['captura_amostra'])} municípios (mais de 10 mil eleitores e ΔL + ΔF > 0)",
      all(t["brasil"]["n"] == SOCIAIS["captura_amostra"] for t in SOCIAIS["testes"] if t["desfecho"] == "cap"))

# ---------- de onde vieram os votos: regressão ecológica (4.1) e por lugar (4.2) ----------
FONTES = [("O", "votos dos outros candidatos do 1º turno"), ("C", "variação do comparecimento"), ("R", "queda de brancos e nulos")]
def coef(y, X, w): return np.linalg.solve(X.T @ (X * w[:, None]), X.T @ (w * y))
def boot_contagens(estr, rng):  # reamostra municípios dentro de cada estrato, a mesma quantidade de cada um
    n = len(estr); planos = []
    for s in np.unique(estr):
        pos = np.flatnonzero(estr == s); k = len(pos)
        planos.append((np.repeat(np.arange(B_BOOT), k) * n + pos[rng.integers(0, k, size=B_BOOT * k)]))
    return np.bincount(np.concatenate(planos), minlength=B_BOOT * n).reshape(B_BOOT, n).astype(float)
def boot_estados(g, rng):  # conferência: reamostra estados inteiros
    gi, G = grupos(g); k = np.zeros((B_BOOT, G))
    np.add.at(k, (np.repeat(np.arange(B_BOOT), G), rng.integers(0, G, size=B_BOOT * G)), 1)
    return k[:, gi]
def ecologica(sel, nome, estr, intercepto=False, peso=True, modo="estrato"):
    E = E1[sel]; X = np.column_stack([O1[sel] / E, dC[sel] / E, R[sel] / E])
    if intercepto: X = np.column_stack([np.ones(len(E)), X])
    w = E if peso else np.ones(len(E))
    yL, yF = dL[sel] / E, dF[sel] / E
    bL, bF = coef(yL, X, w), coef(yF, X, w)
    rng = sorteador("ecológica " + nome)
    cont = boot_contagens(estr, rng) if modo == "estrato" else boot_estados(estr, rng)
    W = cont * w[None, :]; k = X.shape[1]
    M = (W @ (X[:, :, None] * X[:, None, :]).reshape(len(E), k * k)).reshape(B_BOOT, k, k)
    bb = np.linalg.solve(M, (W @ (X * yL[:, None]))[..., None])[..., 0]
    lo, hi = np.percentile(bb, [2.5, 97.5], axis=0)
    nomes = (["intercepto"] if intercepto else []) + [c for c, _ in FONTES]
    out = {"n": int(sel.sum()), "soma_fontes_igual_a_1": bool(np.allclose((bL + bF)[-3:], 1, atol=1e-9))}
    for i, c in enumerate(nomes):
        out[c] = {"lula": r(bL[i]), "lula_ic95": [r(lo[i]), r(hi[i])], "flavio": r(bF[i]), "flavio_ic95": [r(1 - hi[i]), r(1 - lo[i])]
                  if c != "intercepto" else [r(-hi[i]), r(-lo[i])]}
    return out
def dp_ponderado(v, w): m = np.sum(w * v) / w.sum(); return float(np.sqrt(np.sum(w * (v - m) ** 2) / w.sum()))
br = np.ones(N, bool)
# Brasil e regiões: o intervalo principal reamostra estados inteiros, como o erro agrupado das hipóteses (M2, T32); municípios sorteados
# dentro de cada estado viram conferência. Nos estados, só dá para sortear municípios (um estado não tem grupos para reamostrar).
ECO = {"brasil": ecologica(br, "Brasil por estado", uf, modo="estados"),
       "conferencias": {"com_intercepto": ecologica(br, "Brasil com intercepto, por estado", uf, intercepto=True, modo="estados"),
                        "bootstrap_municipios": ecologica(br, "Brasil", uf),
                        "sem_peso": ecologica(br, "Brasil sem peso, por estado", uf, peso=False, modo="estados")}}
ECO["intervalo"] = "estados inteiros"
linha("regressão ecológica: em cada fonte, a parte do Lula mais a do Flávio dá 100% (identidade do saldo)",
      all(v["soma_fontes_igual_a_1"] for v in [ECO["brasil"]] + list(ECO["conferencias"].values())))
VAR_FONTE = {"O": O1 / E1, "C": dC / E1, "R": R / E1}
DP_BR = {c: dp_ponderado(VAR_FONTE[c], E1) for c, _ in FONTES}
ROT_VAR = {"O": "variação pequena dos votos dos outros", "C": "variação pequena do comparecimento", "R": "variação pequena dos brancos e nulos"}
def por_lugar(nivel, nome_lugar, sel, estr):
    n = int(sel.sum())
    modo = "estrato" if nivel == "uf" else "estados"
    item = {"nivel": nivel, "lugar": nome_lugar, "n": n, "var_comparecimento": int(dC[sel].sum()),
            "saldo_comparecimento": "subiu" if dC[sel].sum() > 0 else "caiu", "fontes": {},  # onde caiu, o texto fala da perda (4.2)
            "intervalo": "municípios do estado" if modo == "estrato" else "estados inteiros"}
    est = ecologica(sel, nome_lugar if modo == "estrato" else nome_lugar + " por estado", estr, modo=modo) if n >= MIN_MUN else None
    # m1 (T32): "fora de 0% a 100%" não é falta de precisão, é sinal de que o modelo não descreve o lugar. Vem antes da meia largura,
    # e, quando uma fonte sai de 0% a 100%, todas as fontes do lugar ganham o aviso, inclusive as que passam.
    fora = [] if est is None else [c for c, _ in FONTES if not 0 <= est[c]["lula"] <= 1]
    item["modelo_nao_descreve"] = fora
    for c, rot in FONTES:
        d = {"fonte": rot}
        if est is None:
            d.update(passa=False, motivo="poucos municípios")
        else:
            e = est[c]; meia = (e["lula_ic95"][1] - e["lula_ic95"][0]) / 2
            d.update(lula=e["lula"], lula_ic95=e["lula_ic95"], flavio=e["flavio"], flavio_ic95=e["flavio_ic95"], meia_largura=r(meia))
            dp = dp_ponderado(VAR_FONTE[c][sel], E1[sel])
            d["dp_fonte_razao_brasil"] = r(dp / DP_BR[c], 4)
            d["aviso_modelo"] = bool(fora)
            if c in fora:
                d.update(passa=False, motivo="estimativa fora de 0% a 100%")
            elif meia > MEIA_LARGURA:
                d.update(passa=False, motivo=ROT_VAR[c] if dp < 0.5 * DP_BR[c] else "resultados muito dispersos")
            else:
                d["passa"] = True
                d["maior_parte"] = "Lula" if e["lula_ic95"][0] > 0.5 else "Flávio" if e["lula_ic95"][1] < 0.5 else "sem lado claro"
        item["fontes"][c] = d
    return item
# o critério da 4.2 vale também para o Brasil (decisão P17 do autor, 26/10/2026, 13:03; nota datada no HIPOTESES.md)
LUGARES = [por_lugar("brasil", "Brasil", br, uf)]
LUGARES += [por_lugar("regiao", rg, reg == rg, uf[reg == rg]) for rg in ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]]
LUGARES += [por_lugar("uf", u, uf == u, uf[uf == u]) for u in sorted(set(uf))]
linha("Brasil: a estimativa principal da ecológica é a mesma do critério por lugar (mesmo intervalo, de estados inteiros)",
      all(LUGARES[0]["fontes"][c]["lula_ic95"] == ECO["brasil"][c]["lula_ic95"] for c, _ in FONTES))

# ---------- matriz de transição (M1, T32; conferência, depois do resultado) ----------
# Goodman em níveis, como na literatura de fluxos entre eleições: as cinco categorias do 1º turno (Lula, Flávio, outros, brancos e nulos,
# abstenção) explicam as quatro do 2º (Lula, Flávio, brancos e nulos, abstenção), tudo ÷ E1, peso E1, sem intercepto.
ORIG = ["Lula", "Flávio", "outros", "brancos e nulos", "abstenção"]; DEST = ["Lula", "Flávio", "brancos e nulos", "abstenção"]
XT = np.column_stack([L1, F1, O1, BN1, E1 - C1]) / E1[:, None]
YT = np.column_stack([L2, F2, BN2, E2 - C2]) / E1[:, None]
def transicao(sel, nome, estr, modo):
    X_, Y_, w = XT[sel], YT[sel], E1[sel]
    P_ = np.linalg.solve(X_.T @ (X_ * w[:, None]), X_.T @ (Y_ * w[:, None]))
    cont = boot_contagens(estr, sorteador("transição " + nome)) if modo == "estrato" else boot_estados(estr, sorteador("transição " + nome))
    W = cont * w[None, :]
    M = (W @ (X_[:, :, None] * X_[:, None, :]).reshape(len(w), 25)).reshape(B_BOOT, 5, 5)
    Pb = np.linalg.solve(M, (W @ (X_[:, :, None] * Y_[:, None, :]).reshape(len(w), 20)).reshape(B_BOOT, 5, 4))
    lo, hi = np.percentile(Pb, [2.5, 97.5], axis=0)
    fr, frb = P_[2, 0] / (P_[2, 0] + P_[2, 1]), Pb[:, 2, 0] / (Pb[:, 2, 0] + Pb[:, 2, 1])
    return {"n": int(sel.sum()), "intervalo": "estados inteiros" if modo == "estados" else "municípios do estado",
            "matriz": [[{"valor": r(P_[i, j]), "ic95": [r(lo[i, j]), r(hi[i, j])]} for j in range(4)] for i in range(5)],
            "outros_lula_entre_os_dois": r(fr), "outros_lula_entre_os_dois_ic95": [r(np.percentile(frb, 2.5)), r(np.percentile(frb, 97.5))],
            "celulas_fora_0_100": [[ORIG[i], DEST[j], r(P_[i, j], 4)] for i in range(5) for j in range(4) if not 0 <= P_[i, j] <= 1]}
TRANS = {"origens": ORIG, "destinos": DEST, "brasil": transicao(br, "Brasil", uf, "estados"),
         "brasil_municipios": transicao(br, "Brasil por municípios", uf, "estrato"),
         "regioes": {rg: transicao(reg == rg, rg, uf[reg == rg], "estados") for rg in ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]}}
linha("matriz de transição: as linhas somam o eleitorado do 2º turno ÷ o do 1º (a soma de cada linha fica perto de 1)",
      all(abs(sum(c_["valor"] for c_ in lin) - 1) < 0.1 for lin in TRANS["brasil"]["matriz"]))
# as três especificações lado a lado: dos votos dos outros que foram para um dos dois, a parte do Lula
ESPEC_OUTROS = {"principal": ECO["brasil"]["O"]["lula"], "com_intercepto": ECO["conferencias"]["com_intercepto"]["O"]["lula"],
                "transicao": TRANS["brasil"]["outros_lula_entre_os_dois"]}

# ---------- conta por seção como principal da 4.2 (T35; HIPOTESES.md, 4.5; decisão P28 do autor, 27/10/2026, 09:42) ----------
# Vem pronta de dados/secoes_inferencia.json (scripts/secoes_inferencia.py, que roda antes deste). A conta por município acima fica como
# conferência, em "por_lugar_municipios". A regra 8 da 4.5 (lados opostos → "não deu") usou as leituras por município: confere que são estas.
with open(ENT_SEC_INF, encoding="utf-8") as fh: SEC = json.load(fh)
def leitura(d): return d.get("maior_parte") if d["passa"] else "não deu"
LUG_MUN = {l["lugar"]: l for l in LUGARES}
linha("conta por seção: as leituras por município que ela comparou são as desta conta, nos 33 lugares e nas 3 fontes",
      [l["lugar"] for l in SEC["por_lugar"]] == [l["lugar"] for l in LUGARES]
      and all(x["municipios"] == leitura(LUG_MUN[x["lugar"]]["fontes"][x["fonte"]]) for x in SEC["comparacao"]))
LUGARES_MUN, LUGARES = LUGARES, SEC["por_lugar"]
ECO["secoes"] = {c: {k: LUGARES[0]["fontes"][c][k] for k in ("lula", "lula_ic95", "flavio", "flavio_ic95")} for c, _ in FONTES}
ECO["secoes"]["parte_comum_municipio"] = LUGARES[0]["parte_comum_municipio"]
ESPEC_OUTROS["secoes"] = ECO["secoes"]["O"]["lula"]

# ---------- limites de Duncan e Davis na formulação em níveis (m3, T32) ----------
# Dos votos dos outros no 1º turno, a parte que foi para o Lula no 2º fica entre max(0, (L2 − (E1 − O1)) ÷ O1) e min(1, L2 ÷ O1)
# em cada município: as outras categorias do 1º turno, juntas, não podem dar mais votos ao Lula do que tinham.
lim_lo = np.clip((L2 - (E1 - O1)) / O1, 0, 1); lim_hi = np.clip(L2 / O1, 0, 1)
LIMITES = {"municipios": N, "largura_mediana": r(float(np.median(lim_hi - lim_lo)), 4),
           "sem_informacao": int(np.sum((lim_lo == 0) & (lim_hi == 1))),
           "largura_ponderada_media": r(float(np.sum(O1 * (lim_hi - lim_lo)) / O1.sum()), 4)}

# ---------- funil (4.3) ----------
def funil(y, s, centro, winsor=False):
    # T32 (M3): τ² sem winsorizar. Com as distâncias cortadas em 10% e 90% (o método fixado antes, que fica como conferência), o τ² saía
    # pequeno demais: os z maiores são os dos municípios médios e grandes, e o corte tirava justamente a informação que mede τ².
    z = (y - centro) / s
    if winsor: lo, hi = np.percentile(z, [10, 90]); z = np.clip(z, lo, hi)  # distâncias padronizadas cortadas em 10% e 90%
    phi = np.mean(z ** 2)
    w = 1 / s ** 2; n = len(y)
    tau2 = max(0.0, (n * phi - (n - 1)) / (w.sum() - (w ** 2).sum() / w.sum()))
    sd = np.sqrt(s ** 2 + tau2)
    return {"phi": phi, "tau2": tau2, "sd": sd, "fora95": np.abs(y - centro) > Z95 * sd, "fora998": np.abs(y - centro) > Z998 * sd}
def lista_fora(y, fu, centro, rot_acima, rot_abaixo):
    out = []
    for i in np.flatnonzero(fu["fora998"]):
        out.append({"cd_tse": cd[i], "uf": uf[i], "municipio": nome[i], "eleitorado_1t": int(E1[i]), "valor": r(y[i], 4),
                    "faixa_998": [r(centro - Z998 * fu["sd"][i], 4), r(centro + Z998 * fu["sd"][i], 4)],
                    "lado": rot_acima if y[i] > centro else rot_abaixo})
    return sorted(out, key=lambda x: (x["lado"], -abs(x["valor"] - centro)))
GRADE = np.geomspace(max(100, E1.min()), E1.max(), 80)
FUNIL = {}
th1, th2 = L1.sum() / (L1 + F1).sum(), L2.sum() / (L2 + F2).sum()
r1, r2 = (L1 + F1).sum() / E1.sum(), (L2 + F2).sum() / E1.sum()
centro_s = 100 * (th2 - th1)
def ep_s(Ea, Eb, na=None, nb=None):
    na = r1 * Ea if na is None else na; nb = r2 * Eb if nb is None else nb
    return 100 * np.sqrt(th1 * (1 - th1) / na + th2 * (1 - th2) / nb)
fs_ = funil(ds, ep_s(E1, E1), centro_s)
fs_own = funil(ds, ep_s(None, None, L1 + F1, L2 + F2), centro_s)
fs_win = funil(ds, ep_s(E1, E1), centro_s, winsor=True)
th_a1, th_a2 = (E1 - C1).sum() / E1.sum(), (E2 - C2).sum() / E2.sum()
centro_a = 100 * (th_a2 - th_a1)
def ep_a(Ea, Eb): return 100 * np.sqrt(th_a1 * (1 - th_a1) / Ea + th_a2 * (1 - th_a2) / Eb)
fa_ = funil(da, ep_a(E1, E1), centro_a)
fa_own = funil(da, ep_a(E1, E2), centro_a)
fa_win = funil(da, ep_a(E1, E1), centro_a, winsor=True)
def por_porte(fu, y, centro):  # a proporção fora da faixa de 95% deveria ficar perto de 5% em cada faixa de porte (M3)
    return [{"porte": int(p_), "n": int((porte == p_).sum()), "fora95_pct": r(100 * fu["fora95"][porte == p_].mean(), 2),
             "acima_pct": r(100 * (fu["fora95"] & (y > centro))[porte == p_].mean(), 2),
             "abaixo_pct": r(100 * (fu["fora95"] & (y < centro))[porte == p_].mean(), 2)} for p_ in range(1, 6)]
for chave, y, fu, own, win, centro, epf, acima, abaixo, th, rr in [
        ("var_fatia", ds, fs_, fs_own, fs_win, centro_s, lambda e: ep_s(e, e), "a variação da fatia do Lula ficou acima da faixa",
         "a variação da fatia do Flávio ficou acima da faixa", [th1, th2], [r1, r2]),
        ("var_abstencao", da, fa_, fa_own, fa_win, centro_a, lambda e: ep_a(e, e), "a variação da abstenção ficou acima da faixa",
         "a variação da abstenção ficou abaixo da faixa", [th_a1, th_a2], None)]:
    sdg = np.sqrt(epf(GRADE) ** 2 + fu["tau2"])
    FUNIL[chave] = {"centro_pp": r(centro, 4), "theta": [r(t, 8) for t in th], "razao_votos_eleitorado": None if rr is None else [r(x, 6) for x in rr],
                    "phi": r(fu["phi"], 4), "tau2_pp2": r(fu["tau2"], 6), "n": N,
                    "fora95": int(fu["fora95"].sum()), "fora998": int(fu["fora998"].sum()),
                    "fora998_acima": int((fu["fora998"] & (y > centro)).sum()), "fora998_abaixo": int((fu["fora998"] & (y < centro)).sum()),
                    "fora95_acima": int((fu["fora95"] & (y > centro)).sum()), "fora95_abaixo": int((fu["fora95"] & (y < centro)).sum()),
                    "por_porte": por_porte(fu, y, centro), "winsorizacao": "nenhuma (T32, M3)",
                    "assimetria_z": r(float(stats.skew((y - centro) / fu["sd"])), 3),
                    "curtose_excesso_z": r(float(stats.kurtosis((y - centro) / fu["sd"])), 3),
                    "curva": {"eleitorado": [int(e) for e in GRADE],
                              "lim95": [[r(centro - Z95 * s_, 4), r(centro + Z95 * s_, 4)] for s_ in sdg],
                              "lim998": [[r(centro - Z998 * s_, 4), r(centro + Z998 * s_, 4)] for s_ in sdg]},
                    "lista_fora998": lista_fora(y, fu, centro, acima, abaixo),
                    "conferencia_votos_proprios": {"tau2_pp2": r(own["tau2"], 6), "fora998": int(own["fora998"].sum()),
                                                   "mudam_de_lado_998": int((own["fora998"] != fu["fora998"]).sum())},
                    "conferencia_winsorizado": {"tau2_pp2": r(win["tau2"], 6), "fora95": int(win["fora95"].sum()),
                                                "fora998": int(win["fora998"].sum()), "por_porte": por_porte(win, y, centro)}}

# ---------- erro da projeção da noite (4.4) ----------
def num(x): return float(x.replace(",", ".")) if x.strip() not in ("", "None", "null") else np.nan
with open(ENT_HIST, encoding="utf-8-sig") as fh: hist = list(csv.DictReader(fh, delimiter=";"))
ap = np.array([num(h["urnas_apuradas_pct"]) for h in hist])
proj = np.array([num(h["projecao_final_pct"]) for h in hist])
parc = np.array([num(h["lula_2t_pct"]) for h in hist])
fim = ap >= 100
linha(f"histórico da noite: {len(hist)} leituras, de {n_(ap.min())}% a {n_(ap.max())}%; a de 100% é o resultado final "
      f"({n_(parc[fim][0], 3) if fim.any() else '—'}% contra {n_(S2_FINAL, 3)}%)", fim.sum() == 1 and abs(parc[fim][0] - S2_FINAL) < 0.001)
FAIXAS = []
for lo_ in range(0, 100, 10):
    s_ = (ap >= lo_) & (ap < lo_ + 10) & ~fim
    ep_, eparc = proj[s_] - S2_FINAL, parc[s_] - S2_FINAL
    ep_ = ep_[np.isfinite(ep_)]
    FAIXAS.append({"faixa": f"{lo_} a {lo_ + 10}", "leituras": int(s_.sum()), "leituras_com_projecao": int(len(ep_)),
                   "projecao": {"erro_medio": r(ep_.mean(), 4) if len(ep_) else None, "erro_abs_medio": r(np.abs(ep_).mean(), 4) if len(ep_) else None,
                                "maior_erro_abs": r(np.abs(ep_).max(), 4) if len(ep_) else None},
                   "parcial": {"erro_medio": r(eparc.mean(), 4) if s_.any() else None, "erro_abs_medio": r(np.abs(eparc).mean(), 4) if s_.any() else None,
                               "maior_erro_abs": r(np.abs(eparc).max(), 4) if s_.any() else None}})
tudo = ~fim & np.isfinite(proj)
PROJ = {"resultado_final_pct": r(S2_FINAL, 4), "leituras": int((~fim).sum()), "faixas": FAIXAS,
        "geral": {"projecao_erro_medio": r((proj[tudo] - S2_FINAL).mean(), 4), "projecao_erro_abs_medio": r(np.abs(proj[tudo] - S2_FINAL).mean(), 4),
                  "parcial_erro_medio": r((parc[~fim] - S2_FINAL).mean(), 4), "parcial_erro_abs_medio": r(np.abs(parc[~fim] - S2_FINAL).mean(), 4)},
        "pontos": [{"apurado": r(a_, 2), "projecao": r(p_, 4), "parcial": r(q_, 4)} for a_, p_, q_, z_ in zip(ap, proj, parc, fim) if not z_]}

# ---------- saída ----------
NAO_DEU = [{"nivel": l["nivel"], "lugar": l["lugar"], "n": l["n"], "fonte": d["fonte"], "motivo": d["motivo"]}
           for l in LUGARES for c, d in l["fontes"].items() if not d["passa"]]
saida = {"meta": {"gerado_em": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"), "script": "scripts/inferencia.py",
                  "regras": "docs/analise/HIPOTESES.md, aprovado em 26/10/2026, 12:43, com as mudanças datadas do T32 (correções do parecer "
                            "estatístico de 26/10/2026)", "semente": SEMENTE,
                  "bootstrap_selvagem": f"{B_SELVAGEM} repetições, pesos de Webb, hipótese nula imposta, por UF; intervalo por inversão do teste "
                                        "(ic95_selvagem)",
                  "bootstrap_ecologica": f"{B_BOOT} repetições, percentis 2,5 e 97,5; Brasil e regiões: estados inteiros reamostrados; "
                                         "estados: municípios reamostrados dentro do estado. Por lugar (por_lugar, nao_deu): conta por seção "
                                         "com efeito de município (T35, dados/secoes_inferencia.json; P28), estados inteiros no Brasil e nas "
                                         "regiões e municípios inteiros nos estados; a por município fica em por_lugar_municipios",
                  "erro_padrao": "agrupado por UF, CR1, t com (grupos − 1) graus de liberdade",
                  "unidades": "Δs, Δa e efeitos em pontos percentuais; coeficientes por 1 ponto da variável; ecológica em fração (0 a 1)",
                  "municipios": N, "exterior": "fora (HIPOTESES 2.1)"},
         "hipoteses": {k: {"versoes": v} for k, v in H.items()}, "complementos": COMPL,
         "H5": {"senador_estados_fora": H5_FORA.get("senador", {}), **H5},
         "h1_referencia": H1_REF, "poucos_grupos": POUCOS,
         "ecologica": ECO, "transicao": TRANS, "especificacoes_outros": ESPEC_OUTROS, "limites_duncan_davis": LIMITES,
         "por_lugar": LUGARES, "por_lugar_municipios": LUGARES_MUN, "nao_deu": NAO_DEU, "funil": FUNIL, "projecao": PROJ, "sociais": SOCIAIS}
for k, v in list(saida["hipoteses"].items()) + [(f"H5 {c}", saida["H5"][c]) for c, _, _ in CARGOS]:
    pr = v["versoes"][0]
    v["classificacao"] = pr["classificacao"]
    v["se_mantem"] = f"{sum(x['classificacao'] == pr['classificacao'] for x in v['versoes'][1:])} de {len(v['versoes']) - 1}"
    v["conferencias"] = {c: sum(x["classificacao"] == c for x in v["versoes"][1:]) for c in ("confirmada", "contrária", "inconclusiva")}
with open(SAI, "w", encoding="utf-8") as fh: json.dump(saida, fh, ensure_ascii=False, indent=1)

# ---------- relatório ----------
ESCALA_X = {"s1": 10, "o": 10, "Δa": 1, "escala contínua": 1}
def tabela(vs):
    print("| Versão | Municípios | UFs | Coeficiente | Intervalo de 95% (erro agrupado) | Intervalo de 95% (bootstrap) | p (selvagem) | R² | "
          "Efeito interquartil | Classificação |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for x in vs:
        m_ = ESCALA_X.get(x["variavel"], 10)
        cl = x.get("classificacao", "—") + (" (pequena)" if x.get("pequena") and x.get("classificacao") != "inconclusiva" else "")
        print(f"| {x['versao']} | {f(x['n'])} | {x['grupos']} | {n_(x['coef'] * m_, 3, True)} por {m_} | "
              f"{n_(x['ic95'][0] * m_, 3, True)} a {n_(x['ic95'][1] * m_, 3, True)} | "
              f"{'—' if not x.get('ic95_selvagem') else n_(x['ic95_selvagem'][0] * m_, 3, True) + ' a ' + n_(x['ic95_selvagem'][1] * m_, 3, True)} | "
              f"{'—' if x['p_selvagem'] is None else n_(x['p_selvagem'], 4)} | {n_(x['r2'], 3)} | {n_(x['efeito_interquartil_pp'], 2, True)} p.p. | {cl} |")
    print()
print("\n### Hipóteses H1, H3 e H4 (Δs, em p.p.)\n")
for k, v in saida["hipoteses"].items():
    print(f"**{k}** · variável: {v['versoes'][0]['variavel']} · previsto: {v['versoes'][0]['previsto']} · "
          f"**{v['classificacao']}** · conferências: " + ", ".join(f"{q} {c}" for c, q in v["conferencias"].items()) + "\n")
    tabela(v["versoes"])
print("**Complementos, sem hipótese** (votos ganhos por eleitor do 1º turno, em %)\n")
for k, v in COMPL.items(): tabela(v)
print("### H5: voto dividido\n")
print("Senador, estados fora (campo da esquerda abaixo de 5% dos votos de senador no estado): "
      + ", ".join(f"{u} ({n_(p, 2)}%)" for u, p in saida["H5"]["senador_estados_fora"].items()) + "\n")
for c, _, _ in CARGOS:
    v = saida["H5"][c]
    print(f"**{v['cargo']}** · **{v['classificacao']}** · conferências: " + ", ".join(f"{q} {c}" for c, q in v["conferencias"].items()) + " · "
          f"municípios fora por sub judice acima de 5%: {v['versoes'][7]['municipios_fora_sub_judice']}\n")
    tabela(v["versoes"])
print("### Dados sociais (seção 6; T34): 35 testes, Holm na versão dentro dos estados\n")
print(f"Municípios com dados: {f(SOCIAIS['municipios_com_dados'])}; captura: {f(SOCIAIS['captura_amostra'])}.\n")
print("| Variável | Desfecho | Coeficiente (dentro) | Intervalo (bootstrap) | p selvagem | p Holm | p CR1 Holm | Interquartil | Resultado | "
      "Brasil: coef. | p Holm | Resultado |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|")
def res_soc(v): return ("há associação, " + v["direcao"] + (" (pequena)" if v["pequena"] else "")) if v["associacao"] else "sem associação clara"
for t in SOCIAIS["testes"]:
    a_, b_ = t["principal"], t["brasil"]
    print(f"| {t['variavel']} | {SOCIAIS['desfechos'][t['desfecho']]} | {n_(a_['coef'], 4, True)} | "
          f"{n_(a_['ic95_selvagem'][0], 4, True)} a {n_(a_['ic95_selvagem'][1], 4, True)} | {n_(a_['p_selvagem'], 4)} | {n_(a_['p_holm'], 4)} | "
          f"{n_(a_['p_cr1_holm'], 4)} | {n_(a_['efeito_interquartil_pp'], 2, True)} | {res_soc(a_)} | {n_(b_['coef'], 4, True)} | "
          f"{n_(b_['p_holm'], 4)} | {res_soc(b_)} |")
print()
print("### H1 contra a divisão igual (M4, exploratória)\n")
print(f"Captura do Brasil sem o exterior: {n_(100 * CAPT_BR, 2)}%.\n")
tabela([H["H1"][0], H1_REF["esperada"], H1_REF["diferenca"], H["H1"][1], H1_REF["esperada_brasil"], H1_REF["diferenca_brasil"]])
print("### Poucos grupos (M5)\n")
print("Peso de cada estado (E1): " + ", ".join(f"{u} {n_(100 * p_, 1)}%" for u, p_ in list(PESO_UF.items())[:8]) + "\n")
for cod in ("H1", "H3", "H4"):
    ge = [x["g_efetivo"] for x in POUCOS["g_efetivo"][cod]]; se = POUCOS["sem_um_estado"][cod]
    print(f"- {cod}: número efetivo de grupos de {n_(min(ge), 1)} a {n_(max(ge), 1)} (26 estados); sem um estado, coeficiente de "
          f"{n_(10 * se['coef_min'], 3, True)} a {n_(10 * se['coef_max'], 3, True)} por 10; mudam a classificação: "
          + (", ".join(f"{e['uf']} (p {n_(e['p_selvagem'], 3)})" for e in se["estados"] if e["uf"] in se["mudam_classificacao"]) or "nenhum"))
print("\n### De onde vieram os votos (regressão ecológica, Brasil, em % de cada fonte)\n")
print("| Versão | Fonte | Lula | Intervalo | Flávio | Intervalo |\n|---|---|---|---|---|---|")
for nm, e in [("principal", ECO["brasil"])] + list(ECO["conferencias"].items()):
    for c in (["intercepto"] if "intercepto" in e else []) + [c for c, _ in FONTES]:
        rot = dict(FONTES).get(c, "intercepto (p.p. do eleitorado)")
        print(f"| {nm} | {rot} | {n_(100 * e[c]['lula'], 1)}% | {n_(100 * e[c]['lula_ic95'][0], 1)} a {n_(100 * e[c]['lula_ic95'][1], 1)} | "
              f"{n_(100 * e[c]['flavio'], 1)}% | {n_(100 * e[c]['flavio_ic95'][0], 1)} a {n_(100 * e[c]['flavio_ic95'][1], 1)} |")
print("\n### Matriz de transição (M1; Brasil, estados inteiros)\n")
print("| 1º turno → 2º turno | " + " | ".join(DEST) + " |\n|---|---|---|---|---|")
for i, nm in enumerate(ORIG):
    print(f"| {nm} | " + " | ".join(f"{n_(100 * c_['valor'], 1)}% ({n_(100 * c_['ic95'][0], 0)} a {n_(100 * c_['ic95'][1], 0)})"
                                      for c_ in TRANS["brasil"]["matriz"][i]) + " |")
t_ = TRANS["brasil"]; tm_ = TRANS["brasil_municipios"]
print(f"\nDos votos dos outros que foram para um dos dois, Lula {n_(100 * t_['outros_lula_entre_os_dois'], 1)}% (estados: "
      f"{n_(100 * t_['outros_lula_entre_os_dois_ic95'][0], 1)} a {n_(100 * t_['outros_lula_entre_os_dois_ic95'][1], 1)}; municípios: "
      f"{n_(100 * tm_['outros_lula_entre_os_dois_ic95'][0], 1)} a {n_(100 * tm_['outros_lula_entre_os_dois_ic95'][1], 1)}); "
      f"células fora de 0% a 100%: {len(t_['celulas_fora_0_100'])} de 20.")
for rg, t_ in TRANS["regioes"].items():
    print(f"- {rg}: outros → Lula entre os dois {n_(100 * t_['outros_lula_entre_os_dois'], 0)}% "
          f"({n_(100 * t_['outros_lula_entre_os_dois_ic95'][0], 0)} a {n_(100 * t_['outros_lula_entre_os_dois_ic95'][1], 0)}); "
          f"células fora: {len(t_['celulas_fora_0_100'])}")
print("\nTrês especificações, parte do Lula nos votos dos outros: " + "; ".join(f"{k} {n_(100 * v, 1)}%" for k, v in ESPEC_OUTROS.items()))
print(f"\nLimites de Duncan e Davis (outros → Lula, por município): largura mediana {n_(100 * LIMITES['largura_mediana'], 1)} pontos; "
      f"de 0% a 100%, sem informação, em {f(LIMITES['sem_informacao'])} de {f(N)} municípios.")
print("\n### Por lugar: Brasil, regiões e estados (parte do Lula em cada fonte; a do Flávio é 100% menos ela)\n")
print("| Lugar | Municípios | ΔC | Outros | Comparecimento | Brancos e nulos |\n|---|---|---|---|---|---|")
def cel(d):
    if not d["passa"] and "lula" in d and d["motivo"] == "estimativa fora de 0% a 100%":
        return f"fora do modelo ({n_(100 * d['lula'], 0)}%)"
    if not d["passa"]:
        extra = "" if "lula" not in d else f" ({n_(100 * d['lula'], 0)}%, ±{n_(100 * d['meia_largura'], 0)})"
        return f"não deu: {d['motivo']}{extra}"
    return (f"{n_(100 * d['lula'], 1)}% ({n_(100 * d['lula_ic95'][0], 1)} a {n_(100 * d['lula_ic95'][1], 1)}); {d['maior_parte']}"
            + (" ⚠" if d.get("aviso_modelo") else ""))
for l in LUGARES:
    print(f"| {l['lugar']} | {f(l['n'])} | {'+' if l['var_comparecimento'] > 0 else ''}{f(l['var_comparecimento'])} | "
          + " | ".join(cel(l["fontes"][c]) for c, _ in FONTES) + " |")
print(f"\nEstimativas que não deram: {len(NAO_DEU)} de {3 * len(LUGARES)} (lugar × fonte).\n")
print("### Funil\n")
for k, v in FUNIL.items():
    print(f"- **{k}:** centro {n_(v['centro_pp'], 3, True)} p.p.; φ = {n_(v['phi'], 2)}; τ² = {n_(v['tau2_pp2'], 4)} p.p.²; "
          f"fora da faixa de 95%: {f(v['fora95'])} de {f(v['n'])} ({n_(100 * v['fora95'] / v['n'], 1)}%); fora da de 99,8%: {v['fora998']} "
          f"({v['fora998_acima']} acima, {v['fora998_abaixo']} abaixo); conferência com os votos de cada município: {v['conferencia_votos_proprios']['fora998']} "
          f"fora, {v['conferencia_votos_proprios']['mudam_de_lado_998']} mudam de lado; fora de 95% por porte: "
          + ", ".join(f"{x['porte']}: {n_(x['fora95_pct'], 1)}%" for x in v["por_porte"])
          + f"; acima/abaixo de 95%: {v['fora95_acima']}/{v['fora95_abaixo']}; winsorizado (conferência): τ² = "
          f"{n_(v['conferencia_winsorizado']['tau2_pp2'], 4)}, {v['conferencia_winsorizado']['fora95']} fora de 95%")
print("\n### Erro da projeção da noite (p.p., contra 51,785%)\n")
print("| % apurado | Leituras | Projeção: erro médio | erro absoluto médio | maior | Parcial: erro médio | erro absoluto médio | maior |")
print("|---|---|---|---|---|---|---|---|")
for fx in FAIXAS:
    p_, q_ = fx["projecao"], fx["parcial"]
    print(f"| {fx['faixa']} | {fx['leituras']} | {n_(p_['erro_medio'], 3, True)} | {n_(p_['erro_abs_medio'], 3)} | {n_(p_['maior_erro_abs'], 3)} | "
          f"{n_(q_['erro_medio'], 3, True)} | {n_(q_['erro_abs_medio'], 3)} | {n_(q_['maior_erro_abs'], 3)} |")
g_ = PROJ["geral"]
print(f"| todas | {PROJ['leituras']} | {n_(g_['projecao_erro_medio'], 3, True)} | {n_(g_['projecao_erro_abs_medio'], 3)} | | "
      f"{n_(g_['parcial_erro_medio'], 3, True)} | {n_(g_['parcial_erro_abs_medio'], 3)} | |")
print(f"\n- `inferencia.json`: {os.path.getsize(SAI) // 1024} KB")
print(f"\n**Resultado: {'tudo confere' if ok else 'há conferência com erro'}.**")
sys.exit(0 if ok else 1)
