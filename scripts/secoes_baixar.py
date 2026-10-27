# Baixa os dados por seção do T27, caminho B (P11, D54), como vieram do TSE: boletins de urna do 2º turno
# (28 UFs), votação de presidente por seção do 1º turno e detalhe da apuração por seção (os dois turnos).
# Um arquivo por vez, em blocos, com pausa e nova tentativa no 429. Arquivos já baixados são pulados.
# Confere o tamanho com o Content-Length e, nos boletins, o sha512 publicado pelo TSE ao lado de cada zip.
# Cada arquivo ganha uma linha em baixados.json: endereço, data e hora, bytes, Last-Modified, sha256 (registro de fontes do T12).
# Para antes de passar de 1 GB no total (P11).
# Uso: python -I scripts/secoes_baixar.py dados/tse_secoes
import sys, os, json, time, hashlib, urllib.request, urllib.error
D = sys.argv[1]
BU = "https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_2t_{}_261020260742.zip"
UFS = "AC AL AM AP BA CE DF ES GO MA MG MS MT PA PB PE PI PR RJ RN RO RR RS SC SE SP TO ZZ".split()
ARQ = {
    "votacao_secao_2026_BR.zip": "https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_secao/votacao_secao_2026_BR.zip",
    "detalhe_votacao_secao_2026.zip": "https://cdn.tse.jus.br/estatistica/sead/odsele/detalhe_votacao_secao/detalhe_votacao_secao_2026.zip",
}
ARQ.update({f"bweb_2t_{uf}_261020260742.zip": BU.format(uf) for uf in UFS})
LIMITE = 10**9
PAUSA = 2.0
def log(*a): print(time.strftime("%H:%M:%S"), *a, flush=True)
def abre(url):
    espera = 10
    for tent in range(8):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=120)
        except urllib.error.HTTPError as e:
            if e.code == 404: raise
            log("HTTP", e.code, url, "nova tentativa em", espera, "s")
        except Exception as e:
            log("erro", e, url, "nova tentativa em", espera, "s")
        time.sleep(espera); espera = min(espera * 2, 120)
    raise RuntimeError("falhou: " + url)
def baixa(url, out):
    for tent in range(4):
        h256, h512, n = hashlib.sha256(), hashlib.sha512(), 0
        try:
            with abre(url) as r, open(out + ".parcial", "wb") as f:
                total, lm = int(r.headers["Content-Length"]), r.headers.get("Last-Modified")
                while True:
                    b = r.read(1 << 20)
                    if not b: break
                    f.write(b); h256.update(b); h512.update(b); n += len(b)
            if n != total: raise IOError(f"tamanho {n} diferente do Content-Length {total}")
            os.replace(out + ".parcial", out)
            return n, lm, h256.hexdigest(), h512.hexdigest()
        except Exception as e:
            log("erro no download", url, e); time.sleep(30)
    raise RuntimeError("falhou: " + url)
os.makedirs(D, exist_ok=True)
REG = os.path.join(D, "baixados.json")
reg = json.load(open(REG, encoding="utf-8")) if os.path.exists(REG) else {}
for nome, url in ARQ.items():
    out = os.path.join(D, nome)
    if nome in reg and os.path.exists(out): continue
    usado = sum(r["bytes"] for r in reg.values())
    with abre(url) as r: tam = int(r.headers["Content-Length"])
    if usado + tam > LIMITE: log("PARADO: passaria de 1 GB (P11)", usado, tam, nome); sys.exit(1)
    time.sleep(PAUSA)
    inicio = time.strftime("%d/%m/%Y %H:%M:%S")
    n, lm, s256, s512 = baixa(url, out)
    rec = {"url": url, "baixado_em": inicio, "bytes": n, "modificado": lm, "sha256": s256}
    if nome.startswith("bweb"):
        time.sleep(PAUSA)
        with abre(url + ".sha512") as r: pub = r.read().decode("ascii", "replace").split()[0].lower()
        if pub != s512: raise RuntimeError(f"sha512 não bate em {nome}: {pub} × {s512}")
        rec["sha512_tse"] = "confere"
    reg[nome] = rec
    json.dump(reg, open(REG, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    log(nome, n, "bytes", rec.get("sha512_tse", ""))
    time.sleep(PAUSA)
log("total na pasta:", sum(r["bytes"] for r in reg.values()), "bytes")
