# T41, Parte 3: baixa do TSE o 1º e o 2º turno por seção de 2024 (prefeito) nas 20 UFs com prefeito no 2º turno.
# A ordem de chegada vem do detalhe_votacao_secao_2024.zip (já baixado). Grava dados/tse_2024/baixados.json.
# Uso: python -I scripts/baixar_2024.py
import os, json, time, hashlib, datetime, urllib.request
AQUI = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(AQUI, "..", "dados", "tse_2024")
UFS_GOV = ["AM", "BA", "CE", "ES", "GO", "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PR", "RJ", "RN", "RO", "RS", "SE", "SP", "TO"]
CDN = "https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_secao"
urls = [f"{CDN}/votacao_secao_2024_{uf}.zip" for uf in UFS_GOV]
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
