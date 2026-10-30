/* Método e fontes (T12; especificação 7.3 e 7.6). Monta as partes da página a partir dos dados e do
   catálogo: o passo a passo do cálculo, as fontes (do registro de fontes do T12), a classificação dos
   partidos (dados/escala_partidos.csv, via dados.js), hipóteses e incerteza, os limites, as notas
   sobre os dados com o texto inteiro e o caminho de volta aos gráficos que cada uma afeta, e as
   estimativas que não deram (dados/inferencia.json, via dados.js). O glossário vem de glossario.js;
   os dados para baixar e "Sobre este estudo", de extras.js (T25). Carregado por último: as figuras
   da leitura, do Explorar e da Apuração ao vivo já existem quando as notas procuram as marcas delas.
   Os números das notas saem dos dados sempre que estão neles; os que vêm só dos registros (T04, T05)
   ficam abaixo, com a origem. Todo número é formatado na língua da página, uma vez (diário, D25). */
(function () {
  'use strict';
  const D = window.ESTUDO, G = window.GRAFICOS, T = window.T, { fmt, nf } = G;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  if (!$('#met-passo')) return;
  function el(tag, cls, texto, pai) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (texto !== undefined) e.textContent = texto;
    if (pai) pai.appendChild(e);
    return e;
  }
  const P = (pai, cls, partes) => { const p = el('p', cls, undefined, pai); p.append(...[].concat(partes)); return p; };
  const html = (pai, tag, cls, chave, vals) => { const e = el(tag, cls, undefined, pai); e.innerHTML = T(chave, vals); return e; };
  const link = (href, texto) => { const a = el('a', '', texto); a.href = href; return a; };
  const nota = id => { const a = link('#metodo/nota-' + id, id); a.title = T('nota.' + id); return a; };
  const parte = (id, chave) => link('#metodo/' + id, T(chave));
  const code = t => el('code', '', t);
  const REPO = 'https://github.com/MuriloNM/analise-da-virada';
  const PASTA_CSV = T.raiz + 'csv/' + T.linguas.find(l => l.codigo === T.lingua).pasta;
  const csv = nome => { const a = link(PASTA_CSV + nome + '.csv', nome + '.csv'); a.setAttribute('download', ''); return a; };
  function listaNos(nos) {
    const s = el('span');
    if (nos.length < 2) { s.append(...nos); return s; }
    for (const p of new Intl.ListFormat(T.lingua, { type: 'conjunction' }).formatToParts(nos.map((_, i) => String(i))))
      s.append(p.type === 'element' ? nos[+p.value] : p.value);
    return s;
  }
  const BR = D.brasil;
  const NOME_UF = Object.fromEntries(D.ufs.map(u => [u.codigo, u.nome]));
  const MUN = D.municipios.linhas.split('\n').map(l => {
    const v = l.split('|'), o = {};
    D.municipios.campos.forEach((k, i) => { o[k] = i < 2 ? v[i] : +v[i]; });
    return o;
  });
  const doBrasil = MUN.filter(m => m.uf !== 'ZZ');
  const PR = D.projecao.pontos;

  // ======================= Passo a passo do cálculo =======================
  const PASSOS = [
    { scripts: ['scripts/base1t.py'], saidas: ['dados/base_1t_municipios.json'], csv: ['municipios'] },
    { scripts: ['scripts/base2t.py', 'scripts/confere2t.py'], saidas: ['dados/base_2t_municipios.json'], csv: ['municipios'] },
    { scripts: ['scripts/analise_base.py'], saidas: ['dados/analise_municipios.csv', 'dados/analise_estados.csv'], csv: ['municipios', 'estados'] },
    { scripts: ['scripts/votos_partido_1t.py', 'scripts/tse6259_uf.py'], saidas: ['dados/votos_partido_1t.json'], csv: [] },
    { scripts: ['scripts/escala_partidos.py'], saidas: ['dados/escala_partidos.csv', 'dados/esquerda_1t_municipios.csv'], csv: ['partidos', 'esquerda_municipios'] },
    { scripts: ['scripts/secoes_baixar.py', 'scripts/secoes.py', 'scripts/secoes_inferencia.py', 'scripts/inferencia.py', 'scripts/exploracao.py'],
      saidas: ['dados/secoes_presidente.csv.gz', 'dados/secoes_inferencia.json', 'dados/inferencia.json', 'dados/exploracao.json'], csv: ['hipoteses', 'de_onde_vieram'] }, // T35: a conta por seção; T33: a exploração guiada
    { scripts: ['scripts/collector.py', 'scripts/bweb.py', 'scripts/curva1t.py', 'scripts/apuracao_dados.py'],
      saidas: ['dados/historico_2t.json', 'dados/base_1t_compacta.json', 'apuracao-dados.js'], csv: ['apuracao_ao_vivo'] },
    { scripts: ['scripts/pagina_dados.py', 'scripts/mapa_ufs.py', 'scripts/csv_estudo.py'], saidas: ['dados.js', 'mapa.js', 'csv/'], csv: ['dicionario'] },
  ];
  (function passoAPasso() {
    const caixa = $('#met-passo');
    P(caixa, 'met-intro', T('met.passo.intro'));
    const ol = el('ol', 'met-passos', undefined, caixa);
    const vals = {
      1: { mun: fmt.int(MUN.length) },
      5: { partidos: parte('partidos', 'met.partidos.tit') },
      6: { incerteza: parte('incerteza', 'met.inc.tit') },
      7: { como: link('#apuracao/como', T('met.passo.7.como')) },
      8: { n18: nota('N18') },
    };
    PASSOS.forEach((p, i) => {
      const n = i + 1;
      const li = el('li', 'met-passo', undefined, ol);
      li.id = 'passo-' + n; li.tabIndex = -1;
      el('span', 'met-passo-n', String(n), li).setAttribute('aria-hidden', 'true');
      const c = el('div', 'met-passo-corpo', undefined, li);
      const h = el('h3', '', undefined, c);
      el('span', 'sr', T('met.passo.n', { n }) + ': ', h); h.append(T('met.passo.' + n + '.tit'));
      P(c, '', T.f('met.passo.' + n + '.txt', vals[n]));
      const cadeia = el('p', 'met-cadeia', undefined, c);
      cadeia.setAttribute('aria-label', T('met.passo.cadeia_aria', { n }));
      cadeia.append(listaNos(p.scripts.map(code)), el('span', 'met-seta', ' → '), listaNos(p.saidas.map(code)));
      if (p.csv.length) P(c, 'met-baixar', T.f('met.passo.baixar', { arquivos: listaNos(p.csv.map(csv)) }));
    });
    // o repositório público (T15; github.com/MuriloNM/analise-da-virada, publicado junto com a página no T09)
    P(caixa, 'met-pe', T.f('met.passo.repo', { repo: link(REPO, T('pag.repo')), baixar: parte('dados', 'met.dados.tit') }));
  })();

  // ======================= Fontes =======================
  // Do registro de fontes do T12 (docs/analise/tickets/T12-metodo-fontes.md): endereço, quando foi
  // baixado e a conferência. As contagens da conferência vêm dos dados; as outras, do registro.
  const R = 'https://resultados.tse.jus.br/oficial/ele2026/';
  const ODS = 'https://cdn.tse.jus.br/estatistica/sead/odsele/';
  const quando = (chave, data, h1, h2, tse) => T(chave, { quando: !h1 ? T.data(data) : !h2 ? T('met.fontes.data_hora', { data: T.data(data), hora: h1 })
    : T(tse ? 'met.fontes.hora_tse' : 'met.fontes.data_horas', { data: T.data(data), h1, h2 }) });
  const TSE = [
    { id: '1t', end: [R + '6257/dados/{uf}/{uf}{cdmun}-c0001-e006257-u.json'], quando: quando('met.fontes.quando', '2026-10-25'),
      conf: { mun: fmt.int(MUN.length), l: fmt.int(BR.L1), f: fmt.int(BR.F1) } },
    { id: '2t', end: [R + '6258/dados/{uf}/{uf}{cdmun}-c0001-e006258-u.json'], quando: quando('met.fontes.quando', '2026-10-26', '10:56', '11:08'),
      conf: { arq: fmt.int(5786), l: fmt.int(BR.L2), f: fmt.int(BR.F2), b: fmt.int(1430496), nu: fmt.int(2723305) } },
    { id: '2t_br', end: [R + '6258/dados/br/br-c0001-e006258-u.json'], link: true, quando: quando('met.fontes.quando', '2026-10-25', '23:27'),
      conf: { hora: '23:27:02', pct: fmt.pct(BR.s2, 3) } },
    { id: 'bweb', end: ['https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_1t_{UF}_051020261403.zip'], quando: quando('met.fontes.quando', '2026-10-25'),
      conf: { sec: fmt.int(499206) } },
    // T27 e T35: os dados por seção dos dois turnos, da conta por seção (para onde foi o saldo, por lugar)
    { id: 'secoes', end: [ODS + 'votacao_secao/votacao_secao_2026_BR.zip', ODS + 'detalhe_votacao_secao/detalhe_votacao_secao_2026.zip',
      'https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_2t_{UF}_261020260742.zip'], quando: quando('met.fontes.quando', '2026-10-27', '00:13', '00:16'),
      conf: { sec: fmt.int(D.secoes.secoes_total), mun: fmt.int(MUN.length) } },
    { id: 'mun', end: [R + '6258/config/mun-e006258-cm.json'], link: true, quando: quando('met.fontes.gerado', '2026-10-15'),
      conf: { n: fmt.int(MUN.length) } },
    { id: 'partido', end: [ODS + 'votacao_partido_munzona/votacao_partido_munzona_2026.zip'], link: true, quando: quando('met.fontes.quando', '2026-10-26', '10:55'),
      conf: { mb: T('ext.mb', { n: nf(22.9, 1) }) } },
    { id: 'partido_uf', end: [R + '6259/dados/{uf}/{uf}-c000{3,5,6,7}-e006259-u.json'], quando: quando('met.fontes.quando', '2026-10-26', '10:56', '10:58') },
    { id: 'cand', end: [ODS + 'consulta_cand/consulta_cand_2026.zip'], link: true, quando: quando('met.fontes.consultado', '2026-10-26', '11:05'),
      conf: { n02: nota('N02') } },
    { id: 'fotos', end: [R + '6258/fotos/br/280002542548.jpeg', R + '6258/fotos/br/280002551544.jpeg'], link: true, quando: quando('met.fontes.quando', '2026-10-26', '13:16') },
    { id: 'ao_vivo', antes: T('met.fonte.ao_vivo.end'), end: [R + '6258/dados/'], quando: quando('met.fontes.quando', '2026-10-25', PR[0].hora.slice(0, 5), '23:27', true),
      conf: { n: fmt.int(PR.length + 1), a: fmt.pct(PR[0].apurado, 2), b0: fmt.pct(60.85, 2), b1: fmt.pct(68.8, 1), n17: nota('N17') } },
  ];
  const OUTRAS = [
    { id: 'escala', end: ['https://doi.org/10.7910/DVN/MFIXKW', 'https://doi.org/10.1590/1807-0191202531120'], link: true, quando: quando('met.fontes.quando', '2026-10-26', '11:45'),
      conf: { partidos: parte('partidos', 'met.partidos.tit') } },
    { id: 'escala18', end: ['https://doi.org/10.1590/dados.2023.66.2.303', 'https://doi.org/10.7910/DVN/6KVTUV'], link: true, quando: quando('met.fontes.quando', '2026-10-26', '11:49') },
    { id: 'malha', end: ['https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR?formato=application/json&qualidade=minima&intrarregiao=UF'], link: true,
      quando: quando('met.fontes.quando', '2026-10-26', '13:17') },
    // T36 (P38): a malha dos municípios, só para o Mapa
    { id: 'malha_mun', end: ['https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR?formato=application/json&qualidade=minima&intrarregiao=municipio'], link: true,
      quando: quando('met.fontes.quando', '2026-10-28', '00:20') },
    { id: 'porte', nomes: [['https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm', 'met.fonte.porte.cf'],
      ['https://ftp.ibge.gov.br/Perfil_Municipios/2012/pdf/tab021.pdf', 'met.fonte.porte.ibge']], quando: quando('met.fontes.consultado', '2026-10-26', '11:50'),
      conf: { n08: nota('N08') } },
  ];
  function listaFontes(pai, fontes) {
    const ul = el('ul', 'met-fontes', undefined, pai);
    for (const f of fontes) {
      const li = el('li', '', undefined, ul);
      li.id = 'fonte-' + f.id.replace(/_/g, '-');
      el('h4', '', T('met.fonte.' + f.id + '.tit'), li);
      const end = el('p', 'met-end', undefined, li);
      if (f.antes) end.append(f.antes + ' ');
      if (f.nomes) end.append(listaNos(f.nomes.map(([u, k]) => link(u, T(k)))));
      else end.append(listaNos(f.end.map(u => { const c = code(u.replace(/^https:\/\//, '')); if (!f.link) return c; const a = link(u, ''); a.append(c); return a; })));
      el('p', 'met-quando', f.quando, li);
      if (T.tem('met.fonte.' + f.id + '.conf')) P(li, 'met-conf', T.f('met.fonte.' + f.id + '.conf', f.conf));
    }
  }
  (function fontes() {
    const caixa = $('#met-fontes');
    P(caixa, 'met-intro', T('met.fontes.intro'));
    el('h3', 'met-sub', T('met.fontes.tse'), caixa);
    listaFontes(caixa, TSE);
    el('h3', 'met-sub', T('met.fontes.outras'), caixa);
    listaFontes(caixa, OUTRAS);
    el('h3', 'met-sub', T('met.fontes.contexto'), caixa);
    html(caixa, 'p', 'met-ctx', 'met.ctx.sj.html');
    html(caixa, 'p', 'met-ctx', 'met.ctx.partidos.html');
    P(caixa, 'met-pe', T('met.ctx.pe'));
  })();

  // ======================= Classificação dos partidos =======================
  (function partidos() {
    const caixa = $('#met-partidos');
    html(caixa, 'p', 'met-texto', 'met.partidos.quem.html');
    P(caixa, 'met-texto', T('met.partidos.como'));
    P(caixa, 'met-texto', T('met.partidos.porque'));
    P(caixa, 'met-texto', T.f('met.partidos.corte', { corte: nf(4.49, 2) }));
    el('h3', 'met-sub', T('met.partidos.regras_tit'), caixa);
    const ul = el('ul', 'met-regras', undefined, caixa);
    for (const r of ['R1', 'R2', 'R3', 'R4', 'R5', 'R6']) P(el('li', '', undefined, ul), '', T.f('met.regra.' + r, { n11: nota('N11') }));

    const tc = el('div', 'tab-caixa met-tab-partidos', undefined, caixa);
    const tab = el('table', 'tab', undefined, tc);
    el('caption', '', T('met.partidos.tab'), tab);
    const hr = el('tr', '', undefined, el('thead', '', undefined, tab));
    const cols = [['numero', 'num'], ['partido', ''], ['posicao', 'num'], ['escala', 'met-col-escala'], ['categoria', ''], ['campo', ''], ['regra', ''], ['notas', 'num'], ['pos2018', 'num']];
    for (const [k, cls] of cols) { const th = el('th', cls, T('met.col.' + k), hr); th.scope = 'col'; }
    const tb = el('tbody', '', undefined, tab);
    const CORTE = 4.49;
    const sp = v => (v === null ? T('met.sem_posicao') : nf(v, 2));
    for (const p of D.partidos) {
      const tr = el('tr', '', undefined, tb);
      el('td', 'num', String(p.numero), tr);
      const th = el('th', '', p.sigla, tr); th.scope = 'row';
      el('td', 'num', sp(p.posicao), tr);
      const te = el('td', 'met-col-escala', undefined, tr);
      if (p.posicao !== null) {
        const r = el('span', 'met-escala', undefined, te);
        r.setAttribute('role', 'img'); r.setAttribute('aria-label', T('met.escala_aria', { pos: nf(p.posicao, 2) }));
        el('i', 'met-escala-corte', undefined, r).style.left = (CORTE * 10) + '%';
        el('b', '', undefined, r).style.left = (p.posicao * 10) + '%';
      }
      el('td', '', p.categoria ? T('met.cat.' + p.categoria) : fmt.vazio, tr);
      el('td', '', p.posicao === null ? T('met.sem_posicao') : T(p.esquerda ? 'met.sim' : 'met.nao'), tr);
      el('td', '', p.regra, tr);
      el('td', 'num', p.especialistas === null ? fmt.vazio : String(p.especialistas), tr);
      el('td', 'num', p.pos_2018 === null ? T('met.nao_existia') : nf(p.pos_2018, 2), tr);
    }
    P(caixa, 'met-pe', T.f('met.partidos.pe', { n12: nota('N12') }));
    // Conferências (registro do T05): % de esquerda no Brasil, deputado federal, pelas rodadas de 2022 e de 2018,
    // e a correlação de Spearman com Zucco e Power nos 16 partidos em comum
    html(caixa, 'p', 'met-texto', 'met.partidos.conf.html', { pct22: fmt.pct(26.3, 1), pct18: fmt.pct(24.9, 1), rho: nf(0.953, 3) });
  })();

  // ======================= Hipóteses e incerteza =======================
  (function incerteza() {
    const caixa = $('#met-incerteza');
    const lista = parte('nao-deu', 'met.nao_deu.tit');
    P(caixa, 'met-texto', T.f('met.inc.contagem'));
    P(caixa, 'met-texto', T.f('met.inc.antes', { n16: nota('N16') }));
    P(caixa, 'met-texto', T.f('met.inc.teste'));
    // T32 (M5): quanto o peso se concentra em poucos estados e o número efetivo de grupos (Carter, Schnepel e Steigerwald, 2017)
    const PG = D.poucos_grupos, pesos = Object.values(PG.peso_uf), ge = Object.values(PG.g_efetivo).flat();
    P(caixa, 'met-texto', T.f('met.inc.poucos', { rep: fmt.int(9999), sp: fmt.pct(100 * PG.peso_uf.SP, 1),
      oito: fmt.pct(100 * pesos.slice(0, 8).reduce((x, y) => x + y, 0), 0), gmin: nf(Math.min(...ge), 1), gmax: nf(Math.max(...ge), 0) }));
    P(caixa, 'met-texto', T.f('met.inc.classe', { p: nf(0.05, 2), pp: fmt.pp(0.5, 1).replace(/^\+/, '') }));
    P(caixa, 'met-texto', T.f('met.inc.sociais', { p: nf(0.05, 2) })); // T34: os 35 testes dos dados sociais, com Holm
    P(caixa, 'met-texto', T.f('met.inc.ecologica', { rep: fmt.int(1000), sec: fmt.int(D.secoes.secoes), comum: fmt.miAbs(D.secoes.parte_comum.lula), pct: fmt.pct(100 * D.secoes.parte_comum.lula_pct_do_saldo, 0) }));
    P(caixa, 'met-texto', T.f('met.inc.criterio', { lista }));
    P(caixa, 'met-texto', T.f('met.inc.funil'));
    P(caixa, 'met-texto', T.f('met.inc.projecao'));
    P(caixa, 'met-texto', T('met.inc.semente'));
    el('h3', 'met-sub', T('met.inc.ref_tit'), caixa);
    const ul = el('ul', 'met-refs', undefined, caixa);
    // em ordem alfabética; as do T32 vieram do parecer estatístico, aprovadas pelo autor (parecer/REFERENCIAS-PROPOSTAS.md)
    for (const r of ['barnett', 'bester', 'cameron', 'cameron_miller', 'carter', 'duncan', 'freedman', 'goodman', 'goodman1959', 'holm', 'king',
      'mackinnon_webb', 'mnw', 'nosek', 'plescia', 'robinson', 'romero', 'rubin', 'solon', 'spiegelhalter1', 'spiegelhalter2',
      'spiegelhalter2012', 'webb', 'xia']) html(ul, 'li', '', 'met.ref.' + r + '.html');
  })();

  // ======================= Limites do estudo =======================
  (function limites() {
    const caixa = $('#met-limites');
    P(caixa, 'met-intro', T('met.limites.intro'));
    const ol = el('ul', 'met-limites', undefined, caixa);
    const vals = { n05: nota('N05'), n11: nota('N11'), n17: nota('N17'), n19: nota('N19'), n22: nota('N22'), comentarios: link('#comentarios', T('met.lim.comentarios')) };
    for (let i = 1; T.tem('met.lim.' + i); i++) P(el('li', '', undefined, ol), '', T.f('met.lim.' + i, vals));
  })();

  // ======================= Notas sobre os dados =======================
  // Os valores de cada nota: dos dados quando estão neles; os outros, do NOTAS.md (registros do T04 e do T05).
  const mi1 = v => fmt.miAbs(v, 1);
  const sinal = v => fmt.intSinal(v);
  const nomeMun = m => T('mun.nome', { nome: m.nome, uf: m.uf });
  const dL = m => m.L2 - m.L1, dF = m => m.F2 - m.F1;
  const semCap = MUN.filter(m => dL(m) + dF(m) <= 0);
  const capFora = MUN.filter(m => dL(m) + dF(m) > 0 && (dL(m) < 0 || dF(m) < 0));
  const ufsLista = f => T.lista(D.ufs.filter(f).map(u => u.nome));
  const ds = m => 100 * m.L2 / (m.L2 + m.F2) - 100 * m.L1 / (m.L1 + m.F1);
  const flavioSubiu = doBrasil.filter(m => ds(m) < 0).length;
  // o município em que a variação da fatia é negativa, mas a base (4 casas) mostra zero (nota N18)
  const quaseZero = doBrasil.filter(m => ds(m) < 0 && ds(m) > -0.00005);
  const PORTE = [1, 2, 3, 4, 5].map(k => T('met.notas.faixa', { faixa: T('mun.porte' + k), n: fmt.int(doBrasil.filter(m => m.porte === k).length) }));
  const totalEst = 3 * D.por_lugar.length;
  const ECO = D.ecologica.brasil.R;
  const VAL = {
    N01: () => { const c = doBrasil.reduce((a, m) => a + m.C1, 0); return { vv: mi1(207038240), c: mi1(c), r: nf(207038240 / c, 2) }; },
    N02: () => ({ ac: fmt.int(145244), acp: fmt.pct(16.6, 1) }),
    N03: () => ({ data: T.data('2026-10-08'), n: fmt.int(274411) }),
    N04: () => ({ n: fmt.int(16884) }),
    N05: () => {
      const muda = MUN.filter(m => m.E1 !== m.E2);
      const maiores = muda.slice().sort((a, b) => Math.abs(b.E2 - b.E1) - Math.abs(a.E2 - a.E1)).slice(0, 3);
      // T32 (m14): os municípios do Brasil e as cidades do exterior contados à parte
      return { e: fmt.int(BR.E1), m: fmt.int(muda.filter(m => m.uf !== 'ZZ').length), ex: fmt.int(muda.filter(m => m.uf === 'ZZ').length), mais: fmt.int(muda.filter(m => m.E2 > m.E1).length), menos: fmt.int(muda.filter(m => m.E2 < m.E1).length),
        maiores: T.lista(maiores.map(m => T('met.notas.mun_dif', { mun: nomeMun(m), dif: sinal(m.E2 - m.E1) }))) };
    },
    N06: () => ({ n: fmt.int(MUN.length - doBrasil.length) }),
    N08: () => ({ cap: String(MUN.filter(m => m.cap === 1).length), faixas: T.lista(PORTE) }),
    N09: () => ({ x: fmt.int(MUN.filter(m => m.L1 + m.F1 === 0 || m.L2 + m.F2 === 0).length), m: fmt.int(semCap.length),
      mb: fmt.int(semCap.filter(m => m.uf !== 'ZZ').length), me: fmt.int(semCap.filter(m => m.uf === 'ZZ').length),
      f: fmt.int(capFora.length) }),
    N10: () => ({ regras: link('#metodo/partidos', T('met.partidos.regras_tit')) }),
    N11: () => ({ data: T.data('2025-11-04'), a: fmt.pct(26.3, 1), b: fmt.pct(26.6, 1), vs: fmt.pct(19.7, 1), mil: fmt.int(1000) }),
    N13: () => ({ o: mi1(BR.O1) }),
    N14: () => ({ m1: fmt.int(doBrasil.length - 1), m2: fmt.int(doBrasil.length), n16: nota('N16') }),
    N15: () => ({ al: fmt.pct(D.h5.senador_estados_fora.AL, 2), pi: fmt.pct(D.h5.senador_estados_fora.PI, 2) }),
    N16: () => ({ criterio: parte('incerteza', 'met.inc.tit'), total: String(totalEst), nd: String(D.nao_deu.length), lista: parte('nao-deu', 'met.nao_deu.tit'),
      l: fmt.pct(100 * ECO.lula, 0), f: fmt.pct(100 * ECO.flavio, 0), n21: nota('N21'), n22: nota('N22') }),
    // T35: as notas dos dados por seção (T27)
    N21: () => ({ n: fmt.int(D.secoes.votos_28), pct: fmt.pct(100 * D.secoes.votos_28 / D.secoes.comparecimento_1t, 3) }),
    N22: () => ({ sec: fmt.int(D.secoes.secoes_total), muda: fmt.int(D.secoes.aptos_mudam) }),
    // T42: as cidades com prefeito no 2º turno de 2024 nas projeções refeitas
    N25: () => ({ cid: fmt.int(D.projecoes.chamadas.filter(c => c[0] === 'prefeito').length) }),
    N17: () => ({ n: fmt.int(PR.length + 1), a: fmt.pct(PR[0].apurado, 2), b0: fmt.pct(60.85, 2), b1: fmt.pct(68.8, 1), m: fmt.int(PR.length) }),
    // a revisão final (27/10): o texto da N19 e da N20 entrou no catálogo
    N19: () => ({ pct: fmt.pct(99.5, 1) }),
    N20: () => ({ tse: fmt.int(5571), ibge: fmt.int(5570) }),
    N18: () => ({ d: nf(0.00006, 5), mun: T.lista(quaseZero.map(nomeMun)), v: fmt.dec(ds(quaseZero[0]), 5), n: fmt.int(flavioSubiu), n1: fmt.int(flavioSubiu - quaseZero.length) }),
  };
  // N09: as UFs sem captura e as com captura fora de 0% a 100%, com os nomes na língua da página
  const ufsN09 = [ufsLista(u => u.codigo !== 'ZZ' && u.cap === null), ufsLista(u => u.codigo !== 'ZZ' && u.cap !== null && (u.cap < 0 || u.cap > 100))];

  // Onde cada nota aparece: as marcas "N08" da leitura, do Explorar e da Apuração ao vivo, já montadas
  function ondeAparece() {
    const onde = {};
    for (const a of $$('.vista:not(.metodo) a[href^="#metodo/nota-"]')) {
      const id = a.getAttribute('href').replace('#metodo/nota-', '');
      const fig = a.closest('figure');
      let href, nome;
      if (fig && fig.querySelector('.fig-n')) {
        const alvo = fig.closest('[id]');
        nome = fig.querySelector('.fig-n').textContent.trim().replace(/[.:]$/, '');
        href = /^explorar-/.test(alvo.id) ? '#explorar/' + alvo.id.slice(9) : /^apuracao-/.test(alvo.id) ? '#apuracao/' + alvo.id.slice(9) : '#' + alvo.id;
      } else if (a.closest('[id^="capitulo-"]')) {
        const n = a.closest('[id^="capitulo-"]').id.slice(9);
        href = '#analise/' + n; nome = T('met.notas.onde_cap', { n });
      } else if (a.closest('.exp-parte')) {
        const s = a.closest('.exp-parte');
        href = '#explorar/' + s.id.replace(/^explorar-/, ''); nome = T('met.notas.onde_explorar', { parte: $('h2', s).textContent });
      } else if (a.closest('[data-vista="apuracao"]')) {
        href = '#apuracao'; nome = T('nav.apuracao');
      } else if (a.closest('#resumo')) {
        href = '#resumo'; nome = T('nav.resumo');
      } else continue;
      const l = onde[id] || (onde[id] = []);
      if (!l.some(x => x.href === href)) l.push({ href, nome });
    }
    return onde;
  }
  (function notas() {
    const intro = $('#met-notas-intro');
    P(intro, 'met-intro', T.f('met.notas.intro', { limites: parte('limites', 'met.limites.tit') }));
    P(intro, 'met-texto met-regra', T.f('met.notas.regra', { n02: nota('N02'), n03: nota('N03') }));
    const onde = ondeAparece();
    const ol = $('#lista-notas-dados');
    for (const n of D.notas) {
      const li = el('li', '', undefined, ol);
      li.id = 'nota-' + n.id; li.tabIndex = -1;
      el('span', 'nd-cod', n.id, li);
      const c = el('div', 'nd-corpo', undefined, li);
      el('h3', 'nd-tit', T('nota.' + n.id), c);
      const vals = VAL[n.id] ? VAL[n.id]() : {};
      for (let k = 1; T.tem(`nt.${n.id}.${k}`); k++) {
        const v = n.id === 'N09' ? Object.assign({}, vals, { ufs: ufsN09[k - 1] }) : vals;
        P(c, '', T.f(`nt.${n.id}.${k}`, v));
      }
      if (onde[n.id]) P(c, 'nd-onde', T.f('met.notas.aparece', { onde: listaNos(onde[n.id].map(o => link(o.href, o.nome))) }));
    }
  })();

  // ======================= Estimativas que não deram =======================
  (function naoDeu() {
    const caixa = $('#met-nao-deu');
    P(caixa, 'met-intro', T.f('met.nao_deu.intro', { total: String(totalEst), nd: String(D.nao_deu.length), n16: nota('N16') }));
    const ul = el('ul', 'met-motivos', undefined, caixa);
    for (const m of ['poucos', 'pequena', 'dispersos', 'fora', 'depende']) P(el('li', '', undefined, ul), '', T.f('met.motivo.' + m));
    // uma linha por fonte e motivo, com os lugares na ordem dos dados (Brasil, regiões, estados)
    const grupos = [];
    for (const l of D.nao_deu) {
      let g = grupos.find(x => x.fonte === l.fonte && x.motivo === l.motivo);
      if (!g) grupos.push(g = { fonte: l.fonte, motivo: l.motivo, lugares: [] });
      g.lugares.push(l.nivel === 'uf' ? NOME_UF[l.lugar] || l.lugar : l.lugar);
    }
    // as fontes na ordem dos capítulos (outros candidatos, comparecimento, brancos e nulos) e os motivos
    // na ordem em que o critério confere (os nomes já vêm na língua da página: estudo.js, localizarDados)
    const fontes = Object.values(D.por_lugar[0].fontes).map(f => f.fonte);
    const PEQUENA = [T('dado.variação pequena do comparecimento'), T('dado.variação pequena dos brancos e nulos'), T('dado.variação pequena dos votos dos outros')];
    // T35: o motivo novo (as duas contas dão lados opostos) fica junto do último, "fora de 0% a 100%"
    const ordemMotivo = m => (m === T('dado.poucos municípios') ? 0 : PEQUENA.includes(m) ? 1 : m === T('dado.resultados muito dispersos') ? 2 : 3);
    grupos.sort((a, b) => fontes.indexOf(a.fonte) - fontes.indexOf(b.fonte) || ordemMotivo(a.motivo) - ordemMotivo(b.motivo));
    const tc = el('div', 'tab-caixa', undefined, caixa);
    const tab = el('table', 'tab met-tab-nao-deu', undefined, tc);
    const hr = el('tr', '', undefined, el('thead', '', undefined, tab));
    for (const k of ['fonte', 'motivo', 'onde']) { const th = el('th', '', T('met.col.' + k), hr); th.scope = 'col'; }
    const tb = el('tbody', '', undefined, tab);
    let ultima = null;
    for (const g of grupos) {
      const tr = el('tr', g.fonte !== ultima ? 'met-nova-fonte' : '', undefined, tb);
      const th = el('th', '', g.fonte !== ultima ? g.fonte : '', tr); th.scope = 'row';
      ultima = g.fonte;
      el('td', '', g.motivo, tr);
      el('td', '', T.lista(g.lugares) + ' (' + g.lugares.length + ')', tr);
    }
    P(caixa, 'met-pe', T('met.nao_deu.pe'));
  })();

  // ======================= Baixar os dados: o repositório (os arquivos vêm de extras.js) =======================
  const dados = $('#dados-baixar');
  if (dados) P(dados, 'met-pe', T.f('met.dados.repo', { passo: parte('passo', 'met.passo.tit') }));

  // ======================= Índice das partes, como no Explorar e na Apuração ao vivo =======================
  const PARTES = [['metodo', 'nav.metodo'], ['passo', 'met.passo.tit'], ['fontes', 'met.fontes.tit'], ['partidos', 'met.partidos.tit'],
    ['incerteza', 'met.inc.tit'], ['limites', 'met.limites.tit'], ['estudos-externos', 'met.ee.tit'], ['metodos-parecidos', 'met.mp.tit'], ['notas-dados', 'met.notas.tit'], ['nao-deu', 'met.nao_deu.tit'],
    ['glossario', 'met.glossario.tit'], ['dados', 'met.dados.tit'], ['sobre', 'met.sobre.tit']];
  if (window.ESTUDO_PARTES) window.ESTUDO_PARTES.indicePartes($('#met-lista-indice'), $('#metodo'),
    PARTES.map(([id, k]) => ({ id, nome: T(k), href: id === 'metodo' ? '#metodo' : '#metodo/' + id })));
})();
