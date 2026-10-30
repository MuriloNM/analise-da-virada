# T41, exploração: a regra de chamada no senador (1º turno). Os métodos (b), (c) e (d) de projecoes_2t.py, sem mudança, com uma base
# de 1º turno: os outros cargos da mesma seção e do mesmo dia (presidente e governador; no (b), o voto do partido do senador para
# governador, senão presidente, senão deputado federal). Ordem de chegada: DT_RECEBIMENTO_BU_HOR_TSE do detalhe da UF.
# 2022: 1º × 2º; 2018 e 2026 (duas vagas): 2º × 3º. Regras: ticket T41, "Senador (1º turno, exploração)".
# Uso: python -I scripts/projecoes_senador.py baixar   (completa as UFs de 2022 e 2018)
#      python -I scripts/projecoes_senador.py          (grava dados/projecoes_outras/senador_*)
import os, sys, io, csv, gzip, json, time, hashlib, zipfile, datetime, collections, urllib.request
import numpy as np
from scipy import sparse
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import reconstrucao_2t as rc, projecoes_2t as p2
DADOS = os.path.join(AQUI, "..", "dados"); SAI = os.path.join(DADOS, "projecoes_outras")
TODAS = ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO"]
ANOS = {2022: dict(pasta="tse_2022", ufs=TODAS, vagas=1), 2018: dict(pasta="tse_2018", ufs=TODAS, vagas=2),
        2026: dict(pasta="tse_secoes_gov", ufs=["AC", "AM", "DF", "ES", "RN", "TO"], vagas=2)}
BRANCO_NULO = ("95", "96", "97")
CDN = "https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_secao"

def baixar():
    for ano in (2022, 2018):
        D = os.path.join(DADOS, ANOS[ano]["pasta"]); reg_p = os.path.join(D, "baixados.json"); reg = json.load(open(reg_p))
        for uf in ANOS[ano]["ufs"]:
            nome = f"votacao_secao_{ano}_{uf}.zip"; p = os.path.join(D, nome); u = f"{CDN}/{nome}"
            if nome in reg and os.path.exists(p) and os.path.getsize(p) == reg[nome]["bytes"]: continue
            for k in range(5):
                try:
                    r = urllib.request.urlopen(u, timeout=600); h = hashlib.sha256(); n = 0
                    with open(p, "wb") as f:
                        while True:
                            b = r.read(1 << 20)
                            if not b: break
                            f.write(b); h.update(b); n += len(b)
                    break
                except Exception as e:
                    print(nome, "erro", e); time.sleep(10 * (k + 1))
            reg[nome] = dict(url=u, baixado_em=datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), bytes=n, modificado=r.headers.get("Last-Modified"), sha256=h.hexdigest())
            json.dump(reg, open(reg_p, "w"), indent=1); print(nome, n, flush=True); time.sleep(1)

def ler_zip(zp, so=None):
    z = zipfile.ZipFile(zp)
    for n in z.namelist():
        if not n.lower().endswith(".csv") or (so and not n.endswith(so)): continue
        f = io.TextIOWrapper(z.open(n), encoding="latin-1"); r = csv.reader(f, delimiter=";"); h = next(r)
        ix = {c.replace(" ", ""): i for i, c in enumerate(h)}
        for q in r: yield lambda c, q=q: q[ix[c]]

def chave(g): return (g("SG_UF").lower(), g("CD_MUNICIPIO").zfill(5), g("NR_ZONA"), g("NR_SECAO"))

def seg_data(h):
    """'dd/mm/aaaa hh:mm:ss' → segundos desde 0h do dia da eleição (o 1º turno passa da meia-noite)."""
    if not h or "/" not in h: return np.inf
    d, t = h.split(" "); dt = datetime.date(int(d[6:10]), int(d[3:5]), int(d[0:2]))
    return dt.toordinal() * 86400 + rc.seg(t)

def detalhe(ano, uf):
    """1º turno, cargo 5: hora de recebimento, aptos e comparecimento por seção."""
    zp = os.path.join(DADOS, "tse_secoes" if ano == 2026 else ANOS[ano]["pasta"], f"detalhe_votacao_secao_{ano}.zip")
    d = {}
    for g in ler_zip(zp, so=f"_{uf}.csv"):
        if g("NR_TURNO") != "1" or g("CD_CARGO") != "5": continue
        d[chave(g)] = (seg_data(g("DT_RECEBIMENTO_BU_HOR_TSE")), int(g("QT_APTOS")), int(g("QT_COMPARECIMENTO")))
    return d

def votos_uf(ano, uf):
    """1º turno por seção na UF: {cargo: {seção: Counter(número → votos)}}, cargos 3 (governador), 5 (senador) e 6 (dep. federal)."""
    v = {c: collections.defaultdict(collections.Counter) for c in ("3", "5", "6")}
    for g in ler_zip(os.path.join(DADOS, ANOS[ano]["pasta"], f"votacao_secao_{ano}_{uf}.zip")):
        c = g("CD_CARGO")
        if c not in v or g("NR_TURNO") != "1": continue
        n = g("NR_VOTAVEL")
        if c == "6" and n not in BRANCO_NULO: n = n[:2]  # dep. federal: voto do partido (nominal + legenda)
        v[c][chave(g)][n] += int(g("QT_VOTOS"))
    return v

def presidente(ano, ufs):
    """1º turno do presidente por seção nas UFs pedidas."""
    p = collections.defaultdict(collections.Counter); ufs = {u.lower() for u in ufs}
    if ano == 2026:
        for r in csv.DictReader(gzip.open(os.path.join(DADOS, "secoes_presidente.csv.gz"), "rt", encoding="utf-8")):
            if r["uf"].lower() not in ufs: continue
            k = (r["uf"].lower(), r["cd_mun"], r["zona"], r["secao"])
            for c, x in r.items():
                if c.startswith("t1_") and c[3:].isdigit() and c != "t1_28": p[k][c[3:]] = int(float(x or 0))
            p[k]["95"] = int(float(r["t1_brancos"] or 0)); p[k]["96"] = int(float(r["t1_nulos"] or 0))
        return p
    for g in ler_zip(os.path.join(DADOS, ANOS[ano]["pasta"], f"votacao_secao_{ano}_BR.zip")):
        if g("CD_CARGO") != "1" or g("NR_TURNO") != "1" or g("SG_UF").lower() not in ufs: continue
        p[chave(g)][g("NR_VOTAVEL")] += int(g("QT_VOTOS"))
    return p

def partes(cargo, todas, comp):
    """Variáveis de um cargo pela regra da Parte 3: candidatos com >= 1% dos válidos da UF menos o mais votado, outros, brancos, nulos."""
    tot = collections.Counter()
    for k in todas: tot.update(cargo.get(k, {}))
    val = {c: v for c, v in tot.items() if c not in BRANCO_NULO}
    if not val: return []
    ref = max(val, key=val.get); s = sum(val.values())
    grandes = sorted(c for c, v in val.items() if c != ref and v >= 0.01 * s)
    f = lambda fn: np.array([fn(k) for k in todas], float)
    cols = [f(lambda k, c=c: cargo.get(k, {}).get(c, 0)) for c in grandes]
    cols.append(f(lambda k: sum(v for c, v in cargo.get(k, {}).items() if c not in grandes and c != ref and c not in BRANCO_NULO)))
    cols += [f(lambda k: cargo.get(k, {}).get("95", 0)), f(lambda k: cargo.get(k, {}).get("96", 0))]
    ok = comp > 0
    return [np.where(ok, c / np.where(ok, comp, 1), 0) for c in cols]

def montar(ano, uf, pres, det):
    v = votos_uf(ano, uf); sen = v["5"]
    tot = collections.Counter()
    for x in sen.values(): tot.update(x)
    cand = sorted((c for c in tot if c not in BRANCO_NULO), key=lambda c: -tot[c])
    A, B = cand[:2] if ANOS[ano]["vagas"] == 1 else cand[1:3]
    # base do (b): o partido do senador para governador, senão presidente, senão deputado federal
    gov_tot = collections.Counter(); pres_tot = collections.Counter()
    for x in v["3"].values(): gov_tot.update(x)
    for k, x in pres.items():
        if k[0] == uf.lower(): pres_tot.update(x)
    def fonte(c):
        pt = c[:2]
        if gov_tot.get(pt): return "governador", v["3"], pt
        if pres_tot.get(pt): return "presidente", pres, pt
        return "deputado federal", v["6"], pt
    fa, fb = fonte(A), fonte(B)
    todas = sorted(sen, key=lambda k: (det.get(k, (np.inf,))[0], k)); N = len(todas)
    f = lambda fn: np.array([fn(k) for k in todas], float)
    ufs = [uf.lower()]; mus = sorted({k[1] for k in todas})
    S = dict(uf=np.zeros(N, int), ufs=ufs, mun=np.searchsorted(mus, [k[1] for k in todas]), nmun=len(mus),
             L1=f(lambda k: fa[1].get(k, {}).get(fa[2], 0)), F1=f(lambda k: fb[1].get(k, {}).get(fb[2], 0)),
             comp1=f(lambda k: det.get(k, (0, 0, 0))[2]), aptos1=f(lambda k: det.get(k, (0, 0, 0))[1]),
             L2=f(lambda k: sen[k][A]), F2=f(lambda k: sen[k][B]), t=f(lambda k: det.get(k, (np.inf,))[0]))
    S["aptos2"] = S["aptos1"]
    comp = S["comp1"]; ok = comp > 0
    feats = partes(pres, todas, comp) + partes(v["3"], todas, comp)
    feats += [np.where(ok, S["L1"] / np.where(ok, comp, 1), 0), np.where(ok, S["F1"] / np.where(ok, comp, 1), 0)]
    feats.append(np.where(S["aptos1"] > 0, 1 - comp / np.where(S["aptos1"] > 0, S["aptos1"], 1), 0))
    Xb = np.column_stack([np.ones(N)] + feats); Xb[~ok] = Xb[ok].mean(0)
    S["Xb"] = Xb; S["Xc"] = np.hstack([Xb, np.ones((N, 1))])
    S["C"] = sparse.csr_matrix((np.ones(N), (S["mun"], np.arange(N))), shape=(len(mus), N))
    S["pen_c"] = np.r_[0, np.full(Xb.shape[1] - 1, 1e-6 * N), p2.PEN_UF]
    info = dict(disputa=f"senador_{ano}_{uf}", ano=ano, uf=uf, vagas=ANOS[ano]["vagas"], A=A, B=B,
                base_A=fa[0], base_B=fb[0], variaveis=Xb.shape[1], secoes=N, com_hora=int(np.isfinite(S["t"]).sum()),
                sem_detalhe=sum(k not in det for k in todas), sem_presidente=sum(k not in pres for k in todas),
                sem_governador=sum(k not in v["3"] for k in todas))
    return S, info

def avaliar(S, info):
    nrec = info["com_hora"]; final = 100 * p2.share(S["L2"][:nrec].sum(), S["F2"][:nrec].sum())
    L = []
    for k in range(1, 200):
        n = min(max(1, -int(-k / 2 * info["secoes"] // 100)), nrec)
        vol = p2.volume(S, n); c = p2.metodo_c(S, n, vol); dd, _ = p2.metodo_d(S, n, vol)
        d = dict(disputa=info["disputa"], pst=k / 2, hora=rc.hms(S["t"][n - 1] % 86400), n=n, contagem=100 * p2.share(S["L2"][:n].sum(), S["F2"][:n].sum()),
                 b=100 * p2.metodo_b(S, n), c=100 * c[0], c_lo=100 * c[1], c_hi=100 * c[2], d=100 * dd[0], d_lo=100 * dd[1], d_hi=100 * dd[2], final=final)
        d["m"] = (d["b"] + d["c"] + d["d"]) / 3
        L.append(d)
    R = dict(info, final=round(final, 3), metodos={})
    for m in ("contagem", "b", "c", "d", "m"):
        e = [abs(d[m] - final) for d in L]
        ac = [d[m] > 50 and abs(d[m] - final) <= 0.5 for d in L]; k = next((i for i in range(len(L)) if all(ac[i:])), None)
        x = dict(abs_medio=round(sum(e) / len(e), 3), max_abs=round(max(e), 3), passa_a_acertar=None if k is None else L[k]["pst"])
        if m in ("c", "d"): x["cobre"] = int(sum(d[m + "_lo"] <= final <= d[m + "_hi"] for d in L))
        R["metodos"][m] = x
    conc = [len({d[m] > 50 for m in "bcd"}) == 1 for d in L]; k = next((i for i in range(len(L)) if all(conc[i:])), None)
    R["concordam"] = dict(instantes=sum(conc), desde=None if k is None else L[k]["pst"], concordando_e_errando=sum(c and not d["b"] > 50 for c, d in zip(conc, L)))
    return L, R

def main():
    os.makedirs(SAI, exist_ok=True); linhas, resumo = [], {}
    cab = ["disputa", "pst", "hora", "n", "contagem", "b", "c", "c_lo", "c_hi", "d", "d_lo", "d_hi", "m", "final"]
    for ano in (2022, 2018, 2026):
        ufs = [u for u in ANOS[ano]["ufs"] if os.path.exists(os.path.join(DADOS, ANOS[ano]["pasta"], f"votacao_secao_{ano}_{u}.zip"))]
        pres = presidente(ano, ufs); print(ano, "presidente", len(pres), flush=True)
        for uf in ufs:
            S, info = montar(ano, uf, pres, detalhe(ano, uf))
            L, R = avaliar(S, info); linhas += L; resumo[info["disputa"]] = R
            print(info["disputa"], R["A"], R["B"], R["base_A"], R["base_B"], R["final"], {m: x["abs_medio"] for m, x in R["metodos"].items()},
                  R["concordam"], "sem hora:", R["secoes"] - R["com_hora"], "sem pres/gov:", R["sem_presidente"], R["sem_governador"], flush=True)
            with open(os.path.join(SAI, "senador_instantes.csv"), "w", encoding="utf-8", newline="") as f:
                w = csv.writer(f, delimiter=";"); w.writerow(cab)
                for d in linhas: w.writerow([round(d[k], 4) if isinstance(d[k], float) else d[k] for k in cab])
    ms = ("b", "c", "d", "m")
    resumo["_total"] = dict(disputas=len(resumo), abs_medio={m: round(float(np.mean([r["metodos"][m]["abs_medio"] for r in resumo.values()])), 3) for m in ms},
                            melhor={m: sum(min(ms, key=lambda x: r["metodos"][x]["abs_medio"]) == m for r in resumo.values()) for m in ms},
                            concordando_e_errando=sum(r["concordam"]["concordando_e_errando"] for r in resumo.values()))
    json.dump(resumo, open(os.path.join(SAI, "senador_resumo.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=lambda o: o.item())
    print(json.dumps(resumo["_total"], ensure_ascii=False, indent=1, default=lambda o: o.item()))

if __name__ == "__main__":
    baixar() if sys.argv[1:] == ["baixar"] else main()
