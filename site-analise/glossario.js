/* Glossário do estudo (T25; especificação 7.3 e 7.5). Uma lista só de termos, que alimenta o
   mini-glossário da leitura (o termo sublinhado em pontinhos mostra a definição ao passar o mouse,
   tocar ou chegar pelo teclado) e o glossário completo de Método e fontes, para os dois nunca
   divergirem. O T12 usa a mesma lista (window.GLOSSARIO). Carregado depois de estudo.js, que monta
   a página: aqui só se marcam termos no texto que já existe, sem mudar nenhuma frase.
   Cada termo: chave (o endereço #metodo/glossario-chave, igual em toda língua), se é palavra de
   todo dia (comum) e as notas sobre os dados ligadas a ele; o nome, a definição e os jeitos de achar
   o termo no texto (o mais longo ganha) vêm do catálogo da língua da página (textos/pt-BR.js, chaves
   "glos."; T30). As definições são rascunho: a redação final é do T11 e do T12 (diário, D23). */
(function () {
  'use strict';
  const T = window.T;
  const TERMOS = [
    { chave: 'abstencao', comum: true },
    { chave: 'bootstrap' },
    { chave: 'brancos-e-nulos', comum: true, notas: ['N07'] },
    { chave: 'campo-da-esquerda', notas: ['N10', 'N11'] },
    { chave: 'captura', notas: ['N09'] },
    { chave: 'comparecimento', comum: true },
    { chave: 'conferencias' },
    { chave: 'classificacao' },
    { chave: 'dentro-dos-estados' },
    { chave: 'diferenca', comum: true },
    { chave: 'efeito-interquartil' },
    { chave: 'eleitorado', comum: true, notas: ['N05'] },
    { chave: 'escala', notas: ['N10', 'N12'] },
    { chave: 'espelho' },
    { chave: 'fatia', comum: true },
    { chave: 'funil' },
    { chave: 'hipotese-testada' },
    { chave: 'inferencia-ecologica' },
    { chave: 'intervalo-de-95' },
    { chave: 'margem-de-erro' },
    { chave: 'peso-na-virada' },
    { chave: 'piso', notas: ['N08'] },
    { chave: 'ponte-da-virada' },
    { chave: 'ponto-percentual' },
    { chave: 'contagem-parcial', notas: ['N17'] },
    { chave: 'regressao' },
    { chave: 'regressao-ecologica' },
    { chave: 'saldo', comum: true },
    { chave: 'saldo-do-comparecimento' },
    { chave: 'sub-judice', notas: ['N02'] },
    { chave: 'taxa-de-abstencao', notas: ['N05'] },
    { chave: 'validos', comum: true },
    { chave: 'valor-p' },
    { chave: 'vantagem-potencial' },
    { chave: 'voto-anulado', notas: ['N03'] },
    { chave: 'voto-dividido' },
    { chave: 'votos-novos' },
  ].map(t => Object.assign(t, { termo: T(`glos.${t.chave}.termo`), def: T(`glos.${t.chave}.def`), achar: T(`glos.${t.chave}.achar`) }));
  window.GLOSSARIO = TERMOS;

  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const porChave = Object.fromEntries(TERMOS.map(t => [t.chave, t]));

  // ---------- Glossário completo, em Método e fontes, em ordem alfabética ----------
  (function completo() {
    const dl = $('#lista-glossario');
    if (!dl) return;
    TERMOS.slice().sort((a, b) => a.termo.localeCompare(b.termo, T.lingua)).forEach(t => {
      const d = document.createElement('div');
      d.id = 'glossario-' + t.chave; d.tabIndex = -1;
      const dt = document.createElement('dt'); dt.textContent = t.termo;
      const dd = document.createElement('dd'); dd.textContent = t.def;
      for (const n of t.notas || []) {
        dd.append(' ');
        const a = document.createElement('a');
        a.href = '#metodo/nota-' + n; a.textContent = T('glos.nota', { n });
        dd.appendChild(a);
      }
      d.append(dt, dd); dl.appendChild(d);
    });
  })();

  // ---------- Descrições para leitores de tela: uma por termo, fora da vista ----------
  const caixaDesc = document.createElement('div');
  caixaDesc.hidden = true;
  for (const t of TERMOS) {
    const s = document.createElement('span');
    s.id = 'gl-' + t.chave; s.textContent = t.def;
    caixaDesc.appendChild(s);
  }
  document.body.appendChild(caixaDesc);

  // ---------- Marcar os termos no texto ----------
  // Em cada trecho (o Resumo, cada capítulo, cada parte do Explorar e a página Apuração ao vivo), cada
  // termo é marcado uma vez só, na primeira vez em que aparece no texto corrido. As palavras de todo
  // dia com sentido próprio no estudo (comum: fatia, diferença, eleitorado…) são marcadas uma vez só
  // na leitura inteira, uma vez no Explorar e uma na Apuração ao vivo, para o texto não ficar cheio de
  // sublinhados. Títulos, rótulos, links, botões, tabelas, gráficos, a fita e as Notas (que já são as
  // definições das contas) ficam como estão.
  const FORA = 'a, button, h1, h2, h3, label, summary, table, svg, input, textarea, select, sup, script, style, ' +
    '.fig-tit, .fita, .dica, .termo, .botoes-escolha, [role="listbox"], .hip-cab, .leitores, .indice';
  const TRECHOS = '#resumo, #capitulos > article, #explorar > .linha-fina, #explorar .exp-parte, #apuracao';
  const padroes = TERMOS.flatMap(t => t.achar.map(p => ({ p, t })))
    .sort((a, b) => b.p.replace(/\\/g, '').length - a.p.replace(/\\/g, '').length);
  // o termo inteiro, sem pedaço de palavra; em chinês, japonês e coreano não há espaço entre as palavras
  const borda = /^(zh|ja|ko)/.test(T.lingua) ? ['', ''] : ['(?<![\\p{L}\\p{N}])', '(?![\\p{L}\\p{N}])'];
  const re = new RegExp(borda[0] + '(' + padroes.map(x => x.p).join('|') + ')' + borda[1], 'giu');
  const deTexto = s => {
    const baixo = s.toLowerCase();
    const achado = padroes.find(x => new RegExp('^' + x.p + '$', 'iu').test(baixo));
    return achado && achado.t;
  };

  const comunsVistos = { leitura: new Set(), explorar: new Set(), apuracao: new Set() };
  function marcar(trecho) {
    const vistos = new Set(), comuns = comunsVistos[trecho.closest('#explorar') ? 'explorar' : trecho.closest('#apuracao') ? 'apuracao' : 'leitura'];
    const nos = [];
    const w = document.createTreeWalker(trecho, NodeFilter.SHOW_TEXT, {
      acceptNode: n => (n.nodeValue.trim() && !n.parentElement.closest(FORA) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT),
    });
    while (w.nextNode()) nos.push(w.currentNode);
    for (const no of nos) {
      const texto = no.nodeValue;
      const partes = [];
      let ultimo = 0, m;
      re.lastIndex = 0;
      while ((m = re.exec(texto))) {
        const t = deTexto(m[1]);
        if (!t) continue;
        const ja = t.comum ? comuns : vistos;
        if (ja.has(t.chave)) continue;
        ja.add(t.chave);
        partes.push(texto.slice(ultimo, m.index));
        const b = document.createElement('button');
        b.type = 'button'; b.className = 'termo'; b.textContent = m[1];
        b.dataset.termo = t.chave;
        b.setAttribute('aria-describedby', 'gl-' + t.chave);
        partes.push(b);
        ultimo = m.index + m[1].length;
      }
      if (!partes.length) continue;
      partes.push(texto.slice(ultimo));
      no.replaceWith(...partes.filter(p => p !== ''));
    }
  }
  $$(TRECHOS).forEach(marcar);

  // ---------- O verbete: aparece junto do termo ----------
  // Mouse: ao passar. Teclado: ao chegar no termo. Toque: ao tocar, e some ao tocar fora.
  // Esc fecha. A definição para leitores de tela vai pelo aria-describedby de cada termo.
  const verbete = document.createElement('div');
  verbete.className = 'verbete'; verbete.hidden = true;
  verbete.setAttribute('aria-hidden', 'true');
  const vTit = document.createElement('p'); vTit.className = 'verbete-tit';
  const vDef = document.createElement('p'); vDef.className = 'verbete-def';
  verbete.append(vTit, vDef);
  document.body.appendChild(verbete);
  let atual = null, fixo = false;

  function mostrar(b, fixar) {
    const t = porChave[b.dataset.termo];
    if (!t) return;
    atual = b; fixo = !!fixar;
    vTit.textContent = t.termo;
    vDef.textContent = t.def;
    verbete.hidden = false;
    b.setAttribute('aria-expanded', 'true');
    const r = b.getBoundingClientRect(), v = verbete.getBoundingClientRect();
    const larg = document.documentElement.clientWidth;
    const x = Math.max(8, Math.min(r.left, larg - v.width - 8));
    const embaixo = r.bottom + 8 + v.height <= innerHeight - 8 || r.top - 8 - v.height < 8;
    verbete.style.left = x + 'px';
    verbete.style.top = (embaixo ? r.bottom + 8 : r.top - 8 - v.height) + 'px';
  }
  function esconder() {
    if (atual) atual.removeAttribute('aria-expanded');
    atual = null; fixo = false; verbete.hidden = true;
  }
  document.addEventListener('pointerover', ev => {
    const b = ev.target.closest && ev.target.closest('.termo');
    if (b && ev.pointerType === 'mouse' && !fixo) mostrar(b, false);
  });
  document.addEventListener('pointerout', ev => {
    const b = ev.target.closest && ev.target.closest('.termo');
    if (b && ev.pointerType === 'mouse' && !fixo && !b.contains(ev.relatedTarget)) esconder();
  });
  document.addEventListener('focusin', ev => {
    const b = ev.target.closest && ev.target.closest('.termo');
    if (b) mostrar(b, false); else if (atual) esconder();
  });
  document.addEventListener('click', ev => {
    const b = ev.target.closest && ev.target.closest('.termo');
    if (b) { if (atual === b && fixo) esconder(); else mostrar(b, true); return; }
    if (atual) esconder();
  });
  document.addEventListener('keydown', ev => { if (ev.key === 'Escape' && atual) esconder(); });
  addEventListener('scroll', () => { if (atual && !fixo) esconder(); else if (atual) mostrar(atual, true); }, { passive: true });
  addEventListener('resize', () => { if (atual) esconder(); });
})();
