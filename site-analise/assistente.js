/* O assistente do "Pergunte aos dados" (T14, Proposta 2; diário D82; P36): o botão redondo no canto
   inferior direito abre um painel em que o leitor escreve perguntas sobre o estudo, e uma IA responde
   com o estudo inteiro à mão, citando o trecho onde conferir (servidor/functions/api/assistente.js).
   - O botão só aparece quando o servidor diz que está aberto (fora do ar, na cópia local e no modo PDF,
     não aparece) e nunca na impressão (estudo.css, @media print).
   - O painel é uma janela não modal: Esc fecha e devolve o foco ao botão; no celular, ocupa a tela.
   - A resposta chega como texto simples com **negrito** e links para trechos do estudo (#analise/3); a
     página escreve só isso, nada de HTML vindo do servidor.
   - A conversa fica só na memória da página (some ao recarregar), com até 6 perguntas; vai inteira a
     cada pergunta, porque o servidor não guarda conversa.
   Os textos vêm do catálogo da língua da página (chaves "ia."; T30). */
(function () {
  'use strict';
  const T = window.T;
  const API = '/api/assistente';
  if (!/^https?:$/.test(location.protocol) || new URLSearchParams(location.search).has('pdf')) return;
  function el(tag, cls, texto, pai) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (texto !== undefined) e.textContent = texto;
    if (pai) pai.appendChild(e);
    return e;
  }
  const estreito = () => matchMedia('(max-width: 599px)').matches;

  /** O texto da resposta: parágrafos, itens ("- "), **negrito** e [rótulo](#endereço), e mais nada. */
  function escrever(pai, texto) {
    let lista = null;
    for (const bruto of String(texto).split(/\n+/)) {
      const item = /^\s*[-*•]\s+/.test(bruto);
      const par = bruto.replace(/^\s*[-*•]\s+/, '').trim();
      if (!par) continue;
      if (item && !lista) lista = el('ul', '', undefined, pai);
      if (!item) lista = null;
      const p = el(item ? 'li' : 'p', '', undefined, item ? lista : pai);
      const re = /\*\*([^*]+)\*\*|\[([^\]]+)\]\((#[\w/-]+)\)/g;
      let i = 0, m;
      while ((m = re.exec(par))) {
        if (m.index > i) p.append(par.slice(i, m.index));
        if (m[1]) el('b', '', m[1], p);
        else { const a = el('a', '', m[2], p); a.href = m[3]; }
        i = re.lastIndex;
      }
      if (i < par.length) p.append(par.slice(i));
    }
  }

  let info = null, conversa = [], aberto = false, ocupado = false;
  const botao = el('button', 'ia-botao');
  botao.type = 'button';
  botao.setAttribute('aria-label', T('ia.botao'));
  botao.setAttribute('aria-expanded', 'false');
  botao.setAttribute('aria-controls', 'ia-painel');
  el('span', 'ia-botao-sinal', '?', botao).setAttribute('aria-hidden', 'true');
  botao.hidden = true;

  const painel = el('section', 'ia-painel');
  painel.id = 'ia-painel';
  painel.setAttribute('role', 'dialog');
  painel.setAttribute('aria-labelledby', 'ia-tit');
  painel.hidden = true;
  const cab = el('header', 'ia-cab', undefined, painel);
  el('h2', 'ia-tit', T('ia.tit'), cab).id = 'ia-tit';
  const fechar = el('button', 'ia-fechar', T('ia.fechar'), cab);
  fechar.type = 'button';
  el('p', 'ia-sub', T('ia.sub'), painel);
  const corpo = el('div', 'ia-corpo', undefined, painel);
  const inicio = el('div', 'ia-inicio', undefined, corpo);
  const log = el('div', 'ia-log', undefined, corpo);
  log.setAttribute('aria-live', 'polite');
  const situacao = el('p', 'ia-situacao', undefined, corpo);
  situacao.setAttribute('role', 'status');
  const form = el('form', 'ia-form', undefined, painel);
  const lab = el('label', 'ia-label', T('ia.label'), form);
  lab.htmlFor = 'ia-campo';
  const linha = el('div', 'ia-linha', undefined, form);
  const campo = el('textarea', 'ia-campo', undefined, linha);
  Object.assign(campo, { id: 'ia-campo', rows: 2, maxLength: 400, placeholder: T('ia.placeholder') });
  const enviar = el('button', 'ia-enviar', T('ia.enviar'), linha);
  enviar.type = 'submit';
  const cota = el('p', 'ia-cota', undefined, form); // quantas perguntas a pessoa tem hoje (5 por dia, pedido do autor)
  const pe = el('div', 'ia-pe', undefined, form);
  const contador = el('p', 'ia-contador', undefined, pe);
  const nova = el('button', 'ia-nova', T('ia.nova'), pe);
  nova.type = 'button';
  const aviso = el('p', 'ia-aviso', undefined, form);
  const priv = el('a', '', T('ia.priv'));
  priv.href = 'privacidade/'; // a privacidade da língua da página (en/privacidade/…)
  aviso.append(...T.f('ia.aviso', { priv }));

  /** A tela de começo: as perguntas frequentes (reescritas pelo estudo) ou, sem elas, alguns exemplos. */
  function montarInicio() {
    inicio.replaceChildren();
    const freq = (info && info.frequentes) || [];
    el('h3', 'ia-inicio-tit', T(freq.length ? 'ia.frequentes' : 'ia.exemplos'), inicio);
    const ul = el('ul', 'ia-sugestoes', undefined, inicio);
    const itens = freq.length ? freq : ['ia.ex1', 'ia.ex2', 'ia.ex3', 'ia.ex4'].map(k => ({ pergunta: T(k) }));
    for (const f of itens) {
      const b = el('button', 'ia-sugestao', f.pergunta, el('li', '', undefined, ul));
      b.type = 'button';
      // a pergunta frequente já tem a resposta conferida; o exemplo vai ao serviço
      b.addEventListener('click', () => (f.texto ? mostrarFrequente(f) : perguntar(f.pergunta)));
    }
    const p = el('p', 'ia-prontas', undefined, inicio);
    const a = el('a', '', T('ia.prontas'), p);
    a.href = '#explorar/pergunte';
  }
  function bloco(papel, texto, extra = {}) {
    const art = el('article', 'ia-msg ia-' + papel, undefined, log);
    el('h3', 'ia-quem', T(papel === 'leitor' ? 'ia.voce' : 'ia.estudo'), art);
    const txt = el('div', 'ia-texto', undefined, art);
    if (papel === 'leitor') el('p', '', texto, txt); else escrever(txt, texto);
    if (extra.fontes && extra.fontes.length) {
      const p = el('p', 'ia-fontes', T('ia.onde') + ' ', art);
      extra.fontes.forEach((f, i) => {
        if (i) p.append('; ');
        const a = el('a', '', f.titulo || f.endereco, p);
        a.href = f.endereco;
      });
    }
    if (extra.nivel) el('p', 'ia-nivel', T('ia.quem.' + extra.nivel), art);
    return art;
  }
  let restantes = null;
  function mostrarCota() {
    if (!info || restantes === null) return;
    const lim = info.limite_dia;
    cota.textContent = restantes >= lim ? T.p('ia.limite_dia', lim, { n: String(lim) }) : T.p('ia.restantes', restantes, { n: String(restantes) });
  }
  function atualizar() {
    const n = conversa.filter(c => c.papel === 'leitor').length;
    const max = (info && info.conversa_max) || 6;
    inicio.hidden = n > 0;
    // "pergunta 2 de 6 desta conversa" só quando o limite do dia é maior que a conversa
    contador.textContent = n && (!info || info.limite_dia > max) ? T('ia.contador', { n: String(n), max: String(max) }) : '';
    nova.hidden = !n;
    mostrarCota();
    const fim = n >= max || restantes === 0;
    campo.disabled = enviar.disabled = fim || ocupado;
    if (restantes === 0) situacao.textContent = T('ia.limite');
    else if (fim) situacao.textContent = T('ia.conversa_longa');
  }
  function mostrarFrequente(f) {
    bloco('leitor', f.pergunta);
    bloco('estudo', f.texto, { fontes: (f.fontes || []).map(e => (typeof e === 'string' ? { endereco: e, titulo: f.titulos && f.titulos[e] } : e)) });
    conversa.push({ papel: 'leitor', texto: f.pergunta }, { papel: 'estudo', texto: f.texto });
    atualizar();
  }
  async function perguntar(texto) {
    texto = texto.replace(/\s+/g, ' ').trim();
    if (ocupado) return;
    if (texto.split(' ').length < 2) { situacao.textContent = T('ia.curta'); return; }
    ocupado = true;
    situacao.textContent = '';
    const art = bloco('leitor', texto);
    art.scrollIntoView({ block: 'nearest' });
    const espera = el('p', 'ia-espera', T('ia.esperando'), log);
    atualizar();
    try {
      const r = await fetch(API, { method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pergunta: texto, lingua: T.lingua, conversa }) });
      const j = await r.json().catch(() => ({}));
      espera.remove();
      if (Number.isInteger(j.restantes)) restantes = j.restantes;
      if (j.situacao === 'ok') {
        const resp = bloco('estudo', j.texto, { fontes: j.fontes, nivel: j.nivel });
        conversa.push({ papel: 'leitor', texto }, { papel: 'estudo', texto: j.texto });
        campo.value = '';
        resp.scrollIntoView({ block: 'start' });
      } else {
        art.remove();
        situacao.textContent = T(['cota', 'limite', 'conversa_longa', 'curta'].includes(j.situacao) ? 'ia.' + j.situacao : 'ia.erro');
      }
    } catch (_) {
      espera.remove(); art.remove();
      situacao.textContent = T('ia.erro');
    } finally {
      ocupado = false;
      atualizar();
      if (aberto && !campo.disabled) campo.focus({ preventScroll: true });
    }
  }

  function abrir() {
    aberto = true;
    painel.hidden = false;
    botao.setAttribute('aria-expanded', 'true');
    document.documentElement.classList.toggle('ia-tela-cheia', estreito());
    campo.focus();
  }
  function fecharPainel(devolverFoco = true) {
    aberto = false;
    painel.hidden = true;
    botao.setAttribute('aria-expanded', 'false');
    document.documentElement.classList.remove('ia-tela-cheia');
    if (devolverFoco) botao.focus();
  }
  botao.addEventListener('click', () => (aberto ? fecharPainel() : abrir()));
  fechar.addEventListener('click', () => fecharPainel());
  painel.addEventListener('keydown', ev => { if (ev.key === 'Escape') { ev.stopPropagation(); fecharPainel(); } });
  form.addEventListener('submit', ev => { ev.preventDefault(); perguntar(campo.value); });
  campo.addEventListener('keydown', ev => {
    if (ev.key === 'Enter' && !ev.shiftKey && !ev.isComposing) { ev.preventDefault(); perguntar(campo.value); }
  });
  nova.addEventListener('click', () => {
    conversa = []; log.replaceChildren(); situacao.textContent = ''; atualizar(); campo.focus();
  });
  // um link para um trecho do estudo: no celular, o painel sai da frente para mostrar o trecho
  painel.addEventListener('click', ev => {
    const a = ev.target.closest('a[href^="#"]');
    if (a && estreito()) fecharPainel(false);
  });

  document.body.append(botao, painel);
  fetch(API + '?lingua=' + encodeURIComponent(T.lingua), { headers: { Accept: 'application/json' } })
    .then(r => (r.ok ? r.json() : null))
    .then(j => { if (j && j.aberta) { info = j; restantes = Number.isInteger(j.restantes) ? j.restantes : null; montarInicio(); atualizar(); botao.hidden = false; } })
    .catch(() => {});
})();
