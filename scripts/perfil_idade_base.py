"""T37: base do perfil de comparecimento e abstenção do TSE (2026), por idade.

Lê, sem extrair, os CSV por UF de `dados/tse_perfil_comparecimento/perfil_comparecimento_abstencao_2026.zip`
(o `_BRASIL.csv`, de 3 GB, não é lido: é a soma dos outros) e grava:
- `dados/perfil_idade.csv.gz`: soma por turno, UF, município (código do TSE), zona, faixa de idade e gênero;
- `dados/perfil_idade_instrucao.csv.gz`: soma por turno, UF, faixa de idade e grau de instrução;
- `dados/perfil_idade_meta.json`: turnos presentes, faixas, data de geração e a conferência
  dos totais contra o comparecimento e a abstenção oficiais do T03 (`dados/analise_municipios.csv`).

Só agrega e confere; as taxas por idade saem do `perfil_idade.py`, depois do registro na seção 8
do HIPOTESES.md. Rodar com `python -I scripts/perfil_idade_base.py`.
"""
import csv
import gzip
import io
import json
import os
import sys
import zipfile
from collections import defaultdict

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZIP = os.path.join(RAIZ, "dados", "tse_perfil_comparecimento", "perfil_comparecimento_abstencao_2026.zip")
SAIDA = os.path.join(RAIZ, "dados", "perfil_idade.csv.gz")
SAIDA_INSTR = os.path.join(RAIZ, "dados", "perfil_idade_instrucao.csv.gz")
META = os.path.join(RAIZ, "dados", "perfil_idade_meta.json")
OFICIAL = os.path.join(RAIZ, "dados", "analise_municipios.csv")

QTS = ["QT_APTOS", "QT_COMPARECIMENTO", "QT_ABSTENCAO",
       "QT_COMPAREC_FACULTATIVO", "QT_ABST_FACULTATIVO",
       "QT_COMPAREC_OBRIGATORIO", "QT_ABST_OBRIGATORIO",
       "QT_COMPARECIMENTO_TTE", "QT_ABSTENCAO_TTE"]
NOMES = ["aptos", "comp", "abst", "comp_fac", "abst_fac", "comp_obr", "abst_obr", "comp_tte", "abst_tte"]


def ler():
    por_mun = defaultdict(lambda: [0] * len(QTS))
    por_instr = defaultdict(lambda: [0] * len(QTS))
    faixas, geracao, linhas = {}, set(), 0
    with zipfile.ZipFile(ZIP) as z:
        nomes = sorted(n for n in z.namelist() if n.endswith(".csv") and not n.endswith("_BRASIL.csv"))
        for nome in nomes:
            with z.open(nome) as bruto:
                leitor = csv.DictReader(io.TextIOWrapper(bruto, encoding="latin-1", newline=""), delimiter=";")
                for r in leitor:
                    linhas += 1
                    v = [int(r[q]) for q in QTS]
                    turno, uf, faixa = int(r["NR_TURNO"]), r["SG_UF"], int(r["CD_FAIXA_ETARIA"])
                    faixas[faixa] = r["DS_FAIXA_ETARIA"].strip()
                    geracao.add(r["DT_GERACAO"])
                    k = (turno, uf, r["CD_MUNICIPIO"], int(r["NR_ZONA"]), faixa, int(r["CD_GENERO"]))
                    a = por_mun[k]
                    for i, x in enumerate(v):
                        a[i] += x
                    b = por_instr[(turno, uf, faixa, int(r["CD_GRAU_INSTRUCAO"]))]
                    for i, x in enumerate(v):
                        b[i] += x
            print(f"  {nome}: {linhas:,} linhas até aqui", file=sys.stderr)
    return por_mun, por_instr, faixas, sorted(geracao), linhas


def oficial():
    of = {}
    with open(OFICIAL, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            of[(r["uf"], r["cd_tse"])] = r
    return of


def main():
    por_mun, por_instr, faixas, geracao, linhas = ler()

    with gzip.open(SAIDA, "wt", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["turno", "uf", "cd_tse", "zona", "faixa", "genero"] + NOMES)
        for k in sorted(por_mun):
            w.writerow(list(k) + por_mun[k])
    with gzip.open(SAIDA_INSTR, "wt", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["turno", "uf", "faixa", "instrucao"] + NOMES)
        for k in sorted(por_instr):
            w.writerow(list(k) + por_instr[k])

    # Conferência das identidades internas e contra o T03, por município e turno.
    turnos = sorted({k[0] for k in por_mun})
    mun = defaultdict(lambda: [0] * len(QTS))
    for k, v in por_mun.items():
        a = mun[(k[0], k[1], k[2])]
        for i, x in enumerate(v):
            a[i] += x
    identidade = sum(1 for v in mun.values()
                     if v[0] != v[1] + v[2] or v[1] != v[3] + v[5] or v[2] != v[4] + v[6])

    of = oficial()
    conf = {}
    for t in turnos:
        dif = []
        tot = {"perfil_aptos": 0, "perfil_comp": 0, "perfil_abst": 0,
               "oficial_aptos": 0, "oficial_comp": 0, "oficial_abst": 0,
               "perfil_tte": 0, "soma_abs_dif_aptos": 0}
        chaves = {(k[1], k[2]) for k in mun if k[0] == t}
        for chave in sorted(chaves | set(of)):
            v = mun.get((t, chave[0], chave[1]), [0] * len(QTS))
            o = of.get(chave)
            oa = int(o[f"eleitorado_{t}t"]) if o else 0
            oc = int(o[f"comparecimento_{t}t"]) if o else 0
            ob = int(o[f"abstencao_{t}t"]) if o else 0
            for n, x in (("perfil_aptos", v[0]), ("perfil_comp", v[1]), ("perfil_abst", v[2]),
                         ("oficial_aptos", oa), ("oficial_comp", oc), ("oficial_abst", ob)):
                tot[n] += x
            tot["perfil_tte"] += v[7] + v[8]
            tot["soma_abs_dif_aptos"] += abs(v[0] - oa)
            if (v[0], v[1], v[2]) != (oa, oc, ob):
                dif.append({"uf": chave[0], "cd_tse": chave[1], "municipio": o["municipio"] if o else None,
                            "perfil": v[:3], "oficial": [oa, oc, ob]})
        conf[f"{t}t"] = {"totais": tot, "municipios_diferentes": len(dif), "diferencas": dif[:200]}

    meta = {
        "fonte": "https://cdn.tse.jus.br/estatistica/sead/odsele/perfil_comparecimento_abstencao/perfil_comparecimento_abstencao_2026.zip",
        "dt_geracao": geracao,
        "linhas_lidas": linhas,
        "turnos": turnos,
        "faixas": {str(k): faixas[k] for k in sorted(faixas)},
        "municipios_com_identidade_quebrada": identidade,
        "conferencia_t03": conf,
    }
    with open(META, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)

    print("turnos:", turnos, "| gerado em:", geracao, "| linhas:", f"{linhas:,}")
    print("faixas:", "; ".join(f"{k} {v}" for k, v in sorted(faixas.items())))
    print("identidade quebrada (aptos=comp+abst; comp=fac+obr):", identidade)
    for t, c in conf.items():
        print(t, c["totais"], "| municípios diferentes:", c["municipios_diferentes"])


if __name__ == "__main__":
    main()
