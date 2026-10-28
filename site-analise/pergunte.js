/* "Pergunte aos dados" (T14), a primeira parte do Explorar (#explorar/pergunte). O leitor monta a
   pergunta escolhendo as partes sublinhadas, e a resposta sai, em frases, dos mesmos números dos
   capítulos (dados.js), arredondados uma vez na hora de mostrar (D25). Os dois candidatos têm sempre
   o mesmo tratamento: toda resposta sobre um lugar fala dos dois, e todo ranking pode ser pedido
   para um ou para o outro (seção 1.1 da especificação).
   A caixa da pergunta escrita só aparece quando a função do servidor (/api/pergunta, em
   servidor/functions/) responde que está aberta. Ela manda o texto a um serviço de IA, que só
   devolve qual das perguntas prontas foi feita e com que lugar; a página preenche as escolhas com
   isso e responde com os dados, como se o leitor tivesse escolhido. A IA nunca escreve número nem
   frase da resposta. Os textos vêm do catálogo (chaves "exp.perg."). */
window.PERGUNTE = function (X) {
  'use strict';
  const { D, G, BR, UFS, NOME_UF, REGIAO_UF, doBrasil, nomeMun, el, B, P, nd } = X;
  const { fmt } = G, T = window.T;
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const pai = document.getElementById('exp-pergunte');
  if (!pai) return;
  const semAcento = s => String(s).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().trim();

  // ---------- Os lugares: Brasil, regiões, estados e municípios, com os mesmos campos ----------
  const REGIOES = D.regioes.filter(r => r.codigo !== 'EX');
  const lugarBR = { tipo: 'pais', id: 'BR', u: BR, nome: BR.nome };
  const lugaresReg = REGIOES.map(r => ({ tipo: 'regiao', id: 'R-' + r.codigo, u: r, nome: r.nome }));
  const lugaresUf = UFS.slice().sort((a, b) => a.nome.localeCompare(b.nome, T.lingua))
    .map(u => ({ tipo: 'uf', id: 'U-' + u.codigo, u, nome: u.nome }));
  let lugaresMun = null;
  const municipiosL = () => lugaresMun || (lugaresMun = doBrasil().map(m => ({ tipo: 'mun', id: 'M-' + m.uf + '-' + m.nome, u: m, nome: nomeMun(m) })));
  const conteiners = [lugarBR, ...lugaresReg, ...lugaresUf];
  const porId = id => conteiners.find(l => l.id === id) || municipiosL().find(l => l.id === id) || null;
  /** Os municípios dentro de um lugar (o exterior fica fora das listas de municípios). */
  const munDe = l => doBrasil().filter(m => l.tipo === 'pais' || (l.tipo === 'regiao' && REGIAO_UF[m.uf] === l.nome) ||
    (l.tipo === 'uf' && m.uf === l.u.codigo) || (l.tipo === 'mun' && m === l.u));
  const ufsDe = l => UFS.filter(u => l.tipo === 'pais' || (l.tipo === 'regiao' && u.regiao === l.nome));

  /** Acha o lugar pelo nome escrito (o que a IA devolve, ou o que o leitor digita): Brasil, região,
   *  estado (nome ou sigla) ou município, com a UF quando houver dois com o mesmo nome. */
  function acharLugar(nome, uf) {
    const q = semAcento(nome || ''), u = String(uf || '').toUpperCase().trim();
    if (!q || ['brasil', 'brazil', 'pais', 'o pais', 'country', 'o brasil'].includes(q)) return lugarBR;
    const c = conteiners.find(l => semAcento(l.nome) === q || (l.tipo === 'uf' && l.u.codigo.toLowerCase() === q) ||
      (l.tipo === 'regiao' && semAcento(l.u.regiao || '') === q));
    if (c && !(c.tipo === 'uf' && u && u !== c.u.codigo && municipiosL().some(m => m.u.uf === u && semAcento(m.u.nome) === q))) return c;
    const ms = municipiosL().filter(m => semAcento(m.u.nome) === q);
    if (!ms.length) {
      if (c) return c;
      // o começo do nome de um estado ou região, quando só um serve ("Minas" → Minas Gerais)
      const ini = conteiners.filter(l => semAcento(l.nome).startsWith(q + ' ') && (!u || l.tipo !== 'uf' || l.u.codigo === u));
      return ini.length === 1 ? ini[0] : null;
    }
    return ms.find(m => m.u.uf === u) || ms.slice().sort((a, b) => b.u.E1 - a.u.E1)[0];
  }

  // ---------- Campos: a escolha sublinhada dentro da frase e a caixa de lugar ----------
  /** Escolha dentro da frase (select sem rótulo visível; o rótulo vai para o leitor de tela). */
  let nCampo = 0;
  function escolhaNaFrase(rotulo, opcoes, aoMudar) {
    const s = el('select', 'perg-sel');
    s.id = 'perg-sel-' + (++nCampo);
    s.setAttribute('aria-label', rotulo);
    for (const [v, t] of opcoes) el('option', '', t, s).value = v;
    s.addEventListener('change', () => { ajustar(s); aoMudar(s.value); });
    return s;
  }
  /** A escolha na frase fica da largura do texto escolhido, e não do mais longo da lista. */
  const regua = el('span', 'perg-sel perg-regua');
  regua.setAttribute('aria-hidden', 'true');
  function ajustar(s) {
    if (!s.isConnected || !s.selectedOptions[0]) return;
    regua.textContent = s.selectedOptions[0].textContent;
    s.parentNode.append(regua); // mede com a letra da frase
    const w = regua.getBoundingClientRect().width;
    regua.remove();
    if (w) s.style.width = Math.ceil(w) + 'px';
  }
  /** Lugar com Brasil, regiões e estados (para rankings e contagens). */
  function seletorConteiner(pai, rotulo, aoMudar) {
    const c = el('label', 'exp-campo', undefined, pai);
    el('span', 'exp-campo-rot', rotulo, c);
    const s = el('select', '', undefined, c);
    s.id = 'perg-sel-' + (++nCampo);
    el('option', '', lugarBR.nome, s).value = lugarBR.id;
    for (const [g, ls] of [[T('exp.perg.grupo.regioes'), lugaresReg], [T('exp.perg.grupo.estados'), lugaresUf]]) {
      const og = el('optgroup', '', undefined, s); og.label = g;
      for (const l of ls) el('option', '', l.nome, og).value = l.id;
    }
    s.addEventListener('change', () => aoMudar(porId(s.value)));
    return { campo: c, select: s, valor: () => porId(s.value), por: l => { s.value = l.id; } };
  }
  /** Caixa de lugar com busca em todos (Brasil, regiões, estados e municípios), no mesmo desenho da
   *  busca de municípios do Explorar. */
  function caixaLugar(pai, rotulo, inicial, aoEscolher) {
    const id = 'perg-lugar-' + (++nCampo);
    const c = el('div', 'perg-lugar', undefined, pai);
    const lab = el('label', 'exp-campo-rot', rotulo, c); lab.htmlFor = id;
    const bx = el('div', 'busca', undefined, c);
    const entrada = el('input', 'campo perg-campo', undefined, bx);
    Object.assign(entrada, { id, type: 'search', placeholder: T('exp.perg.lugar_placeholder'), autocomplete: 'off', spellcheck: false });
    entrada.setAttribute('role', 'combobox'); entrada.setAttribute('aria-autocomplete', 'list');
    entrada.setAttribute('aria-expanded', 'false'); entrada.setAttribute('aria-controls', id + '-lista');
    const lista = el('ul', 'busca-lista', undefined, bx);
    lista.id = id + '-lista'; lista.setAttribute('role', 'listbox'); lista.setAttribute('aria-label', T('exp.perg.lugares_aria')); lista.hidden = true;
    let atual = inicial, achados = [], ativo = -1, indice = null;
    entrada.value = atual.nome;
    const fechar = () => { lista.hidden = true; entrada.setAttribute('aria-expanded', 'false'); entrada.removeAttribute('aria-activedescendant'); ativo = -1; };
    const por = l => { atual = l; entrada.value = l.nome; fechar(); };
    function escolher(l) { por(l); aoEscolher(l); }
    function marcar(i) {
      ativo = i;
      $$('li', lista).forEach((li, j) => li.setAttribute('aria-selected', j === i ? 'true' : 'false'));
      if (i >= 0) entrada.setAttribute('aria-activedescendant', id + '-op-' + i);
    }
    const tipo = l => (l.tipo === 'mun' ? l.u.uf : T('exp.perg.tipo.' + l.tipo));
    entrada.addEventListener('input', () => {
      const q = semAcento(entrada.value);
      if (q.length < 2) { fechar(); return; }
      if (!indice) indice = [...conteiners, ...municipiosL()].map(l => ({ l, n: semAcento(l.tipo === 'mun' ? l.u.nome : l.nome) }));
      const comeca = [], palavra = [], contem = [];
      for (const x of indice) {
        if (x.n.startsWith(q) || (x.l.tipo === 'uf' && x.l.u.codigo.toLowerCase() === q)) comeca.push(x.l);
        else if (x.n.includes(' ' + q)) palavra.push(x.l);
        else if (x.n.includes(q)) contem.push(x.l);
      }
      // Brasil, regiões e estados antes dos municípios; os municípios, do maior para o menor
      const ordem = (a, b) => (a.tipo === 'mun') - (b.tipo === 'mun') || (a.tipo === 'mun' ? b.u.E1 - a.u.E1 : 0);
      achados = [...comeca.sort(ordem), ...palavra.sort(ordem), ...contem.sort(ordem)].slice(0, 8);
      lista.replaceChildren();
      if (!achados.length) el('li', 'busca-vazio', T('exp.perg.lugar_nenhum'), lista).setAttribute('aria-disabled', 'true');
      achados.forEach((l, i) => {
        const li = el('li', '', undefined, lista);
        li.id = id + '-op-' + i; li.setAttribute('role', 'option');
        el('span', '', l.tipo === 'mun' ? l.u.nome : l.nome, li); el('span', 'busca-uf', tipo(l), li);
        li.addEventListener('pointerdown', ev => { ev.preventDefault(); escolher(l); });
      });
      lista.hidden = false; entrada.setAttribute('aria-expanded', 'true');
      marcar(achados.length ? 0 : -1);
    });
    entrada.addEventListener('keydown', ev => {
      if (lista.hidden || !achados.length) return;
      if (ev.key === 'ArrowDown') { ev.preventDefault(); marcar((ativo + 1) % achados.length); }
      else if (ev.key === 'ArrowUp') { ev.preventDefault(); marcar((ativo - 1 + achados.length) % achados.length); }
      else if (ev.key === 'Enter') { ev.preventDefault(); escolher(achados[Math.max(0, ativo)]); }
      else if (ev.key === 'Escape') fechar();
    });
    // saiu sem escolher: volta o nome do lugar que está valendo
    entrada.addEventListener('blur', () => setTimeout(() => { fechar(); entrada.value = atual.nome; }, 120));
    return { campo: c, valor: () => atual, por };
  }

  // ---------- A pergunta: quatro modelos, cada um com as suas escolhas ----------
  const q = { modelo: 'lugar', a: lugarBR, b: lugaresUf.find(l => l.u.codigo === 'SP') || lugaresUf[0], cont: lugarBR,
    cand: 'lula', medida: 'votos', nivel: 'municipios', n: 10 };
  const MODELOS = ['lugar', 'ranking', 'comparar', 'trocou'];

  const escolhaModelo = el('div', 'botoes-escolha perg-modelos', undefined, pai);
  escolhaModelo.setAttribute('role', 'group'); escolhaModelo.setAttribute('aria-label', T('exp.perg.modelos_aria'));
  for (const m of MODELOS) {
    const b = el('button', '', T('exp.perg.m.' + m), escolhaModelo);
    b.type = 'button'; b.dataset.v = m;
    b.addEventListener('click', () => { if (q.modelo !== m) { q.modelo = m; montar(); responder(); } });
  }
  const frase = el('p', 'perg-frase', undefined, pai);
  frase.id = 'perg-frase';
  const campos = el('div', 'exp-recorte perg-campos', undefined, pai);
  const caixaA = caixaLugar(campos, T('exp.perg.campo.lugar'), q.a, l => { q.a = l; responder(); });
  const caixaB = caixaLugar(campos, T('exp.perg.campo.lugar2'), q.b, l => { q.b = l; responder(); });
  const cont = seletorConteiner(campos, T('exp.perg.campo.lugar'), l => { q.cont = l; responder(); });
  const quantos = (() => {
    const c = el('label', 'exp-campo', undefined, campos);
    el('span', 'exp-campo-rot', T('exp.perg.campo.quantos'), c);
    const s = el('select', '', undefined, c);
    s.id = 'perg-sel-' + (++nCampo);
    for (const n of [5, 10, 20]) el('option', '', fmt.int(n), s).value = String(n);
    s.value = '10';
    s.addEventListener('change', () => { q.n = +s.value; responder(); });
    return { campo: c, select: s };
  })();
  const selCand = escolhaNaFrase(T('exp.perg.aria_cand'), [['lula', T('exp.perg.op.lula')], ['flavio', T('exp.perg.op.flavio')]], v => { q.cand = v; responder(); });
  const selMedida = escolhaNaFrase(T('exp.perg.aria_medida'), [['votos', T('exp.perg.op.votos')], ['parte', T('exp.perg.op.parte')]], v => { q.medida = v; responder(); });
  const selNivel = escolhaNaFrase(T('exp.perg.aria_nivel'), [['municipios', T('exp.perg.op.municipios')], ['estados', T('exp.perg.op.estados')]], v => { q.nivel = v; responder(); });

  function montar() {
    $$('button', escolhaModelo).forEach(b => b.setAttribute('aria-pressed', b.dataset.v === q.modelo ? 'true' : 'false'));
    frase.replaceChildren(...T.f('exp.perg.q.' + q.modelo, { cand: selCand, medida: selMedida, nivel: selNivel }));
    caixaA.campo.hidden = !['lugar', 'comparar'].includes(q.modelo);
    caixaB.campo.hidden = q.modelo !== 'comparar';
    cont.campo.hidden = !['ranking', 'trocou'].includes(q.modelo);
    quantos.campo.hidden = q.modelo !== 'ranking';
    for (const s of [selCand, selMedida, selNivel]) ajustar(s);
  }

  // ---------- As respostas ----------
  const resp = el('div', 'perg-resp', undefined, pai);
  resp.setAttribute('aria-live', 'polite');
  resp.setAttribute('aria-labelledby', 'perg-frase');
  const quem = c => T('exp.perg.quem.' + c);
  /** As frases sobre um lugar: votos de cada um, parte entre os dois, quem ficou à frente, abstenção. */
  function frasesLugar(caixa, u) {
    P(caixa, 'perg-texto', ...T.f('exp.perg.r.votos', {
      l1: B(fmt.int(u.L1)), l2: B(fmt.int(u.L2)), dl: fmt.intSinal(u.dL),
      f1: B(fmt.int(u.F1)), f2: B(fmt.int(u.F2)), df: fmt.intSinal(u.dF) }));
    if (u.s1 !== null && u.s2 !== null) P(caixa, 'perg-texto', ...T.f('exp.perg.r.parte', {
      s1: B(fmt.pct(u.s1, 1)), s2: B(fmt.pct(u.s2, 1)), ds: fmt.pp(u.ds, 1),
      t1: B(fmt.pct(100 - u.s1, 1)), t2: B(fmt.pct(100 - u.s2, 1)), dt: fmt.pp(-u.ds, 1) }));
    const frente = (t, m) => (m === 0 ? T('exp.perg.r.empate' + t)
      : T('exp.perg.r.frente' + t, { quem: quem(m > 0 ? 'lula' : 'flavio'), m: fmt.int(Math.abs(m)) }));
    P(caixa, 'perg-texto', frente(1, u.M1) + ' ' + frente(2, u.M2));
    P(caixa, 'perg-texto', ...T.f('exp.perg.r.abst', { a1: B(fmt.pct(u.a1, 1)), a2: B(fmt.pct(u.a2, 1)), da: fmt.pp(u.da, 1) }));
  }
  /** De onde vem a resposta, e onde ver mais. */
  function fonte(caixa, l, ver) {
    const p = P(caixa, 'exp-nota perg-fonte', ...T.f('exp.perg.fonte', { n05: nd('N05'), n06: l && l.tipo === 'pais' ? nd('N06') : '' }));
    for (const [href, k] of ver) { p.append(' '); const a = el('a', '', T(k), p); a.href = href; }
  }
  const verDe = l => (l.tipo === 'mun' ? [['#explorar/municipios', 'exp.perg.ver_mun']] : [['#explorar/estados', 'exp.perg.ver_estados']]);

  function rLugar(c) {
    el('h3', 'perg-resp-tit', q.a.nome, c);
    frasesLugar(c, q.a.u);
    fonte(c, q.a, [...verDe(q.a), ['#metodo/dados', 'exp.perg.ver_dados']]);
  }
  function rComparar(c) {
    for (const l of [q.a, q.b]) { el('h3', 'perg-resp-tit', l.nome, c); frasesLugar(c, l.u); }
    if (q.a.u.ds !== null && q.b.u.ds !== null && q.a !== q.b) P(c, 'perg-texto perg-fecho', ...T.f('exp.perg.r.comparar', {
      a: q.a.nome, b: q.b.nome, da: B(fmt.pp(q.a.u.ds, 1)), db: B(fmt.pp(q.b.u.ds, 1)) }));
    fonte(c, q.a.tipo === 'pais' ? q.a : q.b, [...new Map([...verDe(q.a), ...verDe(q.b)]).entries(), ['#metodo/dados', 'exp.perg.ver_dados']]);
  }
  function rRanking(c) {
    const l = q.cont, lula = q.cand === 'lula', votos = q.medida === 'votos', mun = q.nivel === 'municipios';
    const titId = 'perg-rank-tit';
    el('h3', 'perg-resp-tit', T('exp.perg.r.rank_tit', { lugar: l.nome, cand: quem(q.cand), medida: T('exp.perg.r.rank_medida.' + q.medida) }), c).id = titId;
    if (!mun && l.tipo === 'uf') { P(c, 'exp-vazio', T('exp.perg.r.rank_uf_em_uf')); return; }
    const piso = votos ? () => true : u => u.E1 > 10000; // piso dos rankings em pontos (HIPOTESES 5.1)
    const v = votos ? u => (lula ? u.dL : u.dF) : u => (lula ? u.ds : -u.ds);
    const ls = (mun ? munDe(l) : ufsDe(l)).filter(u => (!mun || piso(u)) && v(u) !== null && v(u) > 0)
      .sort((a, b) => v(b) - v(a)).slice(0, q.n);
    if (!ls.length) { P(c, 'exp-vazio', T('exp.perg.r.rank_vazio')); return; }
    const t1 = votos ? u => (lula ? u.L1 : u.F1) : u => (lula ? u.s1 : 100 - u.s1);
    const t2 = votos ? u => (lula ? u.L2 : u.F2) : u => (lula ? u.s2 : 100 - u.s2);
    const f = votos ? fmt.int : x => fmt.pct(x, 1), fv = votos ? fmt.intSinal : x => fmt.pp(x, 1);
    P(c, 'perg-texto', T.p(mun ? 'exp.perg.r.rank_mun' : 'exp.perg.r.rank_uf', ls.length, { n: fmt.int(ls.length) }) +
      (mun && !votos ? ' ' + T('exp.perg.r.rank_piso') : ''));
    const caixaTab = el('div', '', undefined, c);
    G.tabela(caixaTab, { ordenavel: false, linhas: ls, colunas: [
        { t: T(mun ? 'tab.municipio' : 'tab.estado'), v: u => u.nome },
        ...(mun ? [{ t: T('tab.uf'), v: u => u.uf }] : []),
        { t: T('g.turno1'), num: true, v: t1, f }, { t: T('g.turno2'), num: true, v: t2, f },
        { t: T('tab.variacao'), num: true, v, f: fv }] });
    // o título da resposta já diz o que a tabela é; ele serve de nome da tabela para o leitor de tela
    const tab = caixaTab.querySelector('table');
    if (tab) tab.setAttribute('aria-labelledby', titId);
    fonte(c, null, [[mun ? '#explorar/municipios' : '#explorar/estados', mun ? 'exp.perg.ver_mun' : 'exp.perg.ver_estados']]);
  }
  function rTrocou(c) {
    const l = q.cont, ms = munDe(l);
    el('h3', 'perg-resp-tit', l.nome, c);
    let fl = 0, lf = 0, cl = 0, cf = 0, emp = 0;
    for (const m of ms) {
      if (m.M1 === 0 || m.M2 === 0) emp++;
      else if (m.M1 < 0 && m.M2 > 0) fl++;
      else if (m.M1 > 0 && m.M2 < 0) lf++;
      else if (m.M1 > 0) cl++;
      else cf++;
    }
    P(c, 'perg-texto', ...T.f('exp.perg.r.trocou', { n: B(fmt.int(ms.length)), fl: B(fmt.int(fl)), lf: B(fmt.int(lf)) }));
    P(c, 'perg-texto', ...T.f('exp.perg.r.ficou', { k: B(fmt.int(cl + cf)), cl: B(fmt.int(cl)), cf: B(fmt.int(cf)) }));
    if (emp) P(c, 'perg-texto', T.p('exp.perg.r.empates', emp, { n: fmt.int(emp) }));
    fonte(c, null, [['#explorar/municipios', 'exp.perg.ver_mun']]);
  }
  const R = { lugar: rLugar, ranking: rRanking, comparar: rComparar, trocou: rTrocou };
  function responder() {
    G.dicaEsconder && G.dicaEsconder();
    resp.replaceChildren();
    R[q.modelo](el('div', 'perg-resp-in', undefined, resp));
  }

  /** Põe na tela a pergunta que a IA entendeu, como se o leitor tivesse escolhido. Devolve o lugar
   *  que não foi achado, se houver, para a caixa da pergunta escrita avisar. */
  function aplicar(p) {
    if (!MODELOS.includes(p.modelo)) return { erro: 'modelo' };
    const a = acharLugar(p.lugar, p.uf), b = p.modelo === 'comparar' ? acharLugar(p.lugar2, p.uf2) : null;
    if (!a) return { naoAchou: p.lugar };
    if (p.modelo === 'comparar' && !b) return { naoAchou: p.lugar2 };
    q.modelo = p.modelo;
    if (p.modelo === 'lugar' || p.modelo === 'comparar') { q.a = a; caixaA.por(a); }
    if (b) { q.b = b; caixaB.por(b); }
    if (p.modelo === 'ranking' || p.modelo === 'trocou') {
      // ranking e contagem são sobre Brasil, região ou estado; um município leva ao estado dele
      const c = a.tipo === 'mun' ? lugaresUf.find(l => l.u.codigo === a.u.uf) : a;
      q.cont = c; cont.por(c);
    }
    if (p.candidato === 'lula' || p.candidato === 'flavio') q.cand = selCand.value = p.candidato;
    if (p.medida === 'votos' || p.medida === 'parte') q.medida = selMedida.value = p.medida;
    if (p.nivel === 'municipios' || p.nivel === 'estados') q.nivel = selNivel.value = p.nivel;
    if ([5, 10, 20].includes(p.n)) { q.n = p.n; quantos.select.value = String(p.n); }
    montar(); responder();
    return {};
  }

  // ---------- A pergunta escrita (só quando o servidor está aberto) ----------
  const API = '/api/pergunta'; // a mesma para todas as línguas (/ e /en/)
  function caixaEscrita() {
    const s = el('section', 'exp-sub perg-escrita', undefined, pai);
    s.hidden = true;
    el('h3', '', T('exp.perg.livre.tit'), s);
    const f = el('form', 'perg-form', undefined, s);
    const lab = el('label', 'exp-campo-rot', T('exp.perg.livre.label'), f); lab.htmlFor = 'perg-livre';
    const linha = el('div', 'perg-linha', undefined, f);
    const ent = el('input', 'campo', undefined, linha);
    Object.assign(ent, { id: 'perg-livre', type: 'text', maxLength: 300, placeholder: T('exp.perg.livre.placeholder'), autocomplete: 'off' });
    const bt = el('button', 'bt-enviar', T('exp.perg.livre.enviar'), linha); bt.type = 'submit';
    const sit = el('p', 'perg-situacao', undefined, s); sit.setAttribute('role', 'status'); sit.setAttribute('aria-live', 'polite');
    P(s, 'exp-nota', ...T.f('exp.perg.livre.aviso', { priv: (() => { const a = el('a', '', T('exp.perg.livre.priv')); a.href = 'privacidade/'; return a; })() }));
    const dizer = (k, v) => { sit.textContent = T(k, v); };
    f.addEventListener('submit', async ev => {
      ev.preventDefault();
      const texto = ent.value.trim();
      if (texto.split(/\s+/).length < 2) { dizer('exp.perg.livre.curta'); return; }
      bt.disabled = true; dizer('exp.perg.livre.esperando');
      try {
        const r = await fetch(API, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ texto, lingua: T.lingua }) });
        const j = await r.json().catch(() => ({}));
        if (j.situacao === 'cota') { dizer('exp.perg.livre.cota'); return; }
        if (j.situacao === 'limite') { dizer('exp.perg.livre.limite'); return; }
        if (!r.ok || !j.pergunta) { dizer('exp.perg.livre.erro'); return; }
        const p = j.pergunta;
        if (p.modelo === 'fora') { dizer('exp.perg.livre.fora.' + (['opiniao', 'causa', 'previsao'].includes(p.motivo) ? p.motivo : 'outra')); return; }
        const res = aplicar(p);
        if (res.naoAchou !== undefined) { dizer('exp.perg.livre.lugar_nao', { lugar: res.naoAchou || '' }); return; }
        if (res.erro) { dizer('exp.perg.livre.fora.outra'); return; }
        dizer('exp.perg.livre.entendi', { leitor: T('exp.perg.livre.quem_' + (j.nivel === 'claude' ? 'claude' : 'cf')) });
        frase.scrollIntoView({ behavior: X.semMovimento() ? 'auto' : 'smooth', block: 'start' });
      } catch (_) { dizer('exp.perg.livre.erro'); }
      finally { bt.disabled = false; }
    });
    // a caixa só aparece quando o servidor diz que está aberta (fora do ar, ou na cópia local, fica escondida)
    if (!/^https?:$/.test(location.protocol) || 'pdf' in Object.fromEntries(new URLSearchParams(location.search))) return;
    fetch(API, { headers: { Accept: 'application/json' } }).then(r => (r.ok ? r.json() : null)).then(j => { if (j && j.aberta) s.hidden = false; }).catch(() => {});
  }

  montar(); responder(); caixaEscrita();
  return { aplicar, acharLugar };
};
