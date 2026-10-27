/* Descrição em texto de cada gráfico (T25; especificação 7.5, acessibilidade). Carregado depois de
   estudo.js. Cada figura ganha, embaixo da fonte, "Descrição em texto": o que o gráfico mostra e a
   conclusão (do título e do subtítulo da figura) e os números de cada marca, tirados das mesmas
   etiquetas que o leitor de tela lê em cada barra, ponto ou estado. Nos gráficos com milhares de
   pontos (dispersões e funis), a descrição diz onde estão os números de cada município. O texto é
   refeito sempre que o gráfico é desenhado de novo (largura nova, escolha nova, recorte do
   Explorar), então nunca fica diferente do que está na tela. O SVG de cada gráfico aponta para a
   legenda da figura e para a descrição (aria-describedby). Vale para a leitura, o Explorar e a
   página Apuração ao vivo (T28). Os textos vêm do catálogo da língua da página (chaves "desc."; T30). */
(function () {
  'use strict';
  const T = window.T;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const MAX_ITENS = 60;
  let seq = 0;
  const limpa = s => (s || '').replace(/\s+/g, ' ').trim();
  const semPonto = s => s.replace(/[.\s]+$/, '');

  function el(tag, cls, texto, pai) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (texto !== undefined) e.textContent = texto;
    if (pai) pai.appendChild(e);
    return e;
  }
  function link(href, texto) { const a = el('a', '', texto); a.href = href; return a; }

  function preparar(fig) {
    const caixa = $('.grafico', fig);
    if (!caixa || fig.dataset.descricao) return;
    const id = 'desc-' + (++seq);
    fig.dataset.descricao = id;
    const cap = $('figcaption', fig);
    if (cap && !cap.id) cap.id = 'leg-' + seq;
    const det = el('details', 'fig-desc');
    el('summary', '', T('desc.resumo'), det);
    const corpo = el('div', 'fig-desc-corpo', undefined, det);
    corpo.id = id;
    (fig.querySelector('.fig-rodape') || caixa).after(det);
    const atualizar = () => descrever(fig, caixa, corpo, cap);
    new MutationObserver(atualizar).observe(caixa, { childList: true });
    det.addEventListener('toggle', () => { if (det.open) atualizar(); });
    atualizar();
  }

  function descrever(fig, caixa, corpo, cap) {
    const svg = $('svg', caixa);
    corpo.replaceChildren();
    const ft = $('.fig-tit', fig), fn = ft && $('.fig-n', ft);
    const titulo = ft ? limpa(ft.textContent.slice(fn ? fn.textContent.length : 0)) : '';
    const subs = $$('.fig-sub', fig).map(s => limpa(s.textContent));
    const p = el('p', '', undefined, corpo);
    if (subs[0]) p.append(T('desc.sub', { t: semPonto(subs[0]) }));
    if (titulo) p.append(T('desc.conclusao', { t: semPonto(titulo) }));
    if (!svg) { el('p', '', T('desc.sem_grafico'), corpo); return; }
    const resumo = limpa(svg.getAttribute('aria-label'));
    // o rótulo do SVG entra quando acrescenta algo: números ou mais de uma frase (senão repete o subtítulo)
    if (resumo && resumo !== titulo && (/\d[.,]\d|\d{3}/.test(resumo) || /\.\s/.test(resumo))) el('p', '', T('desc.frase', { t: semPonto(resumo) }), corpo);
    // Os números de cada marca: as mesmas etiquetas que o teclado e o leitor de tela percorrem
    const itens = $$('[aria-label]', svg).filter(e => e !== svg && e.getAttribute('aria-label')).map(e => limpa(e.getAttribute('aria-label')));
    const unicos = [...new Set(itens)];
    if (unicos.length && unicos.length <= MAX_ITENS) {
      el('p', '', T('desc.numeros'), corpo);
      const ul = el('ul', '', undefined, corpo);
      for (const t of unicos) el('li', '', t, ul);
    } else if (fig.closest('#apuracao, #capitulo-7')) {
      // as linhas da apuração ao vivo: uma marca por leitura gravada
      const n = window.APURACAO_DADOS ? window.APURACAO_DADOS.leituras.length : '';
      el('p', '', undefined, corpo).append(...T.f('desc.leituras', { n, dados: link('#metodo/dados', T('met.dados.tit')) }));
    } else if ((resumo + ' ' + subs.join(' ')).includes(T('desc.palavra_municipios')) || $('circle', svg)) {
      el('p', '', undefined, corpo).append(...T.f('desc.pontos', { busca: link('#resumo', T('desc.link_busca')),
        explorar: link('#explorar/municipios', T('nav.explorar')), dados: link('#metodo/dados', T('met.dados.tit')) }));
    }
    const tab = fig.closest('.capitulo') && $('.detalhes table', fig.closest('.capitulo'));
    if (tab) el('p', '', T('desc.detalhes'), corpo);
    svg.setAttribute('aria-describedby', [cap && cap.id, corpo.id].filter(Boolean).join(' '));
  }

  const FIGURAS = '.fig-abertura, #capitulos figure.figura, #explorar figure.figura, #apuracao figure.figura';
  $$(FIGURAS).forEach(preparar);
  // O Explorar e a Apuração ao vivo refazem partes ao mudar uma escolha: figuras novas também ganham a descrição
  for (const vista of ['#explorar', '#apuracao']) {
    const e = $(vista);
    if (e) new MutationObserver(() => $$(vista + ' figure.figura').forEach(preparar)).observe(e, { childList: true, subtree: true });
  }
})();
