"""Grava os dados do estudo para baixar em CSV (T25; especificação 7.5 e 7.6), em site-analise/csv/,
uma pasta por língua da página (T30): csv/ em português, csv/en/ em inglês…

    python -I scripts/csv_estudo.py

- municipios.csv, estados.csv, partidos.csv e esquerda_municipios.csv são cópias das bases do
  estudo (T03 e T05), campo por campo, com os mesmos dígitos: o valor é o mesmo das contas
  (diário, D25). Mudam só o formato da língua (abaixo) e a marca UTF-8 no começo, para o Excel
  abrir os acentos. O conteúdo das células de texto (nomes, regiões, regras) fica como nas bases.
- hipoteses.csv e de_onde_vieram.csv achatam dados/inferencia.json (T06), com os números como
  estão no JSON; "sim" e "não" na língua da página. testes_sociais.csv faz o mesmo com os 35 testes dos
  dados sociais (T34), e dados_sociais.csv traz os dados sociais de cada município (T26), como no JSON.
- dicionario.csv descreve cada coluna de cada arquivo, na língua da página.
- arquivos.js lista os arquivos da pasta, com linhas e tamanho, para a página (Método e fontes); a
  descrição de cada arquivo vem do catálogo de textos ("csv.arq.").

apuracao_ao_vivo.csv traz as leituras de dados/historico_2t.json, como a página Apuração ao vivo (T28).

O formato segue a língua da página (pedido do autor, 26/10/2026, diário D41): o separador entre os
campos e o sinal decimal vêm do catálogo da língua ("csv.separador" e "csv.decimal"). Em português,
ponto e vírgula e vírgula decimal, que o Excel em português abre com dois cliques; em inglês, vírgula
e ponto decimal. A troca só muda o separador e o sinal decimal, e o script confere que, desfeita,
ela devolve os mesmos valores. Os textos (descrições do dicionário, cabeçalho dele, sim e não) vêm
do catálogo (site-analise/textos/; scripts/textos.py), com o português no lugar do que faltar.
"""
import csv
import importlib.util
import io
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DADOS = RAIZ / "dados"
SAIDA = RAIZ / "site-analise" / "csv"
_spec = importlib.util.spec_from_file_location("textos", Path(__file__).resolve().parent / "textos.py")
textos = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(textos)

COPIAS = [  # destino, base; a descrição de cada arquivo é a chave "csv.arq.<nome>" do catálogo
    ("municipios.csv", "analise_municipios.csv"),
    ("estados.csv", "analise_estados.csv"),
    ("partidos.csv", "escala_partidos.csv"),
    ("esquerda_municipios.csv", "esquerda_1t_municipios.csv"),
]

# ---------- Dicionário das colunas (T03, T05 e T06) ----------
# Os grupos de colunas, na ordem do dicionário. A descrição de cada grupo é a chave do catálogo
# "csv.col.comum.<primeira coluna>" (as colunas comuns às bases) ou "csv.col.<arquivo>.<primeira coluna>".
COMUNS = [
    "eleitorado_1t, eleitorado_2t", "comparecimento_1t, comparecimento_2t", "abstencao_1t, abstencao_2t",
    "validos_1t, validos_2t", "brancos_nulos_1t, brancos_nulos_2t", "brancos_2t, nulos_2t",
    "lula_1t, flavio_1t, lula_2t, flavio_2t", "outros_1t", "fatia_lula_1t_pct, fatia_lula_2t_pct", "var_fatia_pp",
    "var_lula, var_flavio", "dif_1t, dif_2t, var_dif", "peso_virada_pct", "captura_lula_pct", "var_comparecimento",
    "var_brancos_nulos", "var_eleitorado", "taxa_abst_1t_pct, taxa_abst_2t_pct", "var_taxa_abst_pp", "residuo_identidade",
]
DICIONARIO = {
    "municipios.csv": ["cd_tse", "cd_ibge", "uf, municipio", "regiao", "capital_interior", "porte, porte_faixa"] + COMUNS,
    "estados.csv": ["nivel", "codigo, nome", "regiao", "municipios"] + COMUNS,
    "partidos.csv": ["numero, sigla, nome", "federacao_2026", "posicao", "categoria", "campo_esquerda", "regra, regra_explicada",
                     "sigla_na_pesquisa", "especialistas, desvio_padrao", "fonte",
                     "conf_2018_posicao, conf_2018_campo_esquerda, conf_2018_regra, conf_2018_explicada", "conf_zucco_power_2021"],
    "esquerda_municipios.csv": ["nivel", "cd, uf, nm", "cargo, cargo_nome", "vv, esq, pct_esq", "sem_posicao, pct_sem_posicao", "escala",
                                "lula_1t, flavio_1t, fatia_lula_1t", "vantagem", "sj, sj_esq, pct_esq_com_sj, escala_com_sj, vantagem_com_sj",
                                "conf_2018_pct_esq, conf_2018_sem_posicao, conf_2018_escala, conf_2018_vantagem"],
    "hipoteses.csv": ["hipotese, capitulo", "cargo", "versao", "dentro_dos_estados", "peso", "variavel, controles", "n, grupos",
                      "coef, erro_padrao", "ic95_inf, ic95_sup", "ic95_selvagem_inf, ic95_selvagem_sup", "p_cr1, p_selvagem", "r2, r2_tipo", "efeito_interquartil_pp",
                      "previsto, classificacao, pequena"],
    "apuracao_ao_vivo.csv": ["urnas_apuradas_pct, hora_tse", "lula_2t_pct", "lula_1t_mesmas_urnas_pct", "projecao_final_pct", "lula_1t_por_uf_pct"],
    "dados_sociais.csv": ["cd_tse, cd_ibge, uf, municipio", "pct_60mais", "alfab_15mais", "pct_renda_ate_meio_sm", "pib_pc, ln_pib_pc",
                          "densidade, ln_densidade", "pct_evangelicos", "pct_pretos_pardos", "pop, pop15, pop10, area_km2, pib_mil"],
    "testes_sociais.csv": ["variavel, desfecho", "dentro_dos_estados", "n, grupos", "coef, erro_padrao", "ic95_inf, ic95_sup",
                           "ic95_selvagem_inf, ic95_selvagem_sup", "p_cr1, p_selvagem", "p_holm, p_cr1_holm", "efeito_interquartil",
                           "associacao, direcao, pequena"],
    "de_onde_vieram.csv": ["nivel, lugar, n", "fonte", "lula, lula_ic95_inf, lula_ic95_sup", "flavio, flavio_ic95_inf, flavio_ic95_sup",
                           "meia_largura", "passa_criterio", "maior_parte, motivo", "intervalo", "aviso_modelo"],
}
# números fixos dentro das descrições do dicionário, escritos com o sinal decimal da língua
NUMEROS = {"corte": 4.49, "meio": 0.5, "lim": 0.10, "p05": 0.05}


class Lingua:
    """O que muda de uma língua para outra: a pasta, o formato e os textos do catálogo."""

    def __init__(self, l):
        self.codigo, self.pasta = l["codigo"], SAIDA / l["pasta"]
        self.cat = textos.catalogo(l["codigo"])
        self.sep, self.dec = self.t("csv.separador"), self.t("csv.decimal")

    def t(self, chave, **vals):
        return textos.t(self.cat, chave, **vals)

    def cab(self, coluna):
        """O nome da coluna na língua ("csv.cab.<coluna>"); em português, o das bases."""
        chave = "csv.cab." + coluna
        return self.t(chave) if chave in self.cat or chave in textos.catalogo("pt-BR") else coluna

    def grupo(self, grupo):
        return ", ".join(self.cab(c.strip()) for c in grupo.split(","))

    def descricao(self, arquivo, grupo):
        primeira = grupo.split(",")[0].strip()
        chave = f"csv.col.comum.{primeira}" if grupo in COMUNS else f"csv.col.{arquivo[:-4]}.{primeira}"
        casas = {"corte": 2, "meio": 1, "lim": 2, "p05": 2}
        d = self.t(chave, **{k: f"{v:.{casas[k]}f}".replace(".", self.dec) for k, v in NUMEROS.items()})
        # a descrição que cita outra coluna (com sublinhado) cita o nome na língua do arquivo
        for c in sorted(todas_colunas(), key=len, reverse=True):
            if "_" in c and self.cab(c) != c:
                d = re.sub(rf"(?<!\w){re.escape(c)}(?!\w)", self.cab(c), d)
        return d


def todas_colunas():
    return [c.strip() for grupos in DICIONARIO.values() for g in grupos for c in g.split(",")]


def ler_texto(nome):
    with open(DADOS / nome, encoding="utf-8-sig", newline="") as f:
        return f.read()


NUMERO_DECIMAL = re.compile(r"^-?\d+\.\d+$")


def no_formato(texto, lingua):
    """Passa do formato das bases (vírgula entre campos, ponto decimal) para o da língua da página.
    Só troca o separador e o ponto decimal dos números: os dígitos ficam os mesmos, sem arredondar."""
    sep, dec = lingua.sep, lingua.dec
    linhas = list(csv.reader(io.StringIO(texto)))
    if dec != ".":
        linhas = [[c.replace(".", dec) if NUMERO_DECIMAL.match(c) else c for c in l] for l in linhas]
    buf = io.StringIO()
    csv.writer(buf, delimiter=sep, lineterminator="\n").writerows(linhas)
    volta = [[c.replace(dec, ".") if dec != "." and NUMERO_DECIMAL.match(c.replace(dec, ".")) else c for c in l]
             for l in csv.reader(io.StringIO(buf.getvalue()), delimiter=sep)]
    assert volta == list(csv.reader(io.StringIO(texto))), "a conversão mudou algum valor"
    return buf.getvalue()


def gravar(nome, texto, lingua, cabecalho=True):
    # utf-8-sig: a marca no começo faz o Excel reconhecer os acentos
    if cabecalho:  # o cabeçalho na língua do arquivo (QA nº 14); os valores ficam como estão
        linhas = list(csv.reader(io.StringIO(texto)))
        linhas[0] = [lingua.cab(c) for c in linhas[0]]
        buf = io.StringIO()
        csv.writer(buf, lineterminator="\n").writerows(linhas)
        texto = buf.getvalue()
    with open(lingua.pasta / nome, "w", encoding="utf-8-sig", newline="") as f:
        f.write(no_formato(texto, lingua))


def tabela(linhas, colunas):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(colunas)
    for l in linhas:
        w.writerow(["" if l.get(c) is None else l[c] for c in colunas])
    return buf.getvalue()


def hipoteses(inf, lingua):
    linhas = []
    capitulo = {"H1": 1, "H3": 3, "H4": 4, "H5": 5}
    sim_nao = lambda v: "" if v is None else lingua.t("csv.sim" if v else "csv.nao")

    def linha(h, cargo, v):
        ic = v.get("ic95") or [None, None]
        ics = v.get("ic95_selvagem") or [None, None]  # T32 (M5): intervalo do bootstrap selvagem, por inversão do teste
        return {"hipotese": h, "capitulo": capitulo[h], "cargo": cargo, "versao": v["versao"],
                "dentro_dos_estados": sim_nao(v.get("efeito_fixo_uf")), "peso": v.get("peso"),
                "variavel": v.get("variavel"), "controles": "; ".join(v.get("controles") or []),
                "n": v.get("n"), "grupos": v.get("grupos"), "coef": v.get("coef"), "erro_padrao": v.get("erro_padrao"),
                "ic95_inf": ic[0], "ic95_sup": ic[1], "ic95_selvagem_inf": ics[0], "ic95_selvagem_sup": ics[1], "p_cr1": v.get("p_cr1"), "p_selvagem": v.get("p_selvagem"),
                "r2": v.get("r2"), "r2_tipo": v.get("r2_tipo"), "efeito_interquartil_pp": v.get("efeito_interquartil_pp"),
                "previsto": v.get("previsto"), "classificacao": v.get("classificacao"), "pequena": sim_nao(v.get("pequena"))}

    for h, H in inf["hipoteses"].items():
        for v in H["versoes"]:
            linhas.append(linha(h, "", v))
        for v in inf["complementos"].get(h, []):  # a mesma conta para cada candidato, separado
            linhas.append(linha(h, "", v))
    for chave in ("federal", "estadual", "senador"):
        for v in inf["H5"][chave]["versoes"]:
            linhas.append(linha("H5", inf["H5"][chave]["cargo"], v))
    colunas = ["hipotese", "capitulo", "cargo", "versao", "dentro_dos_estados", "peso", "variavel", "controles", "n", "grupos",
               "coef", "erro_padrao", "ic95_inf", "ic95_sup", "ic95_selvagem_inf", "ic95_selvagem_sup", "p_cr1", "p_selvagem", "r2", "r2_tipo",
               "efeito_interquartil_pp", "previsto", "classificacao", "pequena"]
    return tabela(linhas, colunas), len(linhas)


def de_onde_vieram(inf, lingua):
    linhas = []
    sim_nao = lambda v: "" if v is None else lingua.t("csv.sim" if v else "csv.nao")
    for lugar in inf["por_lugar"]:
        for f in lugar["fontes"].values():
            # com poucos municípios não há estimativa: só o motivo
            li, fi = f.get("lula_ic95") or [None, None], f.get("flavio_ic95") or [None, None]
            linhas.append({"nivel": lugar["nivel"], "lugar": lugar["lugar"], "n": lugar["n"], "fonte": f["fonte"],
                           "lula": f.get("lula"), "lula_ic95_inf": li[0], "lula_ic95_sup": li[1],
                           "flavio": f.get("flavio"), "flavio_ic95_inf": fi[0], "flavio_ic95_sup": fi[1],
                           "meia_largura": f.get("meia_largura"), "passa_criterio": sim_nao(f["passa"]),
                           "maior_parte": f.get("maior_parte"), "motivo": f.get("motivo"),
                           "intervalo": lugar.get("intervalo") if "lula" in f else None,  # T32 (M2, m1)
                           "aviso_modelo": sim_nao(f["aviso_modelo"]) if "aviso_modelo" in f else ""})
    colunas = ["nivel", "lugar", "n", "fonte", "lula", "lula_ic95_inf", "lula_ic95_sup", "flavio", "flavio_ic95_inf",
               "flavio_ic95_sup", "meia_largura", "passa_criterio", "maior_parte", "motivo", "intervalo", "aviso_modelo"]
    return tabela(linhas, colunas), len(linhas)


SOC_COLUNAS = ["pct_60mais", "alfab_15mais", "pct_renda_ate_meio_sm", "pib_pc", "ln_pib_pc", "densidade", "ln_densidade",
               "pct_evangelicos", "pct_pretos_pardos", "pop", "pop15", "pop10", "area_km2", "pib_mil"]


def dados_sociais(_inf, _lingua):
    """Os dados sociais de cada município do Brasil (T26), com o nome do município da base do T03; vazio em
    Boa Esperança do Norte (MT), criado depois do Censo 2022 (nota N20)."""
    soc = json.loads(ler_texto("dados_sociais_municipios.json"))["municipios"]
    nomes = {l["cd_tse"]: l["municipio"] for l in csv.DictReader(io.StringIO(ler_texto("analise_municipios.csv")))}
    linhas = [dict({"cd_tse": cd, "cd_ibge": d["cdi"], "uf": d["uf"], "municipio": nomes[cd]}, **{c: d.get(c) for c in SOC_COLUNAS})
              for cd, d in soc.items()]
    return tabela(linhas, ["cd_tse", "cd_ibge", "uf", "municipio"] + SOC_COLUNAS), len(linhas)


def testes_sociais(inf, lingua):
    """Os 35 testes da seção 6 do HIPOTESES.md (T34), nas duas versões: dentro dos estados (a que decide) e Brasil."""
    sim_nao = lambda v: "" if v is None else lingua.t("csv.sim" if v else "csv.nao")
    linhas = []
    for t in inf["sociais"]["testes"]:
        for ver in ("principal", "brasil"):
            v = t[ver]
            linhas.append({"variavel": t["variavel"], "desfecho": t["desfecho"], "dentro_dos_estados": sim_nao(v["efeito_fixo_uf"]),
                           "n": v["n"], "grupos": v["grupos"], "coef": v["coef"], "erro_padrao": v["erro_padrao"],
                           "ic95_inf": v["ic95"][0], "ic95_sup": v["ic95"][1], "ic95_selvagem_inf": v["ic95_selvagem"][0],
                           "ic95_selvagem_sup": v["ic95_selvagem"][1], "p_cr1": v["p_cr1"], "p_selvagem": v["p_selvagem"],
                           "p_holm": v["p_holm"], "p_cr1_holm": v["p_cr1_holm"], "efeito_interquartil": v["efeito_interquartil_pp"],
                           "associacao": sim_nao(v["associacao"]), "direcao": v["direcao"], "pequena": sim_nao(v["pequena"])})
    colunas = ["variavel", "desfecho", "dentro_dos_estados", "n", "grupos", "coef", "erro_padrao", "ic95_inf", "ic95_sup",
               "ic95_selvagem_inf", "ic95_selvagem_sup", "p_cr1", "p_selvagem", "p_holm", "p_cr1_holm", "efeito_interquartil",
               "associacao", "direcao", "pequena"]
    return tabela(linhas, colunas), len(linhas)


def apuracao_ao_vivo(_inf, _lingua):
    """As leituras gravadas pela página ao vivo do 2º turno, como estão no histórico (a mesma fonte da
    página Apuração ao vivo, T28), na ordem das colunas do CSV que a própria página oferece."""
    hist = json.loads(ler_texto("historico_2t.json"))
    colunas = ["urnas_apuradas_pct", "hora_tse", "lula_2t_pct", "lula_1t_mesmas_urnas_pct", "projecao_final_pct", "lula_1t_por_uf_pct"]
    linhas = [dict(zip(colunas, [h[0], h[4], h[1], h[2], h[3], h[5]])) for h in hist]
    return tabela(linhas, colunas), len(linhas)


def conferir_colunas(nome, texto):
    """Toda coluna do arquivo tem de estar no dicionário, e o dicionário não pode citar coluna que não existe."""
    cab = next(csv.reader(io.StringIO(texto)))
    descritas = [c.strip() for grupo in DICIONARIO[nome] for c in grupo.split(",")]
    faltam = [c for c in cab if c not in descritas]
    sobram = [c for c in descritas if c not in cab]
    assert not faltam and not sobram, f"{nome}: sem descrição {faltam}; no dicionário e não no arquivo {sobram}"


def gravar_lingua(lingua, inf):
    lingua.pasta.mkdir(parents=True, exist_ok=True)
    arquivos = []
    for destino, origem in COPIAS:
        texto = ler_texto(origem)
        conferir_colunas(destino, texto)
        gravar(destino, texto, lingua)
        arquivos.append((destino, texto.count("\n") - 1))
    for destino, fazer in [("hipoteses.csv", hipoteses), ("de_onde_vieram.csv", de_onde_vieram),
                           ("apuracao_ao_vivo.csv", apuracao_ao_vivo), ("testes_sociais.csv", testes_sociais),
                           ("dados_sociais.csv", dados_sociais)]:
        texto, n = fazer(inf, lingua)
        conferir_colunas(destino, texto)
        gravar(destino, texto, lingua)
        arquivos.append((destino, n))
    dic = [{"arquivo": a, "coluna": lingua.grupo(g), "descricao": lingua.descricao(a, g)} for a, grupos in DICIONARIO.items() for g in grupos]
    cab = [lingua.t("csv.dic.arquivo"), lingua.t("csv.dic.coluna"), lingua.t("csv.dic.descricao")]
    texto = tabela([dict(zip(cab, [d["arquivo"], d["coluna"], d["descricao"]])) for d in dic], cab)
    gravar("dicionario.csv", texto, lingua, cabecalho=False)
    arquivos.append(("dicionario.csv", len(dic)))

    lista = [{"nome": n, "linhas": l, "bytes": (lingua.pasta / n).stat().st_size} for n, l in arquivos]
    with open(lingua.pasta / "arquivos.js", "w", encoding="utf-8", newline="\n") as f:
        f.write("// Gerado por scripts/csv_estudo.py. Não editar à mão. A descrição de cada arquivo está no catálogo de textos.\n")
        f.write("window.ARQUIVOS_CSV = " + json.dumps(lista, ensure_ascii=False, indent=1) + ";\n")
    print(f"{lingua.codigo}: {lingua.pasta.relative_to(RAIZ).as_posix()} (separador “{lingua.sep}”, decimal “{lingua.dec}”)")
    for a in lista:
        print(f"  {a['nome']:26} {a['linhas']:>6} linhas {a['bytes'] / 1024:>8.1f} KB")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    inf = json.loads(ler_texto("inferencia.json"))
    for l in textos.linguas():
        gravar_lingua(Lingua(l), inf)


if __name__ == "__main__":
    main()
