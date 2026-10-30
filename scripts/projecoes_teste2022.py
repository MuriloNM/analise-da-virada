# T41, Parte 3: teste limpo em 2022. Os métodos de 2026 (a, b, c, d) e a média (m), sem mudar nada, no 2º turno de 2022:
# presidente e governador nas 12 UFs com 2º turno. Ordem de chegada pela hora de recebimento do boletim (bweb_2t de 2022).
# 1º turno por seção: votacao_secao_2022_{BR,UF}.zip; eleitorado e comparecimento do 1º turno: detalhe_votacao_secao_2022.zip.
# Regras: ticket T41, "Teste limpo em 2022". Uso: python -I scripts/projecoes_teste2022.py   (grava em dados/projecoes_outras/)
import os, sys, io, csv, glob, json, zipfile, collections
import numpy as np
from scipy import sparse
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import reconstrucao_2t as rc, projecoes_2t as p2
DADOS = os.path.join(AQUI, "..", "dados"); T22 = os.path.join(DADOS, "tse_2022"); SAI = os.path.join(DADOS, "projecoes_outras")
UFS_GOV = ["AL", "AM", "BA", "ES", "MS", "PB", "PE", "RO", "RS", "SC", "SE", "SP"]

def ler_zip(zp, so=None):
    z = zipfile.ZipFile(zp)
    for n in z.namelist():
        if not n.lower().endswith(".csv") or (so and so not in n): continue
        f = io.TextIOWrapper(z.open(n), encoding="latin-1"); r = csv.reader(f, delimiter=";"); h = next(r)
        ix = {c.replace(" ", ""): i for i, c in enumerate(h)}
        for q in r: yield lambda c, q=q: q[ix[c]]

def chave(g): return (g("SG_UF").lower(), g("CD_MUNICIPIO").zfill(5), g("NR_ZONA"), g("NR_SECAO"))

def carregar_bweb(cargo):
    """2º turno de 2022: por seção, hora de recebimento, aptos e votos de cada candidato do cargo."""
    bu = {}
    for zp in sorted(glob.glob(os.path.join(T22, "bweb_2t_*_311020221535.zip"))):
        for g in ler_zip(zp):
            if g("CD_CARGO_PERGUNTA") != cargo: continue
            k = chave(g)
            s = bu.setdefault(k, dict(t=rc.seg(g("DT_BU_RECEBIDO")), aptos=int(g("QT_APTOS")), v={}))
            if g("CD_TIPO_VOTAVEL") == "1": s["v"][g("NR_VOTAVEL")] = s["v"].get(g("NR_VOTAVEL"), 0) + int(g("QT_VOTOS"))
    return bu

def carregar_detalhe():
    """1º turno de 2022: aptos e comparecimento por seção (cargo presidente; os eleitores são os mesmos em todos os cargos)."""
    d = {}
    for g in ler_zip(os.path.join(T22, "detalhe_votacao_secao_2022.zip"), so="BR"):
        if g("NR_TURNO") != "1" or g("CD_CARGO") != "1": continue
        d[chave(g)] = (int(g("QT_APTOS")), int(g("QT_COMPARECIMENTO")))
    return d

def carregar_1t(zp, cargo):
    v1 = collections.defaultdict(collections.Counter)
    for g in ler_zip(zp):
        if g("CD_CARGO") != cargo or g("NR_TURNO") != "1": continue
        v1[chave(g)][g("NR_VOTAVEL")] += int(g("QT_VOTOS"))
    return v1

def montar(nome, bu, v1, det):
    cand2 = collections.Counter()
    for s in bu.values():
        for c, q in s["v"].items(): cand2[c] += q
    A, B = sorted(cand2, key=lambda c: -cand2[c])[:2]
    tot1 = collections.Counter()
    for v in v1.values(): tot1.update(v)
    val = sum(v for c, v in tot1.items() if c not in ("95", "96"))
    grandes = sorted(c for c, v in tot1.items() if c not in ("95", "96", B) and v >= 0.01 * val)
    todas = sorted(bu, key=lambda k: (bu[k]["t"], k)); N = len(todas)
    f = lambda fn: np.array([fn(k) for k in todas], float)
    ufs = sorted({k[0] for k in todas}); mus = sorted({k[1] for k in todas})
    S = dict(uf=np.searchsorted(ufs, [k[0] for k in todas]), ufs=ufs, mun=np.searchsorted(mus, [k[1] for k in todas]), nmun=len(mus),
             L1=f(lambda k: v1[k][A]), F1=f(lambda k: v1[k][B]),
             comp1=f(lambda k: det.get(k, (0, 0))[1]), aptos1=f(lambda k: det.get(k, (0, 0))[0]), aptos2=f(lambda k: bu[k]["aptos"]),
             L2=f(lambda k: bu[k]["v"].get(A, 0)), F2=f(lambda k: bu[k]["v"].get(B, 0)), t=f(lambda k: bu[k]["t"]))
    outros = f(lambda k: sum(v for c, v in v1[k].items() if c not in grandes and c not in ("95", "96", B)))
    cols = [f(lambda k, c=c: v1[k][c]) for c in grandes] + [outros, f(lambda k: v1[k]["95"]), f(lambda k: v1[k]["96"])]
    comp = S["comp1"]; ok = comp > 0
    feats = [np.where(ok, c / np.where(ok, comp, 1), 0) for c in cols]
    feats.append(np.where(S["aptos1"] > 0, 1 - comp / np.where(S["aptos1"] > 0, S["aptos1"], 1), 0))
    Xb = np.column_stack([np.ones(N)] + feats); Xb[~ok] = Xb[ok].mean(0)
    S["Xb"] = Xb; S["Xc"] = np.hstack([Xb, (S["uf"][:, None] == np.arange(len(ufs))[None, :]).astype(float)])
    S["C"] = sparse.csr_matrix((np.ones(N), (S["mun"], np.arange(N))), shape=(len(mus), N))
    S["pen_c"] = np.r_[0, np.full(Xb.shape[1] - 1, 1e-6 * N), np.full(len(ufs), p2.PEN_UF)]
    # (a): a conta da página: os 300 maiores municípios da área e o resto de cada UF em bloco
    secs = [dict(uf=k[0], mun=k[1], aptos=bu[k]["aptos"], L=bu[k]["v"].get(A, 0), F=bu[k]["v"].get(B, 0)) for k in todas]
    te_mu = collections.Counter(); te_uf = collections.Counter(); ns = collections.Counter(); muf = {}
    for k in todas: te_mu[k[1]] += bu[k]["aptos"]; te_uf[k[0]] += bu[k]["aptos"]; ns[k[0]] += 1; muf[k[1]] = k[0]
    m1 = collections.defaultdict(lambda: [0, 0]); u1 = collections.defaultdict(lambda: [0, 0])
    for k, v in v1.items():
        if k[1] in te_mu: m1[k[1]][0] += v[A]; m1[k[1]][1] += v[B]
        if k[0] in te_uf: u1[k[0]][0] += v[A]; u1[k[0]][1] += v[B]
    top = sorted(te_mu, key=lambda m: -te_mu[m])[:300]
    base = dict(uf={u: dict(L=u1[u][0], F=u1[u][1]) for u in ufs}, mu=[[m, muf[m], m, te_mu[m], m1[m][0], m1[m][1]] for m in top])
    tot = dict(secoes=dict(ns), te_uf=dict(te_uf), te_mu=dict(te_mu))
    info = dict(disputa=nome, A=A, B=B, grandes=grandes, secoes=N, com_boletim=int(np.isfinite(S["t"]).sum()),
                sem_1t=sum(k not in v1 for k in todas), sem_detalhe=sum(k not in det for k in todas))
    return S, secs, base, tot, info

def avaliar(S, secs, base, tot, info):
    nrec = info["com_boletim"]; final = 100 * p2.share(S["L2"][:nrec].sum(), S["F2"][:nrec].sum())
    est = rc.Estado(tot, base); j = 0; L = []
    for k in range(1, 200):
        n = min(max(1, -int(-k / 2 * info["secoes"] // 100)), nrec)
        while est.n < n: est.add(secs[j]); j += 1
        vol = p2.volume(S, n); c = p2.metodo_c(S, n, vol); dd, _ = p2.metodo_d(S, n, vol)
        d = dict(disputa=info["disputa"], pst=k / 2, hora=rc.hms(S["t"][n - 1]), n=n, contagem=100 * p2.share(S["L2"][:n].sum(), S["F2"][:n].sum()),
                 a=est.conta()["proj"], b=100 * p2.metodo_b(S, n), c=100 * c[0], c_lo=100 * c[1], c_hi=100 * c[2],
                 d=100 * dd[0], d_lo=100 * dd[1], d_hi=100 * dd[2], final=final)
        d["m"] = (d["b"] + d["c"] + d["d"]) / 3
        L.append(d)
    lado = (lambda v: v > 50) if final > 50 else (lambda v: v < 50)
    R = dict(info, final=round(final, 3), metodos={})
    for m in ("contagem", "a", "b", "c", "d", "m"):
        e = [abs(d[m] - final) for d in L]
        ac = [lado(d[m]) and abs(d[m] - final) <= 0.5 for d in L]; k = next((i for i in range(len(L)) if all(ac[i:])), None)
        x = dict(abs_medio=round(sum(e) / len(e), 3), max_abs=round(max(e), 3), passa_a_acertar=None if k is None else L[k]["pst"])
        if m in ("c", "d"): x["cobre"] = int(sum(d[m + "_lo"] <= final <= d[m + "_hi"] for d in L))
        R["metodos"][m] = x
    conc = [len({lado(d[m]) for m in "bcd"}) == 1 for d in L]; k = next((i for i in range(len(L)) if all(conc[i:])), None)
    R["concordam"] = dict(instantes=sum(conc), desde=None if k is None else L[k]["pst"],
                          concordando_e_errando=sum(c and not lado(d["b"]) for c, d in zip(conc, L)))
    return L, R

def main():
    det = carregar_detalhe(); print("detalhe", len(det), flush=True)
    os.makedirs(SAI, exist_ok=True); linhas, resumo = [], {}
    tarefas = [("presidente_2022", "1", os.path.join(T22, "votacao_secao_2022_BR.zip"), None)]
    tarefas += [(f"governador_2022_{uf}", "3", os.path.join(T22, f"votacao_secao_2022_{uf}.zip"), uf.lower()) for uf in UFS_GOV]
    bu_pres = carregar_bweb("1"); bu_gov = carregar_bweb("3")
    for nome, cargo, zp, uf in tarefas:
        bu = bu_pres if cargo == "1" else {k: v for k, v in bu_gov.items() if k[0] == uf}
        v1 = carregar_1t(zp, cargo)
        L, R = avaliar(*montar(nome, bu, v1, det))
        linhas += L; resumo[nome] = R
        print(nome, R["A"], R["B"], R["final"], {m: (x["abs_medio"], x["passa_a_acertar"]) for m, x in R["metodos"].items()},
              R["concordam"], "sem 1t:", R["sem_1t"], "sem detalhe:", R["sem_detalhe"], flush=True)
    cab = ["disputa", "pst", "hora", "n", "contagem", "a", "b", "c", "c_lo", "c_hi", "d", "d_lo", "d_hi", "m", "final"]
    with open(os.path.join(SAI, "teste2022_instantes.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";"); w.writerow(cab)
        for d in linhas: w.writerow([round(d[k], 4) if isinstance(d[k], float) else d[k] for k in cab])
    ms = ("a", "b", "c", "d", "m")
    resumo["_total"] = dict(abs_medio={m: round(float(np.mean([r["metodos"][m]["abs_medio"] for r in resumo.values()])), 3) for m in ms},
                            melhor={m: sum(min(ms, key=lambda x: r["metodos"][x]["abs_medio"]) == m for r in resumo.values()) for m in ms},
                            m_melhor_que={x: sum(r["metodos"]["m"]["abs_medio"] < r["metodos"][x]["abs_medio"] for r in resumo.values()) for x in "bcd"},
                            concordando_e_errando=sum(r["concordam"]["concordando_e_errando"] for r in resumo.values()))
    json.dump(resumo, open(os.path.join(SAI, "teste2022_resumo.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=lambda o: o.item())
    print(json.dumps(resumo["_total"], ensure_ascii=False, indent=1, default=lambda o: o.item()))

if __name__ == "__main__":
    main()
