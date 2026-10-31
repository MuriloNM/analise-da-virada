/* Comentários, no fim do estudo (T16; especificação 7.7; o único lugar para comentar, D31).
   - As "Regras dos comentários" saem do catálogo e aparecem sempre, mesmo com a caixa fechada.
   - Quando a seção chega perto da tela, a página pergunta à função /api/comentarios se a caixa está
     aberta e pede a lista pública. Fora do ar, na cópia local sem a função e no modo PDF, a caixa fica
     como no HTML: fechada, com o aviso para usar "Escrever ao autor".
   - Aberta: aparecem o nome ou apelido, o e-mail opcional e o aviso da moderação. A proteção contra
     robôs (Turnstile, do Cloudflare) só é carregada quando a pessoa começa a escrever.
   - A lista: os comentários liberados com o texto e a "Resposta do autor"; os em análise só como aviso,
     sem o texto. Quem escreveu guarda neste navegador o número, o texto e a chave do próprio
     comentário (localStorage), e por isso vê o texto e o motivo enquanto ele está em análise e pode
     apagá-lo. Nada disso sai do aparelho.
   - O texto do leitor entra na página só como texto (textContent), nunca como HTML.
   Os textos vêm do catálogo da língua da página (chaves "com."; T30). */
(function () {
  'use strict';
  const T = window.T;
  const API = '/api/comentarios';
  const secao = document.getElementById('comentarios');
  const form = secao && secao.querySelector('form[data-comentario]');
  if (!form) return;
  const lista = document.getElementById('com-lista');
  const situacao = form.querySelector('.comentario-situacao');
  const enviar = form.querySelector('.bt-enviar');
  const CATEGORIAS = ['xingamento', 'ataque', 'extremismo', 'odio', 'fraude', 'spam', 'dados'];
  const GUARDA = 'analise-comentarios', GUARDA_NOME = 'analise-comentario-nome';

  function el(tag, cls, texto, pai) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (texto !== undefined) e.textContent = texto;
    if (pai) pai.appendChild(e);
    return e;
  }
  const ler = (k, padrao) => { try { const v = localStorage.getItem(k); return v === null ? padrao : JSON.parse(v); } catch (_) { return padrao; } };
  const gravar = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch (_) { /* sem guardar: segue */ } };
  const meus = () => (Array.isArray(ler(GUARDA, [])) ? ler(GUARDA, []) : []);

  // ---------- Regras dos comentários (sempre publicadas) ----------
  (function regras() {
    const corpo = document.getElementById('regras-com');
    if (!corpo) return;
    el('p', '', T('com.regras.1'), corpo);
    el('p', '', T('com.regras.2'), corpo);
    const ul = el('ul', 'regras-lista', undefined, corpo);
    for (const c of CATEGORIAS) el('li', '', T('com.cat.' + c), ul);
    for (const n of [3, 4, 5]) el('p', '', T('com.regras.' + n), corpo);
  })();

  /** O motivo da análise, numa frase: "revisao" (o autor ainda vai ler) ou uma das categorias. */
  const motivoFrase = (prefixo, motivo) => (CATEGORIAS.includes(motivo)
    ? T(prefixo + '.categoria', { categoria: T('com.cat.' + motivo) }) : T(prefixo + '.revisao'));

  function textoLeitor(pai, texto) {
    const caixa = el('div', 'com-texto', undefined, pai);
    for (const par of String(texto).split(/\n{2,}/)) if (par.trim()) el('p', '', par.trim(), caixa);
    return caixa;
  }
  function meta(pai, c) {
    const p = el('p', 'com-meta', undefined, pai);
    if (c.nome) el('b', 'com-nome', c.nome, p);
    const t = el('time', '', T.data(c.criado.slice(0, 10)), p);
    t.dateTime = c.criado;
    el('span', 'com-n', T('com.numero', { n: c.id }), p);
  }

  // ---------- A lista ----------
  let publicos = [], aberta = false, carregou = false;
  function desenhar() {
    lista.replaceChildren();
    const guardados = meus();
    const porId = new Map(guardados.map(m => [m.id, m]));
    const vistos = new Set(publicos.map(c => c.id));
    const itens = publicos.map(c => ({ ...c, meu: porId.get(c.id) }))
      .concat(guardados.filter(m => !vistos.has(m.id)).map(m => ({ ...m, situacao: 'oculto', meu: m })))
      .sort((a, b) => b.id - a.id);
    if (!itens.length) { if (aberta) el('li', 'com-vazio', T('com.vazio'), lista); return; }
    for (const c of itens) {
      const li = el('li', 'com-item', undefined, lista);
      li.id = 'comentario-' + c.id;
      if (c.situacao === 'analise' && !c.meu) {
        li.classList.add('com-em-analise');
        meta(li, c);
        el('p', 'com-aviso-analise', motivoFrase('com.analise', c.motivo), li);
        continue;
      }
      const dele = c.meu || {};
      if (c.meu) li.classList.add('com-meu');
      if (c.situacao !== 'liberado') li.classList.add('com-retido');
      meta(li, { ...c, nome: c.situacao === 'liberado' ? c.nome : dele.nome });
      textoLeitor(li, c.situacao === 'liberado' ? c.texto : dele.texto);
      if (c.situacao === 'liberado' && c.resposta) {
        const r = el('div', 'com-resposta', undefined, li);
        const rot = el('p', 'com-resp-rot', T('com.resposta_autor'), r);
        if (c.resposta_em) { rot.append(' '); const t = el('time', '', T.data(c.resposta_em.slice(0, 10)), rot); t.dateTime = c.resposta_em; }
        textoLeitor(r, c.resposta);
      }
      if (!c.meu) continue;
      const nota = c.situacao === 'analise' ? motivoFrase('com.ficou', c.motivo) + ' ' + T('com.meu.analise')
        : c.situacao === 'liberado' ? T('com.meu.liberado') : T('com.meu.oculto', { n: c.id });
      const pe = el('p', 'com-nota', nota + ' ', li);
      const bt = el('button', 'bt-apagar', T('com.apagar'), pe);
      bt.type = 'button';
      bt.addEventListener('click', () => confirmarApagar(pe, bt, c.id, dele.chave, li));
    }
  }

  // a confirmação fica na página: a caixa nativa (window.confirm) pode abrir escondida ou ser bloqueada, e o botão parece morto
  function confirmarApagar(pe, bt, id, chave, li) {
    bt.hidden = true;
    const conf = el('span', 'com-conf', undefined, pe);
    conf.setAttribute('role', 'alert');
    conf.append(T('com.apagar_confirma') + ' ');
    const sim = el('button', 'bt-apagar', T('com.apagar_sim'), conf), nao = el('button', 'bt-apagar', T('com.apagar_nao'), conf);
    sim.type = nao.type = 'button';
    sim.addEventListener('click', () => { sim.disabled = nao.disabled = true; apagar(id, chave, li).then(() => { conf.remove(); bt.hidden = false; }); });
    nao.addEventListener('click', () => { conf.remove(); bt.hidden = false; bt.focus(); });
    nao.focus();
  }

  async function apagar(id, chave, li) {
    let ok = false;
    try {
      const r = await fetch(API, { method: 'DELETE', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id, chave }) });
      const j = await r.json().catch(() => ({}));
      ok = r.ok || j.situacao === 'nao_achou'; // já não existe: some também daqui
    } catch (_) { ok = false; }
    if (!ok) { situacao.textContent = T('com.apagar_erro', { n: id }); return; }
    gravar(GUARDA, meus().filter(m => m.id !== id));
    publicos = publicos.filter(c => c.id !== id);
    desenhar();
    situacao.textContent = T('com.apagado');
    form.querySelector('textarea').focus({ preventScroll: true });
  }

  // ---------- A caixa ----------
  let widget = null, carregando = null;
  function carregarTurnstile(chave) {
    if (carregando) return carregando;
    carregando = new Promise((ok, falha) => {
      window.aoCarregarTurnstile = ok;
      const s = document.createElement('script');
      s.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit&onload=aoCarregarTurnstile';
      s.async = true; s.onerror = falha;
      document.head.appendChild(s);
    }).then(() => {
      const caixa = form.querySelector('.comentario-robo');
      caixa.hidden = false;
      widget = window.turnstile.render(caixa, {
        sitekey: chave, action: 'comentario', appearance: 'interaction-only', size: 'flexible', 'refresh-expired': 'auto',
        theme: document.documentElement.getAttribute('data-tema') === 'escuro' ? 'dark'
          : document.documentElement.getAttribute('data-tema') === 'claro' ? 'light' : 'auto',
        language: { 'pt-BR': 'pt-br', 'zh-Hans': 'zh-cn' }[T.lingua] || T.lingua, // o Turnstile não aceita zh-Hans (T47)
      });
    }).catch(() => { carregando = null; });
    return carregando;
  }

  function abrir(chave) {
    const ta = form.querySelector('textarea');
    ta.disabled = false;
    ta.placeholder = T('com.placeholder_aberto');
    enviar.disabled = false;
    form.querySelector('.comentario-quem').hidden = false;
    form.querySelector('.comentario-moderacao').hidden = false;
    form.querySelector('.aviso-it').textContent = T('com.aviso_aberto');
    const nome = ler(GUARDA_NOME, '');
    if (typeof nome === 'string') form.elements.nome.value = nome;
    // o Turnstile só quando a pessoa começa a escrever: quem só lê não chama ninguém de fora
    form.addEventListener('focusin', () => carregarTurnstile(chave), { once: true });
    form.addEventListener('submit', ev => { ev.preventDefault(); mandar(chave); });
  }

  let ocupado = false;
  async function mandar(chave) {
    if (ocupado) return;
    const nome = form.elements.nome.value.trim(), texto = form.elements.texto.value.trim(), email = form.elements.email.value.trim();
    const erro = [...nome].length < 2 || [...nome].length > 40 ? 'com.erro.nome'
      : [...texto].length < 3 || [...texto].length > 2000 ? 'com.erro.texto'
        : email && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email) ? 'com.erro.email' : null;
    if (erro) {
      situacao.textContent = T(erro);
      form.elements[erro === 'com.erro.nome' ? 'nome' : erro === 'com.erro.email' ? 'email' : 'texto'].focus();
      return;
    }
    await carregarTurnstile(chave);
    const prova = window.turnstile && widget !== null ? window.turnstile.getResponse(widget) : '';
    if (!prova) { situacao.textContent = T('com.verificando'); return; }
    ocupado = true; enviar.disabled = true;
    situacao.textContent = T('com.enviando');
    let r, j = {};
    try {
      r = await fetch(API, { method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nome, texto, email, lingua: T.lingua, turnstile: prova }) });
      j = await r.json().catch(() => ({}));
    } catch (_) { r = null; }
    ocupado = false; enviar.disabled = false;
    try { window.turnstile.reset(widget); } catch (_) { /* segue */ }
    if (r && r.status === 201 && j.id) {
      gravar(GUARDA, meus().concat([{ id: j.id, chave: j.chave, nome, texto, criado: j.criado, motivo: j.motivo }]));
      gravar(GUARDA_NOME, nome);
      publicos = [{ id: j.id, criado: j.criado, situacao: 'analise', motivo: j.motivo }].concat(publicos);
      form.elements.texto.value = '';
      desenhar();
      situacao.textContent = motivoFrase('com.ficou', j.motivo);
      return;
    }
    const msg = { nome: 'com.erro.nome', texto: 'com.erro.texto', email: 'com.erro.email', robo: 'com.erro.robo',
      limite: 'com.erro.limite', cheio: 'com.erro.cheio' }[j.situacao] || 'com.erro.outro';
    situacao.textContent = T(msg);
  }

  // ---------- Carregar quando a seção chega perto da tela ----------
  async function carregar() {
    if (carregou) return;
    carregou = true;
    let j;
    try {
      const r = await fetch(API, { headers: { Accept: 'application/json' } });
      if (!r.ok) throw new Error(String(r.status));
      j = await r.json();
    } catch (_) { return; } // sem a função: a caixa fica fechada, como no HTML
    publicos = Array.isArray(j.comentarios) ? j.comentarios : [];
    aberta = Boolean(j.aberta && j.turnstile);
    if (aberta) abrir(j.turnstile);
    desenhar();
  }
  if (!/^https?:$/.test(location.protocol) || new URLSearchParams(location.search).has('pdf')) return;
  if (location.hash === '#comentarios') carregar(); // quem chega pelo link da seção não espera a rolagem
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(es => { if (es.some(e => e.isIntersecting)) { io.disconnect(); carregar(); } }, { rootMargin: '800px 0px' });
    io.observe(secao);
  } else carregar();
})();
