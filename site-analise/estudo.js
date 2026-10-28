/* Página do estudo, no caderno de apuração (T07, esqueleto; T08, os 7 capítulos; T29, o caderno no
   estudo inteiro; T34, o 8º; T33, o 9º). O Resumo, os 9 capítulos e os comentários correm numa rolagem só, com o índice
   fixo dos capítulos (diário, D34); Explorar e Método e fontes ficam à parte, porque são de
   consulta. Cada capítulo tem um endereço (#analise/3), que o índice e o botão voltar usam, e as
   notas sobre os dados continuam em #metodo/nota-N08. Os "Como calculamos" viraram notas em
   sobrescrito, com o texto no fim da leitura. Todos os números vêm de dados.js
   (scripts/pagina_dados.py) e são arredondados uma vez, na hora de mostrar (diário, D25). Os
   textos vêm do catálogo da língua da página (textos/pt-BR.js, lingua.js; T30) e são rascunho: a
   redação final é do T11 (diário, D23). */
(function () {
  'use strict';
  const D = window.ESTUDO, G = window.GRAFICOS, T = window.T, { fmt, nf } = G;
  const html = document.documentElement;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const guarda = {
    ler(k) { try { return localStorage.getItem(k); } catch (_) { return null; } },
    gravar(k, v) { try { v === null ? localStorage.removeItem(k) : localStorage.setItem(k, v); } catch (_) {} },
  };
  const semMovimento = () => matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---------- Textos que vêm dos dados, na língua da página ----------
  // Nomes de região, "Brasil", cargos, fontes de votos e motivos de "não deu" estão em português nos
  // dados (scripts/pagina_dados.py); o catálogo traz cada um como "dado.<texto>". Os nomes dos estados
  // e dos municípios não se traduzem. Os dados ficam com o nome na língua da página daqui em diante.
  const TD = s => (typeof s === 'string' && T.tem('dado.' + s) ? T('dado.' + s) : s);
  (function localizarDados() {
    const COD_REGIAO = Object.fromEntries([D.brasil, ...D.regioes].map(r => [r.nome, r.codigo]));
    for (const u of [D.brasil, ...D.regioes]) u.nome = TD(u.nome);
    for (const u of D.ufs) { u.regiao = TD(u.regiao); if (u.codigo === 'ZZ') u.nome = TD(u.nome); }
    for (const l of D.por_lugar) {
      if (l.nivel !== 'uf') { l.codigo = COD_REGIAO[l.lugar]; l.lugar = TD(l.lugar); }
      for (const f of Object.values(l.fontes)) { f.fonte = TD(f.fonte); if (f.motivo) f.motivo = TD(f.motivo); }
    }
    for (const l of D.nao_deu) { if (l.nivel !== 'uf') l.lugar = TD(l.lugar); l.fonte = TD(l.fonte); l.motivo = TD(l.motivo); }
    for (const l of D.por_lugar_municipios) l.lugar = TD(l.lugar); // T35: a conta entre municípios, ao lado da por seção (tabela do capítulo 4)
    for (const c of ['federal', 'estadual', 'senador']) D.h5[c].cargo = TD(D.h5[c].cargo);
  })();

  // ---------- Dados: unidades e municípios, com as contas da seção 4 da especificação ----------
  const BR = D.brasil;
  for (const u of [BR, ...D.regioes, ...D.ufs]) { u.dL = u.L2 - u.L1; u.dF = u.F2 - u.F1; }
  const UFS = D.ufs.filter(u => u.codigo !== 'ZZ');
  const NOME_UF = Object.fromEntries(D.ufs.map(u => [u.codigo, u.nome]));
  const REGIAO_UF = Object.fromEntries(D.ufs.map(u => [u.codigo, u.regiao]));
  const PORTE = Object.fromEntries([1, 2, 3, 4, 5].map(k => [k, T('mun.porte' + k)]));
  let MUN = null;
  function municipios() {
    if (MUN) return MUN;
    const cs = D.municipios.campos;
    MUN = D.municipios.linhas.split('\n').map(l => {
      const p = l.split('|'), m = { nome: p[0], uf: p[1], capital: p[2] === '1', porte: p[3] };
      for (let i = 4; i < cs.length; i++) m[cs[i]] = p[i] === '' ? null : +p[i]; // dado social vazio: exterior e N20
      m.BN1 = m.C1 - m.L1 - m.F1 - m.O1; m.BN2 = m.C2 - m.L2 - m.F2;
      m.s1 = m.L1 + m.F1 ? 100 * m.L1 / (m.L1 + m.F1) : null;
      m.s2 = m.L2 + m.F2 ? 100 * m.L2 / (m.L2 + m.F2) : null;
      m.ds = m.s1 !== null && m.s2 !== null ? m.s2 - m.s1 : null;
      m.dL = m.L2 - m.L1; m.dF = m.F2 - m.F1;
      m.M1 = m.L1 - m.F1; m.M2 = m.L2 - m.F2; m.dM = m.M2 - m.M1;
      m.cap = m.dL + m.dF > 0 ? 100 * m.dL / (m.dL + m.dF) : null;
      m.a1 = 100 * (m.E1 - m.C1) / m.E1; m.a2 = 100 * (m.E2 - m.C2) / m.E2; m.da = m.a2 - m.a1;
      m.o = m.L1 + m.F1 + m.O1 ? 100 * m.O1 / (m.L1 + m.F1 + m.O1) : null;
      m.peso = 100 * m.dM / BR.dM;
      m.exterior = m.uf === 'ZZ';
      return m;
    });
    return MUN;
  }
  const doBrasil = () => municipios().filter(m => !m.exterior);
  const acimaDoPiso = () => doBrasil().filter(m => m.E1 > 10000); // piso dos rankings em p.p. (HIPOTESES 5.1)
  const nomeMun = m => T('mun.nome', { nome: m.nome, uf: m.exterior ? T('mun.exterior') : m.uf });

  // ---------- Pequenos ajudantes de texto ----------
  function el(tag, cls, texto, pai) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (texto !== undefined && texto !== null) e.textContent = texto;
    if (pai) pai.appendChild(e);
    return e;
  }
  const B = t => el('b', '', t);
  function P(pai, cls, ...partes) {
    const p = el('p', cls, undefined, pai);
    for (const x of partes) p.append(x);
    return p;
  }
  const listaE = T.lista;
  // a forma de plural sem arredondar o número: em português, "ponto" abaixo de 2 (i = 0..1)
  const pontos = (v, c = 2) => T.p('un.pontos', v, { n: fmt.abs(v, c) }, { minimumFractionDigits: c, maximumFractionDigits: 20 });
  /** Número em destaque: algarismos alinhados no meio dos algarismos de texto; não quebra a linha
   *  entre o número e a unidade. */
  const N = t => el('b', 'num', t.replace(/ /g, ' '));
  function ir(pai, href, texto) {
    pai.append(' ');
    const a = el('a', 'ir', texto, pai);
    a.href = href;
    return a;
  }
  // a chave da classificação no catálogo, sem acento: confirmada, contraria, inconclusiva
  const classeChave = c => 'hip.classe.' + String(c).normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  const classeTexto = v => (v.pequena && v.classificacao !== 'inconclusiva'
    ? T('hip.classe_pequena', { classe: T(classeChave(v.classificacao)) }) : T(classeChave(v.classificacao)));
  // As versões de cada teste vêm dos dados com um nome interno (inferencia.json); o catálogo dá o nome para o leitor.
  const VERSAO = {
    principal: 'principal', Brasil: 'brasil', 'sem peso, dentro dos estados': 'sem_peso_estados', 'sem peso, Brasil': 'sem_peso_brasil',
    'conjunto, dentro dos estados': 'conjunto_estados', 'conjunto, Brasil': 'conjunto_brasil', 'sem peso': 'sem_peso',
    'escala contínua': 'escala_continua', 'fatia entre os dois': 'fatia_dois', 'Missão pela regra B': 'missao_b',
    'com sub judice': 'com_sub_judice', 'sem sub judice acima de 5%': 'sem_sub_judice_5', 'com os outros no controle': 'outros_controle',
    'rodada de 2018': 'rodada_2018', 'espelho Flávio': 'espelho',
  };
  const chaveVersao = v => v.versao.replace(/^H\d (federal |estadual |senador )?/, '');
  const nomeVersao = v => (VERSAO[chaveVersao(v)] ? T('versao.' + VERSAO[chaveVersao(v)]) : chaveVersao(v));
  // [no gráfico, no celular]; as versões sem nome curto usam o nome inteiro
  const curtoVersao = (v, i) => {
    const k = VERSAO[chaveVersao(v)];
    return k && T.tem('versao.' + k + '.curto') ? T('versao.' + k + (i ? '.cel' : '.curto')) : nomeVersao(v);
  };

  // ---------- Notas em sobrescrito, no lugar do "ⓘ Como calculamos" ----------
  // Número: a conta, com o texto nas notas do fim da leitura (#nota-3). Código: a nota sobre os
  // dados, em Método e fontes (#metodo/nota-N08), endereço que a busca e o T28 também usam.
  const TITULO_NOTA = Object.fromEntries(D.notas.map(n => [n.id, T('nota.' + n.id)]));
  const notas = [], numNota = {};
  function sup(pai, chave, titulo, paragrafos) {
    if (!(chave in numNota)) { notas.push({ titulo, paragrafos }); numNota[chave] = notas.length; }
    const n = numNota[chave];
    const s = el('sup', 'nota-sup', undefined, pai);
    const a = el('a', '', String(n), s);
    a.href = '#nota-' + n;
    a.title = titulo;
    a.setAttribute('aria-label', T('nota.aria', { n, titulo }));
    return s;
  }
  function notaDados(pai, id) {
    const s = el('sup', 'nota-sup', undefined, pai);
    const a = el('a', '', id, s);
    a.href = '#metodo/nota-' + id;
    a.title = TITULO_NOTA[id] || '';
    a.setAttribute('aria-label', T('nota.dados_aria', { id, titulo: TITULO_NOTA[id] || '' }));
    return s;
  }
  const nd = id => notaDados(el('span'), id); // para entrar no meio de uma frase montada com P()
  // A última linha de cada "Como calculamos" (T12): os arquivos para baixar, com link, e os passos de
  // Método e fontes (#metodo/passo-3) que os geram.
  const PASTA_CSV = T.raiz + 'csv/' + T.linguas.find(l => l.codigo === T.lingua).pasta;
  function listaNos(nos) {
    const s = el('span');
    if (nos.length < 2) { s.append(...nos); return s; }
    for (const p of new Intl.ListFormat(T.lingua, { type: 'conjunction' }).formatToParts(nos.map((_, i) => String(i))))
      s.append(p.type === 'element' ? nos[+p.value] : p.value);
    return s;
  }
  function dadosComo(arquivos, passos) {
    const arqs = arquivos.map(n => { const a = el('a', '', n + '.csv'); a.href = PASTA_CSV + n + '.csv'; a.setAttribute('download', ''); return a; });
    const ps = passos.map(n => { const a = el('a', '', T('como.passo', { n })); a.href = '#metodo/passo-' + n; return a; });
    return T.f('como.dados', { arquivos: listaNos(arqs), passos: listaNos(ps) });
  }
  const COMO = {
    fatia: [T('como.fatia.tit'), [
      T.f('como.fatia.1'),
      T('como.fatia.2', { l2: fmt.int(BR.L2), dois: fmt.int(BR.L2 + BR.F2), s2: fmt.pct(BR.s2, 2) }),
      T('como.fatia.3'), dadosComo(['estados'], [1, 2, 3])]],
    diferenca: [T('como.diferenca.tit'), [
      T.f('como.diferenca.1'),
      T('como.diferenca.2', { m1: fmt.intSinal(BR.M1), m2: fmt.intSinal(BR.M2), dm: fmt.int(BR.dM) }),
      T('como.diferenca.3'), dadosComo(['estados'], [1, 2, 3])]],
    captura: [T('como.captura.tit'), [
      T.f('como.captura.1'),
      T('como.captura.2', { dl: fmt.int(BR.dL), dois: fmt.int(BR.dL + BR.dF), cap: fmt.pct(BR.cap, 1), capf: fmt.pct(100 - BR.cap, 1) }),
      T('como.captura.3'), dadosComo(['estados'], [1, 2, 3])]],
    // D73: os votos a mais dos dois = aumento do comparecimento + votos dos outros no 1º turno + queda de
    // brancos e nulos (conta de soma; pagina_dados.py confere que fecha no Brasil e em cada UF)
    fontes: [T('como.fontes.tit'), [
      T('como.fontes.1'),
      T('como.fontes.2', { c: fmt.int(BR.C2 - BR.C1), o: fmt.int(BR.O1), b: fmt.int(BR.BN1 - BR.BN2), n: fmt.int(BR.dL + BR.dF) }),
      T('como.fontes.3'), dadosComo(['estados'], [1, 2, 3])]],
    ecologica: [T('como.ecologica.tit'), [
      T('como.ecologica.1', { mun: fmt.int(5571) }),
      T('como.ecologica.2'), dadosComo(['de_onde_vieram'], [6])]],
  };
  const notaComo = (pai, chave) => sup(pai, chave, COMO[chave][0], COMO[chave][1]);

  // ---------- Gráficos: desenha quando a caixa ganha largura e de novo quando ela muda ----------
  const redesenhos = [];
  function grafico(pai, desenhar, cls = '') {
    const caixa = el('div', 'grafico ' + cls, undefined, pai);
    let ultima = -1;
    const ro = new ResizeObserver(() => {
      const w = Math.round(caixa.clientWidth);
      if (w > 0 && w !== ultima) { ultima = w; G.dicaEsconder(); desenhar(caixa); }
    });
    ro.observe(caixa);
    // redesenhar(): para quando os dados mudam (os recortes do Explorar); escondida, desenha ao aparecer
    caixa.redesenhar = () => { if (caixa.clientWidth > 0) { G.dicaEsconder(); desenhar(caixa); } else ultima = -1; };
    redesenhos.push(() => { if (caixa.clientWidth > 0) desenhar(caixa); });
    return caixa;
  }

  // ---------- T36: o eixo de um gráfico de tabela, com um passo redondo e o zero dentro ----------
  function eixo(vals, f, rotulo, { zero = true, folga = 0 } = {}) {
    let a = Math.min(...vals), b = Math.max(...vals);
    if (zero) { a = Math.min(0, a); b = Math.max(0, b); }
    const bruto = (b - a) / 5 || 1, ord = 10 ** Math.floor(Math.log10(bruto));
    const passo = [1, 2, 2.5, 5, 10].map(k => k * ord).find(k => k >= bruto);
    return { min: Math.floor((a - folga) / passo) * passo, max: Math.ceil((b + folga) / passo) * passo, passo, fmt: v => f(v, passo), rotulo };
  }
  const casas = passo => (passo >= 1 ? 0 : passo >= 0.1 ? 1 : 2);
  /** A dica de uma linha de tabela no gráfico: todas as colunas, com o número exato (o gráfico mostra a ideia). */
  const dicaColunas = (colunas, l, titulo) => ({ titulo, linhas: colunas.map(c => {
    const v = c.v(l);
    return { t: c.t, v: c.f ? c.f(v, l) : (v === null || v === undefined ? fmt.vazio : String(v)) };
  }) });

  // ======================= Resumo =======================
  (function linhaFina() {
    const p = $('#linha-fina');
    p.append(...T.f('res.linha_fina', { m1: N(fmt.miAbs(-BR.M1)), m2: N(fmt.miAbs(BR.M2)), dm: N(fmt.miAbs(BR.dM)),
      nota: notaComo(el('span'), 'diferenca') }));
  })();

  grafico($('#grafico-virada'), caixa => G.virada(caixa, {
    aria: T('res.virada_aria', { m1: fmt.int(Math.abs(BR.M1)), m2: fmt.int(Math.abs(BR.M2)), dm: fmt.int(BR.dM) }),
    M1: BR.M1, M2: BR.M2, L: [BR.L1, BR.L2], F: [BR.F1, BR.F2], colunas: [T('g.turno1'), T('g.turno2')],
    fotos: { l: T.raiz + 'img/lula.jpeg', f: T.raiz + 'img/flavio.jpeg' },
  }));

  (function fita() {
    const f = $('#fita');
    el('p', 'fita-cab', T('res.fita_cab'), f);
    el('p', 'fita-centro', T('res.fita_sub'), f);
    el('hr', '', undefined, f);
    const t = el('table', '', undefined, f);
    const cab = el('tr', '', undefined, el('thead', '', undefined, t));
    ['', T('g.turno1'), T('g.turno2')].forEach(c => { const th = el('th', '', c, cab); th.scope = 'col'; });
    const tb = el('tbody', '', undefined, t);
    const linha = (rot, a, b, cls) => {
      const r = el('tr', cls || '', undefined, tb);
      const th = el('th', '', rot, r); th.scope = 'row';
      el('td', '', a, r); el('td', '', b, r);
    };
    linha(T('res.fita_lula'), fmt.int(BR.L1), fmt.int(BR.L2));
    linha(T('res.fita_flavio'), fmt.int(BR.F1), fmt.int(BR.F2));
    linha(T('res.fita_diferenca'), fmt.intSinal(BR.M1), fmt.intSinal(BR.M2), 'fita-forte');
    el('hr', '', undefined, f);
    el('p', 'fita-centro', T('res.fita_mudou', { dm: fmt.intSinal(BR.dM) }), f);
    el('p', 'fita-centro', T('res.fita_fonte'), f);
  })();

  // Os achados do topo (T11): um por capítulo, cada um começando pelo número em destaque
  (function achados() {
    const ol = $('#lista-achados');
    const nota = chave => notaComo(el('span'), chave);
    const achado = (cap, chave, vals) => {
      const p = el('p', '', undefined, el('li', '', undefined, ol));
      p.append(...T.f(chave, vals));
      ir(p, '#analise/' + cap, T('res.ir_cap', { n: cap }));
    };
    const ds = UFS.map(u => u.ds), subiu = UFS.filter(u => u.ds > 0).length;
    achado(6, 'res.ach.estados', { n: N(subiu === UFS.length ? T('res.ach.todos', { n: subiu }) : T('res.ach.n_de', { a: subiu, b: UFS.length })), min: fmt.abs(Math.min(...ds), 2),
      max: T.p('un.pontos', Math.max(...ds), { n: fmt.abs(Math.max(...ds), 2) }, { minimumFractionDigits: 2, maximumFractionDigits: 20 }),
      nota: nota('fatia') });
    achado(1, 'res.ach.mais_fraco', { n: N(pontos(-D.hipoteses.H1.versoes[0].coef * 10)) });
    const ganhou = UFS.filter(u => u.dF > 0), pf = u => u.dF / u.E1;
    achado(2, 'res.ach.flavio', { n: N(fmt.miAbs(BR.dF)), ufs: ganhou.length,
      lista: listaE(ganhou.slice().sort((a, b) => pf(b) - pf(a)).slice(0, 3).map(u => u.nome)) });
    // T32 (M1): no lugar do "61 de cada 100", que dependia do modelo, uma contagem: a captura (HIPOTESES.md, seção 8)
    const capL = Math.round(BR.cap);
    achado(3, 'res.ach.outros', { n: N(fmt.miAbs(BR.dL + BR.dF)), l: fmt.comPct(nf(capL, 0)), f: fmt.comPct(nf(100 - capL, 0)), nota: nota('captura') });
    // D73 (recado do autor): a pergunta do debate, de onde vieram os votos a mais, numa conta de soma
    achado(3, 'res.ach.fontes', { n: fmt.miAbs(BR.dL + BR.dF), c: N(fmt.miAbs(BR.C2 - BR.C1)), o: fmt.miAbs(BR.O1), b: fmt.miAbs(BR.BN1 - BR.BN2), nota: nota('fontes') });
    achado(4, 'res.ach.abstencao', { n: N(fmt.miAbs(BR.C2 - BR.C1)), a1: fmt.pct(BR.a1, 2), a2: fmt.pct(BR.a2, 2),
      ufs: UFS.filter(u => u.da > 0).length });
    // a mesma conta do capítulo 7: a primeira faixa a partir da qual o erro médio fica abaixo de 0,1 ponto
    const fx = D.projecao.faixas;
    let desde = fx.length;
    while (desde > 0 && Math.abs(fx[desde - 1].projecao.erro_medio) < 0.1) desde--;
    achado(7, 'res.ach.projecao', { n: N(pontos(-fx.find(f => f.faixa === '10 a 20').projecao.erro_medio)),
      desde: fmt.comPct(fx[desde].faixa.split(' ')[0]), lim: nf(0.1, 1) });
    // T34 (P27, decisão do autor): o teste registrado da renda × parte do Lula nos votos a mais; pagina_dados.py confere que ele dá associação positiva
    // revisão final (D63): o achado começa pelo número, o mesmo da resposta curta do capítulo 8
    const capRen8 = D.sociais.testes.find(t => t.var === 'ren' && t.desfecho === 'cap').principal.efeito_interquartil_pp;
    achado(8, 'res.ach.sociais', { cap: N(T.p('un.pontos', capRen8, { n: fmt.abs(capRen8, 1) })) });
    // T33 (P29, decisão do autor): a contagem da pergunta 2 do capítulo 9, a única exploratória que pode vir para cá, com o rótulo no próprio achado
    const E2x = D.exploracao.E2;
    achado(9, 'res.ach.trocas', { n: N(fmt.int(E2x.casas.fl)), lf: fmt.int(E2x.casas.lf), rot: el('em', 'rotulo-exp', T('c9.rotulo.curto')) });
  })();

  // ---------- E na sua cidade? (busca e ficha) ----------
  const semAcento = s => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  function fichaCidade(caixa, m) {
    caixa.replaceChildren();
    const f = el('article', 'ficha', undefined, caixa);
    el('h3', 'ficha-tit', nomeMun(m), f);
    el('p', 'ficha-meta', m.exterior ? T('ficha.exterior') :
      T('ficha.meta', { regiao: REGIAO_UF[m.uf], tipo: T(m.capital ? 'ficha.capital' : 'ficha.interior'), porte: PORTE[m.porte] }), f);
    const linhas = [
      [T('ficha.lula_votos'), fmt.int(m.L1), fmt.int(m.L2), fmt.intSinal(m.dL)],
      [T('ficha.flavio_votos'), fmt.int(m.F1), fmt.int(m.F2), fmt.intSinal(m.dF)],
      [T('ficha.fatia_lula'), fmt.pct(m.s1, 2), fmt.pct(m.s2, 2), fmt.pp(m.ds)],
      [T('ficha.fatia_flavio'), fmt.pct(m.s1 === null ? null : 100 - m.s1, 2), fmt.pct(m.s2 === null ? null : 100 - m.s2, 2),
        fmt.pp(m.ds === null ? null : -m.ds)],
      [T('ficha.diferenca'), fmt.intSinal(m.M1), fmt.intSinal(m.M2), fmt.intSinal(m.dM)],
      [T('ficha.abstencao'), fmt.pct(m.a1, 2), fmt.pct(m.a2, 2), fmt.pp(m.da)],
    ];
    const t = el('table', 'tab tab-ficha', undefined, el('div', 'tab-caixa', undefined, f));
    const cab = el('tr', '', undefined, el('thead', '', undefined, t));
    ['', T('g.turno1'), T('g.turno2'), T('tab.variacao')].forEach((c, i) => { const th = el('th', i ? 'num' : '', c, cab); th.scope = 'col'; });
    const tb = el('tbody', '', undefined, t);
    for (const l of linhas) {
      const r = el('tr', '', undefined, tb);
      l.forEach((c, i) => { const td = el(i ? 'td' : 'th', i ? 'num' : '', c, r); if (!i) td.scope = 'row'; });
    }
    P(f, 'ficha-pe', ...T.f(m.cap === null ? 'ficha.pe_sem_captura' : 'ficha.pe', {
      peso: B(fmt.pct(m.peso, 3)), n05: nd('N05'), cap: B(fmt.pct(m.cap, 1)), n09: nd('N09') }));
    if (!m.exterior) perfilCidade(f, m);
  }
  // ---------- Dados sociais (T26 e T34): as 7 características de cada município ----------
  const SOC_VARS = ['p60', 'alf', 'ren', 'pib', 'den', 'eva', 'ppa'];
  const socValor = (k, v) => (v === null || v === undefined ? fmt.vazio : k === 'pib' ? T('soc.un.reais', { n: fmt.int(v) })
    : k === 'den' ? T('soc.un.densidade', { n: fmt.dec(v, v < 10 ? 1 : 0) }) : fmt.pct(v, 1));
  /** O perfil do município na ficha da cidade, ao lado da mediana dos 5.570 municípios com dados. */
  function perfilCidade(f, m) {
    el('h4', 'ficha-sub', T('soc.ficha.tit'), f);
    if (m.p60 === null) { P(f, 'ficha-pe', ...T.f('soc.ficha.sem', { n20: nd('N20') })); return; }
    const t = el('table', 'tab tab-ficha', undefined, el('div', 'tab-caixa', undefined, f));
    const cab = el('tr', '', undefined, el('thead', '', undefined, t));
    ['', T('soc.ficha.col_mun'), T('soc.ficha.col_mediana')].forEach((c, i) => { const th = el('th', i ? 'num' : '', c, cab); th.scope = 'col'; });
    const tb = el('tbody', '', undefined, t);
    for (const k of SOC_VARS) {
      const r = el('tr', '', undefined, tb);
      const th = el('th', '', T('soc.var.' + k), r); th.scope = 'row';
      el('td', 'num', socValor(k, m[k]), r); el('td', 'num', socValor(k, D.sociais.medianas[k]), r);
    }
    P(f, 'ficha-pe', ...T.f('soc.ficha.pe', { n: fmt.int(D.sociais.municipios), n19: nd('N19') }));
  }
  /** Busca de município com a ficha: no Resumo e, com outra caixa, no Explorar (T24). */
  function busca(entrada, lista, ficha, prefixo, aoEscolher = fichaCidade) {
    let achadosBusca = [], ativo = -1, indice = null;
    const fechar = () => { lista.hidden = true; entrada.setAttribute('aria-expanded', 'false'); entrada.removeAttribute('aria-activedescendant'); ativo = -1; };
    function escolher(m) { entrada.value = nomeMun(m); fechar(); aoEscolher(ficha, m); if (window.contar) contar('cidade', '', false); }
    function marcar(i) {
      ativo = i;
      $$('li', lista).forEach((li, j) => li.setAttribute('aria-selected', j === i ? 'true' : 'false'));
      if (i >= 0) entrada.setAttribute('aria-activedescendant', prefixo + i);
    }
    entrada.addEventListener('input', () => {
      const q = semAcento(entrada.value.trim());
      if (q.length < 2) { fechar(); return; }
      if (!indice) indice = municipios().map(m => ({ m, n: semAcento(m.nome) }));
      const comeca = [], palavra = [], contem = [];
      for (const x of indice) {
        if (x.n.startsWith(q)) comeca.push(x.m);
        else if (x.n.includes(' ' + q)) palavra.push(x.m);
        else if (x.n.includes(q)) contem.push(x.m);
      }
      const porTamanho = (a, b) => b.E1 - a.E1;
      const todos = [...comeca.sort(porTamanho), ...palavra.sort(porTamanho), ...contem.sort(porTamanho)];
      achadosBusca = todos.slice(0, 8);
      lista.replaceChildren();
      if (!achadosBusca.length) el('li', 'busca-vazio', T('busca.nenhum'), lista).setAttribute('aria-disabled', 'true');
      achadosBusca.forEach((m, i) => {
        const li = el('li', '', undefined, lista);
        li.id = prefixo + i; li.setAttribute('role', 'option');
        el('span', '', m.nome, li); el('span', 'busca-uf', m.exterior ? T('mun.exterior') : m.uf, li);
        li.addEventListener('pointerdown', ev => { ev.preventDefault(); escolher(m); });
      });
      if (todos.length > achadosBusca.length) // QA nº 12: a lista corta em 8 e diz que há mais
        el('li', 'busca-vazio busca-mais', T('busca.mais', { n: achadosBusca.length, total: fmt.int(todos.length) }), lista).setAttribute('aria-disabled', 'true');
      lista.hidden = false; entrada.setAttribute('aria-expanded', 'true');
      marcar(achadosBusca.length ? 0 : -1);
    });
    entrada.addEventListener('keydown', ev => {
      if (lista.hidden || !achadosBusca.length) return;
      if (ev.key === 'ArrowDown') { ev.preventDefault(); marcar((ativo + 1) % achadosBusca.length); }
      else if (ev.key === 'ArrowUp') { ev.preventDefault(); marcar((ativo - 1 + achadosBusca.length) % achadosBusca.length); }
      else if (ev.key === 'Enter') { ev.preventDefault(); escolher(achadosBusca[Math.max(0, ativo)]); }
      else if (ev.key === 'Escape') fechar();
    });
    entrada.addEventListener('blur', () => setTimeout(fechar, 120));
  }
  busca($('#busca-cidade'), $('#busca-lista'), $('#ficha-cidade'), 'busca-op-');

  // ======================= Capítulos: peças comuns =======================
  /** f: {n, titulo (a conclusão), sub (o que a figura mostra, com os eixos), leitura, legenda,
   *      desenhar, fonte, como, notas, extra} */
  // Cada figura ganha um endereço (T12: as notas sobre os dados levam de volta a ela): #fig-1-1 na
  // leitura, #explorar/fig-e1 e #apuracao/fig-a1. Duas figuras com o mesmo número (as abas) ficam com um só.
  const idsFiguras = new Set();
  const idFigura = n => (/^E/.test(n) ? 'explorar-fig-' : /^A/.test(n) ? 'apuracao-fig-' : 'fig-') + String(n).toLowerCase().replace(/\./g, '-');
  function figura(pai, f) {
    const fig = el('figure', 'figura', undefined, pai);
    if (!idsFiguras.has(f.n)) { idsFiguras.add(f.n); fig.id = idFigura(f.n); fig.tabIndex = -1; }
    const cab = el('figcaption', 'fig-cab', undefined, fig);
    const ft = el('span', 'fig-tit', undefined, cab);
    el('span', 'fig-n', T('fig.n', { n: f.n }), ft); ft.append(f.titulo);
    for (const s of [].concat(f.sub || [], f.leitura || [])) {
      const sp = el('span', 'fig-sub', undefined, cab);
      sp.append(...[].concat(s));
    }
    if (f.legenda) G.legenda(fig, f.legenda);
    const aviso = el('span', 'fig-aviso');
    grafico(fig, caixa => { const r = f.desenhar(caixa); aviso.textContent = typeof r === 'string' ? r : ''; });
    if (f.extra) f.extra(fig);
    const rod = el('div', 'fig-rodape', undefined, fig);
    const fonte = el('span', '', f.fonte || T('fig.fonte_padrao'), rod);
    if (f.como) sup(fonte, 'fig-' + f.n, T('fig.como', { n: f.n }), f.como);
    for (const id of f.notas || []) notaDados(fonte, id);
    rod.appendChild(aviso);
    return fig;
  }
  /** Duas figuras no mesmo lugar, com a escolha em texto (capítulos 3, 4 e 6). */
  function figurasComAbas(pai, abas, chave) {
    const caixa = el('div', 'fig-abas', undefined, pai);
    const botoes = el('div', 'botoes-escolha', undefined, caixa);
    botoes.setAttribute('role', 'group'); botoes.setAttribute('aria-label', T('fig.escolha'));
    const paineis = abas.map(a => { const p = el('div', 'fig-painel', undefined, caixa); a.montar(p); return p; });
    const comId = $('figure[id]', caixa); // o endereço vai para a caixa, que fica à vista com qualquer aba
    if (comId) { caixa.id = comId.id; caixa.tabIndex = -1; comId.removeAttribute('id'); comId.removeAttribute('tabindex'); }
    const lembrada = +(guarda.ler('analise-fig-' + chave) || 0);
    const mostrar = i => {
      paineis.forEach((p, j) => { p.hidden = j !== i; });
      $$('button', botoes).forEach((b, j) => b.setAttribute('aria-pressed', j === i ? 'true' : 'false'));
      G.dicaEsconder();
      guarda.gravar('analise-fig-' + chave, i ? String(i) : null);
    };
    abas.forEach((a, i) => {
      const b = el('button', '', a.rotulo, botoes);
      b.type = 'button';
      b.addEventListener('click', () => mostrar(i));
    });
    mostrar(lembrada < abas.length ? lembrada : 0);
    return caixa;
  }
  function notaLateral(pai, titulo, primeiro, ...outros) {
    const n = el('aside', 'nota-lateral', undefined, pai);
    P(n, '', el('span', 'nota-tit', T('lado.tit', { t: titulo })), ...[].concat(primeiro));
    for (const p of outros) P(n, '', ...[].concat(p));
    return n;
  }

  // --- Hipóteses: a frase no topo e "Como se chegou à conclusão" no "Ver detalhes" ---
  function resumoConferencias(H) {
    const p = partesConferencias(H);
    return p.iguais ? T('hip.conf_iguais', { n: p.total }) : T('hip.conf_partes', { partes: p.texto });
  }
  function partesConferencias(H) {
    const c = H.conferencias, total = c.confirmada + c['contrária'] + c.inconclusiva;
    if (c[H.classificacao] === total) return { total, iguais: true };
    const partes = [];
    const versoes = H.versoes.slice(1);
    for (const k of ['confirmada', 'contrária', 'inconclusiva']) {
      if (!c[k]) continue;
      const peq = k !== 'inconclusiva' ? versoes.filter(v => v.classificacao === k && v.pequena).length : 0;
      const sobrePeq = peq === c[k] ? T.p('hip.conf_peq_todas', c[k]) : T('hip.conf_peq_algumas', { n: peq });
      const parte = T.p(classeChave(k) + '.n', c[k], { n: c[k] });
      partes.push(peq ? T('hip.conf_com_peq', { parte, peq: sobrePeq }) : parte);
    }
    return { total, iguais: false, texto: listaE(partes) };
  }
  function abrirDetalhes(d) {
    d.open = true;
    const alvo = $('.como-chegou', d) || d;
    alvo.scrollIntoView({ behavior: semMovimento() ? 'auto' : 'smooth', block: 'start' });
  }
  function caixaHipotese(cab, texto, H, alvoDetalhes, rotuloStatus) {
    const hp = el('div', 'hipotese', undefined, cab);
    const ht = el('p', 'hip-texto', undefined, hp);
    el('span', 'hip-cab', T('hip.cab'), ht); // entrada na própria frase, sem rótulo acima
    ht.append(texto);
    const r = el('p', 'hip-res', undefined, hp);
    const status = B((rotuloStatus || T(classeChave(H.classificacao))).toLowerCase());
    r.append(...(H.conferencias ? T.f('hip.res_conf', { status, conf: resumoConferencias(H) }) : T.f('hip.res', { status })));
    const b = el('button', 'bt-link', T('hip.como_chegou'), r);
    b.type = 'button';
    b.addEventListener('click', () => abrirDetalhes(alvoDetalhes()));
  }
  const P05 = nf(0.05, 2);
  const REGRA = ['confirmada', 'contraria', 'inconclusiva'].map(k => [T('hip.classe.' + k), T('regra.' + k, { p: P05 })]);
  // T32 (M5): ic95 é o intervalo do bootstrap selvagem (por inversão do teste) e ic95_cr1, o do erro agrupado;
  // a classificação pede os dois do mesmo lado (pagina_dados.py confere isso em todas as versões)
  function porQue(v) {
    const lado = ic => (ic[0] > 0 ? 1 : ic[1] < 0 ? -1 : 0);
    const s = v.previsto === 'negativo' ? -1 : 1, b = lado(v.ic95), c = lado(v.ic95_cr1 || v.ic95);
    if (!b && !c) return T('porque.zero');
    if (b === s && c === s) return T('porque.previsto', { p: P05 });
    if (b === -s && c === -s) return T('porque.oposto', { p: P05 });
    return T(b ? 'porque.discordam2' : 'porque.discordam', { p: P05 });
  }
  const coefTxt = (v, fator) => fmt.decSinal(v * fator, 2);
  const icTxt = (ic, fator) => T('g.de_a', { a: fmt.decSinal(ic[0] * fator, 2), b: fmt.decSinal(ic[1] * fator, 2) });
  function regra(pai, aplicada) {
    const ul = el('ul', 'regra', undefined, pai);
    REGRA.forEach(([t, d], i) => {
      const li = el('li', i === aplicada ? 'aplicada' : '', undefined, ul);
      li.append(B(T('regra.item', { t })), d);
      if (i === aplicada) el('span', 'regra-marca', T('regra.este'), li);
    });
    el('li', '', T('regra.tamanho', { lim: nf(0.5, 1) }), ul);
  }
  /** Tabela das versões de um teste (principal e conferências). */
  function tabelaVersoes(pai, n, titulo, versoes, fatorDe, grafico) {
    return G.tabela(pai, {
      legenda: { n, t: titulo }, ordenavel: false, destaque: v => /principal$/.test(v.versao), grafico,
      linhas: versoes,
      colunas: [
        { t: T('tab.versao'), v: v => nomeVersao(v) },
        { t: T('tab.municipios'), num: true, v: v => v.n, f: fmt.int },
        { t: T('tab.coeficiente'), num: true, v: v => v.coef * fatorDe(v), f: v => fmt.decSinal(v, 2) },
        { t: T('tab.ic95'), num: true, v: v => v, f: (_, v) => icTxt(v.ic95, fatorDe(v)) },
        { t: T('tab.ic95_cr1'), num: true, v: v => v, f: (_, v) => (v.ic95_cr1 ? icTxt(v.ic95_cr1, fatorDe(v)) : fmt.vazio) },
        { t: T('tab.p_selvagem'), num: true, v: v => v.p_selvagem, f: v => (v === null || v === undefined ? fmt.vazio : fmt.p(v)) },
        { t: T('tab.entre_quartis'), num: true, v: v => v.efeito_interquartil_pp, f: v => fmt.decSinal(v, 2) },
        { t: T('tab.resultado'), v: v => (v.classificacao ? classeTexto(v) : fmt.vazio) },
      ],
    });
  }
  /** As versões de um teste como pontos com o intervalo de 95% (fatorDe: a escala de cada versão; todas na mesma). */
  function forestOpcoes(vs, fatorDe, unidade) {
    const lim = Math.max(...vs.flatMap(v => v.ic95.map(x => Math.abs(x * fatorDe(v)))));
    const passo = lim > 2 ? 1 : lim > 0.6 ? 0.25 : 0.1;
    const max = Math.ceil(lim / passo) * passo;
    return {
      aria: T('forest.aria'),
      x: { min: -max, max, passo, fmt: v => fmt.decSinal(v, passo >= 1 ? 0 : passo < 0.25 ? 1 : 2), rotulo: T('forest.eixo', { unidade }) },
      lados: vs[0].previsto === 'negativo' ? [T('forest.esq_previsto'), T('forest.dir_contrario')] : [T('forest.esq_contrario'), T('forest.dir_previsto')],
      margE: 260, margEstreito: 116,
      linhas: vs.map(v => { const fator = fatorDe(v); return { nome: curtoVersao(v, 0), curto: curtoVersao(v, 1),
        v: v.coef * fator, ic: v.ic95.map(x => x * fator), destaque: /principal$/.test(v.versao),
        dica: { titulo: nomeVersao(v), linhas: [
          { t: T('tab.coeficiente'), v: coefTxt(v.coef, fator) }, { t: T('tab.ic95'), v: icTxt(v.ic95, fator) },
          { t: T('tab.ic95_cr1'), v: icTxt(v.ic95_cr1, fator) },
          { t: T('dica.valor_p'), v: fmt.p(v.p_selvagem) }, { t: T('tab.municipios'), v: fmt.int(v.n) },
          { t: T('tab.resultado'), v: classeTexto(v) }] } }; }),
    };
  }
  function forestVersoes(pai, H, fator, unidade) {
    return grafico(pai, caixa => G.coeficientes(caixa, forestOpcoes(H.versoes, () => fator, unidade)));
  }
  /** O gráfico da tabela de versões (T36), quando ele não está numa figura ao lado: só as versões na unidade
   *  principal; a de escala contínua, em outra unidade, fica só na tabela, e o texto acima do gráfico diz isso. */
  function graficoVersoes(versoes, fatorDe, unidade) {
    const fator = fatorDe(versoes[0]), vs = versoes.filter(v => fatorDe(v) === fator);
    return { sub: vs.length < versoes.length ? T.p('vd.versoes_fora', versoes.length - vs.length, { n: versoes.length - vs.length }) : null,
      desenhar: caixa => G.coeficientes(caixa, forestOpcoes(vs, () => fator, unidade)) };
  }
  /** cfg: {texto, porque, variavel, unidade, fator, n (figura), t (tabela)} */
  function comoSeChegou(pai, H, cfg) {
    const s = el('section', 'como-chegou', undefined, pai);
    el('h3', '', T('hip.como_chegou'), s);
    const v = H.versoes[0];
    P(s, '', ...T.f('chegou.hipotese', { texto: el('i', '', cfg.texto) }));
    if (cfg.porque) P(s, '', ...[].concat(cfg.porque));
    P(s, '', ...T.f('chegou.teste', { variavel: cfg.variavel, grupos: v.grupos, n14: nd('N14'), previsto: T('chegou.previsto.' + v.previsto) }));
    P(s, '', ...T.f('chegou.regra'));
    regra(s, ['confirmada', 'contrária', 'inconclusiva'].indexOf(H.classificacao));
    P(s, '', ...T.f('chegou.resultado', { coef: coefTxt(v.coef, cfg.fator), unidade: cfg.unidade, ic: icTxt(v.ic95, cfg.fator),
      ic2: icTxt(v.ic95_cr1, cfg.fator),
      p: fmt.p(v.p_selvagem), r2: nf(v.r2, 2), iq: fmt.decSinal(v.efeito_interquartil_pp, 2), porque: porQue(v),
      classe: B(classeTexto(v).toLowerCase()) }));
    const pc = partesConferencias(H);
    P(s, '', ...T.f(pc.iguais ? 'chegou.conf_iguais' : 'chegou.conf_partes', { n: pc.total, partes: pc.texto }));
    const fig = el('figure', 'figura figura-det', undefined, s);
    const cab = el('figcaption', 'fig-cab', undefined, fig);
    const ft = el('span', 'fig-tit', undefined, cab);
    el('span', 'fig-n', T('fig.n', { n: cfg.n }), ft);
    ft.append(pc.iguais ? T('chegou.fig_iguais', { n: pc.total }) : T('chegou.fig_partes'));
    el('span', 'fig-sub', T('chegou.fig_sub'), cab);
    forestVersoes(fig, H, cfg.fator, cfg.unidade);
    const rod = el('div', 'fig-rodape', undefined, fig); // fonte e "Como calculamos" também aqui (T12)
    const fonte = el('span', '', T('chegou.fig_fonte'), rod);
    sup(fonte, 'fig-' + cfg.n, T('fig.como', { n: cfg.n }), [T('chegou.fig_como1'), T('chegou.fig_como2'), dadosComo(['hipoteses'], [6])]);
    notaDados(fonte, 'N14');
    G.juntar(fig, tabelaVersoes(s, cfg.t, T('chegou.tabela', { unidade: cfg.unidade }), H.versoes, () => cfg.fator)); // T36: a tabela na mesma figura
    return s; // a chamada para sugerir hipóteses fica só no fim, junto do único campo de comentário (D31)
  }
  /** g (T36): o gráfico da tabela, {v, rotulo, eixo} (barras de uma medida) ou {pares: [[lado, v, nome]], eixo, f} (os dois). */
  function rankingMunicipios(pai, n, titulo, lista, colunas, g) {
    const cols = [{ t: T('tab.municipio'), v: m => m.nome }, { t: T('tab.uf'), v: m => m.uf }].concat(colunas);
    const nome = m => T('g.mun_uf', { nome: m.nome, uf: m.uf });
    const curto = m => (m.nome.length > 13 ? m.nome.slice(0, 12).trim() + '…' : m.nome);
    const grafico = g && { legenda: g.pares && g.pares.map(([lado, , t]) => ({ t, lado })),
      desenhar: caixa => (g.pares
        ? G.linhasPontos(caixa, { aria: T('vd.aria', { t: titulo }), margE: 190, margEstreito: 100, altLinha: 22,
          x: eixo(lista.flatMap(m => g.pares.map(p => p[1](m))), g.f, g.eixo),
          linhas: lista.map(m => ({ nome: nome(m), curto: curto(m), vals: g.pares.map(([lado, v]) => ({ v: v(m), lado })), dica: dicaColunas(cols.slice(2), m, nome(m)) })) })
        : G.barras(caixa, { aria: T('vd.aria', { t: titulo }), margE: 190, margEstreito: 100, altLinha: 22, margD: 70,
          x: eixo(lista.map(g.v), g.f, g.eixo),
          linhas: lista.map(m => ({ nome: nome(m), curto: curto(m), v: g.v(m), rotulo: g.rotulo(m), dica: dicaColunas(cols.slice(2), m, nome(m)) })) })) };
    return G.tabela(pai, { legenda: { n, t: titulo }, ordenavel: false, linhas: lista, colunas: cols, grafico });
  }
  const tickPp = (v, passo) => fmt.decSinal(v, casas(passo));
  const tickPct = (v, passo) => fmt.pct(v, casas(passo));
  const tickVotos = v => (Math.abs(v) >= 1e6 ? fmt.mi(v, Math.abs(v) % 1e6 ? 1 : 0) : v === 0 ? '0' : fmt.comMil(fmt.decSinal(v / 1e3, 0)));
  function funilFig(pai, n, chave, valor, rotulo, titulo, sub, ladoAcima, ladoAbaixo, lista = doBrasil) {
    const F = D.funil[chave];
    const fig = el('figure', 'figura figura-det', undefined, pai);
    const cab = el('figcaption', 'fig-cab', undefined, fig);
    const ft = el('span', 'fig-tit', undefined, cab);
    el('span', 'fig-n', T('fig.n', { n }), ft); ft.append(titulo);
    el('span', 'fig-sub', sub, cab);
    const p998 = fmt.pct(99.8, 1);
    el('span', 'fig-sub', T('funil.leitura', { p998 }), cab);
    G.legenda(fig, [{ t: T('funil.leg95'), tipo: 'faixa95' }, { t: T('funil.leg998', { p998 }), tipo: 'faixa998' }, { t: T('funil.leg_dentro'), lado: 'dentro' }].concat(
      ladoAcima === ladoAbaixo ? [{ t: T('funil.leg_fora', { p998 }), lado: ladoAcima }]
        : [{ t: T('funil.leg_acima'), lado: ladoAcima }, { t: T('funil.leg_abaixo'), lado: ladoAbaixo }]));
    grafico(fig, caixa => G.funil(caixa, {
      aria: titulo, curva: F.curva, centro: F.centro_pp, ladoAcima, ladoAbaixo,
      y: { min: -12, max: chave === 'var_fatia' ? 12 : 24, passo: chave === 'var_fatia' ? 4 : 6, fmt: v => fmt.decSinal(v, 0), rotulo },
      pontos: lista().map(m => ({ E: m.E1, v: valor(m), titulo: nomeMun(m),
        linhas: [{ t: T(chave === 'var_fatia' ? 'funil.dica_fatia' : 'funil.dica_abstencao'), v: fmt.pp(valor(m)) },
          { t: T('tab.eleitorado'), v: fmt.int(m.E1) }] })),
    }));
    const rod = el('div', 'fig-rodape', undefined, fig);
    const fonte = el('span', '', T('funil.fonte'), rod);
    sup(fonte, 'funil-' + chave, T('funil.como.tit'), [
      T('funil.como.1', { mun: fmt.int(5571), z95: nf(1.96, 2), z998: nf(3.09, 2), p998 }),
      T('funil.como.2', { fora: fmt.pct(100 * F.fora95 / F.n, 1), pmin: fmt.pct(Math.min(...F.por_porte.map(x => x.fora95_pct)), 1),
        pmax: fmt.pct(Math.max(...F.por_porte.map(x => x.fora95_pct)), 1), fw: fmt.pct(100 * F.winsorizado.fora95 / F.n, 1) }),
      ...(chave === 'var_abstencao' ? [T('funil.como.2_abst', { acima: fmt.int(F.fora95_acima), fora95: fmt.int(F.fora95) })] : []),
      T('funil.como.3'), dadosComo(['municipios'], [3, 6])]);
    for (const id of chave === 'var_abstencao' ? ['N05', 'N06', 'N08'] : ['N06', 'N08']) notaDados(rod, id);
    return F;
  }

  // ---------- Montagem comum de cada capítulo ----------
  function cabecalho(ctx, ...resposta) { P(ctx.cab, 'resposta', ...resposta); }
  function corpo(ctx) {
    const c = el('div', 'cap-corpo', undefined, ctx.art);
    return { fig: el('div', 'cap-fig', undefined, c), lado: c };
  }
  function detalhes(ctx) {
    const d = el('details', 'detalhes', undefined, ctx.art);
    const sm = el('summary', '', undefined, d);
    el('span', 'det-rot', T('cap.ver_detalhes'), sm);
    ctx.detalhes = d;
    ctx.oQue = el('span', 'det-o-que', undefined, sm);
    return el('div', 'detalhes-corpo', undefined, d);
  }
  function secao(pai, titulo) { const s = el('section', 'det-secao', undefined, pai); el('h3', '', titulo, s); return s; }

  // ---------- Capítulo 1 ----------
  function cap1(ctx) {
    const H = D.hipoteses.H1, v = H.versoes[0], vb = H.versoes[1];
    cabecalho(ctx, ...T.f('c1.resposta', { pts: N(pontos(-v.coef * 10)), ic0: fmt.abs(-v.ic95[1] * 10, 2), ic1: fmt.abs(-v.ic95[0] * 10, 2) }));
    caixaHipotese(ctx.cab, T('c1.hipotese'), H, () => ctx.detalhes);
    const { fig, lado } = corpo(ctx);
    const r = D.retas.H1;
    figura(fig, {
      n: ctx.nf(), titulo: T('c1.fig1.titulo'),
      sub: T('c1.fig1.sub', { mun: fmt.int(5571) }),
      desenhar: caixa => {
        const fora = G.dispersao(caixa, {
          aria: T('c1.fig1.aria', { mun: fmt.int(5571) }),
          pontos: doBrasil().map(m => ({ x: m.s1, y: m.ds, peso: m.E1, lado: m.ds >= 0 ? 'l' : 'f', titulo: nomeMun(m),
            linhas: [{ t: T('c1.dica.fatia1'), v: fmt.pct(m.s1, 1) }, { lado: 'l', t: T('dica.var_lula'), v: fmt.pp(m.ds) },
              { lado: 'f', t: T('dica.var_flavio'), v: fmt.pp(-m.ds) }, { t: T('tab.eleitorado'), v: fmt.int(m.E1) }] })),
          x: { min: 0, max: 100, passo: 25, fmt: v => fmt.pct(v, 0), rotulo: T('c1.fig1.eixo_x') },
          y: { min: -4, max: 8, passo: 2, fmt: v => fmt.decSinal(v, 0), rotulo: T('eixo.var_fatia_pp') },
          reta: { a: r.a, b: r.b, de: 10, ate: 90, rotulo: T('eixo.tendencia') },
          marca: { x: BR.s1, y: BR.ds, rotulo: BR.nome },
          rotulos: [{ x: 1, y: 7.4, lado: 'l', t: T('c1.fig1.rot_acima'), curto: T('c1.fig1.rot_acima_curto') },
            { x: 1, y: -3.2, lado: 'f', t: T('c1.fig1.rot_abaixo'), curto: T('c1.fig1.rot_abaixo_curto') }],
          anotacao: { linhas: T('c1.fig1.anotacao'), linhasEstreito: T('c1.fig1.anotacao_cel'),
            x: 60, y: 7.1, xEstreito: 62, yEstreito: 7.3, alvo: { x: 80, y: r.a + r.b * 80 } },
        });
        return fora ? T('fig.fora_escala', { n: fmt.int(fora) }) : '';
      },
      como: [
        T.f('c1.fig1.como1'),
        T('c1.fig1.como2', { s1: fmt.pct(BR.s1, 2), s2: fmt.pct(BR.s2, 2), ds: fmt.pp(BR.ds) }),
        T('c1.fig1.como3', { coef: coefTxt(vb.coef, 10) }),
        T('c1.fig1.como4'), dadosComo(['municipios', 'hipoteses'], [3, 6])],
      notas: ['N06', 'N14'],
    });
    notaLateral(lado, T('c1.lado.tit'), T('c1.lado.1'), T('c1.lado.2'));
    const det = detalhes(ctx);
    const capt = el('span'); notaComo(capt, 'captura');
    comoSeChegou(det, H, {
      texto: T('c1.chegou.texto'),
      porque: T.f('c1.chegou.porque', { cap: fmt.pct(BR.cap, 1), nota: capt, s1: fmt.pct(BR.s1, 2) }),
      variavel: T('c1.chegou.variavel'), unidade: T('un.10pontos'), fator: 10, n: ctx.nf(), t: ctx.nt(),
    });
    const t = secao(det, T('cap.resultado_texto'));
    const [cl, , cf] = D.complementos.H1;
    P(t, '', T('c1.texto.1', { pts: pontos(-v.coef * 10), ic0: fmt.abs(-v.ic95[1] * 10, 2), ic1: fmt.abs(-v.ic95[0] * 10, 2),
      iq: fmt.abs(-v.efeito_interquartil_pp, 1), br: fmt.abs(-vb.coef * 10, 2) }));
    P(t, '', ...T.f('c1.texto.2', { cf: fmt.abs(cf.coef * 10, 2), cf0: fmt.abs(cf.ic95[0] * 10, 2), cf1: fmt.abs(cf.ic95[1] * 10, 2),
      cl0: fmt.decSinal(cl.ic95[0] * 10, 2), cl1: fmt.decSinal(cl.ic95[1] * 10, 2) }));
    P(t, '', ...T.f('c1.texto.3'));
    // T32 (M4): a inclinação que a divisão igual do saldo daria, ao lado da observada (exploratório)
    const h1r = D.h1_referencia, esp = h1r.esperada;
    P(t, '', ...T.f('c1.texto.4', { cap: fmt.pct(100 * h1r.captura_brasil_sem_exterior, 1), esp: fmt.decSinal(esp.coef * 10, 2),
      esp0: fmt.decSinal(esp.ic95[0] * 10, 2), esp1: fmt.decSinal(esp.ic95[1] * 10, 2), obs: fmt.decSinal(v.coef * 10, 2) }));
    const fu = secao(det, T('c1.funil.secao'));
    const F = funilFig(fu, ctx.nf(), 'var_fatia', m => m.ds, T('eixo.var_fatia_pp'),
      T('c1.funil.titulo'), T('c1.funil.sub'), 'l', 'f');
    P(fu, '', T('c1.funil.texto', { p998: fmt.pct(99.8, 1), n: fmt.int(F.fora998), acima: fmt.int(F.fora998_acima), abaixo: fmt.int(F.fora998_abaixo) }));
    const rk = secao(det, T('c1.rank.secao'));
    rankingMunicipios(rk, ctx.nt(), T('c1.rank.titulo'),
      acimaDoPiso().sort((a, b) => b.ds - a.ds).slice(0, 10), [
        { t: T('tab.eleitorado'), num: true, v: m => m.E1, f: fmt.int },
        { t: T('tab.fatia_lula_1'), num: true, v: m => m.s1, f: x => fmt.pct(x, 1) },
        { t: T('tab.turno2_curto'), num: true, v: m => m.s2, f: x => fmt.pct(x, 1) },
        { t: T('tab.variacao'), num: true, v: m => m.ds, f: x => fmt.pp(x) }],
      { v: m => m.ds, rotulo: m => fmt.pp(m.ds), f: tickPp, eixo: T('eixo.var_fatia_pp') });
    P(rk, 'nota-tab', T('c1.rank.nota'));
  }

  // ---------- Capítulo 2 ----------
  function cap2(ctx) {
    const mun = doBrasil();
    const ganhou = UFS.filter(u => u.dF > 0), perdeu = UFS.filter(u => u.dF < 0), lulaGanhou = UFS.filter(u => u.dL > 0);
    const munGanhou = mun.filter(m => m.dF > 0).length, munFatia = mun.filter(m => m.ds < 0).length;
    const ufFatia = UFS.filter(u => u.ds < 0).length;
    cabecalho(ctx, ...T.f('c2.resposta', { df: N(fmt.miAbs(BR.dF)), ufs: ganhou.length, mun: fmt.int(munGanhou), total: fmt.int(mun.length),
      onde: ufFatia ? T('c2.resposta.em_estados', { n: 27 - ufFatia }) : T('c2.resposta.nos_27'), dl: fmt.miAbs(BR.dL), munf: fmt.int(munFatia) }));
    const { fig, lado } = corpo(ctx);
    const pe = u => 100 * u.dL / u.E1, pf = u => 100 * u.dF / u.E1;
    const ordem = UFS.slice().sort((a, b) => pf(b) - pf(a));
    const todos = ordem.flatMap(u => [pe(u), pf(u)]);
    const top = ordem.slice(0, 3);
    figura(fig, {
      n: ctx.nf(),
      titulo: T('c2.fig1.titulo', { ufs: ganhou.length, lula: lulaGanhou.length === 27 ? T('c2.fig1.todos') : lulaGanhou.length }),
      sub: T('c2.fig1.sub'),
      leitura: T('c2.fig1.leitura', { top: listaE(top.map(u => T('c2.fig1.top_item', { uf: u.nome, pct: fmt.comPct(fmt.decSinal(pf(u), 2)) }))),
        n: perdeu.length, perdeu: listaE(perdeu.map(u => u.nome)) }),
      desenhar: caixa => G.linhasPontos(caixa, {
        aria: T('c2.fig1.aria'),
        x: { min: 2 * Math.floor(Math.min(...todos) / 2), max: 2 * Math.ceil(Math.max(...todos) / 2), passo: 2, fmt: v => fmt.comPct(fmt.decSinal(v, 0)), rotulo: T('c2.fig1.eixo') },
        margE: 150, margEstreito: 34, altLinha: 15, topo: 30, series: { l: T('nome.lula'), f: T('nome.flavio') },
        linhas: ordem.map(u => ({ nome: u.nome, curto: u.codigo, vals: [{ v: pe(u), lado: 'l' }, { v: pf(u), lado: 'f' }],
          dica: { titulo: u.nome, linhas: [
            { lado: 'l', t: T('nome.lula'), v: T('dica.v_par', { v: fmt.intSinal(u.dL), p: fmt.comPct(fmt.decSinal(pe(u), 2)) }) },
            { lado: 'f', t: T('nome.flavio'), v: T('dica.v_par', { v: fmt.intSinal(u.dF), p: fmt.comPct(fmt.decSinal(pf(u), 2)) }) },
            { t: T('c2.dica.fatia_flavio'), v: T('dica.de_para', { a: fmt.pct(100 - u.s1, 2), b: fmt.pct(100 - u.s2, 2) }) }] } })),
      }),
      como: [
        T.f('c2.fig1.como1'),
        T('c2.fig1.como2', { uf: ordem[0].nome, f1: fmt.int(ordem[0].F1), f2: fmt.int(ordem[0].F2), df: fmt.intSinal(ordem[0].dF),
          pct: fmt.comPct(fmt.decSinal(pf(ordem[0]), 2)), e1: fmt.int(ordem[0].E1) }),
        T('c2.fig1.como3'), dadosComo(['estados'], [3])],
      notas: ['N06'],
    });
    notaLateral(lado, T('c2.lado.tit'), T('c2.lado.1', { n: ganhou.length }), T('c2.lado.2'));
    const det = detalhes(ctx);
    const t = secao(det, T('cap.resultado_texto'));
    const regs = D.regioes.filter(r => r.codigo !== 'EX').sort((a, b) => b.dF - a.dF);
    P(t, '', ...T.f('c2.texto.1', { regs: listaE(regs.map(r => T('c2.texto.1_item', { df: fmt.intSinal(r.dF), regiao: r.nome }))),
      mun: fmt.int(munGanhou), total: fmt.int(mun.length), munf: fmt.int(munFatia), n18: nd('N18') }));
    const [cl, , cf] = D.complementos.H1;
    P(t, '', ...T.f('c2.texto.2', { cf: fmt.abs(cf.coef * 10, 2), cf0: fmt.abs(cf.ic95[0] * 10, 2), cf1: fmt.abs(cf.ic95[1] * 10, 2),
      cl0: fmt.decSinal(cl.ic95[0] * 10, 2), cl1: fmt.decSinal(cl.ic95[1] * 10, 2) }));
    const tb = secao(det, T('c2.tab.secao'));
    const cols21 = [
        { t: T('tab.estado'), v: u => u.nome }, { t: T('tab.lula_ganhos'), num: true, v: u => u.dL, f: fmt.intSinal },
        { t: T('tab.flavio_ganhos'), num: true, v: u => u.dF, f: fmt.intSinal },
        { t: T('tab.fatia_flavio_1'), num: true, v: u => 100 - u.s1, f: v => fmt.pct(v, 2) },
        { t: T('tab.turno2_curto'), num: true, v: u => 100 - u.s2, f: v => fmt.pct(v, 2) },
        { t: T('tab.variacao'), num: true, v: u => -u.ds, f: v => fmt.pp(v) }];
    const ufs21 = D.ufs.slice().sort((a, b) => (100 - b.s2) - (100 - a.s2));
    G.tabela(tb, { legenda: { n: ctx.nt(), t: T('c2.tab.titulo') }, linhas: D.ufs, ordem: { col: 2, desc: true }, colunas: cols21,
      grafico: { legenda: [{ t: T('g.turno1'), lado: 'muted' }, { t: T('g.turno2'), lado: 'f' }], sub: T('vd.c2.sub'),
        desenhar: caixa => {
          const r = G.linhasPontos(caixa, { aria: T('vd.aria', { t: T('c2.tab.titulo') }), margE: 150, margEstreito: 34, altLinha: 16, topo: 30,
            x: Object.assign(eixo(ufs21.flatMap(u => [100 - u.s1, 100 - u.s2]).concat(50), tickPct, T('vd.c2.eixo'), { zero: false }), { ref: 50 }),
            linhas: ufs21.map(u => ({ nome: u.nome, curto: u.codigo, vals: [{ v: 100 - u.s1, lado: 'muted' }, { v: 100 - u.s2, lado: 'f' }],
              dica: dicaColunas(cols21.slice(1), u, u.nome) })) });
          return r;
        } } });
    const rk = secao(det, T('c2.rank.secao'));
    rankingMunicipios(rk, ctx.nt(), T('c2.rank.titulo1'),
      acimaDoPiso().filter(m => m.ds < 0).sort((a, b) => a.ds - b.ds).slice(0, 10), [
        { t: T('tab.eleitorado'), num: true, v: m => m.E1, f: fmt.int },
        { t: T('tab.fatia_flavio_1'), num: true, v: m => 100 - m.s1, f: v => fmt.pct(v, 1) },
        { t: T('tab.turno2_curto'), num: true, v: m => 100 - m.s2, f: v => fmt.pct(v, 1) },
        { t: T('tab.variacao'), num: true, v: m => -m.ds, f: v => fmt.pp(v) }],
      { v: m => -m.ds, rotulo: m => fmt.pp(-m.ds), f: tickPp, eixo: T('vd.eixo.var_flavio') });
    rankingMunicipios(rk, ctx.nt(), T('c2.rank.titulo2'),
      mun.slice().sort((a, b) => b.dF - a.dF).slice(0, 10), [
        { t: T('tab.flavio_ganhos'), num: true, v: m => m.dF, f: fmt.intSinal },
        { t: T('tab.lula_ganhos'), num: true, v: m => m.dL, f: fmt.intSinal }],
      { pares: [['l', m => m.dL, T('nome.lula')], ['f', m => m.dF, T('nome.flavio')]], f: tickVotos, eixo: T('vd.eixo.votos_ganhos') });
    P(rk, 'nota-tab', T('c2.rank.nota'));
  }

  // ---------- Capítulo 3 ----------
  // T32 (M1): a divisão dos votos dos outros em três contas (principal, com intercepto e matriz de transição);
  // o Flávio fica com o resto até 100 de cada uma. Também no Explorar.
  function faixaOutros() {
    const esp = Object.values(D.especificacoes_outros).map(x => Math.round(x * 100));
    const lmin = Math.min(...esp), lmax = Math.max(...esp);
    return { lmin: nf(lmin, 0), lmax: nf(lmax, 0), fmin: nf(100 - lmax, 0), fmax: nf(100 - lmin, 0) };
  }
  // T35 (P28): a parte da mudança comum à cidade inteira, que a conta por seção deixa fora das três fontes (Brasil)
  function comumSecoes() {
    const c = D.secoes.parte_comum;
    return { sec: fmt.int(D.secoes.secoes), comum: fmt.miAbs(c.lula), pct: fmt.pct(100 * c.lula_pct_do_saldo, 0) };
  }
  function linhasVieram() {
    const E = D.ecologica.brasil, FS = D.ecologica.fontes_sem_exterior, TR = D.transicao.brasil, CI = D.ecologica.conferencias.com_intercepto.O;
    const S = D.ecologica.secoes;
    const pctIc = (x, ic) => T('dica.pct_ic', { v: fmt.comPct(nf(x * 100, 1)), a: nf(ic[0] * 100, 1), b: nf(ic[1] * 100, 1) });
    const conta = (chave, e, ic, extra) => ({ nome: T('c3.fig2.esp.' + chave), curto: T('c3.fig2.esp.' + chave + '_curto'),
      lula: e, ic, destaque: chave === 'principal',
      dica: { titulo: T('fonte.O'), linhas: [{ t: T('c3.fig2.dica.conta'), v: T('c3.fig2.esp.' + chave) },
        { lado: 'l', t: T('nome.lula'), v: pctIc(e, ic) }, { lado: 'f', t: T('nome.flavio'), v: pctIc(1 - e, [1 - ic[1], 1 - ic[0]]) }].concat(extra || []) } });
    const linhas = [{ grupo: T('c3.fig2.grupo_outros', { mi: fmt.mi(FS.O, 2).replace(/^\+/, '') }) },
      conta('principal', E.O.lula, E.O.lula_ic95, [{ t: T('dica.tamanho_fonte'), v: T('dica.n_votos', { n: fmt.int(FS.O) }) }]),
      conta('intercepto', CI.lula, CI.lula_ic95),
      conta('transicao', TR.outros_lula_entre_os_dois, TR.outros_lula_entre_os_dois_ic95, [{ t: '', v: T('c3.fig2.dica.transicao') }]),
      // T35 (P28): a quarta conta, comparando seções da mesma cidade; as outras duas fontes vêm dela (é a estimativa por lugar do Brasil)
      conta('secoes', S.O.lula, S.O.lula_ic95, [{ t: '', v: T('c3.fig2.dica.secoes') }]),
      { grupo: T('c3.fig2.grupo_fontes') }];
    for (const k of ['C', 'R']) {
      const e = S[k], pl = D.por_lugar[0].fontes[k], nome = T('fonte.' + k);
      linhas.push({ nome: T('dica.v_par', { v: nome, p: fmt.mi(FS[k], 2) }), curto: T('fonte.' + k + '.curto'), lula: e.lula, ic: e.lula_ic95,
        naoDeu: pl.passa ? null : pl.motivo,
        dica: { titulo: nome, linhas: pl.passa ? [{ t: T('c3.fig2.dica.conta'), v: T('c3.fig2.esp.secoes') },
          { lado: 'l', t: T('nome.lula'), v: pctIc(e.lula, e.lula_ic95) }, { lado: 'f', t: T('nome.flavio'), v: pctIc(e.flavio, e.flavio_ic95) },
          { t: T('dica.tamanho_fonte'), v: T('dica.n_votos', { n: fmt.int(FS[k]) }) }]
          : [{ t: T('dica.nao_deu'), v: '' }, { t: T('dica.motivo'), v: pl.motivo },
          { t: T('dica.conta_daria'), v: T('dica.pct_ic', { v: fmt.pct(e.lula * 100, 0), a: nf(e.lula_ic95[0] * 100, 0), b: nf(e.lula_ic95[1] * 100, 0) }) }] } });
    }
    return linhas;
  }
  function cap3(ctx) {
    const H = D.hipoteses.H3, v = H.versoes[0], vb = H.versoes[1], E = D.ecologica.brasil, S = D.ecologica.secoes;
    // T32 (M1): a divisão dos votos dos outros em três contas; o Flávio fica com o resto até 100 de cada uma
    const faixa = faixaOutros();
    cabecalho(ctx, ...T.f('c3.resposta', { lmin: N(faixa.lmin), lmax: N(faixa.lmax), fmin: N(faixa.fmin), fmax: N(faixa.fmax) }));
    caixaHipotese(ctx.cab, T('c3.hipotese'), H, () => ctx.detalhes);
    const { fig, lado } = corpo(ctx);
    const r = D.retas.H3, FS = D.ecologica.fontes_sem_exterior;
    const nA = ctx.nf(), nB = ctx.nf();
    figurasComAbas(fig, [
      { rotulo: T('c3.aba1'), montar: p => figura(p, {
        n: nA, titulo: T('c3.fig1.titulo'),
        sub: T('c3.fig1.sub'),
        leitura: T('c3.fig1.leitura'),
        desenhar: caixa => {
          const fora = G.dispersao(caixa, {
            aria: T('c3.fig1.aria', { mun: fmt.int(5571) }),
            pontos: doBrasil().map(m => ({ x: m.o, y: m.ds, peso: m.E1, lado: m.ds >= 0 ? 'l' : 'f', titulo: nomeMun(m),
              linhas: [{ t: T('c3.dica.outros'), v: T('c3.dica.outros_v', { pct: fmt.pct(m.o, 1) }) }, { lado: 'l', t: T('dica.var_lula'), v: fmt.pp(m.ds) },
                { lado: 'f', t: T('dica.var_flavio'), v: fmt.pp(-m.ds) }, { t: T('tab.eleitorado'), v: fmt.int(m.E1) }] })),
            x: { min: 0, max: 35, passo: 5, fmt: v => fmt.pct(v, 0), rotulo: T('c3.fig1.eixo_x') },
            y: { min: -4, max: 8, passo: 2, fmt: v => fmt.decSinal(v, 0), rotulo: T('eixo.var_fatia_pp') },
            reta: { a: r.a, b: r.b, de: 2, ate: 25, rotulo: T('eixo.tendencia') },
            marca: { x: 100 * BR.O1 / (BR.L1 + BR.F1 + BR.O1), y: BR.ds, rotulo: BR.nome },
            rotulos: [{ x: 20, y: 3.4, lado: 'l', t: T('c1.fig1.rot_acima'), curto: T('c3.fig1.rot_acima_curto') },
              { x: 20, y: -2.4, lado: 'f', t: T('c1.fig1.rot_abaixo'), curto: T('c1.fig1.rot_abaixo_curto') }],
          });
          return fora ? T('fig.fora_escala', { n: fmt.int(fora) }) : '';
        },
        como: [
          T.f('c3.fig1.como1'),
          T('c3.fig1.como2', { o1: fmt.int(BR.O1), validos: fmt.int(BR.L1 + BR.F1 + BR.O1), pct: fmt.pct(100 * BR.O1 / (BR.L1 + BR.F1 + BR.O1), 2) }),
          T('c3.fig1.como3', { coef: coefTxt(vb.coef, 10) }),
          dadosComo(['municipios', 'hipoteses'], [3, 6])],
        notas: ['N06', 'N14'],
      }) },
      { rotulo: T('c3.aba2'), montar: p => figura(p, {
        n: nB, titulo: T('c3.fig2.titulo', faixa),
        sub: T('c3.fig2.sub'),
        leitura: T('c3.fig2.leitura', { ...faixa, so: nf(S.O.lula * 100, 0), sc: nf(S.C.lula * 100, 0), sr: nf(S.R.lula * 100, 0) }),
        legenda: [{ t: T('leg.ic95'), tipo: 'ic' }, { t: T('leg.cruza50'), tipo: 'barra', lado: 'dentro' }],
        desenhar: caixa => G.divisao(caixa, { aria: T('c3.fig2.aria'), rotuloX: T('c3.fig2.eixo'), margE: 250, margEstreito: 112, linhas: linhasVieram() }),
        fonte: T('c3.fig2.fonte', { mun: fmt.int(5571), sec: fmt.int(D.secoes.secoes) }),
        como: [
          T.f('c3.fig2.como1'),
          T('c3.fig2.como2', { n: fmt.int(1000) }),
          T('c3.fig2.como3'),
          T.f('c3.fig2.como5'),
          T.f('c3.fig2.como6', comumSecoes()),
          T('c3.fig2.como4'), dadosComo(['de_onde_vieram'], [6])],
        notas: ['N06', 'N07', 'N16', 'N21', 'N22'],
      }) },
    ], 'cap3');
    notaLateral(lado, T('c3.lado.tit'), T('c3.lado.1'));
    const det = detalhes(ctx);
    comoSeChegou(det, H, {
      texto: T('c3.chegou.texto'),
      porque: T.f('c3.chegou.porque', { cap: fmt.pct(BR.cap, 1) }),
      variavel: T('c3.chegou.variavel'), unidade: T('un.10pontos'), fator: 10, n: ctx.nf(), t: ctx.nt(),
    });
    const t = secao(det, T('cap.resultado_texto'));
    const SE = D.poucos_grupos.sem_um_estado.H3.estados; // T32 (M5): [coeficiente, valor-p] sem cada estado
    P(t, '', T('c3.texto.1', { pts: pontos(v.coef * 10), ic0: fmt.decSinal(v.ic95[0] * 10, 2), ic1: fmt.decSinal(v.ic95[1] * 10, 2),
      c0: fmt.decSinal(v.ic95_cr1[0] * 10, 2), c1: fmt.decSinal(v.ic95_cr1[1] * 10, 2),
      p: fmt.abs(v.p_selvagem, 2), p05: nf(0.05, 2), br: fmt.abs(vb.coef * 10, 1), br0: fmt.abs(vb.ic95[0] * 10, 1), br1: fmt.abs(vb.ic95[1] * 10, 1),
      sp: fmt.decSinal(SE.SP[0] * 10, 2), psp: fmt.p(SE.SP[1]), pba: fmt.abs(SE.BA[1], 2), pmg: fmt.abs(SE.MG[1], 2),
      iq: fmt.abs(v.efeito_interquartil_pp, 1) }));
    const ci = D.ecologica.conferencias.com_intercepto, TR = D.transicao.brasil;
    P(t, '', ...T.f('c3.texto.2', { ol: nf(E.O.lula * 100, 0), of: nf(E.O.flavio * 100, 0), ol0: nf(E.O.lula_ic95[0] * 100, 0), ol1: nf(E.O.lula_ic95[1] * 100, 0),
      cl: nf(E.C.lula * 100, 0), cf: nf(E.C.flavio * 100, 0), cl0: nf(E.C.lula_ic95[0] * 100, 0), cl1: nf(E.C.lula_ic95[1] * 100, 0),
      rl: fmt.comPct(nf(E.R.lula * 100, 0)), rf: fmt.comPct(fmt.dec(E.R.flavio * 100, 0)), ciol: fmt.comPct(nf(ci.O.lula * 100, 1)),
      il: nf(ci.intercepto.lula * 100, 1), ifl: fmt.dec(ci.intercepto.flavio * 100, 1),
      tl: fmt.comPct(nf(TR.outros_lula_entre_os_dois * 100, 1)), tl0: nf(TR.outros_lula_entre_os_dois_ic95[0] * 100, 1),
      tl1: nf(TR.outros_lula_entre_os_dois_ic95[1] * 100, 1) }));
    // T35 (P28): a conta por seção, que o capítulo 4 usa por lugar
    const ps = (e, k) => ({ [k]: fmt.comPct(nf(e.lula * 100, 0)), [k + '0']: nf(e.lula_ic95[0] * 100, 0), [k + '1']: nf(e.lula_ic95[1] * 100, 0) });
    P(t, '', ...T.f('c3.texto.secoes', { ...ps(S.O, 'sol'), ...ps(S.C, 'scl'), ...ps(S.R, 'srl'), comum: comumSecoes().comum }));
    // T32 (M1, m3): a matriz de transição, conferência calculada depois do parecer
    const M = TR.matriz, pc = x => fmt.comPct(fmt.dec(x * 100, 1));
    P(t, '', ...T.f('c3.texto.3', { ll: pc(M[0][0].valor), ff: pc(M[1][1].valor), fora: TR.celulas_fora_0_100.length, mun: fmt.int(D.limites_duncan_davis.municipios) }));
    const pcIc = c => T('dica.pct_ic_curto', { v: pc(c.valor), a: fmt.dec(c.ic95[0] * 100, 0), b: fmt.dec(c.ic95[1] * 100, 0) });
    G.tabela(t, { legenda: { n: ctx.nt(), t: T('c3.trans.titulo') }, ordenavel: false,
      grafico: { sub: T('vd.c3.trans_sub'), desenhar: caixa => G.calor(caixa, { aria: T('vd.aria', { t: T('c3.trans.titulo') }),
        linhas: D.transicao.origens.map(o => ({ nome: T('trans.' + o) })), colunas: D.transicao.destinos.map(d => ({ nome: T('trans.' + d) })),
        cel: (i, j) => ({ t: M[i][j].valor, rotulo: fmt.dec(M[i][j].valor * 100, 0),
          dica: { titulo: T('vd.c3.trans_dica', { de: T('trans.' + D.transicao.origens[i]), para: T('trans.' + D.transicao.destinos[j]) }),
            linhas: [{ t: T('vd.estimativa'), v: pcIc(M[i][j]) }] } }) }) },
      linhas: D.transicao.origens.map((o, i) => [o, M[i]]),
      colunas: [{ t: T('c3.trans.origem'), v: l => T('trans.' + l[0]) }].concat(D.transicao.destinos.map((d, j) => ({
        t: T('trans.' + d), num: true, v: l => l[1][j].valor,
        f: (_, l) => pcIc(l[1][j]) }))) });
    P(t, 'nota-tab', T('c3.trans.nota'));
    const cf = D.ecologica.conferencias;
    const versoesEco = [[T('c3.tab.principal'), E], [T('c3.tab.intercepto'), cf.com_intercepto], [T('versao.sem_peso'), cf.sem_peso], [T('c3.tab.estados'), cf.bootstrap_municipios],
      [T('c3.tab.secoes'), S]];
    const pctIcLula = e => T('dica.pct_ic', { v: fmt.comPct(nf(e.lula * 100, 1)), a: nf(e.lula_ic95[0] * 100, 1), b: nf(e.lula_ic95[1] * 100, 1) });
    G.tabela(t, { legenda: { n: ctx.nt(), t: T('c3.tab.titulo') }, ordenavel: false,
      grafico: { legenda: [{ t: T('leg.ic95'), tipo: 'ic' }, { t: T('leg.cruza50'), tipo: 'barra', lado: 'dentro' }],
        desenhar: caixa => G.divisao(caixa, { aria: T('vd.aria', { t: T('c3.tab.titulo') }), rotuloX: T('c3.fig2.eixo'), margE: 250, margEstreito: 112,
          linhas: [['O', 'fonte.O'], ['C', 'fonte.C'], ['R', 'fonte.R']].flatMap(([k, n]) => [{ grupo: T(n) }].concat(versoesEco.map(([nome, e]) => ({
            nome, curto: nome.length > 14 ? nome.slice(0, 13).trim() + '…' : nome, lula: e[k].lula, ic: e[k].lula_ic95, destaque: e === E,
            dica: { titulo: T('vd.c3.versao_dica', { fonte: T(n), versao: nome }), linhas: [{ lado: 'l', t: T('nome.lula'), v: pctIcLula(e[k]) }] } })))) }) },
      linhas: versoesEco, destaque: l => l[1] === E,
      colunas: [{ t: T('tab.versao'), v: l => l[0] }].concat([['O', T('fonte.O.col')], ['C', T('fonte.C.col')], ['R', T('fonte.R.col')]].map(([k, n]) => ({
        t: n, num: true, v: l => l[1][k], f: e => T('dica.pct_ic_curto', { v: fmt.comPct(nf(e.lula * 100, 1)), a: nf(e.lula_ic95[0] * 100, 1), b: nf(e.lula_ic95[1] * 100, 1) }) }))) });
    P(t, 'nota-tab', T('c3.tab.nota'));
  }

  // ---------- Capítulo 4 ----------
  function cap4(ctx) {
    const H = D.hipoteses.H4, v = H.versoes[0];
    const subiu = UFS.filter(u => u.da > 0);
    const porRegiao = {};
    for (const u of subiu) (porRegiao[u.regiao] = porRegiao[u.regiao] || []).push(u);
    const partes = Object.entries(porRegiao).flatMap(([r, us]) => {
      const total = UFS.filter(u => u.regiao === r).length;
      return us.length === total && total > 1 ? [T('c4.todos_da_regiao', { n: total, regiao: r })] : us.map(u => u.nome);
    });
    cabecalho(ctx, ...T.f('c4.resposta', { comp: N(fmt.miAbs(BR.C2 - BR.C1)), a1: N(fmt.pct(BR.a1, 2)), a2: N(fmt.pct(BR.a2, 2)), da: N(T('c4.ponto_sinal', { n: fmt.decSinal(BR.da, 2) })),
      n: subiu.length, ufs: listaE(partes), ic0: fmt.decSinal(v.ic95[0], 2), ic1: fmt.decSinal(v.ic95[1], 2) }));
    caixaHipotese(ctx.cab, T('c4.hipotese'), H, () => ctx.detalhes);
    const { fig, lado } = corpo(ctx);
    const PL = D.por_lugar;
    const ordemDa = UFS.slice().sort((a, b) => b.da - a.da);
    const das = ordemDa.map(u => u.da);
    const nA = ctx.nf(), nB = ctx.nf();
    figurasComAbas(fig, [
      { rotulo: T('c4.aba1'), montar: p => figura(p, {
        n: nA, titulo: T('c4.fig1.titulo', { caiu: 27 - subiu.length, subiu: subiu.length }),
        sub: T('c4.fig1.sub'),
        leitura: T('c4.fig1.leitura', { da: fmt.pp(BR.da) }),
        desenhar: caixa => G.barras(caixa, {
          aria: T('c4.fig1.aria'),
          x: { min: 2 * Math.floor(Math.min(...das) / 2), max: 2 * Math.ceil(Math.max(...das) / 2), passo: 2, fmt: v => fmt.decSinal(v, 0), rotulo: T('c4.fig1.eixo') },
          margE: 150, margEstreito: 34, altLinha: 15, topo: 24, margD: 64,
          ref: { v: BR.da, rotulo: BR.nome },
          linhas: ordemDa.map(u => ({ nome: u.nome, curto: u.codigo, v: u.da, rotulo: fmt.decSinal(u.da, 2),
            dica: { titulo: u.nome, linhas: [{ t: T('c4.dica.abst1'), v: fmt.pct(u.a1, 2) }, { t: T('c4.dica.no2'), v: fmt.pct(u.a2, 2) },
              { t: T('tab.variacao'), v: fmt.pp(u.da) }, { t: T('tab.comparecimento'), v: T('c4.dica.eleitores', { n: fmt.intSinal(u.C2 - u.C1) }) }] } })),
        }),
        como: [
          T.f('c4.fig1.como1'),
          T('c4.fig1.como2', { a1: fmt.pct(BR.a1, 2), a2: fmt.pct(BR.a2, 2), da: fmt.pp(BR.da) }),
          T('c4.fig1.como3'), dadosComo(['estados'], [3])],
        notas: ['N05'],
      }) },
      { rotulo: T('c4.aba2'), montar: p => {
        const passa = l => l.fontes.C.passa;
        const linhas = [];
        const linha = (l, destaque) => {
          const c = l.fontes.C, caiu = l.saldo_comparecimento === 'caiu';
          const lugar = l.nivel === 'uf' ? NOME_UF[l.lugar] : l.lugar;
          // T32 (m1): † onde alguma fonte do lugar sai de 0% a 100% (o modelo não descreve bem o lugar)
          const marca = s => (c.passa && c.aviso_modelo ? T('g.aviso_nome', { nome: s }) : s);
          const nome = marca(caiu ? T('c4.caiu_seta', { lugar }) : lugar);
          const sigla = l.nivel === 'uf' ? l.lugar : l.codigo;
          return { nome, curto: marca(caiu ? T('c4.caiu_seta_curto', { lugar: sigla }) : sigla), destaque,
            lula: c.lula, ic: c.lula_ic95, naoDeu: c.passa ? null : c.motivo,
            dica: { titulo: lugar, linhas: c.passa ? [
              { t: T(caiu ? 'c4.dica.caiu' : 'c4.dica.subiu'), v: fmt.intSinal(l.var_comparecimento) },
              { lado: 'l', t: T('nome.lula'), v: T('dica.pct_ic', { v: fmt.comPct(nf(c.lula * 100, 1)), a: nf(c.lula_ic95[0] * 100, 1), b: nf(c.lula_ic95[1] * 100, 1) }) },
              { lado: 'f', t: T('nome.flavio'), v: T('dica.pct_ic', { v: fmt.comPct(nf(c.flavio * 100, 1)), a: nf(c.flavio_ic95[0] * 100, 1), b: nf(c.flavio_ic95[1] * 100, 1) }) },
              { t: T('tab.municipios'), v: fmt.int(l.n) }, { t: T('tab.secoes'), v: fmt.int(l.secoes) }].concat(c.aviso_modelo ? [{ t: T('dica.aviso_modelo'), v: T('dica.aviso_modelo_txt') }] : [])
              : [{ t: T('dica.nao_deu'), v: '' }, { t: T('dica.motivo'), v: c.motivo }] } };
        };
        linhas.push(linha(PL[0], true));
        linhas.push({ grupo: T('c4.grupo.regioes') });
        PL.filter(l => l.nivel === 'regiao').forEach(l => linhas.push(linha(l)));
        linhas.push({ grupo: T('c4.grupo.estados') });
        PL.filter(l => l.nivel === 'uf' && passa(l)).sort((a, b) => b.fontes.C.lula - a.fontes.C.lula).forEach(l => linhas.push(linha(l)));
        const naoUf = PL.filter(l => l.nivel === 'uf' && !passa(l));
        const motivos = {};
        for (const l of naoUf) (motivos[l.fontes.C.motivo] = motivos[l.fontes.C.motivo] || []).push(NOME_UF[l.lugar]);
        const regDeu = PL.filter(l => l.nivel === 'regiao' && passa(l)).length, ufDeu = PL.filter(l => l.nivel === 'uf' && passa(l)).length;
        const ufsDeu = PL.filter(l => l.nivel === 'uf' && passa(l));
        const maiorL = ufsDeu.filter(l => l.fontes.C.maior_parte === 'Lula').length, maiorF = ufsDeu.filter(l => l.fontes.C.maior_parte === 'Flávio').length;
        figura(p, {
          n: nB, titulo: T(ufDeu - maiorL - maiorF ? 'c4.fig2.titulo_sem_lado' : 'c4.fig2.titulo', { n: ufDeu, l: maiorL, f: maiorF, s: ufDeu - maiorL - maiorF }),
          sub: T('c4.fig2.sub'),
          // T35: sem estimativa fora de 0% a 100%, a frase da marca † só entra se algum lugar tiver a marca
          leitura: T('c4.fig2.leitura', { reg: regDeu, ufs: ufDeu }) + (PL.some(l => l.fontes.C.passa && l.fontes.C.aviso_modelo) ? T('c4.fig2.leitura_aviso', { marca: T('g.aviso_marca') }) : '')
            + T('c4.fig2.leitura_fim'),
          legenda: [{ t: T('leg.ic95'), tipo: 'ic' }, { t: T('leg.cruza50'), tipo: 'barra', lado: 'dentro' }, { t: T('c4.fig2.leg_seta'), tipo: 'seta' }], // QA, L2: a seta é explicada junto do gráfico
          desenhar: caixa => G.divisao(caixa, { aria: T('c4.fig2.aria'), linhas,
            rotuloX: T('c4.fig2.eixo'), margE: 150, margEstreito: 40, altLinha: 19 }),
          extra: f => P(f, 'fig-nao-deu', B(T('c4.fig2.nao_deu', { n: naoUf.length })),
            T('c4.fig2.nao_deu_lista', { lista: listaE(Object.entries(motivos).map(([m, us]) => T('dica.v_par', { v: listaE(us), p: m }))) })),
          fonte: T('c4.fig2.fonte'),
          como: [
            T.f('c4.fig2.como1', comumSecoes()),
            T.f('c4.fig2.como2'),
            T('c4.fig2.como3'),
            T.f('c4.fig2.como4', { n22: nd('N22'), n21: nd('N21'), n: D.secoes.c_mantem, total: D.secoes.c_lugares }),
            T.f('c4.fig2.como5', { muda: listaE(D.secoes.c_muda_de_lado.map(u => NOME_UF[u])) }), dadosComo(['de_onde_vieram'], [6])],
          notas: ['N05', 'N07', 'N16', 'N21', 'N22'],
        });
      } },
    ], 'cap4');
    notaLateral(lado, T('c4.lado.tit'), T('c4.lado.1'), T('c4.lado.2'));
    const det = detalhes(ctx);
    comoSeChegou(det, H, {
      texto: T('c4.chegou.texto'),
      porque: T.f('c4.chegou.porque', { cap: fmt.pct(BR.cap, 1) }),
      variavel: T('c4.chegou.variavel'), unidade: T('un.1ponto'), fator: 1, n: ctx.nf(), t: ctx.nt(),
    });
    const t = secao(det, T('cap.resultado_texto'));
    const [cl, , cf] = D.complementos.H4;
    P(t, '', T('c4.texto.1', { ic0: fmt.decSinal(v.ic95[0], 2), ic1: fmt.decSinal(v.ic95[1], 2) }));
    P(t, '', ...T.f('c4.texto.2', { cl: fmt.abs(-cl.coef, 2), cl0: fmt.abs(-cl.ic95[1], 2), cl1: fmt.abs(-cl.ic95[0], 2),
      cf: fmt.abs(-cf.coef, 2), cf0: fmt.abs(-cf.ic95[1], 2), cf1: fmt.abs(-cf.ic95[0], 2) }));
    P(t, '', ...T.f('c4.texto.3', { n05: nd('N05') }));
    const tb = secao(det, T('c4.tab.secao'));
    const lug4 = [BR, ...D.regioes.filter(r => r.codigo !== 'EX'), ...D.ufs.filter(u => u.codigo !== 'ZZ')];
    const cols4 = [{ t: T('tab.lugar'), v: u => u.nome }, { t: T('tab.abst_1'), num: true, v: u => u.a1, f: v => fmt.pct(v, 2) },
      { t: T('tab.turno2_curto'), num: true, v: u => u.a2, f: v => fmt.pct(v, 2) }, { t: T('tab.variacao'), num: true, v: u => u.da, f: v => fmt.pp(v) },
      { t: T('tab.comparecimento'), num: true, v: u => u.C2 - u.C1, f: fmt.intSinal }];
    const linha4 = u => ({ nome: u.nome, curto: u.codigo || u.nome.slice(0, 3), destaque: u === BR, vals: [{ v: u.a1, lado: 'muted' }, { v: u.a2, lado: 'ink' }],
      dica: dicaColunas(cols4.slice(1), u, u.nome) });
    G.tabela(tb, { legenda: { n: ctx.nt(), t: T('c4.tab.titulo') },
      linhas: [BR, ...D.regioes, ...D.ufs.filter(u => u.codigo !== 'ZZ')], ordem: null, destaque: u => u === BR || D.regioes.includes(u),
      colunas: cols4,
      grafico: { legenda: [{ t: T('g.turno1'), lado: 'muted' }, { t: T('g.turno2'), lado: 'ink' }],
        desenhar: caixa => G.linhasPontos(caixa, { aria: T('vd.aria', { t: T('c4.tab.titulo') }), margE: 150, margEstreito: 40, altLinha: 16, topo: 26,
          x: eixo(lug4.flatMap(u => [u.a1, u.a2]), tickPct, T('vd.c4.eixo'), { zero: false }),
          linhas: [linha4(BR), { grupo: T('c4.grupo.regioes') }, ...D.regioes.filter(r => r.codigo !== 'EX').map(linha4),
            { grupo: T('vd.grupo.estados') }, ...D.ufs.filter(u => u.codigo !== 'ZZ').slice().sort((a, b) => b.a2 - a.a2).map(linha4)] }) } });
    const rk = secao(det, T('c4.rank.secao'));
    const cols = [{ t: T('tab.eleitorado'), num: true, v: m => m.E1, f: fmt.int }, { t: T('tab.abst_1'), num: true, v: m => m.a1, f: v => fmt.pct(v, 1) },
      { t: T('tab.turno2_curto'), num: true, v: m => m.a2, f: v => fmt.pct(v, 1) }, { t: T('tab.variacao'), num: true, v: m => m.da, f: v => fmt.pp(v) }];
    const piso = acimaDoPiso();
    const g4 = { v: m => m.da, rotulo: m => fmt.pp(m.da), f: tickPp, eixo: T('c4.fig1.eixo') };
    rankingMunicipios(rk, ctx.nt(), T('c4.rank.titulo1'), piso.slice().sort((a, b) => b.da - a.da).slice(0, 10), cols, g4);
    rankingMunicipios(rk, ctx.nt(), T('c4.rank.titulo2'), piso.slice().sort((a, b) => a.da - b.da).slice(0, 10), cols, g4);
    const munSubiu = doBrasil().filter(m => m.da > 0).length;
    P(rk, 'nota-tab', T('c4.rank.nota', { n: fmt.int(munSubiu), total: fmt.int(doBrasil().length) }));
    const fu = secao(det, T('c4.funil.secao'));
    const F = funilFig(fu, ctx.nf(), 'var_abstencao', m => m.da, T('c4.fig1.eixo'),
      T('c4.funil.titulo'), T('c4.funil.sub'), 'ink', 'ink');
    P(fu, '', T('c4.funil.texto', { p998: fmt.pct(99.8, 1), n: fmt.int(F.fora998), acima: fmt.int(F.fora998_acima) }));
    const es = secao(det, T('c4.lugar.secao'));
    const PLM = Object.fromEntries(D.por_lugar_municipios.map(l => [l.lugar, l.fontes]));
    const pIc = c => ({ v: c.lula * 100, ic: c.lula_ic95.map(x => x * 100) });
    const pctIcC = c => T('dica.pct_ic', { v: fmt.comPct(nf(c.lula * 100, 1)), a: nf(c.lula_ic95[0] * 100, 1), b: nf(c.lula_ic95[1] * 100, 1) });
    const nomeL = l => (l.nivel === 'uf' ? NOME_UF[l.lugar] : l.lugar);
    const linhaL = l => {
      const c = l.fontes.C, m = PLM[l.lugar].C, vals = [];
      if (c.passa) vals.push(Object.assign({ lado: 'ink', cheio: true }, pIc(c)));
      if (m.passa) vals.push(Object.assign({ lado: 'muted', cheio: true }, pIc(m)));
      return { nome: nomeL(l), curto: l.nivel === 'uf' ? l.lugar : l.codigo || nomeL(l).slice(0, 3), vals, destaque: l.nivel === 'brasil',
        dica: { titulo: nomeL(l), linhas: [{ t: T('vd.c4.secoes'), v: c.passa ? pctIcC(c) : T('dica.nao_deu') }, { t: T('tab.por_municipio'), v: m.passa ? pctIcC(m) : T('dica.nao_deu') }] } };
    };
    const PLg = PL.filter(l => l.fontes.C.passa || PLM[l.lugar].C.passa);
    G.tabela(es, { legenda: { n: ctx.nt(), t: T('c4.lugar.titulo') }, ordenavel: false,
      grafico: { legenda: [{ t: T('vd.c4.secoes'), lado: 'ink' }, { t: T('tab.por_municipio'), lado: 'muted' }, { t: T('leg.ic95'), tipo: 'ic' }],
        sub: PLg.length < PL.length ? T.p('vd.c4.lugar_sub', PL.length - PLg.length, { n: PL.length - PLg.length }) : null,
        desenhar: caixa => G.coeficientesPar(caixa, { aria: T('vd.aria', { t: T('c4.lugar.titulo') }), margE: 150, margEstreito: 40,
          x: { min: 0, max: 100, passo: 25, ref: 50, fmt: v => fmt.pct(v, 0), rotulo: T('vd.c4.lugar_eixo') }, linhas: PLg.map(linhaL) }) },
      linhas: PL, destaque: l => l.nivel !== 'uf',
      colunas: [{ t: T('tab.lugar'), v: l => (l.nivel === 'uf' ? NOME_UF[l.lugar] : l.lugar) }, { t: T('tab.municipios'), num: true, v: l => l.n, f: fmt.int },
        { t: T('tab.comparecimento'), num: true, v: l => l.var_comparecimento, f: fmt.intSinal },
        { t: T('tab.parte_lula'), num: true, v: l => l.fontes.C, f: c => (c.passa ? T('dica.pct_ic_curto', { v: fmt.comPct(nf(c.lula * 100, 1)), a: nf(c.lula_ic95[0] * 100, 1), b: nf(c.lula_ic95[1] * 100, 1) }) : fmt.vazio) },
        // T35 (P28): a conta entre municípios, que a figura mostrava antes, como conferência ao lado
        { t: T('tab.por_municipio'), num: true, v: l => PLM[l.lugar].C, f: c => (c.passa ? T('dica.pct_ic_curto', { v: fmt.comPct(nf(c.lula * 100, 1)), a: nf(c.lula_ic95[0] * 100, 1), b: nf(c.lula_ic95[1] * 100, 1) }) : fmt.vazio) },
        { t: T('tab.leitura'), v: l => l, f: l => {
          const c = l.fontes.C, perda = l.saldo_comparecimento === 'caiu';
          const lado = c.maior_parte === 'Lula' || c.maior_parte === 'Flávio' ? T('c4.lugar.maior', { quem: TD(c.maior_parte) }) : T('c4.lugar.sem_lado');
          const leitura = !c.passa ? T('c4.lugar.nao_deu', { motivo: c.motivo }) : perda ? T('c4.lugar.perda', { lado }) : lado;
          return c.passa && c.aviso_modelo ? T('c4.lugar.aviso', { leitura }) : leitura;
        } }] });
  }

  // ---------- Capítulo 5 ----------
  function cap5(ctx) {
    const H5 = D.h5, cargos = ['federal', 'estadual', 'senador'];
    const vf = H5.federal.versoes[0];
    cabecalho(ctx, ...T.f('c5.resposta', { ic: N(T('c5.resposta.ic', { a: fmt.decSinal(vf.ic95[0] * 10, 2), b: fmt.decSinal(vf.ic95[1] * 10, 2) })) }));
    const todasInc = cargos.every(c => H5[c].classificacao === 'inconclusiva');
    caixaHipotese(ctx.cab, T('c5.hipotese'),
      { classificacao: todasInc ? 'inconclusiva' : 'mista' }, () => ctx.detalhes, T(todasInc ? 'c5.status_inc' : 'c5.status_cargo'));
    const { fig, lado } = corpo(ctx);
    const linhas = [];
    for (const c of cargos) {
      linhas.push({ grupo: H5[c].cargo });
      for (const vv of H5[c].versoes.filter(x => /(principal|Brasil|espelho Flávio)$/.test(x.versao))) {
        linhas.push({ nome: curtoVersao(vv, 0), curto: curtoVersao(vv, 1),
          v: vv.coef * 10, ic: vv.ic95.map(x => x * 10), destaque: /principal$/.test(vv.versao),
          dica: { titulo: T('c5.dica.titulo', { cargo: H5[c].cargo, versao: nomeVersao(vv) }), linhas: [{ t: T('c5.dica.coef10'), v: coefTxt(vv.coef, 10) },
            { t: T('tab.ic95'), v: icTxt(vv.ic95, 10) }, { t: T('dica.valor_p'), v: fmt.p(vv.p_selvagem) },
            { t: T('tab.municipios'), v: fmt.int(vv.n) }, { t: T('tab.resultado'), v: classeTexto(vv) }] } });
      }
    }
    const cruzam = linhas.filter(l => l.ic).every(l => l.ic[0] <= 0 && l.ic[1] >= 0);
    figura(fig, {
      n: ctx.nf(), titulo: T(cruzam ? 'c5.fig1.titulo' : 'c5.fig1.titulo_muda'),
      sub: T('c5.fig1.sub'),
      leitura: T('c5.fig1.leitura'),
      desenhar: caixa => G.coeficientes(caixa, {
        aria: T('c5.fig1.aria'),
        x: { min: -0.3, max: 0.3, passo: 0.1, fmt: v => fmt.decSinal(v, 1), rotulo: T('c5.fig1.eixo') },
        lados: [T('c5.fig1.esq'), T('forest.dir_previsto')], margE: 200, margEstreito: 74, altLinha: 20, linhas,
      }),
      como: [
        T.f('c5.fig1.como1', { corte: nf(4.49, 2), v0: nf(Math.max(...D.partidos.filter(p => p.esquerda).map(p => p.posicao)), 2), v1: nf(Math.min(...D.partidos.filter(p => p.posicao !== null && !p.esquerda).map(p => p.posicao)), 2) }),
        T.f('c5.fig1.como2'),
        T('c5.fig1.como3'),
        T('c5.fig1.como4'), dadosComo(['partidos', 'esquerda_municipios', 'hipoteses'], [4, 5, 6])],
      fonte: T('c5.fig1.fonte'),
      notas: ['N01', 'N02', 'N10', 'N11', 'N13', 'N14', 'N15'],
    });
    notaLateral(lado, T('c5.lado.tit'), T('c5.lado.1'),
      T('c5.lado.2', { ufs: listaE(Object.keys(H5.senador_estados_fora).map(u => NOME_UF[u])) }));
    const det = detalhes(ctx);
    const s = el('section', 'como-chegou', undefined, det);
    el('h3', '', T('hip.como_chegou'), s);
    P(s, '', ...T.f('chegou.hipotese', { texto: el('i', '', T('c5.chegou.texto')) }));
    P(s, '', ...T.f('c5.chegou.teste'));
    P(s, '', ...T.f('chegou.regra'));
    regra(s, 2);
    for (const c of cargos) {
      const vv = H5[c].versoes[0];
      P(s, '', ...T.f('c5.chegou.cargo', { cargo: B(T('regra.item', { t: H5[c].cargo })), coef: coefTxt(vv.coef, 10), ic: icTxt(vv.ic95, 10),
        p: fmt.p(vv.p_selvagem), porque: porQue(vv), classe: B(classeTexto(vv).toLowerCase()), conf: resumoConferencias(H5[c]) }));
    }
    P(s, '', ...T.f('c5.chegou.unica'));
    for (const c of cargos) {
      const d = el('details', 'det-aninhado', undefined, s);
      el('summary', '', T('c5.chegou.todas', { cargo: H5[c].cargo.replace(/^\S+/, p => p.toLowerCase()) }), d);
      const fat5 = vv => (/escala contínua$/.test(vv.versao) ? 1 : 10);
      tabelaVersoes(d, ctx.nt(), T('c5.chegou.tabela', { cargo: H5[c].cargo }), H5[c].versoes, fat5, graficoVersoes(H5[c].versoes, fat5, T('un.10pontos')));
    }
    const t = secao(det, T('cap.resultado_texto'));
    const ve = H5.estadual.versoes[0], vs = H5.senador.versoes[0];
    P(t, '', T('c5.texto.1', { f0: fmt.decSinal(vf.ic95[0] * 10, 2), f1: fmt.decSinal(vf.ic95[1] * 10, 2), e0: fmt.decSinal(ve.ic95[0] * 10, 2),
      e1: fmt.decSinal(ve.ic95[1] * 10, 2), s0: fmt.decSinal(vs.ic95[0] * 10, 2), s1: fmt.decSinal(vs.ic95[1] * 10, 2) }));
    const r = secao(det, T('c5.ressalvas.secao'));
    const n12 = el('a', '', T('c5.ressalvas.n12'), null); n12.href = '#metodo/nota-N12';
    P(r, '', ...T.f('c5.ressalvas', { n02: nd('N02'), n11: nd('N11'), n12 }));
  }

  // ---------- Capítulo 6 ----------
  function cap6(ctx) {
    const regs = D.regioes.slice().sort((a, b) => b.dM - a.dM), ufs = D.ufs.slice().sort((a, b) => b.dM - a.dM);
    const aFavor = UFS.filter(u => u.dM > 0).length;
    cabecalho(ctx, ...T.f('c6.resposta', { dm: N(fmt.miAbs(BR.dM)), r0: regs[0].nome, p0: fmt.pct(regs[0].peso, 1),
      r1: regs[1].nome, p1: fmt.pct(regs[1].peso, 1), uf: ufs[0].nome, puf: fmt.pct(ufs[0].peso, 1),
      onde: aFavor === 27 ? T('c6.resposta.todos') : T('c6.resposta.alguns', { n: aFavor }) }));
    const { fig, lado } = corpo(ctx);
    const dicaU = u => [{ t: T('c6.dica.mudanca'), v: fmt.intSinal(u.dM) }, { t: T('c6.dica.peso'), v: fmt.pct(u.peso, 1) },
      { t: T('c6.dica.dif1'), v: fmt.intSinal(u.M1) }, { t: T('c6.dica.dif2'), v: fmt.intSinal(u.M2) },
      { t: T('c6.dica.captura'), v: fmt.pct(u.cap, 1) }];
    const tot = t => [{ lado: 'l', t: T('nome.lula'), v: fmt.int(t === 1 ? BR.L1 : BR.L2) }, { lado: 'f', t: T('nome.flavio'), v: fmt.int(t === 1 ? BR.F1 : BR.F2) },
      { t: T('res.fita_diferenca'), v: fmt.intSinal(t === 1 ? BR.M1 : BR.M2) }];
    const n = ctx.nf(); // as duas versões são a mesma figura, somando regiões ou estados
    const comum = {
      n,
      leitura: T('c6.fig1.leitura', { m1: fmt.mi(BR.M1), m2: fmt.mi(BR.M2) }),
      como: [
        T.f('c6.fig1.como1'),
        T('c6.fig1.como2', { uf: ufs[0].nome, dm: fmt.intSinal(ufs[0].dM), br: fmt.intSinal(BR.dM), peso: fmt.pct(ufs[0].peso, 1) }),
        T('c6.fig1.como3'), dadosComo(['estados'], [3])],
      notas: ['N06', 'N08'],
    };
    figurasComAbas(fig, [
      { rotulo: T('c6.aba1'), montar: p => figura(p, Object.assign({
        titulo: T('c6.fig1.titulo_reg', { r0: regs[0].nome, r1: regs[1].nome, p: fmt.pct(regs[0].peso + regs[1].peso, 1) }),
        sub: T('c6.fig1.sub_reg'),
        desenhar: caixa => G.ponte(caixa, { M1: BR.M1, M2: BR.M2, dica1: tot(1), dica2: tot(2),
          aria: T('c6.fig1.aria_reg', { m1: fmt.mi(BR.M1), m2: fmt.mi(BR.M2) }),
          itens: regs.map(u => ({ nome: u.nome, curto: u.nome, dM: u.dM, dica: dicaU(u) })) }) }, comum)) },
      { rotulo: T('c6.aba2'), montar: p => figura(p, Object.assign({
        titulo: T('c6.fig1.titulo_uf', { uf: ufs[0].nome, p: fmt.pct(ufs[0].peso, 1) }),
        sub: T('c6.fig1.sub_uf'),
        desenhar: caixa => G.ponte(caixa, { M1: BR.M1, M2: BR.M2, dica1: tot(1), dica2: tot(2),
          aria: T('c6.fig1.aria_uf', { m1: fmt.mi(BR.M1), m2: fmt.mi(BR.M2) }),
          itens: ufs.map(u => ({ nome: u.nome, curto: u.codigo === 'ZZ' ? T('c6.ext_curto') : u.codigo, dM: u.dM, dica: dicaU(u) })) }) }, comum)) },
    ], 'cap6');
    // P32 (D63): quem estava à frente em cada estado e em quantos municípios a parte de cada um subiu
    const troca = UFS.filter(u => u.M1 < 0 && u.M2 > 0), mun = doBrasil();
    notaLateral(lado, T('c1.lado.tit'), T('c6.lado.1'), T('c6.lado.2', { uf: listaE(troca.map(u => u.nome)),
      l2: UFS.filter(u => u.M2 > 0).length, f2: UFS.filter(u => u.M2 < 0).length,
      sub: fmt.int(mun.filter(m => m.ds > 0).length), tot: fmt.int(mun.length), fsub: fmt.int(mun.filter(m => m.ds < 0).length) }));
    const det = detalhes(ctx);
    const semCap = UFS.filter(u => u.cap === null), acima = UFS.filter(u => u.cap !== null && u.cap > 100);
    const t = secao(det, T('cap.resultado_texto'));
    P(t, '', T('c6.texto.pesos', { lista: listaE(regs.map(r => T('c6.texto.peso_item', { regiao: r.nome, p: fmt.pct(r.peso, 1) }))) }),
      ...(semCap.length ? T.f('c6.texto.sem_cap', { ufs: listaE(semCap.map(u => u.nome)), n09: nd('N09') }) : []),
      acima.length ? T('c6.texto.acima', { ufs: listaE(acima.map(u => u.nome)) }) : '');
    // P32 (D63): quantos municípios fazem metade e um quarto da mudança da diferença, sem o exterior
    const dMs = mun.map(m => m.dM).sort((a, b) => b - a), somaBr = dMs.reduce((s, v) => s + v, 0);
    const ateParte = f => { let s = 0, i = 0; while (s < f * somaBr) s += dMs[i++]; return i; };
    const neg = dMs.filter(v => v < 0);
    P(t, '', T('c6.texto.concentra', { n50: fmt.int(ateParte(0.5)), n25: fmt.int(ateParte(0.25)), neg: fmt.int(neg.length),
      sneg: fmt.int(Math.abs(neg.reduce((s, v) => s + v, 0))) }));
    const cols6 = [{ t: T('tab.lugar'), v: u => (D.regioes.includes(u) ? T('c6.tab.regiao', { nome: u.nome }) : u.nome) },
        { t: T('c6.tab.dif1'), num: true, v: u => u.M1, f: fmt.intSinal }, { t: T('tab.turno2_curto'), num: true, v: u => u.M2, f: fmt.intSinal },
        { t: T('c6.tab.mudanca'), num: true, v: u => u.dM, f: fmt.intSinal }, { t: T('c6.tab.peso'), num: true, v: u => u.peso, f: v => fmt.pct(v, 1) },
        { t: T('c6.dica.captura'), num: true, v: u => u.cap, f: v => fmt.pct(v, 1) }, { t: T('c6.tab.fatia_var'), num: true, v: u => u.ds, f: v => fmt.pp(v) }];
    const nome6 = u => (D.regioes.includes(u) ? u.nome : u.nome);
    const linha6 = u => ({ nome: nome6(u), curto: u.codigo === 'ZZ' ? T('c6.ext_curto') : u.codigo || u.nome.slice(0, 3),
      vals: [{ v: u.M1, lado: 'muted' }, { v: u.M2, lado: 'ink' }], dica: dicaColunas(cols6.slice(1), u, cols6[0].v(u)) });
    const regs6 = D.regioes.filter(r => r.codigo !== 'EX').sort((a, b) => b.dM - a.dM), ufs6 = D.ufs.slice().sort((a, b) => b.dM - a.dM);
    G.tabela(t, { legenda: { n: ctx.nt(), t: T('c6.tab.titulo') },
      linhas: [...D.regioes.filter(r => r.codigo !== 'EX'), ...D.ufs], ordem: { col: 4, desc: true }, destaque: u => D.regioes.includes(u),
      colunas: cols6,
      grafico: { legenda: [{ t: T('g.turno1'), lado: 'muted' }, { t: T('g.turno2'), lado: 'ink' }], sub: T('vd.c6.sub'),
        desenhar: caixa => G.linhasPontos(caixa, { aria: T('vd.aria', { t: T('c6.tab.titulo') }), margE: 150, margEstreito: 40, altLinha: 16, topo: 30,
          lados: [T('g.seta_esq', { t: T('vd.frente_f') }), T('g.seta_dir', { t: T('vd.frente_l') })],
          x: eixo(regs6.concat(ufs6).flatMap(u => [u.M1, u.M2]), tickVotos, T('vd.c6.eixo')),
          linhas: [{ grupo: T('c4.grupo.regioes') }, ...regs6.map(linha6), { grupo: T('vd.grupo.estados') }, ...ufs6.map(linha6)] }) } });
  }

  // ---------- Capítulo 7 ----------
  function cap7(ctx) {
    const PR = D.projecao, fx = PR.faixas;
    const f1 = fx.find(f => f.faixa === '10 a 20');
    let desde = fx.length;
    while (desde > 0 && Math.abs(fx[desde - 1].projecao.erro_medio) < 0.1) desde--;
    let desde3 = fx.length;
    while (desde3 > 0 && Math.abs(fx[desde3 - 1].projecao.erro_medio) < 0.3) desde3--;
    const ate = fx.findIndex(f => f.projecao.erro_medio >= 0);
    const pctFaixa = f => fmt.comPct(f.faixa.split(' ')[0]); // o começo da faixa ("50 a 60"): um inteiro
    cabecalho(ctx, ...T.f('c7.resposta', { erro: N(pontos(-f1.projecao.erro_medio)), parcial: fmt.abs(-f1.parcial.erro_medio, 2),
      desde: pctFaixa(fx[desde]), lim: nf(0.1, 1) }));
    const { fig, lado } = corpo(ctx);
    const pts = PR.pontos.map(p => ({ x: p.apurado, proj: p.projecao, parc: p.parcial, hora: p.hora }));
    let buraco = null;
    for (let i = 1; i < pts.length; i++) if (!buraco || pts[i].x - pts[i - 1].x > buraco[1] - buraco[0]) buraco = [pts[i - 1].x, pts[i].x];
    const ys = pts.flatMap(p => [p.proj, p.parc]);
    figura(fig, {
      n: ctx.nf(), titulo: T('c7.fig1.titulo'),
      sub: T('c7.fig1.sub'),
      leitura: T('c7.fig1.leitura'),
      desenhar: caixa => G.linhaApuracao(caixa, { pontos: pts, final: PR.resultado_final_pct, buraco,
        rotulos: { x: 30, proj: T('c7.fig1.rot_proj'), parc: T('c7.fig1.rot_parc') },
        y: { min: Math.floor(Math.min(...ys) * 2) / 2, max: Math.ceil(Math.max(...ys, PR.resultado_final_pct) * 2) / 2 + 0.5, passo: 1 },
        aria: T('c7.fig1.aria', { de: fmt.pct(pts[0].x, 2), ate: fmt.comPct('100'), final: fmt.pct(PR.resultado_final_pct, 2) }) }),
      como: [
        T.f('c7.fig1.como1', { final: fmt.pct(PR.resultado_final_pct, 3) }),
        T.f('c7.fig1.como2'),
        T('c7.fig1.como3', { n: PR.leituras }), dadosComo(['apuracao_ao_vivo'], [7])],
      fonte: T('c7.fig1.fonte'),
      notas: ['N17'],
    });
    const irAoVivo = t => { const a = el('a', '', t); a.href = '#apuracao'; return a; };
    notaLateral(lado, T('c7.lado.tit'),
      T('c7.lado.1', { ate: pctFaixa(fx[ate]) }),
      T('c7.lado.2', { de: fmt.pct(buraco[0], 2), ate: fmt.pct(buraco[1], 1) }),
      T.f('c7.lado.3', { link: irAoVivo(T('c7.link_ao_vivo')) }));
    const det = detalhes(ctx);
    const t = secao(det, T('cap.resultado_texto'));
    P(t, '', T('c7.texto.1', { erro: pontos(-f1.projecao.erro_medio), parcial: fmt.abs(-f1.parcial.erro_medio, 2), lim3: nf(0.3, 1),
      desde3: pctFaixa(fx[desde3]), lim1: nf(0.1, 1), desde: pctFaixa(fx[desde]), ate: pctFaixa(fx[ate]),
      b0: fmt.pct(buraco[0], 2), b1: fmt.pct(buraco[1], 1) }));
    tabelaErroFaixas(t, ctx.nt());
    const a = secao(det, T('c7.ao_vivo.secao'));
    P(a, '', ...T.f('c7.ao_vivo.texto', { link: irAoVivo(T('c7.link_ao_vivo')) }));
  }
  /** A tabela do erro por faixa de apurado (capítulo 7 e Explorar), com o gráfico do erro médio das duas leituras (T36). */
  function tabelaErroFaixas(pai, n, comGrafico = true) {
    const PR = D.projecao, fx = PR.faixas;
    const nomeFx = f => (f.faixa === 'todas' ? T('c7.tab.todas') : T('c7.tab.faixa', { a: f.faixa.split(' a ')[0], b: f.faixa.split(' a ')[1] }));
    const vals = fx.flatMap(f => [f.projecao.erro_medio, f.parcial.erro_medio]);
    return G.tabela(pai, { legenda: { n, t: T('c7.tab.titulo') }, ordenavel: false,
      grafico: comGrafico && { legenda: [{ t: T('c7.fig1.rot_proj'), lado: 'ink' }, { t: T('c7.fig1.rot_parc'), lado: 'muted' }], sub: T('vd.c7.sub'),
        desenhar: caixa => G.linhasPontos(caixa, { aria: T('vd.aria', { t: T('c7.tab.titulo') }), margE: 110, margEstreito: 70, altLinha: 20,
          x: eixo(vals, tickPp, T('vd.c7.eixo')),
          linhas: fx.map(f => ({ nome: nomeFx(f), vals: [{ v: f.parcial.erro_medio, lado: 'muted' }, { v: f.projecao.erro_medio, lado: 'ink' }],
            dica: { titulo: nomeFx(f), linhas: [{ lado: 'ink', t: T('c7.fig1.rot_proj'), v: fmt.decSinal(f.projecao.erro_medio, 3) },
              { lado: 'muted', t: T('c7.fig1.rot_parc'), v: fmt.decSinal(f.parcial.erro_medio, 3) }, { t: T('c7.tab.leituras'), v: String(f.leituras) }] } })) }) },
      linhas: fx.concat([{ faixa: 'todas', leituras: PR.leituras, projecao: { erro_medio: PR.geral.projecao_erro_medio, erro_abs_medio: PR.geral.projecao_erro_abs_medio },
        parcial: { erro_medio: PR.geral.parcial_erro_medio, erro_abs_medio: PR.geral.parcial_erro_abs_medio } }]),
      destaque: f => f.faixa === 'todas',
      colunas: [{ t: T('c7.tab.apurado'), v: f => (f.faixa === 'todas' ? T('c7.tab.todas') : T('c7.tab.faixa', { a: f.faixa.split(' a ')[0], b: f.faixa.split(' a ')[1] })) },
        { t: T('c7.tab.leituras'), num: true, v: f => f.leituras },
        { t: T('c7.tab.proj_medio'), num: true, v: f => f.projecao.erro_medio, f: v => fmt.decSinal(v, 3) },
        { t: T('c7.tab.abs_medio'), num: true, v: f => f.projecao.erro_abs_medio, f: v => fmt.dec(v, 3) },
        { t: T('c7.tab.parc_medio'), num: true, v: f => f.parcial.erro_medio, f: v => fmt.decSinal(v, 3) },
        { t: T('c7.tab.abs_medio'), num: true, v: f => f.parcial.erro_abs_medio, f: v => fmt.dec(v, 3) }] });
  }

  // ---------- Capítulo 8 (T34): como eram os lugares onde cada um cresceu ----------
  // Os 35 testes registrados na seção 6 do HIPOTESES.md: 7 características × 5 medidas, uma característica por
  // vez, comparando municípios do mesmo estado, com a correção de Holm. O número mostrado é a diferença entre um
  // município no quarto de cima e um no de baixo da característica (efeito entre quartis), com o intervalo do
  // bootstrap selvagem; o ponto cheio marca associação depois da correção. Sempre "municípios com…".
  const SOC = D.sociais;
  const socTeste = (k, d) => SOC.testes.find(t => t.var === k && t.desfecho === d);
  const socIq = (t, ver = 'principal') => ({ v: t[ver].efeito_interquartil_pp, ic: t[ver].ic95.map(x => x * t.larg_quartis) });
  const socResultado = v => (v.associacao ? T(v.pequena ? 'soc.res.assoc_peq' : 'soc.res.assoc', { dir: T('soc.dir.' + v.direcao) }) : T('soc.res.sem'));
  const socDica = (t, lado) => ({ t: T('soc.dica.' + t.desfecho), v: fmt.decSinal(t.principal.efeito_interquartil_pp, 2), lado });
  function socLinhas(desfechos, lados) {
    return SOC_VARS.map(k => {
      const ts = desfechos.map(d => socTeste(k, d));
      return { nome: T('soc.var.' + k), curto: T('soc.var.' + k + '.curto'),
        vals: ts.map((t, i) => Object.assign(socIq(t), { lado: lados[i], cheio: t.principal.associacao })),
        dica: { titulo: T('soc.var.' + k + '.nome'), linhas: ts.flatMap((t, i) => [socDica(t, lados[i] === 'ink' ? undefined : lados[i]),
          { t: T('tab.ic95'), v: icTxt(t.principal.ic95, t.larg_quartis) }, { t: T('soc.tab.p_holm'), v: fmt.p(t.principal.p_holm) },
          { t: T('tab.resultado'), v: socResultado(t.principal) }]) } };
    });
  }
  function socForest(caixa, desfechos, lados, eixo, ladosTxt) {
    const ls = socLinhas(desfechos, lados);
    const lim = Math.max(...ls.flatMap(l => l.vals.flatMap(v => v.ic.map(Math.abs))));
    const passo = PASSOS_SOC.find(p => lim / p <= 4) || 10;
    const max = Math.ceil(lim / passo) * passo;
    return G.coeficientesPar(caixa, { aria: T('soc.aria', { eixo }), linhas: ls, lados: ladosTxt, margE: 190, margEstreito: 92,
      x: { min: -max, max, passo, fmt: v => fmt.decSinal(v, passo < 0.5 ? 2 : passo < 1 ? 1 : 0), rotulo: eixo } });
  }
  const PASSOS_SOC = [0.25, 0.5, 1, 2, 2.5, 5];
  // o nome curto no meio da frase: inicial minúscula, menos nas siglas (PIB)
  // no meio da frase, em minúscula; fica a maiúscula de sigla e a que a língua mantém no meio da frase
  // (o "Black" do inglês), vista na frase ".mais" do próprio catálogo
  const socMinusc = k => {
    const t = T('soc.var.' + k), p = t.split(' ')[0];
    return /^\p{Lu}{2}/u.test(t) || T('soc.var.' + k + '.mais').includes(' ' + p + ' ') ? t : t.charAt(0).toLowerCase() + t.slice(1);
  };
  const legSoc = duas => (duas ? [{ t: T('nome.lula'), lado: 'l' }, { t: T('nome.flavio'), lado: 'f' }] : [])
    .concat([{ t: T('soc.leg.cheio') }, { t: T('soc.leg.vazio'), tipo: 'vazio' }]);
  function cap8(ctx) {
    const assoc = SOC.testes.filter(t => t.principal.associacao), peq = assoc.filter(t => t.principal.pequena).length;
    const capRen = socTeste('ren', 'cap').principal;
    // a chamada responde "quem ficou com mais": a parte de cada um nos votos a mais (pagina_dados.py confere o que ela diz)
    cabecalho(ctx, ...T.f('c8.resposta', { cap: N(T.p('un.pontos', capRen.efeito_interquartil_pp, { n: fmt.abs(capRen.efeito_interquartil_pp, 1) })) }));
    // a caixa no topo, como a das hipóteses: o que foi registrado antes e o resultado, com o botão que abre o detalhe
    const hp = el('div', 'hipotese', undefined, ctx.cab);
    const ht = el('p', 'hip-texto', undefined, hp);
    el('span', 'hip-cab', T('c8.registro.cab'), ht); ht.append(T('c8.registro.texto'));
    const r = el('p', 'hip-res', undefined, hp);
    r.append(...T.f('c8.registro.res', { n: B(String(assoc.length)), total: SOC.testes.length }));
    const bt = el('button', 'bt-link', T('hip.como_chegou'), r);
    bt.type = 'button';
    bt.addEventListener('click', () => abrirDetalhes(ctx.detalhes));
    const { fig, lado } = corpo(ctx);
    // uma lista nova para cada figura: os trechos montados (negrito, links) são nós e não podem estar em dois lugares
    const como = () => [T.f('c8.fig.como1'), T.f('c8.fig.como2', { p: P05 }), T('c8.fig.como3'), dadosComo(['testes_sociais', 'dados_sociais'], [6])];
    const fonte = T('c8.fig.fonte');
    // 8.1: quem ficou com mais dos votos a mais (a captura); 8.2, em abas: os votos de cada um, a fatia e a abstenção
    const n1 = ctx.nf();
    figura(fig, {
      n: n1, titulo: T('c8.fig1.titulo'), sub: T('c8.fig1.sub', { n: fmt.int(SOC.captura_amostra) }), leitura: T('c8.fig1.leitura'),
      legenda: legSoc(false), como: como(), fonte, notas: ['N09', 'N19', 'N20'],
      desenhar: caixa => socForest(caixa, ['cap'], ['ink'], T('c8.fig1.eixo'), [T('c8.fig1.esq'), T('c8.fig1.dir')]),
    });
    const n2 = ctx.nf();
    const aba = (d, desfechos, lados, extra) => ({ rotulo: T('c8.aba.' + d), montar: p => figura(p, {
      n: n2, titulo: T('c8.fig2.titulo_' + d), sub: T('c8.fig2.sub_' + d), leitura: T('c8.fig2.leitura_' + d, { f1: n1 }),
      legenda: legSoc(lados.length > 1), como: como(), fonte, notas: ['N19', 'N20'].concat(extra || []),
      desenhar: caixa => socForest(caixa, desfechos, lados, T('c8.fig2.eixo_' + d), [T('c8.fig2.esq_' + d), T('c8.fig2.dir_' + d)]) }) });
    figurasComAbas(fig, [aba('votos', ['gL', 'gF'], ['l', 'f']), aba('ds', ['ds'], ['ink']), aba('da', ['da'], ['ink'], ['N05'])], 'cap8');
    notaLateral(lado, T('c8.lado.tit'), T('c8.lado.1'), T('c8.lado.2'));

    const det = detalhes(ctx);
    const s = el('section', 'como-chegou', undefined, det);
    el('h3', '', T('hip.como_chegou'), s);
    P(s, '', ...T.f('c8.chegou.registro', { lista: listaE(SOC_VARS.map(socMinusc)) }));
    P(s, '', ...T.f('c8.chegou.teste', { ncap: fmt.int(SOC.captura_amostra), mun: fmt.int(SOC.municipios), n14: nd('N14'), n09: nd('N09'), n20: nd('N20') }));
    P(s, '', ...T.f('c8.chegou.holm', { p: P05 }));
    const nb = SOC.testes.filter(t => t.brasil.associacao).length;
    const disc = SOC.testes.filter(t => t.brasil.associacao !== t.principal.associacao
      || (t.brasil.associacao && t.brasil.direcao !== t.principal.direcao)).length;
    P(s, '', ...T.f('c8.chegou.resultado', { n: assoc.length, peq, lim: nf(0.5, 1), nb, disc }));
    const DESF = [...new Set(SOC.testes.map(t => t.desfecho))];
    // uma escala por medida (pequenos múltiplos): a parte do Lula nos votos a mais varia dez vezes mais que as outras
    G.tabela(s, { legenda: { n: ctx.nt(), t: T('c8.tab.titulo') }, ordenavel: true,
      grafico: { legenda: legSoc(false).concat([{ t: T('leg.ic95'), tipo: 'ic' }]), sub: T('vd.c8.sub'),
        desenhar: caixa => { caixa.replaceChildren(); DESF.forEach(d => {
          el('p', 'vd-multiplo', T('soc.desf.' + d), caixa);
          G.coeficientesPar(el('div', '', undefined, caixa), { aria: T('vd.aria', { t: T('c8.tab.titulo') + ' — ' + T('soc.desf.' + d) }), margE: 200, margEstreito: 96, altLinha: 20, topo: 12,
          x: eixo(SOC.testes.filter(t => t.desfecho === d).flatMap(t => socIq(t).ic), tickPp, T('vd.c8.eixo')),
          linhas: SOC_VARS.map(k => {
            const t = socTeste(k, d), q = socIq(t);
            return { nome: T('soc.var.' + k), curto: T('soc.var.' + k + '.curto'), vals: [{ lado: 'ink', v: q.v, ic: q.ic, cheio: t.principal.associacao }],
              dica: { titulo: T('vd.c8.dica', { var: T('soc.var.' + k), medida: T('soc.desf.' + d) }), linhas: [
                { t: T('tab.entre_quartis'), v: fmt.decSinal(q.v, 2) }, { t: T('tab.ic95'), v: icTxt(t.principal.ic95, t.larg_quartis) },
                { t: T('soc.tab.p_holm'), v: fmt.p(t.principal.p_holm) }, { t: T('tab.resultado'), v: socResultado(t.principal) }] } };
          }) }); }); } },
      linhas: SOC.testes, destaque: t => t.principal.associacao,
      colunas: [
        { t: T('soc.tab.caracteristica'), v: t => T('soc.var.' + t.var) },
        { t: T('soc.tab.medida'), v: t => T('soc.desf.' + t.desfecho) },
        { t: T('tab.entre_quartis'), num: true, v: t => t.principal.efeito_interquartil_pp, f: v => fmt.decSinal(v, 2) },
        { t: T('tab.ic95'), num: true, v: t => t.principal.ic95[0] * t.larg_quartis, f: (_, t) => icTxt(t.principal.ic95, t.larg_quartis) },
        { t: T('tab.p_selvagem'), num: true, v: t => t.principal.p_selvagem, f: fmt.p },
        { t: T('soc.tab.p_holm'), num: true, v: t => t.principal.p_holm, f: fmt.p },
        { t: T('tab.resultado'), v: t => socResultado(t.principal) },
        { t: T('soc.tab.brasil'), v: t => socResultado(t.brasil) },
      ] });
    P(s, 'nota-tab', T('c8.tab.nota'));

    const tx = secao(det, T('cap.resultado_texto'));
    P(tx, '', T('c8.texto.intro', { n: assoc.length }));
    const ul = el('ul', 'lista-texto', undefined, tx);
    for (const t of assoc) { // um item por teste, na ordem das características
      const v = t.principal.efeito_interquartil_pp;
      el('li', '', T('c8.texto.item', { onde: T('soc.var.' + t.var + '.mais'),
        efeito: T('c8.efeito.' + t.desfecho + '.' + t.principal.direcao, { iq: fmt.abs(v, 2), pts: pontos(Math.abs(v)) }),
        peq: t.principal.pequena ? T('c8.efeito.pequena') : '' }), ul);
    }
    const sem = SOC_VARS.filter(k => !assoc.some(t => t.var === k));
    if (sem.length) P(tx, '', T('c8.texto.sem', { lista: listaE(sem.map(socMinusc)) }));
    P(tx, '', T('c8.texto.resto', { m: SOC.testes.length - assoc.length }));
    // como as características andam juntas: a correlação entre elas nos municípios (sem a eleição)
    const jt = secao(det, T('c8.juntas.secao'));
    P(jt, '', T('c8.juntas.texto', { mun: fmt.int(SOC.municipios) }));
    const R8 = SOC.correlacoes;
    G.tabela(jt, { legenda: { n: ctx.nt(), t: T('c8.juntas.tab') }, ordenavel: false, linhas: SOC_VARS,
      grafico: { sub: T('vd.c8.calor_sub'), desenhar: caixa => G.calor(caixa, { aria: T('vd.aria', { t: T('c8.juntas.tab') }),
        linhas: SOC_VARS.map(k => ({ nome: T('soc.var.' + k), curto: T('soc.var.' + k + '.curto') })),
        colunas: SOC_VARS.map(k => ({ nome: T('soc.var.' + k + '.curto'), curto: T('soc.var.' + k + '.curto').slice(0, 4) })),
        cel: (i, j) => (i === j ? null : { t: Math.abs(R8[i][j]), rotulo: fmt.decSinal(R8[i][j], 2),
          dica: { titulo: T('vd.c8.par', { a: T('soc.var.' + SOC_VARS[i]), b: T('soc.var.' + SOC_VARS[j]) }), linhas: [{ t: T('vd.c8.correlacao'), v: fmt.decSinal(R8[i][j], 2) }] } }) }) },
      colunas: [{ t: T('soc.tab.caracteristica'), v: k => T('soc.var.' + k) }].concat(SOC_VARS.map((k2, j) => ({
        t: T('soc.var.' + k2 + '.curto'), num: true, v: k => SOC.correlacoes[SOC_VARS.indexOf(k)][j], f: v => fmt.decSinal(v, 2) }))) });

    const dd = secao(det, T('c8.dados.secao'));
    const ulD = el('ul', 'lista-texto', undefined, dd);
    for (const k of SOC_VARS) {
      const li = el('li', '', undefined, ulD);
      li.append(T('c8.dados.item', { nome: T('soc.var.' + k + '.nome'), fonte: SOC.variaveis[k].fonte, ano: SOC.variaveis[k].ano }));
    }
    P(dd, '', ...T.f('c8.dados.notas', { n19: nd('N19'), n20: nd('N20') }));
  }

  // ---------- Capítulo 9 (T33): a exploração guiada ----------
  // As cinco perguntas feitas depois de ver os resultados (HIPOTESES.md, seção 8, rodada 1), todas com o resultado,
  // tenha dado achado ou não, e sempre com o rótulo "exploratório, não registrado antes das contas". A caixa do topo
  // tem o fio tracejado: o mesmo lugar da caixa das hipóteses, marcado como o que não foi registrado antes.
  const EXP = D.exploracao;
  const CANDS_E1 = ['70', '14', '55', 'resto'];
  const pctE = v => fmt.pct(v * 100, 0);
  const pctIcE = (v, ic) => T('dica.pct_ic', { v: fmt.pct(v * 100, 1), a: nf(ic[0] * 100, 1), b: nf(ic[1] * 100, 1) });
  const leituraE1 = d => (d.passa ? T('c9.e1.lado.' + ({ Lula: 'l', 'Flávio': 'f' }[d.maior_parte] || 'sem')) : T('c9.e1.nao_deu', { motivo: d.motivo }));
  /** As versões das perguntas 4 e 5 (a cada 10 pontos, com o intervalo de 95%), como pontos com intervalo (T36). */
  const graficoB10 = (versoes, titulo, rotulo) => ({ legenda: [{ t: T('leg.ic95'), tipo: 'ic' }],
    desenhar: caixa => G.coeficientes(caixa, { aria: T('vd.aria', { t: titulo }), margE: 230, margEstreito: 116, altLinha: 22,
      x: eixo(versoes.flatMap(([, x]) => x.ic95_por_10), tickPp, rotulo),
      linhas: versoes.map(([k, x], i) => ({ nome: T(k), v: x.b_por_10, ic: x.ic95_por_10, destaque: i === 0,
        dica: { titulo: T(k), linhas: [{ t: T('c9.tab4.b'), v: fmt.pp(x.b_por_10, 2) },
          { t: T('tab.ic95'), v: T('g.de_a', { a: fmt.decSinal(x.ic95_por_10[0], 2), b: fmt.decSinal(x.ic95_por_10[1], 2) }) }] } })) }) });
  // Rodada 2 (T37): quem votou e quem faltou, por idade (perfil de comparecimento do TSE, só o 1º turno) e as seções
  // com mais inscritos de 60 anos ou mais (perfil do eleitorado por seção). As perguntas seguem a numeração: 6 a 10.
  const ID = D.idade;
  const taxaId = ([a, c]) => 100 * c / a;
  const pctId = (v, c = 1) => fmt.pct(v, c);
  const nomeFaixa = (fx, curto) => {
    fx = +fx;
    if (fx === 9999) return T(curto ? 'c9.faixa.100.curto' : 'c9.faixa.100');
    const a = Math.floor(fx / 100), b = fx % 100;
    return b === 0 ? (curto ? String(a) : T('c9.faixa.um', { a })) : (curto ? T('g.de_a', { a, b }) : T('c9.faixa.de_a', { a, b }));
  };
  const nomeLugarId = lg => (lg === 'Brasil' ? BR.nome : lg === 'Exterior' ? T('ficha.exterior') : NOME_UF[lg] || TD(lg));
  const GRUPOS_ID = ['g1617', 'g1859', 'g6069', 'g70', 'g60', 'total']; // os nomes vêm do catálogo (c9.grupo.*)
  const REG_ID = ['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul'];
  const F70_ID = ['7074', '7579', '8084', '8589', '9094', '9599', '9999'];
  function cap9(ctx) {
    const br1 = EXP.E1.por_lugar[0].fontes, E2 = EXP.E2, E3 = EXP.E3.desfechos.var_abstencao_pp;
    const E4br = EXP.E4.principal[0], E5 = EXP.E5;
    const GB = ID.grupos.Brasil;
    cabecalho(ctx, ...T.f('c9.resposta', { fl: N(fmt.int(E2.casas.fl)), lf: N(fmt.int(E2.casas.lf)), p70: N(pctId(taxaId(GB['g70']))) }));
    // a caixa do rótulo, no lugar da caixa da hipótese
    const hp = el('div', 'hipotese exploratoria', undefined, ctx.cab);
    const ht = el('p', 'hip-texto', undefined, hp);
    el('span', 'hip-cab', T('c9.rotulo.cab'), ht); ht.append(T('c9.rotulo.texto'));
    // a pergunta 2 é contagem: o achado conta só nas quatro com estimativa
    // a pergunta 5 fica como "sem resposta firme" (D62), fora da conta dos achados
    const achados = [Object.keys(EXP.E1.achado_brasil).length > 0, Object.values(EXP.E3.desfechos).some(d => d.achado), EXP.E4.achado];
    const r = el('p', 'hip-res', undefined, hp);
    const S5 = ID.secoes, achado2 = S5.abstencao.achado || S5.fatia_lula.achado;
    r.append(...T.f('c9.rotulo.res', { n: B(String(achados.filter(Boolean).length)), s: B('1'), r2: B(T(achado2 ? 'c9.r2.res.achado' : 'c9.r2.res.sem')) }));
    const bt = el('button', 'bt-link', T('hip.como_chegou'), r);
    bt.type = 'button';
    bt.addEventListener('click', () => abrirDetalhes(ctx.detalhes));

    // as cinco perguntas, na ordem do registro, cada uma com a resposta curta
    const n1 = ctx.nf(), n2 = ctx.nf(), n3 = ctx.nf(), n4 = ctx.nf(), n5 = ctx.nf(), n6 = ctx.nf();
    P(ctx.cab, '', B(T('c9.rodada1')));
    const lista = el('ol', 'lista-exploracao', undefined, ctx.cab);
    const item = (k, ...partes) => { const li = el('li', '', undefined, lista); P(li, '', B(T('c9.' + k + '.p')), ' ', ...partes); };
    const fresto = br1.resto.flavio, f55 = br1['55'].flavio;
    item('e1', ...T.f('c9.e1.r', { l70: pctE(br1['70'].lula), f55: pctE(f55), fresto: pctE(fresto), fig: n1 }));
    item('e2', ...T.f('c9.e2.r', { fl: fmt.int(E2.casas.fl), el: fmt.miAbs(E2.eleitores.fl, 1), lf: fmt.int(E2.casas.lf),
      ellf: fmt.int(E2.eleitores.lf), sub: fmt.int(E2.fatia.subiu), caiu: fmt.int(E2.fatia.caiu), tot: fmt.int(5571), fig: n2 }));
    const ptsS = v => T.p('un.pontos', v, { n: fmt.decSinal(v, 1) });
    item('e3', ...T.f('c9.e3.r', { a1: ptsS(E3.medias_pp.com_2t), a2: ptsS(E3.medias_pp.sem_2t), p: fmt.pct(E3.principal.p_permutacao * 100, 0) }));
    item('e4', ...T.f('c9.e4.r', { iq: pontos(Math.abs(E4br.efeito_interquartil_pp), 2), fig: n3 }));
    item('e5', ...T.f('c9.e5.r'));
    // 2ª rodada (T37), na mesma lista numerada, a partir do 6
    P(ctx.cab, '', B(T('c9.rodada2')));
    const lista2 = el('ol', 'lista-exploracao', undefined, ctx.cab);
    lista2.start = 6;
    const item2 = (k, ...partes) => { const li = el('li', '', undefined, lista2); P(li, '', B(T('c9.' + k + '.p')), ' ', ...partes); };
    const ufs70 = Object.keys(ID.grupos).filter(u => NOME_UF[u] && taxaId(ID.grupos[u]['g70']) < 50)
      .sort((a, b) => taxaId(ID.grupos[a]['g70']) - taxaId(ID.grupos[b]['g70']));
    item2('i1', ...T.f('c9.i1.r', { n70: fmt.miAbs(GB['g70'][0], 1), p70: pctId(taxaId(GB['g70'])), p6069: pctId(taxaId(GB['g6069'])),
      p1859: pctId(taxaId(GB['g1859'])), nuf: fmt.int(ufs70.length), ufs: listaE(ufs70.map(u => NOME_UF[u])), fig: n4 }));
    const FB = ID.faixas.Brasil;
    item2('i2', ...T.f('c9.i2.r', { p7074: pctId(taxaId(FB['7074'])), p7579: pctId(taxaId(FB['7579'])), p8084: pctId(taxaId(FB['8084'])), fig: n4 }));
    const AB = ID.abstencao.Brasil['g70'];
    item2('i3', ...T.f('c9.i3.r', { pa: pctId(AB.parte_dos_aptos), pb: pctId(AB.parte_da_abstencao),
      ka: fmt.int(Math.round(100 / AB.parte_dos_aptos)), kb: fmt.int(Math.round(100 / AB.parte_da_abstencao)) }));
    const GN = ID.genero.Brasil, tg = (g, k) => pctId(taxaId(GN[g][k]));
    item2('i4', ...T.f('c9.i4.r', { m6069: tg('mulheres', 'g6069'), h6069: tg('homens', 'g6069'), m70: tg('mulheres', 'g70'),
      h70: tg('homens', 'g70'), m1859: tg('mulheres', 'g1859'), h1859: tg('homens', 'g1859'), fig: n5 }));
    const iqa = pontos(Math.abs(S5.abstencao.principal[0].efeito_interquartil_pp), 2), iqs = pontos(Math.abs(S5.fatia_lula.principal[0].efeito_interquartil_pp), 2);
    item2('i5', ...T.f('c9.i5.r', { iqa, iqs, fig: n6 }));

    const { fig, lado } = corpo(ctx);
    // 9.1 (E1): a divisão de cada fonte no Brasil, pela conta por seção com os outros candidatos separados
    const linhaE1 = (c, nome, curto) => {
      const d = br1[c];
      return { nome, curto, lula: d.lula, ic: d.lula_ic95, naoDeu: d.passa ? null : d.motivo,
        dica: { titulo: nome, linhas: [{ lado: 'l', t: T('nome.lula'), v: pctIcE(d.lula, d.lula_ic95) }, { lado: 'f', t: T('nome.flavio'), v: pctIcE(d.flavio, d.flavio_ic95) },
          { t: T('dica.tamanho_fonte'), v: T('dica.n_votos', { n: fmt.int(Math.abs(EXP.E1.votos[c])) }) },
          { t: T('c9.dica.leitura'), v: leituraE1(d) }, { t: T('c9.dica.mantem'), v: T('c9.dica.mantem_v', { n: d.mantem, total: EXP.E1.n_conferencias }) }] } };
    };
    figura(fig, {
      n: n1, titulo: T('c9.fig1.titulo'), sub: T('c9.fig1.sub'), leitura: [T('c9.rotulo.curto'), T('c9.fig1.leitura')],
      legenda: [{ t: T('leg.ic95'), tipo: 'ic' }, { t: T('leg.cruza50'), tipo: 'barra', lado: 'dentro' }],
      desenhar: caixa => G.divisao(caixa, { aria: T('c9.fig1.aria'), rotuloX: T('c9.fig1.eixo'), margE: 230, margEstreito: 112, linhas: [
        { grupo: T('c9.fig1.grupo_cand') },
        linhaE1('70', T('c9.cand.70'), T('c9.cand.70.curto')), linhaE1('14', T('c9.cand.14'), T('c9.cand.14.curto')),
        linhaE1('55', T('c9.cand.55'), T('c9.cand.55.curto')), linhaE1('resto', T('c9.cand.resto'), T('c9.cand.resto.curto')),
        { grupo: T('c9.fig1.grupo_fontes') },
        linhaE1('C', T('fonte.C'), T('fonte.C.curto')), linhaE1('R', T('fonte.R'), T('fonte.R.curto'))] }),
      fonte: T('c9.fig1.fonte', { sec: fmt.int(EXP.secoes) }),
      como: [T.f('c9.fig1.como1'), T('c9.fig1.como2', { n: fmt.int(1000) }), T('c9.fig1.como3'), T('c9.como.script')],
      notas: ['N21', 'N22', 'N23'],
    });
    // 9.2 (E2): onde o Lula passou o Flávio, por estado (contagem)
    const ufsTroca = Object.entries(E2.por_uf).filter(([, v]) => v[0] > 0).sort((a, b) => b[1][0] - a[1][0] || a[0].localeCompare(b[0]));
    const ufLF = Object.entries(E2.por_uf).filter(([, v]) => v[1] > 0).map(([u]) => u);
    const maiorUf = ufsTroca[0];
    figura(fig, {
      n: n2, titulo: T('c9.fig2.titulo', { fl: fmt.int(E2.casas.fl), nuf: fmt.int(maiorUf[1][0]), uf: NOME_UF[maiorUf[0]], lf: fmt.int(E2.casas.lf),
        ufslf: listaE(ufLF.map(u => NOME_UF[u])) }),
      sub: T('c9.fig2.sub', { n: ufsTroca.length }), leitura: [T('c9.rotulo.curto'), T('c9.fig2.leitura', { lf: fmt.int(E2.casas.lf), ufs: listaE(ufLF.map(u => NOME_UF[u])) })],
      desenhar: caixa => G.barras(caixa, { aria: T('c9.fig2.aria'), margE: 150, margEstreito: 40, margD: 40,
        x: { min: 0, max: Math.ceil(maiorUf[1][0] / 20) * 20, passo: 20, fmt: v => fmt.int(v), rotulo: T('c9.fig2.eixo') },
        linhas: ufsTroca.map(([u, v]) => ({ nome: NOME_UF[u], curto: u, v: v[0], rotulo: fmt.int(v[0]),
          dica: { titulo: NOME_UF[u], linhas: [{ t: T('c9.fig2.dica.fl'), v: fmt.int(v[0]) }, { t: T('c9.fig2.dica.lf'), v: fmt.int(v[1]) },
            { t: T('c9.fig2.dica.mun'), v: fmt.int(v[2]) }] } })) }),
      fonte: T('fig.fonte_padrao'),
      como: [T('c9.fig2.como1', { mun: fmt.int(5571) }), T('c9.fig2.como2', { todos: fmt.int(EXP.E2.vencedor_todos.outro) }), T('c9.como.script')],
      notas: ['N06'],
    });
    // 9.3 (E4): a abstenção contra a força de cada um, seções da mesma cidade, no Brasil e nas regiões
    const linhasE4 = EXP.E4.principal.filter(x => x.nivel !== 'uf').map(x => ({ nome: x.lugar === 'Brasil' ? BR.nome : x.lugar, v: x.b_por_10, ic: x.ic95_por_10, destaque: x.nivel === 'brasil',
      dica: { titulo: x.lugar === 'Brasil' ? BR.nome : x.lugar, linhas: [{ t: T('c9.fig3.dica.b'), v: fmt.pp(x.b_por_10, 2) }, { t: T('tab.ic95'), v: T('g.de_a', { a: fmt.decSinal(x.ic95_por_10[0], 2), b: fmt.decSinal(x.ic95_por_10[1], 2) }) },
        { t: T('c9.fig3.dica.iq'), v: fmt.pp(x.efeito_interquartil_pp, 2) }, { t: T('c9.fig3.dica.secoes'), v: fmt.int(x.secoes) }] } }));
    figura(fig, {
      n: n3, titulo: T('c9.fig3.titulo'), sub: T('c9.fig3.sub'), leitura: [T('c9.rotulo.curto'), T('c9.fig3.leitura')],
      legenda: [{ t: T('leg.ic95'), tipo: 'ic' }],
      desenhar: caixa => G.coeficientes(caixa, { aria: T('c9.fig3.aria'), margE: 130, margEstreito: 92, linhas: linhasE4,
        lados: [T('c9.fig3.esq'), T('c9.fig3.dir')],
        x: { min: -0.8, max: 0.4, passo: 0.2, fmt: v => fmt.decSinal(v, 1), rotulo: T('c9.fig3.eixo') } }),
      fonte: T('c9.fig1.fonte', { sec: fmt.int(EXP.secoes) }),
      como: [T('c9.fig3.como1'), T('c9.fig3.como2', { n: fmt.int(1000) }), T('c9.como.script')],
      notas: ['N05', 'N22', 'N23'],
    });
    // 9.4 (perguntas 6 e 7): quem foi votar, por idade, no Brasil (contagem); a linha marca a metade
    const faixasB = Object.keys(FB).filter(fx => +fx > 0).sort((a, b) => a - b);
    figura(fig, {
      n: n4, titulo: T('c9.fig4.titulo'), sub: T('c9.fig4.sub'), leitura: [T('c9.rotulo.curto'), T('c9.fig4.leitura')],
      desenhar: caixa => G.barras(caixa, { aria: T('c9.fig4.aria'), margE: 130, margEstreito: 56, margD: 48, altLinha: 18,
        x: { min: 0, max: 100, passo: 25, fmt: v => fmt.int(v), rotulo: T('c9.fig4.eixo') }, ref: { v: 50, rotulo: T('c9.fig4.ref') },
        linhas: faixasB.map(fx => ({ nome: nomeFaixa(fx), curto: nomeFaixa(fx, true), v: taxaId(FB[fx]), rotulo: pctId(taxaId(FB[fx])),
          dica: { titulo: nomeFaixa(fx), linhas: [{ t: T('c9.fig4.dica.taxa'), v: pctId(taxaId(FB[fx])) }, { t: T('c9.fig4.dica.aptos'), v: fmt.int(FB[fx][0]) },
            { t: T('c9.fig4.dica.comp'), v: fmt.int(FB[fx][1]) }] } })) }),
      fonte: T('c9.fig4.fonte'),
      como: [T('c9.fig4.como1'), T('c9.fig4.como2'), T('c9.r2.script')],
      notas: ['N24'],
    });
    // 9.5 (pergunta 9): mulheres e homens, por idade (contagem), com as séries neutras
    const GRUPO_FX = { g1859: 1859, g6069: 6069 }; // os grupos entram como faixas largas
    const linhasGen = ['g1859', 'g6069'].concat(F70_ID.slice(0, -1)).map(k => {
      const nome = nomeFaixa(GRUPO_FX[k] || k), curto = nomeFaixa(GRUPO_FX[k] || k, true);
      const m = taxaId(GN.mulheres[k]), h = taxaId(GN.homens[k]);
      return { nome, curto, vals: [{ v: m, lado: 'ink' }, { v: h, lado: 'muted' }],
        dica: { titulo: nome, linhas: [{ lado: 'ink', t: T('c9.gen.mulheres'), v: pctId(m) }, { lado: 'muted', t: T('c9.gen.homens'), v: pctId(h) }] } };
    });
    figura(fig, {
      n: n5, titulo: T('c9.fig5.titulo'), sub: T('c9.fig5.sub'), leitura: [T('c9.rotulo.curto'), T('c9.fig5.leitura')],
      legenda: [{ t: T('c9.gen.mulheres'), lado: 'ink' }, { t: T('c9.gen.homens'), lado: 'muted' }],
      desenhar: caixa => G.linhasPontos(caixa, { aria: T('c9.fig5.aria'), margE: 130, margEstreito: 56, altLinha: 20,
        series: { ink: T('c9.gen.mulheres'), muted: T('c9.gen.homens') },
        x: { min: 0, max: 100, passo: 25, fmt: v => fmt.int(v), rotulo: T('c9.fig4.eixo') }, linhas: linhasGen }),
      fonte: T('c9.fig4.fonte'),
      como: [T('c9.fig4.como1'), T('c9.r2.script')],
      notas: ['N24'],
    });
    // 9.6 (pergunta 10): seções com mais inscritos de 60 anos ou mais, seções da mesma cidade, nas duas medidas
    const icId = x => T('g.de_a', { a: fmt.decSinal(x.ic975_por_10[0], 2), b: fmt.decSinal(x.ic975_por_10[1], 2) });
    const linhaSec = (x, desf) => { const nome = nomeLugarId(x.lugar);
      return { nome, v: x.b_por_10, ic: x.ic975_por_10, destaque: x.lugar === 'Brasil',
        dica: { titulo: `${nome}: ${T(desf)}`, linhas: [{ t: T('c9.fig3.dica.b'), v: fmt.pp(x.b_por_10, 2) }, { t: T('tab.ic975'), v: icId(x) },
          { t: T('c9.fig3.dica.iq'), v: fmt.pp(x.efeito_interquartil_pp, 2) }, { t: T('c9.fig3.dica.secoes'), v: fmt.int(x.secoes) }] } }; };
    figura(fig, {
      n: n6, titulo: T('c9.fig6.titulo'), sub: T('c9.fig6.sub'), leitura: [T('c9.rotulo.curto'), T('c9.fig6.leitura')],
      legenda: [{ t: T('leg.ic975'), tipo: 'ic' }],
      desenhar: caixa => G.coeficientes(caixa, { aria: T('c9.fig6.aria'), margE: 130, margEstreito: 92,
        linhas: [{ grupo: T('c9.fig6.grupo_a') }].concat(S5.abstencao.principal.map(x => linhaSec(x, 'c9.fig6.grupo_a')),
          [{ grupo: T('c9.fig6.grupo_s') }], S5.fatia_lula.principal.map(x => linhaSec(x, 'c9.fig6.grupo_s'))),
        x: { min: -1.2, max: 0.2, passo: 0.2, fmt: v => fmt.decSinal(v, 1), rotulo: T('c9.fig6.eixo') } }),
      fonte: T('c9.fig6.fonte', { sec: fmt.int(ID.secoes_desc.secoes_com_perfil) }),
      como: [T('c9.fig6.como1'), T('c9.fig6.como2', { n: fmt.int(1000) }), T('c9.r2.script')],
      notas: ['N22', 'N24'],
    });
    notaLateral(lado, T('c9.lado.tit'), T('c9.lado.1'), T('c9.lado.2'));

    // ---------- Ver detalhes: o registro, cada pergunta com o teste e as conferências ----------
    const det = detalhes(ctx);
    const s = el('section', 'como-chegou', undefined, det);
    el('h3', '', T('hip.como_chegou'), s);
    P(s, '', ...T.f('c9.chegou.registro'));
    P(s, '', ...T.f('c9.chegou.regra'));
    // E1
    const s1 = secao(det, T('c9.e1.sec'));
    P(s1, '', ...T.f('c9.det.e1', { n: fmt.int(1000), fig: n1 }));
    const celE1 = d => (d.passa ? T('c9.tab.cel', { v: pctE(d.lula), ic: T('g.de_a', { a: nf(d.lula_ic95[0] * 100, 0), b: nf(d.lula_ic95[1] * 100, 0) }) }) : T('c9.tab.nao_deu'));
    const nomesE1 = c => T(c === 'C' || c === 'R' ? 'fonte.' + c : 'c9.cand.' + c), curtosE1 = c => T(c === 'C' || c === 'R' ? 'fonte.' + c + '.curto' : 'c9.cand.' + c + '.curto');
    G.tabela(s1, { legenda: { n: ctx.nt(), t: T('c9.tab1.titulo') }, ordenavel: false, linhas: EXP.E1.por_lugar, destaque: l => l.nivel === 'brasil',
      grafico: { legenda: [{ t: T('leg.ic95'), tipo: 'ic' }, { t: T('leg.cruza50'), tipo: 'barra', lado: 'dentro' }],
        desenhar: caixa => G.divisao(caixa, { aria: T('vd.aria', { t: T('c9.tab1.titulo') }), rotuloX: T('c9.fig1.eixo'), margE: 230, margEstreito: 112,
          linhas: EXP.E1.por_lugar.flatMap(l => { const lug = l.lugar === 'Brasil' ? BR.nome : l.lugar;
            return [{ grupo: lug }].concat(CANDS_E1.concat(['C', 'R']).map(c => { const d = l.fontes[c];
              return { nome: nomesE1(c), curto: curtosE1(c), lula: d.lula, ic: d.lula_ic95, naoDeu: d.passa ? null : d.motivo,
                dica: { titulo: T('vd.c3.versao_dica', { fonte: nomesE1(c), versao: lug }), linhas: d.passa
                  ? [{ lado: 'l', t: T('nome.lula'), v: pctIcE(d.lula, d.lula_ic95) }, { lado: 'f', t: T('nome.flavio'), v: pctIcE(d.flavio, d.flavio_ic95) }]
                  : [{ t: T('dica.nao_deu'), v: '' }, { t: T('dica.motivo'), v: d.motivo }] } }; })); }) }) },
      colunas: [{ t: T('tab.lugar'), v: l => (l.lugar === 'Brasil' ? BR.nome : l.lugar) }].concat(CANDS_E1.concat(['C', 'R']).map(c => ({
        t: T(c === 'C' || c === 'R' ? 'fonte.' + c + '.curto' : 'c9.cand.' + c + '.curto'), num: true, v: l => l.fontes[c].lula,
        f: (_, l) => celE1(l.fontes[c]) }))) });
    P(s1, 'nota-tab', T('c9.tab1.nota', { total: EXP.E1.n_conferencias }));
    // E2
    const s2 = secao(det, T('c9.e2.sec'));
    P(s2, '', ...T.f('c9.det.e2', { fl: fmt.int(E2.casas.fl), lf: fmt.int(E2.casas.lf), ll: fmt.int(E2.casas.ll),
      ff: fmt.int(E2.casas.ff), emp: fmt.int(E2.casas.emp),
      sub: fmt.int(E2.fatia.subiu), caiu: fmt.int(E2.fatia.caiu), secfl: fmt.int(E2.secoes.fl), seclf: fmt.int(E2.secoes.lf),
      sec: fmt.int(Object.values(E2.secoes).reduce((a, b) => a + b, 0)), extfl: fmt.int(E2.exterior.fl), extlf: fmt.int(E2.exterior.lf) }));
    const ufsE2 = Object.keys(E2.por_uf).sort((a, b) => E2.por_uf[b][0] - E2.por_uf[a][0] || E2.por_uf[b][1] - E2.por_uf[a][1] || a.localeCompare(b));
    G.tabela(s2, { legenda: { n: ctx.nt(), t: T('c9.tab2.titulo') }, ordenavel: true, linhas: Object.keys(E2.por_uf),
      // D80, pendência 1: as trocas nos dois sentidos, no mesmo gráfico
      grafico: { legenda: [{ t: T('c9.fig2.dica.fl'), lado: 'l' }, { t: T('c9.fig2.dica.lf'), lado: 'f' }], sub: T('vd.c9.e2_sub'),
        desenhar: caixa => G.linhasPontos(caixa, { aria: T('vd.aria', { t: T('c9.tab2.titulo') }), margE: 150, margEstreito: 34, altLinha: 16,
          x: eixo(ufsE2.flatMap(u => E2.por_uf[u].slice(0, 2)), v => fmt.int(v), T('vd.c9.e2_eixo')),
          linhas: ufsE2.map(u => ({ nome: NOME_UF[u], curto: u, vals: [{ v: E2.por_uf[u][1], lado: 'f' }, { v: E2.por_uf[u][0], lado: 'l' }],
            dica: { titulo: NOME_UF[u], linhas: [{ lado: 'l', t: T('c9.fig2.dica.fl'), v: fmt.int(E2.por_uf[u][0]) }, { lado: 'f', t: T('c9.fig2.dica.lf'), v: fmt.int(E2.por_uf[u][1]) },
              { t: T('c9.fig2.dica.mun'), v: fmt.int(E2.por_uf[u][2]) }] } })) }) },
      colunas: [{ t: T('tab.estado'), v: u => NOME_UF[u] }, { t: T('c9.tab2.mun'), num: true, v: u => E2.por_uf[u][2], f: fmt.int },
        { t: T('c9.tab2.fl'), num: true, v: u => E2.por_uf[u][0], f: fmt.int }, { t: T('c9.tab2.lf'), num: true, v: u => E2.por_uf[u][1], f: fmt.int }] });
    // E3
    const s3 = secao(det, T('c9.e3.sec'));
    const D3 = EXP.E3.desfechos, F3 = EXP.E3.funil_acima_998;
    P(s3, '', ...T.f('c9.det.e3', { ufs: listaE(EXP.E3.estados_2t_governador.map(u => NOME_UF[u])), perm: fmt.int(D3.var_abstencao_pp.principal.permutacoes), p: P05 }));
    const versoesE3 = [['principal', 'c9.tab3.principal'], ['sem_peso', 'c9.tab3.sem_peso'], ['sem_df', 'c9.tab3.sem_df'], ['efeito_de_regiao', 'c9.tab3.regiao']];
    G.tabela(s3, { legenda: { n: ctx.nt(), t: T('c9.tab3.titulo') }, ordenavel: false, linhas: versoesE3,
      grafico: { legenda: [{ t: T('c9.tab3.da'), lado: 'ink' }, { t: T('c9.tab3.ds'), lado: 'muted' }],
        desenhar: caixa => G.linhasPontos(caixa, { aria: T('vd.aria', { t: T('c9.tab3.titulo') }), margE: 220, margEstreito: 110, altLinha: 22,
          x: eixo(versoesE3.flatMap(([c]) => [D3.var_abstencao_pp[c].b_pp, D3.var_fatia_lula_pp[c].b_pp]), tickPp, T('vd.c9.e3_eixo')),
          linhas: versoesE3.map(([c, k]) => ({ nome: T(k), destaque: c === 'principal',
            vals: [{ v: D3.var_fatia_lula_pp[c].b_pp, lado: 'muted' }, { v: D3.var_abstencao_pp[c].b_pp, lado: 'ink' }],
            dica: { titulo: T(k), linhas: [{ lado: 'ink', t: T('c9.tab3.da'), v: fmt.pp(D3.var_abstencao_pp[c].b_pp, 2) }, { t: T('c9.tab3.p'), v: fmt.p(D3.var_abstencao_pp[c].p_permutacao) },
              { lado: 'muted', t: T('c9.tab3.ds'), v: fmt.pp(D3.var_fatia_lula_pp[c].b_pp, 2) }, { t: T('c9.tab3.p'), v: fmt.p(D3.var_fatia_lula_pp[c].p_permutacao) }] } })) }) },
      colunas: [{ t: T('tab.versao'), v: ([, k]) => T(k) },
        { t: T('c9.tab3.da'), num: true, v: ([c]) => D3.var_abstencao_pp[c].b_pp, f: v => fmt.pp(v, 2) },
        { t: T('c9.tab3.p'), num: true, v: ([c]) => D3.var_abstencao_pp[c].p_permutacao, f: fmt.p },
        { t: T('c9.tab3.ds'), num: true, v: ([c]) => D3.var_fatia_lula_pp[c].b_pp, f: v => fmt.pp(v, 2) },
        { t: T('c9.tab3.p'), num: true, v: ([c]) => D3.var_fatia_lula_pp[c].p_permutacao, f: fmt.p }] });
    P(s3, 'nota-tab', T('c9.tab3.nota', { pa: fmt.p(D3.var_abstencao_pp.p_holm), ps: fmt.p(D3.var_fatia_lula_pp.p_holm),
      sa: fmt.p(D3.var_abstencao_pp.selvagem.p_selvagem), ss: fmt.p(D3.var_fatia_lula_pp.selvagem.p_selvagem) }));
    P(s3, '', ...T.f('c9.det.e3_funil', { total: fmt.int(F3.total), nos6: fmt.int(F3.nos_6_estados), esp: nf(F3.esperado_pelo_numero_de_municipios, 0), faixa: fmt.pct(99.8, 1) }));
    // E4
    const s4 = secao(det, T('c9.e4.sec'));
    const C4 = EXP.E4.conferencias, ufs4 = EXP.E4.principal.filter(x => x.nivel === 'uf');
    P(s4, '', ...T.f('c9.det.e4', { fig: n3, abaixo: ufs4.filter(x => x.ic95_por_10[1] < 0).length, acima: ufs4.filter(x => x.ic95_por_10[0] > 0).length,
      zero: ufs4.filter(x => x.ic95_por_10[0] <= 0 && x.ic95_por_10[1] >= 0).length, n: ufs4.length,
      ctx: fmt.pp(EXP.E4.contexto_sem_efeito_de_municipio.b_por_10, 2) }));
    const versoesE4 = [['c9.tab4.principal', E4br]].concat(['sem_peso', 'sem_agregadas', 'sem_aptos_que_mudam', 'fatia_entre_validos', 'erro_agrupado_por_estado']
      .map(k => ['c9.tab4.' + k, C4[k]]));
    G.tabela(s4, { legenda: { n: ctx.nt(), t: T('c9.tab4.titulo') }, ordenavel: false, linhas: versoesE4, grafico: graficoB10(versoesE4, T('c9.tab4.titulo'), T('c9.fig3.eixo')),
      colunas: [{ t: T('tab.versao'), v: ([k]) => T(k) }, { t: T('c9.tab4.b'), num: true, v: ([, x]) => x.b_por_10, f: v => fmt.pp(v, 2) },
        { t: T('tab.ic95'), v: ([, x]) => T('g.de_a', { a: fmt.decSinal(x.ic95_por_10[0], 2), b: fmt.decSinal(x.ic95_por_10[1], 2) }) }] });
    // E5
    const s5 = secao(det, T('c9.e5.sec'));
    const C5 = E5.conferencias, ref = C5.divisao_igual;
    P(s5, '', ...T.f('c9.det.e5', { bruta: fmt.pp(C5.bruta.b_por_10, 2), corr: fmt.pp(E5.principal.b_por_10, 2), mun: fmt.pp(E5.h1_municipios_por_10, 2),
      frac: fmt.pct(E5.fracao_da_correcao_que_zera * 100, 0), esp: pontos(Math.abs(ref.esperada_por_10), 2), obs: pontos(Math.abs(ref.observada_bruta_por_10), 2),
      dif: pontos(Math.abs(ref.diferenca_por_10), 2), d0: fmt.abs(ref.diferenca_ic95_por_10[0], 2), d1: fmt.abs(ref.diferenca_ic95_por_10[1], 2) }));
    const versoesE5 = [['c9.tab5.principal', E5.principal], ['c9.tab5.bruta', C5.bruta], ['c9.tab5.200', C5.pelo_menos_200_votos],
      ['c9.tab5.sem_peso', C5.sem_peso], ['c9.tab5.sem_agregadas', C5.sem_agregadas]];
    G.tabela(s5, { legenda: { n: ctx.nt(), t: T('c9.tab5.titulo') }, ordenavel: false, linhas: versoesE5, destaque: ([k]) => k === 'c9.tab5.principal',
      grafico: graficoB10(versoesE5, T('c9.tab5.titulo'), T('vd.c9.e5_eixo')),
      colunas: [{ t: T('tab.versao'), v: ([k]) => T(k) }, { t: T('c9.tab5.b'), num: true, v: ([, x]) => x.b_por_10, f: v => fmt.pp(v, 2) },
        { t: T('tab.ic95'), v: ([, x]) => T('g.de_a', { a: fmt.decSinal(x.ic95_por_10[0], 2), b: fmt.decSinal(x.ic95_por_10[1], 2) }) }] });
    // 2ª rodada (T37): perguntas 6 a 10
    const lugaresId = ['Brasil'].concat(REG_ID, Object.keys(ID.grupos).filter(u => NOME_UF[u]).sort((a, b) => NOME_UF[a].localeCompare(NOME_UF[b])), ['Exterior']);
    const cT03 = ID.conf_t03;
    const si1 = secao(det, T('c9.i1.sec'));
    P(si1, '', ...T.f('c9.det.i1', { pa: fmt.int(cT03.aptos[0]), pc: fmt.int(cT03.comp[0]), oa: fmt.int(cT03.aptos[1]), oc: fmt.int(cT03.comp[1]),
      tte: fmt.int(cT03.tte), n24: nd('N24'), anal: fmt.int(ID.facultativo['18_a_69_facultativo_aptos']) }));
    G.tabela(si1, { legenda: { n: ctx.nt(), t: T('c9.tab6.titulo') }, ordenavel: true, linhas: lugaresId, destaque: lg => lg === 'Brasil',
      grafico: { legenda: [{ t: T('c9.grupo.g70'), lado: 'ink' }, { t: T('c9.grupo.g1859'), lado: 'muted' }],
        desenhar: caixa => G.linhasPontos(caixa, { aria: T('vd.aria', { t: T('c9.tab6.titulo') }), margE: 150, margEstreito: 40, altLinha: 16,
          x: { min: 0, max: 100, passo: 25, fmt: v => fmt.int(v), rotulo: T('c9.fig4.eixo') },
          linhas: lugaresId.map(lg => { const g = ID.grupos[lg], a = taxaId(g['g70']), b = taxaId(g['g1859']);
            return { nome: nomeLugarId(lg), curto: NOME_UF[lg] ? lg : nomeLugarId(lg).slice(0, 3), destaque: lg === 'Brasil',
              vals: [{ v: b, lado: 'muted' }, { v: a, lado: 'ink' }],
              dica: { titulo: nomeLugarId(lg), linhas: [{ lado: 'ink', t: T('c9.grupo.g70'), v: pctId(a) }, { lado: 'muted', t: T('c9.grupo.g1859'), v: pctId(b) }] } }; }) }) },
      colunas: [{ t: T('tab.lugar'), v: lg => nomeLugarId(lg) }].concat(GRUPOS_ID.map(g => ({ t: T('c9.grupo.' + g), num: true,
        v: lg => taxaId(ID.grupos[lg][g]), f: v => pctId(v) }))) });
    P(si1, 'nota-tab', T('c9.tab6.nota'));
    const si2 = secao(det, T('c9.i2.sec'));
    const cedo = Object.keys(ID.primeira_abaixo_50).filter(lg => lg !== 'Exterior' && ID.primeira_abaixo_50[lg] === 7579);
    P(si2, '', ...T.f('c9.det.i2', { lugares: listaE(cedo.map(nomeLugarId)) }));
    const lugF = ['Brasil'].concat(REG_ID);
    G.tabela(si2, { legenda: { n: ctx.nt(), t: T('c9.tab7.titulo') }, ordenavel: false, linhas: lugF, destaque: lg => lg === 'Brasil',
      colunas: [{ t: T('tab.lugar'), v: lg => nomeLugarId(lg) }].concat(F70_ID.map(fx => ({ t: nomeFaixa(fx, true), num: true,
        v: lg => taxaId(ID.faixas[lg][fx]), f: v => pctId(v) })), [{ t: T('c9.tab7.primeira'), v: lg => nomeFaixa(ID.primeira_abaixo_50[lg]) }]) });
    const si3 = secao(det, T('c9.i3.sec'));
    P(si3, '', ...T.f('c9.det.i3'));
    G.tabela(si3, { legenda: { n: ctx.nt(), t: T('c9.tab8.titulo') }, ordenavel: false, linhas: lugF, destaque: lg => lg === 'Brasil',
      colunas: [{ t: T('tab.lugar'), v: lg => nomeLugarId(lg) }].concat(GRUPOS_ID.slice(0, 5).map(g => ({ t: T('c9.grupo.' + g),
        v: lg => T('c9.tab8.cel', { b: pctId(ID.abstencao[lg][g].parte_da_abstencao), a: pctId(ID.abstencao[lg][g].parte_dos_aptos) }) }))) });
    const si4 = secao(det, T('c9.i4.sec'));
    P(si4, '', ...T.f('c9.det.i4', { sem: fmt.int(ID.genero_sem), fig: n5 }));
    const linG = lugF.flatMap(lg => ['mulheres', 'homens'].map(g => [lg, g]));
    G.tabela(si4, { legenda: { n: ctx.nt(), t: T('c9.tab9.titulo') }, ordenavel: false, linhas: linG, destaque: ([lg]) => lg === 'Brasil',
      colunas: [{ t: T('tab.lugar'), v: ([lg]) => nomeLugarId(lg) }, { t: T('c9.tab9.genero'), v: ([, g]) => T('c9.gen.' + g) }]
        .concat(['g1859', 'g6069', 'g70'].map(k => ({ t: T('c9.grupo.' + k), num: true,
          v: ([lg, g]) => taxaId(ID.genero[lg][g][k]), f: v => pctId(v) })),
        F70_ID.slice(0, 4).map(fx => ({ t: nomeFaixa(fx, true), num: true, v: ([lg, g]) => taxaId(ID.genero[lg][g][fx]), f: v => pctId(v) }))) });
    const si5 = secao(det, T('c9.i5.sec'));
    P(si5, '', ...T.f('c9.det.i5', { n: fmt.int(1000), fig: n6, iqa: pontos(Math.abs(S5.abstencao.principal[0].efeito_interquartil_pp), 2),
      iqs: pontos(Math.abs(S5.fatia_lula.principal[0].efeito_interquartil_pp), 2), sp: fmt.int(ID.secoes_desc.sem_perfil) }));
    const nomeV = k => T(['p70', 'perfil_igual_aos_aptos', 'sem_efeito_de_municipio', 'com_fatia_do_lula_no_1t'].includes(k) ? 'c9.tab10.' + k : 'c9.tab4.' + k);
    const versoes10 = [['principal', d => d.principal[0]]].concat(['sem_peso', 'sem_agregadas', 'sem_aptos_que_mudam', 'p70', 'erro_agrupado_por_estado', 'perfil_igual_aos_aptos']
      .map(k => [k, d => d.conferencias[k]]), ['sem_efeito_de_municipio', 'com_fatia_do_lula_no_1t'].map(k => [k, d => d.contexto[k]]));
    const celV = x => `${fmt.pp(x.b_por_10, 2)} (${icId(x)})`;
    G.tabela(si5, { legenda: { n: ctx.nt(), t: T('c9.tab10.titulo') }, ordenavel: false, linhas: versoes10, destaque: ([k]) => k === 'principal',
      grafico: { legenda: [{ t: T('leg.ic975'), tipo: 'ic' }],
        desenhar: caixa => G.coeficientes(caixa, { aria: T('vd.aria', { t: T('c9.tab10.titulo') }), margE: 260, margEstreito: 120, altLinha: 22,
          x: eixo(['abstencao', 'fatia_lula'].flatMap(d => versoes10.flatMap(([, f]) => f(S5[d]).ic975_por_10)), tickPp, T('c9.fig6.eixo')),
          linhas: [['abstencao', 'c9.fig6.grupo_a'], ['fatia_lula', 'c9.fig6.grupo_s']].flatMap(([d, kg]) => [{ grupo: T(kg) }].concat(versoes10.map(([k, f]) => {
            const x = f(S5[d]);
            return { nome: nomeV(k), v: x.b_por_10, ic: x.ic975_por_10, destaque: k === 'principal',
              dica: { titulo: `${nomeV(k)}: ${T(kg)}`, linhas: [{ t: T('c9.fig3.dica.b'), v: fmt.pp(x.b_por_10, 2) }, { t: T('tab.ic975'), v: icId(x) }] } }; }))) }) },
      colunas: [{ t: T('tab.versao'), v: ([k]) => nomeV(k) }, { t: T('c9.tab10.a'), v: ([, f]) => celV(f(S5.abstencao)) },
        { t: T('c9.tab10.s'), v: ([, f]) => celV(f(S5.fatia_lula)) }] });
    // os limites, para as dez
    const lim = secao(det, T('c9.limites.secao'));
    const ulL = el('ul', 'lista-texto', undefined, lim);
    for (const k of ['1', '2', '3', '4', '5', '6']) el('li', '', T('c9.limites.' + k), ulL);
  }

  // ======================= Os 9 capítulos, um depois do outro =======================
  // curto: o nome no índice da margem e na barra do celular; a pergunta inteira fica no título.
  const CAPITULOS = [cap1, cap2, cap3, cap4, cap5, cap6, cap7, cap8, cap9].map((montar, i) => ({ p: T(`c${i + 1}.pergunta`), curto: T(`c${i + 1}.curto`), montar }));
  // "Ver detalhes" diz o que tem dentro: o título de cada seção; a versão em texto entra só pela tabela que traz
  const oQueDe = s => (s.querySelector('h3').textContent === T('cap.resultado_texto') ? (s.querySelector('table') ? T('cap.tabela_resultado') : '') : s.querySelector('h3').textContent);
  CAPITULOS.forEach((c, i) => {
    const n = i + 1;
    const art = el('article', 'capitulo', undefined, $('#capitulos'));
    art.id = 'capitulo-' + n; art.tabIndex = -1;
    art.setAttribute('aria-labelledby', 't-cap' + n);
    const cab = el('header', 'cap-cab', undefined, art);
    const h = el('h2', 'cap-titulo', undefined, cab); h.id = 't-cap' + n;
    el('span', 'cap-num', String(n), h);
    h.append(' ' + c.p);
    let kf = 0, kt = 0;
    const ctx = { n, art, cab, nf: () => `${n}.${++kf}`, nt: () => T('cap.tabela_n', { n: `${n}.${++kt}` }) };
    c.montar(ctx);
    // T33: os capítulos dos assuntos da exploração guiada levam só um aviso com o link para o capítulo 9
    if (['c1', 'c3', 'c4', 'c8'].includes('c' + n) && ctx.detalhes) {
      const p = el('p', 'nota-tab', T('c9.link.c' + n), $('.detalhes-corpo', ctx.detalhes));
      ir(p, '#analise/9', T('c9.link.ir'));
    }
    if (ctx.oQue) {
      const itens = $$('.detalhes-corpo > section', ctx.detalhes).map(oQueDe).filter(Boolean);
      ctx.oQue.textContent = listaE(itens.map(x => x.charAt(0).toLowerCase() + x.slice(1)));
    }
  });

  // ======================= Índice das partes das páginas de consulta (diário, D39) =======================
  // Como o índice dos capítulos: na margem no computador e numa barra presa no topo no celular, que
  // rola de lado até a parte atual. partes: [{id, nome, href}], a primeira é o topo da página;
  // extras: links depois de um fio (por exemplo, a volta ao capítulo 7).
  function indicePartes(ol, vista, partes, extras = []) {
    if (!ol || !vista) return;
    for (const t of partes.concat(extras.map(e => Object.assign({ sep: true }, e)))) {
      const a = el('a', '', undefined, el('li', 'sem-n' + (t.sep ? ' sep' : ''), undefined, ol));
      a.href = t.href;
      if (t.id) a.dataset.parte = t.id;
      el('span', 'i-n', '', a); el('span', 'i-t', t.nome, a);
    }
    let pedido = false;
    const marcarParte = () => {
      pedido = false;
      if (vista.hidden) return;
      let agora = partes[0].id;
      for (const t of partes.slice(1)) { const e = document.getElementById(t.id); if (e && e.getBoundingClientRect().top <= innerHeight * 0.35) agora = t.id; }
      if (innerHeight + scrollY >= document.documentElement.scrollHeight - 4) agora = partes[partes.length - 1].id; // no fim da página
      $$('a[data-parte]', ol).forEach(a => {
        if (a.dataset.parte !== agora) { a.removeAttribute('aria-current'); return; }
        if (a.getAttribute('aria-current')) return;
        a.setAttribute('aria-current', 'location');
        const barra = ol.parentElement; // no celular a barra rola de lado: a parte atual fica à vista
        if (barra.scrollWidth > barra.clientWidth) barra.scrollLeft = Math.max(0, a.offsetLeft - 16);
      });
    };
    addEventListener('scroll', () => { if (!pedido) { pedido = true; requestAnimationFrame(marcarParte); } }, { passive: true });
    new MutationObserver(marcarParte).observe(vista, { attributes: true, attributeFilter: ['hidden'] });
    marcarParte();
  }

  // ======================= Explorar (T24, em explorar.js) =======================
  // Montado aqui, antes da lista de notas, para as notas das figuras dele entrarem na mesma lista.
  if (window.EXPLORAR) window.EXPLORAR({ D, G, BR, UFS, NOME_UF, REGIAO_UF, PORTE, municipios, doBrasil, acimaDoPiso, nomeMun,
    el, B, P, N, listaE, figura, figurasComAbas, grafico, sup, notaDados, nd, fichaCidade, busca, funilFig, tabelaVersoes, graficoVersoes, tabelaErroFaixas, eixo,
    nomeVersao, curtoVersao, classeTexto, coefTxt, icTxt, partesConferencias, guarda, semMovimento, dadosComo, faixaOutros, linhasVieram, comumSecoes,
    SOC_VARS, socValor });
  // O mapa para passear pelos dados (T36, em passear.js)
  if (window.PASSEAR) window.PASSEAR({ D, G, BR, UFS, NOME_UF, municipios, nomeMun, el, B, P, busca, semMovimento });
  // "Pergunte aos dados" (T14, em pergunte.js): a primeira parte do Explorar
  if (window.PERGUNTE) window.PERGUNTE({ D, G, BR, UFS, NOME_UF, REGIAO_UF, doBrasil, nomeMun, el, B, P, nd, semMovimento });
  indicePartes($('#exp-lista-indice'), $('#explorar'), [
    { id: 'explorar', nome: T('nav.explorar'), href: '#explorar' },
    { id: 'explorar-pergunte', nome: T('exp.perg.tit'), href: '#explorar/pergunte' },
    { id: 'explorar-ponte', nome: T('exp.ponte.tit'), href: '#explorar/ponte' },
    { id: 'explorar-estados', nome: T('exp.estados.tit'), href: '#explorar/estados' },
    { id: 'explorar-municipios', nome: T('exp.municipios.tit'), href: '#explorar/municipios' },
    { id: 'explorar-incerteza', nome: T('exp.incerteza.tit'), href: '#explorar/incerteza' }]);

  // ======================= Apuração ao vivo (T28, em apuracao.js) =======================
  // Também antes da lista de notas, pelo mesmo motivo do Explorar.
  if (window.APURACAO) window.APURACAO({ D, G, BR, UFS, doBrasil, nomeMun, el, B, P, N, figura, sup, notaDados, semMovimento, indicePartes, dadosComo });
  window.ESTUDO_PARTES = { indicePartes }; // Método e fontes (metodo.js, T12) usa o mesmo índice das partes

  // ---------- Notas da leitura e notas sobre os dados ----------
  (function listaNotas() {
    const ol = $('#lista-notas');
    notas.forEach((n, i) => {
      const li = el('li', '', undefined, ol);
      li.id = 'nota-' + (i + 1); li.tabIndex = -1;
      el('span', 'nota-n', String(i + 1), li);
      const c = el('div', '', undefined, li);
      el('p', 'nota-titulo', n.titulo, c);
      for (const p of n.paragrafos) P(c, '', ...[].concat(p));
    });
  })();
  $$('form[data-comentario]').forEach(f => f.addEventListener('submit', ev => ev.preventDefault()));

  // ======================= Índice fixo dos capítulos =======================
  // Resumo, os 9 capítulos (numerados: são uma sequência), Comentários e Notas. Na margem, todos;
  // na barra do celular, só os números, com o nome do trecho atual ao lado.
  const TRECHOS = [{ id: 'resumo', nome: T('nav.resumo'), href: '#resumo' }]
    .concat(CAPITULOS.map((c, i) => ({ id: 'capitulo-' + (i + 1), n: i + 1, nome: c.curto, p: c.p, href: '#analise/' + (i + 1) })))
    .concat([{ id: 'comentarios', nome: T('ind.comentarios'), href: '#comentarios' }, { id: 'notas', nome: T('ind.notas'), href: '#notas' }]);
  (function indice() {
    const ol = $('#lista-indice');
    TRECHOS.forEach((t, i) => {
      const li = el('li', (t.n ? '' : 'sem-n') + (t.n === 1 || t.id === 'comentarios' ? ' sep' : ''), undefined, ol);
      const a = el('a', '', undefined, li);
      a.href = t.href; a.dataset.trecho = t.id;
      el('span', 'i-n', t.n ? String(t.n) : '', a);
      el('span', 'i-t', t.nome, a);
      if (t.n) { a.title = t.p; a.setAttribute('aria-label', T('ind.cap_aria', { n: t.n, p: t.p })); }
    });
  })();

  // ======================= Endereços, botão voltar e o trecho atual =======================
  // Vistas: a leitura (#resumo, #analise/3, #comentarios, #nota-4), Explorar (#explorar, #explorar/estados),
  // Apuração ao vivo (#apuracao, #apuracao/fim) e Método e fontes (#metodo, #metodo/nota-N08, #metodo/sobre). Os links internos são tratados
  // aqui: cada clique entra no histórico, e o botão voltar devolve a pessoa ao ponto em que estava.
  function rota(hash) {
    const h = decodeURIComponent((hash || '').replace(/^#/, ''));
    const [a, b] = h.split('/');
    // canonico: o endereço que a página realmente mostra, quando o pedido não existe (#analise/99, #xyz); a URL passa a dizer a verdade (QA nº 11)
    if (a === 'mapa') return { vista: 'mapa', alvo: 'mapa', canonico: b && !/^[A-Z]{2}$/.test(b) ? '#mapa' : null }; // T36: #mapa/SP abre o estado (passear.js)
    if (a === 'explorar') return { vista: 'explorar', alvo: b && document.getElementById('explorar-' + b) ? 'explorar-' + b : 'explorar', canonico: b && !document.getElementById('explorar-' + b) ? '#explorar' : null };
    if (a === 'apuracao') return { vista: 'apuracao', alvo: b && document.getElementById('apuracao-' + b) ? 'apuracao-' + b : 'apuracao', canonico: b && !document.getElementById('apuracao-' + b) ? '#apuracao' : null };
    if (a === 'metodo') return { vista: 'metodo', alvo: b && document.getElementById(b) ? b : 'metodo', canonico: b && !document.getElementById(b) ? '#metodo' : null };
    if (a === 'analise') {
      const n = Math.min(CAPITULOS.length, Math.max(1, parseInt(b, 10) || 1));
      return { vista: 'leitura', alvo: 'capitulo-' + n, canonico: String(n) === b ? null : '#analise/' + n };
    }
    if (a && a !== 'resumo' && document.getElementById(a) && $('.leitura').contains(document.getElementById(a))) return { vista: 'leitura', alvo: a, canonico: null };
    return { vista: 'leitura', alvo: 'resumo', canonico: h && h !== 'resumo' && h !== 'conteudo' ? '' : null };
  }
  let vistaAtual = null, trechoAtual = null, rolagemPropriaAte = 0;
  function mostrarVista(v) {
    if (v === vistaAtual) return false;
    $$('.vista').forEach(s => { s.hidden = s.dataset.vista !== v; });
    vistaAtual = v;
    G.dicaEsconder();
    if (window.contar) contar('aba', v); // contadores próprios (T16, P35): uma vez por visita
    return true;
  }
  function marcarNav(secao) {
    $$('.nav a[data-secao]').forEach(a => {
      if (a.dataset.secao === secao) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current');
    });
  }
  const BASE_TITULO = T('pag.nome');
  function marcarTrecho(id, mudarEndereco) {
    if (id === trechoAtual) return;
    trechoAtual = id;
    const t = TRECHOS.find(x => x.id === id);
    $$('#lista-indice a').forEach(a => {
      if (a.dataset.trecho === id) a.setAttribute('aria-current', 'location'); else a.removeAttribute('aria-current');
    });
    $('#indice-atual').textContent = t.nome;
    if (t.n && window.contar) contar('capitulo', t.n);
    marcarNav(id === 'resumo' ? 'resumo' : 'capitulos');
    document.title = t.n ? T('pag.titulo_cap', { n: t.n, p: t.p, nome: BASE_TITULO }) : T('pag.titulo', { titulo: T('pag.manchete'), nome: BASE_TITULO });
    if (mudarEndereco) {
      const novo = id === 'resumo' ? location.pathname + location.search : t.href;
      if ((location.hash || '') !== (id === 'resumo' ? '' : t.href)) history.replaceState(history.state, '', novo);
    }
  }
  function trechoNaTela() {
    const linha = innerHeight * 0.35;
    let atual = 'resumo';
    for (const t of TRECHOS) {
      const e = document.getElementById(t.id);
      if (e && e.getBoundingClientRect().top <= linha) atual = t.id;
    }
    if (innerHeight + scrollY >= document.documentElement.scrollHeight - 4) atual = 'notas'; // no fim da página
    return atual;
  }
  let pedido = false;
  addEventListener('scroll', () => {
    if (pedido || vistaAtual !== 'leitura') return;
    pedido = true;
    requestAnimationFrame(() => {
      pedido = false;
      if (performance.now() < rolagemPropriaAte) return; // enquanto o clique leva ao capítulo, o índice já marca o destino
      marcarTrecho(trechoNaTela(), true);
    });
  }, { passive: true });
  addEventListener('scrollend', () => { rolagemPropriaAte = 0; });

  function navegar(hash, { y = null, suave = true, foco = true } = {}) {
    const r = rota(hash);
    if (r.canonico !== null && r.canonico !== undefined) history.replaceState(history.state, '', r.canonico || location.pathname + location.search);
    const trocou = mostrarVista(r.vista);
    if (r.vista !== 'leitura') {
      marcarNav(r.vista);
      document.title = T('pag.titulo', { titulo: T({ explorar: 'nav.explorar', apuracao: 'nav.apuracao', mapa: 'nav.mapa' }[r.vista] || 'nav.metodo'), nome: BASE_TITULO });
    }
    const alvo = document.getElementById(r.alvo);
    // a nota dentro das notas recolhidas (ou de outro "Ver detalhes" fechado): abre antes de rolar até ela
    for (let e = alvo; e; e = e.parentElement) if (e.tagName === 'DETAILS' && !e.open) e.open = true;
    if (y !== null) {
      window.scrollTo(0, y);
      if (r.vista === 'leitura') { trechoAtual = null; marcarTrecho(trechoNaTela(), false); }
      return;
    }
    if (r.vista === 'leitura') {
      trechoAtual = null;
      const trecho = TRECHOS.some(t => t.id === r.alvo) ? r.alvo : alvo.closest('#notas, #comentarios') ? alvo.closest('#notas, #comentarios').id : trechoNaTela();
      marcarTrecho(trecho, false);
    }
    const comportamento = suave && !trocou && !semMovimento() ? 'smooth' : 'auto';
    rolagemPropriaAte = performance.now() + (comportamento === 'smooth' ? 1500 : 100);
    if (r.alvo === 'resumo' || (r.vista !== 'leitura' && r.alvo === r.vista)) window.scrollTo({ top: 0, behavior: comportamento });
    else alvo.scrollIntoView({ behavior: comportamento, block: /^nota-/.test(r.alvo) ? 'center' : 'start' });
    if (foco) alvo.focus({ preventScroll: true }); // na abertura da página o foco fica no começo, para o Tab achar "Pular para o conteúdo" e o menu
  }
  document.addEventListener('click', ev => {
    const a = ev.target.closest && ev.target.closest('a[href^="#"]');
    if (!a || ev.defaultPrevented || ev.button !== 0 || ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey) return;
    const hash = a.getAttribute('href');
    if (hash === '#conteudo') return; // "Pular para o conteúdo" segue o comportamento normal
    ev.preventDefault();
    history.replaceState(Object.assign({}, history.state, { y: scrollY }), '', location.href); // o ponto de volta
    history.pushState({}, '', hash === '#resumo' ? location.pathname + location.search : hash);
    navegar(hash);
  });
  addEventListener('popstate', ev => {
    if (location.hash === '#conteudo') return; // "Pular para o conteúdo" não troca de trecho
    const y = ev.state && typeof ev.state.y === 'number' ? ev.state.y : null;
    navegar(location.hash, { y, suave: false });
  });

  // ---------- Modo claro e escuro (a escolha é lembrada) ----------
  function temaEfetivo() {
    const t = html.getAttribute('data-tema');
    return t || (matchMedia('(prefers-color-scheme: dark)').matches ? 'escuro' : 'claro');
  }
  const btTema = $('.bt-tema');
  const rotuloTema = () => { btTema.textContent = T(temaEfetivo() === 'escuro' ? 'cab.modo_claro' : 'cab.modo_escuro'); };
  btTema.addEventListener('click', () => {
    const novo = temaEfetivo() === 'escuro' ? 'claro' : 'escuro';
    html.setAttribute('data-tema', novo);
    guarda.gravar('analise-tema', novo);
    rotuloTema();
  });
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', rotuloTema);
  rotuloTema();

  // ---------- Primeira abertura ----------
  // Os gráficos e as fontes mudam a altura dos capítulos: o link direto (#analise/5) é seguido de
  // novo quando eles terminam, para a página parar no começo do capítulo.
  if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
  const inicial = location.hash;
  let mexeu = false;
  for (const tipo of ['wheel', 'touchmove', 'keydown', 'pointerdown']) addEventListener(tipo, () => { mexeu = true; }, { once: true, passive: true });
  navegar(inicial, { suave: false, foco: false });
  const pronto = document.fonts ? document.fonts.ready : Promise.resolve();
  pronto.then(() => {
    redesenhos.forEach(f => f()); // as anotações medem o texto: desenha de novo com as fontes
    requestAnimationFrame(() => requestAnimationFrame(() => {
      if (inicial && location.hash === inicial && !mexeu) navegar(inicial, { suave: false, foco: false });
    }));
  });
})();
