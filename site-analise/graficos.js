/* Componentes de gráfico do estudo (T08; caderno de apuração no T29; reaproveitados no T24):
   dispersão, linhas de pontos, barras, divisão de 100%, coeficientes com intervalo, ponte da
   virada, linha da apuração, funil, a virada da abertura, a tabela ordenável, o mapa dos estados (T24) e as leituras da apuração ao vivo (T28). Rótulo direto e
   anotação editorial onde couber, no lugar da legenda (pedido em prompt design/). SVG puro, sem
   biblioteca, a partir dos gráficos do ateliê (T07).
   Cores só por classes do CSS (--lula, --flavio, tinta e cinzas), para seguir o modo claro ou
   escuro sem redesenhar. Dica (número exato) ao passar o mouse, tocar ou focar pelo teclado;
   todo texto vindo dos dados entra com textContent. */
(function () {
  'use strict';
  const NS = 'http://www.w3.org/2000/svg';
  const MENOS = '−';

  // ---------- Formatação na língua da página (lingua.js); arredonda uma vez, na hora de mostrar (diário, D25) ----------
  // Só o jeito de escrever muda de língua (separador decimal e de milhar, unidade): os dígitos são os mesmos.
  const T = window.T, LINGUA = T.lingua;
  const NF = {};
  const nf = (v, c) => (NF[c] || (NF[c] = new Intl.NumberFormat(LINGUA, { minimumFractionDigits: c, maximumFractionDigits: c }))).format(Math.abs(v));
  const sinalDe = (v, c) => { const r = Math.round(v * 10 ** c); return r > 0 ? '+' : r < 0 ? MENOS : ''; };
  const negDe = (v, c) => (Math.round(v * 10 ** c) < 0 ? MENOS : '');
  const VAZIO = T('un.vazio');
  // Chinês e japonês contam em 万 (dez mil): 6,66 milhões vira 666万, com o mesmo arredondamento (T44).
  const DEZ_MIL = /^(zh|ja)/.test(LINGUA);
  const NFL = {};
  const nfAte = (v, c, grupo = true) => (NFL[c + '' + grupo] || (NFL[c + '' + grupo] = new Intl.NumberFormat(LINGUA, { minimumFractionDigits: grupo ? 0 : c, maximumFractionDigits: c, useGrouping: grupo }))).format(Math.abs(v));
  /** Só o número de milhões, sem unidade nem sinal; em 万, arredondado no mesmo passo. */
  const nMi = (v, c = 2) => {
    if (!DEZ_MIL) return nf(v / 1e6, c);
    const passo = 10 ** (6 - c);
    return nfAte(Math.round(Math.abs(v) / passo) * passo / 1e4, Math.max(0, c - 2), false); // 1500万, sem separador, como a imprensa
  };
  /** Milhares com a unidade, sem sinal: "5 mil"; em chinês e japonês, 5000 ou 5万. */
  const mil = (v, c = 0) => {
    if (!DEZ_MIL) return T('un.mil', { n: nf(v / 1e3, c) });
    const passo = 10 ** (3 - c), r = Math.round(Math.abs(v) / passo) * passo;
    return r >= 1e4 ? T('un.mi', { n: nfAte(r / 1e4, c + 1) }) : nf(r, 0);
  };
  const fmt = {
    int: v => negDe(v, 0) + nf(v, 0),
    intSinal: v => sinalDe(v, 0) + nf(v, 0),
    dec: (v, c = 2) => negDe(v, c) + nf(v, c),
    decSinal: (v, c = 2) => sinalDe(v, c) + nf(v, c),
    abs: (v, c = 2) => nf(v, c),
    pct: (v, c = 1) => (v === null || v === undefined ? VAZIO : T('un.pct', { n: negDe(v, c) + nf(v, c) })),
    pp: (v, c = 2) => (v === null || v === undefined ? VAZIO : T('un.pp', { n: sinalDe(v, c) + nf(v, c) })),
    mi: (v, c = 2) => T('un.mi', { n: sinalDe(v / 1e6, c) + nMi(v, c) }),
    miAbs: (v, c = 2) => T.p('un.milhoes', v / 1e6, { n: nMi(v, c) }),
    /** Milhões sem sinal ("4 mi"), milhares sem e com sinal ("5 mil", "+5 mil"), de um número em votos. */
    miCurto: (v, c = 2) => T('un.mi', { n: nMi(v, c) }),
    mil,
    milSinal: (v, c = 0) => sinalDe(v / 1e3, c) + mil(v, c),
    nMi,
    p: v => (v < 0.0005 ? T('un.abaixo_de', { n: nf(0.001, 3) }) : nf(v, 3)),
    /** Um número já escrito, com a unidade: "+2%", "3 mil". */
    comPct: s => T('un.pct', { n: s }),
    comMi: s => T('un.mi', { n: s }),
    comMil: s => T('un.mil', { n: s }),
    vazio: VAZIO,
  };
  /** Rótulo de uma marca para o leitor de tela e para a descrição em texto: "Título: item valor; item valor". */
  const rotuloAria = (titulo, linhas) => T('g.aria_item', { titulo,
    valores: linhas.map(d => T('g.aria_valor', { t: d.t, v: d.v || '' })).join(T('g.aria_sep')) });

  // ---------- SVG e HTML ----------
  function el(nome, attrs, pai) {
    const e = document.createElementNS(NS, nome);
    for (const k in attrs) if (attrs[k] !== undefined && attrs[k] !== null) e.setAttribute(k, attrs[k]);
    if (pai) pai.appendChild(e);
    return e;
  }
  function texto(pai, x, y, t, attrs = {}) {
    const e = el('text', Object.assign({ x, y }, attrs), pai);
    e.textContent = t;
    return e;
  }
  function svgNovo(caixa, w, h, rotulo, papel = 'img') {
    caixa.replaceChildren();
    return el('svg', { width: w, height: h, viewBox: `0 0 ${w} ${h}`, role: papel, 'aria-label': rotulo }, caixa);
  }
  function h(tag, cls, t, pai) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (t !== undefined && t !== null) e.textContent = t;
    if (pai) pai.appendChild(e);
    return e;
  }
  const escala = (d0, d1, r0, r1) => v => r0 + (v - d0) / (d1 - d0) * (r1 - r0);
  const limita = (v, a, b) => Math.max(a, Math.min(b, v));
  const css = nome => getComputedStyle(document.documentElement).getPropertyValue(nome).trim();
  const corLado = lado => css(lado === 'l' ? '--lula' : lado === 'f' ? '--flavio' : lado === 'muted' ? '--muted' : lado === 'l1' ? '--lula-1t' : '--ink');
  /** Barra com a ponta de dado arredondada (4 px) e a base reta, de x0 (base) a x1 (ponta). */
  function barraH(pai, x0, x1, y, alt, cls) {
    const r = Math.min(4, Math.abs(x1 - x0), alt / 2), d = x1 >= x0 ? 1 : -1;
    const xp = x1 - d * r;
    const path = `M${x0} ${y}H${xp}A${r} ${r} 0 0 ${d > 0 ? 1 : 0} ${x1} ${y + r}V${y + alt - r}` +
      `A${r} ${r} 0 0 ${d > 0 ? 1 : 0} ${xp} ${y + alt}H${x0}Z`;
    return el('path', { d: path, class: cls }, pai);
  }

  // ---------- Dica (tooltip) ----------
  let dica;
  function dicaEl() {
    if (!dica) {
      dica = h('div', 'dica', undefined, document.body);
      dica.hidden = true;
      dica.setAttribute('aria-hidden', 'true');
    }
    return dica;
  }
  /** linhas: [{t, v, lado: 'l' | 'f' | 'ink' | 'muted'}]; o valor vem primeiro na leitura (dataviz). */
  function dicaMostrar(x, y, titulo, linhas) {
    const d = dicaEl();
    d.replaceChildren();
    h('div', 'dt', titulo, d);
    for (const l of linhas) {
      const r = h('div', 'dl', undefined, d);
      if (l.lado) { const k = h('i', 'k', undefined, r); k.style.background = corLado(l.lado); }
      h('span', '', l.t, r);
      if (l.v !== undefined) h('b', '', l.v, r);
    }
    d.hidden = false;
    const q = d.getBoundingClientRect();
    let px = x + 14, py = y + 14;
    if (px + q.width > innerWidth - 8) px = x - q.width - 14;
    if (py + q.height > innerHeight - 8) py = y - q.height - 14;
    d.style.left = Math.max(8, px) + 'px';
    d.style.top = Math.max(8, py) + 'px';
  }
  function dicaEsconder() { if (dica) dica.hidden = true; }
  function dicaNoElemento(alvo, titulo, linhas) {
    const r = alvo.getBoundingClientRect();
    dicaMostrar(r.left + Math.min(r.width / 2, 160), r.top + r.height / 2, titulo, linhas);
  }
  addEventListener('scroll', dicaEsconder, { passive: true });
  document.addEventListener('pointerdown', ev => { if (!ev.target.closest || !ev.target.closest('.grafico')) dicaEsconder(); });
  /** T38: a linha "passe o mouse ou toque" sob o gráfico (CSS: .grafico[data-dica]::after), para a descoberta não depender do acaso. */
  function marcarDica(alvo) {
    const g = alvo.closest && alvo.closest('.grafico');
    if (g && !g.dataset.dica) g.dataset.dica = T('graf.dica');
  }
  /** Liga a dica a um alvo (retângulo transparente ou marca), com mouse, toque e teclado. */
  function ligarDica(alvo, titulo, linhas, aoMostrar) {
    marcarDica(alvo);
    const mostra = ev => {
      const ls = typeof linhas === 'function' ? linhas() : linhas;
      if (ev && ev.clientX !== undefined && ev.pointerType !== 'touch') dicaMostrar(ev.clientX, ev.clientY, titulo, ls);
      else dicaNoElemento(alvo, titulo, ls);
      if (aoMostrar) aoMostrar(true);
    };
    const esconde = () => { dicaEsconder(); if (aoMostrar) aoMostrar(false); };
    alvo.addEventListener('pointermove', mostra);
    alvo.addEventListener('click', ev => { ev.stopPropagation(); mostra(ev); });
    alvo.addEventListener('focus', () => mostra());
    alvo.addEventListener('pointerleave', ev => { if (ev.pointerType !== 'touch') esconde(); });
    alvo.addEventListener('blur', esconde);
  }

  // ---------- Legenda (HTML, acima do gráfico) ----------
  /** itens: [{t, lado: 'l' | 'f' | 'ink' | 'muted', tipo: 'ponto' | 'linha' | 'barra' | 'faixa'}] */
  function legenda(pai, itens) {
    const u = h('ul', 'legenda', undefined, pai);
    for (const i of itens) {
      const li = h('li', '', undefined, u);
      h('i', 'leg-' + (i.tipo || 'ponto') + ' leg-' + (i.lado || 'ink'), undefined, li);
      li.append(i.t);
    }
    return u;
  }

  // ---------- Eixos ----------
  function ticks(min, max, passo) {
    const t = [];
    for (let v = Math.ceil(min / passo - 1e-9) * passo; v <= max + 1e-9; v += passo) t.push(Math.round(v * 1e6) / 1e6);
    return t;
  }

  // ---------- 1. Dispersão (um ponto por município, área pelo eleitorado) ----------
  /** o: {pontos: [{x, y, peso, lado, titulo, linhas}], x: {min, max, passo, fmt, rotulo}, y: {...},
   *      reta: {a, b, de, ate, rotulo}, marca: {x, y, rotulo}, aria}. Devolve quantos ficaram fora do eixo y. */
  function dispersao(caixa, o) {
    const pts = o.pontos.slice().sort((a, b) => b.peso - a.peso); // grandes embaixo, pequenos por cima
    const larg = caixa.clientWidth, estreito = larg < 520;
    const alt = Math.round(Math.max(260, Math.min(340, larg * 0.5)));
    const mE = 44, mD = 12, mT = 26, mB = 44;
    const s = svgNovo(caixa, larg, alt, o.aria);
    const x = escala(o.x.min, o.x.max, mE, larg - mD);
    const yb = escala(o.y.min, o.y.max, alt - mB, mT);
    const y = v => yb(limita(v, o.y.min, o.y.max));
    const grade = el('g', { class: 'grade' }, s);
    for (const v of ticks(o.y.min, o.y.max, o.y.passo)) {
      el('line', { x1: mE, x2: larg - mD, y1: y(v), y2: y(v), class: Math.abs(v) < 1e-9 ? 'zero' : '' }, grade);
      texto(s, mE - 6, y(v) + 4, o.y.fmt(v), { 'text-anchor': 'end', class: 'tick' });
    }
    const tx = ticks(o.x.min, o.x.max, o.x.passo);
    tx.forEach((v, i) => texto(s, x(v), alt - mB + 18, o.x.fmt(v),
      { 'text-anchor': i === 0 ? 'start' : i === tx.length - 1 ? 'end' : 'middle', class: 'tick' }));
    texto(s, estreito ? 0 : mE, alt - 6, o.x.rotulo, { class: 'rotulo-eixo' }); // no celular o rótulo começa na borda, para caber (QA nº 8)
    texto(s, 0, 12, o.y.rotulo, { class: 'rotulo-eixo' });
    const maxP = Math.max(...pts.map(p => p.peso)), rMax = estreito ? 9 : 13;
    const g = el('g', {}, s);
    let fora = 0;
    for (const p of pts) {
      if (p.y < o.y.min || p.y > o.y.max) fora++;
      p.px = x(p.x); p.py = y(p.y); p.r = 1.2 + (rMax - 1.2) * Math.sqrt(p.peso / maxP);
      el('circle', { cx: p.px.toFixed(1), cy: p.py.toFixed(1), r: p.r.toFixed(1), class: 'ponto p-' + p.lado }, g);
    }
    if (o.reta) {
      const { a, b, de, ate } = o.reta;
      el('line', { x1: x(de), y1: y(a + b * de), x2: x(ate), y2: y(a + b * ate), class: 'reta' }, s);
      const rx = x(ate), ry = y(a + b * ate);
      texto(s, rx, ry + (b < 0 ? 18 : -10), o.reta.rotulo, { 'text-anchor': 'end', class: 'nome-linha' });
    }
    if (o.marca) {
      el('circle', { cx: x(o.marca.x), cy: y(o.marca.y), r: 5, class: 'marca-br' }, s);
      texto(s, x(o.marca.x) + 9, y(o.marca.y) - 8, o.marca.rotulo, { class: 'nome-linha val-forte' });
    }
    if (o.rotulos) {
      for (const r of o.rotulos) {
        const g = el('g', { class: 'rotulo-direto' }, s);
        el('circle', { cx: x(r.x) + 5, cy: y(r.y) - 4, r: 4.5, class: 'p-' + r.lado }, g);
        texto(g, x(r.x) + 15, y(r.y), estreito && r.curto ? r.curto : r.t, { class: 'nome-linha' });
      }
    }
    if (o.anotacao) anotar(s, o.anotacao, x, y, estreito);
    const anel = el('circle', { r: 0, class: 'anel', visibility: 'hidden' }, s);
    const cel = 24, grid = new Map();
    for (const p of pts) {
      const k = Math.floor(p.px / cel) + ',' + Math.floor(p.py / cel);
      (grid.get(k) || grid.set(k, []).get(k)).push(p);
    }
    function maisProximo(px, py) {
      let melhor = null, dist = Infinity;
      const cx = Math.floor(px / cel), cy = Math.floor(py / cel);
      for (let i = -1; i <= 1; i++) for (let j = -1; j <= 1; j++) {
        for (const p of grid.get((cx + i) + ',' + (cy + j)) || []) {
          const d = Math.hypot(p.px - px, p.py - py) - p.r;
          if (d < dist) { dist = d; melhor = p; }
        }
      }
      return dist <= 16 ? melhor : null;
    }
    const mover = ev => {
      const r = s.getBoundingClientRect();
      const p = maisProximo(ev.clientX - r.left, ev.clientY - r.top);
      if (!p) { anel.setAttribute('visibility', 'hidden'); dicaEsconder(); return; }
      anel.setAttribute('cx', p.px); anel.setAttribute('cy', p.py); anel.setAttribute('r', p.r + 3);
      anel.setAttribute('visibility', 'visible');
      dicaMostrar(ev.clientX, ev.clientY, p.titulo, typeof p.linhas === 'function' ? p.linhas() : p.linhas);
    };
    s.addEventListener('pointermove', mover);
    s.addEventListener('pointerdown', mover);
    s.addEventListener('pointerleave', ev => { if (ev.pointerType !== 'touch') { anel.setAttribute('visibility', 'hidden'); dicaEsconder(); } });
    return fora;
  }

  /** Anotação editorial dentro do gráfico: a frase do achado em itálico, com uma linha guia até o
   *  que importa. a: {linhas, linhasEstreito, x, y, xEstreito, yEstreito, alvo: {x, y}, ancora},
   *  em unidades dos dados. */
  function anotar(s, a, x, y, estreito) {
    const ls = estreito && a.linhasEstreito ? a.linhasEstreito : a.linhas;
    const tx = x(estreito && a.xEstreito !== undefined ? a.xEstreito : a.x);
    const ty = y(estreito && a.yEstreito !== undefined ? a.yEstreito : a.y);
    const ax = x(a.alvo.x), ay = y(a.alvo.y);
    const t = el('text', { x: tx, y: ty, class: 'anotacao', 'text-anchor': a.ancora || 'start' }, s);
    ls.forEach((l, i) => { const ts = el('tspan', { x: tx, dy: i ? '1.25em' : null }, t); ts.textContent = l; });
    const q = t.getBBox();
    const sx = limita(ax, q.x + 8, q.x + q.width - 8);
    const sy = ay > q.y + q.height ? q.y + q.height + 5 : q.y - 5;
    el('path', { d: `M${sx} ${sy}Q${sx} ${(sy + ay) / 2} ${ax} ${ay}`, class: 'guia' }, s);
    el('circle', { cx: ax, cy: ay, r: 2.5, class: 'guia-ponto' }, s);
    s.appendChild(t); // o texto fica por cima da guia
    return t;
  }

  // ---------- Linha por item: nome à esquerda e o resto desenhado em cada linha ----------
  function linhasBase(caixa, o, desenhaLinha) {
    const larg = caixa.clientWidth, estreito = larg < 520;
    const lh = o.altLinha || 20, topo = o.topo || 22, base = o.base || 40;
    const margE = estreito ? (o.margEstreito || 40) : (o.margE || 150), margD = o.margD || 16;
    const alt = topo + o.linhas.length * lh + base;
    const s = svgNovo(caixa, larg, alt, o.aria, 'group');
    const x = escala(o.x.min, o.x.max, margE, larg - margD);
    const grade = el('g', { class: 'grade' }, s);
    for (const v of ticks(o.x.min, o.x.max, o.x.passo)) {
      el('line', { x1: x(v), x2: x(v), y1: topo - 4, y2: alt - base + 4, class: Math.abs(v - (o.x.ref || 0)) < 1e-9 ? 'zero' : '' }, grade);
      const tk = texto(s, x(v), alt - base + 18, o.x.fmt(v), { 'text-anchor': 'middle', class: 'tick' });
      if (DEZ_MIL && x(v) + tk.getComputedTextLength() / 2 > larg) tk.setAttribute('text-anchor', 'end'); // +1500万 na borda (T44)
    }
    texto(s, estreito ? 0 : margE, alt - 6, o.x.rotulo, { class: 'rotulo-eixo' });
    if (o.lados) {
      texto(s, x(0) - 6, topo - 9, o.lados[0], { 'text-anchor': 'end', class: 'rotulo-eixo' });
      texto(s, x(0) + 6, topo - 9, o.lados[1], { class: 'rotulo-eixo' });
    }
    o.linhas.forEach((l, i) => {
      const y0 = topo + i * lh, yc = y0 + lh / 2;
      if (l.grupo) {
        texto(s, 0, yc + 4, l.grupo, { class: 'nome-linha val-forte' });
        return;
      }
      if (l.destaque) el('rect', { x: 0, y: y0, width: larg, height: lh, class: 'linha-destaque' }, s);
      const nome = estreito && l.curto ? l.curto : l.nome;
      texto(s, margE - 8, yc + 4, nome, { 'text-anchor': 'end', class: 'nome-linha' + (l.destaque ? ' val-forte' : '') });
      desenhaLinha(s, l, x, y0, yc, lh, estreito);
      if (l.dica) {
        const alvo = el('rect', { x: 0, y: y0, width: larg, height: lh, fill: 'transparent', tabindex: 0, class: 'alvo',
          'aria-label': rotuloAria(l.dica.titulo, l.dica.linhas) }, s);
        ligarDica(alvo, l.dica.titulo, l.dica.linhas, on => alvo.classList.toggle('ativo', on));
      }
    });
    return { s, x, alt };
  }

  /** 2. Pontos por linha (um ponto para cada candidato, ligados por um fio).
   *  o: {linhas: [{nome, curto, vals: [{v, lado}], dica: {titulo, linhas}}], x, aria,
   *      series: {l: 'Lula', f: 'Flávio'}}: com series, o nome de cada um vai sobre os pontos da
   *  primeira linha (rótulo direto, sem legenda). */
  function linhasPontos(caixa, o) {
    let primeira = true;
    return linhasBase(caixa, o, (s, l, x, y0, yc) => {
      const vs = l.vals.map(v => v.v);
      el('line', { x1: x(Math.min(...vs)), x2: x(Math.max(...vs)), y1: yc, y2: yc, class: 'fio' }, s);
      for (const v of l.vals) el('circle', { cx: x(v.v), cy: yc, r: 4.5, class: 'pt-anel p-' + v.lado }, s);
      if (o.series && primeira) {
        const [a, b] = l.vals.slice().sort((p, q) => p.v - q.v);
        texto(s, x(a.v) - 2, y0 - 4, o.series[a.lado], { 'text-anchor': 'end', class: 'nome-linha val-forte' });
        const tb = texto(s, x(b.v) + 2, y0 - 4, o.series[b.lado], { class: 'nome-linha val-forte' });
        const wb = tb.getComputedTextLength(), W = +s.getAttribute('width');
        if (x(b.v) + 2 + wb > W - 2) { tb.setAttribute('x', Math.min(x(b.v) + 6, W - 2)); tb.setAttribute('text-anchor', 'end'); } // não passa da borda no celular
      }
      primeira = false;
    });
  }

  /** 3. Barras horizontais de uma série neutra, a partir do zero, com o valor na ponta.
   *  o: {linhas: [{nome, curto, v, rotulo, dica, destaque}], x, ref: {v, rotulo}, aria} */
  function barras(caixa, o) {
    const larg = caixa.clientWidth, margE = larg < 520 ? (o.margEstreito || 40) : (o.margE || 150);
    const negativos = []; // o valor de cada barra negativa e se ele cabe à esquerda da barra
    const r = linhasBase(caixa, o, (s, l, x, y0, yc, lh) => {
      const bh = Math.min(12, lh - 8);
      barraH(s, x(0), x(l.v), yc - bh / 2, bh, 'barra-n' + (l.destaque ? ' barra-forte' : ''));
      const fora = l.v >= 0;
      const t = texto(s, x(l.v) + (fora ? 5 : -5), yc + 4, l.rotulo, { 'text-anchor': fora ? 'start' : 'end', class: 'val' });
      if (!fora) negativos.push({ t, cabe: x(l.v) - 5 - t.getComputedTextLength() >= margE, x0: x(0) });
    });
    // barra negativa comprida no celular: o valor não cabe entre a barra e os nomes (QA nº 6); então todos os
    // valores negativos passam para o lado direito do zero, que está vazio, para a coluna não misturar os dois jeitos
    if (negativos.some(n => !n.cabe)) for (const n of negativos) { n.t.setAttribute('x', n.x0 + 5); n.t.setAttribute('text-anchor', 'start'); }
    if (o.ref) {
      const xr = r.x(o.ref.v);
      el('line', { x1: xr, x2: xr, y1: (o.topo || 22) - 4, y2: r.alt - 36, class: 'ref' }, r.s);
      texto(r.s, xr, (o.topo || 22) - 9, o.ref.rotulo, { 'text-anchor': 'middle', class: 'rotulo-eixo val-forte' });
    }
    // chinês, japonês e coreano: a unidade por extenso (个百分点) passa da margem direita; refaz com a margem que falta (T44)
    if (/^(zh|ja|ko)/.test(LINGUA) && !o.refeito) {
      const W = +r.s.getAttribute('width');
      const falta = Math.max(0, ...[...r.s.querySelectorAll('text.val')].map(t => { const b = t.getBBox(); return b.x + b.width - W + 2; }));
      if (falta > 0) return barras(caixa, Object.assign({}, o, { margD: (o.margD || 16) + Math.ceil(falta), refeito: true }));
    }
    return r;
  }

  /** 4. Coeficientes com intervalo de 95% (um por linha), com a linha do zero.
   *  o: {linhas: [{nome, v, ic: [a, b], destaque, dica} | {grupo}], x, lados: [esq, dir], aria} */
  function coeficientes(caixa, o) {
    return linhasBase(caixa, Object.assign({ topo: 30 }, o), (s, l, x, y0, yc) => {
      el('line', { x1: x(limita(l.ic[0], o.x.min, o.x.max)), x2: x(limita(l.ic[1], o.x.min, o.x.max)), y1: yc, y2: yc, class: 'ic' }, s);
      for (const v of l.ic) if (v >= o.x.min && v <= o.x.max) el('line', { x1: x(v), x2: x(v), y1: yc - 4, y2: yc + 4, class: 'ic' }, s);
      el('circle', { cx: x(limita(l.v, o.x.min, o.x.max)), cy: yc, r: l.destaque ? 5 : 4, class: 'pt-anel p-ink' }, s);
    });
  }

  /** 4b. Coeficientes de uma ou duas séries por linha (T34: o Lula e o Flávio no mesmo gráfico), cada uma com o
   *  intervalo de 95%; ponto cheio onde o teste deu associação, anel vazio onde não deu (a legenda diz isso).
   *  o: {linhas: [{nome, curto, vals: [{lado, v, ic, cheio}], dica}], x, lados: [esq, dir], aria} */
  function coeficientesPar(caixa, o) {
    const duas = o.linhas.some(l => l.vals && l.vals.length > 1);
    return linhasBase(caixa, Object.assign({ topo: 30, altLinha: duas ? 30 : 22 }, o), (s, l, x, y0, yc) => {
      l.vals.forEach((v, i) => {
        const y = duas ? yc + (i ? 5 : -5) : yc;
        const a = x(limita(v.ic[0], o.x.min, o.x.max)), b = x(limita(v.ic[1], o.x.min, o.x.max));
        el('line', { x1: a, x2: b, y1: y, y2: y, class: 'ic ic-' + v.lado + (v.cheio ? '' : ' ic-fraco') }, s);
        el('circle', { cx: x(limita(v.v, o.x.min, o.x.max)), cy: y, r: 4.5,
          class: v.cheio ? 'pt-anel p-' + v.lado : 'pt-vazio s-' + v.lado }, s);
      });
    });
  }

  /** 5. Divisão de 100% entre os dois (estimativa), com o intervalo de 95% na fronteira.
   *  o: {linhas: [{nome, curto, lula (0 a 1), ic: [a, b], naoDeu, marca, destaque, dica} | {grupo}], aria} */
  function divisao(caixa, o) {
    const oo = Object.assign({ x: { min: 0, max: 1, passo: 0.25, fmt: v => fmt.comPct(nf(v * 100, 0)), rotulo: o.rotuloX }, altLinha: 24, topo: 26, base: o.linhas.length > 12 ? 58 : 0 }, o);
    const r = linhasBase(caixa, oo, (s, l, x, y0, yc, lh, estreito) => {
      const bh = Math.min(16, lh - 4), yb = yc - bh / 2;
      if (l.naoDeu) {
        el('rect', { x: x(0), y: yb, width: x(1) - x(0), height: bh, rx: 3, class: 'trilho' }, s);
        texto(s, x(0) + 8, yc + 4, estreito ? T('g.nao_deu_curto') : T('g.nao_deu', { motivo: l.naoDeu }), { class: 'val-sobre-trilho' });
        return;
      }
      const v = limita(l.lula, 0, 1), xm = x(v);
      const incerta = l.ic && l.ic[0] <= 0.5 && l.ic[1] >= 0.5 ? ' barra-incerta' : ''; // o intervalo cruza 50%: sem lado claro (QA, L8)
      if (v > 0) el('rect', { x: x(0), y: yb, width: Math.max(0, xm - x(0) - 1), height: bh, rx: 3, class: 'barra-l' + incerta }, s);
      if (v < 1) el('rect', { x: xm + 1, y: yb, width: Math.max(0, x(1) - xm - 1), height: bh, rx: 3, class: 'barra-f' + incerta }, s);
      const tl = nf(l.lula * 100, 0), tf = nf((1 - l.lula) * 100, 0);
      if (xm - x(0) > 30) texto(s, x(0) + 6, yc + 4, tl, { class: 'val-sobre-l' });
      if (x(1) - xm > 30) texto(s, x(1) - 6, yc + 4, tf, { 'text-anchor': 'end', class: 'val-sobre-f' });
      if (l.ic) {
        const a = x(limita(l.ic[0], 0, 1)), b = x(limita(l.ic[1], 0, 1));
        el('line', { x1: a, x2: b, y1: yc, y2: yc, class: 'ic-sobre' }, s);
        el('line', { x1: a, x2: a, y1: yc - 5, y2: yc + 5, class: 'ic-sobre' }, s);
        el('line', { x1: b, x2: b, y1: yc - 5, y2: yc + 5, class: 'ic-sobre' }, s);
      }
    });
    const xm = r.x(0.5);
    el('line', { x1: xm, x2: xm, y1: (oo.topo) - 4, y2: r.alt - 36, class: 'ref ref-fina' }, r.s);
    texto(r.s, r.x(0), oo.topo - 9, T('g.lado_lula'), { class: 'rotulo-eixo' });
    texto(r.s, r.x(1), oo.topo - 9, T('g.lado_flavio'), { 'text-anchor': 'end', class: 'rotulo-eixo' });
    if (oo.base) { // figura mais alta que a tela: o cabeçalho "← Lula / Flávio →" repete embaixo, junto do eixo (QA nº 17)
      texto(r.s, r.x(0), r.alt - oo.base + 36, T('g.lado_lula'), { class: 'rotulo-eixo' });
      texto(r.s, r.x(1), r.alt - oo.base + 36, T('g.lado_flavio'), { 'text-anchor': 'end', class: 'rotulo-eixo' });
    }
    return r;
  }

  // ---------- 6. Ponte da virada (cascata horizontal) ----------
  /** o: {M1, M2, itens: [{nome, curto, dM, dica}], dica1, dica2, aria} */
  function ponte(caixa, o) {
    const linhas = [{ nome: T('g.turno1'), ini: 0, fim: o.M1, total: true, dica: o.dica1 }];
    let acum = o.M1;
    for (const u of o.itens) { linhas.push({ nome: u.nome, curto: u.curto, ini: acum, fim: acum + u.dM, dica: u.dica }); acum += u.dM; }
    linhas.push({ nome: T('g.turno2'), ini: 0, fim: o.M2, total: true, dica: o.dica2 });
    const larg = caixa.clientWidth, estreito = larg < 520, muitos = linhas.length > 12;
    const lh = muitos ? 21 : 32, bh = muitos ? 13 : 20;
    let margE = estreito && muitos ? 46 : muitos ? 150 : 108;
    const margD = 66, topo = 8, base = 44;
    const alt = topo + linhas.length * lh + base;
    const s = svgNovo(caixa, larg, alt, o.aria, 'group');
    if (estreito) { // o nome mais comprido tem de caber à esquerda da barra, também em outra língua (QA nº 8)
      const largNome = Math.max(...linhas.map(l => {
        const t = texto(s, 0, 0, estreito && muitos && !l.total ? l.curto : l.nome, { class: 'nome-linha val-forte' });
        const w = t.getComputedTextLength(); t.remove(); return w;
      }));
      margE = Math.max(margE, Math.ceil(largNome) + 12);
    }
    const vmin = Math.min(0, ...linhas.map(l => Math.min(l.ini, l.fim)));
    const vmax = Math.max(0, ...linhas.map(l => Math.max(l.ini, l.fim)));
    const x = escala(vmin, vmax, margE, larg - margD);
    const grade = el('g', { class: 'grade' }, s);
    for (const v of ticks(vmin, vmax, 2e6)) {
      el('line', { x1: x(v), x2: x(v), y1: topo, y2: alt - base + 4, class: v === 0 ? 'zero' : '' }, grade);
      const tk = texto(s, x(v), alt - base + 18, v === 0 ? '0' : fmt.mi(v, 0), { 'text-anchor': 'middle', class: 'tick' });
      // em 万 o número fica mais longo (+1500万): o último não passa da borda (T44)
      if (DEZ_MIL && x(v) + tk.getComputedTextLength() / 2 > +s.getAttribute('width')) tk.setAttribute('text-anchor', 'end');
    }
    linhas.forEach((l, i) => {
      const y = topo + i * lh + (lh - bh) / 2;
      const a = Math.min(l.ini, l.fim), b = Math.max(l.ini, l.fim);
      const cls = (l.total ? (l.fim >= 0 ? 'barra-l' : 'barra-f') : (l.fim - l.ini >= 0 ? 'barra-l' : 'barra-f') + ' barra-passo');
      el('rect', { x: x(a), y, width: Math.max(1, x(b) - x(a)), height: bh, rx: 2, class: cls }, s);
      if (i < linhas.length - 1) {
        const prox = topo + (i + 1) * lh + (lh - bh) / 2;
        el('line', { x1: x(l.fim), x2: x(l.fim), y1: y + bh, y2: prox, class: 'conector' }, s);
      }
      const nome = estreito && muitos && !l.total ? l.curto : l.nome;
      texto(s, margE - 8, y + bh / 2 + 4, nome, { 'text-anchor': 'end', class: 'nome-linha' + (l.total ? ' val-forte' : '') });
      const valor = l.total ? fmt.mi(l.fim) : fmt.mi(l.fim - l.ini);
      texto(s, x(b) + 6, y + bh / 2 + 4, valor, { class: 'val' + (l.total ? ' val-forte' : '') });
      if (l.dica) {
        const alvo = el('rect', { x: 0, y: topo + i * lh, width: larg, height: lh, fill: 'transparent', tabindex: 0, class: 'alvo',
          'aria-label': T('g.aria_item', { titulo: l.nome, valores: valor }) }, s);
        ligarDica(alvo, l.nome, l.dica, on => alvo.classList.toggle('ativo', on));
      }
    });
    texto(s, margE, alt - 4, T('g.ponte_eixo'), { class: 'rotulo-eixo' });
  }

  // ---------- 7. Linha da apuração ao vivo (projeção e contagem parcial) ----------
  /** o: {pontos: [{x, proj, parc, hora}], final, buraco: [a, b], refeitas: [{x, proj, parc}] (T42: leituras refeitas
   *  depois, no buraco; em traço curto, fora da dica), y: {min, max, passo}, aria} */
  function linhaApuracao(caixa, o) {
    const larg = caixa.clientWidth;
    const alt = Math.round(Math.max(260, Math.min(340, larg * 0.46)));
    const mE = 44, mD = 14, mT = 22, mB = 44;
    const s = svgNovo(caixa, larg, alt, o.aria);
    const x = escala(0, 100, mE, larg - mD), y = escala(o.y.min, o.y.max, alt - mB, mT);
    if (o.buraco) {
      el('rect', { x: x(o.buraco[0]), y: mT, width: x(o.buraco[1]) - x(o.buraco[0]), height: alt - mB - mT, class: 'buraco' }, s);
      texto(s, (x(o.buraco[0]) + x(o.buraco[1])) / 2, mT + 12, T(o.refeitas ? 'g.refeitas' : 'g.sem_leituras'), { 'text-anchor': 'middle', class: 'tick' });
    }
    const grade = el('g', { class: 'grade' }, s);
    for (const v of ticks(o.y.min, o.y.max, o.y.passo)) {
      el('line', { x1: mE, x2: larg - mD, y1: y(v), y2: y(v), class: v === 50 ? 'zero' : '' }, grade);
      texto(s, mE - 6, y(v) + 4, fmt.comPct(nf(v, 0)), { 'text-anchor': 'end', class: 'tick' });
    }
    for (const v of ticks(0, 100, 25)) texto(s, x(v), alt - mB + 18, fmt.comPct(nf(v, 0)), { 'text-anchor': v === 0 ? 'start' : v === 100 ? 'end' : 'middle', class: 'tick' });
    texto(s, mE, alt - 6, T('g.eixo_apurado'), { class: 'rotulo-eixo' });
    texto(s, 0, 12, T('g.eixo_fatia'), { class: 'rotulo-eixo' });
    el('line', { x1: mE, x2: larg - mD, y1: y(o.final), y2: y(o.final), class: 'ref' }, s);
    texto(s, x(o.rotuloFinalX || 20), y(o.final) - 7, T('g.resultado_final', { pct: fmt.pct(o.final, 2) }), { class: 'nome-linha val-forte' });
    if (o.y.min < 50 && o.y.max > 50) texto(s, larg - mD, y(50) + 14, T('g.empate', { pct: fmt.comPct(nf(50, 0)) }), { 'text-anchor': 'end', class: 'tick' });
    const caminho = chave => o.pontos.map((p, i) => {
      const quebra = i > 0 && o.buraco && o.pontos[i - 1].x <= o.buraco[0] && p.x >= o.buraco[1];
      return (i === 0 || quebra ? 'M' : 'L') + x(p.x).toFixed(1) + ' ' + y(p[chave]).toFixed(1);
    }).join('');
    el('path', { d: caminho('parc'), class: 'linha linha-muted' }, s);
    el('path', { d: caminho('proj'), class: 'linha linha-ink' }, s);
    if (o.refeitas && o.buraco) { // o trecho refeito liga a última leitura antes do buraco à primeira depois
      const antes = o.pontos.filter(p => p.x <= o.buraco[0]).pop(), depois = o.pontos.find(p => p.x >= o.buraco[1]);
      const ps = [antes, ...o.refeitas, depois].filter(Boolean);
      for (const [chave, cls] of [['parc', 'linha-muted'], ['proj', 'linha-ink']])
        el('path', { d: ps.map((p, i) => (i ? 'L' : 'M') + x(p.x).toFixed(1) + ' ' + y(p[chave]).toFixed(1)).join(''), class: ['linha', 'linha-refeita', cls].join(' ') }, s);
    }
    if (o.rotulos) { // rótulo direto de cada linha, embaixo dela, no ponto o.rotulos.x (% apurado), onde as duas estão separadas
      const p0 = o.pontos.reduce((a, q) => (Math.abs(q.x - o.rotulos.x) < Math.abs(a.x - o.rotulos.x) ? q : a));
      texto(s, x(p0.x), y(p0.proj) + 17, o.rotulos.proj, { 'text-anchor': 'middle', class: 'nome-linha val-forte' });
      texto(s, x(p0.x), y(p0.parc) + 17, o.rotulos.parc, { 'text-anchor': 'middle', class: 'nome-linha' });
    }
    const ult = o.pontos[o.pontos.length - 1];
    el('circle', { cx: x(ult.x), cy: y(ult.proj), r: 4, class: 'pt-anel p-ink' }, s);
    const cruz = el('line', { y1: mT, y2: alt - mB, class: 'cruz', visibility: 'hidden' }, s);
    const m1 = el('circle', { r: 4, class: 'pt-anel p-ink', visibility: 'hidden' }, s);
    const m2 = el('circle', { r: 4, class: 'pt-anel p-muted', visibility: 'hidden' }, s);
    const alvo = el('rect', { x: mE, y: mT, width: larg - mD - mE, height: alt - mB - mT, fill: 'transparent' }, s);
    const mover = ev => {
      const r = s.getBoundingClientRect(), px = ev.clientX - r.left;
      let p = o.pontos[0];
      for (const q of o.pontos) if (Math.abs(x(q.x) - px) < Math.abs(x(p.x) - px)) p = q;
      for (const [e, yy] of [[m1, y(p.proj)], [m2, y(p.parc)]]) { e.setAttribute('cx', x(p.x)); e.setAttribute('cy', yy); e.setAttribute('visibility', 'visible'); }
      cruz.setAttribute('x1', x(p.x)); cruz.setAttribute('x2', x(p.x)); cruz.setAttribute('visibility', 'visible');
      dicaMostrar(ev.clientX, ev.clientY, T(p.hora ? 'g.dica_apurado_hora' : 'g.dica_apurado', { pct: fmt.pct(p.x, 2), hora: p.hora }), [
        { lado: 'ink', t: T('g.projecao_ao_vivo'), v: T('g.valor_e_erro', { v: fmt.pct(p.proj, 2), erro: fmt.pp(p.proj - o.final) }) },
        { lado: 'muted', t: T('g.contagem_parcial'), v: T('g.valor_e_erro', { v: fmt.pct(p.parc, 2), erro: fmt.pp(p.parc - o.final) }) },
      ]);
    };
    alvo.addEventListener('pointermove', mover);
    alvo.addEventListener('pointerdown', mover);
    alvo.addEventListener('pointerleave', ev => {
      if (ev.pointerType === 'touch') return;
      for (const e of [cruz, m1, m2]) e.setAttribute('visibility', 'hidden');
      dicaEsconder();
    });
  }

  // ---------- 7b. Curvas por % apurado (T42: as projeções refeitas e a regra de chamada, capítulo 7) ----------
  /** o: {series: [{pontos: [{x, y}], cls: 'linha-ink' | 'linha-muted', ponto: 'ink' | 'muted', nome, rotulo: {x, dy, abaixo},
   *      degraus}], x: {min, max, passo, fmt}, y: {min, max, passo, fmt}, rotuloX, rotuloY, ref: {y, texto, x},
   *      dica: xv => {titulo, linhas: [{lado, t, v}]}, aria}. Linhas de 2 px, rótulo direto de cada série, cursor com dica. */
  function curvas(caixa, o) {
    const larg = caixa.clientWidth;
    const alt = Math.round(Math.max(250, Math.min(330, larg * 0.44)));
    const mE = 44, mD = 14, mT = 22, mB = 44;
    const s = svgNovo(caixa, larg, alt, o.aria);
    const x = escala(o.x.min, o.x.max, mE, larg - mD), y = escala(o.y.min, o.y.max, alt - mB, mT);
    const grade = el('g', { class: 'grade' }, s);
    for (const v of ticks(o.y.min, o.y.max, o.y.passo)) {
      el('line', { x1: mE, x2: larg - mD, y1: y(v), y2: y(v) }, grade);
      texto(s, mE - 6, y(v) + 4, o.y.fmt(v), { 'text-anchor': 'end', class: 'tick' });
    }
    for (const v of ticks(o.x.min, o.x.max, o.x.passo))
      texto(s, x(v), alt - mB + 18, o.x.fmt(v), { 'text-anchor': v === o.x.min ? 'start' : v === o.x.max ? 'end' : 'middle', class: 'tick' });
    texto(s, mE, alt - 6, o.rotuloX, { class: 'rotulo-eixo' });
    texto(s, 0, 12, o.rotuloY, { class: 'rotulo-eixo' });
    if (o.ref) {
      el('line', { x1: mE, x2: larg - mD, y1: y(o.ref.y), y2: y(o.ref.y), class: 'ref' }, s);
      texto(s, x(o.ref.x === undefined ? o.x.min : o.ref.x) + 4, y(o.ref.y) - 7, o.ref.texto, { class: 'nome-linha val-forte' });
    }
    const dentro = p => p.x >= o.x.min && p.x <= o.x.max;
    const cy = v => y(limita(v, o.y.min, o.y.max));
    for (const sr of o.series) {
      const ps = sr.pontos.filter(dentro);
      const d = ps.map((p, i) => (i ? (sr.degraus ? 'H' + x(p.x).toFixed(1) + 'V' : 'L' + x(p.x).toFixed(1) + ' ') : 'M' + x(p.x).toFixed(1) + ' ') + cy(p.y).toFixed(1)).join('');
      el('path', { d, class: 'linha ' + sr.cls }, s);
      if (sr.rotulo) {
        const p0 = ps.reduce((a, q) => (Math.abs(q.x - sr.rotulo.x) < Math.abs(a.x - sr.rotulo.x) ? q : a));
        const t = texto(s, x(p0.x), cy(p0.y) + (sr.rotulo.dy || (sr.rotulo.abaixo ? 17 : -9)), sr.nome,
          { 'text-anchor': 'middle', class: 'nome-linha' + (sr.ponto === 'ink' ? ' val-forte' : '') });
        const w = t.getComputedTextLength(), px = +t.getAttribute('x');
        if (px - w / 2 < mE + 2) t.setAttribute('x', mE + 2 + w / 2);
        else if (px + w / 2 > larg - mD) t.setAttribute('x', larg - mD - w / 2);
      }
    }
    if (!o.dica) return;
    const cruz = el('line', { y1: mT, y2: alt - mB, class: 'cruz', visibility: 'hidden' }, s);
    const aneis = o.series.map(sr => el('circle', { r: 4, class: 'pt-anel p-' + (sr.ponto || 'ink'), visibility: 'hidden' }, s));
    const alvo = el('rect', { x: mE, y: mT, width: larg - mD - mE, height: alt - mB - mT, fill: 'transparent' }, s);
    const valorEm = (sr, xv) => { // o valor da série no x (degrau: o último ponto até x; linha: o ponto mais perto)
      const ps = sr.pontos.filter(dentro);
      if (sr.degraus) { let v = null; for (const p of ps) if (p.x <= xv + 1e-9) v = p.y; return v; }
      return ps.reduce((a, q) => (Math.abs(q.x - xv) < Math.abs(a.x - xv) ? q : a)).y;
    };
    const mover = ev => {
      const r = s.getBoundingClientRect();
      const xv = limita(o.x.min + (ev.clientX - r.left - mE) / (larg - mD - mE) * (o.x.max - o.x.min), o.x.min, o.x.max);
      const xs = o.passoDica ? Math.max(o.x.min, Math.round(xv / o.passoDica) * o.passoDica) : xv;
      cruz.setAttribute('x1', x(xs)); cruz.setAttribute('x2', x(xs)); cruz.setAttribute('visibility', 'visible');
      o.series.forEach((sr, k) => {
        const v = valorEm(sr, xs);
        aneis[k].setAttribute('visibility', v === null ? 'hidden' : 'visible');
        if (v !== null) { aneis[k].setAttribute('cx', x(xs)); aneis[k].setAttribute('cy', cy(v)); }
      });
      const d = o.dica(xs);
      dicaMostrar(ev.clientX, ev.clientY, d.titulo, d.linhas);
    };
    alvo.addEventListener('pointermove', mover);
    alvo.addEventListener('pointerdown', mover);
    alvo.addEventListener('pointerleave', ev => {
      if (ev.pointerType === 'touch') return;
      for (const e of [cruz, ...aneis]) e.setAttribute('visibility', 'hidden');
      dicaEsconder();
    });
  }

  // ---------- 8. Funil: variação esperada pelo tamanho do município ----------
  /** o: {curva: {eleitorado, lim95, lim998}, centro, pontos: [{E, v, titulo, linhas}], y: {min, max, passo, fmt, rotulo},
   *      ladoAcima, ladoAbaixo, aria} */
  function funil(caixa, o) {
    const larg = caixa.clientWidth;
    const alt = Math.round(Math.max(260, Math.min(340, larg * 0.48)));
    const mE = 44, mD = 12, mT = 24, mB = 44;
    const s = svgNovo(caixa, larg, alt, o.aria);
    const E = o.curva.eleitorado, lx0 = Math.log10(E[0]), lx1 = Math.log10(E[E.length - 1]);
    const x = v => mE + (Math.log10(v) - lx0) / (lx1 - lx0) * (larg - mE - mD);
    const yb = escala(o.y.min, o.y.max, alt - mB, mT), y = v => yb(limita(v, o.y.min, o.y.max));
    const area = (lim, cls) => {
      const sup = E.map((e, i) => x(e).toFixed(1) + ' ' + y(lim[i][1]).toFixed(1));
      const inf = E.map((e, i) => x(e).toFixed(1) + ' ' + y(lim[i][0]).toFixed(1)).reverse();
      el('path', { d: 'M' + sup.join('L') + 'L' + inf.join('L') + 'Z', class: cls }, s);
    };
    area(o.curva.lim998, 'faixa-998');
    area(o.curva.lim95, 'faixa-95');
    const grade = el('g', { class: 'grade' }, s);
    for (const v of ticks(o.y.min, o.y.max, o.y.passo)) {
      el('line', { x1: mE, x2: larg - mD, y1: y(v), y2: y(v), class: Math.abs(v) < 1e-9 ? 'zero' : '' }, grade);
      texto(s, mE - 6, y(v) + 4, o.y.fmt(v), { 'text-anchor': 'end', class: 'tick' });
    }
    for (const v of [1e3, 1e4, 1e5, 1e6, 1e7]) {
      if (v < E[0] || v > E[E.length - 1]) continue;
      texto(s, x(v), alt - mB + 18, v >= 1e6 ? fmt.miCurto(v, 0) : fmt.mil(v, 0), { 'text-anchor': 'middle', class: 'tick' });
    }
    texto(s, mE, alt - 6, T('g.eixo_eleitorado'), { class: 'rotulo-eixo' });
    texto(s, 0, 12, o.y.rotulo, { class: 'rotulo-eixo' });
    el('line', { x1: mE, x2: larg - mD, y1: y(o.centro), y2: y(o.centro), class: 'ref ref-fina' }, s);
    const pts = [];
    const lim = (e, k) => { // interpolação da faixa no eleitorado e (log)
      const le = Math.log10(e);
      let i = 0;
      while (i < E.length - 2 && Math.log10(E[i + 1]) < le) i++;
      const t = limita((le - Math.log10(E[i])) / (Math.log10(E[i + 1]) - Math.log10(E[i])), 0, 1);
      return [0, 1].map(j => o.curva[k][i][j] + t * (o.curva[k][i + 1][j] - o.curva[k][i][j]));
    };
    const g = el('g', {}, s);
    for (const p of o.pontos) {
      const f = lim(p.E, 'lim998');
      const lado = p.v > f[1] ? o.ladoAcima : p.v < f[0] ? o.ladoAbaixo : null;
      p.px = x(limita(p.E, E[0], E[E.length - 1])); p.py = y(p.v);
      el('circle', { cx: p.px.toFixed(1), cy: p.py.toFixed(1), r: lado ? 2.4 : 1.6, class: lado ? 'ponto-fora p-' + lado : 'ponto-dentro' }, g);
      pts.push(p);
    }
    const anel = el('circle', { r: 0, class: 'anel', visibility: 'hidden' }, s);
    const mover = ev => {
      const r = s.getBoundingClientRect(), px = ev.clientX - r.left, py = ev.clientY - r.top;
      let melhor = null, dist = 14;
      for (const p of pts) { const d = Math.hypot(p.px - px, p.py - py); if (d < dist) { dist = d; melhor = p; } }
      if (!melhor) { anel.setAttribute('visibility', 'hidden'); dicaEsconder(); return; }
      anel.setAttribute('cx', melhor.px); anel.setAttribute('cy', melhor.py); anel.setAttribute('r', 5); anel.setAttribute('visibility', 'visible');
      const f95 = lim(melhor.E, 'lim95'), f998 = lim(melhor.E, 'lim998');
      dicaMostrar(ev.clientX, ev.clientY, melhor.titulo, melhor.linhas.concat([
        { t: T('g.faixa95'), v: T('g.de_a', { a: o.y.fmt(f95[0]), b: o.y.fmt(f95[1]) }) },
        { t: T('g.faixa998', { pct: fmt.pct(99.8, 1) }), v: T('g.de_a', { a: o.y.fmt(f998[0]), b: o.y.fmt(f998[1]) }) }]));
    };
    s.addEventListener('pointermove', mover);
    s.addEventListener('pointerdown', mover);
    s.addEventListener('pointerleave', ev => { if (ev.pointerType !== 'touch') { anel.setAttribute('visibility', 'hidden'); dicaEsconder(); } });
  }

  // ---------- 10. A virada: a diferença entre os dois em cada turno, a partir do empate ----------
  /** o: {M1, M2 (Lula − Flávio, em votos), L: [1º, 2º], F: [1º, 2º], colunas: [1º, 2º], fotos: {l, f}, aria}.
   *  Uma coluna por turno, a partir da linha do empate: para cima, o Lula à frente; para baixo, o Flávio.
   *  Ao lado, a régua de quanto a diferença mudou. Substitui as duas linhas de votos que se cruzavam,
   *  porque o cruzamento parecia uma hora da apuração (QA, L9; diário, D69). Lado, cor e nome seguem o
   *  sinal de cada diferença, não o candidato. */
  let clipN = 0;
  function virada(caixa, o) {
    const larg = caixa.clientWidth, estreito = larg < 520;
    const alt = estreito ? 272 : Math.round(limita(larg * 0.66, 300, 360));
    const mT = estreito ? 52 : 58, mB = estreito ? 52 : 58;
    const s = svgNovo(caixa, larg, alt, o.aria, 'group');
    const y = escala(Math.min(0, o.M1, o.M2), Math.max(0, o.M1, o.M2), alt - mB, mT), y0 = y(0);
    const lc = estreito ? 56 : 72;
    const X = [larg * (estreito ? 0.24 : 0.22), larg * (estreito ? 0.5 : 0.48)];
    const xr = larg * (estreito ? 0.66 : 0.64); // a régua da mudança
    const M = [o.M1, o.M2];
    const lado = v => (v >= 0 ? 'l' : 'f');
    const defs = el('defs', {}, s);

    // a linha do empate, até a régua
    el('line', { x1: 0, x2: xr - 8, y1: y0, y2: y0, class: 'linha-empate' }, s);
    texto(s, 0, y0 - 7, T('res.virada_empate'), { class: 'tick' });

    // as colunas: ponta arredondada só do lado de fora, a base presa no empate (dataviz)
    M.forEach((v, i) => {
      const x0 = X[i] - lc / 2, x1 = X[i] + lc / 2, b = y(v), r = 4, sobe = b < y0;
      const k = sobe ? r : -r;
      el('path', { d: `M${x0} ${y0}V${b + k}Q${x0} ${b} ${x0 + r} ${b}H${x1 - r}Q${x1} ${b} ${x1} ${b + k}V${y0}Z`, class: 'barra-' + lado(v) }, s);
      // o nome do turno no lado vazio do empate, sobre a base da coluna
      texto(s, X[i], sobe ? y0 + 20 : y0 - 9, o.colunas[i], { 'text-anchor': 'middle', class: 'cab-col' });
      // quem ficou à frente, e por quanto, na ponta da coluna
      const ty = sobe ? b - 30 : b + 24;
      const tx = x0;
      if (!estreito && o.fotos) {
        const id = 'clip-virada-' + (++clipN), cy = ty + 4;
        el('circle', { cx: x0 - 22, cy, r: 16 }, el('clipPath', { id }, defs));
        el('image', { href: o.fotos[lado(v)], x: x0 - 38, y: cy - 16, width: 32, height: 32, 'clip-path': `url(#${id})`,
          preserveAspectRatio: 'xMidYMin slice' }, s);
      }
      const quem = T(v >= 0 ? 'g.lula_a_frente' : 'g.flavio_a_frente');
      texto(s, tx, ty, T('res.virada_por', { quem }), { class: 'nome-linha' });
      texto(s, tx, ty + 20, fmt.miAbs(Math.abs(v)), { class: 'nome-serie' });
      // dica e leitor de tela: os votos de cada um no turno
      const alvo = el('rect', { x: x0 - 6, y: Math.min(b, y0) - 6, width: lc + 12, height: Math.abs(b - y0) + 12, fill: 'transparent', tabindex: 0, class: 'alvo',
        'aria-label': T('res.virada_col_aria', { turno: o.colunas[i], quem, n: fmt.int(Math.abs(v)), l: fmt.int(o.L[i]), f: fmt.int(o.F[i]) }) }, s);
      ligarDica(alvo, o.colunas[i], [{ lado: 'l', t: T('nome.lula'), v: fmt.int(o.L[i]) }, { lado: 'f', t: T('nome.flavio'), v: fmt.int(o.F[i]) },
        { t: T('res.fita_diferenca'), v: fmt.intSinal(v) }]);
    });

    // a régua: de uma diferença à outra, com as guias até a ponta de cada coluna e a seta do sentido da mudança
    const [ya, yb] = [y(o.M1), y(o.M2)], sobe = yb < ya, p = sobe ? 1 : -1;
    M.forEach((v, i) => el('line', { x1: X[i] + lc / 2 + 4, x2: xr + 5, y1: y(v), y2: y(v), class: 'guia-medida' }, s));
    el('line', { x1: xr, x2: xr, y1: ya, y2: yb + p * 6, class: 'medida' }, s);
    el('line', { x1: xr - 5, x2: xr + 5, y1: ya, y2: ya, class: 'medida' }, s);
    el('path', { d: `M${xr - 5} ${yb + p * 8}L${xr} ${yb}L${xr + 5} ${yb + p * 8}Z`, class: 'medida-ponta' }, s);
    const linhas = T('res.virada_mudou'), meio = (ya + yb) / 2 - (linhas.length * 18) / 2 + 4;
    linhas.forEach((l, i) => texto(s, xr + 12, meio + i * 18, l, { class: 'nome-linha' }));
    texto(s, xr + 12, meio + linhas.length * 18 + 4, fmt.miAbs(Math.abs(o.M2 - o.M1)), { class: 'nome-serie' });
    return '';
  }

  // ---------- 11. Escalas de cor do mapa (T24): interpoladas em OKLab a partir das variáveis do CSS ----------
  function hexRgb(hx) {
    hx = hx.replace('#', '');
    if (hx.length === 3) hx = hx.split('').map(c => c + c).join('');
    return [0, 2, 4].map(i => parseInt(hx.slice(i, i + 2), 16) / 255);
  }
  const lin = c => (c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4));
  const delin = c => (c <= 0.0031308 ? 12.92 * c : 1.055 * Math.pow(c, 1 / 2.4) - 0.055);
  function oklab(hx) {
    const [r, g, b] = hexRgb(hx).map(lin);
    const l = Math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b);
    const m = Math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b);
    const s = Math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b);
    return [0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
      1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
      0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s];
  }
  function rgbHex([L, a, b]) {
    const l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3;
    const m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3;
    const s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3;
    return '#' + [4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
      -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
      -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s]
      .map(c => Math.round(limita(delin(c), 0, 1) * 255).toString(16).padStart(2, '0')).join('');
  }
  const mistura = (a, b, k) => rgbHex(a.map((v, i) => v + (b[i] - v) * k));
  /** Divergente (dataviz): t de −1 (azul, Flávio) a +1 (vermelho, Lula), com o cinza claro no meio (50%). */
  function escalaDivergente() {
    const n = oklab(css('--neutro')), l = oklab(css('--lula')), f = oklab(css('--flavio'));
    return t => { t = limita(t, -1, 1); return mistura(n, t >= 0 ? l : f, Math.pow(Math.abs(t), 0.85)); };
  }
  /** Sequencial de um tom só, sem cor de candidato: t de 0 (claro) a 1 (escuro); no modo escuro, ao contrário. */
  function escalaSequencial() {
    const a = oklab(css('--seq-0')), b = oklab(css('--seq-1'));
    return t => mistura(a, b, limita(t, 0, 1));
  }

  // ---------- 12. Mapa dos estados (malha do IBGE em mapa.js) ----------
  /** o: {forma: {largura, altura, caminhos}, ufs: [{codigo, nome}], cor: u => cor, hachura: u => bool,
   *      dica: u => {titulo, linhas}, aoDestacar: codigo | null, aoEscolher: codigo, aria, largMax}.
   *  Devolve {pintar(), destacar(codigo)}: pintar() troca só as cores, e o CSS anima a troca. */
  let hachN = 0;
  function mapa(caixa, o) {
    const M = o.forma, larg = Math.min(caixa.clientWidth, o.largMax || 600), alt = Math.round(larg * M.altura / M.largura);
    caixa.replaceChildren();
    const s = el('svg', { width: larg, height: alt, viewBox: `0 0 ${M.largura} ${M.altura}`, role: 'group', 'aria-label': o.aria }, caixa);
    marcarDica(s);
    const id = 'hachura-' + (++hachN);
    const pat = el('pattern', { id, patternUnits: 'userSpaceOnUse', width: 9, height: 9, patternTransform: 'rotate(45)' }, el('defs', {}, s));
    el('line', { x1: 0, y1: 0, x2: 0, y2: 9, class: 'hachura-linha' }, pat);
    const gUf = el('g', {}, s), gHach = el('g', { 'pointer-events': 'none' }, s);
    const contorno = el('path', { class: 'uf-contorno', visibility: 'hidden' }, s);
    const ufs = o.ufs.slice().sort((a, b) => (a.codigo === 'DF') - (b.codigo === 'DF')); // o DF por cima de Goiás
    const caminhos = {}, hach = {};
    for (const u of ufs) {
      const p = el('path', { d: M.caminhos[u.codigo], class: 'uf', tabindex: 0, role: 'img' }, gUf);
      caminhos[u.codigo] = p;
      hach[u.codigo] = el('path', { d: M.caminhos[u.codigo], fill: `url(#${id})`, visibility: 'hidden' }, gHach);
      const mostra = ev => {
        const d = o.dica(u);
        if (ev && ev.clientX !== undefined && ev.pointerType !== 'touch') dicaMostrar(ev.clientX, ev.clientY, d.titulo, d.linhas);
        else dicaNoElemento(p, d.titulo, d.linhas);
        if (o.aoDestacar) o.aoDestacar(u.codigo);
      };
      const sai = () => { dicaEsconder(); if (o.aoDestacar) o.aoDestacar(null); };
      p.addEventListener('pointermove', mostra);
      p.addEventListener('focus', () => mostra());
      p.addEventListener('click', ev => { ev.stopPropagation(); mostra(ev); if (o.aoEscolher) o.aoEscolher(u.codigo); });
      p.addEventListener('keydown', ev => { if ((ev.key === 'Enter' || ev.key === ' ') && o.aoEscolher) { ev.preventDefault(); o.aoEscolher(u.codigo); } });
      p.addEventListener('pointerleave', ev => { if (ev.pointerType !== 'touch') sai(); });
      p.addEventListener('blur', sai);
    }
    const api = {
      pintar() {
        for (const u of ufs) {
          caminhos[u.codigo].style.fill = o.cor(u);
          hach[u.codigo].setAttribute('visibility', o.hachura && o.hachura(u) ? 'visible' : 'hidden');
          const d = o.dica(u);
          caminhos[u.codigo].setAttribute('aria-label', rotuloAria(d.titulo, d.linhas));
        }
      },
      destacar(cod) {
        if (!cod) { contorno.setAttribute('visibility', 'hidden'); return; }
        contorno.setAttribute('d', M.caminhos[cod]);
        contorno.setAttribute('visibility', 'visible');
      },
    };
    api.pintar();
    return api;
  }
  /** Legenda de cor do mapa: a faixa contínua com as marcas. o: {dom: [a, b], cor: v => cor, marcas: [[v, texto]],
   *  esq, dir, hachura: texto} */
  function legendaCor(caixa, o) {
    const larg = Math.min(caixa.clientWidth || 300, 360), alt = 52;
    const s = svgNovo(caixa, larg, alt, T('g.legenda_mapa'));
    const gid = 'grad-' + (++hachN);
    const g = el('linearGradient', { id: gid }, el('defs', {}, s));
    for (let i = 0; i <= 20; i++) el('stop', { offset: (i * 5) + '%', 'stop-color': o.cor(o.dom[0] + (o.dom[1] - o.dom[0]) * i / 20) }, g);
    const x0 = 6, x1 = larg - 6, X = escala(o.dom[0], o.dom[1], x0, x1);
    el('rect', { x: x0, y: 20, width: x1 - x0, height: 10, fill: `url(#${gid})` }, s);
    o.marcas.forEach(([v, t], i) => {
      el('line', { x1: X(v), x2: X(v), y1: 30, y2: 35, class: 'ref-fina' }, s);
      texto(s, X(v), 47, t, { 'text-anchor': i === 0 ? 'start' : i === o.marcas.length - 1 ? 'end' : 'middle', class: 'tick' });
    });
    texto(s, x0, 12, T('g.seta_esq', { t: o.esq }), { class: 'rotulo-eixo' });
    texto(s, x1, 12, T('g.seta_dir', { t: o.dir }), { class: 'rotulo-eixo', 'text-anchor': 'end' });
  }

  // ---------- 9. Tabela ordenável ----------
  /** o: {legenda, colunas: [{t, v: linha => valor, f: valor => texto, num, abbr}], linhas, ordem: {col, desc},
   *      ordenavel, destaque: linha => bool, aoLinha: (tr, linha) => void} */
  function tabela(pai, o) {
    if (o.grafico) pai = vistaDupla(pai, o);
    const caixa = h('div', 'tab-caixa', undefined, pai);
    const t = h('table', 'tab', undefined, caixa);
    if (o.legenda) {
      const c = h('caption', '', undefined, t);
      if (o.legenda.n) h('span', 'fig-n', o.legenda.n + '. ', c);
      c.append(o.legenda.t);
    }
    const thead = h('thead', '', undefined, t), tr = h('tr', '', undefined, thead), tbody = h('tbody', '', undefined, t);
    let ordem = o.ordem ? Object.assign({}, o.ordem) : null;
    const ths = o.colunas.map((c, i) => {
      const th = h('th', c.num ? 'num' : '', undefined, tr);
      th.scope = 'col';
      if (o.ordenavel === false) { th.textContent = c.t; return th; }
      const b = h('button', 'ordenar', c.t, th);
      b.type = 'button';
      b.addEventListener('click', () => {
        ordem = { col: i, desc: ordem && ordem.col === i ? !ordem.desc : !!c.num };
        render();
      });
      return th;
    });
    function render() {
      let ls = o.linhas.slice();
      if (ordem) {
        const c = o.colunas[ordem.col];
        ls.sort((a, b) => {
          const va = c.v(a), vb = c.v(b);
          if (va === null || va === undefined) return 1;
          if (vb === null || vb === undefined) return -1;
          const r = typeof va === 'string' ? va.localeCompare(vb, LINGUA) : va - vb;
          return ordem.desc ? -r : r;
        });
      }
      ths.forEach((th, i) => th.setAttribute('aria-sort', ordem && ordem.col === i ? (ordem.desc ? 'descending' : 'ascending') : 'none'));
      tbody.replaceChildren();
      for (const l of ls) {
        const r = h('tr', o.destaque && o.destaque(l) ? 'destaque' : '', undefined, tbody);
        o.colunas.forEach((c, i) => {
          const v = c.v(l);
          const td = h(i === 0 ? 'th' : 'td', c.num ? 'num' : '', c.f ? c.f(v, l) : (v === null || v === undefined ? VAZIO : v), r);
          if (i === 0) td.scope = 'row';
        });
        if (o.aoLinha) o.aoLinha(r, l);
      }
    }
    render();
    if (o.grafico) { caixa.querySelector('caption').className = 'sr'; alternar(pai.querySelector('.vd-botoes'), pai.querySelector('.vd-grafico'), caixa); }
    return caixa;
  }

  // ---------- 9b. Gráfico primeiro, a mesma informação em tabela a um clique (T36, D83) ----------
  /** Monta o título, a legenda e o gráfico de uma tabela (o.grafico: {desenhar, legenda, sub}); a tabela vem
   *  logo depois, na aba "Tabela". O título fica fora das abas, à vista com qualquer uma. */
  const observadores = [];
  function vistaDupla(pai, o) {
    const g = o.grafico, vd = h('div', 'vd', undefined, pai);
    const tit = h('p', 'vd-tit', undefined, vd);
    if (o.legenda.n) h('span', 'fig-n', o.legenda.n + '. ', tit);
    tit.append(o.legenda.t);
    h('div', 'botoes-escolha vd-botoes', undefined, vd);
    const pg = h('div', 'vd-grafico', undefined, vd);
    if (g.sub) h('p', 'vd-sub', g.sub, pg);
    if (g.legenda) legenda(pg, g.legenda);
    const cx = h('div', 'grafico', undefined, pg);
    let ultima = -1;
    const ro = new ResizeObserver(() => {
      const w = Math.round(cx.clientWidth);
      if (w > 0 && w !== ultima) { ultima = w; dicaEsconder(); g.desenhar(cx); }
    });
    ro.observe(cx);
    observadores.push(ro); // guardado: um observador sem referência pode ser recolhido e o gráfico não sai
    return vd;
  }
  /** Os botões "Gráfico | Tabela" em botoes (um div vazio), trocando entre os dois painéis. A tabela escondida
   *  fica no DOM com hidden="until-found": a busca do navegador (Ctrl+F) acha o número e abre a aba sozinha;
   *  o PDF e a impressão mostram os dois (pdf.js). Também junta uma tabela a uma figura que já existe. */
  function alternar(botoes, painelG, painelT) {
    botoes.setAttribute('role', 'group');
    botoes.setAttribute('aria-label', T('vd.escolha'));
    const paineis = [painelG, painelT];
    const bs = [T('vd.grafico'), T('vd.tabela')].map((t, i) => {
      const b = h('button', '', t, botoes);
      b.type = 'button';
      b.addEventListener('click', () => mostrar(i));
      return b;
    });
    function mostrar(i) {
      paineis.forEach((p, j) => { if (j === i) p.removeAttribute('hidden'); else if (j) p.setAttribute('hidden', 'until-found'); else p.hidden = true; });
      bs.forEach((b, j) => b.setAttribute('aria-pressed', j === i ? 'true' : 'false'));
      dicaEsconder();
    }
    painelT.addEventListener('beforematch', () => mostrar(1));
    mostrar(0);
    return { mostrar };
  }
  /** Junta uma tabela já montada (a caixa que tabela() devolve) a uma figura com gráfico: os botões vão logo
   *  acima do gráfico, e a tabela entra na figura, no lugar do gráfico, antes do rodapé. */
  function juntar(fig, tabCaixa) {
    const g = fig.querySelector(':scope > .grafico'), rod = fig.querySelector(':scope > .fig-rodape');
    const pg = h('div', 'vd-grafico');
    const leg = fig.querySelector(':scope > .legenda');
    fig.insertBefore(pg, leg || g);
    if (leg) pg.appendChild(leg);
    pg.appendChild(g);
    const botoes = h('div', 'botoes-escolha vd-botoes');
    fig.insertBefore(botoes, pg);
    fig.insertBefore(tabCaixa, rod);
    fig.classList.add('vd-junta');
    return alternar(botoes, pg, tabCaixa);
  }

  // ---------- 9c. Mapa de calor (T36): uma cor de um tom só pela intensidade, o número escrito na célula ----------
  /** o: {linhas: [{nome, curto}], colunas: [{nome, curto}], cel: (i, j) => {t (0 a 1), rotulo, dica: {titulo, linhas}} | null,
   *      aria, margE, margEstreito}. Sem cor de candidato: a cor só diz "quanto", e o número diz o resto. */
  function calor(caixa, o) {
    const larg = caixa.clientWidth, estreito = larg < 520;
    const nomeL = l => (estreito && l.curto ? l.curto : l.nome);
    const s = svgNovo(caixa, larg, 10, o.aria, 'group');
    // a margem cabe o nome mais comprido, também em outra língua; no máximo 45% da largura
    const mede = t => { const e = texto(s, 0, 0, t, { class: 'nome-linha' }), w = e.getComputedTextLength(); e.remove(); return w; };
    const margE = Math.min(Math.ceil(Math.max(...o.linhas.map(l => mede(nomeL(l))))) + 12, larg * 0.45);
    const nc = o.colunas.length, cw = Math.min(84, (larg - margE) / nc), ch = estreito ? 30 : 34;
    // o nome da coluna quebra em linhas quando não cabe na largura da coluna
    const cab = o.colunas.map(c => {
      const ls = [];
      for (const p of (estreito && c.curto ? c.curto : c.nome).split(' ')) {
        if (ls.length && mede(ls[ls.length - 1] + ' ' + p) <= cw - 4) ls[ls.length - 1] += ' ' + p; else ls.push(p);
      }
      return ls;
    });
    const topo = 14 + 16 * Math.max(...cab.map(ls => ls.length));
    const alt = topo + o.linhas.length * ch + 8;
    s.setAttribute('height', alt); s.setAttribute('viewBox', `0 0 ${larg} ${alt}`);
    const seq = escalaSequencial(), tinta = css('--ink'), fundo = css('--bg');
    cab.forEach((ls, j) => ls.forEach((t, k) => texto(s, limita(margE + j * cw + cw / 2, mede(t) / 2, larg - mede(t) / 2 - 2), topo - 10 - 16 * (ls.length - 1 - k), t,
      { 'text-anchor': 'middle', class: 'nome-linha' })));
    o.linhas.forEach((l, i) => {
      const y = topo + i * ch;
      texto(s, margE - 8, y + ch / 2 + 4, nomeL(l), { 'text-anchor': 'end', class: 'nome-linha' });
      for (let j = 0; j < nc; j++) {
        const c = o.cel(i, j);
        if (!c) continue;
        const x = margE + j * cw, t = limita(c.t, 0, 1);
        el('rect', { x: x + 1, y: y + 1, width: cw - 2, height: ch - 2, rx: 3, style: 'fill:' + seq(t) }, s);
        // o número em tinta clara sobre a cor forte e em tinta escura sobre a clara, nos dois temas
        texto(s, x + cw / 2, y + ch / 2 + 4, c.rotulo, { 'text-anchor': 'middle', class: 'val-calor', style: 'fill:' + (t > 0.55 ? fundo : tinta) });
        if (c.dica) {
          const alvo = el('rect', { x, y, width: cw, height: ch, fill: 'transparent', tabindex: 0, class: 'alvo',
            'aria-label': rotuloAria(c.dica.titulo, c.dica.linhas) }, s);
          ligarDica(alvo, c.dica.titulo, c.dica.linhas, on => alvo.classList.toggle('ativo', on));
        }
      }
    });
  }

  // ---------- 13. As leituras da apuração ao vivo (T28): linhas por % apurado, com a leitura escolhida ----------
  /** o: {series: [{pontos: [{x, y}], cls, ponto: 'ink' | 'muted', quebra, refeitas: [{x, y}] (T42: leituras refeitas depois, no
   *      buraco, em traço curto e fora do cursor), rotulo: {x, texto, curto (no celular), abaixo, dy}}],
   *      faixa: [i, j] (duas séries com os mesmos x), faixaPontos: [{x, lo, hi}], leituras: [x], atual, y: {min, max, passo}, buraco: [a, b],
   *      marcos: [{x, y, texto, curto (no celular), dy}], dica: i => {titulo, linhas}, rotuloCursor: i => texto,
   *      aoApontar: i | null => void, aoEscolher: i => void, aria}.
   *  A régua embaixo do eixo tem um traço por leitura. Devolve {marcar(i), mE, mD}: marcar move o
   *  cursor sem redesenhar (a mesma leitura nas duas figuras e na fita). */
  function leiturasApuracao(caixa, o) {
    const larg = caixa.clientWidth;
    const alt = Math.round(Math.max(270, Math.min(350, larg * 0.48)));
    const mE = 44, mD = 16, mT = 46, mB = 60;
    const s = svgNovo(caixa, larg, alt, o.aria);
    const x = escala(0, 100, mE, larg - mD), y = escala(o.y.min, o.y.max, alt - mB, mT);
    const base = alt - mB;
    const comZonas = o.y.min < 50 && o.y.max > 50;
    if (comZonas) { // fundo em tom claro: acima de 50%, o Lula à frente; abaixo, o Flávio (revisão do autor, D39)
      el('rect', { x: mE, y: mT, width: larg - mD - mE, height: y(50) - mT, class: 'zona-l' }, s);
      el('rect', { x: mE, y: y(50), width: larg - mD - mE, height: base - y(50), class: 'zona-f' }, s);
    }
    if (o.buraco) {
      el('rect', { x: x(o.buraco[0]), y: mT, width: x(o.buraco[1]) - x(o.buraco[0]), height: base - mT, class: 'buraco' }, s);
      texto(s, (x(o.buraco[0]) + x(o.buraco[1])) / 2, mT + 12, T(o.series.some(sr => sr.refeitas) ? 'g.refeitas' : 'g.sem_leituras'), { 'text-anchor': 'middle', class: 'tick' });
    }
    const grade = el('g', { class: 'grade' }, s);
    for (const v of ticks(o.y.min, o.y.max, o.y.passo)) {
      el('line', { x1: mE, x2: larg - mD, y1: y(v), y2: y(v), class: v === 50 ? 'zero' : '' }, grade);
      texto(s, mE - 6, y(v) + 4, fmt.comPct(nf(v, 0)), { 'text-anchor': 'end', class: 'tick' });
    }
    for (const v of ticks(0, 100, 25)) texto(s, x(v), base + 18, fmt.comPct(nf(v, 0)), { 'text-anchor': v === 0 ? 'start' : v === 100 ? 'end' : 'middle', class: 'tick' });
    texto(s, mE, base + 38, T('g.eixo_apurado_regua'), { class: 'rotulo-eixo' });
    for (const xv of o.leituras) el('line', { x1: x(xv), x2: x(xv), y1: alt - 8, y2: alt, class: 'regua' }, s);
    texto(s, 0, 12, T('g.eixo_fatia'), { class: 'rotulo-eixo' });
    // trechos contínuos de cada série: o buraco das leituras quebra a linha
    const trechos = sr => {
      const t = [[]];
      sr.pontos.forEach((p, i) => {
        if (i > 0 && sr.quebra && o.buraco && sr.pontos[i - 1].x <= o.buraco[0] && p.x >= o.buraco[1]) t.push([]);
        t[t.length - 1].push(p);
      });
      return t;
    };
    const d = ps => ps.map((p, i) => (i ? 'L' : 'M') + x(p.x).toFixed(1) + ' ' + y(limita(p.y, o.y.min, o.y.max)).toFixed(1)).join('');
    if (o.faixa) {
      const [a, b] = o.faixa.map(i => trechos(o.series[i]));
      a.forEach((ta, k) => el('path', { d: d(ta) + d(b[k].slice().reverse()).replace(/^M/, 'L') + 'Z', class: 'faixa-var' }, s));
    }
    if (o.faixaPontos) { // faixa com os limites dados ponto a ponto ({x, lo, hi}), quebrada no buraco
      const lo = trechos({ quebra: true, pontos: o.faixaPontos.map(p => ({ x: p.x, y: p.lo })) });
      const hi = trechos({ quebra: true, pontos: o.faixaPontos.map(p => ({ x: p.x, y: p.hi })) });
      lo.forEach((tl, k) => el('path', { d: d(hi[k]) + d(tl.slice().reverse()).replace(/^M/, 'L') + 'Z', class: 'faixa-erro' }, s));
    }
    for (const sr of o.series) {
      el('path', { d: trechos(sr).map(d).join(''), class: 'linha ' + sr.cls }, s);
      if (sr.refeitas && o.buraco) { // o trecho refeito liga a última leitura antes do buraco à primeira depois
        const antes = sr.pontos.filter(p => p.x <= o.buraco[0]).pop(), depois = sr.pontos.find(p => p.x >= o.buraco[1]);
        el('path', { d: d([antes, ...sr.refeitas, depois].filter(Boolean)), class: ['linha', 'linha-refeita', sr.cls].join(' ') }, s);
      }
    }
    if (comZonas) {
      texto(s, mE + 6, mT + 14, T('g.lula_a_frente'), { class: 'zona-rot' });
      // o.flavioEsquerda: no canto de baixo à esquerda, longe do rótulo da linha do 1º turno, que fica à direita
      if (o.flavioEsquerda) texto(s, mE + 6, base - 7, T('g.flavio_a_frente'), { class: 'zona-rot' });
      else texto(s, larg - mD - 6, base - 7, T('g.flavio_a_frente'), { 'text-anchor': 'end', class: 'zona-rot' });
    }
    const valorEm = (ps, xv) => {
      if (xv < ps[0].x || xv > ps[ps.length - 1].x) return null;
      let i = 1;
      while (i < ps.length - 1 && ps[i].x < xv) i++;
      const p = ps[i - 1], q = ps[i], t = q.x === p.x ? 0 : (xv - p.x) / (q.x - p.x);
      return p.y + limita(t, 0, 1) * (q.y - p.y);
    };
    const dentro = t => { // texto centrado que não passa das bordas do gráfico
      const w = t.getComputedTextLength(), px = +t.getAttribute('x');
      if (px - w / 2 < mE + 2) t.setAttribute('x', mE + 2 + w / 2);
      else if (px + w / 2 > larg - mD) t.setAttribute('x', larg - mD - w / 2);
      return t;
    };
    for (const sr of o.series) {
      if (!sr.rotulo) continue;
      const v = valorEm(sr.pontos, sr.rotulo.x);
      if (v !== null) dentro(texto(s, x(sr.rotulo.x), y(v) + (sr.rotulo.dy || (sr.rotulo.abaixo ? 18 : -9)), larg < 520 && sr.rotulo.curto ? sr.rotulo.curto : sr.rotulo.texto,
        { 'text-anchor': 'middle', class: 'nome-linha' + (sr.ponto === 'ink' || sr.ponto === 'l' ? ' val-forte' : '') }));
    }
    for (const m of o.marcos || []) { // anotação embaixo do ponto, com um fio até ele; não passa das bordas do gráfico
      const px = x(m.x), py = y(m.y), ty = py + (m.dy || 30);
      el('line', { x1: px, x2: px, y1: ty > py ? py + 5 : py - 5, y2: ty > py ? ty - 13 : ty + 5, class: 'guia' }, s);
      el('circle', { cx: px, cy: py, r: 3.5, class: 'marco' }, s);
      dentro(texto(s, px, ty, larg < 520 && m.curto ? m.curto : m.texto, { 'text-anchor': 'middle', class: 'nome-linha' }));
    }
    // a leitura escolhida: o fio vertical, a hora no alto e um anel em cada linha
    const cur = el('g', { class: 'cursor-leitura' }, s);
    const fio = el('line', { y1: mT - 5, y2: alt, class: 'cursor-fio' }, cur);
    const rot = texto(cur, 0, mT - 11, '', { class: 'val val-forte' });
    const aneis = o.series.map(sr => el('circle', { r: 4.5, class: 'pt-anel p-' + (sr.ponto || 'ink') }, cur));
    function marcar(i) {
      const xv = o.leituras[i], px = x(xv);
      fio.setAttribute('x1', px); fio.setAttribute('x2', px);
      rot.textContent = o.rotuloCursor ? o.rotuloCursor(i) : '';
      rot.setAttribute('x', px);
      rot.setAttribute('text-anchor', px < mE + 40 ? 'start' : px > larg - mD - 40 ? 'end' : 'middle');
      o.series.forEach((sr, k) => {
        const v = valorEm(sr.pontos, xv);
        aneis[k].setAttribute('visibility', v === null ? 'hidden' : 'visible');
        if (v !== null) { aneis[k].setAttribute('cx', px); aneis[k].setAttribute('cy', y(limita(v, o.y.min, o.y.max))); }
      });
    }
    marcar(o.atual);
    const alvo = el('rect', { x: mE, y: mT, width: larg - mD - mE, height: alt - mT, fill: 'transparent', class: 'alvo-leituras' }, s);
    const perto = ev => {
      const px = ev.clientX - s.getBoundingClientRect().left;
      let k = 0;
      o.leituras.forEach((xv, i) => { if (Math.abs(x(xv) - px) < Math.abs(x(o.leituras[k]) - px)) k = i; });
      return k;
    };
    const mostrar = (ev, i) => { if (o.dica) { const c = o.dica(i); dicaMostrar(ev.clientX, ev.clientY, c.titulo, c.linhas); } };
    alvo.addEventListener('pointermove', ev => {
      const i = perto(ev);
      if (ev.pointerType === 'touch') return;
      if (o.aoApontar) o.aoApontar(i);
      mostrar(ev, i);
    });
    alvo.addEventListener('pointerdown', ev => { const i = perto(ev); if (o.aoEscolher) o.aoEscolher(i); mostrar(ev, i); });
    alvo.addEventListener('pointerleave', ev => {
      if (ev.pointerType === 'touch') return;
      if (o.aoApontar) o.aoApontar(null);
      dicaEsconder();
    });
    return { marcar, mE, mD };
  }

  window.GRAFICOS = { fmt, nf, h, legenda, dicaMostrar, dispersao, linhasPontos, barras, coeficientes, coeficientesPar, divisao, ponte, linhaApuracao, curvas, funil,
    tabela, juntar, calor, dicaEsconder, virada, mapa, legendaCor, escalaDivergente, escalaSequencial, leiturasApuracao };
})();
