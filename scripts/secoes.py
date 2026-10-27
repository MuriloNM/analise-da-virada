# T27: resultado de presidente por seção eleitoral nos dois turnos, a partir dos arquivos do caminho B (P11, D54),
# lidos direto dos zips em dados/tse_secoes/ (baixados por secoes_baixar.py), sem extrair:
#   - detalhe_votacao_secao_2026.zip, só o _BR.csv (presidente): aptos, comparecimento, brancos, nulos e nominais, nos dois turnos;
#   - votacao_secao_2026_BR.zip: votos de cada candidato a presidente por seção, 1º turno;
#   - bweb_2t_{UF}_261020260742.zip: boletins de urna do 2º turno (Lula, Flávio, brancos, nulos, aptos, comparecimento, seções agregadas).
# Confere as fontes entre si, seção a seção, e a soma das seções com as bases municipais
# (base_1t_municipios.json e base_2t_municipios.json), em todos os campos; casa as seções entre os turnos.
# Saídas: dados/secoes_presidente.csv.gz (uma linha por seção) e dados/secoes_presidente_meta.json (campos e conferências).
# Uso: python -I scripts/secoes.py
import os, io, csv, json, gzip, glob, zipfile, collections
AQUI = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(AQUI, "..", "dados")
SEC = os.path.join(DADOS, "tse_secoes")
ANULADO = "28"  # candidato a presidente com votos anulados: no resultado oficial, contam como nulos (nota N21)

def linhas(zp, nome=None):
    z = zipfile.ZipFile(zp)
    nome = nome or [n for n in z.namelist() if n.endswith(".csv")][0]
    r = csv.reader(io.TextIOWrapper(z.open(nome), encoding="latin-1"), delimiter=";")
    h = next(r); ix = {c: i for i, c in enumerate(h)}
    for row in r: yield lambda c, row=row: row[ix[c]]

def chave(g, cargo_mun="CD_MUNICIPIO"):
    return (g("SG_UF"), g(cargo_mun).zfill(5), int(g("NR_ZONA")), int(g("NR_SECAO")))

# 1. Detalhe (os dois turnos)
det = {1: {}, 2: {}}
for g in linhas(os.path.join(SEC, "detalhe_votacao_secao_2026.zip"), "detalhe_votacao_secao_2026_BR.csv"):
    assert g("CD_CARGO") == "1"
    t = int(g("NR_TURNO")); k = chave(g)
    assert k not in det[t]
    det[t][k] = dict(aptos=int(g("QT_APTOS")), comp=int(g("QT_COMPARECIMENTO")), abst=int(g("QT_ABSTENCOES")),
                     nom=int(g("QT_VOTOS_NOMINAIS")), br=int(g("QT_VOTOS_BRANCOS")), nu=int(g("QT_VOTOS_NULOS")),
                     leg=int(g("QT_VOTOS_LEGENDA")), anul_sep=int(g("QT_VOTOS_ANULADOS_APU_SEP")),
                     inst=g("ST_SECAO_INSTALADA") == "Sim", anulada=g("ST_SECAO_ANULADA") != "Não", origem=g("DS_ORIGEM_VOTO"))

# 2. Votação por seção, 1º turno
v1 = collections.defaultdict(collections.Counter); cands = set()
for g in linhas(os.path.join(SEC, "votacao_secao_2026_BR.zip")):
    assert g("NR_TURNO") == "1" and g("CD_CARGO") == "1"
    k = chave(g); n = g("NR_VOTAVEL")
    assert n not in v1[k]
    v1[k][n] = int(g("QT_VOTOS")); cands.add(n)
cands = sorted(c for c in cands if c not in ("95", "96"))

# 3. Boletins de urna, 2º turno
bu = {}
for zp in sorted(glob.glob(os.path.join(SEC, "bweb_2t_*_261020260742.zip"))):
    for g in linhas(zp):
        if g("CD_CARGO_PERGUNTA") != "1": continue
        assert g("NR_TURNO") == "2" and g("DS_TIPO_URNA") == "Apurada"
        k = chave(g)
        s = bu.setdefault(k, dict(aptos=int(g("QT_APTOS")), comp=int(g("QT_COMPARECIMENTO")), v=collections.Counter(),
                                  agreg=g("DS_SECOES_AGREGADAS") if g("DS_SECOES_AGREGADAS") != "#NULO#" else ""))
        assert (s["aptos"], s["comp"]) == (int(g("QT_APTOS")), int(g("QT_COMPARECIMENTO")))
        n = g("NR_VOTAVEL"); assert n in ("13", "22", "95", "96") and n not in s["v"]
        s["v"][n] = int(g("QT_VOTOS"))

conf = collections.OrderedDict()
def dif(nome, pares):
    """pares: iterável de (chave, a, b); guarda quantas diferem e até 5 exemplos."""
    d = [(k, a, b) for k, a, b in pares if a != b]
    conf[nome] = {"diferentes": len(d), "exemplos": [[list(k), a, b] for k, a, b in d[:5]]}

# 4. Conferências entre fontes, seção a seção
inst1 = {k for k, s in det[1].items() if s["inst"]}
inst2 = {k for k, s in det[2].items() if s["inst"]}
conf["secoes"] = {"detalhe_1t": len(det[1]), "detalhe_1t_instaladas": len(inst1), "detalhe_2t": len(det[2]),
                  "detalhe_2t_instaladas": len(inst2), "votacao_secao_1t": len(v1), "bweb_2t": len(bu)}
dif("1t: seções da votação por seção que não estão instaladas no detalhe", ((k, True, k in inst1) for k in v1))
dif("1t: seções instaladas do detalhe sem linha na votação por seção (com comparecimento > 0)",
    ((k, True, k in v1) for k in inst1 if det[1][k]["comp"] > 0))
dif("1t: brancos, detalhe × votação por seção", ((k, s["br"], v1[k]["95"]) for k, s in det[1].items() if k in v1))
dif("1t: nulos, detalhe × votação por seção", ((k, s["nu"], v1[k]["96"]) for k, s in det[1].items() if k in v1))
dif("1t: nominais, detalhe × soma dos candidatos (com o 28)",
    ((k, s["nom"], sum(v for n, v in v1[k].items() if n not in ("95", "96"))) for k, s in det[1].items() if k in v1))
dif("1t: comparecimento = nominais + brancos + nulos (detalhe)",
    ((k, s["comp"], s["nom"] + s["br"] + s["nu"] + s["leg"] + s["anul_sep"]) for k, s in det[1].items()))
dif("2t: seções do bweb × instaladas no detalhe", ((k, True, k in inst2) for k in bu))
dif("2t: instaladas do detalhe sem boletim (com comparecimento > 0)", ((k, True, k in bu) for k in inst2 if det[2][k]["comp"] > 0))
for campo, f in (("aptos", lambda s: s["aptos"]), ("comparecimento", lambda s: s["comp"]),
                 ("brancos", lambda s: s["v"]["95"]), ("nulos", lambda s: s["v"]["96"]), ("nominais", lambda s: s["v"]["13"] + s["v"]["22"])):
    cd = {"aptos": "aptos", "comparecimento": "comp", "brancos": "br", "nulos": "nu", "nominais": "nom"}[campo]
    dif(f"2t: {campo}, bweb × detalhe", ((k, f(s), det[2][k][cd]) for k, s in bu.items() if k in det[2]))
dif("2t: comparecimento = nominais + brancos + nulos (detalhe)",
    ((k, s["comp"], s["nom"] + s["br"] + s["nu"] + s["leg"] + s["anul_sep"]) for k, s in det[2].items()))
dif("aptos = comparecimento + abstenções (detalhe, 1t)", ((k, s["aptos"], s["comp"] + s["abst"]) for k, s in det[1].items()))
dif("aptos = comparecimento + abstenções (detalhe, 2t)", ((k, s["aptos"], s["comp"] + s["abst"]) for k, s in det[2].items()))
conf["seções anuladas (detalhe)"] = {"1t": sum(s["anulada"] for s in det[1].values()), "2t": sum(s["anulada"] for s in det[2].values())}
conf["votos anulados em separado ou de legenda (detalhe)"] = {t: sum(s["anul_sep"] + s["leg"] for s in det[t].values()) for t in (1, 2)}
conf["origem do voto (detalhe)"] = {t: dict(collections.Counter(s["origem"] for s in det[t].values())) for t in (1, 2)}

# 5. Tabela por seção
todas = sorted(set(det[1]) | set(det[2]))
CAMPOS = (["uf", "cd_mun", "zona", "secao", "t1_instalada", "t1_aptos", "t1_comp", "t1_brancos", "t1_nulos"]
          + [f"t1_{c}" for c in cands] + ["t2_instalada", "t2_aptos", "t2_comp", "t2_brancos", "t2_nulos", "t2_13", "t2_22", "t2_agregadas"])
linhas_out = []
for k in todas:
    a, b, v, w = det[1].get(k), det[2].get(k), v1.get(k, collections.Counter()), bu.get(k)
    lin = list(k)
    lin += [int(a["inst"]), a["aptos"], a["comp"], a["br"], a["nu"]] if a else ["", "", "", "", ""]
    lin += [v[c] if a else "" for c in cands]
    lin += [int(b["inst"]), b["aptos"], b["comp"], b["br"], b["nu"]] if b else ["", "", "", "", ""]
    lin += [w["v"]["13"], w["v"]["22"], w["agreg"]] if w else ([0, 0, ""] if b else ["", "", ""])
    linhas_out.append(lin)
with gzip.open(os.path.join(DADOS, "secoes_presidente.csv.gz"), "wt", encoding="utf-8", newline="") as f:
    wr = csv.writer(f); wr.writerow(CAMPOS); wr.writerows(linhas_out)

# 6. Soma das seções × bases municipais
b1 = json.load(open(os.path.join(DADOS, "base_1t_municipios.json"), encoding="utf-8"))["mu"]
b2 = json.load(open(os.path.join(DADOS, "base_2t_municipios.json"), encoding="utf-8"))["mu"]
s1 = collections.defaultdict(collections.Counter); s2 = collections.defaultdict(collections.Counter)
for k, s in det[1].items():
    m = s1[k[1]]; v = v1.get(k, collections.Counter())
    m["te"] += s["aptos"]; m["c"] += s["comp"]; m["L"] += v["13"]; m["F"] += v["22"]
    m["vv"] += sum(x for n, x in v.items() if n not in ("95", "96", ANULADO)); m["bn"] += s["br"] + s["nu"] + v[ANULADO]
for k, s in det[2].items():
    m = s2[k[1]]; w = bu.get(k)
    m["te"] += s["aptos"]; m["c"] += s["comp"]; m["vb"] += s["br"]; m["tvn"] += s["nu"]
    if w: m["L"] += w["v"]["13"]; m["F"] += w["v"]["22"]; m["vv"] += w["v"]["13"] + w["v"]["22"]
def compara(nome, base, soma, campos):
    mun = set(base) | set(soma)
    res = {"municipios_base": len(base), "municipios_secoes": len(soma), "so_na_base": sorted(set(base) - set(soma))[:10],
           "so_nas_secoes": sorted(set(soma) - set(base))[:10]}
    for c in campos:
        d = [m for m in mun if round(base.get(m, {}).get(c, 0)) != soma.get(m, {}).get(c, 0)]
        res[c] = {"municipios_diferentes": len(d), "soma_base": round(sum(base[m].get(c, 0) for m in base)),
                  "soma_secoes": sum(soma[m][c] for m in soma), "exemplos": [[m, base.get(m, {}).get(c), soma.get(m, {}).get(c)] for m in sorted(d)[:5]]}
    conf[nome] = res
for m in b1.values(): m["bn"] = m["c"] - m["vv"]
compara("1t: soma das seções × base_1t_municipios.json", b1, s1, ["te", "c", "vv", "L", "F", "bn"])
compara("2t: soma das seções × base_2t_municipios.json", b2, s2, ["te", "c", "vv", "L", "F", "vb", "tvn"])

# 7. Casamento das seções entre os turnos
so1 = [k for k in todas if k in inst1 and k not in inst2]; so2 = [k for k in todas if k in inst2 and k not in inst1]
agreg2 = {k: w["agreg"] for k, w in bu.items() if w["agreg"]}
conf["casamento"] = {
    "instaladas_nos_dois": len(inst1 & inst2), "so_no_1t": len(so1), "so_no_2t": len(so2),
    "exemplos_so_no_1t": [list(k) for k in so1[:10]], "exemplos_so_no_2t": [list(k) for k in so2[:10]],
    "nao_instaladas_nos_dois": len((set(det[1]) - inst1) & (set(det[2]) - inst2)),
    "2t_secoes_que_recebem_agregadas": len(agreg2),
    "2t_secoes_agregadas": sum(len(a.split("/")) for a in agreg2.values()),
    "aptos_iguais_nos_dois": sum(det[1][k]["aptos"] == det[2][k]["aptos"] for k in inst1 & inst2),
    "aptos_diferenca_absoluta_total": sum(abs(det[1][k]["aptos"] - det[2][k]["aptos"]) for k in inst1 & inst2),
    "aptos_diferenca_maior": max(abs(det[1][k]["aptos"] - det[2][k]["aptos"]) for k in inst1 & inst2),
    "aptos_diferenca_ate_5": sum(0 < abs(det[1][k]["aptos"] - det[2][k]["aptos"]) <= 5 for k in inst1 & inst2),
    "agregadas_que_aparecem_como_secao": sum((k[0], k[1], k[2], int(x)) in det[2] for k, a in agreg2.items() for x in a.split("/")),
}
meta = {"fonte": "TSE, dados abertos e boletins de urna (registro de fontes do T12, linhas do T27)",
        "gerado_por": "scripts/secoes.py", "campos": CAMPOS, "linhas": len(linhas_out), "candidatos_1t": cands,
        "notas": "t1_* do detalhe da apuração por seção (aptos, comparecimento, brancos, nulos) e da votação por seção (votos de cada candidato); "
                 "t2_* do detalhe (aptos, comparecimento, brancos, nulos) e dos boletins de urna (13, 22, seções agregadas). "
                 "t1_nulos é o voto nulo da urna; t1_28 são os votos do candidato 28, anulados: o detalhe do TSE os conta nos nominais, e o resultado oficial, fora dos válidos (válidos = soma dos candidatos sem o 28; brancos + nulos oficiais = t1_brancos + t1_nulos + t1_28; nota N21). "
                 "Vazio: seção que não existe no turno. Código do município do TSE, com 5 dígitos; ZZ é o exterior.",
        "conferencias": conf}
json.dump(meta, open(os.path.join(DADOS, "secoes_presidente_meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(conf, ensure_ascii=False, indent=1))
