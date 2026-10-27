# Confere a base do 2º turno (base2t.py) sem baixar nada e imprime o relatório em Markdown para as notas do T02.
# Uso: python confere2t.py [base_2t_municipios.json] [base_1t_municipios.json] [mun-e006258-cm.json]
import json, sys, os
sys.stdout.reconfigure(encoding="utf-8")  # o relatório tem acentos e "−", que o terminal do Windows não codifica
AQUI = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(AQUI, "..", "dados")
B2 = sys.argv[1] if len(sys.argv) > 1 else os.path.join(DADOS, "base_2t_municipios.json")
B1 = sys.argv[2] if len(sys.argv) > 2 else os.path.join(DADOS, "base_1t_municipios.json")
MUN = sys.argv[3] if len(sys.argv) > 3 else os.path.join(DADOS, "tse_config", "mun-e006258-cm.json")
OFICIAL = {"L": 64256232, "F": 59826041}
CAMPOS = ["te", "c", "vv", "L", "F", "vb", "tvn"]
d2, d1 = json.load(open(B2, encoding="utf-8")), json.load(open(B1, encoding="utf-8"))
mun = json.load(open(MUN, encoding="utf-8"))
def f(x): return f"{int(x):,}".replace(",", ".")
def fs(x): return ("+" if x > 0 else "−" if x < 0 else "") + f(abs(x))
def soma(rs, campos): return {k: sum(r[k] for r in rs) for k in campos}
ok = True
def linha(texto, certo):
    global ok
    ok &= certo; print(f"- {'OK' if certo else 'ERRO'}: {texto}")
lista = {m["cd"] for a in mun["abr"] for m in a["mu"]}
mu2, mu1 = d2["mu"], d1["mu"]
print("### Conferência do 2º turno\n")
linha(f"municípios na base: {f(len(mu2))} de {f(len(lista))} da lista do TSE; faltando {len(lista - set(mu2))}, sobrando {len(set(mu2) - lista)}", set(mu2) == lista)
linha(f"mesmos códigos do 1º turno: {f(len(set(mu2) & set(mu1)))} em comum, só no 1º {len(set(mu1) - set(mu2))}, só no 2º {len(set(mu2) - set(mu1))}", set(mu2) == set(mu1))
linha(f"cada município na mesma UF e com o mesmo nome do 1º turno: {sum(mu2[k]['uf'] != mu1[k]['uf'] or mu2[k]['nm'] != mu1[k]['nm'] for k in mu2.keys() & mu1.keys())} diferenças", all(mu2[k]["uf"] == mu1[k]["uf"] and mu2[k]["nm"] == mu1[k]["nm"] for k in mu2.keys() & mu1.keys()))
ext = sum(r["uf"] == "zz" for r in mu2.values())
print(f"- {f(len(mu2) - ext)} municípios no Brasil e {ext} no exterior")
divs = [u for u in d2["uf"] if soma([r for r in mu2.values() if r["uf"] == u], CAMPOS) != {k: d2["uf"][u][k] for k in CAMPOS}]
linha(f"soma dos municípios = arquivo de cada UF ({len(d2['uf'])} UFs, com o exterior), nos campos {', '.join(CAMPOS)}: {len(divs)} UFs divergem {divs}", not divs)
sm, su, br = soma(mu2.values(), CAMPOS), soma(d2["uf"].values(), CAMPOS), {k: d2["br"][k] for k in CAMPOS}
linha("soma dos municípios = soma das UFs = arquivo Brasil", sm == su == br)
linha(f"Brasil = oficial: Lula {f(br['L'])} (oficial {f(OFICIAL['L'])}), Flávio {f(br['F'])} (oficial {f(OFICIAL['F'])})", br["L"] == OFICIAL["L"] and br["F"] == OFICIAL["F"])
todos = list(mu2.values()) + list(d2["uf"].values()) + [d2["br"]]
linha(f"comparecimento − válidos = brancos + nulos (c − vv = vb + tvn) em todos os {f(len(todos))} registros: {sum(r['c'] - r['vv'] != r['vb'] + r['tvn'] for r in todos)} exceções", all(r["c"] - r["vv"] == r["vb"] + r["tvn"] for r in todos))
linha(f"válidos = Lula + Flávio (só dois candidatos) em todos os registros: {sum(r['vv'] != r['L'] + r['F'] for r in todos)} exceções", all(r["vv"] == r["L"] + r["F"] for r in todos))
print("\nTotais do Brasil no 2º turno: " + ", ".join(f"{k} {f(br[k])}" for k in CAMPOS) + ".")
print(f"\n**Resultado: {'tudo confere' if ok else 'há divergências'}.**\n")
# eleitorado: só registrar a diferença entre os turnos
b1, comuns = d1["br"], mu2.keys() & mu1.keys()
dif = {k: mu2[k]["te"] - mu1[k]["te"] for k in comuns}
print("### Eleitorado do 2º turno × 1º turno (só registro)\n")
print(f"- Brasil: 1º turno {f(b1['te'])}; 2º turno {f(br['te'])}; diferença {fs(br['te'] - b1['te']) or '0'}")
print(f"- municípios com eleitorado diferente: {f(sum(v != 0 for v in dif.values()))} de {f(len(comuns))} ({f(sum(v > 0 for v in dif.values()))} com mais eleitores no 2º turno, {f(sum(v < 0 for v in dif.values()))} com menos); soma das diferenças em módulo: {f(sum(abs(v) for v in dif.values()))}")
por_uf = {u: d2["uf"][u]["te"] - d1["uf"][u]["te"] for u in d2["uf"]}
print("- por UF (2º − 1º): " + ", ".join(f"{u.upper()} {fs(v)}" for u, v in sorted(por_uf.items()) if v) + (" (nenhuma)" if not any(por_uf.values()) else ""))
maiores = sorted(dif.items(), key=lambda kv: -abs(kv[1]))[:5]
print("- maiores diferenças: " + "; ".join(f"{mu2[k]['nm']}-{mu2[k]['uf'].upper()} {fs(v)}" for k, v in maiores if v))
print(f"- comparecimento: 1º turno {f(b1['c'])}; 2º turno {f(br['c'])}; diferença {fs(br['c'] - b1['c'])}")
sys.exit(0 if ok else 1)
