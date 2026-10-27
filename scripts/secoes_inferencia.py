# T35: para onde foi o saldo do comparecimento, comparando seções do mesmo município (HIPOTESES.md, 4.5, "Regra por seção",
# escrita em 27/10/2026, 09:34, antes de qualquer conta com os votos das seções).
# Lê em ../dados: secoes_presidente.csv.gz (T27), analise_municipios.csv (T03, só a região de cada município e a conferência das somas)
# e inferencia.json (T06/T32, só para comparar com a estimativa por município). Grava secoes_inferencia.json; não mexe no inferencia.json.
# Uso: python -I scripts/secoes_inferencia.py  (imprime o relatório em Markdown; sai com 1 se alguma conferência falhar)
# Mesmo modelo da 4.1 com efeito de município (tira a média ponderada de cada município), peso E1, bootstrap de 1.000 repetições:
# Brasil e regiões por estados inteiros, estados por municípios inteiros. Mesmo critério de precisão da 4.2 (ordem do T32, m1).
# Roda antes do scripts/inferencia.py, que, desde a decisão P28 do autor (27/10/2026), leva este resultado para a página.
import csv, gzip, json, os, sys, zlib, datetime
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")  # o relatório tem acentos e "−", que o terminal do Windows não codifica (diário, D03)
AQUI = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(AQUI, "..", "dados")
ENT_SEC, ENT_MU, ENT_INF = (os.path.join(DADOS, n) for n in ("secoes_presidente.csv.gz", "analise_municipios.csv", "inferencia.json"))
SAI = os.path.join(DADOS, "secoes_inferencia.json")

# regras fixadas no HIPOTESES.md (4.2 e 4.5)
SEMENTE, B_BOOT = 20261026, 1000
MIN_MUN, MEIA_LARGURA = 30, 0.10
APTOS_MAX = 5  # conferência (b): fora as seções em que os aptos mudam mais de 5 eleitores entre os turnos
REGIOES = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]
FONTES = [("O", "votos dos outros candidatos do 1º turno"), ("C", "variação do comparecimento"), ("R", "queda de brancos e nulos")]
ROT_VAR = {"O": "variação pequena dos votos dos outros", "C": "variação pequena do comparecimento", "R": "variação pequena dos brancos e nulos"}
DEPENDE = "depende da comparação (municípios ou seções)"

ok = True
def linha(texto, certo):
    global ok
    ok &= bool(certo); print(f"- {'OK' if certo else 'ERRO'}: {texto}")
def f(x): return f"{int(round(x)):,}".replace(",", ".")
def p1(v): return "—" if v is None else f"{100 * v:.1f}".replace(".", ",").replace("-", "−")
def r(v, casas=6): return None if v is None or not np.isfinite(v) else round(float(v), casas)
def sorteador(nome): return np.random.default_rng([SEMENTE, zlib.crc32(nome.encode())])

# ---------- dados ----------
with open(ENT_MU, encoding="utf-8") as fh: mu = [l for l in csv.DictReader(fh) if l["uf"] != "ZZ"]
REG = {l["cd_tse"]: l["regiao"] for l in mu}
CAND1 = ["13", "14", "16", "21", "22", "27", "28", "29", "30", "35", "55", "70", "80"]
cols = {k: [] for k in ["uf", "cd", "inst1", "inst2", "E1", "E2", "C1", "C2", "L1", "F1", "O1", "BN1", "L2", "F2", "BN2", "ag", "c28"]}
c28_ext = C1_ext = 0
TODAS = {"secoes": 0, "aptos_mudam": 0}  # as 499.248 seções, com o exterior, para a nota N22 na página
with gzip.open(ENT_SEC, "rt", encoding="utf-8") as fh:
    for l in csv.DictReader(fh):
        TODAS["secoes"] += 1; TODAS["aptos_mudam"] += (l["t1_aptos"] or "0") != (l["t2_aptos"] or "0")
        if l["uf"] == "ZZ": c28_ext += int(l["t1_28"] or 0); C1_ext += int(l["t1_comp"] or 0); continue  # exterior fora (2.1)
        n = lambda k: int(l[k] or 0)
        cols["uf"].append(l["uf"]); cols["cd"].append(l["cd_mun"])
        cols["inst1"].append(l["t1_instalada"] == "1"); cols["inst2"].append(l["t2_instalada"] == "1")
        cols["E1"].append(n("t1_aptos")); cols["E2"].append(n("t2_aptos")); cols["C1"].append(n("t1_comp")); cols["C2"].append(n("t2_comp"))
        cols["L1"].append(n("t1_13")); cols["F1"].append(n("t1_22"))
        cols["O1"].append(sum(n("t1_" + c) for c in CAND1 if c not in ("13", "22", "28")))
        cols["BN1"].append(n("t1_brancos") + n("t1_nulos") + n("t1_28")); cols["c28"].append(n("t1_28"))  # o 28 fora dos válidos (N21)
        cols["L2"].append(n("t2_13")); cols["F2"].append(n("t2_22")); cols["BN2"].append(n("t2_brancos") + n("t2_nulos"))
        cols["ag"].append(len([x for x in l["t2_agregadas"].split("/") if x.strip()]))
uf, cd = np.array(cols.pop("uf")), np.array(cols.pop("cd"))
V = {k: np.array(v, dtype=float if k not in ("inst1", "inst2") else bool) for k, v in cols.items()}
entra = V["inst1"] & V["inst2"] & (V["E1"] > 0) & (V["E2"] > 0)

print("### Conferência das entradas\n")
linha(f"seções do Brasil: {f(len(uf))}; instaladas nos dois turnos e com aptos nos dois: {f(entra.sum())}", entra.all() and len(uf) == 497897)
E1, E2, C1, C2, L1, F1, O1, BN1, L2, F2, BN2 = (V[k] for k in ("E1", "E2", "C1", "C2", "L1", "F1", "O1", "BN1", "L2", "F2", "BN2"))
dL, dF, dC, R = L2 - L1, F2 - F1, C2 - C1, BN1 - BN2
linha("identidade ΔL + ΔF = O1 + ΔC + R em todas as seções", np.all(dL + dF == O1 + dC + R))
linha(f"votos do candidato 28 fora dos válidos (N21): {f(V['c28'].sum())} no Brasil e {f(c28_ext)} no exterior, {f(V['c28'].sum() + c28_ext)} ao todo",
      V["c28"].sum() + c28_ext == 5246)
# as seções somam a base municipal do T03 em todo município do Brasil
idx = {c: i for i, c in enumerate(sorted(set(cd)))}; mi = np.array([idx[c] for c in cd]); M = len(idx)
soma = {k: np.bincount(mi, V[k], M) for k in ("E1", "C1", "L1", "F1", "O1", "BN1", "E2", "C2", "L2", "F2", "BN2")}
campo = {"E1": "eleitorado_1t", "C1": "comparecimento_1t", "L1": "lula_1t", "F1": "flavio_1t", "O1": "outros_1t", "BN1": "brancos_nulos_1t",
         "E2": "eleitorado_2t", "C2": "comparecimento_2t", "L2": "lula_2t", "F2": "flavio_2t", "BN2": "brancos_nulos_2t"}
dif = sum(int(soma[k][idx[l["cd_tse"]]] != int(l[campo[k]])) for l in mu for k in campo)
linha(f"soma das seções = `analise_municipios.csv` nos {f(len(mu))} municípios e nos 11 campos ({dif} diferenças)", dif == 0 and M == len(mu))

uf_m = np.empty(M, dtype=object); uf_m[mi] = uf  # UF e região de cada município
reg_m = np.array([REG[c] for c in sorted(idx)])

# ---------- regressão por seção com efeito de município ----------
def tira_media(v, w, sel):  # média ponderada de cada município (efeito fixo), só com as seções da versão
    sw = np.bincount(mi[sel], w[sel], M)
    m = np.bincount(mi[sel], (w * v)[sel], M) / np.where(sw > 0, sw, 1)
    return v - m[mi]
def blocos(sel, fe, peso):
    """Somas por município de X'WX e X'Wy (Lula), para a regressão e o bootstrap de grupos inteiros."""
    w = E1 if peso else np.ones(len(E1))
    X = np.column_stack([O1 / E1, dC / E1, R / E1]); yL = dL / E1
    if fe: X = np.column_stack([tira_media(X[:, j], w, sel) for j in range(3)]); yL = tira_media(yL, w, sel)
    ws = np.where(sel, w, 0)
    A = np.stack([np.bincount(mi, ws * X[:, i] * X[:, j], M) for i in range(3) for j in range(3)], 1)  # M × 9
    b = np.stack([np.bincount(mi, ws * X[:, i] * yL, M) for i in range(3)], 1)  # M × 3
    return A, b, X, ws
def resolve(A, b): return np.linalg.solve(A.reshape(b.shape[:-1] + (3, 3)), b[..., None])[..., 0]
def boot_grupos(gm, rng):  # gm: o grupo de cada município do lugar; reamostra grupos inteiros
    _, gi = np.unique(gm, return_inverse=True); G = gi.max() + 1; k = np.zeros((B_BOOT, G))
    np.add.at(k, (np.repeat(np.arange(B_BOOT), G), rng.integers(0, G, size=B_BOOT * G)), 1)
    return k[:, gi]
def boot_estratos(estr, rng):  # reamostra municípios dentro de cada estrato (estado), a mesma quantidade de cada um
    cont = np.zeros((B_BOOT, len(estr)))
    for s in np.unique(estr):
        pos = np.flatnonzero(estr == s); k = len(pos)
        np.add.at(cont, (np.repeat(np.arange(B_BOOT), k), pos[rng.integers(0, k, size=B_BOOT * k)]), 1)
    return cont
def dp_ponderado(v, w): m = np.sum(w * v) / w.sum(); return float(np.sqrt(np.sum(w * (v - m) ** 2) / w.sum()))

def versao(nome, sel, fe=True, peso=True, intervalo_br="estados"):
    A, b, X, ws = blocos(sel, fe, peso)
    dp_br = {c: dp_ponderado(X[sel, j], ws[sel]) for j, (c, _) in enumerate(FONTES)}
    lugares = [("brasil", "Brasil", np.ones(M, bool))] + [("regiao", rg, reg_m == rg) for rg in REGIOES] + \
              [("uf", u, uf_m == u) for u in sorted(set(uf_m))]
    out = []
    for nivel, lugar, lm in lugares:
        ms = np.flatnonzero(lm & (np.bincount(mi, sel, M) > 0)); n = len(ms); s_sec = sel & lm[mi]
        item = {"nivel": nivel, "lugar": lugar, "n": n, "secoes": int(s_sec.sum()), "var_comparecimento": int(dC[s_sec].sum()),
                "saldo_comparecimento": "subiu" if dC[s_sec].sum() > 0 else "caiu", "fontes": {},
                "intervalo": "municípios inteiros do estado" if nivel == "uf" else
                             ("estados inteiros" if intervalo_br == "estados" else "municípios inteiros dentro de cada estado")}
        est = None
        if n >= MIN_MUN:
            bL = resolve(A[ms].sum(0), b[ms].sum(0))
            rng = sorteador(f"seções {nome} {lugar}")
            cont = boot_grupos(ms, rng) if nivel == "uf" else (boot_grupos(uf_m[ms], rng) if intervalo_br == "estados" else boot_estratos(uf_m[ms], rng))
            bb = resolve(cont @ A[ms], cont @ b[ms])
            lo, hi = np.percentile(bb, [2.5, 97.5], axis=0)
            est = {c: (bL[j], lo[j], hi[j]) for j, (c, _) in enumerate(FONTES)}
        fora = [] if est is None else [c for c, _ in FONTES if not 0 <= est[c][0] <= 1]
        if est is not None and fe:  # o que os efeitos de município levam: a mudança comum à cidade, que não acompanha nenhuma das três fontes
            tot = {"O": O1[s_sec].sum(), "C": dC[s_sec].sum(), "R": R[s_sec].sum()}; dLt, dFt = dL[s_sec].sum(), dF[s_sec].sum()
            comum = dLt - sum(est[c][0] * tot[c] for c, _ in FONTES)
            item["parte_comum_municipio"] = {"lula": int(round(comum)), "flavio": int(round(-comum)), "saldo_dos_dois": int(dLt + dFt),
                                             "lula_pct_do_saldo": r(comum / (dLt + dFt), 4)}
        item["modelo_nao_descreve"] = fora
        for j, (c, rot) in enumerate(FONTES):
            d = {"fonte": rot}
            if est is None:
                d.update(passa=False, motivo="poucos municípios")
            else:
                v, lo_, hi_ = est[c]; meia = (hi_ - lo_) / 2
                d.update(lula=r(v), lula_ic95=[r(lo_), r(hi_)], flavio=r(1 - v), flavio_ic95=[r(1 - hi_), r(1 - lo_)], meia_largura=r(meia))
                dp = dp_ponderado(X[s_sec, j], ws[s_sec]); d["dp_fonte_razao_brasil"] = r(dp / dp_br[c], 4); d["aviso_modelo"] = bool(fora)
                if c in fora: d.update(passa=False, motivo="estimativa fora de 0% a 100%")
                elif meia > MEIA_LARGURA: d.update(passa=False, motivo=ROT_VAR[c] if dp < 0.5 * dp_br[c] else "resultados muito dispersos")
                else:
                    d["passa"] = True
                    d["maior_parte"] = "Lula" if lo_ > 0.5 else "Flávio" if hi_ < 0.5 else "sem lado claro"
            item["fontes"][c] = d
        out.append(item)
    return out

todas = np.ones(len(E1), bool)
PRINC = versao("principal", todas)
CONF = {"sem_efeito_de_municipio": versao("sem efeito de município", todas, fe=False),
        "sem_aptos_que_mudam": versao("sem aptos que mudam", np.abs(E2 - E1) <= APTOS_MAX),
        "sem_agregadas": versao("sem agregadas", V["ag"] == 0),
        "sem_peso": versao("sem peso", todas, peso=False),
        "municipios_dentro_do_estado": versao("municípios dentro do estado", todas, intervalo_br="estratos")}
linha("Brasil: a parte do Lula mais a do Flávio dá 100% em cada fonte (identidade do saldo)",
      all(abs(PRINC[0]["fontes"][c]["lula"] + PRINC[0]["fontes"][c]["flavio"] - 1) < 1e-9 for c, _ in FONTES))
# a mesma conta com ΔF dá 1 − b do Lula (os dois coeficientes somam 1): conferido no Brasil, refazendo com ΔF
_A, _b, _X, _ws = blocos(todas, True, True)
yF = tira_media(dF / E1, E1, todas)
bF = resolve(_A.sum(0), np.stack([np.bincount(mi, _ws * _X[:, i] * yF, M) for i in range(3)], 1).sum(0))
linha("Brasil: refeita com ΔF, a parte do Flávio é 1 − a do Lula em cada fonte",
      np.allclose(bF, [PRINC[0]["fontes"][c]["flavio"] for c, _ in FONTES], atol=1e-6))
s_sem_aptos, s_sem_ag = int((np.abs(E2 - E1) <= APTOS_MAX).sum()), int((V["ag"] == 0).sum())

# ---------- comparação com a estimativa por município (inferencia.json, como está) ----------
with open(ENT_INF, encoding="utf-8") as fh: INF = json.load(fh)
# desde a P28 (27/10/2026), o inferencia.json traz a conta por seção em "por_lugar" e a por município em "por_lugar_municipios"
LUG_MUN = INF.get("por_lugar_municipios", INF["por_lugar"])
MUN = {l["lugar"]: l for l in LUG_MUN}
linha("os mesmos 33 lugares nas duas contas", [l["lugar"] for l in PRINC] == [l["lugar"] for l in LUG_MUN])
def leitura(d): return d.get("maior_parte") if d["passa"] else "não deu"
def classe(lm, ls):
    if lm == ls: return "igual"
    if lm == "não deu": return "ganha"
    if ls == "não deu": return "perde"
    return "muda de lado"
COMP = []
for l in PRINC:
    lmun = MUN[l["lugar"]]
    for c, _ in FONTES:
        dm, ds = lmun["fontes"][c], l["fontes"][c]
        lm, ls = leitura(dm), leitura(ds)
        item = {"lugar": l["lugar"], "nivel": l["nivel"], "fonte": c, "municipios": lm, "secoes": ls, "classe": classe(lm, ls),
                "motivo_municipios": dm.get("motivo"), "motivo_secoes": ds.get("motivo")}
        if "lula" in dm and "lula" in ds:
            item["secao_dentro_do_ic_municipios"] = bool(dm["lula_ic95"][0] <= ds["lula"] <= dm["lula_ic95"][1])
            item["razao_meia_largura"] = r(ds["meia_largura"] / dm["meia_largura"], 3) if dm["meia_largura"] else None
            item["lula_municipios"], item["lula_secoes"] = dm["lula"], ds["lula"]
        # versões de conferência que mantêm a leitura por seção
        item["conferencias_mantem"] = [k for k, v in CONF.items() if leitura(next(x for x in v if x["lugar"] == l["lugar"])["fontes"][c]) == ls]
        if {lm, ls} == {"Lula", "Flávio"}:  # lados opostos: não sustenta nenhum dos dois (regra 8)
            ds.update(passa=False, motivo=DEPENDE); ds.pop("maior_parte", None); item["secoes_final"] = "não deu"
        COMP.append(item)
def conta(fonte, cl): return [x["lugar"] for x in COMP if x["fonte"] == fonte and x["classe"] == cl]
VEREDITO = {}
for c, _ in FONTES:
    g, p_, m_ = conta(c, "ganha"), conta(c, "perde"), conta(c, "muda de lado")
    VEREDITO[c] = "confirma" if not (g or p_ or m_) else "confirma e acrescenta" if not (p_ or m_) else "muda"
NAO_DEU = [{"nivel": l["nivel"], "lugar": l["lugar"], "n": l["n"], "fonte": d["fonte"], "motivo": d["motivo"]}
           for l in PRINC for c, _ in FONTES for d in [l["fontes"][c]] if not d["passa"]]
# capítulo 3: a parte dos votos dos outros no Brasil, por seção, como quarta especificação (regra 9)
ESPEC = {k: v for k, v in INF["especificacoes_outros"].items() if k != "secoes"}; ESPEC["secoes"] = PRINC[0]["fontes"]["O"]["lula"]

with open(SAI, "w", encoding="utf-8") as fh:
    json.dump({"meta": {"gerado": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"), "script": "scripts/secoes_inferencia.py",
                        "regra": "docs/analise/HIPOTESES.md, 4.5, \"Regra por seção\" (27/10/2026, 09:34)",
                        "entradas": ["dados/secoes_presidente.csv.gz", "dados/analise_municipios.csv", "dados/inferencia.json"],
                        "secoes": int(entra.sum()), "municipios": M, "semente": SEMENTE, "bootstrap": B_BOOT,
                        "secoes_sem_aptos_que_mudam": s_sem_aptos, "secoes_sem_agregadas": s_sem_ag,
                        "secoes_com_exterior": TODAS["secoes"], "secoes_aptos_mudam_com_exterior": TODAS["aptos_mudam"],
                        "votos_28": int(V["c28"].sum() + c28_ext), "comparecimento_1t_com_exterior": int(C1.sum() + C1_ext),
                        "modelo": "ΔL ÷ E1 = α_município + b_O × O1 ÷ E1 + b_C × ΔC ÷ E1 + b_R × R ÷ E1, peso E1 (o mesmo para ΔF)"},
               "por_lugar": PRINC, "conferencias": CONF, "comparacao": COMP, "veredito": VEREDITO, "nao_deu": NAO_DEU,
               "especificacoes_outros": ESPEC}, fh, ensure_ascii=False, indent=1)

# ---------- relatório ----------
print("\n### Resultado por lugar: parte do Lula (intervalo de 95%), seções × municípios\n")
for c, rot in FONTES:
    print(f"\n#### {rot} ({c}) · veredito: **{VEREDITO[c]}**\n")
    print("| Lugar | Municípios | Leitura | Seções | Leitura | Classe | Conferências que mantêm |\n|---|---|---|---|---|---|---|")
    for x, l in zip([x for x in COMP if x["fonte"] == c], PRINC):
        dm, ds = MUN[l["lugar"]]["fontes"][c], l["fontes"][c]
        cel = lambda d: f"{p1(d['lula'])} ({p1(d['lula_ic95'][0])} a {p1(d['lula_ic95'][1])})" if "lula" in d else "—"
        lei = lambda d: d.get("maior_parte") or d.get("motivo")
        print(f"| {l['lugar']} | {cel(dm)} | {lei(dm)} | {cel(ds)} | {lei(ds)} | {x['classe']} | {len(x['conferencias_mantem'])} de 5 |")
print("\n### Parte comum ao município (efeitos de município), em votos para o Lula (o Flávio fica com o oposto)\n")
for l in PRINC:
    pc = l.get("parte_comum_municipio")
    if pc and l["nivel"] != "uf": print(f"- {l['lugar']}: {f(pc['lula'])} ({p1(pc['lula_pct_do_saldo'])}% do saldo dos dois, {f(pc['saldo_dos_dois'])})")
print("\n### Votos dos outros no Brasil, as especificações (capítulo 3)\n")
for k, v in ESPEC.items(): print(f"- {k}: {p1(v)}%")
print(f"\nEstimativas que não deram, por seção: {len(NAO_DEU)} de 99 (por município: {sum(not d['passa'] for l in LUG_MUN for d in l['fontes'].values())}).")
print(f"Seções: {f(entra.sum())}; sem aptos que mudam mais de {APTOS_MAX}: {f(s_sem_aptos)}; sem as que receberam agregadas: {f(s_sem_ag)}.")
print(f"\nGravado em `dados/secoes_inferencia.json`. Conferências: {'todas OK' if ok else 'COM ERRO'}")
sys.exit(0 if ok else 1)
