"""Malha dos estados para o mapa da página Explorar (T24).

Lê a malha dos estados do IBGE (qualidade mínima, localizada no T01 e baixada no
T07) e grava site-analise/mapa.js com o desenho de cada UF em SVG, na mesma
projeção do ateliê (scripts/atelie_dados.py): longitude encolhida pelo cosseno
de 15°, a latitude média do Brasil. Não usa voto nenhum: os números do mapa vêm
de site-analise/dados.js, que não muda.

    python -I scripts/mapa_ufs.py
"""
import json
import sys
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "dados" / "ibge_malha" / "br_uf_minima.json"
SAIDA = RAIZ / "site-analise" / "mapa.js"

UF_IBGE = {
    "11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO",
    "21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL",
    "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP", "41": "PR",
    "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF",
}
ESCALA = 20          # unidades por grau
COS = 0.9659         # cos(15°), latitude média do Brasil

topo = json.load(open(ENTRADA, encoding="utf-8"))
sx, sy = topo["transform"]["scale"]
tx, ty = topo["transform"]["translate"]
arcos = []
for arco in topo["arcs"]:
    x = y = 0
    pts = []
    for dx, dy in arco:
        x += dx
        y += dy
        pts.append((x * sx + tx, y * sy + ty))
    arcos.append(pts)

todos = [p for a in arcos for p in a]
lon0 = min(p[0] for p in todos)
lat1 = max(p[1] for p in todos)


def proj(p):
    return (round((p[0] - lon0) * COS * ESCALA, 1), round((lat1 - p[1]) * ESCALA, 1))


def anel(indices):
    pts = []
    for i in indices:
        a = arcos[i] if i >= 0 else list(reversed(arcos[~i]))
        pts.extend(a if not pts else a[1:])
    return pts


caminhos = {}
for g in topo["objects"]["BRUF"]["geometries"]:
    uf = UF_IBGE[g["properties"]["codarea"]]
    poligonos = [g["arcs"]] if g["type"] == "Polygon" else g["arcs"]
    partes = []
    for poligono in poligonos:
        for indices in poligono:
            pts = [proj(p) for p in anel(indices)]
            partes.append("M" + "L".join(f"{x:g} {y:g}" for x, y in pts) + "Z")
    caminhos[uf] = "".join(partes)
largura = max(proj(p)[0] for p in todos)
altura = max(proj(p)[1] for p in todos)

if sorted(caminhos) != sorted(UF_IBGE.values()):
    sys.exit("ERRO: a malha não tem as 27 UFs")
print(f"OK: 27 UFs, {largura:g} × {altura:g}")

saida = {"gerado": datetime.now().strftime("%d/%m/%Y %H:%M"),
         "fonte": "IBGE, malha dos estados (qualidade mínima): dados/ibge_malha/br_uf_minima.json",
         "largura": round(largura, 1), "altura": round(altura, 1), "caminhos": caminhos}
SAIDA.write_text("/* Gerado por scripts/mapa_ufs.py (T24). Não editar à mão. */\nwindow.MAPA_UFS = "
                 + json.dumps(saida, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
print(f"Gravado: {SAIDA.relative_to(RAIZ)} ({SAIDA.stat().st_size:,} bytes)".replace(",", "."))
