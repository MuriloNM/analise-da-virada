"""Compara o texto de duas versões da página do estudo, frase por frase e número por número (T30).

    python -I scripts/comparar_paginas.py URL_ANTES URL_DEPOIS [--largura 1360] [--saida PASTA]

Abre as duas no Chrome sem janela, deixa a página montar os gráficos e grava o DOM montado. De cada
uma tira, na ordem do documento, o texto de cada bloco (parágrafo, título, célula, rótulo do gráfico,
item de lista…) e os atributos que o leitor ou o leitor de tela recebem (aria-label, title,
placeholder, alt, content das meta tags, href dos links). O que fica fora: os atributos data-t* do
catálogo e o que só existe depois do T30 para ligar as línguas (o botão de língua, os links hreflang
e as meta og:locale:alternate).
Mostra as diferenças e sai com erro se houver alguma. Com --saida, grava os dois textos para
conferir à mão.
Usado para provar que o português não muda ao passar os textos para o catálogo (T30) e, depois, a
cada língua nova (skill traduzir-estudo).
"""
import difflib
import re
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

CHROMES = [Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
           Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")]
BLOCOS = {"p", "li", "h1", "h2", "h3", "h4", "td", "th", "caption", "figcaption", "dt", "dd", "summary", "button",
          "label", "title", "text", "tspan", "option", "div", "section", "article", "header", "footer", "nav", "ul",
          "ol", "dl", "table", "tr", "figure", "aside", "pre", "main", "form", "details", "svg", "g", "noscript"}
ATRIBUTOS = ("aria-label", "title", "placeholder", "alt", "content", "href", "lang")
VAZIOS = {"br", "hr", "img", "input", "meta", "link", "source", "col", "area", "base", "wbr", "image", "circle",
          "rect", "line", "path", "stop", "use", "polygon", "polyline", "ellipse"}


class Texto(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.linhas, self.buf, self.pular, self.fora = [], [], 0, 0

    def soltar(self):
        t = re.sub(r"\s+", " ", "".join(self.buf)).strip()
        if t:
            self.linhas.append(t)
        self.buf = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("script", "style"):
            self.pular += 1
            return
        if ("linguas" in (a.get("class") or "").split() or (tag == "link" and a.get("hreflang"))
                or (tag == "meta" and a.get("property") == "og:locale:alternate")):
            if tag not in VAZIOS:
                self.fora += 1
            return
        if self.fora:
            if tag not in VAZIOS:
                self.fora += 1
            return
        if tag in BLOCOS:
            self.soltar()
        for k in ATRIBUTOS:
            v = a.get(k)
            if v and not (k == "lang" and tag != "html"):
                self.linhas.append(f"@{k}={re.sub(chr(10) + '|' + chr(13), ' ', v).strip()}")

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VAZIOS and tag not in ("script", "style"):
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.pular = max(0, self.pular - 1)
            return
        if self.fora:
            if tag not in VAZIOS:
                self.fora -= 1
            return
        if tag in BLOCOS:
            self.soltar()

    def handle_data(self, data):
        if not self.pular and not self.fora:
            self.buf.append(data)


def chrome():
    for c in CHROMES:
        if c.exists():
            return str(c)
    sys.exit("Chrome ou Edge não encontrado")


def dom(url, largura, perfil):
    r = subprocess.run([chrome(), "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
                        f"--user-data-dir={perfil}", "--virtual-time-budget=15000", f"--window-size={largura},900",
                        "--dump-dom", url], capture_output=True, timeout=180)
    return r.stdout.decode("utf-8", "replace")


def texto(html):
    t = Texto()
    t.feed(html)
    t.soltar()
    return t.linhas


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    largura = int(args[args.index("--largura") + 1]) if "--largura" in args else 1360
    saida = Path(args[args.index("--saida") + 1]) if "--saida" in args else None
    antes_url, depois_url = [a for a in args if a.startswith("http") or a.startswith("file:")][:2]
    perfil = tempfile.mkdtemp(prefix="comparar-chrome-")
    try:
        antes, depois = texto(dom(antes_url, largura, perfil)), texto(dom(depois_url, largura, perfil))
    finally:
        shutil.rmtree(perfil, ignore_errors=True)
    if saida:
        saida.mkdir(parents=True, exist_ok=True)
        (saida / f"antes-{largura}.txt").write_text("\n".join(antes), encoding="utf-8")
        (saida / f"depois-{largura}.txt").write_text("\n".join(depois), encoding="utf-8")
    diff = list(difflib.unified_diff(antes, depois, "antes", "depois", n=1, lineterm=""))
    numeros = lambda ls: re.findall(r"[−+-]?\d[\d.,]*", "\n".join(ls))
    print(f"{largura} px: {len(antes)} trechos antes, {len(depois)} depois; "
          f"{len(numeros(antes))} números antes, {len(numeros(depois))} depois.")
    if diff:
        print("\n".join(diff[:400]))
        sys.exit(f"\nDIFERENTE: {sum(1 for l in diff if l[:1] in '+-' and l[:3] not in ('+++', '---'))} linhas.")
    print("Igual: o mesmo texto, os mesmos números e os mesmos atributos.")


if __name__ == "__main__":
    main()
