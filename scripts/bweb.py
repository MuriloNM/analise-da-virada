# Baixa os boletins de urna do 1º turno por UF, guarda só presidente por seção: hora de chegada, aptos, Lula, Flávio, nominais.
import sys, os, io, json, zipfile, urllib.request, concurrent.futures as cf, time
D = sys.argv[1]  # pasta de trabalho (downloads e saídas)
UFS = sys.argv[2].split(",") if len(sys.argv) > 2 else "SP MG RJ BA RS PR PE CE PA SC GO MA AM PB ES PI RN MT AL MS DF SE RO TO AC AP RR ZZ".split()
URL = "https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_1t_{}_051020261403.zip"
def log(*a): print(time.strftime("%H:%M:%S"), *a, flush=True)
def one(uf):
    out = os.path.join(D, f"sec_{uf}.json")
    if os.path.exists(out): return uf, "já feito"
    zp = os.path.join(D, f"bweb_{uf}.zip")
    if not os.path.exists(zp + ".ok"):
        for tent in range(3):
            try:
                with urllib.request.urlopen(URL.format(uf), timeout=120) as r, open(zp, "wb") as f:
                    while True:
                        b = r.read(1 << 20)
                        if not b: break
                        f.write(b)
                open(zp + ".ok", "w").close(); break
            except Exception as e:
                log(uf, "erro no download", e); time.sleep(5)
        else: return uf, "falhou"
    log(uf, "baixado", os.path.getsize(zp) // 2**20, "MB")
    secs = {}
    z = zipfile.ZipFile(zp)
    name = [n for n in z.namelist() if n.lower().endswith(".csv")][0]
    with io.TextIOWrapper(z.open(name), encoding="latin-1") as f:
        f.readline()
        for line in f:
            if ';1;"Presidente";' not in line: continue
            p = line.split(";")
            k = (p[11], p[13], p[14])
            s = secs.get(k)
            if s is None:
                s = secs[k] = [p[21].strip('"'), int(p[22]), 0, 0, 0]
            if p[27] == "1":
                v = int(p[31]); s[4] += v
                if p[29] == "13": s[2] += v
                elif p[29] == "22": s[3] += v
    json.dump(list(secs.values()), open(out, "w"))
    z.close(); os.remove(zp); os.remove(zp + ".ok")
    return uf, f"{len(secs)} seções"
with cf.ThreadPoolExecutor(4) as ex:
    for uf, msg in ex.map(one, UFS): log(uf, msg)
log("FIM")
