# T41, pesquisas como ponto de partida: baixa as pesquisas eleitorais publicadas antes de cada disputa testada (2º turno: as 86
# disputas sem senador; 1º turno: presidente e governador de 2022 e 2026 nas mesmas UFs) das tabelas da Wikipédia (pt e en),
# que citam cada pesquisa. Cada página fica gravada como veio (dados/pesquisas/wiki/, com o número da revisão), e cada linha
# extraída leva o endereço da revisão e o link da referência da linha.
# Regras: ticket T41, "Pesquisas como ponto de partida". Uso:
#   python -I scripts/baixar_pesquisas.py disputas   (nomes dos candidatos e das cidades, dos arquivos do TSE em disco)
#   python -I scripts/baixar_pesquisas.py paginas    (busca e grava as páginas)
#   python -I scripts/baixar_pesquisas.py extrair    (lê as tabelas e grava dados/pesquisas/pesquisas.csv)
import os, sys, io, re, csv, json, glob, time, zipfile, datetime, unicodedata
AQUI = os.path.dirname(os.path.abspath(__file__)); DADOS = os.path.join(AQUI, "..", "dados")
SAI = os.path.join(DADOS, "pesquisas"); WIKI = os.path.join(SAI, "wiki"); OUT = os.path.join(DADOS, "projecoes_outras")
H = {"User-Agent": "apuracao-estudo/1.0 (estudo Analise da virada; https://github.com/MuriloNM/analise-da-virada)"}
DATAS = {2018: ("2018-10-07", "2018-10-28"), 2022: ("2022-10-02", "2022-10-30"), 2024: ("2024-10-06", "2024-10-27"), 2026: ("2026-10-04", "2026-10-25")}
UF_NOME = dict(AC=("Acre", "no Acre"), AL=("Alagoas", "em Alagoas"), AM=("Amazonas", "no Amazonas"), AP=("Amapá", "no Amapá"),
               BA=("Bahia", "na Bahia"), DF=("Distrito Federal", "no Distrito Federal"), ES=("Espírito Santo", "no Espírito Santo"),
               MG=("Minas Gerais", "em Minas Gerais"), MS=("Mato Grosso do Sul", "em Mato Grosso do Sul"), PA=("Pará", "no Pará"),
               PB=("Paraíba", "na Paraíba"), PE=("Pernambuco", "em Pernambuco"), RJ=("Rio de Janeiro", "no Rio de Janeiro"),
               RN=("Rio Grande do Norte", "no Rio Grande do Norte"), RO=("Rondônia", "em Rondônia"), RR=("Roraima", "em Roraima"),
               RS=("Rio Grande do Sul", "no Rio Grande do Sul"), SC=("Santa Catarina", "em Santa Catarina"), SE=("Sergipe", "em Sergipe"),
               SP=("São Paulo", "em São Paulo"), TO=("Tocantins", "no Tocantins"))
UF_EN = dict(AP="Amapá", DF="Federal District", ES="Espírito Santo", PA="Pará", PB="Paraíba", RO="Rondônia", SP="São Paulo")

def sem_acento(s): return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()

def ler_zip(zp, so=None):
    z = zipfile.ZipFile(zp)
    for n in z.namelist():
        if not n.lower().endswith(".csv") or (so and so not in n): continue
        f = io.TextIOWrapper(z.open(n), encoding="latin-1"); r = csv.reader(f, delimiter=";"); h = next(r)
        ix = {c.replace(" ", ""): i for i, c in enumerate(h)}
        for q in r: yield lambda c, q=q: q[ix[c]]

# ---------- disputas ----------
def disputas():
    """As 86 disputas do 2º turno (A e B dos resumos já gravados) e as 20 de 1º turno; nomes de urna dos arquivos do TSE."""
    D = []
    for arq in ("governador_2026_resumo", "teste2022_resumo", "teste2018_resumo", "teste2024_resumo"):
        for k, r in json.load(open(os.path.join(OUT, arq + ".json"), encoding="utf-8")).items():
            if k.startswith("_"): continue
            p = k.split("_"); cargo, ano = p[0], int(p[1])
            D.append(dict(disputa=k, turno=2, cargo=cargo, ano=ano, uf=p[2] if len(p) > 2 else "BR", mun=p[3] if len(p) > 3 else "",
                          A=r["A"], B=r["B"], final=r["final"]))
    D.insert(0, dict(disputa="presidente_2026", turno=2, cargo="presidente", ano=2026, uf="BR", mun="", A="13", B="22", final=51.785))
    for d in [d for d in D if d["ano"] in (2022, 2026) and d["cargo"] != "prefeito"]:
        D.append(dict(d, disputa=d["disputa"] + "_1t", turno=1, final=""))   # no 1º turno, o par é o do 2º (os dois primeiros)
    nomes = {}  # (ano, cargo, uf, mun, numero) -> nome de urna; (ano, mun) -> nome do município
    def pega(g, ano, cargo, uf, mun):
        nomes[(ano, cargo, uf, mun, g("NR_VOTAVEL"))] = g("NM_VOTAVEL").title()
    falta = lambda ano, cargo, uf, mun: [d for d in D if d["ano"] == ano and d["cargo"] == cargo and d["uf"] == uf and d["mun"] == mun
                                         and not all((ano, cargo, uf, mun, d[x]) in nomes for x in "AB")]
    for ano, pasta, pad in ((2026, "tse_secoes", "bweb_2t_{}_*.zip"), (2022, "tse_2022", "bweb_2t_{}_*.zip")):
        for uf in sorted({"AC"} | {d["uf"] for d in D if d["ano"] == ano and d["cargo"] == "governador"}):
            for g in ler_zip(glob.glob(os.path.join(DADOS, pasta, pad.format(uf)))[0]):
                c = g("CD_CARGO_PERGUNTA")
                if c == "1": pega(g, ano, "presidente", "BR", "")
                elif c == "3": pega(g, ano, "governador", uf, "")
                if not falta(ano, "presidente", "BR", "") and not falta(ano, "governador", uf, ""): break
    for uf in ["BR"] + sorted({d["uf"] for d in D if d["ano"] == 2018 and d["cargo"] == "governador"}):
        for g in ler_zip(os.path.join(DADOS, "tse_2018", f"votacao_secao_2018_{uf}.zip")):
            if g("NR_TURNO") != "2": continue
            if g("CD_CARGO") == "1": pega(g, 2018, "presidente", "BR", "")
            elif g("CD_CARGO") == "3": pega(g, 2018, "governador", uf, "")
            if not falta(2018, "presidente" if uf == "BR" else "governador", uf, ""): break
    for uf in sorted({d["uf"] for d in D if d["ano"] == 2024}):
        for g in ler_zip(os.path.join(DADOS, "tse_2024", f"votacao_secao_2024_{uf}.zip")):
            if g("NR_TURNO") != "2" or g("CD_CARGO") != "11" or g("CD_TIPO_ELEICAO") != "2": continue
            mun = g("CD_MUNICIPIO").zfill(5); pega(g, 2024, "prefeito", uf, mun); nomes[(2024, mun)] = g("NM_MUNICIPIO").title()
            if not any(falta(2024, "prefeito", uf, m) for m in {d["mun"] for d in D if d["ano"] == 2024 and d["uf"] == uf}): break
        print(uf, flush=True)
    for d in D:
        d["nome_A"] = nomes[(d["ano"], d["cargo"], d["uf"], d["mun"], d["A"])]; d["nome_B"] = nomes[(d["ano"], d["cargo"], d["uf"], d["mun"], d["B"])]
        d["municipio"] = nomes.get((d["ano"], d["mun"]), ""); d["data_eleicao"] = DATAS[d["ano"]][d["turno"] - 1]
    os.makedirs(SAI, exist_ok=True)
    cab = ["disputa", "turno", "cargo", "ano", "uf", "mun", "municipio", "data_eleicao", "A", "nome_A", "B", "nome_B", "final"]
    with open(os.path.join(SAI, "disputas.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, cab, delimiter=";", extrasaction="ignore"); w.writeheader(); w.writerows(D)
    print(len(D), "disputas")

def ler_disputas():
    return list(csv.DictReader(open(os.path.join(SAI, "disputas.csv"), encoding="utf-8"), delimiter=";"))

# ---------- páginas ----------
def api(lang, **p):
    import requests
    for i in range(5):
        try:
            r = requests.get(f"https://{lang}.wikipedia.org/w/api.php", params=dict(p, format="json"), headers=H, timeout=60)
            if r.status_code == 200 and ("error" not in r.json() or r.json()["error"].get("code") == "missingtitle"):
                time.sleep(0.5); return r.json()
            print("  resposta", r.status_code, r.text[:200])
        except Exception as e: print("  erro", e)
        time.sleep(2 + 3 * i)
    raise RuntimeError(p)

def arq_pagina(lang, titulo): return os.path.join(WIKI, lang + "_" + re.sub(r"[^\w]+", "_", sem_acento(titulo)).strip("_") + ".json")

def pagina(lang, titulo):
    """A página como o MediaWiki a monta (HTML), com o número da revisão; gravada uma vez e lida do disco depois."""
    fn = arq_pagina(lang, titulo)
    if os.path.exists(fn): return json.load(open(fn, encoding="utf-8"))
    r = api(lang, action="parse", page=titulo, prop="text|revid", redirects=1)
    if "parse" not in r: return None
    p = r["parse"]; d = dict(lang=lang, titulo=p["title"], revid=p["revid"], baixado=datetime.datetime.now().isoformat(timespec="seconds"),
                            url=f"https://{lang}.wikipedia.org/w/index.php?oldid={p['revid']}", html=p["text"]["*"])
    os.makedirs(WIKI, exist_ok=True); json.dump(d, open(fn, "w", encoding="utf-8"), ensure_ascii=False)
    return d

def busca(lang, q, n=5):
    return [x["title"] for x in api(lang, action="query", list="search", srsearch=q, srlimit=n)["query"]["search"]]

def candidatas(d):
    """Títulos a ler para a disputa: os fixos e os da busca da Wikipédia que têm o ano e o lugar no título."""
    ano = d["ano"]
    if d["cargo"] == "presidente":
        return [("en", f"Opinion polling for the {ano} Brazilian presidential election"), ("pt", f"Pesquisas de opinião para a eleição presidencial no Brasil em {ano}")]
    if d["cargo"] == "governador":
        nome, prep = UF_NOME[d["uf"]]; lugar = nome; en = UF_EN.get(d["uf"], nome)
        fixos = [("pt", f"Pesquisas eleitorais para a eleição estadual de {ano} {prep}"), ("pt", f"Eleição estadual {prep} em {ano}".replace(" em em ", " em ")),
                 ("en", f"{ano} {en} gubernatorial election"), ("en", f"{ano} {en} general election")]
        qs = [("pt", f"eleição estadual {nome} {ano} governador pesquisas"), ("en", f"{ano} {en} gubernatorial election")]
    else:
        lugar = d["municipio"]; en = lugar
        fixos = [("pt", f"Eleição municipal de {lugar} em {ano}"), ("pt", f"Eleição municipal em {lugar} em {ano}"), ("en", f"{ano} {lugar} mayoral election")]
        qs = [("pt", f"eleição municipal {lugar} {ano}"), ("en", f"{ano} {lugar} mayoral election")]
    achados = list(fixos)
    for lang, q in qs:
        for t in busca(lang, q):
            if str(ano) in t and (sem_acento(lugar) in sem_acento(t) or sem_acento(en) in sem_acento(t)): achados.append((lang, t))
    vistos = set(); out = []
    for x in achados:
        if x not in vistos: vistos.add(x); out.append(x)
    return out

def paginas():
    D = ler_disputas(); mapa = {}
    feitos = {}
    for d in D:
        chave = (d["cargo"], d["ano"], d["uf"], d["mun"])
        if chave not in feitos:
            lista = []
            for lang, t in candidatas(d):
                p = pagina(lang, t)
                if p and p["titulo"] not in [x["titulo"] for x in lista]: lista.append(dict(lang=lang, titulo=p["titulo"], revid=p["revid"], arquivo=os.path.basename(arq_pagina(lang, t))))
            feitos[chave] = lista
            print(d["disputa"], [x["titulo"] for x in lista], flush=True)
        mapa[d["disputa"]] = feitos[chave]
    json.dump(mapa, open(os.path.join(SAI, "paginas.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------- extração ----------
MESES = {**{m: i + 1 for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])},
         **{m: i + 1 for i, m in enumerate(["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"])}}
NAO_CAND = re.compile(r"pollster|polling|instituto|fonte|empresa|publisher|aggregator|data|period|per[ií]odo|datas|amostra|sample|"
                      r"outros|others|branco|blank|nulo|null|indec|undec|ns/nr|b/n|^bn$|^ns|^nr|nao sabe|nenhum|none|abst|lead|vantagem|dif|margin|margem|erro|link|ref|"
                      r"registro|contratante|commission|cliente|^$|^#", re.I)
STOP = {"de", "da", "do", "dos", "das", "e", "junior", "júnior", "filho", "silva", "santos", "souza", "sousa", "oliveira", "ferreira",
        "lima", "costa", "pereira", "alves", "rodrigues", "gomes", "martins", "barbosa", "ribeiro", "carvalho", "araujo", "moraes"}


def grade(t):
    """A tabela HTML como grade, com rowspan e colspan abertos; cada célula guarda (tag, texto, elemento)."""
    G = {}; rows = t.find_all("tr")
    for i, tr in enumerate(rows):
        j = 0
        for c in tr.find_all(["th", "td"], recursive=False):
            while (i, j) in G: j += 1
            rs = int(re.sub(r"\D", "", c.get("rowspan", "1")) or 1); cs = int(re.sub(r"\D", "", c.get("colspan", "1")) or 1)
            for a in range(rs):
                for b in range(cs): G[(i + a, j + b)] = (c.name, c, a == 0 and b == 0)
            j += cs
    n = len(rows); m = max([k[1] for k in G] + [-1]) + 1
    return [[G.get((i, j)) for j in range(m)] for i in range(n)]

def texto(c):
    if c is None: return ""
    el = c[1]
    for s in el.find_all(["sup", "style"]): s.extract() if s.name == "style" else None
    return re.sub(r"\s+", " ", "".join(x if isinstance(x, str) else "" for x in el.strings)).strip()

def texto_sem_ref(el):
    import copy
    e = copy.copy(el)
    for s in e.find_all(["sup", "style"]): s.decompose()
    return re.sub(r"\s+", " ", e.get_text(" ", strip=True)).strip()

NUM = re.compile(r"^\s*(\d{1,2}(?:[.,]\d+)?)\s*%?\s*$")
def pct(s):
    m = NUM.match(s.replace(" ", ""))
    return float(m.group(1).replace(",", ".")) if m else None

def datas(s, ano):
    """(início, fim) do campo. Aceita '25–26 Oct 2022', '30 Sep – 1 Oct 2022', '24 a 26 de outubro de 2022', '24/10 a 26/10/2022', 'Oct 25–26, 2022'."""
    s = sem_acento(s).replace("–", "-").replace("—", "-").replace("º", "").replace("°", "").replace("o.", " ").replace(".", " ")
    s = re.sub(r"(\d)\s*/\s*([a-z])", r"\1 \2", s); s = re.sub(r"([a-z])\s*/\s*(\d)", r"\1 \2", s)
    toks = []
    for m in re.finditer(r"(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?|(\d{1,2})(?:\s*(?:de\s+)?([a-z]{3,})(?:\s+(?:de\s+)?(\d{4}))?)?|([a-z]{3,})\s+(\d{1,2})(?:\s*-\s*(\d{1,2}))?(?:,\s*(\d{4}))?|(\d{4})", s):
        g = m.groups()
        if g[0]: toks.append([int(g[0]), int(g[1]), int(g[2]) + (2000 if len(g[2]) == 2 else 0) if g[2] else None])
        elif g[3]:
            mes = MESES.get(g[4][:3]) if g[4] else None
            if g[4] and mes is None: continue
            toks.append([int(g[3]), mes, int(g[5]) if g[5] else None])
        elif g[6] and MESES.get(g[6][:3]):
            mes = MESES[g[6][:3]]; toks.append([int(g[7]), mes, int(g[9]) if g[9] else None])
            if g[8]: toks.append([int(g[8]), mes, int(g[9]) if g[9] else None])
        elif g[10]:
            if toks: toks[-1][2] = toks[-1][2] or int(g[10])
    toks = [t for t in toks if 1 <= t[0] <= 31]
    if not toks or toks[-1][1] is None: return None, None
    for k in range(len(toks) - 2, -1, -1):
        if toks[k][1] is None: toks[k][1] = toks[k + 1][1]
        if toks[k][2] is None: toks[k][2] = toks[k + 1][2]
    for t in toks: t[2] = t[2] or ano
    try:
        f = datetime.date(toks[-1][2], toks[-1][1], toks[-1][0]); i = datetime.date(toks[0][2], toks[0][1], toks[0][0])
    except ValueError: return None, None
    if i > f: i = i.replace(year=i.year - 1)
    return i, f

def tokens(nome): return {t for t in re.findall(r"[a-z]+", sem_acento(nome)) if len(t) >= 3 and t not in STOP}

def refs(soup):
    """id da nota → primeiro link externo da referência."""
    R = {}
    for li in soup.select("li[id^=cite_note]"):
        a = li.select_one("a.external, a[rel~=nofollow]")
        if a and a.get("href"): R[li["id"]] = a["href"]
    return R

def tabelas(p, d):
    """Linhas de pesquisa das tabelas da página que têm colunas para A e B (pelo nome de urna)."""
    import bs4
    soup = bs4.BeautifulSoup(p["html"], "lxml"); R = refs(soup); ano = int(d["ano"]); out = []
    tA, tB = tokens(d["nome_A"]) - tokens(d["nome_B"]), tokens(d["nome_B"]) - tokens(d["nome_A"])
    for it, t in enumerate(soup.find_all("table", class_=re.compile("wikitable"))):
        G = grade(t)
        if len(G) < 2 or not G[0]: continue
        # cabeçalho: as linhas antes da primeira com um número de % numa célula td
        nh = next((i for i, row in enumerate(G) if any(c and c[0] == "td" and pct(texto_sem_ref(c[1])) is not None for c in row)), None)
        if not nh: continue
        cab = [" ".join(dict.fromkeys(texto_sem_ref(G[i][j][1]) for i in range(nh) if G[i][j])) for j in range(len(G[0]))]
        low = [sem_acento(c) for c in cab]
        col = lambda pat: next((j for j, c in enumerate(low) if re.search(pat, c)), None)
        DATA = r"period|periodo|data|date|campo|realiza|conduc|conduz|divulga|publica|releas"
        jinst = next((j for pat in (r"pollster|polling firm|instituto|empresa", r"fonte|publisher|pesquisa|contratante")
                      for j, c in enumerate(low) if re.search(pat, c) and not re.search(DATA, c)), None)
        jdata = col(r"period|periodo|data|date|campo|realiza|conduc|conduz"); tipo_data = "campo"
        if jdata is None: jdata = col(r"divulga|publica|releas"); tipo_data = "divulgação"
        jam = col(r"amostra|sample|entrevist")
        if jinst is None or jdata is None: continue
        pessoas = [j for j, c in enumerate(cab) if not NAO_CAND.search(sem_acento(c).strip()) and j not in (jinst, jdata, jam)]
        def acha(tt):
            sc = [(len(tt & tokens(cab[j])), j) for j in pessoas]; sc = [x for x in sc if x[0] > 0]
            if not sc: return None
            sc.sort(reverse=True)
            return sc[0][1] if len(sc) == 1 or sc[0][0] > sc[1][0] else None
        jA, jB = acha(tA), acha(tB)
        if jA is None or jB is None or jA == jB: continue
        titulo = texto_sem_ref(t.find_previous(["h2", "h3", "h4"])) if t.find_previous(["h2", "h3", "h4"]) else ""
        cap = (t.caption.get_text(" ", strip=True) if t.caption else "")
        if re.search(r"rejei|reject|espont|spontan|avalia|approv|aprova|potencial|governo|government|agrega|aggregat|graphic", sem_acento(titulo + " " + cap)): continue
        anos = re.findall(r"\b(20\d\d)\b", titulo + " " + cap); ano_t = int(anos[-1]) if anos else ano
        base = "válidos" if re.search(r"valid", sem_acento(titulo + " " + cap + " " + " ".join(cab))) else "totais ou não informado"
        for i in range(nh, len(G)):
            row = G[i]
            if not row[jA] or not row[jB] or not row[jinst] or not row[jdata]: continue
            a, b = pct(texto_sem_ref(row[jA][1])), pct(texto_sem_ref(row[jB][1]))
            if a is None or b is None: continue
            ini, fim = datas(texto_sem_ref(row[jdata][1]), ano_t)
            if fim is None: continue
            am = re.sub(r"[^\d]", "", texto_sem_ref(row[jam][1]).split("(")[0]) if jam is not None and row[jam] else ""
            ref = ""
            for c in row:
                if not c: continue
                for s in c[1].select("sup.reference a[href^='#cite_note']"):
                    ref = ref or R.get(s["href"][1:], "")
            outros = {cab[j]: pct(texto_sem_ref(row[j][1])) for j in pessoas if j not in (jA, jB) and row[j]}
            outros = {k: v for k, v in outros.items() if v}
            out.append(dict(instituto=texto_sem_ref(row[jinst][1]), campo_inicio=ini.isoformat() if ini else "", campo_fim=fim.isoformat(),
                            amostra=am if am and 100 <= int(am) <= 200000 else "", pct_A=a, pct_B=b, n_outros=sum(v is not None for v in outros.values()),
                            base=base, data_tipo=tipo_data, tabela=f"{it}: {titulo[:60]}", fonte_pagina=p["url"], pagina=p["titulo"], fonte_ref=ref))
    return out

def norm_inst(s):
    s = sem_acento(s); s = re.sub(r"\(.*?\)|\[.*?\]", " ", s)
    return re.findall(r"[a-z0-9]+", s)[0] if re.findall(r"[a-z0-9]+", s) else s

def extrair():
    D = ler_disputas(); mapa = json.load(open(os.path.join(SAI, "paginas.json"), encoding="utf-8")); linhas = []; cont = {}
    for d in D:
        e1 = datetime.date.fromisoformat(DATAS[int(d["ano"])][0]); el = datetime.date.fromisoformat(d["data_eleicao"])
        vistos = set(); n = 0
        for pg in mapa[d["disputa"]]:
            p = json.load(open(os.path.join(WIKI, pg["arquivo"]), encoding="utf-8"))
            for r in tabelas(p, d):
                fim = datetime.date.fromisoformat(r["campo_fim"])
                if fim >= el: continue                                   # só as publicadas antes da eleição (campo antes do dia)
                if d["turno"] == "2" and (r["n_outros"] > 0 or fim <= e1): continue   # 2º turno: só os dois, campo depois do 1º turno
                if d["turno"] == "1" and r["n_outros"] == 0: continue                 # 1º turno: tabela com os outros candidatos
                k = (r["campo_fim"], r["pct_A"], r["pct_B"])   # a mesma pesquisa em duas páginas (o nome do instituto varia: Atlas, AtlasIntel)
                if k in vistos: continue
                vistos.add(k); n += 1
                linhas.append(dict(disputa=d["disputa"], turno=d["turno"], data_eleicao=d["data_eleicao"], candidato_A=d["nome_A"], candidato_B=d["nome_B"], **r))
        cont[d["disputa"]] = n
    cab = ["disputa", "turno", "data_eleicao", "instituto", "campo_inicio", "campo_fim", "amostra", "candidato_A", "pct_A", "candidato_B", "pct_B",
           "n_outros", "base", "data_tipo", "pagina", "tabela", "fonte_pagina", "fonte_ref"]
    with open(os.path.join(SAI, "pesquisas.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, cab, delimiter=";", extrasaction="ignore"); w.writeheader(); w.writerows(linhas)
    json.dump(cont, open(os.path.join(SAI, "contagem.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(linhas), "linhas;", sum(v > 0 for v in cont.values()), "disputas com alguma pesquisa")
    for k, v in cont.items(): print(k, v)

if __name__ == "__main__":
    {"disputas": disputas, "paginas": paginas, "extrair": extrair}[sys.argv[1]]()
