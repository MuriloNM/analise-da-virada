# Classificação ideológica dos 30 partidos de 2026 e medidas do "campo da esquerda" por município × cargo no 1º turno (T05).
# Posição de cada partido: média das notas dos especialistas na rodada de 2022 de Bolognesi, Ribeiro, Codato e Silva (2025),
# calculada da base aberta (Harvard Dataverse, doi:10.7910/DVN/MFIXKW) e conferida com a Tabela 1 do artigo.
# Conferência: rodada de 2018 (Bolognesi, Ribeiro e Codato, 2023) e Zucco e Power (2024, doi:10.7910/DVN/6KVTUV).
# Fonte, regras R1 a R6 e corte fixados no ticket T05 em 26/10/2026, 11:52, antes destas contas. Não cruza com o 2º turno.
# Uso: python -I scripts/escala_partidos.py <df_experts.csv> <bls9_estimates_partiespresidents_long.tab> <escala_partidos.csv> <esquerda_1t_municipios.csv>
import sys, os, csv, json, math, statistics as st
from decimal import Decimal, ROUND_HALF_UP
sys.stdout.reconfigure(encoding="utf-8")
EXP, ZP, OUT_ESC, OUT_MED = sys.argv[1:5]
DADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dados")
VOTOS = os.path.join(DADOS, "votos_partido_1t.json")
BASE1T = os.path.join(DADOS, "base_1t_municipios.json")
CORTE = 4.49  # limite de cima da centro-esquerda no artigo (p. 13): extrema esquerda, esquerda e centro-esquerda formam o campo
LIMITES = [(1.50, "extrema esquerda"), (3.00, "esquerda"), (4.49, "centro-esquerda"), (5.50, "centro"), (7.00, "centro-direita"), (8.50, "direita"), (10.0, "extrema direita")]
CARGOS = {"5": "Senador", "6": "Deputado Federal", "7": "Deputado Estadual", "8": "Deputado Distrital"}
FONTE = ("Bolognesi, Ribeiro, Codato e Silva (2025), Opinião Pública 31, e31120, doi:10.1590/1807-0191202531120, rodada de 2022; "
         "dados em doi:10.7910/DVN/MFIXKW")
REGRAS = {"R1": "mesmo partido", "R2": "só mudou de nome", "R3": "fusão: média simples", "R4": "incorporação: fica a posição de quem incorporou",
          "R5": "criado depois da pesquisa: sem posição", "R6": "federação: cada partido com a própria posição"}

# Tabela 1 do artigo de 2025 (p. 12-13): média de 2022 e categoria publicada (última coluna, calculada pelos autores sobre a "média ponderada")
TAB22 = {"pstu": (0.51, "extrema esquerda"), "pco": (0.55, "extrema esquerda"), "pcb": (0.69, "extrema esquerda"), "psol": (1.41, "extrema esquerda"),
         "up": (1.63, "esquerda"), "p_cdo_b": (1.78, "esquerda"), "pt": (2.68, "esquerda"), "psb": (3.59, "centro-esquerda"),
         "rede": (3.69, "centro-esquerda"), "pdt": (3.86, "centro-esquerda"), "pv": (4.12, "centro-esquerda"), "sdd": (6.01, "centro-direita"),
         "cdd": (6.17, "centro-direita"), "avante": (6.47, "centro-direita"), "mdb": (6.50, "centro-direita"), "pmn": (6.74, "centro-direita"),
         "psdb": (6.76, "centro-direita"), "psd": (6.94, "direita"), "pmb": (7.29, "direita"), "podemos": (7.44, "direita"), "pros": (7.45, "direita"),
         "prtb": (7.49, "direita"), "agir": (7.55, "direita"), "ptb": (7.72, "direita"), "progre": (8.15, "direita"), "dc": (8.21, "direita"),
         "rep": (8.33, "extrema direita"), "psc": (8.41, "extrema direita"), "uniao": (8.49, "extrema direita"), "patri": (8.60, "extrema direita"),
         "novo": (8.67, "extrema direita"), "pl": (8.80, "extrema direita")}
# Tabela 1 do artigo de 2023 (Dados, p. 6-7), rodada de 2018. O artigo corta na segunda casa (3,9255 aparece como 3,92): tolerância de 0,01
TAB18 = {"pstu": 0.51, "pco": 0.61, "pcb": 0.91, "psol": 1.28, "p_cdo_b": 1.92, "pt": 2.97, "pdt": 3.92, "psb": 4.05, "rede": 4.77, "pps": 4.92,
         "pv": 5.29, "ptb": 6.10, "avante": 6.32, "sdd": 6.50, "pmn": 6.88, "pmb": 6.90, "phs": 6.96, "mdb": 7.01, "psd": 7.09, "psdb": 7.11,
         "pode": 7.24, "ppl": 7.27, "prtb": 7.45, "pros": 7.47, "prp": 7.59, "prb": 7.78, "pr": 7.78, "ptc": 7.86, "dc": 8.11, "psl": 8.11,
         "novo": 8.13, "progressistas": 8.20, "psc": 8.33, "patri": 8.55, "dem": 8.57}

# 2026 -> pesquisa: número: (regra 2022, colunas 2022, explicação, regra 2018, colunas 2018, explicação 2018, siglas em Zucco e Power 2021)
MAPA = {
    "10": ("R1", ["rep"], "Republicanos.", "R2", ["prb"], "PRB, que passou a se chamar Republicanos em 2019.", ["REP"]),
    "11": ("R1", ["progre"], "Progressistas.", "R1", ["progressistas"], "Progressistas.", ["PP"]),
    "12": ("R1", ["pdt"], "PDT.", "R1", ["pdt"], "PDT.", ["PDT"]),
    "13": ("R1", ["pt"], "PT.", "R1", ["pt"], "PT.", ["PT"]),
    "14": ("R5", [], "Partido Missão, registrado pelo TSE em 04/11/2025, depois da pesquisa. Nenhuma fonte acadêmica o classifica.", "R5", [], "Não existia.", []),
    "15": ("R1", ["mdb"], "MDB.", "R1", ["mdb"], "MDB.", ["MDB"]),
    "16": ("R1", ["pstu"], "PSTU.", "R1", ["pstu"], "PSTU.", []),
    "18": ("R1", ["rede"], "Rede.", "R1", ["rede"], "Rede.", []),
    "20": ("R4", ["podemos"], "Podemos. Incorporou o PSC (TSE, 15/06/2023), cuja posição não entra.", "R4", ["pode"], "Podemos. O PHS (2019) e o PSC (2023), incorporados depois, não entram.", ["PODE"]),
    "21": ("R1", ["pcb"], "PCB.", "R1", ["pcb"], "PCB.", []),
    "22": ("R1", ["pl"], "PL.", "R2", ["pr"], "PR, que voltou a se chamar PL em 2019.", ["PL"]),
    "23": ("R1", ["cdd"], "Cidadania.", "R2", ["pps"], "PPS, que passou a se chamar Cidadania em 2019.", ["CID"]),
    "25": ("R3", ["ptb", "patri"], "Fusão de PTB e Patriota (TSE, 09/11/2023): média das duas posições.", "R3", ["ptb", "patri"], "Média de PTB e Patriota. O PRP, incorporado ao Patriota em 2019, não entra.", []),
    "27": ("R1", ["dc"], "Democracia Cristã.", "R1", ["dc"], "Democracia Cristã.", []),
    "28": ("R1", ["prtb"], "PRTB.", "R1", ["prtb"], "PRTB.", []),
    "29": ("R1", ["pco"], "PCO.", "R1", ["pco"], "PCO.", []),
    "30": ("R1", ["novo"], "Novo.", "R1", ["novo"], "Novo.", ["NOVO"]),
    "33": ("R2", ["pmn"], "PMN, que passou a se chamar Mobilização Nacional (Mobiliza), com o mesmo número 33.", "R2", ["pmn"], "PMN.", []),
    "35": ("R2", ["pmb"], "PMB (Partido da Mulher Brasileira), que passou a se chamar Democrata (TSE, 02/12/2025), com o mesmo número 35.", "R2", ["pmb"], "PMB.", []),
    "36": ("R1", ["agir"], "Agir.", "R2", ["ptc"], "PTC, que passou a se chamar Agir.", []),
    "40": ("R1", ["psb"], "PSB.", "R1", ["psb"], "PSB.", ["PSB"]),
    "43": ("R1", ["pv"], "PV.", "R1", ["pv"], "PV.", []),
    "44": ("R1", ["uniao"], "União Brasil.", "R3", ["dem", "psl"], "Média de DEM e PSL, que se fundiram em 2022.", ["DEM", "PSL"]),
    "45": ("R1", ["psdb"], "PSDB.", "R1", ["psdb"], "PSDB.", ["PSDB"]),
    "50": ("R1", ["psol"], "PSOL.", "R1", ["psol"], "PSOL.", ["PSOL"]),
    "55": ("R1", ["psd"], "PSD.", "R1", ["psd"], "PSD.", ["PSD"]),
    "65": ("R1", ["p_cdo_b"], "PCdoB.", "R4", ["p_cdo_b"], "PCdoB. O PPL, incorporado em 2019, não entra.", ["PCDOB"]),
    "70": ("R1", ["avante"], "Avante.", "R1", ["avante"], "Avante.", []),
    "77": ("R4", ["sdd"], "Solidariedade. Incorporou o PROS (TSE, 14/02/2023), cuja posição não entra.", "R4", ["sdd"], "Solidariedade.", ["SD"]),
    "80": ("R1", ["up"], "Unidade Popular.", "R5", [], "Não existia (registrada no fim de 2019).", []),
}

def r2(x): return float(Decimal(repr(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
def categoria(x):
    return next(nome for lim, nome in LIMITES if x <= lim)
def spearman(a, b):
    def rank(v):
        o = sorted(range(len(v)), key=lambda i: v[i]); r = [0.0] * len(v); i = 0
        while i < len(o):
            j = i
            while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]: j += 1
            for k in range(i, j + 1): r[o[k]] = (i + j) / 2 + 1
            i = j + 1
        return r
    return pearson(rank(a), rank(b))
def pearson(a, b):
    ma, mb = st.mean(a), st.mean(b)
    sab = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    return sab / math.sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b))

# --- 1. posições dos partidos, da base aberta dos especialistas ---
with open(EXP, encoding="utf-8-sig", newline="") as f:
    rd = csv.reader(f, delimiter=";"); cab = next(rd); resp = list(rd)
def notas(col):
    j = cab.index(col)
    return [float(x[j].replace(",", ".")) for x in resp if x[j].strip()]
n18 = sum(x[0].startswith("2018") for x in resp); n22 = sum(x[0].startswith("2022") for x in resp)
media = {}
for col in cab[1:]:
    if col.startswith(("ideol_18_", "ideol_22_")):
        v = notas(col); media[col] = (r2(st.mean(v)), len(v), st.stdev(v))
for p, (m, _) in TAB22.items():
    if media["ideol_22_" + p][0] != m: raise SystemExit(f"2022 {p}: base {media['ideol_22_' + p][0]} × artigo {m}")
for p, m in TAB18.items():
    if abs(media["ideol_18_" + p][0] - m) > 0.0101: raise SystemExit(f"2018 {p}: base {media['ideol_18_' + p][0]} × artigo {m}")
print(f"base dos especialistas: {len(resp)} linhas, {n18} de 2018 e {n22} de 2022; médias de 2022 iguais à Tabela 1 do artigo nos {len(TAB22)} partidos; 2018 igual ao artigo da Dados (até 0,01)")

zp = {}
with open(ZP, encoding="utf-8", newline="") as f:
    for x in csv.DictReader(f):
        if x["year"] == "2021": zp[x["party.or.pres"]] = float(x["ideo"])

vp = json.load(open(VOTOS, encoding="utf-8"))
if set(vp["partidos"]) != set(MAPA): raise SystemExit(f"partidos diferentes do mapa: {sorted(set(vp['partidos']) ^ set(MAPA), key=int)}")
pos, pos18, linhas = {}, {}, []
for num in sorted(MAPA, key=int):
    rg, cols, txt, rg18, cols18, txt18, cz = MAPA[num]
    pt = vp["partidos"][num]
    p22 = r2(st.mean(media["ideol_22_" + c][0] for c in cols)) if cols else None
    p18 = r2(st.mean(media["ideol_18_" + c][0] for c in cols18)) if cols18 else None
    z = st.mean(zp[c] for c in cz) if cz and all(c in zp for c in cz) else None
    pos[num], pos18[num] = p22, p18
    um = len(cols) == 1
    cat = TAB22[cols[0]][1] if um else (categoria(p22) if p22 is not None else "")
    fed = vp["federacoes"][pt["fed"]]["sg"] if pt["fed"] else ""
    linhas.append({
        "numero": num, "sigla": pt["sg"], "nome": pt["nm"], "federacao_2026": fed,
        "posicao": "" if p22 is None else f"{p22:.2f}", "categoria": cat,
        "campo_esquerda": "" if p22 is None else ("sim" if p22 <= CORTE else "não"),
        "regra": rg, "regra_explicada": f"{REGRAS[rg]}. {txt}", "sigla_na_pesquisa": " + ".join(c.upper() for c in cols),
        "especialistas": media["ideol_22_" + cols[0]][1] if um else "", "desvio_padrao": f"{media['ideol_22_' + cols[0]][2]:.2f}" if um else "",
        "fonte": FONTE if p22 is not None else "sem posição na fonte",
        "conf_2018_posicao": "" if p18 is None else f"{p18:.2f}", "conf_2018_campo_esquerda": "" if p18 is None else ("sim" if p18 <= CORTE else "não"),
        "conf_2018_regra": rg18, "conf_2018_explicada": f"{REGRAS[rg18]}. {txt18}",
        "conf_zucco_power_2021": "" if z is None else f"{z:.3f}",
    })
with open(OUT_ESC, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(linhas[0])); w.writeheader(); w.writerows(linhas)
esq = {k for k, v in pos.items() if v is not None and v <= CORTE}
esq18 = {k for k, v in pos18.items() if v is not None and v <= CORTE}
sig = lambda ks: ", ".join(vp["partidos"][k]["sg"] for k in sorted(ks, key=lambda k: pos[k] if pos[k] is not None else 99))
print(f"\n{OUT_ESC}: {len(linhas)} partidos, {sum(v is not None for v in pos.values())} com posição; sem posição: {sig(k for k, v in pos.items() if v is None)}")
for l in linhas: print(f"  {l['numero']:>3} {l['sigla']:14s} {l['posicao']:>5} {l['categoria']:17s} {l['campo_esquerda']:4s} {l['regra']}  2018: {l['conf_2018_posicao']:>5} {l['conf_2018_campo_esquerda']:4s} ZP: {l['conf_zucco_power_2021']}")
print(f"campo da esquerda (até {CORTE}): {len(esq)} partidos: {sig(esq)}")
fora = sorted((v, k) for k, v in pos.items() if v is not None and v > CORTE)[0]
dentro = sorted((v, k) for k, v in pos.items() if v is not None and v <= CORTE)[-1]
print(f"  último dentro: {vp['partidos'][dentro[1]]['sg']} {dentro[0]}; primeiro fora: {vp['partidos'][fora[1]]['sg']} {fora[0]}")
print(f"campo da esquerda na conferência de 2018: {len(esq18)} partidos: {sig(esq18)}; mudam de lado: {sig(esq ^ esq18)}")
for fd, fi in vp["federacoes"].items():
    lados = {k in esq for k in fi["partidos"]}
    print(f"  federação {fi['sg']}: {'mesmo lado do corte' if len(lados) == 1 else 'PARTIDOS DOS DOIS LADOS'}")
c18 = [k for k in pos if pos[k] is not None and pos18[k] is not None]
zpv = {l["numero"]: float(l["conf_zucco_power_2021"]) for l in linhas if l["conf_zucco_power_2021"]}
czp = [k for k in zpv if pos[k] is not None]
print(f"Spearman 2022 × 2018: {spearman([pos[k] for k in c18], [pos18[k] for k in c18]):.3f} ({len(c18)} partidos); "
      f"2022 × Zucco e Power 2021: {spearman([pos[k] for k in czp], [zpv[k] for k in czp]):.3f} ({len(czp)} partidos)")
print("  ordem em Zucco e Power 2021:", ", ".join(f"{vp['partidos'][k]['sg']} {zpv[k]:+.2f}" for k in sorted(czp, key=lambda k: zpv[k])))

# --- 2. medidas por município × cargo, estado e Brasil (sem 2º turno) ---
b1 = json.load(open(BASE1T, encoding="utf-8"))
def medidas(c, pz, ez):
    v = {k: n + l for k, (n, l) in c["p"].items()}
    vv = c["vv"]
    if sum(v.values()) != vv: raise SystemExit("soma dos partidos diferente de vv")
    e = sum(x for k, x in v.items() if k in ez)
    sp = sum(x for k, x in v.items() if pz[k] is None)
    esc = sum(pz[k] * x for k, x in v.items() if pz[k] is not None) / (vv - sp) if vv - sp else None
    return vv, e, sp, esc
def pct(a, b): return 100 * a / b if b else None
def fmt(x, d=4): return "" if x is None else f"{x:.{d}f}"
def linha(nivel, cd, uf, nm, cg, c, L, F):
    vv, e, sp, esc = medidas(c, pos, esq)
    sj = c.get("sj", {})
    cs = {"vv": vv + sum(sj.values()), "p": {k: [n + sj.get(k, 0), l] for k, (n, l) in c["p"].items()}}
    for k, x in sj.items(): cs["p"].setdefault(k, [x, 0])
    vs, es, ss, escs = medidas(cs, pos, esq)
    v18, e18, sp18, esc18 = medidas(c, pos18, esq18)
    s1 = pct(L, L + F)
    pe, pes, pe18 = pct(e, vv), pct(es, vs), pct(e18, v18)
    return {"nivel": nivel, "cd": cd, "uf": uf, "nm": nm, "cargo": cg, "cargo_nome": CARGOS[cg],
            "vv": vv, "esq": e, "pct_esq": fmt(pe), "sem_posicao": sp, "pct_sem_posicao": fmt(pct(sp, vv)), "escala": fmt(esc),
            "lula_1t": int(L), "flavio_1t": int(F), "fatia_lula_1t": fmt(s1), "vantagem": fmt(None if pe is None else pe - s1),
            "sj": sum(sj.values()), "sj_esq": es - e, "pct_esq_com_sj": fmt(pes), "escala_com_sj": fmt(escs), "vantagem_com_sj": fmt(None if pes is None else pes - s1),
            "conf_2018_pct_esq": fmt(pe18), "conf_2018_sem_posicao": sp18, "conf_2018_escala": fmt(esc18), "conf_2018_vantagem": fmt(None if pe18 is None else pe18 - s1)}
out, falta = [], set(vp["mu"]) - set(b1["mu"])
if falta: raise SystemExit(f"municípios sem 1º turno de presidente: {sorted(falta)[:5]}")
agr = {}
for cd, m in sorted(vp["mu"].items()):
    p1 = b1["mu"][cd]
    for cg in CARGOS:
        if cg in m["c"]:
            out.append(linha("mu", cd, m["uf"], m["nm"], cg, m["c"][cg], p1["L"], p1["F"]))
            for chave in ((m["uf"], cg), ("br", cg)):
                a = agr.setdefault(chave, [0, 0]); a[0] += p1["L"]; a[1] += p1["F"]
for u in sorted(vp["uf"]):
    for cg in CARGOS:
        if cg in vp["uf"][u]: out.append(linha("uf", "", u, u.upper(), cg, vp["uf"][u][cg], *agr[(u, cg)]))
for cg in CARGOS: out.append(linha("br", "", "", "BRASIL", cg, vp["br"][cg], *agr[("br", cg)]))
for u in sorted(vp["uf"]):  # a fatia do estado, somada dos municípios, tem de bater com o arquivo do estado
    if (agr[(u, "6")][0], agr[(u, "6")][1]) != (b1["uf"][u]["L"], b1["uf"][u]["F"]): raise SystemExit(f"Lula/Flávio de {u} não batem com a base do 1º turno")
with open(OUT_MED, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
mus = [r for r in out if r["nivel"] == "mu"]
print(f"\n{OUT_MED}: {len(out)} linhas ({len(mus)} município × cargo, {sum(r['nivel'] == 'uf' for r in out)} estado × cargo, {sum(r['nivel'] == 'br' for r in out)} Brasil)")
for cg in CARGOS:
    br = next(r for r in out if r["nivel"] == "br" and r["cargo"] == cg)
    ms = [r for r in mus if r["cargo"] == cg]
    vazios = sum(r["pct_esq"] == "" for r in ms)
    ok = [r for r in ms if r["pct_esq"] and r["conf_2018_pct_esq"]]
    rr = pearson([float(r["pct_esq"]) for r in ok], [float(r["conf_2018_pct_esq"]) for r in ok]) if len(ok) > 2 else float("nan")
    re_ = pearson([float(r["pct_esq"]) for r in ok], [float(r["escala"]) for r in ok]) if len(ok) > 2 else float("nan")
    msp = max(ms, key=lambda r: float(r["pct_sem_posicao"] or 0))
    print(f"  {CARGOS[cg]:18s} municípios {len(ms):5d} (sem válidos: {vazios}); Brasil: válidos {br['vv']:,}, % esquerda {br['pct_esq']}, escala {br['escala']}, "
          f"sem posição {br['pct_sem_posicao']}%, com sub judice {br['pct_esq_com_sj']}, conferência 2018 {br['conf_2018_pct_esq']}".replace(",", "."))
    print(f"  {'':18s} municípios: correlação % esquerda × conferência 2018 {rr:.3f}; % esquerda × escala {re_:.3f}; "
          f"maior fatia sem posição {msp['pct_sem_posicao']}% ({msp['nm']}-{msp['uf'].upper()})")
