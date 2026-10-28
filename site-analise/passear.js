/* O mapa para passear pelos dados (T36, diário D83): o Brasil por estado e, ao clicar, o estado por município,
   com a ficha do lugar em barras de proporção (quem ficou à frente e por quanto), a comparação de dois lugares
   e a lista do nível em que se está. Fácil de achar: tem lugar no menu e uma chamada no Resumo.
   Só mostra os números que o estudo já tem (dados.js); nenhuma conta nova. A malha dos municípios (P38)
   fica em mapas/mun-<UF>.js (scripts/mapa_municipios.py) e só é carregada quando o estado abre; até
   chegar, ou se falhar, o estado aparece inteiro e os municípios ficam na lista. Montado por estudo.js. */
window.PASSEAR = function (X) {
  'use strict';
  const T = window.T;
  const { D, G, BR, UFS, NOME_UF, municipios, nomeMun, el, B, P, busca, semMovimento } = X;
  const { fmt, nf } = G;
  const $ = (s, r = document) => r.querySelector(s);
  const FORMA = window.MAPA_UFS;
  const malhaDe = cod => (window.MAPA_MUN || {})[cod];
  const carregando = {};
  /** O desenho dos municípios do estado, carregado na primeira vez que ele abre. */
  function carregar(cod) {
    if (malhaDe(cod) || carregando[cod]) return;
    carregando[cod] = 'indo';
    const s = document.createElement('script');
    s.src = T.raiz + 'mapas/mun-' + cod + '.js';
    s.onload = () => { carregando[cod] = 'ok'; if (uf === cod) { desenharMapa(); pintarMapa(); } };
    s.onerror = () => { carregando[cod] = 'falhou'; if (uf === cod) avisoMalha.textContent = T('pas.mapa.sem_malha'); };
    document.head.appendChild(s);
  }
  const raiz = $('#mapa-corpo');
  if (!raiz || !FORMA) return;

  // ---------- Estado da página: o modo de cor, o estado aberto, o lugar da ficha e o lugar fixado para comparar ----------
  let modo = 's2', uf = null, lugar = BR, fixado = null, ordem = 'E1', todos = false;
  const munDe = {};
  const munsDe = cod => munDe[cod] || (munDe[cod] = municipios().filter(m => m.uf === cod));
  const nomeDe = l => (l === BR ? BR.nome : l.codigo ? l.nome : nomeMun(l));
  const ehUf = l => l !== BR && !!l.codigo;

  // ---------- Cores: as mesmas do mapa do Explorar (divergente dos dois lados, cinza no meio; abstenção num tom só) ----------
  const piso = t => (t === 0 ? 0 : Math.sign(t) * (0.3 + 0.7 * Math.min(1, Math.abs(t))));
  const MODOS = {
    s2: { rot: T('pas.modo.s2'), cor: l => G.escalaDivergente()(piso((l.s2 - 50) / 30)) },
    ds: { rot: T('pas.modo.ds'), cor: l => G.escalaDivergente()(l.ds / (uf ? 8 : 5)) },
    da: { rot: T('pas.modo.da'), cor: l => G.escalaSequencial()((l.da + 4) / 12) },
  };
  const corDe = l => (l.s2 === null ? 'var(--neutro)' : MODOS[modo].cor(l));

  // ---------- Esqueleto ----------
  const barraModo = el('div', 'botoes-escolha pas-modos', undefined, raiz);
  barraModo.setAttribute('role', 'group'); barraModo.setAttribute('aria-label', T('pas.modo.aria'));
  const botoesModo = Object.entries(MODOS).map(([k, m]) => {
    const b = el('button', '', m.rot, barraModo);
    b.type = 'button';
    b.addEventListener('click', () => { modo = k; pintar(); });
    return [k, b];
  });
  const grade = el('div', 'pas-grade', undefined, raiz);
  const colMapa = el('div', 'pas-col-mapa', undefined, grade);
  const trilha = el('nav', 'pas-trilha', undefined, colMapa);
  trilha.setAttribute('aria-label', T('pas.trilha.aria'));
  const titulo = el('p', 'pas-titulo', undefined, colMapa);
  const legCor = el('div', 'grafico pas-legenda-cor', undefined, colMapa);
  const caixaMapa = el('div', 'grafico pas-mapa', undefined, colMapa);
  const avisoMalha = el('p', 'pas-aviso', undefined, colMapa);
  const colFicha = el('aside', 'pas-col-ficha', undefined, grade);
  colFicha.setAttribute('aria-live', 'polite');

  // a busca de município, para ir direto ao lugar
  const bq = el('div', 'pas-busca', undefined, raiz);
  const rotB = el('label', '', T('pas.busca'), bq);
  rotB.htmlFor = 'pas-busca-campo';
  const bqc = el('div', 'busca', undefined, bq);
  const entrada = el('input', 'campo', undefined, bqc);
  Object.assign(entrada, { id: 'pas-busca-campo', type: 'search', placeholder: T('res.cidade_placeholder'), autocomplete: 'off', spellcheck: false });
  entrada.setAttribute('role', 'combobox'); entrada.setAttribute('aria-autocomplete', 'list');
  entrada.setAttribute('aria-expanded', 'false'); entrada.setAttribute('aria-controls', 'pas-busca-lista');
  const listaB = el('ul', 'busca-lista', undefined, bqc);
  Object.assign(listaB, { id: 'pas-busca-lista', hidden: true });
  listaB.setAttribute('role', 'listbox'); listaB.setAttribute('aria-label', T('busca.aria'));
  busca(entrada, listaB, null, 'pas-b-', (_, m) => { if (!m.exterior) irPara(m.uf, m); });

  const secLista = el('section', 'pas-lista', undefined, raiz);
  const titLista = el('h2', '', undefined, secLista);
  const ordemBarra = el('div', 'botoes-escolha pas-ordem', undefined, secLista);
  ordemBarra.setAttribute('role', 'group'); ordemBarra.setAttribute('aria-label', T('pas.ordem.aria'));
  const ORDENS = { E1: T('pas.ordem.E1'), s2: T('pas.ordem.s2'), ds: T('pas.ordem.ds') };
  const botoesOrdem = Object.entries(ORDENS).map(([k, t]) => {
    const b = el('button', '', t, ordemBarra);
    b.type = 'button';
    b.addEventListener('click', () => { ordem = k; lista(); });
    return [k, b];
  });
  const caixaLista = el('ol', 'pas-linhas', undefined, secLista);
  const maisLista = el('button', 'bt-link pas-mais', undefined, secLista);
  maisLista.type = 'button';
  maisLista.addEventListener('click', () => { todos = !todos; lista(); });

  // o assistente do estudo (T14) a um clique, para a pergunta que o mapa não responde
  const ia = P(raiz, 'pas-ia', T('pas.ia.texto'), ' ');
  const btIa = el('button', 'bt-link', T('pas.ia.botao'), ia);
  btIa.type = 'button';
  btIa.addEventListener('click', () => { const b = $('.ia-botao'); if (b) b.click(); });
  P(raiz, 'pas-fonte', T('pas.fonte'));

  // ---------- O mapa: o Brasil por estado, ou um estado (por município, quando há malha) ----------
  let mapaEls = {}, contorno = null;
  function desenharMapa() {
    const larg = Math.max(260, Math.min(caixaMapa.clientWidth, 680));
    caixaMapa.replaceChildren();
    const malha = uf && malhaDe(uf);
    if (uf && !malha) carregar(uf);
    let vb, itens;
    if (!uf) { vb = [0, 0, FORMA.largura, FORMA.altura]; itens = UFS.map(u => [u.codigo, FORMA.caminhos[u.codigo], u]); }
    else {
      const n = FORMA.caminhos[uf].match(/-?[0-9.]+/g).map(Number);
      const xs = n.filter((_, i) => i % 2 === 0), ys = n.filter((_, i) => i % 2 === 1);
      const f = 0.04 * Math.max(Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys));
      vb = [Math.min(...xs) - f, Math.min(...ys) - f, Math.max(...xs) - Math.min(...xs) + 2 * f, Math.max(...ys) - Math.min(...ys) + 2 * f];
      const ms = munsDe(uf);
      itens = malha ? ms.map((m, i) => [String(i), malha.caminhos[m.nome], m]).filter(x => x[1]) : [[uf, FORMA.caminhos[uf], UFS.find(u => u.codigo === uf)]];
    }
    // o desenho cabe na largura e numa altura que deixa a ficha à vista
    const altMax = Math.min(560, innerHeight * 0.7);
    let w = larg, h = w * vb[3] / vb[2];
    if (h > altMax) { h = altMax; w = h * vb[2] / vb[3]; }
    const NS = 'http://www.w3.org/2000/svg';
    const s = document.createElementNS(NS, 'svg');
    Object.entries({ width: Math.round(w), height: Math.round(h), viewBox: vb.join(' '), role: 'group',
      'aria-label': uf ? T(malha ? 'pas.mapa.aria_uf' : 'pas.mapa.aria_uf_sem', { uf: NOME_UF[uf] }) : T('pas.mapa.aria_br') })
      .forEach(([k, v]) => s.setAttribute(k, v));
    caixaMapa.appendChild(s);
    const k = vb[2] / w; // um pixel na escala do desenho: o traço fica com a mesma espessura em qualquer zoom
    s.style.setProperty('--px', k);
    if (uf && !malha) { // o estado inteiro, e os vizinhos apagados em volta, para situar
      for (const u of UFS) if (u.codigo !== uf) {
        const p = document.createElementNS(NS, 'path');
        p.setAttribute('d', FORMA.caminhos[u.codigo]); p.setAttribute('class', 'pas-vizinho');
        s.appendChild(p);
      }
    }
    mapaEls = {};
    for (const [id, d, l] of itens) {
      const p = document.createElementNS(NS, 'path');
      p.setAttribute('d', d);
      p.setAttribute('class', 'uf pas-area');
      p.setAttribute('tabindex', '0');
      p.setAttribute('role', 'button');
      s.appendChild(p);
      mapaEls[id] = { p, l };
      const linhas = () => dicaDe(l);
      const ver = ev => {
        const c = linhas();
        if (ev && ev.clientX !== undefined && ev.pointerType !== 'touch') G.dicaMostrar(ev.clientX, ev.clientY, nomeDe(l), c);
        else { const r = p.getBoundingClientRect(); G.dicaMostrar(r.left + r.width / 2, r.top + r.height / 2, nomeDe(l), c); }
      };
      p.addEventListener('pointermove', ver);
      p.addEventListener('focus', () => ver());
      p.addEventListener('pointerleave', ev => { if (ev.pointerType !== 'touch') G.dicaEsconder(); });
      p.addEventListener('blur', () => G.dicaEsconder());
      const escolhe = () => { G.dicaEsconder(); if (!uf) irPara(l.codigo); else if (malha) irPara(uf, l); };
      p.addEventListener('click', ev => { ev.stopPropagation(); escolhe(); });
      p.addEventListener('keydown', ev => { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); escolhe(); } });
    }
    if (malha) { // a divisa do estado por cima dos municípios
      const p = document.createElementNS(NS, 'path');
      p.setAttribute('d', FORMA.caminhos[uf]); p.setAttribute('class', 'pas-divisa');
      s.appendChild(p);
    }
    contorno = document.createElementNS(NS, 'path');
    contorno.setAttribute('class', 'uf-contorno pas-contorno');
    s.appendChild(contorno);
    avisoMalha.textContent = !uf ? '' : !malha ? T(carregando[uf] === 'falhou' ? 'pas.mapa.sem_malha' : 'pas.mapa.carregando')
      : malha.sem_desenho.length ? T.p('pas.mapa.sem_desenho', malha.sem_desenho.length, { lista: malha.sem_desenho.join(', ') }) : '';
    pintarMapa();
  }
  function pintarMapa() {
    for (const id in mapaEls) {
      const { p, l } = mapaEls[id];
      p.style.fill = corDe(l);
      p.setAttribute('aria-label', T('g.aria_item', { titulo: nomeDe(l), valores: dicaDe(l).map(d => T('g.aria_valor', { t: d.t, v: d.v })).join(T('g.aria_sep')) }));
    }
    if (!contorno) return; // o mapa ainda não foi desenhado (a vista estava escondida)
    const sel = Object.values(mapaEls).find(x => x.l === lugar);
    if (sel) { contorno.setAttribute('d', sel.p.getAttribute('d')); contorno.removeAttribute('visibility'); }
    else contorno.setAttribute('visibility', 'hidden');
  }
  function dicaDe(l) {
    if (l.s2 === null) return [{ t: T('pas.sem_votos'), v: '' }];
    if (modo === 'da') return [{ t: T('c4.dica.abst1'), v: fmt.pct(l.a1, 1) }, { t: T('c4.dica.no2'), v: fmt.pct(l.a2, 1) }, { t: T('tab.variacao'), v: fmt.pp(l.da) }];
    if (modo === 'ds') return [{ lado: 'l', t: T('exp.dica.fatia_lula'), v: T('exp.dica.de_para_var', { a: fmt.pct(l.s1, 1), b: fmt.pct(l.s2, 1), v: fmt.pp(l.ds) }) },
      { lado: 'f', t: T('c2.dica.fatia_flavio'), v: T('exp.dica.de_para_var', { a: fmt.pct(100 - l.s1, 1), b: fmt.pct(100 - l.s2, 1), v: fmt.pp(-l.ds) }) }];
    return [{ lado: 'l', t: T('nome.lula'), v: fmt.pct(l.s2, 1) }, { lado: 'f', t: T('nome.flavio'), v: fmt.pct(100 - l.s2, 1) }];
  }

  // ---------- A legenda e o título do mapa, pelo sinal (D80, pendência 2: nenhum lado fixo no título) ----------
  function cabecalho() {
    const ls = uf ? munsDe(uf).filter(m => m.s2 !== null) : UFS;
    const onde = uf ? NOME_UF[uf] : BR.nome, n = ls.length;
    const conta = f => ls.filter(f).length;
    if (modo === 's2') {
      const l = conta(x => x.s2 > 50), f = conta(x => x.s2 < 50), e = n - l - f;
      titulo.textContent = T(uf ? 'pas.tit.s2_uf' : 'pas.tit.s2_br', { onde, l, f, n }) + (e ? T('pas.tit.empates', { e }) : '');
      G.legendaCor(legCor, { dom: [20, 80], cor: v => G.escalaDivergente()(piso((v - 50) / 30)), marcas: [20, 35, 50, 65, 80].map(v => [v, fmt.pct(v, 0)]),
        esq: T('exp.mapa.leg_mais_f'), dir: T('exp.mapa.leg_mais_l') });
    } else if (modo === 'ds') {
      const l = conta(x => x.ds > 0), f = conta(x => x.ds < 0);
      titulo.textContent = T(uf ? 'pas.tit.ds_uf' : 'pas.tit.ds_br', { onde, l, f, n });
      const lim = uf ? 8 : 5;
      G.legendaCor(legCor, { dom: [-lim, lim], cor: v => G.escalaDivergente()(v / lim), marcas: [[-lim, fmt.decSinal(-lim, 0)], [0, '0'], [lim, fmt.pp(lim, 0)]],
        esq: T('exp.mapa.leg_subiu_f'), dir: T('exp.mapa.leg_subiu_l') });
    } else {
      const sub = conta(x => x.da > 0);
      titulo.textContent = T(uf ? 'pas.tit.da_uf' : 'pas.tit.da_br', { onde, sub, caiu: n - sub, n });
      G.legendaCor(legCor, { dom: [-4, 8], cor: v => G.escalaSequencial()((v + 4) / 12), marcas: [[-4, fmt.decSinal(-4, 0)], [0, '0'], [4, fmt.decSinal(4, 0)], [8, fmt.pp(8, 0)]],
        esq: T('exp.mapa.leg_caiu'), dir: T('exp.mapa.leg_subiu') });
    }
  }

  // ---------- A trilha: Brasil › estado › município ----------
  function marcarTrilha() {
    trilha.replaceChildren();
    const ol = el('ol', '', undefined, trilha);
    const passo = (t, acao, atual) => {
      const li = el('li', '', undefined, ol);
      if (atual) { el('span', '', t, li).setAttribute('aria-current', 'location'); return; }
      const b = el('button', 'bt-link', t, li); b.type = 'button'; b.addEventListener('click', acao);
    };
    passo(BR.nome, () => irPara(null), lugar === BR);
    if (uf) passo(NOME_UF[uf], () => irPara(uf), ehUf(lugar));
    if (lugar !== BR && !ehUf(lugar)) passo(lugar.nome, null, true);
  }

  // ---------- A ficha: quem ficou à frente e por quanto, em barras de proporção ----------
  /** Uma barra de 100% entre os dois, com a parte de cada um escrita dentro; o número exato fica no rótulo. */
  function barraDivisao(pai, rot, s, L, F) {
    const lin = el('div', 'pas-div', undefined, pai);
    el('span', 'pas-div-rot', rot, lin);
    const b = el('div', 'pas-div-barra', undefined, lin);
    b.setAttribute('role', 'img');
    b.setAttribute('aria-label', T('pas.ficha.div_aria', { rot, l: fmt.pct(s, 1), lv: fmt.int(L), f: fmt.pct(100 - s, 1), fv: fmt.int(F) }));
    const pl = el('span', 'pas-div-l', undefined, b), pf = el('span', 'pas-div-f', undefined, b);
    pl.style.flexBasis = s + '%'; pf.style.flexBasis = (100 - s) + '%';
    if (s >= 12) pl.textContent = fmt.pct(s, 1);
    if (100 - s >= 12) pf.textContent = fmt.pct(100 - s, 1);
    pl.title = T('pas.ficha.votos', { nome: T('nome.lula'), n: fmt.int(L) });
    pf.title = T('pas.ficha.votos', { nome: T('nome.flavio'), n: fmt.int(F) });
  }
  /** Os votos a mais de cada um, do 1º para o 2º turno, em barras na mesma escala (a partir do zero). */
  function barrasGanho(pai, l, max) {
    const g = el('div', 'pas-ganhos', undefined, pai);
    for (const [lado, nome, v] of [['l', T('nome.lula'), l.dL], ['f', T('nome.flavio'), l.dF]]) {
      const lin = el('div', 'pas-ganho', undefined, g);
      el('span', 'pas-div-rot', nome, lin);
      const trilho = el('span', 'pas-ganho-trilho', undefined, lin);
      const b = el('span', 'pas-ganho-barra pas-' + lado + (v < 0 ? ' pas-neg' : ''), undefined, trilho);
      b.style.width = Math.min(100, 100 * Math.abs(v) / max) + '%';
      el('span', 'pas-ganho-val', T('pas.ficha.ganho', { n: curto(v), p: fmt.comPct(fmt.decSinal(100 * v / l.E1, 1)) }), lin);
    }
  }
  /** "+812 mil", "+1,2 milhão": o número que se lê; o exato fica na tabela e na dica. */
  function curto(v) {
    const a = Math.abs(v);
    if (a >= 1e6) return T.p('un.milhoes', a / 1e6, { n: (v < 0 ? '−' : '+') + nf(a / 1e6, 2) });
    if (a >= 1e4) return fmt.comMil((v < 0 ? '−' : '+') + nf(a / 1e3, 0));
    return fmt.intSinal(v);
  }
  function frente(l, t) {
    const L = t === 1 ? l.L1 : l.L2, F = t === 1 ? l.F1 : l.F2;
    if (L === F) return T('pas.ficha.empate');
    return T('pas.ficha.frente', { nome: T(L > F ? 'nome.lula' : 'nome.flavio'), n: fmt.int(Math.abs(L - F)), p: fmt.pct(100 * Math.abs(L - F) / (L + F), 1) });
  }
  function ficha(pai, l, comparar) {
    const f = el('div', 'pas-ficha' + (comparar ? ' pas-ficha-par' : ''), undefined, pai);
    el('h3', 'ficha-tit', nomeDe(l), f);
    el('p', 'ficha-meta', l === BR ? T('pas.ficha.meta_br') : ehUf(l) ? T('pas.ficha.meta_uf', { regiao: l.regiao, n: fmt.int(munsDe(l.codigo).length) })
      : T('pas.ficha.meta_mun', { uf: NOME_UF[l.uf], e: fmt.int(l.E2) }), f);
    if (l.s2 === null) { P(f, 'ficha-pe', T('pas.sem_votos')); return f; }
    el('p', 'pas-frente', frente(l, 2), f);
    barraDivisao(f, T('g.turno2'), l.s2, l.L2, l.F2);
    barraDivisao(f, T('g.turno1'), l.s1, l.L1, l.F1);
    P(f, 'pas-nota', T('pas.ficha.no1', { frente: frente(l, 1) }));
    el('h4', 'pas-sub', T('pas.ficha.ganhos'), f);
    barrasGanho(f, l, Math.max(Math.abs(l.dL), Math.abs(l.dF)) || 1);
    el('h4', 'pas-sub', T('pas.ficha.abst'), f);
    P(f, 'pas-nota', T('pas.ficha.abst_v', { a1: fmt.pct(l.a1, 1), a2: fmt.pct(l.a2, 1), v: fmt.pp(l.da, 1) }));
    return f;
  }
  function fichas() {
    colFicha.replaceChildren();
    if (fixado && fixado !== lugar) {
      el('p', 'pas-comp-tit', T('pas.comp.tit'), colFicha);
      const par = el('div', 'pas-par', undefined, colFicha);
      ficha(par, fixado, true); ficha(par, lugar, true);
    } else ficha(colFicha, lugar, false);
    const acoes = el('p', 'pas-acoes', undefined, colFicha);
    const bt = (t, f) => { const b = el('button', 'bt-link', t, acoes); b.type = 'button'; b.addEventListener('click', f); return b; };
    if (fixado && fixado !== lugar) bt(T('pas.comp.parar'), () => { fixado = null; fichas(); });
    else if (!fixado || fixado === lugar) {
      if (fixado === lugar) { P(colFicha, 'pas-dica', T('pas.comp.escolha')); bt(T('pas.comp.parar'), () => { fixado = null; fichas(); }); }
      else bt(T('pas.comp.fixar', { nome: nomeDe(lugar) }), () => { fixado = lugar; fichas(); });
    }
    if (!uf && lugar === BR) P(colFicha, 'pas-dica', T('pas.dica_br'));
  }

  // ---------- A lista do nível: os estados, ou os municípios do estado, com a barra de cada um ----------
  function lista() {
    const ls = (uf ? munsDe(uf) : UFS).filter(l => l.s2 !== null).slice();
    const chave = { E1: l => -l.E1, s2: l => -l.s2, ds: l => -l.ds }[ordem];
    ls.sort((a, b) => chave(a) - chave(b) || a.nome.localeCompare(b.nome, T.lingua));
    titLista.textContent = uf ? T('pas.lista.tit_uf', { uf: NOME_UF[uf], n: fmt.int(ls.length) }) : T('pas.lista.tit_br');
    botoesOrdem.forEach(([k, b]) => b.setAttribute('aria-pressed', k === ordem ? 'true' : 'false'));
    const LIM = 30, mostra = todos ? ls : ls.slice(0, LIM);
    caixaLista.replaceChildren();
    for (const l of mostra) {
      const li = el('li', l === lugar ? 'atual' : '', undefined, caixaLista);
      const b = el('button', 'pas-linha', undefined, li);
      b.type = 'button';
      el('span', 'pas-linha-nome', l.nome, b);
      const barra = el('span', 'pas-div-barra pas-mini', undefined, b);
      const pl = el('span', 'pas-div-l', undefined, barra), pf = el('span', 'pas-div-f', undefined, barra);
      pl.style.flexBasis = l.s2 + '%'; pf.style.flexBasis = (100 - l.s2) + '%';
      el('span', 'pas-linha-val', T('pas.lista.val', { l: fmt.pct(l.s2, 0), f: fmt.pct(100 - l.s2, 0) }), b);
      el('span', 'pas-linha-var', fmt.pp(l.ds, 1), b);
      b.setAttribute('aria-label', T('pas.lista.aria', { nome: l.nome, l: fmt.pct(l.s2, 1), f: fmt.pct(100 - l.s2, 1), v: fmt.pp(l.ds, 1) }));
      b.addEventListener('click', () => (uf ? irPara(uf, l) : irPara(l.codigo)));
    }
    maisLista.hidden = ls.length <= LIM;
    maisLista.textContent = todos ? T('pas.lista.menos') : T('pas.lista.todos', { n: fmt.int(ls.length) });
  }

  // ---------- Navegar: o endereço guarda o estado (#mapa/SP), para voltar e para compartilhar ----------
  let ultimaLarg = -1;
  function irPara(cod, mun, { endereco = true } = {}) {
    const mudouUf = (cod || null) !== uf;
    uf = cod || null;
    lugar = mun || (uf ? UFS.find(u => u.codigo === uf) : BR);
    if (mudouUf) todos = false;
    if (endereco) {
      const h = uf ? '#mapa/' + uf : '#mapa';
      if (location.hash !== h) history.pushState(null, '', h);
    }
    if (mudouUf) desenharMapa();
    pintar();
  }
  function pintar() {
    botoesModo.forEach(([k, b]) => b.setAttribute('aria-pressed', k === modo ? 'true' : 'false'));
    cabecalho(); pintarMapa(); marcarTrilha(); fichas(); lista();
  }
  new ResizeObserver(() => {
    const w = Math.round(caixaMapa.clientWidth);
    if (w > 0 && w !== ultimaLarg) { ultimaLarg = w; desenharMapa(); cabecalho(); }
  }).observe(caixaMapa);
  // o endereço #mapa/SP abre o estado; o voltar do navegador também
  function doEndereco() {
    const m = /^#mapa(?:\/([A-Z]{2}))?$/.exec(location.hash);
    if (!m) return;
    const c = m[1] && UFS.some(u => u.codigo === m[1]) ? m[1] : null;
    if (c !== uf || (lugar !== BR && !c)) irPara(c, null, { endereco: false });
  }
  addEventListener('hashchange', doEndereco);
  addEventListener('popstate', doEndereco);
  doEndereco();
  pintar();
  return { irPara };
};
