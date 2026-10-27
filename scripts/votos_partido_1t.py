# Soma os votos por partido do 1º turno de 2026 (eleição 6259, cargos estaduais) por município × cargo, a partir dos dados abertos do TSE (T04).
# Lê os 27 CSV dos estados direto do zip: o BRASIL.csv repete os estados e o BR.csv é o presidente. Soma as zonas e o voto em trânsito,
# registra também por federação e, se receber a pasta dos JSON oficiais por estado (scripts/tse6259_uf.py), confere estado × cargo.
# Uso: python -I scripts/votos_partido_1t.py <votacao_partido_munzona_2026.zip> <votos_partido_1t.json> [dados/tse_6259_uf]
import sys, os, io, re, csv, json, zipfile, hashlib, time
ZIP, OUT = sys.argv[1], sys.argv[2]
OFI = sys.argv[3] if len(sys.argv) > 3 else None
DADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dados")
MUN = os.path.join(DADOS, "tse_config", "mun-e006258-cm.json")
BASE1T = os.path.join(DADOS, "base_1t_municipios.json")
URL = "https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_partido_munzona/votacao_partido_munzona_2026.zip"
CARGOS = {
    "3": {"nome": "Governador", "na_especificacao": False, "nota": "Vem no mesmo arquivo; guardado, mas fora da especificação (seção 6)."},
    "5": {"nome": "Senador", "na_especificacao": True, "votos_por_eleitor": 2, "nota": "Duas vagas em 2026: cada eleitor podia votar em dois candidatos. Os votos são somados, por isso os válidos passam do comparecimento."},
    "6": {"nome": "Deputado Federal", "na_especificacao": True},
    "7": {"nome": "Deputado Estadual", "na_especificacao": True, "nota": "Não existe no DF, que elege deputado distrital (cargo 8)."},
    "8": {"nome": "Deputado Distrital", "na_especificacao": True, "nota": "Só no DF; ocupa o lugar do deputado estadual."},
}
def log(*a): print(*a, flush=True)
def num(s): return int(s) if s not in (None, "") else 0

# --- leitura e soma ---
z = zipfile.ZipFile(ZIP)
ufs = sorted(n[-6:-4] for n in z.namelist() if re.fullmatch(r"votacao_partido_munzona_2026_[A-Z]{2}\.csv", n) and n[-6:-4] != "BR")
assert len(ufs) == 27, ufs
mu, partidos, feds, geracao, zonas = {}, {}, {}, set(), set()
linhas = transito = 0
for uf in ufs:
    with io.TextIOWrapper(z.open(f"votacao_partido_munzona_2026_{uf}.csv"), encoding="latin-1", newline="") as f:
        for x in csv.DictReader(f, delimiter=";"):
            linhas += 1
            if (x["NR_TURNO"], x["CD_ELEICAO"], x["SG_UF"]) != ("1", "6259", uf): raise SystemExit(f"linha inesperada em {uf}: {x}")
            c = x["CD_CARGO"]
            if c not in CARGOS: raise SystemExit(f"cargo inesperado {c} em {uf}")
            p, fd = x["NR_PARTIDO"], (None if x["NR_FEDERACAO"] == "-1" else x["NR_FEDERACAO"])
            info = {"sg": x["SG_PARTIDO"], "nm": x["NM_PARTIDO"], "fed": fd}
            if partidos.setdefault(p, info) != info: raise SystemExit(f"partido {p} muda de nome ou federação: {partidos[p]} × {info}")
            if fd:
                fi = {"sg": x["SG_FEDERACAO"], "nm": x["NM_FEDERACAO"], "composicao": x["DS_COMPOSICAO_FEDERACAO"]}
                if feds.setdefault(fd, fi) != fi: raise SystemExit(f"federação {fd} muda: {feds[fd]} × {fi}")
            n, l = num(x["QT_VOTOS_NOMINAIS_VALIDOS"]), num(x["QT_TOTAL_VOTOS_LEG_VALIDOS"])
            if x["ST_VOTO_EM_TRANSITO"] != "N": transito += n + l
            cd = x["CD_MUNICIPIO"].zfill(5)
            m = mu.setdefault(cd, {"uf": uf.lower(), "nm": x["NM_MUNICIPIO"], "c": {}})
            if m["uf"] != uf.lower(): raise SystemExit(f"município {cd} em dois estados")
            v = m["c"].setdefault(c, {}).setdefault(p, [0, 0, 0, 0])
            v[0] += n; v[1] += l
            v[2] += num(x["QT_VOTOS_NOMINAIS_ANUL_SUBJUD"]) + num(x["QT_VOTOS_LEGENDA_ANUL_SUBJUD"])
            v[3] += num(x["QT_VOTOS_NOMINAIS_ANULADOS"]) + num(x["QT_VOTOS_LEGENDA_ANULADOS"])
            geracao.add(x["DT_GERACAO"] + " " + x["HH_GERACAO"]); zonas.add((uf, x["NR_ZONA"]))
log(f"linhas {linhas}, municípios {len(mu)}, zonas {len(zonas)}, partidos {len(partidos)}, federações {len(feds)}, voto em trânsito {transito}")

def bloco(pv):
    # pv: {partido: [nominais, legenda, anulados sub judice, anulados]} -> totais, partidos, federações e anulados (só os diferentes de zero)
    ks = sorted(pv, key=int)
    p = {k: pv[k][:2] for k in ks}
    f = {}
    for k, (n, l) in p.items():
        fd = partidos[k]["fed"]
        if fd: a = f.setdefault(fd, [0, 0]); a[0] += n; a[1] += l
    n, l = sum(v[0] for v in p.values()), sum(v[1] for v in p.values())
    b = {"vv": n + l, "n": n, "l": l, "p": p, "f": {k: f[k] for k in sorted(f, key=int)}}
    sj, an = {k: pv[k][2] for k in ks if pv[k][2]}, {k: pv[k][3] for k in ks if pv[k][3]}
    if sj: b["sj"] = sj
    if an: b["an"] = an
    return b
def soma(lista):
    t = {}
    for pv in lista:
        for k, v in pv.items():
            a = t.setdefault(k, [0, 0, 0, 0])
            for i in range(4): a[i] += v[i]
    return t

out_mu = {cd: {"uf": m["uf"], "nm": m["nm"], "c": {c: bloco(m["c"][c]) for c in sorted(m["c"], key=int)}} for cd, m in sorted(mu.items())}
out_uf = {}
for u in sorted({m["uf"] for m in mu.values()}):
    cs = sorted({c for m in mu.values() if m["uf"] == u for c in m["c"]}, key=int)
    out_uf[u] = {c: bloco(soma(m["c"][c] for m in mu.values() if m["uf"] == u and c in m["c"])) for c in cs}
out_br = {c: bloco(soma(m["c"][c] for m in mu.values() if c in m["c"])) for c in sorted(CARGOS, key=int)}

# --- conferência: todos os municípios do Brasil aparecem em todos os cargos ---
tse = json.load(open(MUN, encoding="utf-8"))
tse_br = {m["cd"]: (a["cd"], m["nm"]) for a in tse["abr"] if a["cd"] != "zz" for m in a["mu"]}
tse_zz = sum(len(a["mu"]) for a in tse["abr"] if a["cd"] == "zz")
base = json.load(open(BASE1T, encoding="utf-8"))
base_br = {cd for cd, m in base["mu"].items() if m["uf"] != "zz"}
erros = []
if set(mu) != set(tse_br): erros.append(f"municípios: {len(set(tse_br) - set(mu))} da lista do TSE faltam no CSV, {len(set(mu) - set(tse_br))} do CSV não estão na lista")
if base_br != set(tse_br): erros.append(f"base do 1º turno e lista do TSE diferem em {len(base_br ^ set(tse_br))} municípios")
for cd, (u, nm) in tse_br.items():
    if cd not in mu: continue
    if mu[cd]["uf"] != u: erros.append(f"{cd}: estado {mu[cd]['uf']} no CSV × {u} na lista")
    for c in ("3", "5", "6", "8" if u == "df" else "7"):
        if c not in mu[cd]["c"]: erros.append(f"{cd} {nm}-{u}: falta o cargo {c}")
nomes = [(cd, mu[cd]["nm"], tse_br[cd][1]) for cd in mu if cd in tse_br and mu[cd]["nm"] != tse_br[cd][1]]
# o CSV troca o apóstrofo por espaço (OLHO D ÁGUA); a saída usa o nome da lista do TSE, como a base do 1º turno
for cd in out_mu:
    if cd in tse_br: out_mu[cd]["nm"] = tse_br[cd][1]
mun_conf = {"lista_tse_brasil": len(tse_br), "lista_tse_exterior": tse_zz, "no_csv": len(mu), "base_1t_brasil": len(base_br),
            "todos_presentes_em_todos_os_cargos": not erros, "nomes_diferentes_da_lista": len(nomes)}
log(f"municípios: lista do TSE {len(tse_br)} no Brasil (+{tse_zz} no exterior, que não votam para estes cargos), no CSV {len(mu)}, base do 1º turno {len(base_br)}; nomes diferentes {len(nomes)}")
for e in erros[:20]: log("  ERRO", e)
for t in nomes[:10]: log("  nome", t)

# --- conferência: soma por estado e cargo × resultado oficial (campo v.vv), também partido por partido ---
conf, ok_total = [], True
if OFI:
    for u in out_uf:
        for c, b in out_uf[u].items():
            j = json.load(open(os.path.join(OFI, f"{u}-c{int(c):04d}-e006259-u.json"), encoding="utf-8"))
            v = j["v"]
            ofp = {}
            for a in j["carg"][0]["agr"]:
                for pp in a["par"]:
                    ofp[pp["n"]] = [num(pp.get("tvtn")), num(pp.get("tvtl"))]
            dif_p = {k: [b["p"].get(k, [0, 0]), ofp.get(k, [0, 0])] for k in set(b["p"]) | set(ofp)
                     if b["p"].get(k, [0, 0]) != ofp.get(k, [0, 0]) and (b["p"].get(k, [0, 0]) != [0, 0] or ofp.get(k, [0, 0]) != [0, 0])}
            r = {"uf": u, "cargo": c, "csv_vv": b["vv"], "oficial_vv": num(v["vv"]), "csv_nominais": b["n"], "oficial_vnom": num(v.get("vnom")),
                 "csv_legenda": b["l"], "oficial_vl": num(v.get("vl")), "partidos_divergentes": dif_p,
                 "csv_anulados_sub_judice": sum(b.get("sj", {}).values()), "oficial_vansj": num(v.get("vansj")),
                 "csv_anulados": sum(b.get("an", {}).values()), "oficial_van": num(v.get("van")),
                 "oficial_gerado": j.get("dg", "") + " " + j.get("hg", "")}
            r["confere"] = r["csv_vv"] == r["oficial_vv"] and r["csv_nominais"] == r["oficial_vnom"] and r["csv_legenda"] == r["oficial_vl"] and not dif_p
            r["anulados_conferem"] = r["csv_anulados_sub_judice"] == r["oficial_vansj"] and r["csv_anulados"] == r["oficial_van"]
            ok_total &= r["confere"]
            conf.append(r)
    log(f"\n{'UF':3} {'cargo':5} {'CSV vv':>12} {'oficial vv':>12} {'dif':>8}  partidos")
    for r in conf:
        log(f"{r['uf']:3} {r['cargo']:5} {r['csv_vv']:>12,} {r['oficial_vv']:>12,} {r['csv_vv'] - r['oficial_vv']:>8,}  {'ok' if not r['partidos_divergentes'] else r['partidos_divergentes']}".replace(",", "."))
    log(f"\nconferência por estado e cargo: {sum(r['confere'] for r in conf)} de {len(conf)} conferem (válidos, nominais, legenda e partido por partido)")
    log(f"anulados e anulados sub judice (informativo): {sum(r['anulados_conferem'] for r in conf)} de {len(conf)} conferem")
    for r in conf:
        if not r["anulados_conferem"]: log(f"  {r['uf']} {r['cargo']}: sub judice {r['csv_anulados_sub_judice']} × {r['oficial_vansj']}, anulados {r['csv_anulados']} × {r['oficial_van']}")

# --- saída ---
info_zip = os.stat(ZIP)
out = {
    "meta": {
        "descricao": "Votos válidos por partido no 1º turno de 2026 (eleição 6259), por município × cargo, com as federações. Cada partido: [nominais, legenda].",
        "fonte": URL,
        "arquivo": {"nome": os.path.basename(ZIP), "bytes": info_zip.st_size, "sha256": hashlib.sha256(open(ZIP, "rb").read()).hexdigest(),
                    "data_no_disco": time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(info_zip.st_mtime)),
                    "csv_gerado_pelo_tse": sorted(geracao), "csv_usados": [f"votacao_partido_munzona_2026_{u}.csv" for u in ufs]},
        "gerado_em": time.strftime("%d/%m/%Y %H:%M:%S"),
        "script": "scripts/votos_partido_1t.py",
        "campos": {
            "n": "votos nominais válidos (QT_VOTOS_NOMINAIS_VALIDOS)",
            "l": "votos de legenda válidos, incluindo nominais convertidos em legenda (QT_TOTAL_VOTOS_LEG_VALIDOS)",
            "vv": "votos válidos do cargo = n + l, igual ao campo v.vv do resultado oficial",
            "p": "por partido (número): [n, l]",
            "f": "por federação (número): [n, l], soma dos partidos da federação. Partidos fora de federação aparecem só em p",
            "sj": "por partido: votos anulados sub judice (nominais + legenda), só quando há. Não entram em vv; podem mudar com decisão judicial",
            "an": "por partido: votos anulados (nominais + legenda), só quando há. Não entram em vv",
            "c": "por cargo (código): 3 governador, 5 senador, 6 deputado federal, 7 deputado estadual, 8 deputado distrital",
            "mu": "chave = código TSE do município com 5 dígitos, o mesmo de tse_config/mun-e006258-cm.json e base_1t_municipios.json",
            "nm": "nome do município pela lista do TSE (o CSV troca o apóstrofo por espaço em 45 nomes, como OLHO D ÁGUA)",
            "br, uf": "somas do Brasil e de cada estado, no mesmo formato de cada município × cargo",
        },
        "ressalvas": [
            "Senador: duas vagas em 2026, cada eleitor votou duas vezes. Os votos são somados, então os válidos de senador passam do comparecimento.",
            "Governador (cargo 3) está guardado, mas fica fora da especificação.",
            "Somadas todas as zonas de cada município. O voto em trânsito entraria no município da linha; nesta versão do arquivo não há nenhuma linha de trânsito.",
            "Votos anulados e anulados sub judice ficam fora de vv, n, l, p e f, como no resultado oficial; estão à parte em sj e an. Onde um candidato teve muitos votos anulados sub judice, a fatia dos outros partidos entre os válidos fica maior.",
            "Os 186 municípios do exterior não aparecem: no exterior só se vota para presidente.",
        ],
        "voto_em_transito": transito,
        "linhas_csv": linhas,
        "zonas": len(zonas),
        "conferencia": {"municipios": mun_conf, "estado_cargo_confere": ok_total if OFI else None,
                        "estado_cargo": conf, "fonte_oficial": "https://resultados.tse.jus.br/oficial/ele2026/6259/dados/{uf}/{uf}-c000{3,5,6,7,8}-e006259-u.json"},
    },
    "cargos": CARGOS,
    "partidos": {k: partidos[k] for k in sorted(partidos, key=int)},
    "federacoes": {k: dict(feds[k], partidos=sorted((p for p in partidos if partidos[p]["fed"] == k), key=int)) for k in sorted(feds, key=int)},
    "br": out_br,
    "uf": out_uf,
    "mu": out_mu,
}
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
log(f"gravado {OUT}: {os.path.getsize(OUT) / 2**20:.1f} MB")
if erros or (OFI and not ok_total): sys.exit(1)
