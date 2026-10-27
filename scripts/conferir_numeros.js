/* Confere que nenhum número muda de valor com a língua da página (T30; diário D25 e D42).

    node scripts/conferir_numeros.js [língua…]

Carrega os catálogos (site-analise/textos/), lingua.js e graficos.js num ambiente sem navegador,
uma vez em português e uma vez em cada outra língua (as de textos/linguas.js, ou as pedidas), e
formata com o próprio fmt da página a mesma amostra de 50 números dos dados (dados.js): inteiros,
inteiros com sinal, porcentagens, pontos percentuais, milhões e valores-p, cada um com as casas que
a página usa. Depois lê cada texto de volta com o separador decimal e de milhar da língua e confere
que o valor é o mesmo nas duas línguas (e o mesmo que o número arredondado uma vez, D25). Mostra a
amostra lado a lado e sai com erro se algum número mudar.
*/
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const SITE = path.join(__dirname, '..', 'site-analise');
const ler = f => fs.readFileSync(path.join(SITE, f), 'utf8');

function pagina(lingua) {
  // o mínimo de navegador que lingua.js e graficos.js usam ao carregar
  const nada = () => {};
  const ctx = { console, Intl, Math, JSON, Object, Array, String, Number, Set, Map, Promise, setTimeout };
  ctx.window = ctx;
  ctx.document = { documentElement: { lang: lingua }, querySelectorAll: () => [], addEventListener: nada, body: {} };
  ctx.addEventListener = nada;
  ctx.getComputedStyle = () => ({ getPropertyValue: () => '' });
  vm.createContext(ctx);
  const arquivos = ['textos/linguas.js', 'textos/pt-BR.js'];
  if (lingua !== 'pt-BR') arquivos.push(`textos/${lingua}.js`);
  for (const f of arquivos.concat(['lingua.js', 'graficos.js', 'dados.js'])) vm.runInContext(ler(f), ctx, { filename: f });
  return ctx;
}

// A amostra: 50 valores dos dados, com o formato e as casas com que a página os mostra
function amostra(D) {
  const ufs = D.ufs.filter(u => u.codigo !== 'ZZ');
  const s = u => 100 * u.L2 / (u.L2 + u.F2), s1 = u => 100 * u.L1 / (u.L1 + u.F1);
  const a = [];
  const H = D.hipoteses.H1.versoes[0];
  for (const u of ufs.slice(0, 8)) {
    a.push(['int', u.L2], ['intSinal', u.L2 - u.L1], ['pct', s(u), 2], ['pp', s(u) - s1(u)]);
  }
  for (const r of D.regioes) a.push(['mi', (r.L2 - r.F2) - (r.L1 - r.F1)]);
  a.push(['miAbs', D.brasil.L2 - D.brasil.F2], ['miAbs', D.brasil.F1 - D.brasil.L1], ['dec', H.coef * 10, 2], ['decSinal', H.ic95[0] * 10, 2],
    ['decSinal', H.ic95[1] * 10, 2], ['p', H.p_selvagem], ['p', D.hipoteses.H3.versoes[0].p_selvagem], ['pct', 51.785, 3],
    ['pct', 99.77, 2], ['dec', 0.05, 2], ['dec', 4.49, 2], ['pct', 0.5, 1]);
  return a.slice(0, 50);
}

// lê de volta o texto formatado: tira a unidade, o separador de milhar e põe o ponto decimal
function valor(texto, lingua) {
  const partes = new Intl.NumberFormat(lingua).formatToParts(12345.6);
  const milhar = (partes.find(p => p.type === 'group') || {}).value || '';
  const decimal = partes.find(p => p.type === 'decimal').value;
  let t = texto.replace(/−/g, '-').replace(/[^\d\-+.,   ]/g, '').trim();
  t = t.split(milhar).join('').split(decimal).join('.').replace(/[   ]/g, '');
  return Number(t);
}

const pt = pagina('pt-BR');
const linguas = process.argv.slice(2).length ? process.argv.slice(2) : pt.LINGUAS.map(l => l.codigo).filter(c => c !== 'pt-BR');
const A = amostra(pt.ESTUDO);
let erros = 0;
for (const lingua of linguas) {
  const ot = pagina(lingua);
  console.log(`\nAmostra de ${A.length} números: pt-BR × ${lingua}`);
  A.forEach(([f, v, c], i) => {
    const escala = f === 'mi' || f === 'miAbs' ? 1e6 : 1;
    const a = c === undefined ? pt.GRAFICOS.fmt[f](v) : pt.GRAFICOS.fmt[f](v, c);
    const b = c === undefined ? ot.GRAFICOS.fmt[f](v) : ot.GRAFICOS.fmt[f](v, c);
    const va = valor(a, 'pt-BR'), vb = valor(b, lingua);
    const ok = va === vb && !Number.isNaN(va);
    if (!ok) erros++;
    console.log(`${String(i + 1).padStart(2)} ${f.padEnd(8)} ${a.padEnd(22)} ${b.padEnd(22)} ${ok ? 'igual' : 'DIFERENTE'}${escala > 1 ? ' (milhões)' : ''}`);
  });
}
if (erros) { console.error(`\nFALHOU: ${erros} número(s) mudaram de valor com a língua.`); process.exit(1); }
console.log('\nResultado: os mesmos números em todas as línguas; só muda o jeito de escrever.');
