# Baixa o resultado oficial por estado dos cargos estaduais do 1º turno (eleição 6259), para conferir o T04.
# Uma consulta por vez, com pausa, e nova tentativa no 429. Arquivos já baixados são pulados.
# Uso: python -I scripts/tse6259_uf.py dados/tse_6259_uf [dados/tse_config/mun-e006258-cm.json]
import sys, os, json, gzip, time, urllib.request, urllib.error
D = sys.argv[1]
MUN = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), "..", "dados", "tse_config", "mun-e006258-cm.json")
URL = "https://resultados.tse.jus.br/oficial/ele2026/6259/dados/{u}/{u}-c{c:04d}-e006259-u.json"
PAUSA = 1.0
def log(*a): print(time.strftime("%H:%M:%S"), *a, flush=True)
def get(url):
    espera = 5
    for tent in range(6):
        try:
            req = urllib.request.Request(url, headers={"Accept-Encoding": "gzip", "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                b = r.read()
                return gzip.decompress(b) if r.headers.get("Content-Encoding") == "gzip" else b
        except urllib.error.HTTPError as e:
            if e.code == 404: raise
            log("HTTP", e.code, url, "nova tentativa em", espera, "s")
        except Exception as e:
            log("erro", e, url, "nova tentativa em", espera, "s")
        time.sleep(espera); espera *= 2
    raise RuntimeError("falhou: " + url)
ufs = [a["cd"] for a in json.load(open(MUN, encoding="utf-8"))["abr"] if a["cd"] != "zz"]
os.makedirs(D, exist_ok=True)
n = 0
for u in ufs:
    # 3 governador, 5 senador, 6 deputado federal, 7 deputado estadual; no DF, 8 deputado distrital
    for c in (3, 5, 6, 8) if u == "df" else (3, 5, 6, 7):
        out = os.path.join(D, f"{u}-c{c:04d}-e006259-u.json")
        if os.path.exists(out): continue
        b = get(URL.format(u=u, c=c))
        json.loads(b)  # só grava se for JSON válido
        open(out, "wb").write(b); n += 1
        time.sleep(PAUSA)
log("baixados", n, "arquivos;", len(os.listdir(D)), "na pasta")
