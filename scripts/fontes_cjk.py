"""Fontes dos ideogramas da versão em chinês simplificado (T44): o subconjunto da Noto Serif SC e da Noto Sans SC
só com os caracteres que a página, as prévias e o PDF em chinês usam, em woff2, e o bloco das @font-face em
site-analise/estudo.css (entre as marcas "fontes_cjk.py: início" e "fim").

    python -I scripts/fontes_cjk.py PASTA_DAS_FONTES

PASTA_DAS_FONTES tem os arquivos variáveis do Google Fonts (SIL OFL 1.1), fora do repositório por pesarem 43 MB:
NotoSerifSC[wght].ttf e NotoSansSC[wght].ttf (github.com/google/fonts, ofl/notoserifsc e ofl/notosanssc; os
nomes sem "[wght]" também servem). O eixo de peso fica de 400 a 800, os pesos que a página usa.

Rodar de novo sempre que o catálogo em chinês mudar (textos/zh-Hans.js ou comparacao.zh-Hans.json): um
caractere novo fora do subconjunto cairia na fonte do sistema, ou num quadradinho onde não houver fonte. A
conferência no fim diz se algum caractere chinês das páginas ficou de fora.
"""
import re
import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

RAIZ = Path(__file__).resolve().parent.parent
SITE = RAIZ / "site-analise"
CSS = SITE / "estudo.css"
FONTES = SITE / "fontes"
CODIGO = "zh-Hans"
# de onde vêm os textos em chinês: o catálogo, os estudos externos, as páginas e as prévias gravadas
ORIGENS = [SITE / "textos" / f"{CODIGO}.js", RAIZ / "docs" / "analise" / "monitoramento" / f"comparacao.{CODIGO}.json"]
PASTAS = [SITE / "zh", SITE / "csv" / "zh"]
# o que o navegador escreve sozinho na língua (datas e listas do Intl) e a pontuação de largura total
EXTRAS = "年月日时分秒上下午周星期一二三四五六七八九十〇和或、，。：；？！（）《》〈〉【】「」『』—…～·％＋－＝"
FAMILIAS = [("Noto Serif SC", "NotoSerifSC", "noto-serif-sc"), ("Noto Sans SC", "NotoSansSC", "noto-sans-sc")]


def cjk(c):
    o = ord(c)
    return (0x2E80 <= o <= 0x9FFF or 0xF900 <= o <= 0xFAFF or 0xFE30 <= o <= 0xFE4F or 0xFF00 <= o <= 0xFFEF
            or 0x20000 <= o <= 0x2FA1F)


def caracteres():
    texto = EXTRAS
    for f in ORIGENS:
        if not f.exists():
            sys.exit(f"falta {f.relative_to(RAIZ)}")
        texto += f.read_text(encoding="utf-8")
    for p in PASTAS:
        for f in p.rglob("*"):
            if f.suffix in {".html", ".js", ".csv", ".md"}:
                texto += f.read_text(encoding="utf-8", errors="ignore")
    return sorted({c for c in texto if cjk(c)})


def faixas(cs):
    ns = sorted(ord(c) for c in cs)
    saida, ini, ant = [], ns[0], ns[0]
    for n in ns[1:] + [None]:
        if n is not None and n == ant + 1:
            ant = n
            continue
        saida.append(f"U+{ini:04X}" if ini == ant else f"U+{ini:04X}-{ant:04X}")
        if n is not None:
            ini = ant = n
    return ",".join(saida)


def origem(pasta, base):
    for nome in (f"{base}[wght].ttf", f"{base}.ttf"):
        if (pasta / nome).exists():
            return pasta / nome
    sys.exit(f"não achei {base}[wght].ttf em {pasta}")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    pasta = Path(sys.argv[1])
    cs = caracteres()
    texto = "".join(cs)
    blocos = []
    for familia, base, saida in FAMILIAS:
        fonte = TTFont(origem(pasta, base))
        fonte = instancer.instantiateVariableFont(fonte, {"wght": (400, 800)})
        opcoes = subset.Options()
        opcoes.flavor = "woff2"
        opcoes.layout_features = ["*"]
        opcoes.name_IDs = ["*"]
        sub = subset.Subsetter(opcoes)
        sub.populate(text=texto)
        sub.subset(fonte)
        destino = FONTES / f"{saida}.woff2"
        fonte.flavor = "woff2"
        fonte.save(destino)
        faltam = [c for c in cs if ord(c) not in fonte.getBestCmap()]
        print(f"{destino.relative_to(RAIZ)}: {destino.stat().st_size // 1024} KB, {len(cs) - len(faltam)} de {len(cs)} caracteres")
        if faltam:
            print("  sem glifo nesta fonte: " + "".join(faltam))
        blocos.append(f'@font-face{{font-family:"{familia}";font-style:normal;font-weight:400 800;font-display:swap;'
                      f'src:url(fontes/{saida}.woff2) format("woff2");unicode-range:{faixas(cs)}}}')
    css = CSS.read_text(encoding="utf-8")
    novo, n = re.subn(r"(/\* fontes_cjk\.py: início \*/\n).*?(/\* fontes_cjk\.py: fim \*/)",
                      lambda m: m.group(1) + "\n".join(blocos) + "\n" + m.group(2), css, flags=re.S)
    if n != 1:
        sys.exit("não achei as marcas do bloco em estudo.css")
    CSS.write_text(novo, encoding="utf-8", newline="")
    print(f"estudo.css: {len(cs)} caracteres chineses no unicode-range")


if __name__ == "__main__":
    main()
