# T41, exploração da regra de chamada: o mesmo teste limpo de projecoes_teste2018.py, no 2º turno de prefeito de 2024 (51 cidades).
# Ordem de chegada pelo detalhe_votacao_secao_2024.zip (DT_RECEBIMENTO_BU_HOR_TSE); votos por seção: votacao_secao_2024_{UF}.zip.
# Só a eleição ordinária (CD_TIPO_ELEICAO 2; as suplementares ficam de fora) e só os arquivos por UF (o _BRASIL repete as UFs).
# Numa cidade, UF e município são um só: os métodos rodam sem mudança. Regras: ticket T41, "Regra de chamada (exploração)".
# Uso: python -I scripts/projecoes_teste2024.py   (grava dados/projecoes_outras/teste2024_*)
import os, sys, csv, json, collections
import numpy as np
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import reconstrucao_2t as rc
from projecoes_teste2022 import ler_zip, chave, montar, avaliar, SAI
T24 = os.path.join(AQUI, "..", "dados", "tse_2024")

def detalhe():
    """Por seção do prefeito: (aptos, comparecimento) no 1º turno; hora de recebimento e aptos no 2º; e as cidades com 2º turno."""
    d1, d2 = {}, {}
    for g in ler_zip(os.path.join(T24, "detalhe_votacao_secao_2024.zip")):
        if g("CD_CARGO") != "11" or g("CD_TIPO_ELEICAO") != "2" or g("SG_UF") == "BR": continue
        k = chave(g)
        if g("NR_TURNO") == "1": d1[k] = (int(g("QT_APTOS")), int(g("QT_COMPARECIMENTO")))
        else: d2[k] = (rc.seg(g("DT_RECEBIMENTO_BU_HOR_TSE")), int(g("QT_APTOS")))
    return d1, d2

def votos(zp, cidades):
    v = {1: collections.defaultdict(collections.Counter), 2: collections.defaultdict(collections.Counter)}
    for g in ler_zip(zp):
        if g("CD_CARGO") != "11" or g("CD_TIPO_ELEICAO") != "2": continue
        k = chave(g)
        if k[1] in cidades: v[int(g("NR_TURNO"))][k][g("NR_VOTAVEL")] += int(g("QT_VOTOS"))
    return v

def main():
    d1, d2 = detalhe(); print("detalhe", len(d1), len(d2), flush=True)
    cid = collections.defaultdict(set)
    for k in d2: cid[k[0]].add(k[1])
    linhas, resumo = [], {}
    for uf in sorted(cid):
        v = votos(os.path.join(T24, f"votacao_secao_2024_{uf.upper()}.zip"), cid[uf])
        for mu in sorted(cid[uf]):
            nome = f"prefeito_2024_{uf.upper()}_{mu}"
            bu = {k: dict(t=d2[k][0], aptos=d2[k][1], v={c: q for c, q in vv.items() if c not in ("95", "96")})
                  for k, vv in v[2].items() if k[1] == mu and k in d2}
            v1 = {k: vv for k, vv in v[1].items() if k[1] == mu}
            L, R = avaliar(*montar(nome, bu, v1, d1))
            linhas += L; resumo[nome] = R
            print(nome, R["A"], R["B"], R["final"], {m: (x["abs_medio"], x["passa_a_acertar"]) for m, x in R["metodos"].items()},
                  R["concordam"], "sem 1t:", R["sem_1t"], "sem detalhe:", R["sem_detalhe"], flush=True)
    cab = ["disputa", "pst", "hora", "n", "contagem", "a", "b", "c", "c_lo", "c_hi", "d", "d_lo", "d_hi", "m", "final"]
    with open(os.path.join(SAI, "teste2024_instantes.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";"); w.writerow(cab)
        for d in linhas: w.writerow([round(d[k], 4) if isinstance(d[k], float) else d[k] for k in cab])
    ms = ("a", "b", "c", "d", "m")
    resumo["_total"] = dict(abs_medio={m: round(float(np.mean([r["metodos"][m]["abs_medio"] for r in resumo.values()])), 3) for m in ms},
                            melhor={m: sum(min(ms, key=lambda x: r["metodos"][x]["abs_medio"]) == m for r in resumo.values()) for m in ms},
                            concordando_e_errando=sum(r["concordam"]["concordando_e_errando"] for r in resumo.values()))
    json.dump(resumo, open(os.path.join(SAI, "teste2024_resumo.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=lambda o: o.item())
    print(json.dumps(resumo["_total"], ensure_ascii=False, indent=1, default=lambda o: o.item()))

if __name__ == "__main__":
    main()
