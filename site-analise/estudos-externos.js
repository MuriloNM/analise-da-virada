/* Estudos externos (T13), em Método e fontes: estudos de outras fontes sobre a mesma mudança, comparados
   tema por tema com o que este estudo encontrou. O dado vem de estudos-externos-dados.js, gravado por
   scripts/estudos_externos.py a partir de docs/analise/monitoramento/ (a rotina de monitoramento mantém
   o português; o inglês fica ao lado). Os rótulos ficam no catálogo ('ee.*'). Sem vermelho nem azul,
   que são as cores dos candidatos: cada célula é um sinal em tinta (=, ≠, +, ·), com o nome para leitor
   de tela. A data da última verificação é a do dado publicado. */
(function () {
  'use strict';
  const E = window.ESTUDOS_EXTERNOS, T = window.T;
  const caixa = document.getElementById('met-estudos-externos');
  if (!E || !caixa) return;
  const L = x => x[T.lingua] || x['pt-BR'];
  function el(tag, cls, texto, pai) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (texto !== undefined) e.textContent = texto;
    if (pai) pai.appendChild(e);
    return e;
  }
  const P = (pai, cls, partes) => { const p = el('p', cls, undefined, pai); p.append(...[].concat(partes)); return p; };
  // T42: data e hora (o dado tem as duas, AAAA-MM-DD HH:MM, horário de Brasília)
  const dia = s => (String(s).length >= 16 ? T('ee.data_hora', { data: T.data(String(s).slice(0, 10)), hora: String(s).slice(11, 16) }) : T.data(String(s).slice(0, 10)));
  const SINAL = { igual: '=', diverge: '≠', so_eles: '+' };
  const ROT = { igual: 'ee.igual', diverge: 'ee.diverge', so_eles: 'ee.so_eles' };
  const curto = t => t.id === 'resumo' ? T('ee.col.resumo') : t.id === 'limites' ? T('ee.col.limites') : T('ee.col.cap', { n: t.id.slice(1) });
  const voto = (s, pai) => {
    const v = el('span', 'ee-voto ee-' + (s || 'nada'), s ? SINAL[s] : '·', pai);
    v.setAttribute('aria-hidden', 'true');
    el('span', 'sr', T(s ? ROT[s] : 'ee.nada'), pai);
  };

  P(caixa, 'met-intro', T('ee.intro'));
  P(caixa, 'met-quando ee-quando', T.f('ee.verificado', { data: dia(E.verificado_em), tse: T(E.tse.situacao === 'sem mudança' ? 'ee.tse_igual' : 'ee.tse_outro') }));

  const leg = el('ul', 'ee-legenda', undefined, caixa);
  leg.setAttribute('aria-label', T('ee.legenda_aria'));
  for (const s of ['igual', 'diverge', 'so_eles', '']) {
    const li = el('li', '', undefined, leg);
    el('span', 'ee-voto ee-' + (s || 'nada'), s ? SINAL[s] : '·', li).setAttribute('aria-hidden', 'true');
    li.append(T(s ? ROT[s] : 'ee.nada'));
  }

  const tc = el('div', 'tab-caixa ee-tab', undefined, caixa);
  const tab = el('table', 'tab ee-matriz', undefined, tc);
  el('caption', '', T('ee.tab'), tab);
  const hr = el('tr', '', undefined, el('thead', '', undefined, tab));
  const th0 = el('th', '', T('ee.col.estudo'), hr); th0.scope = 'col';
  for (const t of E.temas) {
    const th = el('th', 'ee-col', curto(t), hr); th.scope = 'col'; th.title = L(t).titulo;
  }
  const tb = el('tbody', '', undefined, tab);
  for (const e of E.estudos) {
    const tr = el('tr', '', undefined, tb);
    const th = el('th', '', undefined, tr); th.scope = 'row';
    const a = el('a', '', L(e).veiculo, th); a.href = '#metodo/ee-' + e.id;
    el('span', 'ee-data', e.data ? dia(e.data) : T('ee.sem_data'), th);
    for (const t of E.temas) {
      const td = el('td', 'ee-cel', undefined, tr);
      voto(e.s[t.id], td);
      if (e.s[t.id]) td.title = L(t).titulo + ': ' + L(e).temas[t.id];
    }
  }

  el('h3', 'met-sub', T('ee.temas_tit'), caixa);
  const dl = el('dl', 'ee-temas', undefined, caixa);
  for (const t of E.temas) { el('dt', '', L(t).titulo, dl); el('dd', '', L(t).nosso, dl); }

  el('h3', 'met-sub', T('ee.fichas_tit'), caixa);
  const ol = el('ol', 'ee-fichas', undefined, caixa);
  for (const e of E.estudos) {
    const x = L(e), li = el('li', '', undefined, ol);
    li.id = 'ee-' + e.id; li.tabIndex = -1;
    const h = el('h4', '', undefined, li);
    const a = el('a', '', x.titulo, h); a.href = e.link;
    P(li, 'met-quando', [x.veiculo, ' · ', x.autor, ' · ', e.data ? T('ee.publicado', { data: dia(e.data) }) : T('ee.sem_data'), ' · ',
      T(e.no_ar ? 'ee.verificado_link' : 'ee.fora_do_ar', { data: dia(e.verificado_em) })]);
    P(li, 'met-conf', x.resumo);
    const grupos = el('div', 'ee-grupos', undefined, li);
    const grupo = (rot, itens) => {
      if (!itens.length) return;
      const g = el('div', '', undefined, grupos);
      el('p', 'ee-grupo', T(rot), g);
      const ul = el('ul', '', undefined, g);
      for (const it of itens) {
        const i = el('li', '', undefined, ul);
        if (it.tema) { el('span', 'ee-tema', it.tema, i); i.append(' ' + it.t); } else i.textContent = it.t;
      }
    };
    const doTipo = s => E.temas.filter(t => e.s[t.id] === s).map(t => ({ tema: L(t).titulo, t: x.temas[t.id] }));
    grupo('ee.g.igual', doTipo('igual'));
    grupo('ee.g.diverge', doTipo('diverge'));
    grupo('ee.g.so_eles', doTipo('so_eles').concat(x.so_eles.map(t => ({ t }))));
    grupo('ee.g.so_nos', x.so_nos.map(t => ({ t })));
  }
  P(caixa, 'met-pe', T('ee.pe'));
})();
