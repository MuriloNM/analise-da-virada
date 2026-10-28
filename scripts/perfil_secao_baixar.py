"""T37 (I5b): baixa o perfil do eleitorado por seção de 2026 do TSE, um estado por vez.

28 arquivos (`perfil_eleitor_secao_2026_{UF}.zip`, com ZZ, o exterior), 2.818 MB no total,
aprovados pelo autor em 28/10/2026 (D88). Grava em `dados/tse_perfil_eleitor_secao/`, com
`baixados.json` (endereço, hora, bytes, data de modificação e sha256 de cada arquivo).
Arquivo já baixado com o mesmo tamanho não é baixado de novo. Rodar com `python -I`.
"""
import datetime
import hashlib
import json
import os
import time
import urllib.error
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA = os.path.join(RAIZ, "dados", "tse_perfil_eleitor_secao")
BASE = "https://cdn.tse.jus.br/estatistica/sead/odsele/perfil_eleitor_secao/perfil_eleitor_secao_2026_{}.zip"
UFS = ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA",
       "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO", "ZZ"]


def baixar(url, destino):
    for tentativa in range(6):
        try:
            with urllib.request.urlopen(url, timeout=120) as r, open(destino + ".parcial", "wb") as f:
                modificado = r.headers.get("Last-Modified")
                h = hashlib.sha256()
                while True:
                    bloco = r.read(1 << 20)
                    if not bloco:
                        break
                    h.update(bloco)
                    f.write(bloco)
            os.replace(destino + ".parcial", destino)
            return modificado, h.hexdigest()
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            time.sleep(10 * (tentativa + 1))
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            time.sleep(10 * (tentativa + 1))
    raise RuntimeError(f"falhou: {url}")


def main():
    os.makedirs(PASTA, exist_ok=True)
    registro_caminho = os.path.join(PASTA, "baixados.json")
    registro = {}
    if os.path.exists(registro_caminho):
        with open(registro_caminho, encoding="utf-8") as f:
            registro = json.load(f)
    for uf in UFS:
        url = BASE.format(uf)
        nome = os.path.basename(url)
        destino = os.path.join(PASTA, nome)
        if nome in registro and os.path.exists(destino) and os.path.getsize(destino) == registro[nome]["bytes"]:
            continue
        hora = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        modificado, sha = baixar(url, destino)
        registro[nome] = {"url": url, "hora": hora, "bytes": os.path.getsize(destino),
                          "modificado": modificado, "sha256": sha}
        with open(registro_caminho, "w", encoding="utf-8") as f:
            json.dump(registro, f, ensure_ascii=False, indent=1)
        print(f"{nome}: {registro[nome]['bytes']:,} bytes", flush=True)
    print("total:", f"{sum(v['bytes'] for v in registro.values()):,} bytes")


if __name__ == "__main__":
    main()
