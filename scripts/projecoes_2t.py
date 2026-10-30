# T41, Parte 2: testa projeções do resultado final do 2º turno na apuração reconstruída (Parte 1, scripts/reconstrucao_2t.py).
# Em cada instante, só o que se sabia: as seções recebidas até ali (2º turno) e, de todas, o 1º turno e o eleitorado do 2º turno.
# Métodos: (a) a conta da página (standalone.js), (b) variação 1º→2º por seção, (c) regressão, (d) hierárquico por UF e município.
# Regras escritas antes de rodar: docs/analise/tickets/T41-reconstrucao-apuracao.md, "Regras da Parte 2".
# Uso: python -I scripts/projecoes_2t.py   (grava em dados/projecoes_2t/)
import os, sys, csv, gzip, json, math
import numpy as np
from scipy import sparse
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import reconstrucao_2t as rc
DADOS = os.path.join(AQUI, "..", "dados"); SAI = os.path.join(DADOS, "projecoes_2t")
FINAL = 51.785; ATRASO = 28  # atraso mediano recebido → hora do TSE (Parte 1)
CAND = ["13", "14", "16", "21", "27", "28", "29", "30", "35", "55", "70", "80"]  # 22 fica de referência
PEN_UF = 10.0   # penalidade do efeito fixo de UF em (c), em "seções": UF sem seção fica no nacional
Z = 1.959964

def secoes(secs):
    """Arrays de todas as 499.248 seções, na ordem de recebimento da Parte 1 (as 43 sem boletim no fim)."""
    pos = {(s["uf"], s["mun"], s["zona"], s["secao"]): k for k, s in enumerate(secs)}
    N = rc.TOTAL; ordem = np.full(N, -1); rows = []
    for r in csv.DictReader(gzip.open(os.path.join(DADOS, "secoes_presidente.csv.gz"), "rt", encoding="utf-8")):
        rows.append(r)
    extra = len(secs)
    for i, r in enumerate(rows):
        k = pos.get((r["uf"].lower(), r["cd_mun"], r["zona"], r["secao"]))
        if k is None: k = extra; extra += 1
        ordem[k] = i
    assert extra == N and (ordem >= 0).all()
    rows = [rows[i] for i in ordem]
    f = lambda c: np.array([float(r[c] or 0) for r in rows])
    ufs = sorted({r["uf"].lower() for r in rows}); mus = sorted({r["cd_mun"] for r in rows})
    S = dict(uf=np.array([ufs.index(r["uf"].lower()) for r in rows]), ufs=ufs,
             mun=np.searchsorted(mus, [r["cd_mun"] for r in rows]), nmun=len(mus),
             L1=f("t1_13"), F1=f("t1_22"), comp1=f("t1_comp"), aptos1=f("t1_aptos"), aptos2=f("t2_aptos"),
             L2=np.zeros(N), F2=np.zeros(N), t=np.full(N, np.inf))
    for k, s in enumerate(secs):
        S["L2"][k] = s["L"]; S["F2"][k] = s["F"]; S["t"][k] = s["t"]
    # 1º turno da seção: parte de cada candidato (menos o 22), brancos e nulos no comparecimento, e abstenção
    cols = [f("t1_" + c) for c in CAND] + [f("t1_brancos"), f("t1_nulos")]
    comp = S["comp1"]; ok = comp > 0
    feats = [np.where(ok, c / np.where(ok, comp, 1), 0) for c in cols]
    feats.append(np.where(S["aptos1"] > 0, 1 - comp / np.where(S["aptos1"] > 0, S["aptos1"], 1), 0))
    Xb = np.column_stack([np.ones(N)] + feats)
    m = Xb[ok].mean(0); Xb[~ok] = m  # 41 seções não instaladas no 1º turno: média nacional
    S["Xb"] = Xb
    S["Xc"] = np.hstack([Xb, (S["uf"][:, None] == np.arange(len(ufs))[None, :]).astype(float)])
    S["C"] = sparse.csr_matrix((np.ones(N), (S["mun"], np.arange(N))), shape=(len(mus), N))
    return S

def share(L, F): return L / (L + F)

# ---------- (b) variação 1º→2º por seção ----------
def metodo_b(S, n):
    R = slice(0, n); M = slice(n, None)
    L2, F2, L1, F1 = S["L2"], S["F2"], S["L1"], S["F1"]
    def agg(idx, size):
        g = lambda a: np.bincount(idx[R], a[R], minlength=size)
        return g(L2), g(F2), g(L1), g(F1)
    def sw(l2, f2, l1, f1, piso):
        v2, v1 = l2 + f2, l1 + f1; ok = (v2 >= piso) & (v1 > 0)
        with np.errstate(invalid="ignore", divide="ignore"):
            return ok, np.where(ok, l2 / v2 - l1 / v1, 0), np.where(ok, v2 / v1, 0)
    okm, swm, rm = sw(*agg(S["mun"], S["nmun"]), 1500)
    oku, swu, ru = sw(*agg(S["uf"], len(S["ufs"])), 3000)
    l2, f2, l1, f1 = L2[R].sum(), F2[R].sum(), L1[R].sum(), F1[R].sum()
    swb, rb = (l2 / (l2 + f2) - l1 / (l1 + f1), (l2 + f2) / (l1 + f1)) if l1 + f1 > 0 else (0, 1)
    mu, uf = S["mun"][M], S["uf"][M]
    s = np.where(okm[mu], swm[mu], np.where(oku[uf], swu[uf], swb))
    r = np.where(okm[mu], rm[mu], np.where(oku[uf], ru[uf], rb))
    v1 = L1[M] + F1[M]
    sh = np.clip(np.where(v1 > 0, L1[M] / np.where(v1 > 0, v1, 1), 0.5) + s, 0, 1); vol = v1 * r
    return share(l2 + (vol * sh).sum(), f2 + (vol * (1 - sh)).sum())

# ---------- regressões (c) e (d) ----------
def mqo(X, y, pen):
    A = X.T @ X + np.diag(pen); return np.linalg.solve(A, X.T @ y), A

def volume(S, n):
    """Votos dos dois ÷ eleitorado do 2º turno, pela regressão com efeito fixo de UF; prevê os votos das seções que faltam."""
    X = S["Xc"]; a = S["aptos2"]; ok = a[:n] > 0
    y = (S["L2"][:n] + S["F2"][:n])[ok] / a[:n][ok]
    b, _ = mqo(X[:n][ok], y, S["pen_c"])
    return np.clip(X[n:] @ b, 0, 1) * a[n:]

def junta(S, n, s_hat, vol, var_S):
    l2, f2 = S["L2"][:n].sum(), S["F2"][:n].sum()
    tot = l2 + f2 + vol.sum(); p = (l2 + (vol * s_hat).sum()) / tot; sd = math.sqrt(var_S) / tot
    return p, p - Z * sd, p + Z * sd

def metodo_c(S, n, vol):
    X = S["Xc"][:n]; v = S["L2"][:n] + S["F2"][:n]; ok = v > 0
    X, y, mun = X[ok], (S["L2"][:n][ok] / v[ok]), S["mun"][:n][ok]
    b, A = mqo(X, y, S["pen_c"]); e = y - X @ b
    Ai = np.linalg.inv(A)
    Cm = S["C"][:, :n][:, np.flatnonzero(ok)]
    sc = Cm @ (X * e[:, None]); V = Ai @ (sc.T @ sc) @ Ai  # agrupado por município
    s2e = e @ e / max(1, len(e) - X.shape[1])
    XM = S["Xc"][n:]; s_hat = np.clip(XM @ b, 0, 1); g = XM.T @ vol
    return junta(S, n, s_hat, vol, g @ V @ g + s2e * (vol ** 2).sum())

def metodo_d(S, n, vol):
    X = S["Xb"][:n]; v = S["L2"][:n] + S["F2"][:n]; ok = v > 0
    X, y = X[ok], S["L2"][:n][ok] / v[ok]; mun, uf = S["mun"][:n][ok], S["uf"][:n][ok]
    nm_, nu_ = S["nmun"], len(S["ufs"]); N = len(y); k = X.shape[1]
    pen = np.r_[0, np.full(k - 1, 1e-6 * N)]
    A = X.T @ X + np.diag(pen); Ai = np.linalg.inv(A); Xty = X.T @ y
    nm = np.bincount(mun, minlength=nm_).astype(float); nu = np.bincount(uf, minlength=nu_).astype(float)
    muf = np.zeros(nm_, int); muf[mun] = uf  # UF de cada município (só os vistos importam aqui)
    u = np.zeros(nu_); vm = np.zeros(nm_)
    for _ in range(4):
        b = Ai @ (Xty - X.T @ (u[uf] + vm[mun]))
        r = y - X @ b
        # componentes de variância pelo método dos momentos (ANOVA aninhada: seção em município em UF)
        rm = np.bincount(mun, r, nm_) / np.maximum(nm, 1)
        ru = np.bincount(uf, r, nu_) / np.maximum(nu, 1)
        M = (nm > 0).sum(); U = (nu > 0).sum()
        s2e = ((r - rm[mun]) ** 2).sum() / max(1, N - M)
        ssb = (nm * (rm - ru[muf]) ** 2)[nm > 0].sum()
        c = N - (np.bincount(muf[nm > 0], nm[nm > 0] ** 2, nu_) / np.maximum(nu, 1)).sum()
        s2v = max(0.0, (ssb - (M - U) * s2e) / c) if c > 0 else 0.0
        sum_nm2 = np.bincount(muf[nm > 0], nm[nm > 0] ** 2, nu_)
        ruido_u = np.where(nu > 0, s2v * sum_nm2 / np.maximum(nu, 1) ** 2 + s2e / np.maximum(nu, 1), np.inf)
        vis = nu > 0
        s2u = max(0.0, (((ru[vis] - ru[vis].mean()) ** 2).sum() - ruido_u[vis].mean() * (U - 1)) / max(1, U - 1)) if U > 1 else 0.0
        tau = np.where(vis, s2u / (s2u + ruido_u), 0) if s2u > 0 else np.zeros(nu_)
        u = tau * np.where(vis, ru, 0)
        lam = np.where(nm > 0, s2v / (s2v + s2e / np.maximum(nm, 1)), 0) if s2v > 0 else np.zeros(nm_)
        vm = lam * (rm - u[muf])
    var_u = s2u * (1 - tau); var_v = s2v * (1 - lam)
    e = y - X @ b - u[uf]
    sc = S["C"][:, :n][:, np.flatnonzero(ok)] @ (X * e[:, None]); V = Ai @ (sc.T @ sc) @ Ai
    XM = S["Xb"][n:]; mM, uM = S["mun"][n:], S["uf"][n:]
    s_hat = np.clip(XM @ b + u[uM] + vm[mM], 0, 1); g = XM.T @ vol
    Wu = np.bincount(uM, vol, nu_); Wm = np.bincount(mM, vol, nm_)
    var = g @ V @ g + (Wu ** 2 * var_u).sum() + (Wm ** 2 * var_v).sum() + s2e * (vol ** 2).sum()
    p = junta(S, n, s_hat, vol, var)
    return p, dict(s2u=s2u, s2v=s2v, s2e=s2e)

# ---------- instantes ----------
def instantes(secs):
    hist = rc.ler_historico(); ts = [s["t"] for s in secs]; out = []
    for h in hist[:-1]:
        n = min(len(secs), max(1, -int(-(h["pst"] - 0.005) * rc.TOTAL // 100)))
        out.append(dict(conjunto="principal", tipo="gravada", hora_tse=h["hora"], pst=h["pst"], n=n))
    a, b = rc.seg("20:36:09"), rc.seg("20:43:00")
    for x in range(a + 30, b, 30):
        n = int(np.searchsorted(ts, x - ATRASO, side="right"))
        out.append(dict(conjunto="principal", tipo="buraco", hora_tse=rc.hms(x), pst=round(n / rc.TOTAL * 100, 2), n=n))
    for k in range(1, 200):
        p = k / 2; n = -int(-p * rc.TOTAL // 100)
        out.append(dict(conjunto="fino", tipo="grade", hora_tse=rc.hms(ts[n - 1] + ATRASO), pst=p, n=n))
    return sorted(out, key=lambda d: (d["n"], d["conjunto"]))

FAIXAS = [(10 * i, 10 * i + 10) for i in range(10)]
def faixa(p): return next(f"{a}–{b}" for a, b in FAIXAS if a <= p < b or (b == 100 and p == 100))

def main():
    secs, tot = rc.carregar()
    base = json.load(open(os.path.join(DADOS, "base_1t_compacta.json"), encoding="utf-8"))
    S = secoes(secs)
    S["pen_c"] = np.r_[0, np.full(S["Xb"].shape[1] - 1, 1e-6 * rc.TOTAL), np.full(len(S["ufs"]), PEN_UF)]
    ref = {r["hora_tse"]: float(r["projecao_pct"]) for r in csv.DictReader(open(os.path.join(DADOS, "reconstrucao_2t", "leituras_br.csv"), encoding="utf-8"), delimiter=";")}
    est = rc.Estado(tot, base); j = 0; linhas = []
    for d in instantes(secs):
        n = d["n"]
        while est.n < n: est.add(secs[j]); j += 1
        a = est.conta()["proj"]
        if d["conjunto"] == "principal": assert abs(a - ref[d["hora_tse"]]) < 1e-9, (d, a)
        l2, f2 = S["L2"][:n].sum(), S["F2"][:n].sum()
        vol = volume(S, n)
        c = metodo_c(S, n, vol); dd, comp = metodo_d(S, n, vol)
        d.update(contagem=100 * share(l2, f2), a=a, b=100 * metodo_b(S, n), c=100 * c[0], c_lo=100 * c[1], c_hi=100 * c[2],
                 d=100 * dd[0], d_lo=100 * dd[1], d_hi=100 * dd[2], **{k: v for k, v in comp.items()})
        linhas.append(d)
        if d["conjunto"] == "principal" and d["tipo"] == "gravada" and len(linhas) % 10 == 0:
            print(d["hora_tse"], d["pst"], round(d["a"], 3), round(d["b"], 3), round(d["c"], 3), round(d["d"], 3))
    os.makedirs(SAI, exist_ok=True)
    cab = ["conjunto", "tipo", "hora_tse", "pst", "n", "contagem", "a", "b", "c", "c_lo", "c_hi", "d", "d_lo", "d_hi", "s2u", "s2v", "s2e"]
    with open(os.path.join(SAI, "instantes.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";"); w.writerow(cab)
        for d in linhas: w.writerow([round(d[k], 4) if isinstance(d[k], float) and k not in ("s2u", "s2v", "s2e") else d[k] for k in cab])
    M = ["contagem", "a", "b", "c", "d"]
    resumo = {}
    for conj in ("principal", "fino"):
        L = [d for d in linhas if d["conjunto"] == conj]; R = resumo[conj] = {"faixas": [], "metodos": {}}
        for fx in [f"{a}–{b}" for a, b in FAIXAS]:
            F = [d for d in L if faixa(d["pst"]) == fx]
            if not F: continue
            row = dict(faixa=fx, leituras=len(F))
            for m in M:
                e = [d[m] - FINAL for d in F]
                row[m] = dict(medio=round(sum(e) / len(e), 3), abs_medio=round(sum(map(abs, e)) / len(e), 3), max_abs=round(max(map(abs, e)), 3))
            for m in ("c", "d"):
                row[m]["cobre"] = int(sum(d[m + "_lo"] <= FINAL <= d[m + "_hi"] for d in F))
            R["faixas"].append(row)
        for m in M:
            e = [abs(d[m] - FINAL) for d in L]
            acerta = [bool(d[m] > 50) and abs(d[m] - FINAL) <= 0.5 for d in L]
            k = next((i for i in range(len(L)) if all(acerta[i:])), None)
            x = dict(abs_medio=round(sum(e) / len(e), 3), max_abs=round(max(e), 3),
                     passa_a_acertar=None if k is None else dict(pst=L[k]["pst"], hora_tse=L[k]["hora_tse"]))
            if m in ("c", "d"):
                x["cobre"] = f"{sum(d[m + '_lo'] <= FINAL <= d[m + '_hi'] for d in L)} de {len(L)}"
                ac = [d[m + "_lo"] > 50 for d in L]; k = next((i for i in range(len(L)) if all(ac[i:])), None)
                x["intervalo_acima_de_50"] = None if k is None else dict(pst=L[k]["pst"], hora_tse=L[k]["hora_tse"])
                x["meia_largura_mediana"] = round(float(np.median([(d[m + "_hi"] - d[m + "_lo"]) / 2 for d in L])), 3)
            R["metodos"][m] = x
    json.dump(resumo, open(os.path.join(SAI, "resumo.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    with open(os.path.join(SAI, "faixas.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["conjunto", "faixa", "leituras", "metodo", "erro_medio", "erro_abs_medio", "erro_abs_max", "intervalo_cobre"])
        for conj, R in resumo.items():
            for row in R["faixas"]:
                for m in M:
                    w.writerow([conj, row["faixa"], row["leituras"], m, row[m]["medio"], row[m]["abs_medio"], row[m]["max_abs"], row[m].get("cobre", "")])
    print(json.dumps({c: R["metodos"] for c, R in resumo.items()}, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
