"""Confere o catálogo de textos do estudo (T30; especificação 7.11): nenhum texto para o leitor
sobrando no código e nenhuma chave faltando ou sobrando no catálogo.

    python -I scripts/conferir_textos.py

1. Procura, nos scripts da página (site-analise/*.js), literais de texto que parecem frase para o
   leitor (com espaço entre palavras ou com letra acentuada) e não são chave do catálogo, nome de
   classe, seletor ou caminho. Os achados vão para a tela com o arquivo e a linha; a lista PERMITIDOS
   guarda os falsos positivos já conferidos (nomes internos dos dados, que o código compara).
2. Lê as chaves usadas no código (T('…'), T.f('…'), T.p('…'), data-t="…" no HTML) e confere que
   todas existem no catálogo em português. Chaves montadas no código ('c' + n + '.pergunta') não
   entram nessa conta.
3. Para cada outra língua, diz quantas chaves já têm texto próprio e lista chaves que não existem
   em português e marcadores ({n}) que não batem com os do português.
Sai com erro se achar texto solto no código ou chave usada que não existe.
"""
import importlib.util
import re
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parent
SITE = RAIZ / "site-analise"
_spec = importlib.util.spec_from_file_location("textos", PASTA / "textos.py")
textos = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(textos)

# Scripts da página sem texto para o leitor: dados gerados por script e o próprio catálogo
FORA = {"dados.js", "mapa.js", "apuracao-dados.js"}
# Literais conferidos à mão: nomes internos que vêm dos dados e o código compara (o texto que o
# leitor vê sai do catálogo)
PERMITIDOS = {
    "sem peso, dentro dos estados", "sem peso, Brasil", "conjunto, dentro dos estados", "conjunto, Brasil",
    "sem peso", "escala contínua", "fatia entre os dois", "Missão pela regra B", "com sub judice",
    "sem sub judice acima de 5%", "com os outros no controle", "rodada de 2018", "espelho Flávio",
    "contrária", "Flávio", "use strict", "xMidYMin slice",
    "Chave sem texto no catálogo: ",  # aviso para quem mantém a página, no console
    "text/csv;charset=utf-8",
    # o nome do autor nas normas de citação (extras.js): não se traduz
    "Murilo Neves de Martins", "MARTINS, Murilo Neves de", "Martins, Murilo Neves de",
}
CHAVE = re.compile(r"^[a-z][a-z0-9_]*(\.[A-Za-z0-9_À-ú -]+)+$")
PARECE_TEXTO = re.compile(r"[A-Za-zÀ-ú]{2,}[ ,;:][A-Za-zÀ-ú]{2,}|[À-ú]")
NAO_TEXTO = re.compile(r"^[#.\[]|^[a-z-]+(\s+[a-z-]+)*$|^[a-z]+\([^)]*\)$|^\s*$|^https?://"
                       r"|^[a-z0-9_/.-]+\.(js|csv|json|png|jpeg|woff2|html)$")


def literais(js):
    """Os literais de texto de um script, com a linha: pula comentários e expressões regulares e,
    nos textos entre crases, as expressões ${…}."""
    i, n, linha, anterior = 0, len(js), 1, ""
    while i < n:
        c = js[i]
        if js.startswith("//", i):
            f = js.find("\n", i)
            i = n if f < 0 else f
            continue
        if js.startswith("/*", i):
            f = js.find("*/", i + 2)
            linha += js.count("\n", i, f)
            i = f + 2
            continue
        if c == "/" and anterior in "(,=:[!&|?{};+":  # começo de expressão regular
            j, classe = i + 1, False
            while j < n and (js[j] != "/" or classe):
                if js[j] == "\\":
                    j += 1
                elif js[j] == "[":
                    classe = True
                elif js[j] == "]":
                    classe = False
                j += 1
            i, anterior = j + 1, "x"
            continue
        if c in "'\"`":
            j, partes = i + 1, []
            while j < n and js[j] != c:
                if js[j] == "\\":
                    partes.append(js[j:j + 2])
                    j += 2
                    continue
                if c == "`" and js.startswith("${", j):
                    prof = 0
                    while j < n:
                        prof += js[j] == "{"
                        prof -= js[j] == "}"
                        j += 1
                        if prof == 0:
                            break
                    partes.append(" ")
                    continue
                partes.append(js[j])
                j += 1
            yield linha, "".join(partes)
            linha += js.count("\n", i, j)
            i, anterior = j + 1, "x"
            continue
        if c == "\n":
            linha += 1
        elif not c.isspace():
            anterior = c
        i += 1


def soltos(arquivo):
    achados = []
    for linha, s in literais(arquivo.read_text(encoding="utf-8")):
        if s in PERMITIDOS or CHAVE.match(s) or NAO_TEXTO.match(s) or not PARECE_TEXTO.search(s):
            continue
        achados.append((arquivo.name, linha, s.strip()[:90]))
    return achados


def chaves_usadas():
    usadas = set()
    for js in SITE.glob("*.js"):
        if js.name == "lingua.js":  # o comentário do começo explica T('chave'): não é uso
            continue
        t = js.read_text(encoding="utf-8")
        # a chave inteira, não o começo de uma chave montada ('mun.porte' + k)
        usadas.update(re.findall(r"""\bT(?:\.f|\.p|\.fp|\.tem)?\(\s*'([^']+)'(?!\s*\+)""", t))
    usadas.update(re.findall(r'data-t(?:-[a-z-]+)?="([^"]+)"', (SITE / "index.html").read_text(encoding="utf-8")))
    return usadas


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    problemas = 0
    achados = [a for js in sorted(SITE.glob("*.js")) if js.name not in FORA for a in soltos(js)]
    if achados:
        print(f"Texto para o leitor ainda no código ({len(achados)}):")
        for nome, linha, s in achados:
            print(f"  {nome}:{linha}: {s}")
        problemas += len(achados)
    else:
        print("Nenhum texto solto nos scripts da página.")
    pt = textos.catalogo("pt-BR", com_origem=False)
    faltam = sorted(k for k in chaves_usadas() if k not in pt)
    if faltam:
        print(f"Chaves usadas que não existem no catálogo ({len(faltam)}): " + ", ".join(faltam))
        problemas += len(faltam)
    print(f"Catálogo em português: {len(pt)} chaves.")
    for l in textos.linguas():
        if l["codigo"] == "pt-BR":
            continue
        cat = textos.catalogo(l["codigo"], com_origem=False)
        estranhas = sorted(k for k in cat if k not in pt)
        ruins = [k for k in cat if k in pt and textos.marcadores(cat[k]) != textos.marcadores(pt[k])]
        print(f"{l['codigo']}: {len(cat)} de {len(pt)} chaves com texto próprio; as outras caem no português.")
        if estranhas:
            print("  chaves que não existem em português: " + ", ".join(estranhas))
            problemas += len(estranhas)
        if ruins:
            print("  marcadores diferentes do português: " + ", ".join(ruins))
            problemas += len(ruins)
    if problemas:
        sys.exit(f"\nFALHOU: {problemas} problema(s).")
    print("\nResultado: tudo confere.")


if __name__ == "__main__":
    main()
