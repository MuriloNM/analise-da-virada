# Dicionário de dados

English: [DATA-DICTIONARY.md](DATA-DICTIONARY.md) · Español: [DICCIONARIO.md](DICCIONARIO.md) · 简体中文: [SHUJU-ZIDIAN.md](SHUJU-ZIDIAN.md)

Os arquivos de `planilha/`, coluna por coluna. Os de `planilha/pt-BR/`, `planilha/en/`, `planilha/es/` e `planilha/zh-Hans/` são os mesmos números; mudam a língua dos cabeçalhos, o separador e o sinal decimal. A unidade e a fórmula de cada coluna estão na descrição. Este arquivo é gerado de `planilha/pt-BR/dicionario.csv`.

## municipios.csv

Os dois turnos lado a lado nos 5.757 municípios (5.571 do Brasil e 186 do exterior), com os indicadores do estudo.

- **Fonte:** TSE, resultados oficiais (resultados.tse.jus.br, eleições 6257 e 6258)
- **Feito por:** `scripts/base1t.py`, `scripts/base2t.py`, `scripts/analise_base.py` → `dados/analise_municipios.csv`
- **Linhas:** 5.757

| coluna | descrição |
|---|---|
| `cd_tse` | código do município no TSE, 5 dígitos |
| `cd_ibge` | código do município no IBGE, 7 dígitos; vazio no exterior |
| `uf, municipio` | sigla da UF (ZZ no exterior) e nome do município |
| `regiao` | Norte, Nordeste, Centro-Oeste, Sudeste, Sul ou Exterior (nota N08) |
| `capital_interior` | capital, interior ou exterior (nota N08) |
| `porte, porte_faixa` | faixa de porte pelo eleitorado do 1º turno: código de 1 a 5 (X no exterior) e nome (nota N08) |
| `eleitorado_1t, eleitorado_2t` | eleitorado apto de cada turno (nota N05) |
| `comparecimento_1t, comparecimento_2t` | comparecimento |
| `abstencao_1t, abstencao_2t` | abstenção: eleitorado − comparecimento |
| `validos_1t, validos_2t` | votos válidos |
| `brancos_nulos_1t, brancos_nulos_2t` | brancos e nulos: comparecimento − válidos (no 1º turno, juntos: nota N07) |
| `brancos_2t, nulos_2t` | brancos e nulos separados, só no 2º turno |
| `lula_1t, flavio_1t, lula_2t, flavio_2t` | votos de cada candidato |
| `outros_1t` | votos dos outros candidatos no 1º turno: válidos − Lula − Flávio |
| `fatia_lula_1t_pct, fatia_lula_2t_pct` | fatia do Lula entre os dois, Lula ÷ (Lula + Flávio), em %; vazio sem voto nos dois (nota N09). A do Flávio é 100 − fatia |
| `var_fatia_pp` | variação da fatia do Lula, 2º − 1º turno, em pontos percentuais |
| `var_lula, var_flavio` | votos ganhos por cada um do 1º para o 2º turno |
| `dif_1t, dif_2t, var_dif` | diferença Lula − Flávio em cada turno e a variação dela |
| `peso_virada_pct` | peso na virada: variação da diferença da unidade ÷ a do Brasil, em % |
| `captura_lula_pct` | captura: votos ganhos pelo Lula ÷ votos ganhos pelos dois, em %; vazio quando os dois juntos não ganharam votos; pode passar de 100 ou ficar abaixo de 0 (nota N09) |
| `var_comparecimento` | variação do comparecimento, 2º − 1º turno |
| `var_brancos_nulos` | variação de brancos e nulos, 2º − 1º turno |
| `var_eleitorado` | variação do eleitorado, 2º − 1º turno, só registro (nota N05) |
| `taxa_abst_1t_pct, taxa_abst_2t_pct` | taxa de abstenção: abstenção ÷ eleitorado, em %, cada turno com o próprio eleitorado (nota N05) |
| `var_taxa_abst_pp` | variação da taxa de abstenção, em pontos percentuais |
| `residuo_identidade` | conferência: (votos ganhos pelos dois) − (outros do 1º turno + variação do comparecimento − variação de brancos e nulos); é zero em todas as linhas |

## estados.csv

As mesmas colunas para o Brasil, as 5 regiões, o exterior e as 27 UFs (o exterior como ZZ).

- **Fonte:** TSE, resultados oficiais (resultados.tse.jus.br, eleições 6257 e 6258)
- **Feito por:** `scripts/base1t.py`, `scripts/base2t.py`, `scripts/analise_base.py` → `dados/analise_estados.csv`
- **Linhas:** 35

| coluna | descrição |
|---|---|
| `nivel` | brasil, regiao ou uf |
| `codigo, nome` | código (BR, sigla da região ou da UF; ZZ e EX para o exterior) e nome |
| `regiao` | região da UF; vazio no Brasil |
| `municipios` | quantos municípios a unidade soma |
| `eleitorado_1t, eleitorado_2t` | eleitorado apto de cada turno (nota N05) |
| `comparecimento_1t, comparecimento_2t` | comparecimento |
| `abstencao_1t, abstencao_2t` | abstenção: eleitorado − comparecimento |
| `validos_1t, validos_2t` | votos válidos |
| `brancos_nulos_1t, brancos_nulos_2t` | brancos e nulos: comparecimento − válidos (no 1º turno, juntos: nota N07) |
| `brancos_2t, nulos_2t` | brancos e nulos separados, só no 2º turno |
| `lula_1t, flavio_1t, lula_2t, flavio_2t` | votos de cada candidato |
| `outros_1t` | votos dos outros candidatos no 1º turno: válidos − Lula − Flávio |
| `fatia_lula_1t_pct, fatia_lula_2t_pct` | fatia do Lula entre os dois, Lula ÷ (Lula + Flávio), em %; vazio sem voto nos dois (nota N09). A do Flávio é 100 − fatia |
| `var_fatia_pp` | variação da fatia do Lula, 2º − 1º turno, em pontos percentuais |
| `var_lula, var_flavio` | votos ganhos por cada um do 1º para o 2º turno |
| `dif_1t, dif_2t, var_dif` | diferença Lula − Flávio em cada turno e a variação dela |
| `peso_virada_pct` | peso na virada: variação da diferença da unidade ÷ a do Brasil, em % |
| `captura_lula_pct` | captura: votos ganhos pelo Lula ÷ votos ganhos pelos dois, em %; vazio quando os dois juntos não ganharam votos; pode passar de 100 ou ficar abaixo de 0 (nota N09) |
| `var_comparecimento` | variação do comparecimento, 2º − 1º turno |
| `var_brancos_nulos` | variação de brancos e nulos, 2º − 1º turno |
| `var_eleitorado` | variação do eleitorado, 2º − 1º turno, só registro (nota N05) |
| `taxa_abst_1t_pct, taxa_abst_2t_pct` | taxa de abstenção: abstenção ÷ eleitorado, em %, cada turno com o próprio eleitorado (nota N05) |
| `var_taxa_abst_pp` | variação da taxa de abstenção, em pontos percentuais |
| `residuo_identidade` | conferência: (votos ganhos pelos dois) − (outros do 1º turno + variação do comparecimento − variação de brancos e nulos); é zero em todas as linhas |

## partidos.csv

Os 30 partidos de 2026, com a posição na escala dos especialistas (0 a 10), o campo da esquerda e as regras aplicadas.

- **Fonte:** Bolognesi, Ribeiro, Codato e Silva (2025), doi:10.7910/DVN/MFIXKW
- **Feito por:** `scripts/escala_partidos.py` → `dados/escala_partidos.csv`
- **Linhas:** 30

| coluna | descrição |
|---|---|
| `numero, sigla, nome` | número, sigla e nome do partido em 2026 |
| `federacao_2026` | federação de que o partido faz parte em 2026, se fizer |
| `posicao` | posição na escala dos especialistas, rodada de 2022: de 0 (extrema esquerda) a 10 (extrema direita); vazio no Missão (nota N11) |
| `categoria` | categoria do artigo de origem (extrema esquerda, esquerda, centro-esquerda, centro, centro-direita, direita, extrema direita) |
| `campo_esquerda` | sim para posição até 4,49 (extrema esquerda, esquerda e centro-esquerda) |
| `regra, regra_explicada` | regra usada para ligar o partido de 2026 ao da pesquisa (fusões, mudanças de nome, partidos novos: nota N10) |
| `sigla_na_pesquisa` | sigla do partido na base da pesquisa |
| `especialistas, desvio_padrao` | quantos especialistas deram nota e o desvio padrão das notas (nota N12) |
| `fonte` | a publicação e a base de dados |
| `conf_2018_posicao, conf_2018_campo_esquerda, conf_2018_regra, conf_2018_explicada` | conferência com a rodada de 2018 da mesma pesquisa |
| `conf_zucco_power_2021` | conferência com a escala de Zucco e Power (pesquisa com deputados federais, 2021), de cerca de −1 a +1; só a ordem é comparável |

## esquerda_municipios.csv

Voto no campo da esquerda para deputado e senador no 1º turno, por município, estado e Brasil (capítulo 5). O do campo da direita, do espelho do Flávio, é 100% menos o da esquerda e o dos partidos sem posição.

- **Fonte:** TSE, dados abertos, votacao_partido_munzona_2026.zip; escala de partidos.csv
- **Feito por:** `scripts/votos_partido_1t.py`, `scripts/escala_partidos.py` → `dados/esquerda_1t_municipios.csv`
- **Linhas:** 16.798

| coluna | descrição |
|---|---|
| `nivel` | mu (município), uf ou br |
| `cd, uf, nm` | código TSE do município (vazio em estado e Brasil), UF e nome |
| `cargo, cargo_nome` | 5 senador, 6 deputado federal, 7 deputado estadual, 8 deputado distrital |
| `vv, esq, pct_esq` | votos válidos do cargo, votos dos partidos do campo da esquerda e a parcela deles nos válidos, em % |
| `sem_posicao, pct_sem_posicao` | votos do partido sem posição na escala (Missão) e a parcela deles nos válidos (nota N11) |
| `escala` | média das posições dos partidos, ponderada pelos votos, de 0 a 10, só entre os votos com posição |
| `lula_1t, flavio_1t, fatia_lula_1t` | votos de presidente no 1º turno e a fatia do Lula entre os dois, em % |
| `vantagem` | pct_esq − fatia do Lula entre os dois, em pontos percentuais. O teste do capítulo 5 usa a fatia sobre os válidos (HIPOTESES.md, P14); esta coluna é a da conferência |
| `sj, sj_esq, pct_esq_com_sj, escala_com_sj, vantagem_com_sj` | a versão com os votos sub judice somados aos válidos e aos partidos deles (nota N02) |
| `conf_2018_pct_esq, conf_2018_sem_posicao, conf_2018_escala, conf_2018_vantagem` | conferência com a rodada de 2018 da escala |

## votos_partido_1t.csv

Arquivo achatado de `dados/votos_partido_1t.json`, só neste repositório: uma linha por município × cargo × partido com algum voto no 1º turno (partido sem voto no lugar não tem linha).

- **Fonte:** TSE, dados abertos, votacao_partido_munzona_2026.zip
- **Feito por:** `scripts/votos_partido_1t.py` → `dados/votos_partido_1t.json`
- **Linhas:** 318.397

| coluna | descrição |
|---|---|
| `uf` | sigla da UF |
| `cd_tse` | código do município no TSE, 5 dígitos (o mesmo de municipios.csv) |
| `municipio` | nome do município pela lista do TSE |
| `cargo_codigo, cargo` | cargo no 1º turno: 3 governador, 5 senador, 6 deputado federal, 7 deputado estadual, 8 deputado distrital (só no DF, no lugar do estadual) |
| `partido_numero, partido_sigla` | número e sigla do partido |
| `federacao_sigla` | federação de que o partido faz parte; vazio fora de federação |
| `votos_nominais` | votos válidos dados a candidatos do partido (QT_VOTOS_NOMINAIS_VALIDOS do TSE) |
| `votos_legenda` | votos válidos dados só ao número do partido, com os nominais convertidos em legenda (QT_TOTAL_VOTOS_LEG_VALIDOS) |
| `votos_validos` | votos válidos do partido: votos_nominais + votos_legenda. A soma do cargo no município é igual aos válidos do resultado oficial. Senador: duas vagas em 2026, cada eleitor votou duas vezes, e os válidos passam do comparecimento |
| `anulados_sub_judice` | votos anulados sub judice (nominais + legenda), fora dos válidos como no resultado oficial; podem mudar com decisão judicial (notas sobre os dados, em Método e fontes) |
| `anulados` | votos anulados (nominais + legenda), fora dos válidos |

## hipoteses.csv

Os testes das hipóteses dos capítulos 1, 3, 4 e 5: o principal e as versões de conferência, com intervalo de 95%, valor-p e classificação.

- **Fonte:** municipios.csv e esquerda_municipios.csv
- **Feito por:** `scripts/inferencia.py` → `dados/inferencia.json`
- **Linhas:** 59

| coluna | descrição |
|---|---|
| `hipotese, capitulo` | a hipótese (H1, H3, H4, H5) e o capítulo em que aparece |
| `cargo` | no capítulo 5, o cargo (deputado federal, deputado estadual ou senador) |
| `versao` | o teste principal ou uma versão de conferência |
| `dentro_dos_estados` | sim: compara municípios do mesmo estado (efeito fixo de UF); não: todos os municípios juntos |
| `peso` | peso de cada município na regressão |
| `variavel, controles` | a variável testada e os controles |
| `n, grupos` | quantos municípios e quantos estados entram |
| `coef, erro_padrao` | coeficiente (pontos de variação da fatia do Lula por ponto da variável; nos complementos, sem hipótese, votos ganhos pelo candidato em % do eleitorado do 1º turno por ponto da variável) e erro padrão agrupado por estado |
| `ic95_inf, ic95_sup` | intervalo de 95% do coeficiente pelo erro agrupado (t com o número de estados menos 1 graus de liberdade) |
| `ic95_selvagem_inf, ic95_selvagem_sup` | intervalo de 95% do bootstrap selvagem, por inversão do teste: o que os gráficos mostram (T32) |
| `p_cr1, p_selvagem` | valor-p do erro agrupado e do bootstrap selvagem por grupo (vazio onde não foi calculado) |
| `r2, r2_tipo` | R² e de que tipo (comum ou dentro dos estados) |
| `efeito_interquartil_pp` | diferença prevista na variação da fatia entre um município no quartil de baixo e um no de cima da variável, em pontos |
| `previsto, classificacao, pequena` | sinal previsto antes das contas, a classificação (confirmada, contrária ou inconclusiva) e se a associação é pequena (menos de 0,5 ponto) |

## de_onde_vieram.csv

De onde vieram os votos novos de cada um, no Brasil, por região e por estado, comparando seções eleitorais da mesma cidade, com o intervalo de 95% e o critério de precisão.

- **Fonte:** TSE, dados abertos e boletins de urna por seção (dados/secoes_presidente.csv.gz)
- **Feito por:** `scripts/secoes_baixar.py`, `scripts/secoes.py`, `scripts/secoes_inferencia.py`, `scripts/inferencia.py` → `dados/inferencia.json`
- **Linhas:** 99

| coluna | descrição |
|---|---|
| `nivel, lugar, n` | Brasil, região ou estado, e quantos municípios entram (com todas as suas seções) |
| `fonte` | a fonte de votos novos: votos dos outros candidatos do 1º turno, variação do comparecimento ou queda de brancos e nulos |
| `lula, lula_ic95_inf, lula_ic95_sup` | a parte da fonte que ficou, em saldo, com o Lula (de 0 a 1) e o intervalo de 95% por bootstrap (ver a coluna intervalo) |
| `flavio, flavio_ic95_inf, flavio_ic95_sup` | o mesmo para o Flávio (as duas partes somam 1) |
| `meia_largura` | metade da largura do intervalo de 95%, de 0 a 1 |
| `passa_criterio` | sim quando passa no critério de precisão (pelo menos 30 municípios, estimativa entre 0 e 1 e meia largura até 0,10; HIPOTESES.md 4.2, com a ordem do T32) |
| `maior_parte, motivo` | com quem ficou a maior parte, quando passa; o motivo, quando não passa (nota N16) |
| `intervalo` | o que o bootstrap reamostrou: estados inteiros (Brasil e regiões) ou municípios inteiros, com todas as suas seções (estados) |
| `aviso_modelo` | sim quando alguma fonte do lugar sai de 0 a 1: o modelo não descreve bem o lugar, e todas as fontes dele levam o aviso (marca † na página) |

## apuracao_ao_vivo.csv

As leituras gravadas pela página da apuração ao vivo do 2º turno: % apurado, hora, contagem, 1º turno nas mesmas urnas e projeção (capítulo 7 e Apuração ao vivo).

- **Fonte:** leituras gravadas pela página da apuração ao vivo (resultados.tse.jus.br, eleição 6258), 25/10/2026
- **Feito por:** `scripts/collector.py` → `dados/historico_2t.json`
- **Linhas:** 115

| coluna | descrição |
|---|---|
| `urnas_apuradas_pct, hora_tse` | % das urnas apuradas na leitura e a hora da leitura no TSE |
| `lula_2t_pct` | fatia do Lula entre os dois na contagem do 2º turno até aquela leitura, em % |
| `lula_1t_mesmas_urnas_pct` | fatia do Lula no 1º turno nas mesmas urnas já apuradas no 2º, em % |
| `projecao_final_pct` | projeção do resultado final mostrada ao vivo, em % (fatia do Lula) |
| `lula_1t_por_uf_pct` | fatia do Lula no 1º turno nas mesmas urnas tomadas só por estado, em % (conferência da página ao vivo) |

## testes_sociais.csv

Os 35 testes dos dados sociais do capítulo 8 (7 características × 5 medidas), dentro dos estados e no Brasil, com intervalo de 95%, valor-p, valor-p corrigido por Holm e resultado.

- **Fonte:** municipios.csv e dados_sociais.csv
- **Feito por:** `scripts/inferencia.py` → `dados/inferencia.json`
- **Linhas:** 70

| coluna | descrição |
|---|---|
| `variavel, desfecho` | a característica do município e a medida da eleição: ds (variação da fatia do Lula), gL e gF (votos ganhos pelo Lula e pelo Flávio, em % do eleitorado do 1º turno), cap (parte do Lula nos votos a mais dos dois) e da (variação da abstenção) |
| `dentro_dos_estados` | sim: compara municípios do mesmo estado (a versão que decide); não: todos os municípios juntos |
| `n, grupos` | quantos municípios e quantos estados entram |
| `coef, erro_padrao` | coeficiente (pontos da medida por 1 ponto da característica; por 1 unidade de logaritmo no PIB por habitante e na densidade) e erro padrão agrupado por estado |
| `ic95_inf, ic95_sup` | intervalo de 95% do coeficiente pelo erro agrupado |
| `ic95_selvagem_inf, ic95_selvagem_sup` | intervalo de 95% do bootstrap selvagem, por inversão do teste |
| `p_cr1, p_selvagem` | valor-p do erro agrupado e do bootstrap selvagem |
| `p_holm, p_cr1_holm` | os dois valores-p corrigidos pelo método de Holm nos 35 testes da mesma versão |
| `efeito_interquartil` | diferença prevista na medida entre um município no quartil de baixo e um no de cima da característica, em pontos |
| `associacao, direcao, pequena` | sim quando os dois valores-p corrigidos ficam abaixo de 0,05; a direção (positiva ou negativa) e se é pequena (menos de 0,5 ponto entre quartis) |

## dados_sociais.csv

As 7 características de cada município do capítulo 8 (IBGE, Censo 2022 e PIB dos Municípios 2023), com as bases de cada uma.

- **Fonte:** IBGE: Censo 2022 (SIDRA), PIB dos Municípios 2023, Áreas Territoriais 2022
- **Feito por:** `scripts/sociais_baixar.py`, `scripts/dados_sociais.py` → `dados/dados_sociais_municipios.json`
- **Linhas:** 5.571

| coluna | descrição |
|---|---|
| `cd_tse, cd_ibge, uf, municipio` | código do município no TSE (5 dígitos) e no IBGE (7 dígitos), UF e nome |
| `pct_60mais` | % da população residente com 60 anos ou mais (Censo 2022) |
| `alfab_15mais` | taxa de alfabetização das pessoas de 15 anos ou mais, em %, como publicada pelo IBGE (Censo 2022) |
| `pct_renda_ate_meio_sm` | % de moradores em domicílios particulares permanentes com rendimento domiciliar per capita de até meio salário mínimo, com os sem rendimento (Censo 2022, amostra) |
| `pib_pc, ln_pib_pc` | PIB por habitante de 2023, em reais, como publicado pelo IBGE, e o logaritmo natural dele, que é o usado nos testes |
| `densidade, ln_densidade` | habitantes por km² (Censo 2022), como publicada pelo IBGE, e o logaritmo natural, usado nos testes |
| `pct_evangelicos` | % de evangélicos entre as pessoas de 10 anos ou mais (Censo 2022, amostra; nota N19) |
| `pct_pretos_pardos` | % de pretos e pardos na população residente (Censo 2022) |
| `pop, pop15, pop10, area_km2, pib_mil` | as bases: população residente, de 15 anos ou mais e de 10 anos ou mais, área em km² e PIB de 2023 em mil reais; tudo vazio em Boa Esperança do Norte (MT), nota N20 |
