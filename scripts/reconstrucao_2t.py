# T41, Parte 1: refaz a apuração do 2º turno (6258, presidente) pela hora de recebimento de cada boletim (DT_BU_RECEBIDO).
# Lê o CSV direto dos zips do bweb_2t (T27). Uma linha por seção: UF, município, zona, seção, recebido, aptos, Lula, Flávio.
# Uso: python -I scripts/reconstrucao_2t.py   (grava em dados/reconstrucao_2t/)
import os, io, csv, glob, json, zipfile, gzip
AQUI = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(AQUI, "..", "dados")
SAI = os.path.join(DADOS, "reconstrucao_2t")
SEC = os.path.join(SAI, "secoes_2t.csv.gz")

def extrair():
    secs = {}
    tipos = {}
    for zp in sorted(glob.glob(os.path.join(DADOS, "tse_secoes", "bweb_2t_*.zip"))):
        z = zipfile.ZipFile(zp)
        nome = [n for n in z.namelist() if n.lower().endswith(".csv")][0]
        with io.TextIOWrapper(z.open(nome), encoding="latin-1") as f:
            f.readline()
            for p in csv.reader(f, delimiter=";"):
                if p[8] != "6258" or p[16] != "1": continue
                k = (p[10], p[11], p[13], p[14])
                s = secs.get(k)
                if s is None:
                    s = secs[k] = {"uf": p[10], "mun": p[11], "zona": p[13], "secao": p[14], "recebido": p[21],
                                   "emissao": p[42], "aptos": int(p[22]), "comp": int(p[23]), "urna": p[26],
                                   "agregadas": "" if p[38] == "#NULO#" else p[38], "L": 0, "F": 0}
                    tipos[p[26]] = tipos.get(p[26], 0) + 1
                elif s["recebido"] != p[21]: print("recebido diferente na mesma seção", k)
                if p[27] == "1":
                    if p[29] == "13": s["L"] += int(p[31])
                    elif p[29] == "22": s["F"] += int(p[31])
        print(os.path.basename(zp), len(secs))
    print("tipos de urna", tipos)
    os.makedirs(SAI, exist_ok=True)
    cols = ["uf", "mun", "zona", "secao", "recebido", "emissao", "aptos", "comp", "urna", "agregadas", "L", "F"]
    with gzip.open(SEC, "wt", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";"); w.writerow(cols)
        for s in sorted(secs.values(), key=lambda s: (s["recebido"], s["uf"], s["mun"], s["zona"], s["secao"])):
            w.writerow([s[c] for c in cols])

# ---------- reconstrução ----------
TOTAL = 499248  # seções do 2º turno (ts do TSE); 43 seções sem boletim nunca entram

def seg(h): a, b, c = map(int, h[-8:].split(":")); return a * 3600 + b * 60 + c
def hms(x): x = int(x); return f"{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}"
def share(L, F): return L / (L + F) if L + F > 0 else None
def r3(z): return None if z is None else round(z * 100, 3)

def carregar():
    secs = list(csv.DictReader(gzip.open(SEC, "rt", encoding="utf-8"), delimiter=";"))
    for s in secs:
        s["t"] = seg(s["recebido"]); s["mun"] = s["mun"].zfill(5); s["uf"] = s["uf"].lower()
        for k in ("aptos", "L", "F"): s[k] = int(s[k])
    secs.sort(key=lambda s: (s["t"], s["uf"], s["mun"], s["zona"], s["secao"]))
    # total de seções e eleitorado do 2º turno por UF e município (todas as 499.248 seções, T27)
    tot = {"secoes": {}, "te_uf": {}, "te_mu": {}}
    for r in csv.DictReader(gzip.open(os.path.join(DADOS, "secoes_presidente.csv.gz"), "rt", encoding="utf-8")):
        if not r["t2_aptos"]: continue
        u = r["uf"].lower(); a = int(r["t2_aptos"])
        tot["secoes"][u] = tot["secoes"].get(u, 0) + 1
        tot["te_uf"][u] = tot["te_uf"].get(u, 0) + a
        tot["te_mu"][r["cd_mun"]] = tot["te_mu"].get(r["cd_mun"], 0) + a
    return secs, tot

class Estado:
    """Acumula as seções recebidas e refaz, num instante, a conta da página ao vivo (a mesma de scripts/standalone.js)."""
    def __init__(self, tot, base):
        self.tot, self.base = tot, base
        self.mu = {m[0]: m for m in base["mu"]}
        self.n = 0; self.uf = {}; self.m = {}
    def add(self, s):
        self.n += 1
        for d, k in ((self.uf, s["uf"]), (self.m, s["mun"])):
            x = d.setdefault(k, [0, 0, 0, 0]); x[0] += 1; x[1] += s["aptos"]; x[2] += s["L"]; x[3] += s["F"]
    def conta(self, br=None):  # br: (Lula, Flávio) do arquivo nacional, se lido noutro instante que os das UFs
        ufs = list(self.base["uf"].keys()); units = []
        for u in ufs:
            U = self.uf.get(u, [0, 0, 0, 0]); U1 = self.base["uf"][u]
            rest = dict(te=self.tot["te_uf"][u], est=U[1], L2=U[2], F2=U[3], L1=U1["L"], F1=U1["F"])
            for cd, m in self.mu.items():
                if m[1] != u: continue
                M = self.m.get(cd, [0, 0, 0, 0])
                x = dict(uf=u, nm=m[2], te=self.tot["te_mu"][cd], est=M[1], L2=M[2], F2=M[3], L1=m[4], F1=m[5])
                units.append(x)
                for k in ("te", "est", "L2", "F2", "L1", "F1"): rest[k] -= x[k]
            if rest["te"] > 0: units.append(dict(uf=u, nm=None, **rest))
        for x in units: x["f"] = min(1, x["est"] / x["te"]) if x["te"] else 0
        L2 = sum(v[2] for v in self.uf.values()); F2 = sum(v[3] for v in self.uf.values())
        if br: L2, F2 = br
        L1eq = sum(x["f"] * x["L1"] for x in units); F1eq = sum(x["f"] * x["F1"] for x in units)
        s2, s1eq = share(L2, F2), share(L1eq, F1eq)
        swing = s2 - s1eq if s2 is not None and s1eq is not None else None
        def swk(x, minv):
            if x["L2"] + x["F2"] < minv or x["f"] <= 0: return None
            return (share(x["L2"], x["F2"]) - share(x["f"] * x["L1"], x["f"] * x["F1"]), (x["L2"] + x["F2"]) / (x["f"] * (x["L1"] + x["F1"])))
        nat = (swing, (L2 + F2) / (L1eq + F1eq)) if swing is not None and L1eq + F1eq > 0 else (0, 1)
        ufsw, ufout = {}, {}
        for u in ufs:
            xs = [x for x in units if x["uf"] == u]
            a = {k: sum(x[k] for x in xs) for k in ("L2", "F2")}
            l1 = sum(x["f"] * x["L1"] for x in xs); f1 = sum(x["f"] * x["F1"] for x in xs)
            ufsw[u] = (share(a["L2"], a["F2"]) - share(l1, f1), (a["L2"] + a["F2"]) / (l1 + f1)) if a["L2"] + a["F2"] >= 3000 and l1 + f1 > 0 else None
            U = self.uf.get(u, [0, 0, 0, 0])
            ufout[u] = dict(pst=round(U[0] / self.tot["secoes"][u] * 100, 2), L2=U[2], F2=U[3], s2=r3(share(U[2], U[3])), s1eq=r3(share(l1, f1)),
                            s1fin=r3(share(self.base["uf"][u]["L"], self.base["uf"][u]["F"])))
        remL = remF = 0.0
        for x in units:
            sw = swk(x, 1500) or ufsw.get(x["uf"]) or nat
            rem = (1 - x["f"]) * (x["L1"] + x["F1"]) * sw[1]
            sh = min(1, max(0, share(x["L1"], x["F1"]) + sw[0])) if x["L1"] + x["F1"] > 0 else 0.5
            remL += rem * sh; remF += rem * (1 - sh)
        proj = share(L2 + remL, F2 + remF) if swing is not None else None
        return dict(pst=round(self.n / TOTAL * 100, 2), L2=L2, F2=F2, s2=r3(s2), s1eq=r3(s1eq), proj=r3(proj), uf=ufout, units=units)

def ler_historico():
    h = list(csv.reader(open(os.path.join(DADOS, "historico_2t.csv"), encoding="utf-8-sig"), delimiter=";"))[1:]
    f = lambda v: float(v.replace(",", "."))
    return [dict(pst=f(r[0]), hora=r[1], t=seg(r[1]), s2=f(r[2]), s1eq=f(r[3]), proj=f(r[4])) for r in h]

def grava(nome, cab, linhas):
    with open(os.path.join(SAI, nome), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";"); w.writerow(cab); w.writerows(linhas)

def main():
    import statistics as st
    if not os.path.exists(SEC): extrair()
    secs, tot = carregar()
    assert sum(tot["secoes"].values()) == TOTAL
    base = json.load(open(os.path.join(DADOS, "base_1t_compacta.json"), encoding="utf-8"))
    hist = ler_historico()
    L, F = sum(s["L"] for s in secs), sum(s["F"] for s in secs)
    resumo = dict(cond0=dict(L=L, F=F, lula=round(L / (L + F) * 100, 4), secoes_com_boletim=len(secs), secoes_total=TOTAL))

    # 1) curva por minuto (hora de recebimento), Brasil e UF
    cum = {}; linhas_br, linhas_uf = [], []
    i = 0
    for m in range(secs[0]["t"] // 60 * 60 + 60, secs[-1]["t"] // 60 * 60 + 120, 60):
        while i < len(secs) and secs[i]["t"] < m:
            s = secs[i]; i += 1
            for k in ("br", s["uf"]):
                c = cum.setdefault(k, [0, 0, 0]); c[0] += 1; c[1] += s["L"]; c[2] += s["F"]
        c = cum["br"]
        linhas_br.append([hms(m), c[0], round(c[0] / TOTAL * 100, 3), c[1], c[2], r3(share(c[1], c[2]))])
        for u in sorted(tot["secoes"]):
            c = cum.get(u, [0, 0, 0])
            linhas_uf.append([hms(m), u, c[0], round(c[0] / tot["secoes"][u] * 100, 3), c[1], c[2], r3(share(c[1], c[2]))])
    grava("curva_br_minuto.csv", ["recebido_antes_de", "secoes", "pct_secoes", "lula", "flavio", "lula_pct"], linhas_br)
    grava("curva_uf_minuto.csv", ["recebido_antes_de", "uf", "secoes", "pct_secoes", "lula", "flavio", "lula_pct"], linhas_uf)

    # 2) conferência: cada leitura gravada contra o instante reconstruído com o mesmo % apurado
    alvo = sorted((min(len(secs), max(1, -int(-(h["pst"] - 0.005) * TOTAL // 100))), k) for k, h in enumerate(hist))
    est = Estado(tot, base); j = 0; rec = {}
    for n, k in alvo:
        while est.n < n: est.add(secs[j]); j += 1
        rec[k] = (secs[j - 1]["t"], est.conta())
    conf = []
    for k, h in enumerate(hist):
        t, r = rec[k]
        conf.append(dict(hora_tse=h["hora"], pst=h["pst"], hora_recebido=hms(t), atraso_s=h["t"] - t, lula_gravado=h["s2"], lula_reconst=r["s2"],
                         dif_lula=round(r["s2"] - h["s2"], 3), s1eq_gravado=h["s1eq"], s1eq_reconst=r["s1eq"], dif_s1eq=round(r["s1eq"] - h["s1eq"], 3),
                         proj_gravada=h["proj"], proj_reconst=r["proj"], dif_proj=round(r["proj"] - h["proj"], 3)))
    grava("conferencia_leituras.csv", list(conf[0].keys()), [list(c.values()) for c in conf])
    c114 = conf[:-1]
    at = [c["atraso_s"] for c in c114]; med = st.median(at); q = st.quantiles(at, n=4)
    dl = [abs(c["dif_lula"]) for c in c114]; ds = [abs(c["dif_s1eq"]) for c in c114]; dp = [abs(c["dif_proj"]) for c in c114]
    resumo.update(atraso_mediana_s=med, atraso_quartis_s=[q[0], q[2]], atraso_min_max_s=[min(at), max(at)],
                  leituras_atraso_ate_3min_da_mediana=sum(abs(a - med) <= 180 for a in at),
                  fora=[(c["hora_tse"], c["atraso_s"]) for c in c114 if abs(c["atraso_s"] - med) > 180],
                  dif_lula_mediana=st.median(dl), dif_lula_max=max(dl), leituras_dif_lula_ate_010=sum(v <= 0.10 for v in dl), n=len(c114),
                  dif_s1eq_mediana=st.median(ds), dif_s1eq_max=max(ds),
                  dif_proj_mediana=st.median(dp), dif_proj_maiores=sorted(((abs(c["dif_proj"]), c["hora_tse"]) for c in c114), reverse=True)[:5])
    resumo["bate"] = (abs(resumo["cond0"]["lula"] - 51.785) < 0.0005 and resumo["dif_lula_mediana"] <= 0.05
                      and resumo["leituras_dif_lula_ate_010"] >= 0.9 * len(c114) and resumo["leituras_atraso_ate_3min_da_mediana"] >= 0.9 * len(c114))

    # 3) leituras reconstruídas: as 114 gravadas (no mesmo % apurado) e o buraco, a cada 30 s (hora divulgada = recebido + atraso mediano)
    pontos = [("gravada", h["hora"], rec[k][0]) for k, h in enumerate(hist[:-1])]
    a, b = seg("20:36:09"), seg("20:43:00")
    pontos += [("buraco", hms(x), x - med) for x in range(a + 30, b, 30)]
    pontos.sort(key=lambda p: p[2])
    est = Estado(tot, base); j = 0; out_br, out_uf = [], []
    for tipo, hora, trec in pontos:
        alvo_n = next((n for n, k in alvo if hist[k]["hora"] == hora), None) if tipo == "gravada" else None
        while j < len(secs) and (est.n < alvo_n if alvo_n else secs[j]["t"] <= trec): est.add(secs[j]); j += 1
        r = est.conta()
        out_br.append([tipo, hora, hms(trec), r["pst"], r["L2"], r["F2"], r["s2"], r["s1eq"], r["proj"]])
        for u, d in sorted(r["uf"].items()):
            out_uf.append([tipo, hora, u, d["pst"], d["L2"], d["F2"], d["s2"], d["s1eq"], d["s1fin"]])
    grava("leituras_br.csv", ["tipo", "hora_tse", "hora_recebido", "pct_secoes", "lula", "flavio", "lula_pct", "lula_1t_mesmas_urnas_pct", "projecao_pct"], out_br)
    grava("leituras_uf.csv", ["tipo", "hora_tse", "uf", "pct_secoes", "lula", "flavio", "lula_pct", "lula_1t_mesmas_urnas_pct", "lula_1t_final_pct"], out_uf)

    # 4) estados no último retrato (21:14:00, 99,77%) contra a reconstrução no mesmo % apurado
    ult = json.load(open(os.path.join(DADOS, "ultimo_retrato_2t.json"), encoding="utf-8"))
    k = next(k for k, h in enumerate(hist) if h["hora"] == ult["hg"]); r = rec[k][1]
    e = {u: dict(pst_gravado=ult["uf"][u]["pst"], pst_reconst=r["uf"][u]["pst"], lula_gravado=ult["uf"][u]["s2"], lula_reconst=r["uf"][u]["s2"]) for u in sorted(ult["uf"])}
    resumo["estados_21h14_max"] = dict(dif_lula=round(max(abs(v["lula_gravado"] - v["lula_reconst"]) for v in e.values()), 3),
                                       dif_pst=round(max(abs(v["pst_gravado"] - v["pst_reconst"]) for v in e.values()), 2))
    resumo["estados_21h14"] = e
    json.dump(resumo, open(os.path.join(SAI, "conferencia.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in resumo.items() if k != "estados_21h14"}, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
