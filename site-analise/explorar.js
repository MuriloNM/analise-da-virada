/* Página Explorar do estudo (T24): consulta, fora da leitura corrida (diário, D34). Quatro partes,
   cada uma com endereço próprio (#explorar/ponte, /estados, /municipios, /incerteza): a ponte da
   virada, os estados no mapa e na tabela, os municípios com recortes, busca, rankings, dispersões
   e funil, e as estimativas com o intervalo de cada uma. Os números são os mesmos dos capítulos,
   de dados.js, arredondados uma vez na hora de mostrar (D25); o desenho dos estados vem de mapa.js
   (malha do IBGE, scripts/mapa_ufs.py). As peças (figura, notas, busca, tabela) são as de
   estudo.js, que chama EXPLORAR antes de montar a lista de notas. Os textos vêm do catálogo da
   língua da página (textos/pt-BR.js, chaves "exp."; T30) e são rascunho (D23). */
window.EXPLORAR = function (X) {
  'use strict';
  const { D, G, BR, UFS, NOME_UF, PORTE, el, B, P, listaE, figura, figurasComAbas, sup, notaDados, nd, dadosComo } = X;
  const { fmt, nf } = G, T = window.T;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  let kf = 0, kt = 0;
  const nfig = () => `E${++kf}`, ntab = () => T('cap.tabela_n', { n: `E${++kt}` });
  const REGIOES = D.regioes.filter(r => r.codigo !== 'EX');
  const FORMA = window.MAPA_UFS;

  /** Escolha em texto sublinhado, como no capítulo 3 (sem pílula); lembra a última escolha. */
  function escolha(pai, rotulo, opcoes, chave, aoMudar) {
    const g = el('div', 'botoes-escolha', undefined, pai);
    g.setAttribute('role', 'group'); g.setAttribute('aria-label', rotulo);
    const lembrada = X.guarda.ler('analise-exp-' + chave);
    let atual = opcoes.some(o => o[0] === lembrada) ? lembrada : opcoes[0][0];
    const marcar = () => $$('button', g).forEach(b => b.setAttribute('aria-pressed', b.dataset.v === atual ? 'true' : 'false'));
    for (const [v, t] of opcoes) {
      const b = el('button', '', t, g);
      b.type = 'button'; b.dataset.v = v;
      b.addEventListener('click', () => {
        if (v === atual) return;
        atual = v; marcar(); G.dicaEsconder();
        X.guarda.gravar('analise-exp-' + chave, v === opcoes[0][0] ? null : v);
        aoMudar(v);
      });
    }
    marcar();
    return { valor: () => atual };
  }
  /** Campo de escolha (select) com o rótulo antes, no estilo do campo da busca. */
  let selN = 0;
  function seletor(pai, rotulo, opcoes, aoMudar) {
    const c = el('label', 'exp-campo', undefined, pai);
    el('span', 'exp-campo-rot', rotulo, c);
    const s = el('select', '', undefined, c);
    s.id = 'exp-sel-' + (++selN);
    for (const o of opcoes) {
      if (o.grupo) { const og = el('optgroup', '', undefined, s); og.label = o.grupo; for (const x of o.itens) el('option', '', x[1], og).value = x[0]; continue; }
      el('option', '', o[1], s).value = o[0];
    }
    s.addEventListener('change', () => aoMudar(s.value));
    return s;
  }
  /** Troca o título (a conclusão) e o subtítulo de uma figura já montada. */
  function retitular(fig, titulo, sub) {
    const ft = $('.fig-tit', fig), n = $('.fig-n', ft);
    ft.replaceChildren(n, titulo);
    if (sub !== undefined) $('.fig-sub', fig).replaceChildren(...[].concat(sub));
  }
  const redesenharEm = caixa => $$('.grafico', caixa).forEach(g => g.redesenhar && g.redesenhar());

  // ======================= 1. Ponte da virada =======================
  (function ponte() {
    const pai = $('#exp-ponte');
    $('#exp-ponte-intro').textContent = T('exp.ponte.intro', { m1: fmt.mi(BR.M1), m2: fmt.mi(BR.M2) });
    const regs = D.regioes.slice().sort((a, b) => b.dM - a.dM), ufs = D.ufs.slice().sort((a, b) => b.dM - a.dM);
    const dicaU = u => [{ t: T('c6.dica.mudanca'), v: fmt.intSinal(u.dM) }, { t: T('c6.dica.peso'), v: fmt.pct(u.peso, 1) },
      { t: T('c6.dica.dif1'), v: fmt.intSinal(u.M1) }, { t: T('c6.dica.dif2'), v: fmt.intSinal(u.M2) },
      { t: T('c6.dica.captura'), v: fmt.pct(u.cap, 1) }];
    const tot = t => [{ lado: 'l', t: T('nome.lula'), v: fmt.int(t === 1 ? BR.L1 : BR.L2) }, { lado: 'f', t: T('nome.flavio'), v: fmt.int(t === 1 ? BR.F1 : BR.F2) },
      { t: T('res.fita_diferenca'), v: fmt.intSinal(t === 1 ? BR.M1 : BR.M2) }];
    const n = nfig();
    const comum = {
      n,
      leitura: T('exp.ponte.leitura', { m1: fmt.mi(BR.M1), m2: fmt.mi(BR.M2) }),
      como: [
        T.f('exp.ponte.como1', { dm: fmt.int(BR.dM) }),
        T.f('exp.ponte.como2'),
        T('c4.fig1.como3'), dadosComo(['estados'], [3])],
      notas: ['N06', 'N08'],
    };
    figurasComAbas(pai, [
      { rotulo: T('c6.aba1'), montar: p => figura(p, Object.assign({
        titulo: T('c6.fig1.titulo_reg', { r0: regs[0].nome, r1: regs[1].nome, p: fmt.pct(regs[0].peso + regs[1].peso, 1) }),
        sub: T('exp.ponte.sub_reg'),
        desenhar: caixa => G.ponte(caixa, { M1: BR.M1, M2: BR.M2, dica1: tot(1), dica2: tot(2),
          aria: T('c6.fig1.aria_reg', { m1: fmt.mi(BR.M1), m2: fmt.mi(BR.M2) }),
          itens: regs.map(u => ({ nome: u.nome, curto: u.nome, dM: u.dM, dica: dicaU(u) })) }) }, comum)) },
      { rotulo: T('c6.aba2'), montar: p => figura(p, Object.assign({
        titulo: T('c6.fig1.titulo_uf', { uf: ufs[0].nome, p: fmt.pct(ufs[0].peso, 1) }),
        sub: T('exp.ponte.sub_uf'),
        desenhar: caixa => G.ponte(caixa, { M1: BR.M1, M2: BR.M2, dica1: tot(1), dica2: tot(2),
          aria: T('c6.fig1.aria_uf', { m1: fmt.mi(BR.M1), m2: fmt.mi(BR.M2) }),
          itens: ufs.map(u => ({ nome: u.nome, curto: u.codigo === 'ZZ' ? T('c6.ext_curto') : u.codigo, dM: u.dM, dica: dicaU(u) })) }) }, comum)) },
    ], 'exp-ponte');
  })();

  // ======================= 2. Estados: mapa, ficha e tabela, ligados =======================
  (function estados() {
    const pai = $('#exp-estados');
    const MODOS = {
      s1: { rot: T('g.turno1'), marcas: 'fatia' }, s2: { rot: T('g.turno2'), marcas: 'fatia' },
      ds: { rot: T('exp.mapa.modo_ds'), marcas: 'var' }, da: { rot: T('exp.mapa.modo_da'), marcas: 'abst' },
    };
    const ganhouL = k => UFS.filter(u => u[k] > 50).length;
    const ds = UFS.map(u => u.ds), subiuA = UFS.filter(u => u.da > 0).length;
    const TITULO = {
      s1: T('exp.mapa.titulo_s1', { l: ganhouL('s1'), f: 27 - ganhouL('s1') }),
      s2: T('exp.mapa.titulo_s2', { l: ganhouL('s2'), f: 27 - ganhouL('s2') }),
      ds: T('exp.mapa.titulo_ds', { onde: UFS.every(u => u.ds > 0) ? T('c6.resposta.todos') : T('c6.resposta.alguns', { n: UFS.filter(u => u.ds > 0).length }),
        min: fmt.abs(Math.min(...ds), 2), max: fmt.abs(Math.max(...ds), 2) }),
      da: T('exp.mapa.titulo_da', { caiu: 27 - subiuA, subiu: subiuA }),
    };
    const SUB = { s1: T('exp.mapa.sub_s1'), s2: T('exp.mapa.sub_s2'), ds: T('exp.mapa.sub_ds'), da: T('exp.mapa.sub_da') };
    let modo = 'ds', fixo = null, mapaApi = null;
    // nas fatias (1º e 2º turno) a cor tem piso: quem passa de 50% sai sempre do cinza para o seu lado (QA, L4), para dar para contar quem ganhou cada estado
    const piso = t => (t === 0 ? 0 : Math.sign(t) * (0.3 + 0.7 * Math.min(1, Math.abs(t))));
    const cor = u => {
      if (modo === 'da') return G.escalaSequencial()((u.da + 4) / 12);
      return G.escalaDivergente()(modo === 'ds' ? u.ds / 5 : piso((u[modo] - 50) / 30));
    };
    const dica = u => {
      if (modo === 'da') return { titulo: u.nome, linhas: [{ t: T('c4.dica.abst1'), v: fmt.pct(u.a1, 2) }, { t: T('c4.dica.no2'), v: fmt.pct(u.a2, 2) },
        { t: T('tab.variacao'), v: fmt.pp(u.da) }, { t: T('tab.comparecimento'), v: T('c4.dica.eleitores', { n: fmt.intSinal(u.C2 - u.C1) }) }] };
      if (modo === 'ds') return { titulo: u.nome, linhas: [
        { lado: 'l', t: T('exp.dica.fatia_lula'), v: T('exp.dica.de_para_var', { a: fmt.pct(u.s1, 2), b: fmt.pct(u.s2, 2), v: fmt.pp(u.ds) }) },
        { lado: 'f', t: T('c2.dica.fatia_flavio'), v: T('exp.dica.de_para_var', { a: fmt.pct(100 - u.s1, 2), b: fmt.pct(100 - u.s2, 2), v: fmt.pp(-u.ds) }) },
        { t: T('c6.dica.mudanca'), v: fmt.intSinal(u.dM) }] };
      const s = u[modo];
      return { titulo: u.nome, linhas: [{ lado: 'l', t: T('nome.lula'), v: fmt.pct(s, 2) }, { lado: 'f', t: T('nome.flavio'), v: fmt.pct(100 - s, 2) },
        { t: T('exp.dica.a_frente'), v: T('exp.dica.a_frente_v', { nome: T(s > 50 ? 'nome.lula' : 'nome.flavio'), n: fmt.int(Math.abs(modo === 's1' ? u.M1 : u.M2)) }) }] };
    };

    modo = escolha(pai, T('exp.mapa.escolha'), Object.entries(MODOS).map(([k, m]) => [k, m.rot]), 'mapa', v => { modo = v; pintar(); }).valor();

    const fig = el('figure', 'figura', undefined, pai);
    const cab = el('figcaption', 'fig-cab', undefined, fig);
    const ft = el('span', 'fig-tit', undefined, cab);
    const nF = nfig();
    el('span', 'fig-n', T('fig.n', { n: nF }), ft);
    el('span', 'fig-sub', undefined, cab);
    const grade = el('div', 'exp-mapa', undefined, fig);
    const colMapa = el('div', 'exp-mapa-col', undefined, grade);
    const legCor = el('div', 'grafico exp-legenda-cor', undefined, colMapa);
    const legHach = G.legenda(colMapa, [{ t: T('exp.mapa.leg_listras'), tipo: 'hachura' }]);
    X.grafico(colMapa, caixa => {
      mapaApi = G.mapa(caixa, { forma: FORMA, ufs: UFS, cor, hachura: u => modo === 'da' && u.da > 0, dica,
        aria: T('exp.mapa.aria'),
        aoDestacar: c => { mapaApi.destacar(c || fixo); ficha(c || fixo); marcarLinha(c); },
        aoEscolher: c => escolher(c) });
      mapaApi.destacar(fixo);
    }, 'exp-mapa-svg');
    const fichaCaixa = el('aside', 'exp-ficha', undefined, grade);
    fichaCaixa.setAttribute('aria-live', 'polite');
    const rod = el('div', 'fig-rodape', undefined, fig);
    const fonte = el('span', '', T('exp.mapa.fonte'), rod);
    sup(fonte, 'exp-mapa', T('exp.mapa.como.tit'), [T.f('exp.mapa.como1'), T.f('exp.mapa.como2'), T.f('exp.mapa.como3'), T('exp.mapa.como4'), dadosComo(['estados'], [3, 8])]);
    notaDados(fonte, 'N05'); notaDados(fonte, 'N06');

    function legenda() {
      const div = G.escalaDivergente(), seq = G.escalaSequencial();
      const L = MODOS[modo].marcas === 'fatia'
        ? { dom: [20, 80], cor: v => div(piso((v - 50) / 30)), marcas: [20, 35, 50, 65, 80].map(v => [v, fmt.pct(v, 0)]), esq: T('exp.mapa.leg_mais_f'), dir: T('exp.mapa.leg_mais_l') }
        : MODOS[modo].marcas === 'var'
          ? { dom: [-5, 5], cor: v => div(v / 5), marcas: [[-5, fmt.decSinal(-5, 0)], [-2.5, fmt.decSinal(-2.5, 1)], [0, '0'], [2.5, fmt.decSinal(2.5, 1)], [5, fmt.pp(5, 0)]], esq: T('exp.mapa.leg_subiu_f'), dir: T('exp.mapa.leg_subiu_l') }
          : { dom: [-4, 8], cor: v => seq((v + 4) / 12), marcas: [[-4, fmt.decSinal(-4, 0)], [0, '0'], [4, fmt.decSinal(4, 0)], [8, fmt.pp(8, 0)]], esq: T('exp.mapa.leg_caiu'), dir: T('exp.mapa.leg_subiu') };
      G.legendaCor(legCor, L);
      legHach.hidden = modo !== 'da';
    }
    function pintar() {
      retitular(fig, TITULO[modo], SUB[modo]);
      legenda();
      if (mapaApi) mapaApi.pintar();
    }

    // A silhueta do estado a traço e a virada dele em miniatura: o gráfico da abertura, por estado
    // (pedido do autor na revisão do T24, no lugar do estado em voxel; diário, D37).
    const NS = 'http://www.w3.org/2000/svg';
    const svgEl = (nome, attrs, pai) => {
      const e = document.createElementNS(NS, nome);
      for (const k in attrs) e.setAttribute(k, attrs[k]);
      if (pai) pai.appendChild(e);
      return e;
    };
    const svgTexto = (pai, x, y, t, attrs = {}) => { const e = svgEl('text', Object.assign({ x, y }, attrs), pai); e.textContent = t; return e; };
    const caixaDe = {};
    function caixaDoEstado(cod) {
      if (!caixaDe[cod]) {
        const n = (cod ? FORMA.caminhos[cod] : Object.values(FORMA.caminhos).join('')).match(/-?[0-9.]+/g).map(Number);
        const xs = n.filter((_, i) => i % 2 === 0), ys = n.filter((_, i) => i % 2 === 1);
        caixaDe[cod] = [Math.min(...xs), Math.min(...ys), Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys)];
      }
      return caixaDe[cod];
    }
    function viradaDoEstado(pai, u, cod) {
      const caixa = el('div', 'grafico exp-virada-uf', undefined, pai);
      const W = Math.max(260, Math.min(fichaCaixa.clientWidth || 330, 440)), H = 128, lado = 92;
      const s = svgEl('svg', { width: W, height: H, viewBox: `0 0 ${W} ${H}`, role: 'img',
        'aria-label': T('exp.virada_uf.aria', { uf: u.nome, l1: fmt.int(u.L1), l2: fmt.int(u.L2), f1: fmt.int(u.F1), f2: fmt.int(u.F2) }) }, caixa);
      // silhueta: o estado a traço; para o Brasil, os 27 estados
      const [bx, by, bw, bh] = caixaDoEstado(cod);
      const k = Math.min(lado / bw, (H - 16) / bh);
      const g = svgEl('g', { transform: `translate(${(lado - bw * k) / 2},${(H - bh * k) / 2}) scale(${k}) translate(${-bx},${-by})` }, s);
      for (const c of cod ? [cod] : Object.keys(FORMA.caminhos)) svgEl('path', { d: FORMA.caminhos[c], class: 'uf-silhueta' }, g);
      // a virada: votos de cada um nos dois turnos, duas linhas, com o valor na ponta
      const X1 = lado + 56, X2 = W - 100, topo = 24, base = H - 10;
      const vs = [u.L1, u.L2, u.F1, u.F2], lo = Math.min(...vs), hi = Math.max(...vs), folga = (hi - lo) * 0.04 || 1;
      const y = v => base - (v - lo + folga) / (hi - lo + 2 * folga) * (base - topo);
      [[X1, T('g.turno1')], [X2, T('g.turno2')]].forEach(([x, t]) => {
        svgEl('line', { x1: x, x2: x, y1: topo - 6, y2: base + 4, class: 'col-fio' }, s);
        svgTexto(s, x, topo - 11, t, { 'text-anchor': 'middle', class: 'cab-col' });
      });
      const mi = hi >= 1e6 ? v => fmt.comMi(nf(v / 1e6, 2)) : v => fmt.comMil(nf(v / 1e3, 0)); // estados pequenos em milhares
      const afasta = (a, b) => { const d = 13 - Math.abs(a - b); return d > 0 ? (a <= b ? [a - d / 2, b + d / 2] : [a + d / 2, b - d / 2]) : [a, b]; };
      const [yl1, yf1] = afasta(y(u.L1), y(u.F1)), [yl2, yf2] = afasta(y(u.L2), y(u.F2));
      for (const [lado2, nome, v1, v2, t1, t2] of [['l', T('nome.lula'), u.L1, u.L2, yl1, yl2], ['f', T('nome.flavio'), u.F1, u.F2, yf1, yf2]]) {
        svgEl('line', { x1: X1, y1: y(v1), x2: X2, y2: y(v2), class: 'linha linha-grossa linha-' + lado2 }, s);
        svgEl('circle', { cx: X1, cy: y(v1), r: 4, class: 'pt-anel p-' + lado2 }, s);
        svgEl('circle', { cx: X2, cy: y(v2), r: 4, class: 'pt-anel p-' + lado2 }, s);
        svgTexto(s, X1 - 8, t1 + 4, mi(v1), { 'text-anchor': 'end', class: 'val' });
        svgTexto(s, X2 + 8, t2 + 4, T('exp.virada_uf.ponta', { nome, v: mi(v2) }), { class: 'val' });
      }
      P(pai, 'ficha-pe exp-virada-rot', T('exp.virada_uf.rot'));
    }

    // Ficha do estado: o Brasil, até a pessoa escolher um estado no mapa ou na tabela
    function ficha(cod) {
      const u = cod ? UFS.find(x => x.codigo === cod) : BR;
      fichaCaixa.replaceChildren();
      el('h3', 'ficha-tit', u.nome, fichaCaixa);
      el('p', 'ficha-meta', cod ? (fixo === cod ? T('exp.ficha.fixado', { regiao: u.regiao }) : u.regiao) : T('exp.ficha.brasil'), fichaCaixa);
      viradaDoEstado(fichaCaixa, u, cod);
      const t = el('table', 'tab tab-ficha', undefined, el('div', 'tab-caixa', undefined, fichaCaixa));
      const cabT = el('tr', '', undefined, el('thead', '', undefined, t));
      ['', T('exp.ficha.col1'), T('tab.turno2_curto'), T('exp.ficha.var')].forEach((c, i) => { const th = el('th', i ? 'num' : '', c, cabT); th.scope = 'col'; });
      const tb = el('tbody', '', undefined, t);
      for (const l of [
        [T('ficha.lula_votos'), fmt.int(u.L1), fmt.int(u.L2), fmt.intSinal(u.dL)],
        [T('ficha.flavio_votos'), fmt.int(u.F1), fmt.int(u.F2), fmt.intSinal(u.dF)],
        [T('exp.dica.fatia_lula'), fmt.pct(u.s1, 2), fmt.pct(u.s2, 2), fmt.pp(u.ds)],
        [T('c2.dica.fatia_flavio'), fmt.pct(100 - u.s1, 2), fmt.pct(100 - u.s2, 2), fmt.pp(-u.ds)],
        [T('res.fita_diferenca'), fmt.intSinal(u.M1), fmt.intSinal(u.M2), fmt.intSinal(u.dM)],
        [T('ficha.abstencao'), fmt.pct(u.a1, 2), fmt.pct(u.a2, 2), fmt.pp(u.da)]]) {
        const r = el('tr', '', undefined, tb);
        l.forEach((c, i) => { const td = el(i ? 'td' : 'th', i ? 'num' : '', c, r); if (!i) td.scope = 'row'; });
      }
      P(fichaCaixa, 'ficha-pe', ...T.f(u.cap === null ? 'exp.ficha.pe_sem_captura' : 'exp.ficha.pe', { peso: B(fmt.pct(u.peso, 1)), cap: B(fmt.pct(u.cap, 1)), n09: nd('N09') }));
      if (fixo) {
        const b = el('button', 'bt-link exp-voltar', T('exp.ficha.voltar'), P(fichaCaixa, 'ficha-pe'));
        b.type = 'button';
        b.addEventListener('click', () => escolher(fixo));
      } else {
        P(fichaCaixa, 'ficha-pe exp-dica', T('exp.ficha.dica'));
      }
    }
    function escolher(cod) {
      fixo = fixo === cod ? null : cod;
      if (mapaApi) mapaApi.destacar(fixo);
      ficha(fixo);
      marcarLinha(null);
    }
    function marcarLinha(cod) {
      $$('tr[data-uf]', tabCaixa).forEach(tr => {
        tr.classList.toggle('ativa', tr.dataset.uf === cod);
        tr.classList.toggle('escolhida', tr.dataset.uf === fixo);
      });
    }

    const tabCaixa = el('div', 'exp-tab-estados', undefined, pai);
    G.tabela(tabCaixa, { legenda: { n: ntab(), t: T('exp.estados.tabela') },
      linhas: UFS, ordem: { col: 3, desc: true },
      colunas: [{ t: T('tab.estado'), v: u => u.nome },
        { t: T('tab.fatia_lula_1'), num: true, v: u => u.s1, f: v => fmt.pct(v, 2) }, { t: T('tab.turno2_curto'), num: true, v: u => u.s2, f: v => fmt.pct(v, 2) },
        { t: T('tab.variacao'), num: true, v: u => u.ds, f: v => fmt.pp(v) },
        { t: T('tab.abst_1'), num: true, v: u => u.a1, f: v => fmt.pct(v, 2) }, { t: T('tab.turno2_curto'), num: true, v: u => u.a2, f: v => fmt.pct(v, 2) },
        { t: T('tab.variacao'), num: true, v: u => u.da, f: v => fmt.pp(v) },
        { t: T('c6.dica.mudanca'), num: true, v: u => u.dM, f: fmt.intSinal }],
      aoLinha: (tr, u) => {
        tr.dataset.uf = u.codigo;
        tr.classList.toggle('escolhida', u.codigo === fixo);
        tr.addEventListener('pointerenter', () => { if (mapaApi) mapaApi.destacar(u.codigo); ficha(u.codigo); tr.classList.add('ativa'); });
        tr.addEventListener('pointerleave', () => { if (mapaApi) mapaApi.destacar(fixo); ficha(fixo); tr.classList.remove('ativa'); });
        const th = tr.firstElementChild, nome = th.textContent;
        th.replaceChildren();
        const b = el('button', 'bt-uf', nome, th);
        b.type = 'button';
        b.setAttribute('aria-label', T('exp.estados.fixar', { uf: nome }));
        b.addEventListener('click', () => escolher(u.codigo));
      } });
    P(pai, 'exp-nota', ...T.f('exp.estados.nota', { n06: nd('N06') }));

    pintar();
    ficha(null);
    // As cores do mapa são lidas do CSS: o modo claro ou escuro pede para pintar de novo
    new MutationObserver(pintar).observe(document.documentElement, { attributes: true, attributeFilter: ['data-tema'] });
    matchMedia('(prefers-color-scheme: dark)').addEventListener('change', pintar);
  })();

  // ======================= 3. Municípios: recorte, busca, rankings, dispersões e funil =======================
  (function municipios() {
    const pai = $('#exp-municipios');
    const rec = { regiao: '', uf: '', porte: '', cap: '' };
    let lista = X.doBrasil();
    const filtra = () => X.doBrasil().filter(m => (!rec.regiao || X.REGIAO_UF[m.uf] === rec.regiao) && (!rec.uf || m.uf === rec.uf) &&
      (!rec.porte || m.porte === rec.porte) && (!rec.cap || (rec.cap === 'capital') === m.capital));
    const comRecorte = () => Object.values(rec).some(Boolean);
    const descreve = () => [rec.uf ? NOME_UF[rec.uf] : rec.regiao, rec.porte ? PORTE[rec.porte] : '', rec.cap ? T('exp.rec.so_' + rec.cap) : '']
      .filter(Boolean).join(T('exp.rec.sep'));

    // --- Recorte: vale para os rankings, as dispersões e o funil (a busca procura em todos) ---
    const barra = el('div', 'exp-recorte', undefined, pai);
    barra.setAttribute('role', 'group'); barra.setAttribute('aria-label', T('exp.rec.aria'));
    const selReg = seletor(barra, T('exp.rec.regiao'), [['', T('exp.rec.todas')]].concat(REGIOES.map(r => [r.nome, r.nome])), v => { rec.regiao = v; rec.uf = ''; opcoesUf(); mudou(); });
    const selUf = seletor(barra, T('tab.estado'), [], v => { rec.uf = v; mudou(); });
    const selPorte = seletor(barra, T('exp.rec.porte'), [['', T('exp.rec.todos')]].concat(Object.entries(PORTE).map(([k, t]) => [k, t])), v => { rec.porte = v; mudou(); });
    const selCap = seletor(barra, T('exp.rec.capital'), [['', T('exp.rec.cap_e_interior')], ['capital', T('exp.rec.so_capital')], ['interior', T('exp.rec.so_interior')]], v => { rec.cap = v; mudou(); });
    function opcoesUf() {
      selUf.replaceChildren();
      el('option', '', T('exp.rec.todos'), selUf).value = '';
      for (const u of UFS.filter(u => !rec.regiao || u.regiao === rec.regiao).sort((a, b) => a.nome.localeCompare(b.nome, T.lingua))) el('option', '', u.nome, selUf).value = u.codigo;
    }
    opcoesUf();
    const conta = el('p', 'exp-conta', undefined, pai);
    conta.setAttribute('aria-live', 'polite');
    const limpar = el('button', 'bt-link', T('exp.rec.limpar'), undefined);
    limpar.type = 'button';
    limpar.addEventListener('click', () => {
      Object.keys(rec).forEach(k => { rec[k] = ''; });
      selReg.value = selPorte.value = selCap.value = ''; opcoesUf(); mudou();
    });

    // --- Busca com a ficha da cidade ---
    const sb = el('section', 'exp-sub', undefined, pai);
    el('h3', '', T('exp.busca.tit'), sb);
    const pb = el('div', 'pergunta exp-busca', undefined, sb);
    const lab = el('label', '', T('tab.municipio'), pb); lab.htmlFor = 'busca-exp';
    const bx = el('div', 'busca', undefined, pb);
    const entrada = el('input', 'campo', undefined, bx);
    Object.assign(entrada, { id: 'busca-exp', type: 'search', placeholder: T('res.cidade_placeholder'), autocomplete: 'off', spellcheck: false });
    entrada.setAttribute('role', 'combobox'); entrada.setAttribute('aria-autocomplete', 'list');
    entrada.setAttribute('aria-expanded', 'false'); entrada.setAttribute('aria-controls', 'busca-exp-lista');
    const lb = el('ul', 'busca-lista', undefined, bx);
    lb.id = 'busca-exp-lista'; lb.setAttribute('role', 'listbox'); lb.setAttribute('aria-label', T('busca.aria')); lb.hidden = true;
    const fc = el('div', '', undefined, sb);
    fc.setAttribute('aria-live', 'polite');
    X.busca(entrada, lb, fc, 'busca-exp-op-', (caixa, m) => {
      X.fichaCidade(caixa, m);
      const f = $('.ficha', caixa);
      P(f, 'ficha-pe', ...T.f('exp.busca.extra', { o: B(fmt.pct(m.o, 1)), e1: B(fmt.int(m.E1)), e2: B(fmt.int(m.E2)), n05: nd('N05') }));
    });

    // --- Rankings ---
    const sr = el('section', 'exp-sub', undefined, pai);
    el('h3', '', T('exp.rank.tit'), sr);
    const piso = m => m.E1 > 10000;
    const colE = { t: T('tab.eleitorado'), num: true, v: m => m.E1, f: fmt.int };
    const colFat = lula => [{ t: T(lula ? 'tab.fatia_lula_1' : 'tab.fatia_flavio_1'), num: true, v: m => (lula ? m.s1 : 100 - m.s1), f: v => fmt.pct(v, 1) },
      { t: T('tab.turno2_curto'), num: true, v: m => (lula ? m.s2 : 100 - m.s2), f: v => fmt.pct(v, 1) },
      { t: T('tab.variacao'), num: true, v: m => (lula ? m.ds : -m.ds), f: v => fmt.pp(v) }];
    const colVot = [{ t: T('tab.lula_ganhos'), num: true, v: m => m.dL, f: fmt.intSinal }, { t: T('tab.flavio_ganhos'), num: true, v: m => m.dF, f: fmt.intSinal }];
    const colPeso = [{ t: T('c6.dica.mudanca'), num: true, v: m => m.dM, f: fmt.intSinal }, { t: T('c6.dica.peso'), num: true, v: m => m.peso, f: v => fmt.pct(v, 3) }];
    const colAbs = [{ t: T('tab.abst_1'), num: true, v: m => m.a1, f: v => fmt.pct(v, 1) }, { t: T('tab.turno2_curto'), num: true, v: m => m.a2, f: v => fmt.pct(v, 1) },
      { t: T('tab.variacao'), num: true, v: m => m.da, f: v => fmt.pp(v) }];
    const RANK = {
      fatiaL: { piso: true, filtro: m => m.ds > 0, ordem: (a, b) => b.ds - a.ds, cols: [colE, ...colFat(true)] },
      fatiaF: { piso: true, filtro: m => m.ds < 0, ordem: (a, b) => a.ds - b.ds, cols: [colE, ...colFat(false)] },
      votosL: { filtro: m => m.dL > 0, ordem: (a, b) => b.dL - a.dL, cols: colVot },
      votosF: { filtro: m => m.dF > 0, ordem: (a, b) => b.dF - a.dF, cols: [colVot[1], colVot[0]] },
      pesoL: { filtro: m => m.dM > 0, ordem: (a, b) => b.dM - a.dM, cols: colPeso },
      pesoF: { filtro: m => m.dM < 0, ordem: (a, b) => a.dM - b.dM, cols: colPeso },
      abstS: { piso: true, filtro: m => m.da > 0, ordem: (a, b) => b.da - a.da, cols: [colE, ...colAbs] },
      abstC: { piso: true, filtro: m => m.da < 0, ordem: (a, b) => a.da - b.da, cols: [colE, ...colAbs] },
    };
    // T36: a medida que ordena o ranking vira o gráfico (barras), com o número exato na dica e na aba Tabela
    const ppR = (v, passo) => fmt.decSinal(v, passo >= 1 ? 0 : 1), vR = (v, passo) => (Math.abs(v) >= 1e6 ? fmt.mi(v, 1) : fmt.comMil(fmt.decSinal(v / 1e3, passo >= 1e3 ? 0 : 1)));
    Object.assign(RANK.fatiaL, { g: m => m.ds, gf: v => fmt.pp(v), gt: ppR, ge: 'eixo.var_fatia_pp' });
    Object.assign(RANK.fatiaF, { g: m => -m.ds, gf: v => fmt.pp(v), gt: ppR, ge: 'vd.eixo.var_flavio' });
    Object.assign(RANK.votosL, { g: m => m.dL, gf: fmt.intSinal, gt: vR, ge: 'vd.eixo.votos_lula' });
    Object.assign(RANK.votosF, { g: m => m.dF, gf: fmt.intSinal, gt: vR, ge: 'vd.eixo.votos_flavio' });
    Object.assign(RANK.pesoL, { g: m => m.dM, gf: fmt.intSinal, gt: vR, ge: 'vd.eixo.mudanca' });
    Object.assign(RANK.pesoF, { g: m => m.dM, gf: fmt.intSinal, gt: vR, ge: 'vd.eixo.mudanca' });
    Object.assign(RANK.abstS, { g: m => m.da, gf: v => fmt.pp(v), gt: ppR, ge: 'c4.fig1.eixo' });
    Object.assign(RANK.abstC, { g: m => m.da, gf: v => fmt.pp(v), gt: ppR, ge: 'c4.fig1.eixo' });
    for (const k in RANK) RANK[k].t = T('exp.rank.' + k); // o fim do título: "onde a fatia do Lula mais subiu"
    const lembrado = X.guarda.ler('analise-exp-ranking');
    let rk = RANK[lembrado] ? lembrado : 'fatiaL';
    const opcoesRk = (grupo, ks) => ({ grupo: T('exp.rank.grupo_' + grupo), itens: ks.map(k => [k, T('exp.rank.op_' + k)]) });
    const selRk = seletor(sr, T('exp.rank.ordenar'), [
      opcoesRk('fatia', ['fatiaL', 'fatiaF']), opcoesRk('votos', ['votosL', 'votosF']),
      opcoesRk('peso', ['pesoL', 'pesoF']), opcoesRk('abst', ['abstS', 'abstC']),
    ], v => { rk = v; X.guarda.gravar('analise-exp-ranking', v === 'fatiaL' ? null : v); ranking(); });
    selRk.value = rk;
    const caixaRk = el('div', 'exp-ranking', undefined, sr);
    const nRk = ntab();
    function ranking() {
      const R = RANK[rk];
      const ls = lista.filter(m => (!R.piso || piso(m)) && R.filtro(m)).sort(R.ordem).slice(0, 20);
      caixaRk.replaceChildren();
      const titulo = T(R.piso ? 'exp.rank.titulo_piso' : 'exp.rank.titulo', { n: ls.length < 20 ? ls.length : 20, onde: R.t }) +
        (comRecorte() ? T('exp.rank.titulo_recorte', { recorte: descreve() }) : '');
      if (!ls.length) { P(caixaRk, 'exp-vazio', T(R.piso ? 'exp.rank.vazio_piso' : 'exp.rank.vazio')); return; }
      const nomeM = m => T('g.mun_uf', { nome: m.nome, uf: m.uf });
      G.tabela(caixaRk, { legenda: { n: nRk, t: titulo }, ordenavel: false, linhas: ls,
        colunas: [{ t: T('tab.municipio'), v: m => m.nome }, { t: T('tab.uf'), v: m => m.uf }].concat(R.cols),
        grafico: { desenhar: caixa => G.barras(caixa, { aria: T('vd.aria', { t: titulo }), margE: 190, margEstreito: 100, altLinha: 20, margD: 76,
          x: X.eixo(ls.map(R.g), R.gt, T(R.ge)),
          linhas: ls.map(m => ({ nome: nomeM(m), curto: m.nome.length > 13 ? m.nome.slice(0, 12).trim() + '…' : m.nome, v: R.g(m), rotulo: R.gf(R.g(m)),
            dica: { titulo: nomeM(m), linhas: R.cols.map(c => ({ t: c.t, v: c.f(c.v(m)) })) } })) }) } });
    }
    P(sr, 'exp-nota', T('exp.rank.nota'));

    // --- Dispersões: duas fixas e uma com os eixos à escolha ---
    const sd = el('section', 'exp-sub', undefined, pai);
    el('h3', '', T('exp.disp.tit'), sd);
    const PASSOS = [0.5, 1, 2, 2.5, 5, 10, 20, 25, 50];
    /** Escala de um eixo: sem o 0,5% mais extremo de cada lado (com menos de 400 municípios, todos),
     *  e com o zero dentro quando a variável tem sinal. */
    function faixaDe(vals, fixa, comZero) {
      if (fixa) return fixa;
      const v = vals.filter(x => x !== null && isFinite(x)).sort((a, b) => a - b);
      if (!v.length) return { min: -1, max: 1, passo: 1 };
      const q = p => v[Math.min(v.length - 1, Math.max(0, Math.round(p * (v.length - 1))))];
      const corte = v.length < 400 ? 0 : 0.005;
      let a = q(corte), b = q(1 - corte);
      if (comZero) { a = Math.min(a, 0); b = Math.max(b, 0); }
      if (a === b) { a -= 1; b += 1; }
      const passo = PASSOS.find(p => (b - a) / p <= 6) || 100;
      return { min: Math.floor(a / passo) * passo, max: Math.ceil(b / passo) * passo, passo };
    }
    const VARS = {
      s1: { v: m => m.s1, f: v => fmt.pct(v, 1), tick: v => fmt.comPct(nf(v, 0)), fixa: { min: 0, max: 100, passo: 25 } },
      o: { v: m => m.o, f: v => T('c3.dica.outros_v', { pct: fmt.pct(v, 1) }), tick: v => fmt.comPct(nf(v, 0)) },
      a1: { v: m => m.a1, f: v => fmt.pct(v, 1), tick: v => fmt.comPct(nf(v, 0)) },
      da: { v: m => m.da, f: v => fmt.pp(v), tick: v => fmt.decSinal(v, v % 1 ? 1 : 0) },
      lE: { v: m => Math.log10(m.E1), f: v => fmt.int(10 ** v),
        tick: v => (v >= 6 ? fmt.comMi(nf(10 ** v / 1e6, 0)) : fmt.comMil(nf(10 ** v / 1e3, 0))), fixa: { min: 3, max: 7, passo: 1 } },
      ds: { v: m => m.ds, f: v => fmt.pp(v), tick: v => fmt.decSinal(v, v % 1 ? 1 : 0), lado: m => (m.ds >= 0 ? 'l' : 'f') },
      gL: { v: m => 100 * m.dL / m.E1, f: v => fmt.comPct(fmt.decSinal(v, 2)), tick: v => fmt.comPct(fmt.decSinal(v, v % 1 ? 1 : 0)), lado: () => 'l' },
      gF: { v: m => 100 * m.dF / m.E1, f: v => fmt.comPct(fmt.decSinal(v, 2)), tick: v => fmt.comPct(fmt.decSinal(v, v % 1 ? 1 : 0)), lado: () => 'f' },
    };
    // T34: as 7 características dos municípios (IBGE) como opção do eixo horizontal; PIB por habitante e densidade em
    // escala logarítmica, como nos testes do capítulo 8. Boa Esperança do Norte (MT), sem dados (N20), fica fora do gráfico.
    const pctSoc = k => ({ v: m => m[k], f: v => fmt.pct(v, 1), tick: v => fmt.comPct(nf(v, 0)), social: true });
    for (const k of ['p60', 'alf', 'ren', 'eva', 'ppa']) VARS[k] = pctSoc(k);
    VARS.pib = { v: m => (m.pib ? Math.log10(m.pib) : null), f: v => X.socValor('pib', 10 ** v), social: true,
      tick: v => (v >= 6 ? fmt.comMi(nf(10 ** v / 1e6, 0)) : fmt.comMil(nf(10 ** v / 1e3, 0))), fixa: { min: 3.8, max: 6, passo: 1 } };
    VARS.den = { v: m => (m.den ? Math.log10(m.den) : null), f: v => X.socValor('den', 10 ** v), social: true,
      tick: v => nf(10 ** v, v < 0 ? 1 : 0), fixa: { min: -1, max: 4.2, passo: 1 } };
    for (const k in VARS) Object.assign(VARS[k], { t: T('exp.var.' + k), eixo: T('exp.var.' + k + '.eixo') });
    /** Desenha a dispersão de Y por X nos municípios do recorte; a tendência e o Brasil só sem recorte. */
    function disp(caixa, kx, ky, extra = {}) {
      const vx = VARS[kx], vy = VARS[ky];
      const base = vx.social ? lista.filter(m => vx.v(m) !== null) : lista; // sem dados sociais: fora do gráfico (N20)
      const fx = faixaDe(base.map(vx.v), vx.fixa, kx === 'da'), fy = faixaDe(base.map(vy.v), vy.fixa, true);
      let foraX = 0;
      const pontos = base.map(m => {
        let x = vx.v(m);
        if (x < fx.min || x > fx.max) { foraX++; x = Math.max(fx.min, Math.min(fx.max, x)); }
        const linhas = [{ t: vx.t, v: vx.f(vx.v(m)) }];
        if (ky === 'ds') linhas.push({ lado: 'l', t: T('dica.var_lula'), v: fmt.pp(m.ds) }, { lado: 'f', t: T('dica.var_flavio'), v: fmt.pp(-m.ds) });
        else linhas.push({ lado: vy.lado ? vy.lado(m) : undefined, t: vy.t, v: vy.f(vy.v(m)) });
        if (kx !== 'lE') linhas.push({ t: T('tab.eleitorado'), v: fmt.int(m.E1) });
        return { x, y: vy.v(m), peso: m.E1, lado: vy.lado ? vy.lado(m) : 'ink', titulo: X.nomeMun(m), linhas };
      });
      const zeroY = fy.min < 0 && fy.max > 0 && ky === 'ds';
      const sy = fy.max - fy.min;
      const foraY = G.dispersao(caixa, Object.assign({
        aria: T(comRecorte() ? 'exp.disp.aria_recorte' : 'exp.disp.aria', { n: fmt.int(lista.length), x: vx.t.toLowerCase(), y: vy.t.toLowerCase() }),
        pontos,
        x: { min: fx.min, max: fx.max, passo: fx.passo, fmt: vx.tick, rotulo: vx.eixo },
        y: { min: fy.min, max: fy.max, passo: fy.passo, fmt: vy.tick, rotulo: vy.eixo },
        rotulos: zeroY ? [{ x: fx.min + (fx.max - fx.min) * 0.01, y: 0.05 * sy, lado: 'l', t: T('c1.fig1.rot_acima'), curto: T('c3.fig1.rot_acima_curto') },
          { x: fx.min + (fx.max - fx.min) * 0.01, y: -0.11 * sy, lado: 'f', t: T('c1.fig1.rot_abaixo'), curto: T('c1.fig1.rot_abaixo_curto') }] : undefined,
      }, comRecorte() ? {} : extra));
      const fora = foraX + foraY;
      return fora ? T.p('exp.disp.fora', fora, { n: fmt.int(fora) }) : '';
    }
    const subRec = (soc = false) => { // soc: só os municípios com dados sociais (sem Boa Esperança do Norte, N20)
      const n = fmt.int(soc ? lista.filter(m => m.p60 !== null).length : lista.length);
      return comRecorte() ? T('exp.disp.sub_recorte', { recorte: descreve(), n }) : T('exp.disp.sub_todos', { n });
    };
    const nD = [nfig(), nfig(), nfig()];
    const figsD = [];
    const H1 = D.hipoteses.H1, H3 = D.hipoteses.H3;
    const FIXAS = [
      { kx: 's1', ky: 'ds', titulo: T('c1.fig1.titulo'), semRecorte: T('exp.disp.sem_rec1'), sub: T('exp.disp.sub1'),
        reta: { a: D.retas.H1.a, b: D.retas.H1.b, de: 10, ate: 90, rotulo: T('eixo.tendencia') }, marca: { x: BR.s1, y: BR.ds, rotulo: BR.nome }, cap: 1 },
      { kx: 'o', ky: 'ds', titulo: T('c3.fig1.titulo'), semRecorte: T('exp.disp.sem_rec2'), sub: T('exp.disp.sub2'),
        reta: { a: D.retas.H3.a, b: D.retas.H3.b, de: 2, ate: 25, rotulo: T('eixo.tendencia') }, marca: { x: 100 * BR.O1 / (BR.L1 + BR.F1 + BR.O1), y: BR.ds, rotulo: BR.nome }, cap: 3 },
    ];
    const tituloD = i => (comRecorte() ? T('exp.disp.no_recorte', { t: FIXAS[i].semRecorte }) : FIXAS[i].titulo);
    let livreX = X.guarda.ler('analise-exp-dx') || 'a1', livreY = X.guarda.ler('analise-exp-dy') || 'ds';
    if (!VARS[livreX] || ['ds', 'gL', 'gF'].includes(livreX)) livreX = 'a1';
    if (!['ds', 'da', 'gL', 'gF'].includes(livreY)) livreY = 'ds';
    const minusc = t => (/^\p{Lu}{2}/u.test(t) ? t : t.charAt(0).toLowerCase() + t.slice(1)); // as siglas (PIB) ficam
    const tituloLivre = () => T('exp.disp.livre_titulo', { y: VARS[livreY].t, x: minusc(VARS[livreX].t) }) + (comRecorte() ? T('exp.disp.no_recorte_fim') : '');
    const subLivre = () => T('exp.disp.livre_sub', { y: VARS[livreY].t, x: minusc(VARS[livreX].t) }) + subRec(!!VARS[livreX].social);
    figurasComAbas(sd, [
      ...FIXAS.map((F, i) => ({ rotulo: T(i ? 'exp.disp.aba2' : 'exp.disp.aba1'), montar: p => {
        figsD[i] = figura(p, { n: nD[i], titulo: tituloD(i), sub: F.sub + subRec(),
          leitura: T('exp.disp.leitura', { cap: F.cap }),
          desenhar: caixa => disp(caixa, F.kx, F.ky, { reta: F.reta, marca: F.marca }),
          como: [T.f('exp.disp.como1'), i ? T.f('c3.fig1.como1') : T('exp.disp.como_tendencia'), dadosComo(['municipios', 'hipoteses'], [3, 6])],
          notas: ['N06', 'N14'] });
        el('a', 'ir exp-ir', T('res.ir_cap', { n: F.cap }), $('.fig-rodape', figsD[i])).href = '#analise/' + F.cap;
      } })),
      { rotulo: T('exp.disp.aba3'), montar: p => {
        const ctl = el('div', 'exp-recorte exp-eixos', undefined, p);
        const sx = seletor(ctl, T('exp.disp.horizontal'), [
          { grupo: T('exp.disp.grupo_eleicao'), itens: [['s1', VARS.s1.t], ['o', VARS.o.t], ['a1', VARS.a1.t], ['da', VARS.da.t], ['lE', T('exp.disp.log', { t: VARS.lE.t })]] },
          { grupo: T('exp.disp.grupo_sociais'), itens: X.SOC_VARS.map(k => [k, ['pib', 'den'].includes(k) ? T('exp.disp.log', { t: VARS[k].t }) : VARS[k].t]) }], v => {
          livreX = v; X.guarda.gravar('analise-exp-dx', v); retitular(figsD[2], tituloLivre(), subLivre()); redesenharEm(figsD[2]);
        });
        const sy = seletor(ctl, T('exp.disp.vertical'), [['ds', VARS.ds.t], ['da', VARS.da.t], ['gL', VARS.gL.t], ['gF', VARS.gF.t]], v => {
          livreY = v; X.guarda.gravar('analise-exp-dy', v); retitular(figsD[2], tituloLivre(), subLivre()); redesenharEm(figsD[2]);
        });
        sx.value = livreX; sy.value = livreY;
        figsD[2] = figura(p, { n: nD[2], titulo: tituloLivre(), sub: subLivre(),
          leitura: T('exp.disp.livre_leitura'),
          desenhar: caixa => disp(caixa, livreX, livreY),
          como: [T('exp.disp.livre_como', { pct: fmt.pct(0.5, 1) }), dadosComo(['municipios'], [3])],
          notas: ['N05', 'N06', 'N19', 'N20'] });
      } },
    ], 'exp-disp');

    // --- Funil ---
    const sf = el('section', 'exp-sub', undefined, pai);
    el('h3', '', T('c1.funil.secao'), sf);
    const nFu = [nfig(), nfig()];
    figurasComAbas(sf, [
      { rotulo: T('exp.mapa.modo_ds'), montar: p => X.funilFig(p, nFu[0], 'var_fatia', m => m.ds, T('eixo.var_fatia_pp'),
        T('c1.funil.titulo'), T('exp.funil.sub_fatia'), 'l', 'f', () => lista) },
      { rotulo: T('exp.mapa.modo_da'), montar: p => X.funilFig(p, nFu[1], 'var_abstencao', m => m.da, T('c4.fig1.eixo'),
        T('c4.funil.titulo'), T('c4.funil.sub'), 'ink', 'ink', () => lista) },
    ], 'exp-funil');
    P(sf, 'exp-nota', T('exp.funil.nota', { mun: fmt.int(5571) }));

    function mudou() {
      lista = filtra();
      conta.replaceChildren(...(lista.length ? T.fp('exp.conta', lista.length, { n: B(fmt.int(lista.length)) }) : T.f('exp.conta.zero', { n: B(fmt.int(0)) })),
        comRecorte() ? T('exp.conta.recorte', { recorte: descreve() }) : T('exp.conta.brasil'));
      if (comRecorte()) conta.append(limpar);
      ranking();
      figsD.forEach((f, i) => f && retitular(f, i < 2 ? tituloD(i) : tituloLivre(), i < 2 ? FIXAS[i].sub + subRec() : subLivre()));
      redesenharEm(sd); redesenharEm(sf);
    }
    mudou();
  })();

  // ======================= 4. Hipótese e incerteza =======================
  (function incerteza() {
    const pai = $('#exp-incerteza');
    const pct1 = v => fmt.comPct(nf(v * 100, 1));
    const icPct = ic => T('exp.inc.de_a', { a: nf(ic[0] * 100, 1), b: nf(ic[1] * 100, 1) });

    // --- Voto dividido, por cargo: todas as versões do teste ---
    const sv = el('section', 'exp-sub', undefined, pai);
    el('h3', '', T('exp.voto.tit'), sv);
    const H5 = D.h5;
    figurasComAbas(sv, ['federal', 'estadual', 'senador'].map(c => ({ rotulo: T('exp.voto.aba_' + c), montar: p => {
      const vs = H5[c].versoes.filter(v => !/escala contínua$/.test(v.versao)); // outra unidade: fica na tabela
      const cruzam = vs.filter(v => v.ic95[0] <= 0 && v.ic95[1] >= 0).length;
      const lim = Math.max(0.3, ...vs.flatMap(v => v.ic95.map(x => Math.abs(x * 10))));
      const max = Math.ceil(lim * 10) / 10;
      figura(p, { n: nfig(),
        titulo: T(cruzam === vs.length ? 'exp.voto.titulo_todas' : 'exp.voto.titulo_algumas', { cargo: H5[c].cargo, n: cruzam, total: vs.length }),
        sub: T('exp.voto.sub'),
        leitura: T('exp.voto.leitura', { classe: X.classeTexto(vs[0]).toLowerCase(),
          conf: X.partesConferencias(H5[c]).iguais ? T('exp.voto.conf_iguais') : T('exp.voto.conf_partes', { partes: X.partesConferencias(H5[c]).texto }) }),
        desenhar: caixa => G.coeficientes(caixa, {
          aria: T('exp.voto.aria', { cargo: H5[c].cargo }),
          x: { min: -max, max, passo: max > 0.6 ? 0.2 : 0.1, fmt: v => fmt.decSinal(v, 1), rotulo: T('c5.fig1.eixo') },
          lados: [T('c5.fig1.esq'), T('forest.dir_previsto')], margE: 250, margEstreito: 110, altLinha: 22,
          linhas: vs.map(v => ({ nome: X.nomeVersao(v), curto: X.curtoVersao(v, 1).slice(0, 18), v: v.coef * 10, ic: v.ic95.map(x => x * 10), destaque: /principal$/.test(v.versao),
            dica: { titulo: X.nomeVersao(v), linhas: [{ t: T('c5.dica.coef10'), v: X.coefTxt(v.coef, 10) }, { t: T('tab.ic95'), v: X.icTxt(v.ic95, 10) },
              { t: T('dica.valor_p'), v: fmt.p(v.p_selvagem) }, { t: T('tab.municipios'), v: fmt.int(v.n) }, { t: T('tab.resultado'), v: X.classeTexto(v) }] } })),
        }),
        fonte: T('exp.voto.fonte'),
        como: [T.f('exp.voto.como1'), T('exp.voto.como2', { p: nf(0.05, 2) }), dadosComo(['partidos', 'esquerda_municipios', 'hipoteses'], [4, 5, 6])],
        notas: c === 'senador' ? ['N01', 'N02', 'N10', 'N11', 'N13', 'N14', 'N15'] : ['N02', 'N10', 'N11', 'N13', 'N14'] });
      const d = el('details', 'det-aninhado', undefined, p);
      el('summary', '', T('exp.voto.todas'), d);
      const fat5 = v => (/escala contínua$/.test(v.versao) ? 1 : 10);
      X.tabelaVersoes(d, ntab(), T('c5.chegou.tabela', { cargo: H5[c].cargo }), H5[c].versoes, fat5, X.graficoVersoes(H5[c].versoes, fat5, T('un.10pontos')));
    } })), 'exp-voto');
    const cap5 = el('a', '', T('res.ir_cap', { n: 5 })); cap5.href = '#analise/5';
    P(sv, 'exp-nota', ...T.f('exp.voto.nota', { link: cap5 }));

    // --- De onde vieram os votos: Brasil, as três fontes ---
    const so = el('section', 'exp-sub', undefined, pai);
    el('h3', '', T('exp.inc.vieram_tit'), so);
    const E = D.ecologica.brasil, FS = D.ecologica.fontes_sem_exterior, PL = D.por_lugar;
    // [chave, nome, curto, "dos votos dos outros candidatos" (a parte de quê), nome sem "no 1º turno"]
    const FONTES = ['O', 'C', 'R'].map(k => [k, T('fonte.' + k), T('fonte.' + k + '.curto'), T('fonte.' + k + '.de_que'), T('fonte.' + k + '.aba')]);
    // T32 (M1): as mesmas três contas do capítulo 3 para os votos dos outros
    figura(so, { n: nfig(), titulo: T('c3.fig2.titulo', X.faixaOutros()),
      sub: T('exp.inc.vieram_sub'),
      leitura: T('exp.inc.vieram_leitura'),
      legenda: [{ t: T('leg.ic95'), tipo: 'ic' }],
      desenhar: caixa => G.divisao(caixa, { aria: T('c3.fig2.aria'), rotuloX: T('c3.fig2.eixo'), margE: 250, margEstreito: 92, linhas: X.linhasVieram() }),
      fonte: T('c3.fig2.fonte', { mun: fmt.int(5571), sec: X.comumSecoes().sec }),
      como: [T.f('exp.inc.vieram_como1'), T('exp.inc.vieram_como2', { n: fmt.int(1000) }), dadosComo(['de_onde_vieram'], [6])],
      notas: ['N06', 'N07', 'N16', 'N21', 'N22'] });

    // --- Por lugar, fonte por fonte: o comparecimento primeiro ---
    const sl = el('section', 'exp-sub', undefined, pai);
    el('h3', '', T('exp.inc.lugar_tit'), sl);
    const nomeL = l => (l.nivel === 'uf' ? NOME_UF[l.lugar] : l.lugar);
    figurasComAbas(sl, [FONTES[1], FONTES[0], FONTES[2]].map(([k, nomeF, , doQue, nomeAba]) => ({ rotulo: nomeAba, montar: p => {
      const passa = l => l.fontes[k].passa;
      const caiu = l => k === 'C' && l.saldo_comparecimento === 'caiu';
      const linha = (l, destaque) => {
        const c = l.fontes[k], sigla = l.nivel === 'uf' ? l.lugar : l.codigo;
        const marca = s => (c.passa && c.aviso_modelo ? T('g.aviso_nome', { nome: s }) : s); // T32 (m1)
        return { nome: marca(caiu(l) ? T('c4.caiu_seta', { lugar: nomeL(l) }) : nomeL(l)), curto: marca(caiu(l) ? T('c4.caiu_seta_curto', { lugar: sigla }) : sigla),
          destaque, lula: c.lula, ic: c.lula_ic95, naoDeu: c.passa ? null : c.motivo,
          dica: { titulo: nomeL(l), linhas: c.passa ? [
            ...(k === 'C' ? [{ t: T(caiu(l) ? 'c4.dica.caiu' : 'c4.dica.subiu'), v: fmt.intSinal(l.var_comparecimento) }] : []),
            { lado: 'l', t: T('nome.lula'), v: T('dica.v_par', { v: pct1(c.lula), p: icPct(c.lula_ic95) }) }, { lado: 'f', t: T('nome.flavio'), v: T('dica.v_par', { v: pct1(c.flavio), p: icPct(c.flavio_ic95) }) },
            { t: T('tab.municipios'), v: fmt.int(l.n) }, { t: T('tab.secoes'), v: fmt.int(l.secoes) }].concat(c.aviso_modelo ? [{ t: T('dica.aviso_modelo'), v: T('dica.aviso_modelo_txt') }] : [])
            : [{ t: T('dica.nao_deu'), v: '' }, { t: T('dica.motivo'), v: c.motivo }, { t: T('tab.municipios'), v: fmt.int(l.n) }] } };
      };
      const ufs = PL.filter(l => l.nivel === 'uf');
      const linhas = [linha(PL[0], true), { grupo: T('c4.grupo.regioes') }, ...PL.filter(l => l.nivel === 'regiao').map(l => linha(l)), { grupo: T('exp.estados.tit') },
        ...ufs.filter(passa).sort((a, b) => b.fontes[k].lula - a.fontes[k].lula).map(l => linha(l)),
        ...ufs.filter(l => !passa(l)).sort((a, b) => nomeL(a).localeCompare(nomeL(b), T.lingua)).map(l => linha(l))];
      const deu = ufs.filter(passa), mL = deu.filter(l => l.fontes[k].maior_parte === 'Lula').length, mF = deu.filter(l => l.fontes[k].maior_parte === 'Flávio').length;
      const lugaresDeu = PL.filter(passa).map(nomeL);
      // T35: quando todos os estados que deram ficam com o mesmo candidato, "em todos" (e não "com o outro em 0"), igual para os dois
      const todosDe = mL === deu.length ? 'nome.lula' : mF === deu.length ? 'nome.flavio' : null;
      const titulo = deu.length
        ? todosDe ? T('exp.inc.lugar_titulo_todos', { n: deu.length, de_que: doQue, quem: T(todosDe) })
          : T(deu.length - mL - mF ? 'exp.inc.lugar_titulo_sem_lado' : 'exp.inc.lugar_titulo', { n: deu.length, de_que: doQue, l: mL, f: mF, s: deu.length - mL - mF })
        : lugaresDeu.length ? T('exp.inc.lugar_titulo_poucos', { fonte: nomeAba, n: lugaresDeu.length, total: PL.length, lugares: listaE(lugaresDeu) })
          : T('exp.inc.lugar_titulo_nenhum', { fonte: nomeF });
      figura(p, { n: nfig(), titulo,
        sub: T('exp.inc.lugar_sub', { de_que: doQue }),
        leitura: T('exp.inc.lugar_leitura', { reg: PL.filter(l => l.nivel === 'regiao' && passa(l)).length, ufs: deu.length }) +
          (k === 'C' ? T('exp.inc.lugar_leitura_caiu') : '') +
          (PL.some(l => l.fontes[k].passa && l.fontes[k].aviso_modelo) ? T('exp.inc.lugar_leitura_aviso', { marca: T('g.aviso_marca') }) : '') + T('exp.inc.lugar_leitura_fim'), // T35: sem †, sem a frase
        legenda: [{ t: T('leg.ic95'), tipo: 'ic' }],
        desenhar: caixa => G.divisao(caixa, { aria: T('exp.inc.lugar_aria', { de_que: doQue }), linhas,
          rotuloX: T('exp.inc.lugar_eixo_' + k), margE: 150, margEstreito: 40, altLinha: 20 }),
        fonte: T('c4.fig2.fonte'),
        como: [T.f('exp.inc.lugar_como1'), T.f('c4.fig2.como2'), T('exp.inc.lugar_como3'), dadosComo(['de_onde_vieram'], [6])],
        notas: k === 'C' ? ['N05', 'N07', 'N16', 'N21', 'N22'] : ['N07', 'N16', 'N21', 'N22'] });
    } })), 'exp-lugar');

    // --- Erro da projeção ao vivo, por faixa de urnas apuradas ---
    const se = el('section', 'exp-sub', undefined, pai);
    el('h3', '', T('exp.proj.tit'), se);
    const PR = D.projecao, fx = PR.faixas.filter(f => f.projecao && f.projecao.erro_medio !== null && f.projecao.erro_medio !== undefined);
    const menor = fx.filter(f => Math.abs(f.projecao.erro_medio) < Math.abs(f.parcial.erro_medio)).length;
    const todos = fx.flatMap(f => [f.projecao.erro_medio, f.parcial.erro_medio]);
    const figProj = figura(se, { n: nfig(),
      titulo: menor === fx.length ? T('exp.proj.titulo_todas') : T('exp.proj.titulo_algumas', { n: menor, total: fx.length }),
      sub: T('exp.proj.sub'),
      leitura: T('exp.proj.leitura'),
      desenhar: caixa => G.linhasPontos(caixa, {
        aria: T('exp.proj.aria'),
        x: { min: Math.floor(Math.min(0, ...todos)), max: Math.max(0.5, Math.ceil(Math.max(...todos) * 2) / 2),
          passo: Math.max(...todos) - Math.min(0, ...todos) > 4 ? 1 : 0.5, fmt: v => fmt.decSinal(v, v % 1 ? 1 : 0), rotulo: T('exp.proj.eixo') },
        margE: 110, margEstreito: 64, altLinha: 22, topo: 30, series: { ink: T('c7.fig1.rot_proj'), muted: T('c7.fig1.rot_parc') },
        linhas: fx.map(f => { const [a, b] = f.faixa.split(' a ');
          return { nome: T('exp.proj.faixa_nome', { a, b }), curto: T('exp.proj.faixa_curto', { a, b }),
          vals: [{ v: f.projecao.erro_medio, lado: 'ink' }, { v: f.parcial.erro_medio, lado: 'muted' }],
          dica: { titulo: T('exp.proj.faixa_dica', { a, b }), linhas: [{ lado: 'ink', t: T('c7.tab.proj_medio'), v: fmt.decSinal(f.projecao.erro_medio, 3) },
            { lado: 'muted', t: T('g.contagem_parcial'), v: fmt.decSinal(f.parcial.erro_medio, 3) }, { t: T('c7.tab.leituras'), v: String(f.leituras) }] } }; }),
      }),
      fonte: T('c7.fig1.fonte'),
      como: [T.f('exp.proj.como1', { final: fmt.pct(PR.resultado_final_pct, 3) }), T('exp.proj.como2', { n: PR.leituras }), dadosComo(['apuracao_ao_vivo'], [7])],
      notas: ['N17'] });
    G.juntar(figProj, X.tabelaErroFaixas(se, ntab(), false)); // T36: a tabela na mesma figura do gráfico
    const cap7 = el('a', '', T('res.ir_cap', { n: 7 })); cap7.href = '#analise/7';
    P(se, 'exp-nota', ...T.f('exp.proj.nota', { link: cap7 }));
  })();
};
