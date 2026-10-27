/* A caixa "Escrever ao autor", numa janela aberta pelo cabeçalho e pelo rodapé (T17; especificação 7.6; P08, diário D71): uma mensagem
   privada, só texto, que o Web3Forms entrega no e-mail do autor sem mostrar o endereço. A chave de
   acesso do Web3Forms é pública por natureza (só permite mandar mensagem ao autor, nunca ler nada).
   Contra robôs: o campo escondido "botcheck", que o Web3Forms descarta se vier preenchido; depois da
   publicação (T09) pode entrar também o Turnstile do Cloudflare. Os textos vêm do catálogo da língua
   da página (chaves "rod."; T30). */
(function () {
  'use strict';
  const T = window.T;
  const CHAVE = ''; // a chave do formulário do Web3Forms (web3forms.com): cada um cria a sua
  const form = document.querySelector('.contato-form');
  if (!form) return;
  // a janela: abre pelo link do cabeçalho e pelo do rodapé; fecha no "Fechar", no Esc e no clique fora dela
  const janela = form.closest('dialog');
  let quemAbriu = null;
  // no celular e no tablet o cabeçalho rola com a página: o "Contato" vai também na barra presa no alto
  // (o índice dos capítulos e o das partes de Explorar, Apuração ao vivo e Método e fontes)
  for (const barra of document.querySelectorAll('nav.indice')) {
    const b = document.createElement('button');
    b.type = 'button'; b.className = 'bt-contato-barra'; b.dataset.abrirContato = '';
    b.setAttribute('aria-haspopup', 'dialog');
    b.textContent = T('rod.contato_curto');
    barra.appendChild(b);
  }
  for (const b of document.querySelectorAll('[data-abrir-contato]')) {
    b.addEventListener('click', () => {
      quemAbriu = b;
      janela.showModal();
      form.elements.mensagem.focus();
    });
  }
  janela.querySelector('[data-fechar-contato]').addEventListener('click', () => janela.close());
  janela.addEventListener('click', ev => { if (ev.target === janela) janela.close(); });
  janela.addEventListener('close', () => { if (quemAbriu) quemAbriu.focus({ preventScroll: true }); });
  const situacao = form.querySelector('.contato-situacao');
  const botao = form.querySelector('button[type="submit"]');
  const campo = n => form.elements[n];
  const dizer = (chave, erro = false) => {
    situacao.textContent = chave ? T(chave) : '';
    situacao.classList.toggle('erro', erro);
  };
  form.addEventListener('submit', async ev => {
    ev.preventDefault();
    const mensagem = campo('mensagem').value.trim();
    const email = campo('email').value.trim();
    if (!mensagem) { dizer('rod.vazia', true); campo('mensagem').focus(); return; }
    if (email && !campo('email').checkValidity()) { dizer('rod.email_errado', true); campo('email').focus(); return; }
    botao.disabled = true;
    dizer('rod.enviando');
    try {
      const r = await fetch('https://api.web3forms.com/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({
          access_key: CHAVE,
          subject: T('rod.assunto'),
          from_name: T('pag.nome'),
          name: campo('nome').value.trim() || '—',
          email: email || undefined,
          message: mensagem,
          lingua: T.lingua,
          pagina: location.href,
          botcheck: campo('botcheck').checked,
        }),
      });
      const j = await r.json().catch(() => ({}));
      if (!r.ok || !j.success) throw new Error(j.message || String(r.status));
      form.reset();
      dizer('rod.enviada');
    } catch (_) {
      dizer('rod.erro', true);
    } finally {
      botao.disabled = false;
    }
  });
})();
