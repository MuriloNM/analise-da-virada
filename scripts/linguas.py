"""Páginas do estudo por língua (T30; especificação 7.11, diário D42).

    python -I scripts/linguas.py [--conferir]

site-analise/index.html é o molde e a página em português. Para cada língua de
site-analise/textos/linguas.js, este script:
1. troca o texto de cada elemento marcado pelo do catálogo da língua (textos/<língua>.js, com o
   português no lugar do que faltar): data-t="chave" troca o texto, data-t-html="chave" o texto com
   marcação e data-t-<atributo>="chave" o atributo (placeholder, aria-label, content…). O <title> e
   os textos com {titulo} e {nome} recebem a manchete e o nome do estudo;
2. põe o lang da língua no <html>, os links hreflang entre as versões (com o endereço publicado,
   P19) e a conferência da língua guardada, que leva à página da língua escolhida antes de desenhar;
3. grava o botão de língua no menu do alto, só com as línguas que existem, cada uma escrita nela
   mesma (textos/linguas.js);
4. nas outras línguas, grava a página na pasta delas (en/index.html…), com os caminhos dos arquivos
   ajustados (../estudo.css), o catálogo da língua carregado depois do português e a lista dos CSV
   da língua (csv/en/arquivos.js).
O trecho das prévias de link (<!-- prévias de link: … -->) de cada página é do scripts/previas.py:
este script o mantém como está na página da língua, se ela já existir.

A página de privacidade (site-analise/privacidade/index.html, T17) passa pelo mesmo caminho, como
subpágina: a de cada língua fica em <pasta da língua>privacidade/ (en/privacidade/…), com os arquivos
do estudo apontados a partir dela e o botão de língua levando à privacidade da outra língua. Os links
para privacidade/ da página principal ficam relativos, para levar à privacidade da língua da página.

Com --conferir, não grava nada: diz se alguma página está diferente do que o catálogo pede (por
exemplo, depois de mudar um texto no catálogo sem rodar o script) e sai com erro nesse caso.
Rodado também pelo scripts/previas.py, antes das prévias.
"""
import html
import importlib.util
import json
import re
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parent
SITE = RAIZ / "site-analise"
URL = "https://analise-da-virada.pages.dev/"
_spec = importlib.util.spec_from_file_location("textos", PASTA / "textos.py")
textos = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(textos)

PREVIAS = ("<!-- prévias de link:", "<!-- fim das prévias de link -->")
BLOCO_LINGUAS = ("<!-- línguas: gravado por scripts/linguas.py (T30) -->", "<!-- fim das línguas -->")
BLOCO_BOTAO = ("<!-- botão de língua: gravado por scripts/linguas.py (T30) -->", "<!-- fim do botão de língua -->")
ELEMENTO = re.compile(r'(<(\w+)\b[^>]*?\sdata-t(-html)?="([^"]+)"[^>]*>)(.*?)(</\2>)', re.S)
ABERTURA = re.compile(r"<\w+\b[^>]*\sdata-t-(?!html\b)[a-z-]+=\"[^\"]*\"[^>]*>")
CAMINHO = re.compile(r'\s(src|href)="(?!#|https?:|/|mailto:|data:|\.\./|privacidade/)([^"]*)"')
# numa subpágina (privacidade/), os arquivos do estudo, a partir da raiz: ../estudo.css, ../textos/pt-BR.js…
ARQUIVO_RAIZ = re.compile(r'\s(src|href)="\.\./([^"]*\.(?:css|js|woff2|png|svg|ico))"')
SUBPAGINAS = ["privacidade/"]


def trocar_bloco(texto, marcas, conteudo):
    i, f = texto.find(marcas[0]), texto.find(marcas[1])
    if i < 0 or f < 0:
        sys.exit(f"Marcadores não encontrados: {marcas[0]}")
    return texto[:i] + marcas[0] + "\n" + conteudo + texto[f:]


def bloco_de(texto, marcas):
    i, f = texto.find(marcas[0]), texto.find(marcas[1])
    return texto[i:f + len(marcas[1])] if i >= 0 and f >= 0 else None


def pagina(molde, lingua, linguas, existente, sub=""):
    cod, pasta = lingua["codigo"], lingua["pasta"]
    raiz = re.sub(r"[^/]+", "..", pasta + sub)  # o caminho de volta à raiz do estudo
    cat = textos.catalogo(cod)
    valores = {"titulo": textos.t(cat, "pag.manchete"), "nome": textos.t(cat, "pag.nome")}
    t = lambda chave: textos.t(cat, chave, **valores)

    def elemento(m):
        abertura, _, com_html, chave, _, fim = m.groups()
        return abertura + (t(chave) if com_html else html.escape(t(chave), quote=False)) + fim

    def atributos(m):
        tag = m.group(0)
        for attr, chave in re.findall(r'\sdata-t-(?!html\b)([a-z-]+)="([^"]+)"', tag):
            novo = f'{attr}="{html.escape(t(chave), quote=True)}"'
            if re.search(rf'\s{attr}="[^"]*"', tag):
                tag = re.sub(rf'(\s){attr}="[^"]*"', lambda x: x.group(1) + novo, tag, count=1)
            else:
                tag = tag[:-1] + " " + novo + ">"
        return tag

    s = re.sub(r'<html lang="[^"]*">', f'<html lang="{cod}">', molde, count=1)
    s = ELEMENTO.sub(elemento, s)
    s = ABERTURA.sub(atributos, s)
    if pasta and sub:
        # subpágina de outra língua: o catálogo da língua depois do português; os arquivos, a partir da raiz
        s = s.replace('<script src="../textos/pt-BR.js"></script>',
                      f'<script src="../textos/pt-BR.js"></script>\n<script src="../textos/{cod}.js"></script>')
        s = ARQUIVO_RAIZ.sub(lambda m: f' {m.group(1)}="{raiz}{m.group(2)}"', s)
    elif pasta:
        # os arquivos ficam na raiz do estudo: a página da língua aponta para eles; o catálogo da
        # língua entra depois do português, e a lista dos CSV é a da pasta da língua
        s = s.replace('<script src="csv/arquivos.js"></script>', f'<script src="csv/{pasta}arquivos.js"></script>')
        s = s.replace('<script src="textos/pt-BR.js"></script>',
                      f'<script src="textos/pt-BR.js"></script>\n<script src="textos/{cod}.js"></script>')
        s = CAMINHO.sub(lambda m: f' {m.group(1)}="{raiz}{m.group(2)}"', s)
    # links entre as versões, para a busca e as prévias, e a língua guardada (antes de desenhar)
    alternativas = "".join(f'<link rel="alternate" hreflang="{l["codigo"]}" href="{URL}{l["pasta"]}{sub}">\n' for l in linguas)
    alternativas += f'<link rel="alternate" hreflang="x-default" href="{URL}{sub}">\n'
    destinos = json.dumps({l["codigo"]: l["pasta"] for l in linguas})
    if sub and not pasta:
        pass  # a subpágina em português não leva à língua guardada: só a raiz faz isso (D66)
    elif not pasta:
        # só a raiz obedece à língua guardada (D66)
        alternativas += ("<script>\n/* A língua escolhida no botão fica guardada, como o tema: a raiz leva à versão dela, no mesmo trecho. */\n"
                         "(function(){\n"
                         f"  var p = {destinos}, l;\n"
                         "  try { l = localStorage.getItem('analise-lingua'); } catch (_) {}\n"
                         f"  if (l && l !== '{cod}' && p.hasOwnProperty(l)) location.replace('{raiz}' + p[l] + location.hash);\n"
                         "})();\n</script>\n")
    else:
        # o endereço de uma língua abre sempre nela (o Voltar e o link compartilhado funcionam, D66); só grava a escolha
        alternativas += ("<script>\n/* O endereço desta língua abre sempre nela e grava a escolha, para a raiz do estudo levar a ela. */\n"
                         f"try {{ localStorage.setItem('analise-lingua', '{cod}'); }} catch (_) {{}}\n"
                         "</script>\n")
    s = trocar_bloco(s, BLOCO_LINGUAS, alternativas)
    # o botão de língua: o nome de cada língua escrito nela mesma; a atual marcada
    if len(linguas) > 1:
        itens = "".join(
            f'        <li><a href="{raiz + l["pasta"] + sub or "./"}" lang="{l["codigo"]}" hreflang="{l["codigo"]}" data-lingua="{l["codigo"]}"'
            + (' aria-current="true"' if l["codigo"] == cod else "") + f'>{html.escape(l["nome"])}</a></li>\n'
            for l in linguas)
        botao = ('    <details class="linguas">\n'
                 f'      <summary><span class="sr">{html.escape(t("cab.lingua"))}</span><span class="ling-nome" lang="{cod}">{html.escape(lingua["nome"])}</span>'
                 f'<span class="ling-curto" lang="{cod}">{cod.split("-")[0].lower()}</span></summary>\n'
                 f'      <ul aria-label="{html.escape(t("cab.lingua_lista"), quote=True)}">\n{itens}      </ul>\n'
                 '    </details>\n    ')
    else:
        botao = "    "
    s = trocar_bloco(s, BLOCO_BOTAO, botao)
    # as prévias de link da língua são do previas.py: ficam como estão na página que já existe
    if existente and pasta:
        antigo = bloco_de(existente, PREVIAS)
        if antigo:
            s = s.replace(bloco_de(s, PREVIAS), antigo)
    return s


def gerar(conferir=False):
    linguas = textos.linguas()
    diferentes = []
    for sub in [""] + SUBPAGINAS:
        molde = (SITE / sub / "index.html").read_text(encoding="utf-8")
        for l in linguas:
            destino = SITE / l["pasta"] / sub / "index.html"
            existente = destino.read_text(encoding="utf-8") if destino.exists() else None
            novo = pagina(molde, l, linguas, existente, sub)
            if novo != existente:
                diferentes.append(destino.relative_to(RAIZ).as_posix())
                if not conferir:
                    destino.parent.mkdir(parents=True, exist_ok=True)
                    destino.write_text(novo, encoding="utf-8", newline="\n")
    return diferentes


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    conferir = "--conferir" in sys.argv
    diferentes = gerar(conferir)
    if conferir:
        if diferentes:
            sys.exit("Diferente do catálogo (rodar python -I scripts/linguas.py): " + ", ".join(diferentes))
        print("As páginas de todas as línguas batem com o catálogo.")
    else:
        print("Gravadas: " + (", ".join(diferentes) if diferentes else "nada mudou"))


if __name__ == "__main__":
    main()
