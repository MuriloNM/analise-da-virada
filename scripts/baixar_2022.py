# T41, Parte 3: baixa do TSE os arquivos de 2022 do teste limpo (2º turno com hora de recebimento, detalhe por seção e
# 1º turno de governador nas 12 UFs com 2º turno). Devagar, com nova tentativa. Grava dados/tse_2022/baixados.json.
# Uso: python -I scripts/baixar_2022.py
import os, json, time, hashlib, datetime, urllib.request
AQUI = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(AQUI, "..", "dados", "tse_2022")
UFS_GOV = ["AL", "AM", "BA", "ES", "MS", "PB", "PE", "RO", "RS", "SC", "SE", "SP"]
TODAS = ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO", "ZZ"]
CDN = "https://cdn.tse.jus.br/estatistica/sead"
urls = [f"{CDN}/eleicoes/eleicoes2022/buweb/bweb_2t_{uf}_311020221535.zip" for uf in TODAS]
urls += [f"{CDN}/odsele/detalhe_votacao_secao/detalhe_votacao_secao_2022.zip"]
urls += [f"{CDN}/odsele/votacao_secao/votacao_secao_2022_{uf}.zip" for uf in UFS_GOV]
os.makedirs(D, exist_ok=True)
reg_p = os.path.join(D, "baixados.json"); reg = json.load(open(reg_p)) if os.path.exists(reg_p) else {}
for u in urls:
    nome = u.rsplit("/", 1)[1]; p = os.path.join(D, nome)
    if nome in reg and os.path.exists(p) and os.path.getsize(p) == reg[nome]["bytes"]: continue
    for k in range(5):
        try:
            r = urllib.request.urlopen(u, timeout=600); h = hashlib.sha256(); n = 0
            with open(p, "wb") as f:
                while True:
                    b = r.read(1 << 20)
                    if not b: break
                    f.write(b); h.update(b); n += len(b)
            break
        except Exception as e:
            print(nome, "erro", e); time.sleep(10 * (k + 1))
    reg[nome] = dict(url=u, baixado_em=datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), bytes=n, modificado=r.headers.get("Last-Modified"), sha256=h.hexdigest())
    json.dump(reg, open(reg_p, "w"), indent=1); print(nome, n, flush=True); time.sleep(1)
