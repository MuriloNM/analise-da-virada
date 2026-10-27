"""Catálogos de textos do estudo para os scripts (T30; especificação 7.11, diário D42).

O texto para o leitor vive em site-analise/textos/<língua>.js (pt-BR.js é a origem) e as línguas que
existem, em site-analise/textos/linguas.js. Este módulo lê os dois para os scripts que escrevem texto
(previas.py, csv_estudo.py, linguas.py, pagina_dados.py, conferir_textos.py), com as mesmas regras
da página (lingua.js): a chave que falta numa língua cai no português, e {nome} é um marcador.

Uso, a partir de outro script da pasta (rodados com python -I, sem a pasta no caminho):
    import importlib.util
    spec = importlib.util.spec_from_file_location("textos", Path(__file__).parent / "textos.py")
    textos = importlib.util.module_from_spec(spec); spec.loader.exec_module(textos)
"""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "site-analise" / "textos"
ORIGEM = "pt-BR"


def _json_do_js(texto, nome):
    """O objeto JSON de um arquivo de catálogo: sem as linhas de comentário e sem a vírgula final."""
    linhas = [l for l in texto.split("\n") if not l.lstrip().startswith("//")]
    corpo = "\n".join(linhas)
    i = corpo.index("{", corpo.index("=", corpo.index(nome)))
    corpo = corpo[i:corpo.rindex("}") + 1]
    corpo = re.sub(r",(\s*[}\]])", r"\1", corpo)
    return json.loads(corpo)


def linguas():
    """[{codigo, nome, pasta, og}], na ordem do botão de língua; o português primeiro."""
    texto = (PASTA / "linguas.js").read_text(encoding="utf-8")
    linhas = [l for l in texto.split("\n") if not l.lstrip().startswith("//")]
    corpo = "\n".join(linhas)
    return json.loads(re.sub(r",(\s*\])", r"\1", corpo[corpo.index("["):corpo.rindex("]") + 1]))


def catalogo(codigo, com_origem=True):
    """As chaves da língua; com_origem completa as que faltam com o português."""
    arquivo = PASTA / f"{codigo}.js"
    cat = _json_do_js(arquivo.read_text(encoding="utf-8"), f"window.TEXTOS['{codigo}']") if arquivo.exists() else {}
    if com_origem and codigo != ORIGEM:
        return {**catalogo(ORIGEM, False), **cat}
    return cat


def texto(valor):
    """O texto de um valor do catálogo: o próprio texto, ou o "t" de um rótulo ou de um texto fixo."""
    return valor if isinstance(valor, (str, list)) else valor.get("t", valor)


def t(cat, chave, **vals):
    """A frase da chave, com os marcadores preenchidos. Chave que não existe é erro."""
    if chave not in cat:
        raise KeyError(f"chave sem texto no catálogo: {chave}")
    s = texto(cat[chave])
    return re.sub(r"\{(\w+)\}", lambda m: str(vals[m.group(1)]) if m.group(1) in vals else m.group(0), s)


def marcadores(valor):
    """Os marcadores {nome} de um valor, em todas as formas (plural, lista), para comparar línguas."""
    if isinstance(valor, dict):
        partes = [v for k, v in valor.items() if k not in ("rotulo", "fixo")]
    elif isinstance(valor, list):
        partes = valor
    else:
        partes = [valor]
    return sorted({m for p in partes if isinstance(p, str) for m in re.findall(r"\{(\w+)\}", p)})
