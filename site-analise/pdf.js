/* O estudo em PDF e a impressão (T17; especificação 7.8). Carregado por último, depois de todos os
   outros scripts da página.
   1. O botão "Baixar o estudo em PDF", no Resumo e em Método e fontes: o PDF da língua da página
      (P25), com a versão, as páginas e o tamanho, que vêm de pdf/arquivos.js (scripts/pdf.py). Sem o
      arquivo gravado, o botão não aparece.
   2. A impressão (Ctrl+P) sai limpa pelo @media print de estudo.css; aqui só marcam-se os links
      externos cujo texto já é o endereço, para o endereço não sair duas vezes.
   3. O modo PDF (endereço com ?pdf), que o scripts/pdf.py abre no Chrome sem janela para gravar o
      PDF: a página inteira de leitura (Resumo, os 9 capítulos com os detalhes abertos e as notas) e
      Método e fontes, com capa, sumário e, no fim, o contato do autor. Explorar e Apuração ao vivo
      ficam só na página, com o endereço no sumário. Os links internos levam ao trecho dentro do PDF;
      os que vão para o que ficou só na página levam ao endereço publicado. O sumário recebe os
      números das páginas do scripts/pdf.py, que grava o PDF duas vezes (PDF_SUMARIO, abaixo).
   Os textos vêm do catálogo da língua da página (chaves "pdf."; T30). */
(function () {
  'use strict';
  const T = window.T;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  function el(tag, cls, texto, pai) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (texto !== undefined) e.textContent = texto;
    if (pai) pai.appendChild(e);
    return e;
  }
  const LINGUA = T.linguas.find(l => l.codigo === T.lingua);
  const ENDERECO = 'https://analise-da-virada.pages.dev/' + LINGUA.pasta; // o endereço publicado (P19)
  const V = window.ESTUDO_VERSAO;
  const AUTOR = { nome: 'Murilo Neves de Martins', linkedin: 'https://www.linkedin.com/in/murilomartins/' };
  // O e-mail do autor sai só no PDF, escrito com "(arroba)" e sem link, contra os robôs que colhem endereços
  // (P08); aqui fica em duas partes, para o código da página também não mostrar um endereço inteiro.
  const EMAIL = ['murilomartins', 'gmail.com'];
  const tamanho = b => (b >= 1048576 ? T('ext.mb', { n: (b / 1048576).toLocaleString(T.lingua, { maximumFractionDigits: 1 }) })
    : T('ext.kb', { n: Math.max(1, Math.round(b / 1024)).toLocaleString(T.lingua) }));

  // ---------- 1. Baixar o estudo em PDF ----------
  const ARQ = (window.PDF_ESTUDO || {})[T.lingua];
  for (const caixa of $$('[data-pdf-baixar]')) {
    if (!ARQ) { caixa.hidden = true; continue; }
    const a = el('a', 'pdf-link', T('pdf.baixar'), caixa);
    a.href = T.raiz + 'pdf/' + ARQ.arquivo;
    a.setAttribute('download', '');
    a.type = 'application/pdf';
    el('span', 'pdf-meta', T('pdf.baixar_meta', { versao: ARQ.versao, paginas: ARQ.paginas.toLocaleString(T.lingua), tamanho: tamanho(ARQ.bytes) }), caixa);
  }
  // A impressão digital (SHA-256) de cada PDF desta versão, em "Versão e correções" (extras.js, #pdf-sha),
  // para quem recebeu uma cópia conferir se ela é igual à original. Fica fora do próprio PDF: ele não
  // pode trazer a impressão digital de si mesmo.
  const shaCaixa = $('#pdf-sha');
  const comSha = Object.values(window.PDF_ESTUDO || {}).filter(a => a.sha256 && a.versao === V.numero);
  if (shaCaixa && comSha.length && !new URLSearchParams(location.search).has('pdf')) {
    const cmd = t => el('code', '', t);
    el('p', '', undefined, shaCaixa).append(...T.f('ext.sha', { win: cmd(T('ext.sha.win')), mac: cmd(T('ext.sha.mac')) }));
    const dl = el('dl', 'sha', undefined, shaCaixa);
    dl.setAttribute('aria-label', T('ext.sha.aria'));
    for (const a of comSha) {
      const linha = el('div', 'sha-linha', undefined, dl);
      el('dt', '', a.arquivo, linha);
      el('dd', '', a.sha256, linha);
    }
  }

  // ---------- 2. Impressão: o endereço dos links externos ----------
  // O endereço sai depois do link (estudo.css, @media print), menos quando o próprio texto já é o endereço.
  const semEsquema = u => u.replace(/^https?:\/\//, '').replace(/\/$/, '');
  function marcarLinks() {
    for (const a of $$('a[href^="http"]')) {
      // o texto do link sem o aviso só para leitor de tela (externos.js)
      const t = Array.from(a.childNodes).filter(n => !(n.classList && n.classList.contains('sr'))).map(n => n.textContent).join('').trim();
      if (!t || semEsquema(t) === semEsquema(a.href) || /^(https?:\/\/|www\.|doi:)/.test(t)) a.classList.add('sem-url');
    }
  }
  addEventListener('beforeprint', marcarLinks);

  if (!new URLSearchParams(location.search).has('pdf')) return;

  // ---------- 3. Modo PDF ----------
  const html = document.documentElement;
  html.classList.add('modo-pdf');
  html.setAttribute('data-tema', 'claro'); // o PDF é sempre no papel claro
  // o rodapé de cada página (estudo.css, @page): à esquerda, o nome do estudo, a versão e a data; à
  // direita, o endereço e o número da página, para uma página solta dizer de que versão é e onde está a mais nova
  html.style.setProperty('--pdf-rodape', JSON.stringify(T('pdf.rodape', { nome: T('pag.nome'), versao: V.numero, data: T.data(V.data) })));
  html.style.setProperty('--pdf-rodape-end', JSON.stringify(ENDERECO.replace(/^https:\/\//, '').replace(/\/$/, '')));
  const main = $('#conteudo');

  // a leitura e Método e fontes à vista; Explorar e Apuração ao vivo, não
  for (const v of $$('.vista')) v.hidden = !['leitura', 'metodo'].includes(v.dataset.vista);
  // os detalhes abertos (com as tabelas de todas as versões) e as duas figuras de cada escolha
  for (const d of $$('details.detalhes, details.det-aninhado')) d.open = true; // também as notas recolhidas
  for (const p of $$('.fig-painel')) p.hidden = false;
  for (const r of $$('.capitulo details.detalhes > summary .det-rot')) r.textContent = T('pdf.detalhes');

  // links internos: o trecho dentro do PDF, ou o endereço publicado para o que fica só na página
  for (const a of $$('a[href^="#"]')) {
    const [x, y] = decodeURIComponent(a.getAttribute('href').slice(1)).split('/');
    let alvo = null;
    if (x === 'analise') alvo = 'capitulo-' + (parseInt(y, 10) || 1);
    else if (x === 'metodo') alvo = y || 'metodo';
    else if (x !== 'explorar' && x !== 'apuracao' && x !== 'comentarios') alvo = x || 'resumo';
    const e = alvo && document.getElementById(alvo), vista = e && e.closest('[data-vista]');
    if (e && (!vista || !vista.hidden)) a.setAttribute('href', '#' + alvo);
    else a.setAttribute('href', ENDERECO + a.getAttribute('href'));
  }
  // os arquivos do estudo (CSV, privacidade…): o endereço publicado, e não o do computador que gravou o PDF
  for (const a of $$('a[href]')) {
    if (a.getAttribute('href').startsWith('#')) continue;
    const u = new URL(a.href);
    if (u.origin === location.origin) a.href = 'https://analise-da-virada.pages.dev' + u.pathname + u.hash;
  }

  // ----- Capa -----
  const capa = el('section', 'pdf-capa');
  main.prepend(capa);
  const topo = el('div', 'pdf-capa-topo', undefined, capa);
  el('p', 'pdf-capa-nome', T('pag.nome'), topo);
  el('p', 'pdf-capa-sub', T('ext.subtitulo'), topo);
  el('h1', 'pdf-capa-pergunta', T('prev.pergunta_capa'), capa);
  const fig = el('figure', 'pdf-capa-fig', undefined, capa);
  const svg = $('#grafico-virada svg');
  if (svg) el('div', 'grafico', undefined, fig).appendChild(svg.cloneNode(true)); // .grafico: os estilos das marcas
  el('figcaption', '', T('res.fig_rodape'), fig);
  const pe = el('div', 'pdf-capa-pe', undefined, capa);
  el('p', 'pdf-capa-autor', AUTOR.nome, pe);
  el('p', '', T('ext.versao', { versao: T('ext.versao.n', { n: V.numero }), data: T.data(V.data), situacao: V.situacao }), pe);
  el('p', 'pdf-capa-end', ENDERECO.replace(/^https:\/\//, ''), pe);

  // ----- Sumário -----
  const sum = el('nav', 'pdf-sumario');
  capa.after(sum);
  el('h2', '', T('pdf.sumario'), sum);
  const ol = el('ol', '', undefined, sum);
  const entradas = [];
  function entrada(id, texto, { n = '', sub = false } = {}) {
    const alvo = document.getElementById(id);
    if (!alvo) return;
    const li = el('li', sub ? 'sub' : '', undefined, ol);
    const a = el('a', '', undefined, li);
    a.href = '#' + id;
    el('span', 'pdf-sum-n', n, a);
    el('span', 'pdf-sum-t', texto, a);
    el('span', 'pdf-sum-pag', '00', a).dataset.alvo = id;
    entradas.push(id);
  }
  entrada('resumo', T('nav.resumo'));
  $$('.capitulo').forEach((c, i) => entrada(c.id, T(`c${i + 1}.pergunta`), { n: String(i + 1) }));
  entrada('notas', T('notas.tit'));
  entrada('metodo', T('nav.metodo'));
  for (const s of $$('#metodo .met-parte')) entrada(s.id, $('h2', s).textContent, { sub: true });
  const fim = el('section', 'pdf-fim');
  fim.id = 'pdf-contato';
  main.append(fim);
  const so = el('p', 'pdf-so-pagina', undefined, sum);
  const ligar = (href, texto) => { const a = el('a', '', texto); a.href = ENDERECO + href; return a; };
  so.append(...T.f('pdf.so_na_pagina', { explorar: ligar('#explorar', T('nav.explorar')), apuracao: ligar('#apuracao', T('nav.apuracao')) }));

  // ----- Última página: o contato do autor -----
  el('h2', '', T('pdf.contato.tit'), fim);
  el('p', 'pdf-fim-txt', undefined, fim).append(...T.f('pdf.contato.txt', { nome: el('b', '', AUTOR.nome) }));
  const dl = el('dl', 'pdf-fim-lista', undefined, fim);
  const item = (rotulo, href) => {
    el('dt', '', rotulo, dl);
    const a = el('a', 'sem-url', href.replace(/^https:\/\//, ''), el('dd', '', undefined, dl));
    a.href = href;
  };
  el('dt', '', T('pdf.contato.email'), dl);
  el('dd', 'pdf-fim-email', T('pdf.contato.email_fmt', { usuario: EMAIL[0], dominio: EMAIL[1] }), dl);
  item(T('pdf.contato.linkedin'), AUTOR.linkedin);
  item(T('pdf.contato.estudo'), ENDERECO);
  item(T('met.sobre.tit'), ENDERECO + '#metodo/sobre');
  item(T('met.dados.tit'), ENDERECO + '#metodo/dados');
  el('h3', '', T('pdf.contato.versao_tit'), fim);
  el('p', 'pdf-fim-txt', T('pdf.contato.versao', { versao: V.numero, data: T.data(V.data) }), fim);
  const desta = (V.correcoes || []).filter(c => c.versao === V.numero);
  if (!desta.length) el('p', 'pdf-fim-txt', T('pdf.contato.sem_mudanca'), fim);
  else {
    el('p', 'pdf-fim-txt', T('pdf.contato.mudou'), fim);
    const ul = el('ul', 'pdf-fim-mudou', undefined, fim);
    for (const c of desta) el('li', '', T(c.oQue), ul);
  }
  entrada('pdf-contato', T('pdf.contato.tit'));

  // ----- Marcas para o scripts/pdf.py achar a página de cada entrada do sumário -----
  // Na primeira gravação, o título de cada trecho vira um link para um endereço inventado, que o
  // script procura no PDF; o texto e o tamanho não mudam. Depois, PDF_SUMARIO(paginas) põe os números
  // no sumário e tira as marcas.
  const titulo = id => { const a = document.getElementById(id); return a && (a.matches('h1, h2') ? a : $('h1, h2', a)); };
  for (const id of entradas) {
    const h = titulo(id);
    if (!h) continue;
    const m = document.createElement('a');
    m.className = 'pdf-marca';
    m.href = 'https://marca.invalid/' + id;
    m.append(...h.childNodes);
    h.append(m);
  }
  window.PDF_SUMARIO = paginas => {
    for (const s of $$('.pdf-sum-pag')) s.textContent = paginas[s.dataset.alvo] ? String(paginas[s.dataset.alvo]) : '';
    for (const m of $$('.pdf-marca')) m.replaceWith(...m.childNodes);
  };
  window.PDF_ENTRADAS = entradas;
  window.PDF_ARQUIVO = `${T('pdf.arquivo')}-v${V.numero}.pdf`;

  marcarLinks();
  // pronto quando as fontes carregaram e os gráficos (que medem o texto) foram desenhados de novo
  (document.fonts ? document.fonts.ready : Promise.resolve()).then(() =>
    requestAnimationFrame(() => requestAnimationFrame(() => setTimeout(() => { window.PDF_PRONTO = true; }, 300))));
})();
