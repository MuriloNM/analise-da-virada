# Reconstrói a apuração do 1º turno: ordena as seções pela hora de chegada do boletim e acumula.
# x = % do eleitorado em seções já recebidas (equivale ao % de seções apuradas); y = % de Lula entre Lula e Flávio.
import json, glob, os, sys
B, base = sys.argv[1], sys.argv[2]
secs = []
for f in sorted(glob.glob(os.path.join(B, "sec_*.json"))): secs += json.load(open(f))
secs.sort(key=lambda s: s[0])
T = sum(s[1] for s in secs); L = F = A = 0; out = []; nxt = 0.1
for dt, apt, l, f, nom in secs:
    A += apt; L += l; F += f
    x = A / T * 100
    if (x >= nxt or A == T) and L + F > 0:
        out.append([round(x, 2), round(L / (L + F) * 100, 3), dt[11:16]])
        nxt = x + (0.1 if x < 5 else 0.25)
print("seções", len(secs), "aptos", T, "Lula", L, "Flávio", F, "pontos", len(out))
for q in out[::max(1, len(out) // 12)]: print(q)
b = json.load(open(base, encoding="utf-8")); b["t1c"] = out
json.dump(b, open(base, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
