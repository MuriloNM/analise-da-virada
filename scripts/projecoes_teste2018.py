# T41, Parte 3: o mesmo teste limpo de projecoes_teste2022.py, no 2º turno de 2018 (presidente e governador nas 14 UFs com 2º turno).
# O boletim de 2018 não tem a hora de recebimento; ela vem do detalhe_votacao_secao_2018.zip (DT_RECEBIMENTO_BU_HOR_TSE,
# idêntica ao DT_BU_RECEBIDO do boletim em 2022). Votos por seção: votacao_secao_2018_{BR,UF}.zip.
# Regras: ticket T41, "Teste limpo em 2022" (item 2018). Uso: python -I scripts/projecoes_teste2018.py
import os, sys, csv, json, collections
import numpy as np
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import reconstrucao_2t as rc
from projecoes_teste2022 import ler_zip, chave, montar, avaliar, SAI
T18 = os.path.join(AQUI, "..", "dados", "tse_2018")
UFS_GOV = ["AM", "AP", "DF", "MG", "MS", "PA", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP"]

def detalhe():
    """Por seção: (aptos, comparecimento) no 1º turno; hora de recebimento e aptos no 2º (cargo presidente; o boletim é um só por seção)."""
    d1, d2 = {}, {}
    for g in ler_zip(os.path.join(T18, "detalhe_votacao_secao_2018.zip"), so="_BR."):
        if g("CD_CARGO") != "1": continue
        k = chave(g)
        if g("NR_TURNO") == "1": d1[k] = (int(g("QT_APTOS")), int(g("QT_COMPARECIMENTO")))
        else: d2[k] = (rc.seg(g("DT_RECEBIMENTO_BU_HOR_TSE")), int(g("QT_APTOS")))
    return d1, d2

def votos(zp, cargo):
    v = {1: collections.defaultdict(collections.Counter), 2: collections.defaultdict(collections.Counter)}
    for g in ler_zip(zp):
        if g("CD_CARGO") != cargo: continue
        v[int(g("NR_TURNO"))][chave(g)][g("NR_VOTAVEL")] += int(g("QT_VOTOS"))
    return v

def main():
    d1, d2 = detalhe(); print("detalhe", len(d1), len(d2), flush=True)
    linhas, resumo = [], {}
    tarefas = [("presidente_2018", "1", "BR", None)] + [(f"governador_2018_{uf}", "3", uf, uf.lower()) for uf in UFS_GOV]
    for nome, cargo, arq, uf in tarefas:
        v = votos(os.path.join(T18, f"votacao_secao_2018_{arq}.zip"), cargo)
        bu = {k: dict(t=d2[k][0], aptos=d2[k][1], v={c: q for c, q in vv.items() if c not in ("95", "96")})
              for k, vv in v[2].items() if k in d2 and (uf is None or k[0] == uf)}
        L, R = avaliar(*montar(nome, bu, v[1], d1))
        linhas += L; resumo[nome] = R
        print(nome, R["A"], R["B"], R["final"], {m: (x["abs_medio"], x["passa_a_acertar"]) for m, x in R["metodos"].items()},
              R["concordam"], "sem 1t:", R["sem_1t"], "sem detalhe:", R["sem_detalhe"], "sem hora 2t:", len(v[2]) - len(bu) if uf is None else "", flush=True)
    cab = ["disputa", "pst", "hora", "n", "contagem", "a", "b", "c", "c_lo", "c_hi", "d", "d_lo", "d_hi", "m", "final"]
    with open(os.path.join(SAI, "teste2018_instantes.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";"); w.writerow(cab)
        for d in linhas: w.writerow([round(d[k], 4) if isinstance(d[k], float) else d[k] for k in cab])
    ms = ("a", "b", "c", "d", "m")
    resumo["_total"] = dict(abs_medio={m: round(float(np.mean([r["metodos"][m]["abs_medio"] for r in resumo.values()])), 3) for m in ms},
                            melhor={m: sum(min(ms, key=lambda x: r["metodos"][x]["abs_medio"]) == m for r in resumo.values()) for m in ms},
                            m_melhor_que={x: sum(r["metodos"]["m"]["abs_medio"] < r["metodos"][x]["abs_medio"] for r in resumo.values()) for x in "bcd"},
                            concordando_e_errando=sum(r["concordam"]["concordando_e_errando"] for r in resumo.values()))
    json.dump(resumo, open(os.path.join(SAI, "teste2018_resumo.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=lambda o: o.item())
    print(json.dumps(resumo["_total"], ensure_ascii=False, indent=1, default=lambda o: o.item()))

if __name__ == "__main__":
    main()
