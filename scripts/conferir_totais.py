# Confere se os arquivos baixados estão completos: a soma das colunas bate com os totais oficiais do TSE
# (README, "Totais para conferir") e a impressão digital de cada arquivo bate com SHA256SUMS.txt.
# Só a biblioteca padrão. Uso, da pasta raiz do repositório: python scripts/conferir_totais.py
import csv, gzip, hashlib, os, sys
sys.stdout.reconfigure(encoding="utf-8")
RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
TOTAIS = {  # Brasil e exterior, resultado oficial do TSE
    "eleitorado_1t": 158745502, "comparecimento_1t": 125275835, "validos_1t": 119300788,
    "lula_1t": 53879538, "flavio_1t": 56104503,
    "eleitorado_2t": 158745502, "comparecimento_2t": 128236074, "validos_2t": 124082273,
    "lula_2t": 64256232, "flavio_2t": 59826041,
}
EN = {"eleitorado_1t": "electorate_r1", "comparecimento_1t": "turnout_r1", "validos_1t": "valid_votes_r1", "lula_1t": "lula_r1",
      "flavio_1t": "flavio_r1", "eleitorado_2t": "electorate_r2", "comparecimento_2t": "turnout_r2", "validos_2t": "valid_votes_r2",
      "lula_2t": "lula_r2", "flavio_2t": "flavio_r2"}
SECOES = {"t2_13": 64256232, "t2_22": 59826041, "t1_13": 53879538, "t1_22": 56104503}
erros = []


def confere(cond, msg):
    print(("ok   " if cond else "ERRO ") + msg)
    if not cond:
        erros.append(msg)


def soma(caminho, sep, colunas):
    with open(caminho, encoding="utf-8-sig", newline="") as f:
        linhas = list(csv.DictReader(f, delimiter=sep))
    return len(linhas), {c: sum(int(l[c]) for l in linhas if l[c] != "") for c in colunas}


for rotulo, caminho, sep, nomes in [
    ("dados/analise_municipios.csv", "dados/analise_municipios.csv", ",", {c: c for c in TOTAIS}),
    ("planilha/pt-BR/municipios.csv", "planilha/pt-BR/municipios.csv", ";", {c: c for c in TOTAIS}),
    ("planilha/en/municipios.csv", "planilha/en/municipios.csv", ",", EN),
]:
    n, s = soma(os.path.join(RAIZ, caminho), sep, nomes.values())
    confere(n == 5757, f"{rotulo}: {n} municípios (5.757)")
    for c, total in TOTAIS.items():
        confere(s[nomes[c]] == total, f"{rotulo}: soma de {nomes[c]} = {s[nomes[c]]:,} (oficial {total:,})".replace(",", "."))

with gzip.open(os.path.join(RAIZ, "dados", "secoes_presidente.csv.gz"), "rt", encoding="utf-8", newline="") as f:
    r = csv.DictReader(f)
    n, s = 0, dict.fromkeys(SECOES, 0)
    for l in r:
        n += 1
        for c in SECOES:
            s[c] += int(l[c] or 0)
confere(n == 499248, f"dados/secoes_presidente.csv.gz: {n:,} seções (499.248)".replace(",", "."))
for c, total in SECOES.items():
    confere(s[c] == total, f"dados/secoes_presidente.csv.gz: soma de {c} = {s[c]:,} (oficial {total:,})".replace(",", "."))

lista = os.path.join(RAIZ, "SHA256SUMS.txt")
ruins = 0
with open(lista, encoding="utf-8") as f:
    itens = [l.rstrip("\n").split("  ", 1) for l in f if l.strip()]
for h, nome in itens:
    p = os.path.join(RAIZ, nome)
    if not os.path.exists(p):
        ruins += 1; print(f"ERRO falta {nome}"); continue
    d = hashlib.sha256()
    with open(p, "rb") as g:
        for b in iter(lambda: g.read(1 << 20), b""):
            d.update(b)
    if d.hexdigest() != h:
        ruins += 1; print(f"ERRO impressão digital diferente: {nome}")
confere(ruins == 0, f"SHA256SUMS.txt: {len(itens) - ruins} de {len(itens)} arquivos iguais aos originais")

print("\nTudo confere." if not erros else f"\n{len(erros)} conferência(s) com erro.")
sys.exit(1 if erros else 0)
