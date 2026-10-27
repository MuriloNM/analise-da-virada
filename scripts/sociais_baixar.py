# Baixa os dados sociais por município do T26 (lista curta do HIPOTESES.md, seção 6), como vieram da fonte.
# Uma consulta por vez, com pausa, e nova tentativa no 429. Arquivos já baixados são pulados.
# Cada arquivo ganha uma linha em baixados.json: endereço, data e hora, bytes e sha256 (registro de fontes do T12).
# Uso: python -I scripts/sociais_baixar.py dados/sociais_fontes
import sys, os, json, gzip, time, hashlib, urllib.request, urllib.error
D = sys.argv[1]
SIDRA = "https://apisidra.ibge.gov.br/values"
# nome do arquivo → endereço. Nas consultas do SIDRA, n1 é o Brasil (para conferir o total) e n6, os municípios.
ARQ = {
    # 1: população por idade (total e 60 anos ou mais), Censo 2022. Em duas consultas: o SIDRA recusa (erro 400) mais de 50 mil valores
    "sidra_9514_idade.json": SIDRA + "/t/9514/n1/all/n6/all/v/93/p/2022/c2/6794/c287/100362,93095,93096,93097,93098/c286/113635",
    "sidra_9514_idade_b.json": SIDRA + "/t/9514/n1/all/n6/all/v/93/p/2022/c2/6794/c287/49108,49109,60040,60041,6653/c286/113635",
    # 2: taxa de alfabetização, 15 anos ou mais, Censo 2022
    "sidra_9543_alfabetizacao.json": SIDRA + "/t/9543/n1/all/n6/all/v/2513/p/2022/c2/6794/c86/95251/c287/100362",
    # população de 15 anos ou mais, para conferir a taxa do Brasil pela média ponderada dos municípios
    "sidra_9514_15mais.json": SIDRA + "/t/9514/n1/all/n6/all/v/93/p/2022/c2/6794/c287/93070,93084,93085/c286/113635",
    # 5: população, área e densidade, Censo 2022
    "sidra_4714_densidade.json": SIDRA + "/t/4714/n1/all/n6/all/v/93,6318,614/p/2022",
    # 6: religião, pessoas de 10 anos ou mais, Censo 2022 (amostra)
    "sidra_9537_religiao.json": SIDRA + "/t/9537/n1/all/n6/all/v/140/p/2022/c133/95278,95277/c2/6794/c58/95253",
    # 7: cor ou raça, Censo 2022
    "sidra_9605_cor_raca.json": SIDRA + "/t/9605/n1/all/n6/all/v/93/p/2022/c86/95251,2777,2779",
    # reserva da 3, fora da lista curta: moradores por classe de rendimento domiciliar per capita, Censo 2022 (amostra)
    "sidra_10296_renda.json": SIDRA + "/t/10296/n1/all/n6/all/v/13604/p/2022/c2/6794/c86/95251/c386/9680,9681,9682,9692",
    # 4: PIB dos Municípios 2010-2023 (traz o PIB per capita publicado pelo IBGE)
    "pib_municipios_2010_2023_txt.zip": "https://ftp.ibge.gov.br/Pib_Municipios/2022_2023/base/base_de_dados_2010_2023_txt.zip",
    # PIB do Brasil em 2023 publicado no SIDRA (PIB dos Municípios), para conferir a soma dos municípios
    "sidra_5938_pib_brasil.json": SIDRA + "/t/5938/n1/all/v/37/p/2023",
}
PAUSA = 2.0
def log(*a): print(time.strftime("%H:%M:%S"), *a, flush=True)
def get(url):
    espera = 5
    for tent in range(6):
        try:
            req = urllib.request.Request(url, headers={"Accept-Encoding": "gzip", "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=300) as r:
                b = r.read()
                return gzip.decompress(b) if r.headers.get("Content-Encoding") == "gzip" else b
        except urllib.error.HTTPError as e:
            if e.code in (400, 404): raise
            log("HTTP", e.code, url, "nova tentativa em", espera, "s")
        except Exception as e:
            log("erro", e, url, "nova tentativa em", espera, "s")
        time.sleep(espera); espera *= 2
    raise RuntimeError("falhou: " + url)
os.makedirs(D, exist_ok=True)
REG = os.path.join(D, "baixados.json")
reg = json.load(open(REG, encoding="utf-8")) if os.path.exists(REG) else {}
for nome, url in ARQ.items():
    out = os.path.join(D, nome)
    if os.path.exists(out): continue
    inicio = time.strftime("%d/%m/%Y %H:%M:%S")
    b = get(url)
    if nome.endswith(".json"): json.loads(b)  # só grava se for JSON válido
    open(out, "wb").write(b)
    reg[nome] = {"url": url, "baixado_em": inicio, "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()}
    json.dump(reg, open(REG, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    log(nome, len(b), "bytes")
    time.sleep(PAUSA)
log("total na pasta:", sum(r["bytes"] for r in reg.values()), "bytes")
