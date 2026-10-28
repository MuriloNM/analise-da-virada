/* Língua da página (T30; especificação 7.11, diário D42). Lê os catálogos de textos (textos/pt-BR.js,
   a origem, e o da língua da página, se não for o português) e dá aos outros scripts a função T, que
   devolve a frase de uma chave com os marcadores preenchidos. A língua é a do <html lang>, que cada
   página por língua traz (/, /en/…): a página não troca de língua sozinha.
   - T('chave', {n: '2,22'}): o texto, com {n} trocado pelo valor (já formatado por quem chama).
   - T.f('chave', {n: no}): o mesmo, em partes, para frases com números em destaque, links ou notas no
     meio (os valores podem ser elementos); entra direto no append. No catálogo, **assim** vira negrito
     (sem marcador dentro do negrito: um número em negrito vem pronto do código).
   - T.p('chave', n, {...}): a forma de plural de n na língua (Intl.PluralRules).
   - T.lista([...]): "a, b e c" na língua (Intl.ListFormat).
   Chave que falta na língua cai no português; chave que não existe em nenhum catálogo aparece como
   o próprio nome e vai para o console como erro, para ser achada na conferência.
   Também aqui: o botão de língua do menu do alto, que leva ao mesmo trecho na outra língua. A
   escolha não fica guardada: cada endereço abre na sua língua (pedido do autor, 27/10). */
(function () {
  'use strict';
  const ORIGEM = 'pt-BR';
  const LINGUAS = window.LINGUAS;
  const codigo = document.documentElement.lang || ORIGEM;
  const atual = LINGUAS.find(l => l.codigo === codigo) || LINGUAS[0];
  const BASE = window.TEXTOS[ORIGEM], CAT = window.TEXTOS[codigo] || BASE;
  const avisadas = new Set();

  function bruto(chave) {
    let v = CAT[chave];
    if (v === undefined) v = BASE[chave];
    if (v === undefined) {
      if (!avisadas.has(chave)) { avisadas.add(chave); console.error('Chave sem texto no catálogo: ' + chave); }
      return chave;
    }
    return v;
  }
  const texto = v => (typeof v === 'string' || Array.isArray(v) ? v : v.t);
  const preencher = (s, vals) => (vals ? s.replace(/\{(\w+)\}/g, (m, k) => (k in vals ? String(vals[k]) : m)) : s);
  /** O texto em partes: os marcadores viram os valores (texto ou elemento) e **assim** vira negrito. */
  function partes(s, vals) {
    const saida = [];
    const negrito = t => t.split(/\*\*(.+?)\*\*/).forEach((x, j) => {
      if (j % 2 === 0) { if (x) saida.push(x); return; }
      const b = document.createElement('b'); b.textContent = x; saida.push(b);
    });
    let i = 0;
    s.replace(/\{(\w+)\}/g, (m, k, pos) => {
      negrito(s.slice(i, pos));
      const v = vals && k in vals ? vals[k] : m;
      if (v !== '' && v !== null && v !== undefined) saida.push(typeof v === 'number' ? String(v) : v);
      i = pos + m.length;
      return m;
    });
    negrito(s.slice(i));
    return saida;
  }
  const plurais = {};
  function forma(chave, n, opcoes) {
    const v = bruto(chave);
    if (typeof v === 'string') return v;
    const k = JSON.stringify(opcoes || {});
    const pr = plurais[k] || (plurais[k] = new Intl.PluralRules(codigo, opcoes));
    const f = v[pr.select(Math.abs(n))];
    return f !== undefined ? f : v.other;
  }

  const T = (chave, vals) => preencher(texto(bruto(chave)), vals);
  T.f = (chave, vals) => partes(texto(bruto(chave)), vals);
  T.p = (chave, n, vals, opcoes) => preencher(forma(chave, n, opcoes), vals);
  T.fp = (chave, n, vals, opcoes) => partes(forma(chave, n, opcoes), vals);
  T.lista = a => (a.length < 2 ? a.join('') : new Intl.ListFormat(codigo, { type: 'conjunction' }).format(a.map(String)));
  T.tem = chave => chave in CAT || chave in BASE;
  /** Data por extenso na língua da página ("25 de outubro de 2026"), de uma data AAAA-MM-DD. */
  T.data = iso => new Intl.DateTimeFormat(codigo, { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' })
    .format(new Date(iso + 'T12:00:00Z'));
  T.lingua = codigo;
  T.linguas = LINGUAS;
  T.raiz = atual.pasta ? atual.pasta.replace(/[^/]+/g, '..') : ''; // o caminho de volta à raiz do estudo
  window.T = T;

  // ---------- Botão de língua ----------
  // Os links vêm prontos no HTML (scripts/linguas.py); aqui só levam o trecho atual (o #) e guardam a
  // escolha. A lista fecha com Esc (o foco volta ao botão) e ao clicar fora dela.
  document.querySelectorAll('details.linguas').forEach(d => {
    d.addEventListener('keydown', ev => {
      if (ev.key === 'Escape' && d.open) { d.open = false; d.querySelector('summary').focus(); }
    });
    document.addEventListener('click', ev => { if (d.open && !d.contains(ev.target)) d.open = false; });
    d.addEventListener('focusout', ev => { if (d.open && ev.relatedTarget && !d.contains(ev.relatedTarget)) d.open = false; });
  });
  document.querySelectorAll('[data-lingua]').forEach(a => {
    const leva = () => { a.href = a.getAttribute('href').replace(/#.*$/, '') + location.hash; };
    a.addEventListener('pointerdown', leva);
    a.addEventListener('focus', leva);
    a.addEventListener('click', leva);
  });
})();
