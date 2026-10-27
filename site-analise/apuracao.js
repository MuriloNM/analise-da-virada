/* Página "Apuração ao vivo" do estudo (T28): o registro da página que acompanhou a apuração do
   2º turno, refeito no caderno de apuração e ligado ao capítulo 7 (diário, D28 e D29; para o
   leitor, sempre "apuração ao vivo", nunca "da noite"). Consulta, fora da leitura corrida, com
   endereço próprio (#apuracao, #apuracao/fim, #apuracao/como). As leituras vêm de
   apuracao-dados.js (scripts/apuracao_dados.py), como a página as gravou, com 3 casas, e são
   mostradas assim, sem arredondar de novo (D25); o fim da apuração vem de dados.js. Uma régua com
   as 115 leituras, alinhada ao eixo das figuras, escolhe a leitura que a fita imprime. Não repete
   o capítulo 7: o erro da projeção fica lá, e as duas páginas se ligam. Os textos vêm do catálogo
   da língua da página (textos/pt-BR.js, chaves "av."; T30) e são rascunho (D23). */
window.APURACAO = function (X) {
  'use strict';
  const A = window.APURACAO_DADOS;
  const raiz = document.getElementById('av-corpo');
  if (!A || !raiz) return;
  const { D, G, BR, UFS, doBrasil, nomeMun, el, B, P, N, figura, sup, notaDados, semMovimento, dadosComo } = X;
  const { fmt } = G, T = window.T;
  let kf = 0, kt = 0;
  const nfig = () => `A${++kf}`, ntab = () => T('cap.tabela_n', { n: `A${++kt}` });

  // ---------- As leituras, como gravadas ----------
  const L = A.leituras.map(h => ({ x: h[0], c: h[1], m: h[2], p: h[3], hora: h[4] }));
  const ULT = L.length - 1;
  const T1 = A.curva1t.filter(q => q[0] >= Math.floor(L[0].x)).map(q => ({ x: q[0], y: q[1] }));
  const t1Em = xv => { // a curva do 1º turno no mesmo % apurado (interpolada entre dois pontos dela)
    let i = 1;
    while (i < T1.length - 1 && T1[i].x < xv) i++;
    const p = T1[i - 1], q = T1[i];
    return p.y + (xv - p.x) / (q.x - p.x) * (q.y - p.y);
  };
  const pct3 = v => fmt.pct(v, 3);
  const hm = hora => T('av.hora_curta', { h: hora.slice(0, 2), m: hora.slice(3, 5) });
  const aFrente = v => (v > 50 ? 'Lula' : v < 50 ? 'Flávio' : 'empate'); // quem estava à frente (interno, para comparar)
  const nomeDe = q => T(q === 'Lula' ? 'nome.lula' : 'nome.flavio');
  const variacao = L.map(l => l.c - l.m);
  const vMin = Math.min(...variacao), vMax = Math.max(...variacao);
  const dif1t = L.map(l => l.c - t1Em(l.x));
  const viradas = []; // leituras em que quem estava à frente na contagem mudou
  for (let i = 1; i < L.length; i++) if (aFrente(L[i].c) !== aFrente(L[i - 1].c)) viradas.push(i);
  const projSempre = ['Lula', 'Flávio'].find(q => L.every(l => aFrente(l.p) === q));
  let buraco = [L[0].x, L[1].x];
  for (let i = 1; i < L.length; i++) if (L[i].x - L[i - 1].x > buraco[1] - buraco[0]) buraco = [L[i - 1].x, L[i].x];
  const ys = L.flatMap(l => [l.c, l.m]).concat(T1.map(q => q.y));
  const EIXO_Y = { min: Math.floor(Math.min(...ys)), max: Math.ceil(Math.max(...ys) * 2) / 2 + 0.5, passo: 1 };

  // ---------- Abertura: o que foi a página e o que se viu nela ----------
  const lf = document.getElementById('av-linha-fina');
  const a7 = el('a', '', T('res.ir_cap', { n: 7 })); a7.href = '#analise/7';
  lf.append(...T.f('av.linha_fina', { data: T.data('2026-10-25'), n: L.length, de: L[0].hora, ate: L[ULT].hora,
    pct0: fmt.pct(L[0].x, 2), pct1: fmt.pct(L[ULT].x, 0), link: a7 }));
  const frases = [aFrente(L[0].c) === 'empate' ? T('av.frase.comecou_empate') : T('av.frase.comecou', { quem: nomeDe(aFrente(L[0].c)) })];
  for (const i of viradas) {
    const q = aFrente(L[i].c), antes = L.slice(0, i).some(l => aFrente(l.c) === q);
    frases.push(T(q === 'empate' ? 'av.frase.empatou' : antes ? 'av.frase.voltou' : 'av.frase.passou',
      { quem: q === 'empate' ? '' : nomeDe(q), hora: L[i].hora, pct: fmt.pct(L[i].x, 2) }));
  }
  const resp = P(raiz, 'av-resposta', T('av.frase.fim', { frases: T.lista(frases) }));
  resp.append(...T.f('av.resposta', { min: N(fmt.dec(vMin, 1)),
    max: N(T.p('un.pontos', vMax, { n: fmt.dec(vMax, 1) }, { minimumFractionDigits: 1, maximumFractionDigits: 20 })) }));

  // ---------- Leitura escolhida: a mesma nas duas figuras e na fita ----------
  const grade = el('div', 'av-grade', undefined, raiz);
  const colFig = el('div', 'av-col-fig', undefined, grade);
  const fita = el('aside', 'fita av-fita', undefined, grade);
  fita.setAttribute('aria-label', T('av.fita_aria'));
  const colProj = el('div', 'av-col-proj', undefined, grade);
  const colFig2 = el('div', 'av-col-fig2', undefined, grade);
  const anuncio = el('p', 'sr', undefined, grade);
  anuncio.setAttribute('aria-live', 'polite');
  const figs = [];
  let atual = ULT, tocando = null;
  let regua, btTocar;

  // A ficha da leitura (revisão do autor, D39): uma frase com o momento, os números de cada um com a
  // cor dele e uma barra de quem está à frente e por quanto (diferença = fatia do Lula − fatia do
  // Flávio, em pontos; a mesma escala para cada lado). Na última leitura, a contagem é o
  // resultado final e a projeção sai, para não repetir.
  const ESCALA = 7; // cobre a maior diferença das leituras (6,18 pontos, no 1º turno nas mesmas urnas)
  const dif = v => 2 * (v - 50);
  // "ponto" abaixo de 2,00 depois de arredondar a duas casas, como o número que aparece
  const pts = v => T.p('un.pontos', v, { n: fmt.abs(v, 2) }, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  // "o Lula estava à frente por 0,01 ponto"; sem verbo: "o Lula à frente por 0,01 ponto"
  const frente = (v, verbo = false) => (Math.round(Math.abs(dif(v)) * 100) === 0 ? T('av.empate')
    : T(verbo ? 'av.frente_estava' : 'av.frente', { quem: nomeDe(aFrente(v)), pts: pts(Math.abs(dif(v))) }));
  function bloco(tit, v, nota, escala) {
    const b = el('section', 'av-bloco', undefined, fita);
    el('h3', '', tit, b);
    const par = el('p', 'av-par', undefined, b);
    for (const [nome, lado, val] of [[T('nome.lula'), 'l', v], [T('nome.flavio'), 'f', 100 - v]]) {
      const c = el('span', 'av-c', undefined, par);
      el('i', 'av-k ' + lado, undefined, c);
      c.append(...T.f('av.par', { nome, pct: el('b', '', pct3(val)) }));
    }
    const barra = el('div', 'av-barra', undefined, b);
    barra.setAttribute('aria-hidden', 'true');
    const d = dif(v), f = el('i', d >= 0 ? 'l' : 'f', undefined, barra);
    f.style.width = Math.min(Math.abs(d), ESCALA) / ESCALA * 50 + '%';
    f.style[d >= 0 ? 'right' : 'left'] = '50%';
    if (escala) {
      const e = el('p', 'av-escala', undefined, b);
      e.setAttribute('aria-hidden', 'true');
      el('span', '', T('g.lula_a_frente'), e); el('span', '', T('av.empate'), e); el('span', '', T('g.flavio_a_frente'), e);
    }
    if (nota) el('p', 'av-nota-bloco', nota, b);
  }
  function imprimir(i) {
    const l = L[i], fim = L[ULT].c;
    fita.replaceChildren();
    el('p', 'av-quando', T('av.quando', { hora: l.hora, i: i + 1, n: L.length }), fita);
    el('p', 'av-apurado', T('av.apurado', { pct: i === ULT ? fmt.comPct('100') : fmt.pct(l.x, 2) }), fita);
    el('p', 'av-frase', i === ULT ? T('av.frase_fim', { frente: frente(l.c) })
      : T('av.frase_leitura', { contagem: frente(l.c, true), projecao: frente(l.p) }), fita);
    if (i === ULT) bloco(T('av.bloco.final'), l.c, null, true);
    else {
      bloco(T('av.bloco.contagem'), l.c, null, true);
      const e = l.p - fim;
      bloco(T('av.bloco.projecao'), l.p, Math.round(Math.abs(e) * 100) === 0 ? T('av.bloco.igual')
        : T(e < 0 ? 'av.bloco.abaixo' : 'av.bloco.acima', { pts: pts(Math.abs(e)) }));
    }
    bloco(T(i === ULT ? 'av.bloco.t1_inteiro' : 'av.bloco.t1_mesmas'), l.m,
      T('av.bloco.variacao', { v: T.p('un.pontos', l.c - l.m, { n: fmt.decSinal(l.c - l.m, 2) }, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }));
  }
  function mostrar(i) {
    imprimir(i);
    for (const f of figs) if (f.inst) f.inst.marcar(i);
  }
  const resumoLeitura = i => T('av.resumo_leitura', { hora: L[i].hora, pct: fmt.pct(L[i].x, 2), cl: pct3(L[i].c), cf: pct3(100 - L[i].c),
    pl: pct3(L[i].p), pf: pct3(100 - L[i].p) });
  function escolher(i, anunciar) {
    atual = Math.max(0, Math.min(ULT, i));
    if (regua) {
      regua.value = String(Math.round(L[atual].x * 100));
      regua.setAttribute('aria-valuetext', T('av.regua_valor', { i: atual + 1, n: L.length, hora: L[atual].hora, pct: fmt.pct(L[atual].x, 2) }));
    }
    mostrar(atual);
    if (anunciar) anuncio.textContent = resumoLeitura(atual);
  }
  const apontar = i => mostrar(i === null ? atual : i);
  function parar() {
    if (!tocando) return;
    clearInterval(tocando); tocando = null;
    btTocar.textContent = T('av.bt.tocar');
    btTocar.setAttribute('aria-pressed', 'false');
  }

  // Figura A1: a contagem e o 1º turno nas mesmas urnas
  const posX = L.map(l => l.x);
  const desenho = (f, o) => caixa => {
    f.inst = G.leiturasApuracao(caixa, Object.assign({
      leituras: posX, atual, y: EIXO_Y, buraco, aoApontar: apontar, aoEscolher: i => { parar(); escolher(i, false); },
      rotuloCursor: i => L[i].hora,
    }, o));
    if (f.aoDesenhar) f.aoDesenhar(f.inst);
    return '';
  };
  const f1 = {}, f2 = {}, f3 = {};
  figs.push(f1, f2, f3);
  figura(colFig, {
    n: nfig(),
    titulo: T('av.a1.titulo', { min: fmt.dec(vMin, 1), max: fmt.dec(vMax, 1) }),
    sub: T('av.a1.sub'),
    leitura: (viradas.length ? T('av.a1.leitura_marcos') : '') + T('av.a1.leitura'),
    desenhar: desenho(f1, {
      series: [
        { pontos: L.map(l => ({ x: l.x, y: l.c })), cls: 'linha-l', ponto: 'l', quebra: true, rotulo: { x: 86, texto: T('av.rot.lula2'), curto: T('av.rot.lula2'), dy: 18 } },
        { pontos: L.map(l => ({ x: l.x, y: l.m })), cls: 'linha-l linha-1t tracejada', ponto: 'l1', quebra: true, rotulo: { x: 86, texto: T('av.rot.lula1'), curto: T('av.rot.lula1'), dy: 24 } },
      ],
      flavioEsquerda: true,
      faixa: [0, 1],
      marcos: viradas.map((i, k) => ({ x: L[i].x, y: L[i].c,
        texto: T('av.marco', { hora: hm(L[i].hora), t: aFrente(L[i].c) === 'empate' ? T('av.empate') : T('av.marco_frente', { quem: nomeDe(aFrente(L[i].c)) }) }),
        curto: hm(L[i].hora), dy: k % 2 ? 50 : 30 })),
      dica: i => ({ titulo: T('av.dica.titulo', { pct: fmt.pct(L[i].x, 2), hora: L[i].hora }), linhas: [
        { lado: 'l', t: T('av.dica.contagem2'), v: pct3(L[i].c) },
        { lado: 'l1', t: T('av.rot.mesmas'), v: pct3(L[i].m) },
        { t: T('tab.variacao'), v: fmt.pp(L[i].c - L[i].m, 3) }] }),
      aria: T('av.a1.aria', { de: fmt.pct(L[0].x, 2), ate: fmt.comPct('100'), min: fmt.dec(vMin, 1), max: fmt.dec(vMax, 1) }),
    }),
    extra: fig => {
      const caixa = el('div', 'av-regua', undefined, fig);
      regua = el('input', 'av-range', undefined, caixa);
      regua.type = 'range'; regua.min = '0'; regua.max = '10000'; regua.step = '1';
      regua.setAttribute('aria-label', T('av.regua_aria'));
      f1.aoDesenhar = inst => { caixa.style.setProperty('--mE', inst.mE + 'px'); caixa.style.setProperty('--mD', inst.mD + 'px'); };
      const maisPerto = v => { let k = 0; L.forEach((l, i) => { if (Math.abs(l.x * 100 - v) < Math.abs(L[k].x * 100 - v)) k = i; }); return k; };
      regua.addEventListener('input', () => { parar(); escolher(maisPerto(+regua.value), false); });
      regua.addEventListener('change', () => escolher(atual, true));
      regua.addEventListener('keydown', ev => {
        const passo = { ArrowLeft: -1, ArrowDown: -1, ArrowRight: 1, ArrowUp: 1, PageDown: -10, PageUp: 10 }[ev.key];
        let alvo = null;
        if (passo) alvo = atual + passo; else if (ev.key === 'Home') alvo = 0; else if (ev.key === 'End') alvo = ULT;
        if (alvo === null) return;
        ev.preventDefault(); parar(); escolher(alvo, true);
      });
      const botoes = el('div', 'av-botoes', undefined, fig);
      botoes.setAttribute('role', 'group'); botoes.setAttribute('aria-label', T('av.bt.aria'));
      const bt = (t, f) => { const b = el('button', '', t, botoes); b.type = 'button'; b.addEventListener('click', f); return b; };
      bt(T('av.bt.anterior'), () => { parar(); escolher(atual - 1, true); });
      bt(T('av.bt.proxima'), () => { parar(); escolher(atual + 1, true); });
      btTocar = bt(T('av.bt.tocar'), () => {
        if (tocando) { parar(); escolher(atual, true); return; }
        if (atual === ULT) escolher(0, false);
        btTocar.textContent = T('av.bt.pausar');
        btTocar.setAttribute('aria-pressed', 'true');
        tocando = setInterval(() => { if (atual >= ULT) { parar(); escolher(ULT, true); } else escolher(atual + 1, false); }, semMovimento() ? 400 : 120);
      });
      btTocar.setAttribute('aria-pressed', 'false');
      bt(T('av.bt.final'), () => { parar(); escolher(ULT, true); });
    },
    como: [T.f('av.a1.como1'), T.f('av.a1.como2'), T('av.a1.como3', { m: pct3(L[ULT].m), b0: fmt.pct(buraco[0], 2), b1: fmt.pct(buraco[1], 1) }), dadosComo(['apuracao_ao_vivo'], [7])],
    fonte: T('av.fonte'),
    notas: ['N17'],
  });

  // Figura A2: a projeção ao vivo e o tamanho do erro dela, contra a linha de 50%. A faixa usa o
  // resultado final (o maior erro daquela leitura até a última antes do fim): só se traça depois.
  const FIN = L[ULT].c;
  const ERRO = L.map((_, i) => Math.max(0, ...L.slice(i, ULT).map(l => Math.abs(l.p - FIN))));
  const faixaP = L.map((l, i) => ({ x: l.x, lo: l.p - ERRO[i], hi: l.p + ERRO[i] }));
  let desde = ULT;
  while (desde > 0 && faixaP[desde - 1].lo > 50) desde--;
  const piorAntes = desde > 0 ? Math.min(...faixaP.slice(0, desde).map(f => f.lo)) : null;
  let iSalto = 1;
  for (let i = 1; i < ULT; i++) if (Math.abs(L[i].p - (L[i - 1].p + L[i + 1].p) / 2) > Math.abs(L[iSalto].p - (L[iSalto - 1].p + L[iSalto + 1].p) / 2)) iSalto = i;
  let abaixo = 0; // primeira leitura, fora o salto, em que a projeção chegou ao resultado final
  while (abaixo < ULT && (abaixo === iSalto || L[abaixo].p < FIN)) abaixo++;
  const notaSalto = el('span');
  sup(notaSalto, 'apuracao-salto', T('av.salto.tit', { hora: hm(L[iSalto].hora) }), [
    T('av.salto.1', { hora: L[iSalto].hora, de: pct3(L[iSalto - 1].p), para: pct3(L[iSalto].p), volta: pct3(L[iSalto + 1].p), hora2: L[iSalto + 1].hora }),
    T('av.salto.2'), T('av.salto.3'), T('av.salto.4')]);
  const contraste = viradas.length === 2 && projSempre && aFrente(L[viradas[0]].c) !== projSempre
    ? T('av.a2.contraste', { quem: nomeDe(aFrente(L[viradas[0]].c)), de: L[viradas[0]].hora, ate: L[viradas[1]].hora }) : '';
  const yP = { min: Math.floor(Math.min(49.5, ...faixaP.map(f => f.lo))), max: Math.ceil(Math.max(...faixaP.map(f => f.hi)) * 2) / 2, passo: 1 };
  const p50 = fmt.comPct('50');
  if (projSempre) resp.append(T(desde > 0 ? 'av.resposta_proj_desde' : 'av.resposta_proj', { quem: nomeDe(projSempre), pct: desde > 0 ? fmt.pct(L[desde].x, 2) : '', p50 }));
  figura(colProj, {
    n: nfig(),
    titulo: desde > 0 ? T('av.a2.titulo', { pct: fmt.pct(L[desde].x, 2), p50 }) : T('av.a2.titulo_todas', { p50 }),
    sub: T('av.a2.sub'),
    leitura: [[(projSempre ? T('av.a2.leitura_sempre', { quem: nomeDe(projSempre), contraste }) : '') +
      (piorAntes !== null ? T('av.a2.leitura_antes', { pct: fmt.pct(L[desde].x, 2), min: fmt.pct(piorAntes, 2) }) : '') +
      T('av.a2.leitura_erro'), ...T.f('av.a2.leitura_salto', { hora: L[iSalto].hora, nota: notaSalto, pct: fmt.pct(L[abaixo - 1].x, 2) })]],
    desenhar: desenho(f2, {
      y: yP,
      series: [{ pontos: L.map(l => ({ x: l.x, y: l.p })), cls: 'linha-ink', ponto: 'ink', quebra: true, rotulo: { x: 35, texto: T('c7.fig1.rot_proj'), curto: T('av.rot.projecao_curto'), dy: -12 } }],
      faixaPontos: faixaP,
      marcos: [{ x: L[iSalto].x, y: L[iSalto].p, texto: T('av.marco', { hora: hm(L[iSalto].hora), t: T('av.marco_salto') }), curto: hm(L[iSalto].hora), dy: -14 }]
        .concat(desde > 0 ? [{ x: L[desde].x, y: faixaP[desde].lo, texto: T('av.marco', { hora: hm(L[desde].hora), t: T('av.marco_faixa', { p50 }) }), curto: hm(L[desde].hora), dy: 32 }] : []),
      dica: i => ({ titulo: T('av.dica.titulo', { pct: fmt.pct(L[i].x, 2), hora: L[i].hora }), linhas: [
        { lado: 'ink', t: T('g.projecao_ao_vivo'), v: pct3(L[i].p) },
        { t: T('av.dica.maior_erro'), v: T('un.pp', { n: fmt.abs(ERRO[i], 3) }) },
        { t: T('av.dica.faixa'), v: T('g.de_a', { a: fmt.pct(faixaP[i].lo, 2), b: fmt.pct(faixaP[i].hi, 2) }) }] }),
      aria: T('av.a2.aria', { de: fmt.pct(L[0].x, 2), ate: fmt.comPct('100'), pct: fmt.pct(L[desde].x, 2), p50 }),
    }),
    como: [T.f('av.a2.como1', { final: pct3(FIN) }), T.f('av.a2.como2'), dadosComo(['apuracao_ao_vivo'], [7])],
    fonte: T('av.fonte'),
    notas: ['N17'],
  });

  // Figura A3: a contagem contra o 1º turno com o mesmo % apurado
  const iMax1t = dif1t.indexOf(Math.max(...dif1t));
  figura(colFig2, {
    n: nfig(),
    titulo: T('av.a3.titulo', { dif: fmt.dec(dif1t[iMax1t], 1), max: fmt.dec(vMax, 1) }),
    sub: T('av.a3.sub'),
    leitura: T('av.a3.leitura', { v: T('av.a3.pontos', { n: fmt.decSinal(dif1t[ULT], 3) }) }),
    desenhar: desenho(f3, {
      series: [
        { pontos: L.map(l => ({ x: l.x, y: l.c })), cls: 'linha-ink', ponto: 'ink', quebra: true, rotulo: { x: 30, texto: T('av.rot.contagem2'), curto: T('g.turno2') } },
        { pontos: T1, cls: 'linha-muted pontilhada', ponto: 'muted', rotulo: { x: 62, texto: T('av.rot.contagem1'), curto: T('g.turno1') } },
      ],
      dica: i => ({ titulo: T('av.dica.titulo', { pct: fmt.pct(L[i].x, 2), hora: L[i].hora }), linhas: [
        { lado: 'ink', t: T('av.dica.contagem2'), v: pct3(L[i].c) },
        { lado: 'muted', t: T('av.dica.mesmo_pct'), v: fmt.pct(t1Em(L[i].x), 2) },
        { t: T('res.fita_diferenca'), v: fmt.pp(dif1t[i], 2) }] }),
      aria: T('av.a3.aria', { dif: fmt.dec(dif1t[iMax1t], 1) }),
    }),
    como: [T.f('av.a3.como1'), T('av.a3.como2', { n: A.curva1t.length, pct: fmt.pct(T1[0].x, 2) }), dadosComo(['apuracao_ao_vivo'], [7])],
    fonte: T('av.a3.fonte'),
    notas: ['N17'],
  });
  escolher(ULT, false);

  // ---------- Ao fim da apuração ----------
  const fim = document.getElementById('apuracao-fim');
  const sF = 100 - BR.s2;
  const aExp = el('a', '', T('nav.explorar')); aExp.href = '#explorar/estados';
  const aCap4 = el('a', '', T('res.ir_cap', { n: 4 })); aCap4.href = '#analise/4';
  P(fim, 'av-intro', ...T.f('av.fim.intro', { l2: fmt.int(BR.L2), s2: fmt.pct(BR.s2, 2), f2: fmt.int(BR.F2), sf: fmt.pct(sF, 2),
    c2: fmt.pct(100 * BR.C2 / BR.E2, 1), c1: fmt.pct(100 * BR.C1 / BR.E1, 1), bn: fmt.pct(100 * BR.BN2 / BR.C2, 1), explorar: aExp, cap4: aCap4 }));
  const fatia = v => fmt.pct(v, 2);
  const colunasFatia = [
    { t: T('av.fim.col_l1'), num: true, v: u => u.s1, f: fatia },
    { t: T('av.fim.col_l2'), num: true, v: u => u.s2, f: fatia },
    { t: T('tab.variacao'), num: true, v: u => u.s2 - u.s1, f: v => fmt.pp(v) }];
  const est = el('div', 'av-tabela', undefined, fim);
  G.tabela(est, { legenda: { n: ntab(), t: T('av.fim.tab_estados') },
    linhas: [BR].concat(UFS.slice().sort((a, b) => b.E2 - a.E2), D.ufs.filter(u => u.codigo === 'ZZ')),
    ordem: { col: 1, desc: true }, destaque: u => u === BR,
    colunas: [{ t: T('tab.estado'), v: u => u.nome }, { t: T('tab.eleitorado'), num: true, v: u => u.E2, f: fmt.int }].concat(colunasFatia) });
  const mun = doBrasil().slice().sort((a, b) => b.E2 - a.E2).slice(0, 40);
  const tm = el('div', 'av-tabela', undefined, fim);
  G.tabela(tm, { legenda: { n: ntab(), t: T('av.fim.tab_municipios') },
    linhas: mun, ordem: { col: 1, desc: true },
    colunas: [{ t: T('tab.municipio'), v: m => nomeMun(m) }, { t: T('tab.eleitorado'), num: true, v: m => m.E2, f: fmt.int }].concat(colunasFatia) });
  const pe = P(fim, 'av-nota', T('av.fim.fonte'));
  sup(pe, 'apuracao-fim', T('av.fim.como.tit'), [T('av.fim.como1', { pct: fmt.pct(99.77, 2) }), T('av.fim.como2')]);

  // ---------- Como a página funcionava ----------
  const como = document.getElementById('apuracao-como');
  P(como, 'av-texto', T('av.como.1', { n: L.length, b0: fmt.pct(buraco[0], 2), b1: fmt.pct(buraco[1], 1) }), nd());
  P(como, 'av-texto', T('av.como.2'));
  const aCap7 = el('a', '', T('res.ir_cap', { n: 7 })); aCap7.href = '#analise/7';
  P(como, 'av-texto', ...T.f('av.como.3', { link: aCap7 }));
  P(como, 'av-texto', T('av.como.4'));
  const ao = el('a', '', T('av.como.original_nome'));
  ao.href = 'https://apuracao-mesmas-urnas.pages.dev/'; ao.rel = 'noopener';
  P(como, 'av-texto', ...T.f('av.como.5', { link: ao }));
  const baixar = P(como, 'av-texto av-baixar', '');
  const ab = el('a', '', T('av.como.baixar', { n: L.length }), baixar);
  ab.href = '#';
  ab.addEventListener('click', ev => {
    ev.preventDefault(); ev.stopPropagation();
    // no formato da língua da página (diário, D41): o separador entre campos e o sinal decimal vêm do catálogo
    const sep = T('csv.separador'), dec = (v, c) => v.toFixed(c).replace('.', T('csv.decimal'));
    const linhas = [['urnas_apuradas_pct', 'hora_tse', 'lula_2t_pct', 'lula_1t_mesmas_urnas_pct', 'projecao_final_pct', 'lula_1t_por_uf_pct']]
      .concat(A.leituras.map(h => [dec(h[0], 2), h[4], dec(h[1], 3), dec(h[2], 3), dec(h[3], 3), dec(h[5], 3)]));
    const url = URL.createObjectURL(new Blob(['﻿' + linhas.map(r => r.join(sep)).join('\r\n')], { type: 'text/csv;charset=utf-8' }));
    const a = document.createElement('a');
    a.href = url; a.download = 'apuracao-ao-vivo-2t-leituras.csv';
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });

  // ---------- Índice das partes, como o dos capítulos (revisão do autor, D39; peça comum de estudo.js) ----------
  grade.id = 'apuracao-leituras'; grade.tabIndex = -1;
  if (X.indicePartes) X.indicePartes(document.getElementById('av-lista-indice'), document.getElementById('apuracao'), [
    { id: 'apuracao', nome: T('nav.apuracao'), href: '#apuracao' },
    { id: 'apuracao-leituras', nome: T('av.ind.leituras'), href: '#apuracao/leituras' },
    { id: 'apuracao-fim', nome: T('av.fim.tit'), href: '#apuracao/fim' },
    { id: 'apuracao-como', nome: T('av.como.tit'), href: '#apuracao/como' },
  ], [{ nome: T('av.ind.cap7'), href: '#analise/7' }]);
  function nd() { return notaDados(el('span'), 'N17'); }
};
