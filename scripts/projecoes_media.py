# T41, Parte 3: média simples de (b), (c) e (d) e concordância dos três, a partir das saídas de projecoes_2t.py e projecoes_governador.py.
# Regras: ticket T41, "Regras da média dos métodos". Uso: python -I scripts/projecoes_media.py
import os, csv, json
AQUI = os.path.dirname(os.path.abspath(__file__)); DADOS = os.path.join(AQUI, "..", "dados")
SAI = os.path.join(DADOS, "projecoes_outras")

def avalia(L, final):
    lado = (lambda v: v > 50) if final > 50 else (lambda v: v < 50)
    out = {}
    for m in ("a", "b", "c", "d", "m"):
        e = [abs(d[m] - final) for d in L]
        ac = [lado(d[m]) and abs(d[m] - final) <= 0.5 for d in L]; k = next((i for i in range(len(L)) if all(ac[i:])), None)
        out[m] = dict(abs_medio=round(sum(e) / len(e), 3), max_abs=round(max(e), 3), passa_a_acertar=None if k is None else L[k]["pst"])
    conc = [len({d[m] > 50 for m in "bcd"}) == 1 for d in L]
    k = next((i for i in range(len(L)) if all(conc[i:])), None)
    out["concordam"] = dict(instantes=f"{sum(conc)} de {len(L)}", desde=None if k is None else L[k]["pst"],
                            concordando_e_errando_o_vencedor=sum(c and not lado(d["b"]) for c, d in zip(conc, L)))
    return out

def main():
    f = lambda v: float(v)
    res = {}
    P = list(csv.DictReader(open(os.path.join(DADOS, "projecoes_2t", "instantes.csv"), encoding="utf-8"), delimiter=";"))
    for conj in ("principal", "fino"):
        L = [dict(pst=f(r["pst"]), **{m: f(r[m]) for m in "abcd"}) for r in P if r["conjunto"] == conj]
        for d in L: d["m"] = (d["b"] + d["c"] + d["d"]) / 3
        res[f"presidente_2026_{conj}"] = avalia(L, 51.785)
    G = list(csv.DictReader(open(os.path.join(SAI, "governador_2026_instantes.csv"), encoding="utf-8"), delimiter=";"))
    for disp in sorted({r["disputa"] for r in G}):
        L = [dict(pst=f(r["pst"]), **{m: f(r[m]) for m in "abcd"}) for r in G if r["disputa"] == disp]
        final = f(next(r["final"] for r in G if r["disputa"] == disp))
        for d in L: d["m"] = (d["b"] + d["c"] + d["d"]) / 3
        res[disp] = avalia(L, final)
    json.dump(res, open(os.path.join(SAI, "media_resumo.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for k, v in res.items():
        print(k, {m: (v[m]["abs_medio"], v[m]["passa_a_acertar"]) for m in "abcdm"}, v["concordam"])

if __name__ == "__main__":
    main()
