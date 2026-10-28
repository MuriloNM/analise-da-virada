/* Extras de Método e fontes (T25; especificação 7.5 e 7.6): os dados para baixar em CSV, a versão e
   o registro de correções, "Como citar" e "Sobre este estudo". Carregado depois de estudo.js.
   A versão e as correções ficam só aqui (VERSAO), e o "Como citar" é montado a partir delas: uma
   correção nova entra na lista, com a data, e a versão sobe. A lista dos arquivos vem de
   csv/arquivos.js (scripts/csv_estudo.py), com o tamanho de cada arquivo na língua da página; a
   descrição de cada um vem do catálogo ("csv.arq."). Os textos vêm do catálogo da língua da página
   (textos/pt-BR.js, chaves "ext."; T30) e são rascunho: a redação final é do T11 e do T12 (diário, D23).
   "Como citar" fica nas normas como elas são (ABNT e APA): o título e o subtítulo vão na língua da
   página, e a data da ABNT, no formato da norma. */
(function () {
  'use strict';
  const T = window.T;
  // 0.1 foi a versão de trabalho; a 1.0 é a primeira publicada (T25, item 8; sessão sobre-estudo, 27/10)
  const VERSAO = {
    numero: '1.0.3',
    data: '2026-10-27',
    situacao: T('ext.situacao'),
    // { data: 'AAAA-MM-DD', versao: '1.1', oQue: 'chave do catálogo: o que estava errado e o que mudou', onde: '#analise/3',
    //   quem: 'nome de quem avisou, só se a pessoa quiser (D72)' }
    correcoes: [
      // D80: revisão de neutralidade (manchete, linha fina e 33 trechos; docs/analise/revisao/NEUTRALIDADE-2026-10-27.md)
      { data: '2026-10-27', versao: '1.0.1', oQue: 'ext.corr.v101', onde: '#resumo' },
      // T14: "Pergunte aos dados" no Explorar; cada endereço abre na sua língua (pedido do autor, 27/10)
      { data: '2026-10-27', versao: '1.0.2', oQue: 'ext.corr.v102', onde: '#explorar/pergunte' },
      // T14, Proposta 2: o assistente do botão "Pergunte ao estudo" (D82; P36)
      { data: '2026-10-27', versao: '1.0.3', oQue: 'ext.corr.v103', onde: '#explorar/pergunte' },
    ],
  };
  const AUTOR = { nome: 'Murilo Neves de Martins', citacao: 'MARTINS, Murilo Neves de', apa: 'Martins, M. N. de',
    bib: 'Martins, Murilo Neves de', linkedin: 'https://www.linkedin.com/in/murilomartins/' };
  // o repositório público dos dados e dos scripts (T15), e o texto para perguntar ao estudo com uma IA (D75), na língua da página
  const REPO = 'https://github.com/MuriloNM/analise-da-virada';
  const REPO_IA = REPO + '/blob/main/' + T('ext.ia.arquivo');
  const TITULO = T('pag.nome'), SUBTITULO = T('ext.subtitulo');
  const URL = 'https://analise-da-virada.pages.dev/' + T.linguas.find(l => l.codigo === T.lingua).pasta;
  window.ESTUDO_VERSAO = VERSAO;

  const $ = (s, r = document) => r.querySelector(s);
  function el(tag, cls, texto, pai) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (texto !== undefined) e.textContent = texto;
    if (pai) pai.appendChild(e);
    return e;
  }
  function link(pai, href, texto, externo) {
    const a = el('a', '', texto, pai);
    a.href = href;
    if (externo) a.rel = 'noopener';
    return a;
  }
  // os meses abreviados da ABNT (NBR 6023) ficam em português em toda língua: é a norma
  const MESES_ABNT = T('ext.meses_abnt');
  const partes = iso => iso.split('-').map(Number);
  const porExtenso = T.data;
  const abnt = d => `${d.getDate()} ${MESES_ABNT[d.getMonth()]} ${d.getFullYear()}`;
  const tamanho = b => (b >= 1048576 ? T('ext.mb', { n: (b / 1048576).toLocaleString(T.lingua, { maximumFractionDigits: 1 }) })
    : T('ext.kb', { n: Math.max(1, Math.round(b / 1024)).toLocaleString(T.lingua) }));

  // ---------- Baixar os dados ----------
  (function dados() {
    const caixa = $('#dados-baixar');
    if (!caixa) return;
    el('p', '', T('ext.dados.intro'), caixa);
    const lista = el('ul', 'baixar', undefined, caixa);
    // os arquivos na língua da página: csv/ em português, csv/en/ em inglês… (scripts/csv_estudo.py)
    const pasta = T.raiz + 'csv/' + T.linguas.find(l => l.codigo === T.lingua).pasta;
    const n = v => v.toLocaleString(T.lingua);
    const NUMEROS_CSV = { total: n(5757), brasil: n(5571), exterior: n(186) }; // os municípios de municipios.csv
    for (const a of window.ARQUIVOS_CSV || []) {
      const li = el('li', '', undefined, lista);
      const l = link(li, pasta + a.nome, a.nome);
      l.setAttribute('download', '');
      el('span', 'baixar-meta', T('ext.dados.meta', { n: a.linhas.toLocaleString(T.lingua), tamanho: tamanho(a.bytes) }), li);
      el('span', 'baixar-desc', T('csv.arq.' + a.nome.replace(/\.csv$/, ''), NUMEROS_CSV), li);
    }
    const n09 = el('a', '', 'N09'); n09.href = '#metodo/nota-N09';
    const repo = el('a', '', T('pag.repo')); repo.href = REPO;
    el('p', 'baixar-pe', undefined, caixa).append(...T.f('ext.dados.pe', { n09, sep: T('csv.separador'), dec: T('csv.decimal'), repo }));
  })();

  // ---------- Sobre este estudo, versão, correções e como citar ----------
  (function sobre() {
    const caixa = $('#sobre-estudo');
    if (!caixa) return;
    // por que o estudo existe, como foi feito, o nome do autor, os erros e como ajudar, na voz do autor (D72;
    // a ajuda de IA, dita por escolha do autor, P23). O primeiro título fica sob o h2 "Sobre este estudo".
    const parte = (chave, nos) => {
      el('h3', 'sobre-tit', T(chave + '.tit'), caixa);
      el('p', '', undefined, caixa).append(...(nos || [T(chave)]));
    };
    parte('ext.sobre.porque');
    parte('ext.sobre.como');
    if (T('ext.sobre.lingua')) el('p', '', T('ext.sobre.lingua'), caixa); // as palavras da tradução (só nas outras línguas)
    const perfil = el('a', '', T('ext.sobre.perfil')); perfil.href = AUTOR.linkedin; perfil.rel = 'noopener';
    parte('ext.sobre.nome', T.f('ext.sobre.nome', { nome: el('b', '', AUTOR.nome), perfil }));
    const dados = el('a', '', T('ext.sobre.dados')); dados.href = '#metodo/dados';
    const passo = el('a', '', T('ext.sobre.passo')); passo.href = '#metodo/passo';
    const repo = el('a', '', T('ext.sobre.repo')); repo.href = REPO;
    const ia = el('a', '', T('ext.sobre.ia_texto')); ia.href = REPO_IA;
    parte('ext.sobre.erros', T.f('ext.sobre.erros', { dados, passo, repo, ia }));
    // a caixa de mensagem abre por este botão também (contato.js, carregado depois, liga todo [data-abrir-contato])
    const escrever = el('button', 'bt-inline', T('ext.sobre.escrever'));
    escrever.type = 'button'; escrever.dataset.abrirContato = ''; escrever.setAttribute('aria-haspopup', 'dialog');
    const linkedin = el('a', '', T('ext.sobre.linkedin')); linkedin.href = AUTOR.linkedin; linkedin.rel = 'noopener';
    parte('ext.sobre.ajudar', T.f('ext.sobre.ajudar', { escrever, linkedin }));

    el('h3', 'sobre-tit', T('ext.versao.tit'), caixa);
    const v = el('p', '', undefined, caixa);
    v.append(...T.f('ext.versao', { versao: el('b', '', T('ext.versao.n', { n: VERSAO.numero })), data: porExtenso(VERSAO.data), situacao: VERSAO.situacao }));
    if (VERSAO.correcoes.length) {
      const ol = el('ol', 'correcoes', undefined, caixa);
      for (const c of VERSAO.correcoes) {
        const li = el('li', '', undefined, ol);
        li.append(el('b', '', T('ext.correcao', { data: porExtenso(c.data), versao: c.versao })), T(c.oQue) + ' ');
        if (c.quem) li.append(T('ext.correcao_quem', { quem: c.quem }));
        if (c.onde) link(li, c.onde, T('ext.correcao_onde'));
      }
    } else {
      el('p', '', T('ext.sem_correcao'), caixa);
    }
    // a impressão digital de cada PDF desta versão: pdf.js preenche, depois de ler pdf/arquivos.js
    el('div', '', undefined, caixa).id = 'pdf-sha';

    el('h3', 'sobre-tit', T('ext.citar.tit'), caixa);
    const [a, m, d] = partes(VERSAO.data);
    const hoje = new Date();
    const formas = [
      ['ABNT', T('ext.citar.abnt', { autor: AUTOR.citacao, titulo: TITULO, sub: SUBTITULO, versao: VERSAO.numero, data: abnt(new Date(a, m - 1, d)), url: URL, acesso: abnt(hoje) })],
      ['APA', T('ext.citar.apa', { autor: AUTOR.apa, ano: a, titulo: TITULO, sub: SUBTITULO, versao: VERSAO.numero, url: URL })],
      ['BibTeX', `@misc{martins${a}virada,\n  author = {${AUTOR.bib}},\n  title = {${TITULO}: ${SUBTITULO}},\n  year = {${a}},\n  version = {${VERSAO.numero}},\n  url = {${URL}},\n  urldate = {${hoje.toISOString().slice(0, 10)}}\n}`],
    ];
    const dl = el('dl', 'citar', undefined, caixa);
    formas.forEach(([nome, texto], i) => {
      const linha = el('div', 'citar-linha', undefined, dl);
      el('dt', '', nome, linha);
      const dd = el('dd', '', undefined, linha);
      const pre = el('pre', 'citar-texto' + (nome === 'BibTeX' ? ' citar-bib' : ''), texto, dd);
      pre.id = 'citar-' + i;
      const b = el('button', 'bt-copiar', T('ext.copiar'), dd);
      b.type = 'button';
      b.setAttribute('aria-describedby', pre.id);
      const aviso = el('span', 'citar-aviso', '', dd);
      aviso.setAttribute('role', 'status');
      b.addEventListener('click', () => copiar(texto, pre, aviso));
    });
  })();

  function copiar(texto, pre, aviso) {
    const ok = () => { aviso.textContent = T('ext.copiado'); setTimeout(() => { aviso.textContent = ''; }, 2500); };
    const selecionar = () => {
      // sem permissão para a área de transferência: seleciona o texto e tenta o jeito antigo de copiar
      const r = document.createRange(); r.selectNodeContents(pre);
      const s = getSelection(); s.removeAllRanges(); s.addRange(r);
      let copiou = false;
      try { copiou = document.execCommand('copy'); } catch (_) {}
      if (copiou) ok(); else aviso.textContent = T('ext.selecionado');
    };
    if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(texto).then(ok, selecionar);
    else selecionar();
  }
})();
