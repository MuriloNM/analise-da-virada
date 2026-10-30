# T41, Parte 3: o 2º turno de 2022 da mesma seção ajuda a projetar o 2º turno de 2026?
# Casa as seções de 2026 com as de 2022 (seção; senão local de votação; senão município) e roda (b22), (c22) e (d22)
# ao lado de (b), (c) e (d) da Parte 2, nos mesmos instantes. Regras: ticket T41, "Regras do teste 2022 ajuda...".
# Uso: python -I scripts/projecoes_2022.py   (grava em dados/projecoes_outras/)
import os, sys, io, csv, gzip, json, zipfile, collections
import numpy as np
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import reconstrucao_2t as rc, projecoes_2t as p2
DADOS = os.path.join(AQUI, "..", "dados"); SAI = os.path.join(DADOS, "projecoes_outras")
CASA = os.path.join(SAI, "secoes_2022_casadas.csv.gz")

def linhas(zp, nome):
    z = zipfile.ZipFile(zp); f = io.TextIOWrapper(z.open(nome), encoding="latin-1"); r = csv.reader(f, delimiter=";"); h = next(r)
    ix = {c: i for i, c in enumerate(h)}
    for q in r: yield lambda c, q=q: q[ix[c]]

def casar():
    """Para cada seção de 2026: Lula e Bolsonaro de 2022 (1º e 2º turno) e o nível do casamento (1 seção, 2 local, 3 município)."""
    sec = collections.defaultdict(lambda: [0, 0, 0, 0]); loc = collections.defaultdict(lambda: [0, 0, 0, 0, set()])
    mun = collections.defaultdict(lambda: [0, 0, 0, 0, set()])
    for g in linhas(os.path.join(DADOS, "tse_2022", "votacao_secao_2022_BR.zip"), "votacao_secao_2022_BR.csv"):
        n = g("NR_VOTAVEL")
        if g("CD_CARGO") != "1" or n not in ("13", "22"): continue
        j = (int(g("NR_TURNO")) - 1) * 2 + (n == "22"); q = int(g("QT_VOTOS"))
        k = (g("SG_UF").lower(), g("CD_MUNICIPIO").zfill(5), g("NR_ZONA"), g("NR_SECAO"))
        sec[k][j] += q
        for d, kk in ((loc, k[:3] + (g("NR_LOCAL_VOTACAO"),)), (mun, k[:2])):
            d[kk][j] += q; d[kk][4].add(k)
    local26 = {}
    for g in linhas(os.path.join(DADOS, "tse_secoes", "votacao_secao_2026_BR.zip"), "votacao_secao_2026_BR.csv"):
        local26[(g("SG_UF").lower(), g("CD_MUNICIPIO").zfill(5), g("NR_ZONA"), g("NR_SECAO"))] = g("NR_LOCAL_VOTACAO")
    out = []
    for r in csv.DictReader(gzip.open(os.path.join(DADOS, "secoes_presidente.csv.gz"), "rt", encoding="utf-8")):
        k = (r["uf"].lower(), r["cd_mun"], r["zona"], r["secao"])
        if k in sec: v, nv = sec[k], 1
        elif k[:3] + (local26.get(k),) in loc:
            x = loc[k[:3] + (local26[k],)]; m = len(x[4]); v, nv = [y / m for y in x[:4]], 2
        elif k[:2] in mun:
            x = mun[k[:2]]; m = len(x[4]); v, nv = [y / m for y in x[:4]], 3
        else: v, nv = [0, 0, 0, 0], 4
        out.append(list(k) + [round(y, 2) for y in v] + [nv])
    os.makedirs(SAI, exist_ok=True)
    with gzip.open(CASA, "wt", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";"); w.writerow(["uf", "mun", "zona", "secao", "lula22_1t", "bolso22_1t", "lula22_2t", "bolso22_2t", "nivel"]); w.writerows(out)

def metodo_b22(S, n):
    """(b) com a base do 2º turno de 2022 da seção; votos como em (b) (1º turno de 2026 × razão observada)."""
    R = slice(0, n); M = slice(n, None)
    L2, F2, L1, F1, P, Q = S["L2"], S["F2"], S["L1"], S["F1"], S["L22"], S["B22"]
    def agg(idx, size):
        g = lambda a: np.bincount(idx[R], a[R], minlength=size)
        return g(L2), g(F2), g(L1), g(F1), g(P), g(Q)
    def sw(l2, f2, l1, f1, p, q, piso):
        v2 = l2 + f2; ok = (v2 >= piso) & (l1 + f1 > 0) & (p + q > 0)
        with np.errstate(invalid="ignore", divide="ignore"):
            return ok, np.where(ok, l2 / v2 - p / (p + q), 0), np.where(ok, v2 / (l1 + f1), 0)
    okm, swm, rm = sw(*agg(S["mun"], S["nmun"]), 1500)
    oku, swu, ru = sw(*agg(S["uf"], len(S["ufs"])), 3000)
    t = [a[R].sum() for a in (L2, F2, L1, F1, P, Q)]
    swb, rb = t[0] / (t[0] + t[1]) - t[4] / (t[4] + t[5]), (t[0] + t[1]) / (t[2] + t[3])
    mu, uf = S["mun"][M], S["uf"][M]
    s = np.where(okm[mu], swm[mu], np.where(oku[uf], swu[uf], swb))
    r = np.where(okm[mu], rm[mu], np.where(oku[uf], ru[uf], rb))
    pq = P[M] + Q[M]; v1 = L1[M] + F1[M]
    sh = np.clip(np.where(pq > 0, P[M] / np.where(pq > 0, pq, 1), 0.5) + s, 0, 1); vol = v1 * r
    return p2.share(t[0] + (vol * sh).sum(), t[1] + (vol * (1 - sh)).sum())

def main():
    if not os.path.exists(CASA): casar()
    secs, tot = rc.carregar(); S = p2.secoes(secs)
    S["pen_c"] = np.r_[0, np.full(S["Xb"].shape[1] - 1, 1e-6 * rc.TOTAL), np.full(len(S["ufs"]), p2.PEN_UF)]
    cas = {(r["uf"], r["mun"], r["zona"], r["secao"]): r for r in csv.DictReader(gzip.open(CASA, "rt", encoding="utf-8"), delimiter=";")}
    # mesma ordem de S (a de p2.secoes): as seções recebidas na ordem de secs, depois as sem boletim
    chaves = [(s["uf"], s["mun"], s["zona"], s["secao"]) for s in secs]
    vistas = set(chaves); chaves += [k for k in cas if k not in vistas]
    # p2.secoes põe as sem boletim na ordem do arquivo de seções; conferir pelos votos do 1º turno
    rows = [cas[k] for k in chaves]
    S["L22"] = np.array([float(r["lula22_2t"]) for r in rows]); S["B22"] = np.array([float(r["bolso22_2t"]) for r in rows])
    niv = np.array([int(r["nivel"]) for r in rows])
    niveis = {str(k): int((niv == k).sum()) for k in (1, 2, 3, 4)}
    print("casamento:", niveis)
    pq = S["L22"] + S["B22"]; ok = pq > 0
    s22 = np.where(ok, S["L22"] / np.where(ok, pq, 1), (S["L22"][ok].sum() / pq[ok].sum()))
    Xb0, Xc0, pen0 = S["Xb"], S["Xc"], S["pen_c"]
    Xb22 = np.hstack([Xb0, s22[:, None], (niv >= 3).astype(float)[:, None]])
    nuf = len(S["ufs"]); Xc22 = np.hstack([Xb22, Xc0[:, -nuf:]])
    pen22 = np.r_[pen0[:Xb0.shape[1]], 1e-6 * rc.TOTAL, 1e-6 * rc.TOTAL, pen0[-nuf:]]
    linhas_ = []
    for d in p2.instantes(secs):
        n = d["n"]
        vol = p2.volume(S, n)
        r0 = dict(b=p2.metodo_b(S, n), c=p2.metodo_c(S, n, vol)[0], d=p2.metodo_d(S, n, vol)[0][0])
        S["Xb"], S["Xc"], S["pen_c"] = Xb22, Xc22, pen22
        r1 = dict(b22=metodo_b22(S, n), c22=p2.metodo_c(S, n, vol)[0], d22=p2.metodo_d(S, n, vol)[0][0])
        S["Xb"], S["Xc"], S["pen_c"] = Xb0, Xc0, pen0
        d.update({k: 100 * v for k, v in {**r0, **r1}.items()}); linhas_.append(d)
    M = ["b", "b22", "c", "c22", "d", "d22"]
    cab = ["conjunto", "tipo", "hora_tse", "pst", "n"] + M
    with open(os.path.join(SAI, "presidente_2026_com_2022_instantes.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";"); w.writerow(cab)
        for d in linhas_: w.writerow([round(d[k], 4) if isinstance(d[k], float) else d[k] for k in cab])
    res = dict(casamento=niveis)
    for conj in ("principal", "fino"):
        L = [d for d in linhas_ if d["conjunto"] == conj]; res[conj] = {}
        for m in M:
            e = [abs(d[m] - p2.FINAL) for d in L]
            ac = [d[m] > 50 and abs(d[m] - p2.FINAL) <= 0.5 for d in L]; k = next((i for i in range(len(L)) if all(ac[i:])), None)
            res[conj][m] = dict(abs_medio=round(sum(e) / len(e), 3), max_abs=round(max(e), 3), ate_30=round(float(np.mean([x for x, d in zip(e, L) if d["pst"] < 30])), 3),
                                passa_a_acertar=None if k is None else L[k]["pst"])
    json.dump(res, open(os.path.join(SAI, "presidente_2026_com_2022_resumo.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(res, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
