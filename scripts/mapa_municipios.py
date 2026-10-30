"""Malha dos municípios para o Mapa do estudo (T36, P38).

Lê a malha dos municípios do IBGE (API de malhas v3, qualidade mínima, baixada em 28/10/2026 com o
ok do autor) e grava um arquivo por estado, site-analise/mapas/mun-<UF>.js, com o desenho de cada
município em SVG, na mesma projeção do mapa dos estados (scripts/mapa_ufs.py): longitude encolhida
pelo cosseno de 15° e a mesma origem, tirada da malha dos estados, para os dois desenhos coincidirem.
O Mapa (site-analise/passear.js) carrega o arquivo do estado só quando ele é aberto.

Cada município é ligado ao nome usado na página (site-analise/dados.js) pelo código do IBGE da lista
de municípios do TSE (dados/tse_config/mun-e006258-cm.json: "cdi" é o código do IBGE). Não usa voto
nenhum. Sai com erro se algum município da página ficar sem desenho.

    python -I scripts/mapa_municipios.py
"""
import json
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parent.parent
MALHA_UF = RAIZ / "dados" / "ibge_malha" / "br_uf_minima.json"
MALHA_MUN = RAIZ / "dados" / "ibge_malha" / "br_mun_minima.json"
TSE = RAIZ / "dados" / "tse_config" / "mun-e006258-cm.json"
DADOS = RAIZ / "site-analise" / "dados.js"
SAIDA = RAIZ / "site-analise" / "mapas"
ESCALA = 20          # unidades por grau, como em mapa_ufs.py
COS = 0.9659         # cos(15°)


def arcos_de(topo):
    sx, sy = topo["transform"]["scale"]
    tx, ty = topo["transform"]["translate"]
    saida = []
    for arco in topo["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in arco:
            x += dx
            y += dy
            pts.append((x * sx + tx, y * sy + ty))
        saida.append(pts)
    return saida


# a origem da projeção vem da malha dos estados, para o município cair no lugar certo do estado
arcos_uf = arcos_de(json.load(open(MALHA_UF, encoding="utf-8")))
todos = [p for a in arcos_uf for p in a]
lon0 = min(p[0] for p in todos)
lat1 = max(p[1] for p in todos)


def proj(p):
    # duas casas: 0,005° (uns 500 m), o bastante para os municípios pequenos não virarem um ponto
    return (round((p[0] - lon0) * COS * ESCALA, 2), round((lat1 - p[1]) * ESCALA, 2))


topo = json.load(open(MALHA_MUN, encoding="utf-8"))
arcos = arcos_de(topo)


def anel(indices):
    pts = []
    for i in indices:
        a = arcos[i] if i >= 0 else list(reversed(arcos[~i]))
        pts.extend(a if not pts else a[1:])
    return pts


def caminho(g):
    poligonos = [g["arcs"]] if g["type"] == "Polygon" else g["arcs"]
    partes = []
    for poligono in poligonos:
        for indices in poligono:
            pts = []
            for q in (proj(p) for p in anel(indices)):
                if not pts or q != pts[-1]:
                    pts.append(q)
            if len(pts) >= 3:
                partes.append("M" + "L".join(f"{x:g} {y:g}" for x, y in pts) + "Z")
    return "".join(partes)


def norm(s):
    s = unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode()
    return " ".join(s.upper().replace("'", " ").replace("-", " ").split())


# o código do IBGE de cada município, pelo nome do TSE
tse = json.load(open(TSE, encoding="utf-8"))
ibge = {}  # código do IBGE -> (UF, nome normalizado)
for e in tse["abr"]:
    for m in e["mu"]:
        if m.get("cdi"):
            ibge[m["cdi"]] = (e["cd"].upper(), norm(m["nm"]))

# os nomes da página
txt = DADOS.read_text(encoding="utf-8")
estudo = json.loads(txt[txt.index("{"):txt.rindex("}") + 1])
pagina = {}  # (UF, nome normalizado) -> nome na página
for linha in estudo["municipios"]["linhas"].split("\n"):
    nome, uf = linha.split("|")[:2]
    if uf != "ZZ":
        pagina[(uf, norm(nome))] = nome

por_uf, sem_nome = {}, []
refs_uf = {}  # UF -> {arco: vezes que os municípios do estado o usam}; arco usado uma vez só é divisa do estado
for g in list(topo["objects"].values())[0]["geometries"]:
    cod = g["properties"]["codarea"]
    chave = ibge.get(cod)
    if not chave or chave not in pagina:
        sem_nome.append(cod)
        continue
    por_uf.setdefault(chave[0], {})[pagina[chave]] = caminho(g)
    r = refs_uf.setdefault(chave[0], {})
    for poligono in ([g["arcs"]] if g["type"] == "Polygon" else g["arcs"]):
        for indices in poligono:
            for i in indices:
                r[i if i >= 0 else ~i] = r.get(i if i >= 0 else ~i, 0) + 1


def divisa(uf):
    """A divisa do estado feita com os próprios arcos dos municípios (mesma malha, encaixa sem folga)."""
    partes = []
    for a, n in refs_uf[uf].items():
        if n == 1:
            pts = []
            for q in (proj(p) for p in arcos[a]):
                if not pts or q != pts[-1]:
                    pts.append(q)
            if len(pts) >= 2:
                partes.append("M" + "L".join(f"{x:g} {y:g}" for x, y in pts))
    return "".join(partes)

# municípios criados depois da malha do IBGE: ficam só na lista do Mapa, e o mapa do estado diz isso
SEM_MALHA = {("MT", "BOA ESPERANCA DO NORTE")}  # instalado depois da malha do IBGE (2022)
faltam = [k for k in pagina if k[1] and pagina[k] not in por_uf.get(k[0], {}) and k not in SEM_MALHA]
print(f"municípios na página: {len(pagina)}; com desenho: {sum(len(v) for v in por_uf.values())}")
if sem_nome:
    print(f"áreas da malha sem município na página: {len(sem_nome)} ({', '.join(sem_nome[:10])})")
if faltam:
    print("municípios da página sem desenho:", ", ".join(f"{p[k]} ({k[0]})" for k in faltam for p in [pagina]))
    sys.exit(1)

SAIDA.mkdir(exist_ok=True)
gerado = datetime.now().strftime("%d/%m/%Y %H:%M")
total = 0
for uf, caminhos in sorted(por_uf.items()):
    arq = SAIDA / f"mun-{uf}.js"
    corpo = json.dumps({"gerado": gerado, "fonte": "IBGE, malha dos municípios (qualidade mínima): dados/ibge_malha/br_mun_minima.json",
                        "sem_desenho": sorted(pagina[k] for k in SEM_MALHA if k[0] == uf), "divisa": divisa(uf), "caminhos": caminhos}, ensure_ascii=False, separators=(",", ":"))
    arq.write_text(f"/* Gerado por scripts/mapa_municipios.py (T36). Não editar à mão. */\n"
                   f"(window.MAPA_MUN = window.MAPA_MUN || {{}})[{json.dumps(uf)}] = {corpo};\n", encoding="utf-8", newline="\n")
    total += arq.stat().st_size
print(f"Gravados: {len(por_uf)} arquivos em {SAIDA.relative_to(RAIZ)}, {total / 1e6:.1f} MB no total; "
      f"o maior: {max((SAIDA / f'mun-{u}.js').stat().st_size for u in por_uf) / 1e3:.0f} KB")
