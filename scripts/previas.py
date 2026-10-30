"""Prévias de link do estudo (T25; especificação 7.5), em cada língua da página (T30): a imagem da
capa, um cartão por capítulo, as páginas /c/1 … /c/8 e as meta tags (Open Graph) da página principal.

    python -I scripts/previas.py [--miniaturas PASTA]

0. Roda scripts/linguas.py: a página de cada língua sai do catálogo de textos (index.html, en/index.html…).
Para cada língua de site-analise/textos/linguas.js (pasta "" para o português, "en/" para o inglês…):
1. Abre a página da língua no Chrome sem janela e lê da página montada a linha fina, as perguntas e
   as respostas dos capítulos: o texto das prévias é o mesmo da página (e provisório até o T11,
   diário D23).
2. Grava scripts/previas/textos.js e fotografa scripts/previas/cartao.html em 1200 × 627:
   site-analise/img/previa/<pasta>capa.png e c1.png … c9.png.
3. Grava site-analise/<pasta>c/N/index.html: a página pequena de cada capítulo, com a prévia
   própria, que leva direto ao capítulo na língua (o WhatsApp ignora a parte do link depois do "#").
4. Troca, no <head> da página da língua, só o trecho entre os marcadores das prévias.
Os textos fixos das prévias (a pergunta da capa, a fonte, "Capítulo 1 de 8"…) vêm do catálogo
(chaves "prev."), com o português no lugar do que faltar.

Com --miniaturas, grava também as imagens reduzidas a 150 px de largura (e o recorte quadrado do
centro), para conferir a leitura na miniatura do WhatsApp.

Nada é publicado: o endereço nas tags é o do projeto decidido (P19), e o validador de Open Graph
fica para o T09.
"""
import html
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

PASTA_SCRIPTS = Path(__file__).resolve().parent
RAIZ = PASTA_SCRIPTS.parent
SITE = RAIZ / "site-analise"
MOLDE = RAIZ / "scripts" / "previas"
ENDERECO = "analise-da-virada.pages.dev"
URL = f"https://{ENDERECO}"
LARGURA, ALTURA = 1200, 627
CHROMES = [Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
           Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")]
INICIO, FIM = "<!-- prévias de link:", "<!-- fim das prévias de link -->"


def modulo(nome):
    spec = importlib.util.spec_from_file_location(nome, PASTA_SCRIPTS / f"{nome}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


textos = modulo("textos")


def chrome():
    for c in CHROMES:
        if c.exists():
            return str(c)
    sys.exit("Chrome ou Edge não encontrado")


NCAP = 9  # capítulos da leitura (o 8º, dos dados sociais, entrou no T34; o 9º, da exploração guiada, no T33)


def rodar(args, perfil):
    base = [chrome(), "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
            "--allow-file-access-from-files", f"--user-data-dir={perfil}"]
    r = subprocess.run(base + args, capture_output=True, timeout=120)
    return r.stdout.decode("utf-8", "replace")


class Leitor(HTMLParser):
    """Tira da página montada a linha fina e, de cada capítulo, a pergunta e a resposta, sem os sobrescritos."""
    VAZIOS = {"br", "hr", "img", "input", "meta", "link", "source", "col", "area", "base", "wbr"}

    def __init__(self):
        super().__init__()
        self.alvo, self.prof, self.pular = None, 0, None  # pular: a profundidade do sobrescrito em curso
        self.cap = 0
        self.textos = {}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "article" and (a.get("id") or "").startswith("capitulo-"):
            self.cap = int(a["id"].split("-")[1])
        if tag in self.VAZIOS:
            return
        classes = (a.get("class") or "").split()
        if self.alvo:
            self.prof += 1
            if (tag == "sup" or "cap-num" in classes) and self.pular is None:
                self.pular = self.prof
            return
        chave = None
        if a.get("id") == "linha-fina":
            chave = "linha_fina"
        elif self.cap and tag == "h2" and "cap-titulo" in classes:
            chave = f"pergunta{self.cap}"
        elif self.cap and tag == "p" and "resposta" in classes and f"resposta{self.cap}" not in self.textos:
            chave = f"resposta{self.cap}"
        if chave:
            self.alvo, self.prof, self.pular = chave, 1, None
            self.textos[chave] = ""

    def handle_endtag(self, tag):
        if not self.alvo or tag in self.VAZIOS:
            return
        if self.pular == self.prof:
            self.pular = None
        self.prof -= 1
        if self.prof == 0:
            self.alvo = None

    def handle_data(self, data):
        if self.alvo and self.pular is None:
            self.textos[self.alvo] += data


def limpa(s):
    return re.sub(r"\s+", " ", s).strip()


def ate(texto, limite, encher=False):
    """As frases inteiras que cabem no limite. Com encher, uma resposta curta leva o começo da frase seguinte."""
    # chinês e japonês: a frase termina no 。！？ e as frases se juntam sem espaço; o ponto de "0.51" não corta (T44)
    cjk = bool(re.search(r"[。！？]", texto))
    frases = [f for f in re.split(r"(?<=[。！？])", texto) if f] if cjk else re.split(r"(?<=[.!?])\s+", texto)
    junta = "" if cjk else " "
    saida = ""
    for f in frases:
        if len(saida) + len(f) + len(junta) > limite:
            break
        saida = (saida + junta + f).strip()
    # sem nenhuma frase inteira no limite (o cartão do capítulo 7), corta do mesmo jeito, para o cartão não sair vazio
    if (encher or not saida) and len(saida) < 60 and len(texto) > len(saida):
        # resposta curta seguida de frase longa: leva o começo da frase seguinte, cortado numa vírgula ou num espaço
        corte = max(texto.rfind(s, 0, limite) for s in (",", ";", "，", "；"))
        if corte < len(saida) + 40:
            corte = limite - 1 if cjk else texto.rfind(" ", 0, limite)
        saida = texto[:corte].rstrip(" ,;:") + "…"
    return saida


class Lingua:
    """A língua das prévias: a pasta, o catálogo e o formato dos números."""

    def __init__(self, l):
        self.codigo, self.pasta, self.og = l["codigo"], l["pasta"], l["og"]
        self.cat = textos.catalogo(l["codigo"])
        self.pagina = SITE / self.pasta / "index.html"
        self.imagens = SITE / "img" / "previa" / self.pasta
        self.url = f"{URL}/{self.pasta}"  # termina em /

    def t(self, chave, **vals):
        return textos.t(self.cat, chave, **vals)

    def mi(self, v):
        """+4,43 mi: a mesma conta da ponte do capítulo 6, com o sinal decimal da língua."""
        if self.codigo.startswith(("zh", "ja")):  # em 万, no mesmo passo (graficos.js, nMi)
            n = ("−" if v < 0 else "+") + f"{int(abs(v) / 1e4 + 0.5)}"
            return self.t("un.mi", n=n)
        n = ("−" if v < 0 else "+") + f"{abs(v) / 1e6:.2f}".replace(".", self.t("un.decimal"))
        return self.t("un.mi", n=n)


def textos_da_pagina(lingua, perfil):
    dom = rodar(["--virtual-time-budget=10000", "--window-size=1360,900", "--dump-dom", lingua.pagina.as_uri()], perfil)
    leitor = Leitor()
    leitor.feed(dom)
    t = {k: limpa(v) for k, v in leitor.textos.items()}
    falta = [k for k in ["linha_fina"] + [f"{p}{n}" for n in range(1, NCAP + 1) for p in ("pergunta", "resposta")] if not t.get(k)]
    if falta:
        sys.exit(f"Não achei na página {lingua.pagina.relative_to(RAIZ)}: {falta}")
    caps = []
    for n in range(1, NCAP + 1):
        resposta = t[f"resposta{n}"]
        # a exploração leva o rótulo também no cartão e na descrição (HIPOTESES.md, seção 8; revisão final, D63)
        rot = lingua.t("c9.rotulo.curto") + ("" if lingua.codigo.startswith(("zh", "ja")) else " ") if n == 9 else ""
        caps.append({"n": n, "pergunta": t[f"pergunta{n}"], "resposta": rot + resposta,
                     "cartao": rot + ate(resposta, 190 - len(rot)), "descricao": rot + ate(resposta, 240 - len(rot), encher=True),
                     "fonte": lingua.t({7: "prev.fonte_cap7", 8: "prev.fonte_cap8", 9: "prev.fonte_cap9"}.get(n, "prev.fonte"))})
    return {"endereco": ENDERECO + "/" + lingua.pasta.rstrip("/") if lingua.pasta else ENDERECO,
            "capa": {"pergunta": lingua.t("prev.pergunta_capa"), "linha_fina": t["linha_fina"]}, "capitulos": caps}


def fotografar(lingua, textos_previa, perfil):
    """As imagens da língua, com o molde cartao.html; os rótulos fixos e o formato vêm do catálogo."""
    br = json.loads(dados_js())["regioes"]
    rotulos = {
        "nome": lingua.t("pag.nome"), "eleicao": lingua.t("prev.eleicao"), "capitulo_de": lingua.t("prev.capitulo_de"),
        "ponte": lingua.t("prev.ponte"), "turno1": lingua.t("g.turno1"), "turno2": lingua.t("g.turno2"),
        "mi": lingua.t("un.mi"), "regioes": {r["codigo"]: textos.texto(lingua.cat.get("dado." + r["nome"], r["nome"])) for r in br},
    }
    (MOLDE / "textos.js").write_text(
        "// Gravado por scripts/previas.py a partir da página montada e do catálogo de textos. Não editar à mão.\n"
        "window.TEXTOS = " + json.dumps(dict(textos_previa, lingua=lingua.codigo, rotulos=rotulos), ensure_ascii=False, indent=1) + ";\n",
        encoding="utf-8", newline="\n")
    lingua.imagens.mkdir(parents=True, exist_ok=True)
    for c in range(0, NCAP + 1):
        saida = lingua.imagens / ("capa.png" if c == 0 else f"c{c}.png")
        rodar(["--force-device-scale-factor=1", f"--window-size={LARGURA},{ALTURA}", "--virtual-time-budget=5000",
               f"--screenshot={saida}", (MOLDE / "cartao.html").as_uri() + f"?c={c}"], perfil)
        if not saida.exists():
            sys.exit(f"O Chrome não gravou {saida}")


def tags(lingua, titulo, descricao, url, imagem, alt):
    e = lambda s: html.escape(s, quote=True)
    return "\n".join([
        f'<meta property="og:type" content="website">',
        f'<meta property="og:site_name" content="{e(lingua.t("pag.nome"))}">',
        f'<meta property="og:locale" content="{lingua.og}">',
        *[f'<meta property="og:locale:alternate" content="{l["og"]}">' for l in textos.linguas() if l["og"] != lingua.og],
        f'<meta property="og:title" content="{e(titulo)}">',
        f'<meta property="og:description" content="{e(descricao)}">',
        f'<meta property="og:url" content="{e(url)}">',
        f'<meta property="og:image" content="{e(imagem)}">',
        f'<meta property="og:image:type" content="image/png">',
        f'<meta property="og:image:width" content="{LARGURA}">',
        f'<meta property="og:image:height" content="{ALTURA}">',
        f'<meta property="og:image:alt" content="{e(alt)}">',
        f'<meta name="twitter:card" content="summary_large_image">',
    ])


PAGINA_CAP = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>{titulo_html}</title>
<meta name="description" content="{descricao}">
<!-- Gerada por scripts/previas.py (T25, T30). Só existe para a prévia do link deste capítulo: o WhatsApp
     e o LinkedIn ignoram a parte do endereço depois do "#". Quem abre vai direto ao capítulo. -->
{tags}
<script>location.replace('/{pasta}' + location.search + '#analise/{n}');</script>
<style>
:root{{color-scheme:light dark}}
body{{margin:0;padding:48px 24px;background:#f5f1e8;color:#1d1a16;font:18px/1.6 Georgia,serif}}
@media (prefers-color-scheme: dark){{body{{background:#1c1a17;color:#ece4d6}}}}
main{{max-width:36em;margin:0 auto}}
h1{{font-size:30px;line-height:1.2;margin:0 0 12px}}
a{{color:inherit}}
</style>
</head>
<body>
<main>
<p>{de}</p>
<h1>{pergunta}</h1>
<p>{resposta}</p>
<p><a href="/{pasta}#analise/{n}">{ler}</a></p>
</main>
</body>
</html>
"""


def paginas(lingua, textos_previa):
    e = lambda s: html.escape(s, quote=True)
    nome = lingua.t("pag.nome")
    for c in textos_previa["capitulos"]:
        n = c["n"]
        pasta = SITE / lingua.pasta / "c" / str(n)
        pasta.mkdir(parents=True, exist_ok=True)
        t = tags(lingua, lingua.t("prev.cap_titulo", n=n, p=c["pergunta"]), c["descricao"], f"{lingua.url}c/{n}/",
                 f"{URL}/img/previa/{lingua.pasta}c{n}.png", lingua.t("prev.cap_alt", n=n, nome=nome, p=c["pergunta"], cartao=c["cartao"]))
        de = f"<i>{e(nome)}</i>" + e(lingua.t("prev.cap_de", n=n))
        (pasta / "index.html").write_text(PAGINA_CAP.format(
            lang=lingua.codigo, titulo_html=e(lingua.t("pag.titulo_cap", n=n, p=c["pergunta"], nome=nome)), descricao=e(c["descricao"]),
            tags=t, n=n, pasta=lingua.pasta, de=de, pergunta=e(c["pergunta"]), resposta=e(c["resposta"]),
            ler=e(lingua.t("prev.ler", n=n))), encoding="utf-8", newline="\n")


def cabecalho_principal(lingua, textos_previa):
    """Troca só o trecho entre os marcadores, relendo o arquivo na hora (outra sessão pode ter editado)."""
    caminho = lingua.pagina
    texto = caminho.read_text(encoding="utf-8")
    i, f = texto.find(INICIO), texto.find(FIM)
    if i < 0 or f < 0:
        sys.exit(f"Marcadores das prévias não encontrados no <head> de {caminho.relative_to(RAIZ)}")
    capa = textos_previa["capa"]
    bloco = (INICIO + " gravado por scripts/previas.py (T25); texto provisório até o T11 -->\n" +
             tags(lingua, lingua.t("pag.manchete"), capa["linha_fina"], lingua.url, f"{URL}/img/previa/{lingua.pasta}capa.png",
                  lingua.t("prev.capa_alt", pergunta=capa["pergunta"], m1=textos_previa["ponte"][0], m2=textos_previa["ponte"][1])) + "\n")
    novo = texto[:i] + bloco + texto[f:]
    if novo != texto:
        caminho.write_text(novo, encoding="utf-8", newline="\n")


def dados_js():
    dados = (SITE / "dados.js").read_text(encoding="utf-8")
    return dados[dados.index("{"):dados.rindex("}") + 1]


def miniaturas(pasta):
    from PIL import Image
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    for png in sorted((SITE / "img" / "previa").rglob("*.png")):
        im = Image.open(png)
        assert im.size == (LARGURA, ALTURA), f"{png.name}: {im.size}"
        nome = png.relative_to(SITE / "img" / "previa").as_posix().replace("/", "-")[:-4]
        im.resize((150, round(150 * ALTURA / LARGURA)), Image.LANCZOS).save(pasta / f"{nome}-150.png")
        lado = ALTURA
        x = (LARGURA - lado) // 2
        im.crop((x, 0, x + lado, lado)).resize((150, 150), Image.LANCZOS).save(pasta / f"{nome}-quadrado-150.png")
        print(f"{nome}: {im.size[0]} × {im.size[1]}, {png.stat().st_size / 1024:.0f} KB")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    modulo("linguas").gerar()  # as páginas por língua, do catálogo, antes de ler o texto delas
    perfil = tempfile.mkdtemp(prefix="previas-chrome-")
    br = json.loads(dados_js())["brasil"]
    try:
        for l in textos.linguas():
            lingua = Lingua(l)
            textos_previa = textos_da_pagina(lingua, perfil)
            # a ponte da capa, com os mesmos números do capítulo 6
            textos_previa["ponte"] = [lingua.mi(br["M1"]), lingua.mi(br["M2"])]
            fotografar(lingua, textos_previa, perfil)
            paginas(lingua, textos_previa)
            cabecalho_principal(lingua, textos_previa)
            print(f"{lingua.codigo}:")
            for c in textos_previa["capitulos"]:
                print(f"  c{c['n']}: {c['cartao']}")
    finally:
        shutil.rmtree(perfil, ignore_errors=True)
    if "--miniaturas" in sys.argv:
        miniaturas(sys.argv[sys.argv.index("--miniaturas") + 1])


if __name__ == "__main__":
    main()
