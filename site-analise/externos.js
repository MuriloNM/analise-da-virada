/* Links externos (QA nº 5, diário D66): toda fonte fora do estudo abre em outra aba, sem passar a
   página de origem (noopener noreferrer), e o leitor de tela é avisado. Vale para todo link, também os
   que os outros scripts desenham depois (referências, notas, Método e fontes): um observador marca os
   que chegam. O aviso é um texto só para leitor de tela ('pag.aba_nova', no catálogo). */
(function () {
  'use strict';
  const PROPRIOS = ['analise-da-virada.pages.dev'];
  const externo = a => {
    const h = a.getAttribute('href') || '';
    if (!/^https?:\/\//i.test(h)) return false;
    let u; try { u = new URL(h); } catch (_) { return false; }
    return u.host !== location.host && !PROPRIOS.includes(u.host);
  };
  function marcar(a) {
    if (a.dataset.externo || !externo(a)) return;
    a.dataset.externo = '1';
    a.target = '_blank';
    a.rel = 'noopener noreferrer';
    const s = document.createElement('span');
    s.className = 'sr';
    s.textContent = T('pag.aba_nova');
    a.appendChild(s);
  }
  const varrer = raiz => {
    if (raiz.nodeType !== 1) return;
    if (raiz.matches('a[href]')) marcar(raiz);
    raiz.querySelectorAll('a[href]').forEach(marcar);
  };
  varrer(document.body);
  new MutationObserver(ms => ms.forEach(m => m.addedNodes.forEach(varrer))).observe(document.body, { childList: true, subtree: true });
})();
