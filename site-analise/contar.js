/* Contadores próprios (T20 e T16; P35; especificação 7.10): a página avisa a função /api/contar de
   algumas ações, só com o nome da ação e um detalhe da lista (a língua do PDF, a parte do menu, o número
   do capítulo, a origem do link), sem nada que diga quem leu. Vai por navigator.sendBeacon, que não
   espera resposta nem atrasa a página.
   - window.contar(evento, detalhe, umaVez): umaVez (o padrão) conta a mesma coisa só uma vez por visita;
     o PDF e a busca da cidade contam a cada vez.
   - Na abertura: o ?origem= dos links da divulgação (?origem=linkedin).
   - Fora do ar (arquivo aberto do disco) e no modo PDF, não manda nada.
   Quem chama: estudo.js (aba, capítulo, cidade) e o clique em qualquer link de PDF, aqui. */
(function () {
  'use strict';
  const params = new URLSearchParams(location.search);
  const pode = /^https?:$/.test(location.protocol) && !params.has('pdf');
  const vistos = new Set();
  function contar(evento, detalhe = '', umaVez = true) {
    const d = String(detalhe);
    const k = evento + '|' + d;
    if (!pode || (umaVez && vistos.has(k))) return;
    vistos.add(k);
    const corpo = JSON.stringify({ e: evento, d });
    try { if (navigator.sendBeacon && navigator.sendBeacon('/api/contar', corpo)) return; } catch (_) { /* segue */ }
    try { fetch('/api/contar', { method: 'POST', body: corpo, keepalive: true }).catch(() => {}); } catch (_) { /* contador não derruba nada */ }
  }
  window.contar = contar;

  const origem = (params.get('origem') || '').trim().toLowerCase();
  if (/^[a-z0-9_-]{1,32}$/.test(origem)) contar('origem', origem);

  // o PDF baixa na língua da página (P25)
  document.addEventListener('click', ev => {
    const a = ev.target.closest && ev.target.closest('a[href$=".pdf"]');
    if (a) contar('pdf', (window.T && window.T.lingua) || document.documentElement.lang, false);
  }, true);
})();
