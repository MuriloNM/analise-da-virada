"""O estudo em PDF, em cada língua da página (T17; especificação 7.8; P25).

    python -I scripts/pdf.py [--lingua es …]

Para cada língua de site-analise/textos/linguas.js:
1. Serve site-analise/ num endereço local de passagem e abre a página da língua no Chrome sem
   janela (Playwright), no modo PDF (?pdf, site-analise/pdf.js): capa, sumário, Resumo, os 9
   capítulos com os detalhes abertos, as notas, Método e fontes e, no fim, o contato do autor. A
   janela tem a largura da página impressa, para os gráficos serem desenhados nela.
2. Grava o PDF duas vezes: na primeira, o título de cada trecho do sumário leva um link para um
   endereço inventado (https://marca.invalid/<id>), que este script procura nas páginas do PDF para
   saber onde cada trecho caiu; na segunda, o sumário já tem os números das páginas e as marcas saem.
   As duas gravações têm de dar o mesmo número de páginas.
3. Grava site-analise/pdf/<nome>-v<versão>.pdf (o nome vem do catálogo, "pdf.arquivo"; a versão, de
   extras.js) e site-analise/pdf/arquivos.js, que o botão "Baixar o estudo em PDF" lê (tamanho,
   páginas e versão de cada língua) e a impressão digital (SHA-256) de cada PDF, que "Versão e
   correções" mostra para quem quiser conferir se uma cópia é igual à original (D72). PDFs de versões
   antigas na pasta são apagados.

Com --lingua, grava só as línguas pedidas (uma língua nova, T43): os PDFs das outras e as linhas delas em
arquivos.js ficam como estão, com a mesma impressão digital.

Rodar depois de mudar texto, número ou versão (e depois do scripts/previas.py, que grava as páginas
das línguas). Nada é publicado: o PDF fica em site-analise/pdf/ e vai junto no T09.
"""
import functools
import hashlib
import http.server
import importlib.util
import json
import re
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parent
SITE = RAIZ / "site-analise"
SAIDA = SITE / "pdf"
ESCALA = 0.8  # o texto de 18 px da página sai com 10,8 pt
LARGURA = round((210 - 2 * 18) / 25.4 * 96 / ESCALA)  # a largura útil da A4 (estudo.css, @page), em px da página
MARCA = "https://marca.invalid/"

_spec = importlib.util.spec_from_file_location("textos", PASTA / "textos.py")
textos = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(textos)


class Calado(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def objetos(pdf):
    """Os objetos do PDF (o Chrome os grava soltos, sem fluxo de objetos): número → texto."""
    s = pdf.decode("latin-1")
    return {int(m.group(1)): m.group(2) for m in re.finditer(r"(\d+) 0 obj\s*(.*?)\s*endobj", s, re.S)}


def paginas_das_marcas(pdf):
    """Em que página (1, 2…) está cada marca https://marca.invalid/<id>."""
    obj = objetos(pdf)
    if any("/ObjStm" in t for t in obj.values()):
        sys.exit("O PDF tem fluxo de objetos: a leitura das marcas precisa ser refeita")
    raiz = next(t for t in obj.values() if re.search(r"/Type\s*/Pages\b", t) and "/Parent" not in t)

    def folhas(t):
        for ref in re.findall(r"(\d+) 0 R", re.search(r"/Kids\s*\[(.*?)\]", t, re.S).group(1)):
            filho = obj[int(ref)]
            if re.search(r"/Type\s*/Pages\b", filho):
                yield from folhas(filho)
            else:
                yield filho

    achadas = {}
    for n, pag in enumerate(folhas(raiz), 1):
        m = re.search(r"/Annots\s*(\[(.*?)\]|(\d+) 0 R)", pag, re.S)
        if not m:
            continue
        lista = m.group(2) if m.group(2) is not None else obj[int(m.group(3))]
        for ref in re.findall(r"(\d+) 0 R", lista):
            u = re.search(r"/URI\s*\((.*?)\)", obj.get(int(ref), ""))
            if u and u.group(1).startswith(MARCA):
                achadas.setdefault(u.group(1)[len(MARCA):], n)
    return achadas


def contar_paginas(pdf):
    obj = objetos(pdf)
    raiz = next(t for t in obj.values() if re.search(r"/Type\s*/Pages\b", t) and "/Parent" not in t)
    return int(re.search(r"/Count\s+(\d+)", raiz).group(1))


def gravar(navegador, url, lingua):
    pagina = navegador.new_page(viewport={"width": LARGURA, "height": 1100})
    pagina.emulate_media(media="print", color_scheme="light")
    erros = []
    pagina.on("console", lambda m: erros.append(m.text) if m.type == "error" and "Failed to load resource" not in m.text else None)
    pagina.on("pageerror", lambda e: erros.append(str(e)))
    pagina.on("response", lambda r: erros.append(f"{r.status} {r.url}") if r.status >= 400 and not r.url.endswith("favicon.ico") else None)
    pagina.goto(url, wait_until="load")
    pagina.wait_for_function("window.PDF_PRONTO === true", timeout=60000)
    # as fontes baixadas só quando aparece um caractere delas (os ideogramas do chinês, T44) precisam ter chegado
    pagina.evaluate("document.fonts.ready.then(() => document.fonts.status)")
    opcoes = dict(prefer_css_page_size=True, print_background=True, scale=ESCALA, outline=True, tagged=True)
    primeiro = pagina.pdf(**opcoes)
    entradas = pagina.evaluate("window.PDF_ENTRADAS")
    onde = paginas_das_marcas(primeiro)
    faltam = [e for e in entradas if e not in onde]
    if faltam:
        sys.exit(f"{lingua}: trechos do sumário sem página no PDF: {', '.join(faltam)}")
    pagina.evaluate("p => window.PDF_SUMARIO(p)", onde)
    final = pagina.pdf(**opcoes)
    n1, n2 = contar_paginas(primeiro), contar_paginas(final)
    if n1 != n2:
        sys.exit(f"{lingua}: as duas gravações deram {n1} e {n2} páginas; o sumário ficaria errado")
    if paginas_das_marcas(final):
        sys.exit(f"{lingua}: sobraram marcas do sumário no PDF final")
    arquivo = pagina.evaluate("window.PDF_ARQUIVO")
    versao = pagina.evaluate("window.ESTUDO_VERSAO.numero")
    pagina.close()
    if erros:
        sys.exit(f"{lingua}: erros na página: " + " | ".join(erros[:5]))
    return final, arquivo, versao, n2, onde


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    servidor = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Calado, directory=str(SITE)))
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{servidor.server_address[1]}/"
    SAIDA.mkdir(exist_ok=True)
    pedidas = sys.argv[sys.argv.index("--lingua") + 1:] if "--lingua" in sys.argv else None
    lista, gravados = {}, set()
    if pedidas:  # as outras línguas ficam como estão
        velho = (SAIDA / "arquivos.js").read_text(encoding="utf-8")
        lista = json.loads(velho[velho.index("{"):velho.rindex("}") + 1])
        lista = {c: v for c, v in lista.items() if c not in pedidas}
        gravados = {v["arquivo"] for v in lista.values()}
    try:
        with sync_playwright() as p:
            navegador = p.chromium.launch(channel="chrome")
            for l in textos.linguas():
                if pedidas and l["codigo"] not in pedidas:
                    continue
                pdf, arquivo, versao, n, onde = gravar(navegador, base + l["pasta"] + "?pdf", l["codigo"])
                (SAIDA / arquivo).write_bytes(pdf)
                gravados.add(arquivo)
                lista[l["codigo"]] = {"arquivo": arquivo, "versao": versao, "paginas": n, "bytes": len(pdf),
                                      "sha256": hashlib.sha256(pdf).hexdigest()}
                print(f"{l['codigo']}: pdf/{arquivo}, {n} páginas, {len(pdf) / 1048576:.1f} MB; "
                      f"capítulos nas páginas {', '.join(str(onde.get(f'capitulo-{i}')) for i in range(1, 10))}")
            navegador.close()
    finally:
        servidor.shutdown()
    lista = {l["codigo"]: lista[l["codigo"]] for l in textos.linguas() if l["codigo"] in lista}
    for velho in SAIDA.glob("*.pdf"):
        if velho.name not in gravados:
            velho.unlink()
            print(f"apagado o PDF de versão antiga: pdf/{velho.name}")
    (SAIDA / "arquivos.js").write_text(
        "// O estudo em PDF de cada língua (gravado por scripts/pdf.py; T17): o arquivo, a versão, as\n"
        "// páginas e o tamanho, para o botão \"Baixar o estudo em PDF\" (pdf.js), e a impressão digital\n"
        "// (SHA-256) de cada PDF, que \"Versão e correções\" mostra (D72).\n"
        "window.PDF_ESTUDO = " + json.dumps(lista, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8", newline="\n")
    print("gravado: pdf/arquivos.js")


if __name__ == "__main__":
    main()
