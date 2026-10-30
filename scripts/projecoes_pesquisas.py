# T41, exploração: a média das últimas pesquisas como ponto de partida das projeções (b), (c) e (d).
# Passo 1 (um_turno): o 1º turno de presidente e governador (2022 e 2026, as UFs com 2º turno) com a base da eleição de 4 anos
# antes, pelas funções de projecoes_teste2022.py (montar, avaliar) e projecoes_2t.py, sem mudança.
# Passo 2 (testar): a média das pesquisas (dados/pesquisas/pesquisas.csv) combinada com cada método, P = w·q + (1 − w)·M,
# w = σ_m² / (σ_m² + σ_q²), w = 0 a partir de 50% apurado; σ_m e σ_q sempre medidos deixando um cargo ou um ano de fora.
# Regras: ticket T41, "Pesquisas como ponto de partida". Uso:
#   python -I scripts/projecoes_pesquisas.py um_turno   (~30 min; grava dados/projecoes_outras/pesquisas_1t_instantes.csv)
#   python -I scripts/projecoes_pesquisas.py testar     (grava dados/projecoes_outras/pesquisas_*.json e pesquisas_2t_instantes.csv)
import os, sys, re, csv, json, math, datetime, statistics, collections
import numpy as np
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
from projecoes_teste2022 import montar, avaliar
from projecoes_senador import ler_zip, chave, seg_data
import regra_chamada as rch
DADOS = os.path.join(AQUI, "..", "dados"); SAI = os.path.join(DADOS, "projecoes_outras"); PESQ = os.path.join(DADOS, "pesquisas")
PASTA = {2018: "tse_2018", 2022: "tse_2022", 2026: "tse_secoes"}
UFS = {2022: ["AL", "AM", "BA", "ES", "MS", "PB", "PE", "RO", "RS", "SC", "SE", "SP"], 2026: ["AC", "AM", "DF", "ES", "RN", "TO"]}
BN = ("95", "96", "97")
STOP = {"de", "da", "do", "dos", "das", "e", "junior", "filho", "neto", "silva", "santos", "souza", "sousa", "oliveira", "ferreira", "lima", "costa"}

# ---------- passo 1: 1º turno com a base de 4 anos antes ----------
def zip_votos(ano, uf):
    if ano == 2026 and uf != "BR": return os.path.join(DADOS, "tse_secoes_gov", f"votacao_secao_2026_{uf}.zip")
    return os.path.join(DADOS, PASTA[ano], f"votacao_secao_{ano}_{uf}.zip")

def votos(ano, uf, cargos):
    """1º turno por seção: {cargo: {seção: Counter(número → votos)}} e os nomes; deputado federal (6) somado por partido."""
    v = {c: collections.defaultdict(collections.Counter) for c in cargos}; nomes = {c: {} for c in cargos}
    for g in ler_zip(zip_votos(ano, uf)):
        c = g("CD_CARGO")
        if c not in v or g("NR_TURNO") != "1": continue
        n = g("NR_VOTAVEL")
        if c == "6" and n not in BN: n = n[:2]
        v[c][chave(g)][n] += int(g("QT_VOTOS")); nomes[c][n] = g("NM_VOTAVEL")
    return v, nomes

def detalhe(ano, uf, cargo):
    """1º turno: (hora de recebimento, aptos, comparecimento) por seção; no presidente, o arquivo _BR (todas as UFs e o exterior)."""
    d = {}
    for g in ler_zip(os.path.join(DADOS, PASTA[ano], f"detalhe_votacao_secao_{ano}.zip"), so=f"_{uf}.csv"):
        if g("NR_TURNO") != "1" or g("CD_CARGO") != cargo: continue
        d[chave(g)] = (seg_data(g("DT_RECEBIMENTO_BU_HOR_TSE")), int(g("QT_APTOS")), int(g("QT_COMPARECIMENTO")))
    return d

def palavras(s):
    import unicodedata
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()
    return {t for t in re.findall(r"[a-z]+", s) if len(t) >= 3 and t not in STOP}

def antecessor(num, nome, ant_cargo, ant_nomes, outros):
    """Quem, na eleição anterior, faz o papel do candidato: o mesmo nome (2 palavras), o mesmo partido no cargo, ou o partido em outro cargo."""
    tot = collections.Counter()
    for v in ant_cargo.values(): tot.update(v)
    for n, nm in ant_nomes.items():
        if n not in BN and len(palavras(nm) & palavras(nome)) >= 2: return ("mesmo candidato", ant_cargo, n, nm)
    if num[:2] in ant_nomes: return ("mesmo partido", ant_cargo, num[:2], ant_nomes[num[:2]])
    for rot, (vv, nn) in outros:
        if num[:2] in nn: return (rot, vv, num[:2], f"partido {num[:2]}" if "deputado" in rot else nn[num[:2]])
    return ("sem antecessor", ant_cargo, None, "")

def base_secoes(bu, A, B, ant_A, ant_B, ant_cargo, det_ant):
    """Base de cada seção do 1º turno atual: a mesma seção na eleição anterior, com os antecessores de A e B nas chaves A e B;
    seção nova: a soma do município (senão da UF) na proporção do eleitorado. Devolve (v1, det) no formato de montar()."""
    def linha(k):
        c = collections.Counter({(("x" + n) if n in (A, B) else n): q for n, q in ant_cargo.get(k, {}).items() if n not in (ant_A[2], ant_B[2])})
        c[A] = ant_A[1].get(k, {}).get(ant_A[2], 0) if ant_A[2] else 0
        c[B] = ant_B[1].get(k, {}).get(ant_B[2], 0) if ant_B[2] else 0
        return c
    v1 = {}; det = {}; soma = {}; sdet = {}
    for k in set(ant_cargo) | set(det_ant):
        c = linha(k)
        for g in (k[1], k[0]):
            soma.setdefault(g, collections.Counter()).update(c)
            a = det_ant.get(k, (0, 0, 0)); s = sdet.setdefault(g, [0, 0]); s[0] += a[1]; s[1] += a[2]
    novas = collections.Counter()
    for k, s in bu.items():
        if k in ant_cargo and k in det_ant:
            v1[k] = linha(k); det[k] = det_ant[k][1:]; continue
        g = k[1] if k[1] in soma and sdet[k[1]][0] > 0 else k[0]
        f = s["aptos"] / sdet[g][0] if sdet.get(g, [0])[0] > 0 else 0
        v1[k] = collections.Counter({n: q * f for n, q in soma.get(g, {}).items()})
        det[k] = (s["aptos"], sdet[g][1] * f if g in sdet else 0); novas["município" if g == k[1] else "UF"] += 1
    return v1, det, dict(novas)

def um_turno():
    so = sys.argv[2] if len(sys.argv) > 2 else None   # só uma disputa, para conferir (não grava)
    linhas, resumo = [], {}
    for ano in (2022, 2026):
        ant = ano - 4
        tarefas = [(f"presidente_{ano}_1t", "1", "BR")] + [(f"governador_{ano}_{uf}_1t", "3", uf) for uf in UFS[ano]]
        pres_ant = None
        for nome, cargo, uf in tarefas:
            if so and so != nome: continue
            if cargo == "1":
                cur, nomes_cur = votos(ano, "BR", ("1",)); ant_v, ant_n = votos(ant, "BR", ("1",)); outros = []
            else:
                cur, nomes_cur = votos(ano, uf, ("3",)); ant_v, ant_n = votos(ant, uf, ("3", "6"))
                if pres_ant is None:
                    pv, pn = votos(ant, "BR", ("1",)); pres_ant = (pv["1"], pn["1"])
                pv_uf = {k: v for k, v in pres_ant[0].items() if k[0] == uf.lower()}
                outros = [("partido para presidente", (pv_uf, pres_ant[1])), ("partido para deputado federal", (ant_v["6"], ant_n["6"]))]
            dcur = detalhe(ano, uf, cargo); dant = detalhe(ant, uf, cargo)
            bu = {k: dict(t=dcur[k][0], aptos=dcur[k][1], v={n: q for n, q in vv.items() if n not in BN})
                  for k, vv in cur[cargo].items() if k in dcur and np.isfinite(dcur[k][0])}
            par = next((d["A"], d["B"]) for d in csv.DictReader(open(os.path.join(PESQ, "disputas.csv"), encoding="utf-8"), delimiter=";") if d["disputa"] == nome)
            for s in bu.values(): s["v"] = {n: q for n, q in s["v"].items() if n in par}   # o par do 2º turno (regra; em SE 2022 o 22 teve os votos anulados)
            tot = collections.Counter()
            for s in bu.values(): tot.update(s["v"])
            A, B = [n for n, _ in tot.most_common(2)]
            aA = antecessor(A, nomes_cur[cargo][A], ant_v[cargo], ant_n[cargo], outros)
            aB = antecessor(B, nomes_cur[cargo][B], ant_v[cargo], ant_n[cargo], outros)
            v1, det, novas = base_secoes(bu, A, B, aA, aB, ant_v[cargo], dant)
            S, secs, base, totp, info = montar(nome, bu, v1, det)
            assert (info["A"], info["B"]) == (A, B)
            L, R = avaliar(S, secs, base, totp, info)
            R.update(antecessor_A=f"{aA[3]} ({aA[2]}, {aA[0]})", antecessor_B=f"{aB[3]} ({aB[2]}, {aB[0]})",
                     nome_A=nomes_cur[cargo][A], nome_B=nomes_cur[cargo][B], secoes_novas=novas,
                     sem_hora=sum(1 for k in cur[cargo] if k not in dcur or not np.isfinite(dcur[k][0])))
            linhas += L; resumo[nome] = R
            print(nome, A, B, R["final"], R["antecessor_A"], "|", R["antecessor_B"], novas,
                  {m: (x["abs_medio"], x["passa_a_acertar"]) for m, x in R["metodos"].items() if m in "bcd"}, flush=True)
    if so: return
    cab = ["disputa", "pst", "hora", "n", "contagem", "b", "c", "c_lo", "c_hi", "d", "d_lo", "d_hi", "final"]
    with open(os.path.join(SAI, "pesquisas_1t_instantes.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";"); w.writerow(cab)
        for d in linhas: w.writerow([round(d[k], 4) if isinstance(d[k], float) else d[k] for k in cab])
    json.dump(resumo, open(os.path.join(SAI, "pesquisas_1t_base_resumo.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=lambda o: o.item())

# ---------- passo 2: o ponto de partida das pesquisas ----------
INST = ["datafolha", "ibope", "ipec", "quaest", "atlas", "parana", "mda", "realtime", "real time", "ipespe", "futura", "gerp", "poderdata",
        "nexus", "palver", "verita", "ifp", "ideia", "vox", "badra", "ipri", "brasmarket", "datatempo", "radar", "ibpe", "doxa", "fespsp",
        "anza", "seta", "opiniao", "dataqualy", "potencial", "instituto mapa", "agora", "ranking", "consult", "item", "dados", "veritá"]
def instituto(s):
    import unicodedata
    t = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()
    for x in INST:
        if x in t: return x.replace(" ", "")
    return re.sub(r"\s+", " ", t.split("/")[-1]).strip()

def medias():
    """q (% de A entre A e B) por disputa, pela janela e pelos pesos da regra; e as pesquisas usadas."""
    R = collections.defaultdict(list)
    for arq in ("pesquisas.csv", "pesquisas_extra.csv"):   # extra: busca manual nos jornais, para as cidades sem tabela na Wikipédia
        if not os.path.exists(os.path.join(PESQ, arq)): continue
        for r in csv.DictReader(open(os.path.join(PESQ, arq), encoding="utf-8"), delimiter=";"):
            R[r["disputa"]].append(r)
    out = {}
    for disp, L in R.items():
        D = datetime.date.fromisoformat(L[0]["data_eleicao"])
        dias = lambda r: (D - datetime.date.fromisoformat(r["campo_fim"])).days
        J = [r for r in L if 1 <= dias(r) <= 10] or [r for r in L if 1 <= dias(r) <= 21]
        if not J: continue
        por = collections.defaultdict(list)
        for r in J: por[instituto(r["instituto"])].append(r)
        ult = []
        for i, rs in por.items():
            fim = max(r["campo_fim"] for r in rs); rs = [r for r in rs if r["campo_fim"] == fim]
            am = [int(r["amostra"]) for r in rs if r["amostra"]]
            q = statistics.mean(100 * float(r["pct_A"]) / (float(r["pct_A"]) + float(r["pct_B"])) for r in rs)
            ult.append(dict(instituto=i, fim=fim, q=q, amostra=statistics.mean(am) if am else None))
        med = statistics.median([u["amostra"] for u in ult if u["amostra"]]) if any(u["amostra"] for u in ult) else 1000
        pesos = [math.sqrt(min(u["amostra"] or med, 5000)) for u in ult]
        out[disp] = dict(q=sum(p * u["q"] for p, u in zip(pesos, ult)) / sum(pesos), institutos=len(ult), pesquisas=len(J),
                         janela=10 if all(1 <= dias(r) <= 10 for r in J) else 21, usadas=ult)
    return out

FX = [1, 2.5, 5, 10, 20, 40, 60, 80, 100]
def fx(p): return next(i for i, a in enumerate(FX) if p <= a)

def disputas():
    """{disputa: dict(turno, cargo, ano, final, L=[{pst, b, c, d}])}: as 86 do 2º turno (as mesmas da regra de chamada) e as 20 do 1º."""
    G = rch.disputas(); D = {}
    for grupo in ("dentro", "fora"):
        for nome, (final, L) in G[grupo].items():
            p = nome.split("_"); D[nome] = dict(turno=2, cargo=p[0], ano=p[1], final=final, L=sorted(L, key=lambda d: d["pst"]))
    p1 = os.path.join(SAI, "pesquisas_1t_instantes.csv")
    if os.path.exists(p1):
        for r in csv.DictReader(open(p1, encoding="utf-8"), delimiter=";"):
            p = r["disputa"].split("_")
            d = D.setdefault(r["disputa"], dict(turno=1, cargo=p[0], ano=p[1], final=float(r["final"]), L=[]))
            d["L"].append({k: float(r[k]) for k in ("pst", "b", "c", "d")})
    return D

def sigma_m(D, nomes, m):
    """Erro típico do método por faixa: raiz do erro quadrático médio, média por disputa dentro da faixa, depois entre disputas."""
    s = []
    for i in range(len(FX)):
        por = [np.mean([(x[m] - D[n]["final"]) ** 2 for x in D[n]["L"] if fx(x["pst"]) == i]) for n in nomes
               if any(fx(x["pst"]) == i for x in D[n]["L"])]
        s.append(math.sqrt(np.mean(por)) if por else None)
    return s

def sigma_q(D, Q, nomes):
    e = [(Q[n]["q"] - D[n]["final"]) ** 2 for n in nomes if n in Q]
    return max(1.0, math.sqrt(np.mean(e))) if e else None

def combina(D, Q, teste, treino):
    """Instantes com o ponto de partida para as disputas de teste, com σ medidos no treino."""
    sm = {m: sigma_m(D, treino, m) for m in "bcd"}; sq = sigma_q(D, Q, treino); out = {}
    for n in teste:
        q = Q.get(n, {}).get("q"); L = []
        for x in D[n]["L"]:
            y = dict(pst=x["pst"])
            for m in "bcd":
                s = sm[m][fx(x["pst"])]
                w = 0.0 if q is None or sq is None or x["pst"] >= 50 or not s else s * s / (s * s + sq * sq)
                y[m] = x[m] if w == 0 else w * q + (1 - w) * x[m]; y["w_" + m] = w
            L.append(y)
        out[n] = L
    return out, dict(sigma_q=sq, sigma_m={m: [None if v is None else round(v, 3) for v in sm[m]] for m in "bcd"})

def wilson(x, n, z=1.959964):
    if n == 0: return None
    p = x / n; c = (p + z * z / (2 * n)) / (1 + z * z / n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [round(max(0, c - h), 4), round(min(1, c + h), 4)]

def acerta_desde(L, final, m):
    lado = (lambda v: v > 50) if final > 50 else (lambda v: v < 50)
    ac = [lado(d[m]) and abs(d[m] - final) <= 0.5 for d in L]
    k = next((i for i in range(len(L)) if all(ac[i:])), None)
    return None if k is None else L[k]["pst"]

def medidas(D, inst, nomes):
    """Desde quando acerta, erro por faixa e a regra de chamada, para um conjunto de disputas (instantes dados em inst)."""
    res = dict(disputas=len(nomes))
    for m in "bcd":
        desde = [acerta_desde(inst[n], D[n]["final"], m) for n in nomes]
        ok = [x for x in desde if x is not None]
        res["acerta_desde_" + m] = dict(mediana=statistics.median(ok) if ok else None, ate_1=sum(x <= 1 for x in ok), ate_5=sum(x <= 5 for x in ok),
                                       ate_10=sum(x <= 10 for x in ok), nunca=len(desde) - len(ok))
        fa = []
        for i in range(len(FX)):
            por = [np.mean([abs(x[m] - D[n]["final"]) for x in inst[n] if fx(x["pst"]) == i]) for n in nomes if any(fx(x["pst"]) == i for x in inst[n])]
            fa.append(round(float(np.mean(por)), 3) if por else None)
        res["erro_abs_faixa_" + m] = fa
    Dm = {n: (D[n]["final"], inst[n]) for n in nomes}
    for r, ms in rch.REGRAS.items():
        for X in rch.XS:
            x = rch.medir(Dm, ms, X)
            res[f"{r}|{X}"] = dict(chamadas=x["chamadas"], erradas=x["chamadas_erradas"], quais=x["quais_erradas"],
                                   taxa=round(x["chamadas_erradas"] / x["chamadas"], 4) if x["chamadas"] else None,
                                   ic95=wilson(x["chamadas_erradas"], x["chamadas"]), pst_mediana=x["chamada_pst_mediana"],
                                   pst_max=x["chamada_pst_max"], instantes_errados=x["instantes_errados"], ate_50=x["chamadas_ate_50"])
    return res

def testar():
    D = disputas(); Q = medias()
    Q = {n: v for n, v in Q.items() if n in D}
    # no 1º turno, o A das projeções é o mais votado no 1º turno; o das pesquisas, o do disputas.csv (o mais votado no 2º): alinhar
    A_pesq = {d["disputa"]: d["A"] for d in csv.DictReader(open(os.path.join(PESQ, "disputas.csv"), encoding="utf-8"), delimiter=";")}
    p1 = os.path.join(SAI, "pesquisas_1t_base_resumo.json")
    for n, r in (json.load(open(p1, encoding="utf-8")).items() if os.path.exists(p1) else []):
        if n in Q and r["A"] != A_pesq[n]:
            Q[n] = dict(Q[n], q=100 - Q[n]["q"], usadas=[dict(u, q=100 - u["q"]) for u in Q[n]["usadas"]], invertida=True)
    out = dict(regras="ticket T41, 'Pesquisas como ponto de partida'", medias={}, turnos={})
    for n in sorted(D):
        x = Q.get(n)
        out["medias"][n] = None if not x else dict(q=round(x["q"], 2), final=D[n]["final"], erro=round(x["q"] - D[n]["final"], 2),
                                                   acerta_vencedor=(x["q"] > 50) == (D[n]["final"] > 50), institutos=x["institutos"],
                                                   pesquisas=x["pesquisas"], janela_dias=x["janela"], usadas=x["usadas"])
    linhas = []
    for turno in (2, 1):
        T = [n for n in D if D[n]["turno"] == turno]
        if not T: continue
        com = [n for n in T if n in Q]
        R = out["turnos"][str(turno)] = dict(disputas=len(T), com_pesquisa=len(com), sem_pesquisa=sorted(set(T) - set(com)))
        e = [Q[n]["q"] - D[n]["final"] for n in com]
        R["panorama"] = dict(erro_medio=round(float(np.mean(e)), 2), erro_abs_medio=round(float(np.mean(np.abs(e))), 2),
                             rmse=round(math.sqrt(np.mean(np.square(e))), 2), vencedor_certo=sum((Q[n]["q"] > 50) == (D[n]["final"] > 50) for n in com),
                             quais_erram=[f"{n} (q {Q[n]['q']:.1f}, final {D[n]['final']:.1f})" for n in com if (Q[n]["q"] > 50) != (D[n]["final"] > 50)])
        sem = {n: D[n]["L"] for n in T}
        R["sem_pesquisas"] = dict(todas=medidas(D, sem, T), com_pesquisa=medidas(D, sem, com))
        for esquema, chave_g in (("por_cargo", "cargo"), ("por_ano", "ano")):
            grupos = sorted({D[n][chave_g] for n in T}); inst = {}; rod = {}
            for g in grupos:
                teste = [n for n in T if D[n][chave_g] == g]; treino = [n for n in T if D[n][chave_g] != g]
                o, s = combina(D, Q, teste, treino); inst.update(o)
                rod[g] = dict(teste=len(teste), treino=len(treino), com_pesquisa=sum(n in Q for n in teste), **s)
            R[esquema] = dict(rodadas=rod, todas=medidas(D, inst, T), com_pesquisa=medidas(D, inst, com))
            if esquema == "por_cargo":
                for n in T:
                    for x, y in zip(D[n]["L"], inst[n]):
                        linhas.append(dict(disputa=n, turno=turno, pst=x["pst"], final=D[n]["final"], q=Q.get(n, {}).get("q", ""),
                                           **{m: x[m] for m in "bcd"}, **{m + "_p": y[m] for m in "bcd"}, **{"w_" + m: y["w_" + m] for m in "bcd"}))
    json.dump(out, open(os.path.join(SAI, "pesquisas_resumo.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=float)
    cab = ["disputa", "turno", "pst", "final", "q", "b", "c", "d", "b_p", "c_p", "d_p", "w_b", "w_c", "w_d"]
    with open(os.path.join(SAI, "pesquisas_instantes.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";"); w.writerow(cab)
        for d in linhas: w.writerow([round(d[k], 4) if isinstance(d[k], float) else d[k] for k in cab])
    for t, R in out["turnos"].items():
        print(f"== {t}º turno: {R['disputas']} disputas, {R['com_pesquisa']} com pesquisa; panorama {R['panorama']}")
        for nome, M in [("sem", R["sem_pesquisas"])] + [(e, R[e]) for e in ("por_cargo", "por_ano")]:
            for sub in ("todas", "com_pesquisa"):
                x = M[sub]
                print(f"  {nome:9} {sub:12}", {m: x["acerta_desde_" + m] ["mediana"] for m in "bcd"},
                      {k: (v["erradas"], v["chamadas"], v["pst_mediana"]) for k, v in x.items() if "|" in k})
        for e in ("por_cargo", "por_ano"):
            print("  ", e, {g: (r["sigma_q"] and round(r["sigma_q"], 2), r["sigma_m"]["d"][:4]) for g, r in R[e]["rodadas"].items()})

if __name__ == "__main__":
    {"um_turno": um_turno, "testar": testar}[sys.argv[1]]()
