// Línguas em que o estudo existe (T30, diário D42). O botão de língua mostra só estas, cada uma
// escrita nela mesma. codigo: o lang da página e o nome do catálogo (textos/<codigo>.js); pasta: onde
// a página da língua fica, a partir da raiz do estudo; og: o og:locale das prévias de link.
// Lido também por scripts/textos.py: manter em JSON (aspas duplas, sem comentário dentro da lista).
// Língua nova: uma linha aqui, o catálogo textos/<codigo>.js e python -I scripts/previas.py, que grava
// a página da língua e as prévias (e python -I scripts/csv_estudo.py, os CSV).
window.LINGUAS = [
  {"codigo": "pt-BR", "nome": "Português", "pasta": "", "og": "pt_BR"},
  {"codigo": "en", "nome": "English", "pasta": "en/", "og": "en_US"},
  {"codigo": "es", "nome": "Español", "pasta": "es/", "og": "es_LA"}
];
