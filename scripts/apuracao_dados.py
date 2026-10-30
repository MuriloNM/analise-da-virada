"""Dados da página "Apuração ao vivo" do estudo (T28).

Lê só arquivos já gravados durante a apuração e grava site-analise/apuracao-dados.js:
- dados/historico_2t.json: as 115 leituras da página ao vivo do 2º turno, como foram
  gravadas (% de urnas apuradas, fatia do Lula na contagem, no 1º turno nas mesmas urnas,
  projeção final, hora do TSE e 1º turno ponderado só por UF);
- dados/base_1t_compacta.json: a curva da contagem do 1º turno pelo % apurado (`t1c`),
  reconstruída dos boletins de urna por scripts/curva1t.py.

Não faz conta nova: os valores vão como estão nos arquivos. Confere a última leitura e o
fim da curva do 1º turno contra o resultado final de dados/analise_estados.csv (T03) e o
histórico contra o CSV gravado na mesma noite. A página arredonda uma vez, na hora de
mostrar (diário, D25). O pagina_dados.py (dados.js) não muda.

    python -I scripts/apuracao_dados.py
"""
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parent.parent
DADOS = RAIZ / "dados"
SAIDA = RAIZ / "site-analise" / "apuracao-dados.js"

problemas = []


def confere(ok, texto):
    print(("ok    " if ok else "FALHA ") + texto)
    if not ok:
        problemas.append(texto)


def dec(s):
    return float(s.replace(",", "."))


# --- Resultado final do Brasil (T03), com o valor completo ------------------------
with open(DADOS / "analise_estados.csv", encoding="utf-8") as f:
    br = next(r for r in csv.DictReader(f) if r["nivel"] == "brasil")
L1, F1, L2, F2 = (int(br[k]) for k in ("lula_1t", "flavio_1t", "lula_2t", "flavio_2t"))
s1, s2 = 100 * L1 / (L1 + F1), 100 * L2 / (L2 + F2)
print(f"Resultado final: 1º turno {s1:.4f}%, 2º turno {s2:.4f}% (fatia do Lula entre os dois)")

# --- Leituras da apuração ao vivo do 2º turno ---------------------------------------
print("\n## Leituras (dados/historico_2t.json)")
hist = json.load(open(DADOS / "historico_2t.json", encoding="utf-8"))
confere(len(hist) == 115 and all(len(h) == 6 for h in hist), f"{len(hist)} leituras com 6 campos")
confere(all(hist[i][0] < hist[i + 1][0] for i in range(len(hist) - 1)), "% apurado sempre crescente")
confere(all(hist[i][4] < hist[i + 1][4] for i in range(len(hist) - 1)), "hora sempre crescente")
confere(hist[-1][0] == 100.0 and abs(hist[-1][1] - round(s2, 3)) < 1e-9 and abs(hist[-1][3] - round(s2, 3)) < 1e-9,
        f"a última leitura é o resultado final: 100% apurado, {hist[-1][1]}% na contagem e na projeção")
confere(abs(hist[-1][2] - round(s1, 3)) < 1e-9, f"com 100% apurado, o 1º turno nas mesmas urnas é o 1º turno inteiro ({hist[-1][2]}%)")
with open(DADOS / "historico_2t.csv", encoding="utf-8-sig") as f:
    linhas = list(csv.DictReader(f, delimiter=";"))
iguais = len(linhas) == len(hist) and all(
    abs(dec(r["urnas_apuradas_pct"]) - h[0]) < 1e-9 and r["hora_tse"] == h[4]
    and abs(dec(r["lula_2t_pct"]) - h[1]) < 1e-9 and abs(dec(r["lula_1t_mesmas_urnas_pct"]) - h[2]) < 1e-9
    and abs(dec(r["projecao_final_pct"]) - h[3]) < 1e-9 and abs(dec(r["lula_1t_por_uf_pct"]) - h[5]) < 1e-9
    for r, h in zip(linhas, hist))
confere(iguais, "JSON igual ao CSV gravado na mesma noite, campo a campo")
buraco = max(((hist[i][0], hist[i + 1][0]) for i in range(len(hist) - 1)), key=lambda b: b[1] - b[0])
confere(buraco == (60.85, 68.8), f"maior intervalo sem leitura: de {buraco[0]}% a {buraco[1]}% (nota N17)")

# --- Leituras refeitas no buraco (T41; T42, etapa 2) ------------------------------------
print("\n## Leituras refeitas no buraco (dados/reconstrucao_2t/leituras_br.csv, T41)")
with open(DADOS / "reconstrucao_2t" / "leituras_br.csv", encoding="utf-8") as f:
    refeitas = [[float(r["pct_secoes"]), float(r["lula_pct"]), float(r["lula_1t_mesmas_urnas_pct"]), float(r["projecao_pct"]), r["hora_tse"]]
                for r in csv.DictReader(f, delimiter=";") if r["tipo"] == "buraco"]
confere(len(refeitas) == 13 and all(buraco[0] < r[0] < buraco[1] for r in refeitas)
        and all(refeitas[i][0] < refeitas[i + 1][0] for i in range(len(refeitas) - 1)),
        f"{len(refeitas)} leituras refeitas, todas dentro do buraco, de {refeitas[0][0]}% a {refeitas[-1][0]}% ({refeitas[0][4]} a {refeitas[-1][4]})")

# --- Estados leitura a leitura, refeitos (T41; T42, etapa 2b) ----------------------------
print("\n## Estados leitura a leitura (dados/reconstrucao_2t/leituras_uf.csv, T41)")
with open(DADOS / "reconstrucao_2t" / "leituras_uf.csv", encoding="utf-8") as f:
    luf = [r for r in csv.DictReader(f, delimiter=";") if r["tipo"] == "gravada"]
ufs_l = sorted({r["uf"] for r in luf})
por_hora = {}
for r in luf:
    por_hora.setdefault(r["hora_tse"], {})[r["uf"]] = [float(r["pct_secoes"]), float(r["lula_pct"]), float(r["lula_1t_mesmas_urnas_pct"])]
horas = [h[4] for h in hist[:-1]]
confere(len(ufs_l) == 28 and set(por_hora) == set(horas) and all(len(v) == 28 for v in por_hora.values()),
        f"{len(por_hora)} leituras × {len(ufs_l)} unidades, com a mesma hora do TSE das leituras gravadas")
uf_leituras = {"ufs": [u.upper() for u in ufs_l], "campos": ["apurado", "contagem", "mesmas_urnas_1t"],
               "leituras": [[por_hora[h][u] for u in ufs_l] for h in horas]}

# --- Curva da contagem do 1º turno -----------------------------------------------------
print("\n## Curva do 1º turno (dados/base_1t_compacta.json, t1c)")
t1c = json.load(open(DADOS / "base_1t_compacta.json", encoding="utf-8"))["t1c"]
confere(all(len(q) == 3 for q in t1c) and all(t1c[i][0] < t1c[i + 1][0] for i in range(len(t1c) - 1)),
        f"{len(t1c)} pontos, % apurado sempre crescente")
confere(t1c[-1][0] == 100.0 and abs(t1c[-1][1] - round(s1, 3)) < 1e-9, f"o fim da curva é o 1º turno final ({t1c[-1][1]}%)")

# --- Saída ------------------------------------------------------------------------------
saida = {
    "gerado": datetime.now().strftime("%d/%m/%Y %H:%M"),
    "fontes": "dados/historico_2t.json; dados/base_1t_compacta.json (t1c); dados/analise_estados.csv (T03), só para conferir",
    "campos": ["apurado", "contagem", "mesmas_urnas_1t", "projecao", "hora", "por_uf_1t"],
    "leituras": hist,
    "curva1t": t1c,
    # T42: as leituras refeitas depois (T41), só no trecho sem leituras gravadas; ficam fora das contas da página
    "refeitas_campos": ["apurado", "contagem", "mesmas_urnas_1t", "projecao", "hora"],
    "refeitas": refeitas,
    # T42: os estados em cada leitura gravada (menos a final), refeitos pela hora de recebimento dos boletins (T41)
    "uf_leituras": uf_leituras,
}
SAIDA.write_text("// Gerado por scripts/apuracao_dados.py. Não editar à mão.\n"
                 "window.APURACAO_DADOS = " + json.dumps(saida, ensure_ascii=False, separators=(",", ":")) + ";\n",
                 encoding="utf-8")
print(f"\n{SAIDA.relative_to(RAIZ)}: {SAIDA.stat().st_size / 1024:.0f} KB")
if problemas:
    sys.exit("\nFALHOU:\n- " + "\n- ".join(problemas))
print("Resultado: tudo confere.")
