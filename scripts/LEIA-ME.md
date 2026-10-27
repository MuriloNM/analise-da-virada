# Scripts: como refazer as bases

Os scripts que fizeram cada arquivo de `../dados/`, a partir dos arquivos do TSE e do IBGE. Rode da pasta raiz do repositório, com `python -I scripts/<nome>.py`. Cada um imprime um relatório das conferências e sai com erro (código 1) se alguma não fechar.

**Requisitos:** Python 3.14 (as contas foram feitas com o 3.14.0). Só três scripts usam bibliotecas de fora da biblioteca padrão (`secoes_inferencia.py`, `inferencia.py` e `exploracao.py`): `pip install -r requirements.txt` instala as mesmas versões (numpy 2.3.4 e scipy 1.16.2). As contas com sorteio (bootstrap) usam uma semente fixa, por isso o resultado sai igual a cada rodada.

**Não precisa rodar nada para usar os dados:** tudo que os scripts gravam já está em `../dados/` e `../planilha/`. Rodar serve para conferir que as bases saem das fontes.

**Os comentários** citam códigos do registro interno de trabalho: T (tarefas), D (diário) e P (decisões do autor). As notas N estão em Método e fontes, na página do estudo, e as regras dos testes, em [`../docs/analise/HIPOTESES.md`](../docs/analise/HIPOTESES.md).

## Na ordem

Os downloads vão devagar, poucos de cada vez e com nova tentativa quando o TSE pede para esperar (erro 429). Arquivos já baixados são pulados.

| # | Comando | O que faz | Grava |
|---|---|---|---|
| 1 | `python -I scripts/base1t.py PASTA` | Baixa o resultado final do 1º turno (eleição 6257) do Brasil, das UFs e dos 5.757 municípios | `PASTA/base1t.json`, que é o `dados/base_1t_municipios.json` |
| 2 | `python -I scripts/base2t.py` | Baixa o resultado final do 2º turno (6258), com brancos e nulos | `dados/base_2t_municipios.json` |
| 3 | `python -I scripts/confere2t.py` | Confere o 2º turno contra o 1º e contra o total oficial, sem baixar nada | só o relatório |
| 4 | `python -I scripts/analise_base.py` | Junta os dois turnos e calcula os indicadores (fatia, variações, diferença, captura, abstenção) | `dados/analise_municipios.csv`, `dados/analise_estados.csv`, `dados/analise_compacta.json` |
| 5 | `python -I scripts/tse6259_uf.py dados/tse_6259_uf` | Baixa o resultado oficial de cada estado para governador, senador e deputados (6259), para conferir o passo 6 | `dados/tse_6259_uf/` (bruto) |
| 6 | `python -I scripts/votos_partido_1t.py ZIP dados/votos_partido_1t.json dados/tse_6259_uf` | Soma os votos por partido, cargo e município do 1º turno. `ZIP` é o `votacao_partido_munzona_2026.zip` do TSE (22,9 MB; endereço no começo do script), baixado à mão | `dados/votos_partido_1t.json` |
| 7 | `python -I scripts/escala_partidos.py dados/escala_fontes/dataverse_MFIXKW/df_experts.csv dados/escala_fontes/dataverse_6KVTUV/bls9_estimates_partiespresidents_long.tab dados/escala_partidos.csv dados/esquerda_1t_municipios.csv` | Posição de cada partido na escala dos especialistas e o voto no campo da esquerda por município e cargo | `dados/escala_partidos.csv`, `dados/esquerda_1t_municipios.csv` |
| 8 | `python -I scripts/secoes_baixar.py dados/tse_secoes` | Baixa os dados por seção dos dois turnos (cerca de 540 MB) e confere cada arquivo | `dados/tse_secoes/` (bruto) |
| 9 | `python -I scripts/secoes.py` | Resultado de presidente por seção nos dois turnos, casado entre os turnos e conferido contra as bases municipais | `dados/secoes_presidente.csv.gz`, `dados/secoes_presidente_meta.json` |
| 10 | `python -I scripts/sociais_baixar.py dados/sociais_fontes` | Baixa as tabelas do IBGE (Censo 2022, PIB dos Municípios, áreas; cerca de 63 MB) | `dados/sociais_fontes/` (bruto) |
| 11 | `python -I scripts/dados_sociais.py dados/sociais_fontes dados/dados_sociais_municipios.json` | As 7 características de cada município, conferidas contra o total do Brasil de cada fonte | `dados/dados_sociais_municipios.json` |
| 12 | `python -I scripts/secoes_inferencia.py` | De onde vieram os votos de cada um, comparando seções da mesma cidade | `dados/secoes_inferencia.json` |
| 13 | `python -I scripts/inferencia.py` | As hipóteses, as regressões, os intervalos, o funil, o erro da projeção e os 35 testes dos dados sociais | `dados/inferencia.json` |
| 14 | `python -I scripts/exploracao.py` | As cinco perguntas da exploração guiada (capítulo 9); usa também `dados/tse_6259_uf/`, do passo 5 | `dados/exploracao.json` |

Os passos 12 a 14 levam alguns minutos. Conferido em 27/10/2026: os passos 3, 4, 7 e 12 a 14, rodados de novo a partir dos arquivos desta pasta, gravam arquivos iguais aos de `dados/`, número a número; só muda a data de geração no `meta`. Os CSV de `../planilha/` são esses arquivos na forma da página (separador e decimal da língua, cabeçalhos traduzidos); o script que os formata faz parte do código da página e não muda nenhum número. Para conferir os totais e as impressões digitais: `python scripts/conferir_totais.py`.

## A página

A página (`../site-analise/`) lê as bases e não faz conta nova. Todo texto para o leitor está no catálogo `site-analise/textos/pt-BR.js` (a origem) e `en.js`, chave por chave; mude o texto lá, nunca no HTML ou no JavaScript.

| Comando | O que faz | Grava |
|---|---|---|
| `python -I scripts/pagina_dados.py` | Os números da página, das bases de `dados/`, conferidos contra elas; os títulos das notas, de `docs/analise/NOTAS.md` | `site-analise/dados.js` e o bloco das notas do catálogo |
| `python -I scripts/apuracao_dados.py` | A página "Apuração ao vivo" | `site-analise/apuracao-dados.js` |
| `python -I scripts/mapa_ufs.py` | O desenho dos estados para o mapa (malha do IBGE) | `site-analise/mapa.js` |
| `python -I scripts/csv_estudo.py` | Os CSV para baixar, nas duas línguas, e o dicionário | `site-analise/csv/` |
| `python -I scripts/previas.py` | As páginas de cada língua (roda `linguas.py`), as imagens e as páginas de prévia de link. Precisa do Chrome ou do Edge | `site-analise/index.html`, `en/`, `c/`, `img/previa/` |
| `python -I scripts/pdf.py` | O estudo em PDF, de cada língua, e a impressão digital de cada PDF. Precisa do Playwright (`pip install playwright`) e do Chrome | `site-analise/pdf/` |
| `python -I scripts/site_local.py` | Serve a página em `http://127.0.0.1:8790/` para ver no navegador | — |
| `python -I scripts/conferir_textos.py`, `node scripts/conferir_numeros.js` | Conferem que não sobrou texto fora do catálogo e que as duas línguas dizem os mesmos números | só o relatório |

Conferido em 27/10/2026: rodar os quatro primeiros e o `linguas.py` nesta pasta grava arquivos iguais aos de `site-analise/`; só muda a data de geração. O formulário "Escrever ao autor" (`site-analise/contato.js`) está sem a chave do autor: quem publicar uma cópia cria a sua no Web3Forms.

## A noite da apuração (não dá para refazer)

Estes rodaram durante a apuração do 2º turno, em 25/10/2026, lendo o TSE ao vivo. Ficam aqui para mostrar como as leituras foram feitas.

| Script | O que fez | Arquivo |
|---|---|---|
| `collector.py PASTA` | A cada leitura, a contagem do 2º turno e o 1º turno nas mesmas urnas (lê `PASTA/base1t.json`, do passo 1) | `hist.json` e `now.json`, guardados como `dados/historico_2t.json` (e `.csv`) e `dados/ultimo_retrato_2t.json` |
| `bweb.py PASTA` | Baixa os boletins de urna do 1º turno e guarda, de cada seção, a hora de chegada e os votos de presidente | `PASTA/sec_UF.json` (bruto, fora do repositório) |
| `curva1t.py PASTA dados/base_1t_compacta.json` | Remonta a contagem do 1º turno pela hora de chegada de cada boletim | a curva `t1c` em `dados/base_1t_compacta.json` |
