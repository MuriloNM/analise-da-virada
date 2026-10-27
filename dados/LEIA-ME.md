# dados/: as bases como os scripts gravam

Os arquivos que os scripts de `../scripts/` gravam, sem nenhuma mudança. Para abrir numa planilha, prefira `../planilha/`, que tem os mesmos números no formato do Excel; o que é cada coluna está em [`../DICIONARIO.md`](../DICIONARIO.md).

Formato: CSV com vírgula entre os campos e ponto decimal, UTF-8; JSON em UTF-8. Nas bases municipais, a chave do município é o código do TSE, com 5 dígitos (pode começar com zero). Percentuais calculados só entre Lula (13) e Flávio Bolsonaro (22), a não ser quando o nome da coluna diz outra coisa. Os arquivos brutos do TSE e do IBGE não estão aqui: os scripts baixam de novo (`../scripts/LEIA-ME.md`).

| Arquivo | O que é | Feito por |
|---|---|---|
| `tse_config/mun-e006258-cm.json`, `tse_config/ele-c.json` | A lista de municípios do TSE (5.757, com os 186 do exterior) e a configuração das eleições, como vieram de `resultados.tse.jus.br` | TSE |
| `base_1t_municipios.json` | Resultado final do 1º turno no Brasil, nas UFs e nos 5.757 municípios: eleitorado (`te`), comparecimento (`c`), válidos (`vv`), Lula (`L`) e Flávio (`F`) | `base1t.py` |
| `base_2t_municipios.json` | O mesmo para o 2º turno, mais brancos (`vb`) e nulos (`tvn`) | `base2t.py`, conferido por `confere2t.py` |
| `analise_municipios.csv` | Os dois turnos lado a lado por município, com região, capital ou interior, porte e os indicadores (fatia, variações, diferença, peso na virada, captura, de onde vieram os votos, abstenção) | `analise_base.py` |
| `analise_estados.csv` | As mesmas colunas para o Brasil, as 5 regiões, o exterior e as UFs (coluna `nivel`) | `analise_base.py` |
| `analise_compacta.json` | Só as contagens, por município, UF, região e Brasil, com as fórmulas e as faixas de porte no `meta` (é o que a página lê) | `analise_base.py` |
| `votos_partido_1t.json` | Votos válidos por partido e federação no 1º turno, para governador, senador e deputados, por município, estado e Brasil. Cada partido: [nominais, legenda]; anulados e sub judice à parte. Campos e ressalvas no `meta` | `votos_partido_1t.py` |
| `escala_partidos.csv` | Os 30 partidos de 2026 com a posição de esquerda a direita (0 a 10) da pesquisa com especialistas, a categoria, o campo da esquerda, a regra aplicada e as conferências | `escala_partidos.py` |
| `esquerda_1t_municipios.csv` | Voto no campo da esquerda, escala contínua e vantagem potencial no 1º turno, por município, estado e Brasil e por cargo | `escala_partidos.py` |
| `escala_fontes/` | As bases da escala como vieram do Harvard Dataverse (licença CC0): Bolognesi, Ribeiro, Codato e Silva (doi:10.7910/DVN/MFIXKW) e Zucco e Power (doi:10.7910/DVN/6KVTUV, conferência) | Harvard Dataverse |
| `secoes_presidente.csv.gz` | Presidente por seção eleitoral nos dois turnos (499.248 seções, as mesmas nos dois), compactado em gzip (41,6 MB aberto). Campos e conferências em `secoes_presidente_meta.json` | `secoes.py` |
| `dados_sociais_municipios.json` | As 7 características dos 5.571 municípios do Brasil (idade, alfabetização, renda, PIB per capita, densidade, religião, cor ou raça), com o ano, a fonte e o universo de cada uma no `meta` | `dados_sociais.py` |
| `secoes_inferencia.json` | De onde vieram os votos de cada um (comparecimento, outros candidatos, brancos e nulos), comparando seções da mesma cidade, no Brasil, nas regiões e nos estados | `secoes_inferencia.py` |
| `inferencia.json` | Tudo que tem incerteza: as hipóteses (coeficiente, intervalo de 95%, valor-p, classificação), a regressão ecológica, o funil, o erro da projeção da noite e os 35 testes dos dados sociais | `inferencia.py` |
| `exploracao.json` | As cinco perguntas da exploração guiada (capítulo 9) | `exploracao.py` |
| `historico_2t.json`, `historico_2t.csv` | A noite do 2º turno, uma linha por leitura (8,31% a 100% das urnas, 19:34 a 23:27 no horário do TSE): % apurado, % do Lula na contagem, % do Lula no 1º turno nas mesmas urnas, projeção final, hora do TSE e 1º turno ponderado por UF. Há um trecho sem leituras entre 60,85% e 68,8% | `collector.py`, na noite |
| `ultimo_retrato_2t.json` | O último retrato completo gravado na noite (Brasil, UFs e 40 maiores municípios), com 99,77% apurado | `collector.py`, na noite |
| `base_1t_compacta.json` | O 1º turno resumido que a página da noite usava (UFs e os 300 maiores municípios), com a curva da contagem do 1º turno pela hora de chegada dos boletins (`t1c`) | `curva1t.py` |
| `proveniencia/` | O registro dos downloads brutos (endereço, data e hora, bytes e sha256): os dados por seção do TSE e as tabelas do IBGE. O do zip de votos por partido está no `meta.arquivo` de `votos_partido_1t.json` | `secoes_baixar.py`, `sociais_baixar.py` |
