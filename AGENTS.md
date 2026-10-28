# Guia para IAs: conferir, refazer e continuar o estudo

Este arquivo é para uma inteligência artificial que vai trabalhar com este repositório: um assistente de programação (Claude Code, Codex, Cursor, Copilot…) aberto nesta pasta, ou um chat que recebeu os arquivos. Ferramentas que leem `AGENTS.md` ou `CLAUDE.md` sozinhas já começam por aqui. Para só fazer perguntas ao estudo, sem rodar código, o caminho mais curto é [`PERGUNTE-A-SUA-IA.md`](PERGUNTE-A-SUA-IA.md).

**English summary.** This repository holds the processed data, the scripts and the web page of the study "Brazil's runoff reversal" (Brazil, 2026 presidential election, first round vs. runoff, by state and municipality). Everything below is in Portuguese, as are file names, columns and code comments; `DATA-DICTIONARY.md` translates the columns. Three uses: (1) answer questions from the CSV files; (2) review: check the numbers against the sources, rerun the scripts and compare; (3) reproduce or extend: rebuild the datasets and the page, or add a new analysis following the rules in section 6. Never attribute causes, never talk about individual voters (the data are counts by place), treat both candidates alike.

## 1. O estudo em cinco linhas

- **Pergunta:** o que mudou do 1º para o 2º turno da eleição presidencial de 2026, entre Lula e Flávio Bolsonaro, por estado, município e seção eleitoral. Entre os votos dados aos dois, o Lula passou de 48,99% para 51,79%, e a diferença virou de −2.224.965 para +4.430.191.
- **Dados:** resultados oficiais e dados abertos do TSE (por município e por seção), votos por partido do 1º turno, escala ideológica dos partidos de especialistas e dados sociais do IBGE.
- **Método:** contagens; regressões ponderadas com efeito fixo de estado, erro agrupado por estado e bootstrap selvagem; regressão ecológica comparando seções da mesma cidade; correção de Holm nos 35 testes dos dados sociais. As regras de cada teste foram escritas **antes** das contas, em [`docs/analise/HIPOTESES.md`](docs/analise/HIPOTESES.md).
- **Página:** [analise-da-virada.pages.dev](https://analise-da-virada.pages.dev/) (e `/en/`), feita do código em `site-analise/`.
- **Versão:** 1.1.1, de 28/10/2026. Autor: Murilo Neves de Martins.

## 2. Mapa do repositório

```
planilha/pt-BR/, planilha/en/   CSV prontos para planilha (mesmos números; muda a língua, o separador e o decimal)
DICIONARIO.md, DATA-DICTIONARY.md   cada coluna de cada CSV, com fonte e script
dados/                          as bases como os scripts gravam (CSV com ponto decimal, JSON, seções em .csv.gz)
dados/LEIA-ME.md                o que é cada arquivo de dados/
scripts/                        Python (e um .js) que baixam as fontes, fazem as bases e montam a página
scripts/LEIA-ME.md              a ordem dos scripts, com os comandos
site-analise/                   a página (HTML, CSS, JS; textos em site-analise/textos/pt-BR.js e en.js)
docs/analise/HIPOTESES.md       as regras dos testes, fixadas antes das contas, e as mudanças datadas
docs/analise/NOTAS.md           as notas sobre os dados (N01…), como foram registradas
SHA256SUMS.txt                  impressão digital dos arquivos de dados/ e planilha/
scripts/conferir_totais.py      confere somas e impressões digitais (só biblioteca padrão)
```

Fora do repositório (os scripts baixam de novo): os zips do TSE (votação por partido, dados por seção, boletins de urna, cerca de 560 MB), as tabelas do IBGE (63 MB) e os resultados por estado dos cargos estaduais.

## 3. Como os dados andam

```
TSE resultados (6257, 6258) ─ base1t.py, base2t.py ─► base_1t/2t_municipios.json ─ analise_base.py ─► analise_municipios.csv, analise_estados.csv
TSE dados abertos (partidos) ─ votos_partido_1t.py ─► votos_partido_1t.json ─┐
Harvard Dataverse (escala) ──────────────────────────────────────────────────┴ escala_partidos.py ─► escala_partidos.csv, esquerda_1t_municipios.csv
TSE dados por seção ─ secoes_baixar.py, secoes.py ─► secoes_presidente.csv.gz ─ secoes_inferencia.py ─► secoes_inferencia.json
IBGE ─ sociais_baixar.py, dados_sociais.py ─► dados_sociais_municipios.json
analise_municipios.csv + esquerda_1t + secoes_inferencia + dados_sociais + historico_2t ─ inferencia.py ─► inferencia.json
secoes_presidente + analise_municipios + inferencia ─ exploracao.py ─► exploracao.json
tudo acima ─ pagina_dados.py, apuracao_dados.py, mapa_ufs.py, csv_estudo.py ─► site-analise/dados.js, apuracao-dados.js, mapa.js, csv/
site-analise/textos/*.js ─ linguas.py (dentro de previas.py) ─► site-analise/index.html, en/index.html ; pdf.py ─► site-analise/pdf/
```

`planilha/` é cópia de `site-analise/csv/` (mais `votos_partido_1t.csv`, achatado de `votos_partido_1t.json`).

## 4. Como ler os arquivos

- **Chave do município:** o código do TSE, 5 dígitos, texto (pode começar com zero): `cd_tse` nos CSV, a chave de `mu` nos JSON. O código IBGE (7 dígitos) está em `cd_ibge` / `cdi`. `uf` = `ZZ` (ou `zz`) é o exterior: 186 "municípios" que só votam para presidente e ficam fora das regressões.
- **CSV de `dados/`:** vírgula entre os campos, ponto decimal, UTF-8. **CSV de `planilha/pt-BR/`:** ponto e vírgula e vírgula decimal, com marca UTF-8 (BOM); `planilha/en/`: vírgula e ponto, cabeçalhos em inglês. Porcentagens já multiplicadas por 100. Célula vazia = conta sem valor (por exemplo, fatia com zero voto nos dois).
- **Contagens nos JSON de base** (`base_*_municipios.json`, `analise_compacta.json`): `te` eleitorado, `c` comparecimento, `vv` válidos, `L` Lula, `F` Flávio, `vb` brancos, `tvn` nulos (só no 2º turno). Em `analise_compacta.json`, cada linha de `mu` é uma lista na ordem de `meta.mu_colunas`.
- **`votos_partido_1t.json`:** `mu[cd].c[cargo]` com `vv`, `n` (nominais), `l` (legenda), `p` (por partido: [nominais, legenda]), `f` (por federação), `sj` e `an` (anulados sub judice e anulados, fora dos válidos). Cargos: 3 governador, 5 senador (dois votos por eleitor), 6 deputado federal, 7 estadual, 8 distrital. Campos em `meta.campos`.
- **`secoes_presidente.csv.gz`:** uma linha por seção (499.248), chave `uf`, `cd_mun`, `zona`, `secao`; colunas `t1_*` (1º turno, `t1_13` Lula, `t1_22` Flávio, um por candidato) e `t2_*` (2º turno). `t1_28` são nulos técnicos (nota N21). Campos em `secoes_presidente_meta.json`.
- **`inferencia.json`:** `hipoteses` (H1, H3, H4: `versoes` com `coef`, `ic95`, `ic95_selvagem`, `p_cr1`, `p_selvagem`, `classificacao`), `H5` (por cargo), `ecologica` e `por_lugar` (de onde vieram os votos), `transicao`, `limites_duncan_davis`, `funil`, `projecao` (erro da projeção da noite), `sociais` (os 35 testes dos dados sociais) e `meta` (semente, número de repetições, regras). `secoes_inferencia.json`: `por_lugar` (Brasil, regiões, estados), `conferencias`, `nao_deu` (lugares que não passaram no critério de precisão). `exploracao.json`: as perguntas E1 a E5 do capítulo 9.
- **Textos da página:** todo texto para o leitor está em `site-analise/textos/pt-BR.js` (origem) e `en.js`, chave por chave. O JavaScript da página só formata: não faz conta nova.

## 5. Tarefas

### 5.1 Responder perguntas

Use `planilha/` e o dicionário. Cite arquivo, coluna e linha (ou filtro) de cada número; mostre a conta. As regras da seção 6 valem para toda resposta.

### 5.2 Revisar (dupla checagem)

Objetivo: achar erro, não confirmar. Entregue uma lista do que conferiu, com o resultado de cada item (confere / não confere / não deu para conferir) e, para cada erro, onde está, o que esperava e como chegou lá. Não corrija nada sem pedir.

1. **Integridade:** `python scripts/conferir_totais.py` (somas contra o oficial e impressões digitais).
2. **Totais do Brasil** (linha `BR` de `dados/analise_estados.csv`): Lula 53.879.538 → 64.256.232; Flávio 56.104.503 → 59.826.041; diferença −2.224.965 → +4.430.191 (virada de 6.655.156); juntos, 14.098.232 votos a mais, 73,6% para o Lula (`captura_lula_pct`).
3. **De onde vieram os 14,10 milhões** (conta de soma, sem estimativa): `var_comparecimento` 2.960.239 + `outros_1t` 9.316.747 + queda de brancos e nulos 1.821.246 (`var_brancos_nulos` = −1.821.246) = 14.098.232. Vale no Brasil, em cada região e em cada estado.
4. **Fonte contra base:** sorteie municípios e compare `dados/base_2t_municipios.json` com o resultado oficial do TSE (`https://resultados.tse.jus.br/oficial/ele2026/6258/dados/{uf}/{uf}{cd_tse}-c0001-e006258-u.json`, uf em minúsculas). Some as seções de um município em `secoes_presidente.csv.gz` e compare com a base municipal.
5. **Reproduzir as contas:** numa cópia da pasta, rode `python -I scripts/analise_base.py`, `secoes_inferencia.py`, `inferencia.py` e `exploracao.py` (seção 7). Os arquivos gravados devem ser iguais aos de `dados/`, número a número; só muda a data de geração no `meta` (sementes fixas).
6. **Regras antes das contas:** para cada hipótese de `inferencia.json`, confira em `docs/analise/HIPOTESES.md` se o teste, o peso, os controles e o corte de classificação são os registrados, e se as mudanças posteriores estão datadas e explicadas.
7. **Página contra dados:** cada número de uma frase em `site-analise/textos/pt-BR.js` deve sair de `site-analise/dados.js` (que `pagina_dados.py` grava das bases). `node scripts/conferir_numeros.js` confere que português e inglês dizem os mesmos números; `python -I scripts/conferir_textos.py`, que não sobra texto fora do catálogo.
8. **Método:** a técnica serve à pergunta? As premissas valem (divisão igual da regressão ecológica, poucos grupos no erro agrupado, eleitorado que muda entre os turnos)? A conclusão diz mais do que o teste permite? Os limites assumidos estão em "Limites do estudo", na página.

Achou um erro? O autor pede que seja aberto como issue, no modelo "Achei um erro": https://github.com/MuriloNM/analise-da-virada/issues

### 5.3 Refazer e continuar

- **Refazer as bases:** `scripts/LEIA-ME.md`, na ordem. Os downloads são lentos de propósito (poucos de cada vez, nova tentativa no erro 429): não acelere contra o servidor do TSE.
- **Refazer a página:** `python -I scripts/pagina_dados.py`, `apuracao_dados.py`, `mapa_ufs.py`, `csv_estudo.py` e `python -I scripts/previas.py` (que roda `linguas.py`); ver: `python -I scripts/site_local.py` e abrir `http://127.0.0.1:8790/`. `previas.py` e `pdf.py` precisam do Chrome ou do Edge e `pdf.py`, do Playwright (`pip install playwright`). Rodar os scripts da página nesta pasta grava arquivos iguais aos de `site-analise/`, fora a data.
- **Mudar um texto:** no catálogo (`textos/pt-BR.js` e `en.js`, a mesma chave), nunca no HTML ou no JS; depois `previas.py`, `pdf.py`, `conferir_textos.py` e `conferir_numeros.js`.
- **Análise nova:** escreva a pergunta, a variável, o teste e o que conta como resultado **antes** de olhar os números, num arquivo com data. Rode num script próprio que lê `dados/` e grava um arquivo novo, sem mexer nos existentes. O que for feito depois de ver os dados é exploratório e deve ser chamado assim. Use as mesmas regras de `HIPOTESES.md` (peso, efeito fixo de estado, erro agrupado, critério de precisão, correção para muitas comparações).
- **O formulário "Escrever ao autor"** (`site-analise/contato.js`) está sem chave neste repositório: quem publicar uma cópia cria a sua no Web3Forms. Uma cópia publicada é obra derivada: cite o estudo (CC BY 4.0) e deixe claro que não é a página do autor.

## 6. Regras do estudo (valem para resposta, revisão e trabalho novo)

1. **Lugares, não pessoas.** Os dados são contagens por município e seção. Nunca diga como um eleitor ou um grupo de pessoas votou ou mudou de voto; diga o que aconteceu no lugar. As contas de onde vieram os votos dão o **saldo** de cada fonte, não o caminho de cada eleitor.
2. **Onde e quanto, não por quê.** Não atribua causas (campanha, debate, aliança, rede social, economia).
3. **Os dois do mesmo jeito.** Teste da troca: a mesma frase, com o outro candidato no lugar, tem de soar igualmente justa.
4. **Incerteza à vista.** Estimativa vem com intervalo de 95%; a que não passa no critério de precisão é "sem lado claro", não resultado.
5. **Regras antes das contas.** Não mude um teste registrado depois de ver o resultado; se precisar, registre a mudança com data e motivo, e mostre as duas versões.
6. **O oficial é o TSE.** Este estudo pode ter erros.

## 7. Ambiente

Python 3.14 (as contas foram feitas com o 3.14.0); `pip install -r requirements.txt` (numpy 2.3.4 e scipy 1.16.2, só para `secoes_inferencia.py`, `inferencia.py` e `exploracao.py`). Node.js para `conferir_numeros.js`. Rode da raiz do repositório, com `python -I scripts/<nome>.py`; cada script imprime as conferências e sai com código 1 se alguma falhar. Os scripts gravam em `dados/` e `site-analise/`: para revisar sem mexer no original, trabalhe numa cópia.

Os comentários do código e os documentos citam códigos do registro interno de trabalho do autor: T (tarefas), D (diário), P (decisões). Esse registro não está aqui; as notas N estão em `docs/analise/NOTAS.md` e na página.
