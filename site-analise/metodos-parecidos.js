/* Métodos parecidos (T42), em Método e fontes: outras projeções da apuração de 2026, achadas numa busca na
   imprensa, no GitHub e em sites próprios, como verificação dos métodos do capítulo 7 (T41). Cada ficha diz
   o método como a fonte o descreve, a avaliação que ela publicou e como se compara com este estudo. Os
   textos ficam no catálogo ('mp.*'); aqui, só o endereço, a data de publicação e a hora da busca. */
(function () {
  'use strict';
  const T = window.T, caixa = document.getElementById('met-metodos-parecidos');
  if (!caixa) return;
  // os números do estudo que as fichas citam vêm de dados.js, como no resto da página
  const C = window.ESTUDO && window.ESTUDO.projecoes.chamada, fmt = window.GRAFICOS.fmt;
  const VAL = C ? { secoes: fmt.int(C.secoes), mpg: fmt.pct(C.mediana_pg, 0) } : {};
  const BUSCA = '2026-10-29 23:24'; // a última busca e a hora em que os links foram abertos de novo (horário de Brasília)
  const FICHAS = [
    { id: 'estadao', data: '2026-10-25', link: 'https://www.bnewssaopaulo.com.br/noticias/politica/projecao-do-estadao-estima-lula-com-517-e-flavio-com-483.html' },
    { id: 'teixeira', data: '2026-10-26', link: 'https://github.com/gabrieltt1103-creator/projecao-apuracao-tse' },
    { id: 'aberta', data: '2026-10-29', link: 'https://apuracaoaberta.com.br/' },
    { id: 'setup', data: '2026-10-26', link: 'https://timesbrasil.com.br/eleicoes-2026/projecao-lula-vitoria-4-urnas-apuradas/' },
    { id: 'apura', data: null, link: 'https://apurabrasil.com/' },
    { id: 'prumo', data: '2026-10-05', link: 'https://www.brasilparalelo.com.br/noticias/mais-de-16-milhoes-de-telas-acompanharam-as-eleicoes-pela-brasil-paralelo' },
  ];
  function el(tag, cls, texto, pai) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (texto !== undefined) e.textContent = texto;
    if (pai) pai.appendChild(e);
    return e;
  }
  const P = (pai, cls, partes) => { const p = el('p', cls, undefined, pai); p.append(...[].concat(partes)); return p; };
  const dia = s => (String(s).length >= 16 ? T('ee.data_hora', { data: T.data(String(s).slice(0, 10)), hora: String(s).slice(11, 16) }) : T.data(String(s).slice(0, 10)));

  P(caixa, 'met-intro', T('mp.intro'));
  P(caixa, 'met-quando', T('mp.busca', { data: dia(BUSCA) }));
  const ol = el('ol', 'ee-fichas', undefined, caixa);
  for (const f of FICHAS) {
    const li = el('li', '', undefined, ol);
    li.id = 'mp-' + f.id; li.tabIndex = -1;
    const a = el('a', '', T(`mp.${f.id}.titulo`), el('h4', '', undefined, li));
    a.href = f.link; a.rel = 'noopener';
    P(li, 'met-quando', [T(`mp.${f.id}.quem`), ' · ', f.data ? T('ee.publicado', { data: dia(f.data) }) : T('ee.sem_data'), ' · ',
      T('ee.verificado_link', { data: dia(BUSCA) })]);
    const grupos = el('div', 'ee-grupos', undefined, li);
    for (const k of ['metodo', 'avaliacao', 'comparacao']) {
      const g = el('div', '', undefined, grupos);
      el('p', 'ee-grupo', T('mp.rot.' + k), g);
      P(g, 'met-conf', T(`mp.${f.id}.${k}`, VAL));
    }
  }
  P(caixa, 'met-pe', T.f('mp.nosso'));
})();
