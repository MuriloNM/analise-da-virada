# T41, Parte 3: os métodos da Parte 2 (scripts/projecoes_2t.py), sem mudar nada, no 2º turno de governador de 2026 (AC, AM, DF, ES, RN, TO).
# 2º turno: bweb_2t (cargo 3, hora de recebimento). 1º turno por seção: votacao_secao_2026_{UF}.zip (dados/tse_secoes_gov/);
# eleitorado e comparecimento do 1º turno da seção: secoes_presidente.csv.gz (os mesmos eleitores).
# Regras: docs/analise/tickets/T41-reconstrucao-apuracao.md, "Parte 3". Uso: python -I scripts/projecoes_governador.py
import os, sys, io, csv, glob, gzip, json, zipfile, collections
import numpy as np
from scipy import sparse
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import reconstrucao_2t as rc, projecoes_2t as p2
DADOS = os.path.join(AQUI, "..", "dados"); SAI = os.path.join(DADOS, "projecoes_outras")
UFS = ["AC", "AM", "DF", "ES", "RN", "TO"]

def ler_zip(zp):
    z = zipfile.ZipFile(zp); n = [x for x in z.namelist() if x.lower().endswith(".csv")][0]
    f = io.TextIOWrapper(z.open(n), encoding="latin-1"); r = csv.reader(f, delimiter=";"); h = next(r)
    ix = {c: i for i, c in enumerate(h)}
    for q in r: yield lambda c, q=q: q[ix[c]]

def disputa(uf, pres):
    # 2º turno: uma linha por seção, com os dois candidatos
    bu = {}; cand2 = collections.Counter()
    for g in ler_zip(glob.glob(os.path.join(DADOS, "tse_secoes", f"bweb_2t_{uf}_*.zip"))[0]):
        if g("CD_CARGO_PERGUNTA") != "3": continue
        k = (uf.lower(), g("CD_MUNICIPIO").zfill(5), g("NR_ZONA"), g("NR_SECAO"))
        s = bu.setdefault(k, dict(t=rc.seg(g("DT_BU_RECEBIDO")), aptos=int(g("QT_APTOS")), v={}))
        if g("CD_TIPO_VOTAVEL") == "1": s["v"][g("NR_VOTAVEL")] = int(g("QT_VOTOS")); cand2[g("NR_VOTAVEL")] += int(g("QT_VOTOS"))
    A, B = sorted(cand2, key=lambda c: -cand2[c])  # A = o mais votado no 2º turno; o erro é simétrico
    # 1º turno por seção
    v1 = collections.defaultdict(collections.Counter); tot1 = collections.Counter()
    for g in ler_zip(os.path.join(DADOS, "tse_secoes_gov", f"votacao_secao_2026_{uf}.zip")):
        if g("CD_CARGO") != "3" or g("NR_TURNO") != "1": continue
        k = (uf.lower(), g("CD_MUNICIPIO").zfill(5), g("NR_ZONA"), g("NR_SECAO")); n = g("NR_VOTAVEL"); q = int(g("QT_VOTOS"))
        v1[k][n] += q; tot1[n] += q
    val = sum(v for c, v in tot1.items() if c not in ("95", "96"))
    grandes = sorted(c for c, v in tot1.items() if c not in ("95", "96", B) and v >= 0.01 * val)
    # seções do 2º turno na ordem de recebimento (as sem boletim no fim)
    todas = sorted(bu, key=lambda k: (bu[k]["t"], k))
    N = len(todas); sem1 = sum(k not in v1 for k in todas)
    f = lambda fn: np.array([fn(k) for k in todas], float)
    pr = lambda k, c: float(pres.get(k, {}).get(c) or 0)
    S = dict(uf=np.zeros(N, int), ufs=[uf.lower()], L1=f(lambda k: v1[k][A]), F1=f(lambda k: v1[k][B]),
             comp1=f(lambda k: pr(k, "t1_comp")), aptos1=f(lambda k: pr(k, "t1_aptos")), aptos2=f(lambda k: bu[k]["aptos"]),
             L2=f(lambda k: bu[k]["v"].get(A, 0)), F2=f(lambda k: bu[k]["v"].get(B, 0)), t=f(lambda k: bu[k]["t"]))
    mus = sorted({k[1] for k in todas}); S["mun"] = np.searchsorted(mus, [k[1] for k in todas]); S["nmun"] = len(mus)
    outros = f(lambda k: sum(v for c, v in v1[k].items() if c not in grandes and c not in ("95", "96", B)))
    cols = [f(lambda k, c=c: v1[k][c]) for c in grandes] + [outros, f(lambda k: v1[k]["95"]), f(lambda k: v1[k]["96"])]
    comp = S["comp1"]; ok = comp > 0
    feats = [np.where(ok, c / np.where(ok, comp, 1), 0) for c in cols]
    feats.append(np.where(S["aptos1"] > 0, 1 - comp / np.where(S["aptos1"] > 0, S["aptos1"], 1), 0))
    Xb = np.column_stack([np.ones(N)] + feats); Xb[~ok] = Xb[ok].mean(0)
    S["Xb"] = Xb; S["Xc"] = np.hstack([Xb, np.ones((N, 1))])
    S["C"] = sparse.csr_matrix((np.ones(N), (S["mun"], np.arange(N))), shape=(len(mus), N))
    S["pen_c"] = np.r_[0, np.full(Xb.shape[1] - 1, 1e-6 * N), p2.PEN_UF]
    nrec = int(np.isfinite(S["t"]).sum())
    # (a): a conta da página com os 300 maiores municípios do estado (todos, se forem menos) e o resto em bloco
    secs = [dict(uf=uf.lower(), mun=k[1], aptos=bu[k]["aptos"], L=bu[k]["v"].get(A, 0), F=bu[k]["v"].get(B, 0)) for k in todas]
    te_mu = collections.Counter(); m1 = collections.defaultdict(lambda: [0, 0])
    for k in todas: te_mu[k[1]] += bu[k]["aptos"]
    for k, v in v1.items(): m1[k[1]][0] += v[A]; m1[k[1]][1] += v[B]
    top = sorted(te_mu, key=lambda m: -te_mu[m])[:300]
    base = dict(uf={uf.lower(): dict(L=tot1[A], F=tot1[B])}, mu=[[m, uf.lower(), m, te_mu[m], m1[m][0], m1[m][1]] for m in top])
    tot = dict(secoes={uf.lower(): N}, te_uf={uf.lower(): sum(te_mu.values())}, te_mu=dict(te_mu))
    return S, secs, base, tot, dict(uf=uf, A=A, B=B, grandes=grandes, secoes=N, com_boletim=nrec, sem_1t=sem1)

def main():
    pres = {}
    for r in csv.DictReader(gzip.open(os.path.join(DADOS, "secoes_presidente.csv.gz"), "rt", encoding="utf-8")):
        if r["uf"] in UFS: pres[(r["uf"].lower(), r["cd_mun"], r["zona"], r["secao"])] = r
    os.makedirs(SAI, exist_ok=True); linhas = []; resumo = {}
    M = ["contagem", "a", "b", "c", "d"]
    for uf in UFS:
        S, secs, base, tot, info = disputa(uf, pres)
        nrec = info["com_boletim"]; final = 100 * p2.share(S["L2"][:nrec].sum(), S["F2"][:nrec].sum())
        est = rc.Estado(tot, base); j = 0; L = []
        for k in range(1, 200):
            n = max(1, -int(-k / 2 * info["secoes"] // 100)); n = min(n, nrec)
            while est.n < n: est.add(secs[j]); j += 1
            vol = p2.volume(S, n); c = p2.metodo_c(S, n, vol); dd, _ = p2.metodo_d(S, n, vol)
            d = dict(disputa=f"governador_2026_{uf}", pst=k / 2, hora_tse=rc.hms(S["t"][n - 1] + p2.ATRASO), n=n,
                     contagem=100 * p2.share(S["L2"][:n].sum(), S["F2"][:n].sum()), a=est.conta()["proj"], b=100 * p2.metodo_b(S, n),
                     c=100 * c[0], c_lo=100 * c[1], c_hi=100 * c[2], d=100 * dd[0], d_lo=100 * dd[1], d_hi=100 * dd[2], final=final)
            L.append(d)
        linhas += L
        R = dict(info, final=round(final, 3), metodos={})
        for m in M:
            e = [abs(d[m] - final) for d in L]
            lado = (lambda d: d[m] > 50) if final > 50 else (lambda d: d[m] < 50)
            ac = [lado(d) and abs(d[m] - final) <= 0.5 for d in L]; k = next((i for i in range(len(L)) if all(ac[i:])), None)
            x = dict(abs_medio=round(sum(e) / len(e), 3), max_abs=round(max(e), 3), ate_30=round(sum(e[:60]) / 60, 3),
                     passa_a_acertar=None if k is None else L[k]["pst"])
            if m in ("c", "d"): x["cobre"] = int(sum(d[m + "_lo"] <= final <= d[m + "_hi"] for d in L))
            R["metodos"][m] = x
        resumo[f"governador_2026_{uf}"] = R
        print(uf, info["A"], info["B"], round(final, 3), {m: (R["metodos"][m]["abs_medio"], R["metodos"][m]["passa_a_acertar"]) for m in M},
              "cobre c/d:", R["metodos"]["c"]["cobre"], R["metodos"]["d"]["cobre"], "sem 1t:", info["sem_1t"])
    cab = ["disputa", "pst", "hora_tse", "n", "contagem", "a", "b", "c", "c_lo", "c_hi", "d", "d_lo", "d_hi", "final"]
    with open(os.path.join(SAI, "governador_2026_instantes.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";"); w.writerow(cab)
        for d in linhas: w.writerow([round(d[k], 4) if isinstance(d[k], float) else d[k] for k in cab])
    json.dump(resumo, open(os.path.join(SAI, "governador_2026_resumo.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
