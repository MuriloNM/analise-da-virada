# Análise da virada: dados e scripts

**English:** [README.en.md](README.en.md) · **Español:** o estudo em [analise-da-virada.pages.dev/es/](https://analise-da-virada.pages.dev/es/); dicionário em [DICCIONARIO.md](DICCIONARIO.md) · **简体中文:** o estudo em [analise-da-virada.pages.dev/zh/](https://analise-da-virada.pages.dev/zh/); dicionário em [SHUJU-ZIDIAN.md](SHUJU-ZIDIAN.md)

Os dados tratados e os scripts do estudo **[Análise da virada](https://analise-da-virada.pages.dev/)**: o que mudou do 1º para o 2º turno da eleição presidencial de 2026, por estado e município. Entre os votos dados aos dois candidatos, o Lula passou de 48,99% para 51,79%, e o Flávio Bolsonaro, de 51,01% para 48,21%. O estudo mostra onde e quanto isso mudou, com os dados oficiais do TSE, o mesmo tratamento para os dois e sem atribuir causas.

Aqui está tudo para conferir as contas ou fazer o seu próprio estudo, sem precisar reprocessar os arquivos brutos do TSE: os CSV prontos para planilha, as bases que os scripts gravam, os scripts que refazem tudo a partir das fontes, o código da página e o registro das hipóteses, escrito antes das contas. Uma IA também consegue fazer esse trabalho com você, perguntando, revisando ou continuando o estudo: veja [`PERGUNTE-A-SUA-IA.md`](PERGUNTE-A-SUA-IA.md).

## O que tem aqui

| Pasta ou arquivo | O que é |
|---|---|
| [`planilha/pt-BR/`](planilha/pt-BR/) | Os CSV para abrir no Excel em português (ponto e vírgula entre os campos, vírgula decimal). São os mesmos que a página oferece em "Baixar os dados", mais `votos_partido_1t.csv` |
| [`planilha/en/`](planilha/en/) | Os mesmos números, com cabeçalhos em inglês, vírgula entre os campos e ponto decimal |
| [`planilha/es/`](planilha/es/) | Os mesmos números, com cabeçalhos em espanhol, ponto e vírgula entre os campos e vírgula decimal |
| [`planilha/zh-Hans/`](planilha/zh-Hans/) | Os mesmos números, com cabeçalhos em chinês simplificado, vírgula entre os campos e ponto decimal |
| [`DICIONARIO.md`](DICIONARIO.md) | Cada coluna de cada CSV: descrição, unidade, fórmula, fonte e o script que a faz (também em `planilha/*/dicionario.csv`) |
| [`dados/`](dados/) | As bases como os scripts gravam (CSV com ponto decimal, JSON e as seções em `.csv.gz`). Guia em [`dados/LEIA-ME.md`](dados/LEIA-ME.md) |
| [`scripts/`](scripts/) | Os scripts em Python que baixam as fontes e refazem as bases, na ordem. Guia em [`scripts/LEIA-ME.md`](scripts/LEIA-ME.md) |
| [`site-analise/`](site-analise/) | O código da página do estudo (HTML, CSS e JavaScript; os textos em `site-analise/textos/`). Os scripts da página a refazem a partir de `dados/` |
| [`docs/analise/HIPOTESES.md`](docs/analise/HIPOTESES.md) | O registro das hipóteses e das regras de cada teste, fixadas antes das contas, com as mudanças posteriores datadas |
| [`docs/analise/NOTAS.md`](docs/analise/NOTAS.md) | As notas sobre os dados (N01, N02…): o que aconteceu com um dado e como foi tratado |
| [`PERGUNTE-A-SUA-IA.md`](PERGUNTE-A-SUA-IA.md) | Textos prontos para colar no ChatGPT, Claude, Gemini ou outra IA: para perguntar ao estudo, para revisá-lo como um segundo par de olhos e para refazê-lo ou continuá-lo |
| [`AGENTS.md`](AGENTS.md) | O guia para a IA que vai trabalhar com o repositório: mapa, como os dados passam de um script para outro, como ler cada arquivo, a lista de conferências de um revisor e as regras do estudo |
| [`SHA256SUMS.txt`](SHA256SUMS.txt) | A impressão digital de cada arquivo de dados, para conferir se a sua cópia é igual à original |

## Totais para conferir

Se a soma da coluna de um arquivo baixado bater com estes totais, o arquivo está completo. Brasil e exterior juntos, 5.757 municípios (5.571 no Brasil e 186 no exterior):

| | 1º turno | 2º turno |
|---|---:|---:|
| Lula (`lula_1t`, `lula_2t`) | 53.879.538 | 64.256.232 |
| Flávio Bolsonaro (`flavio_1t`, `flavio_2t`) | 56.104.503 | 59.826.041 |
| Votos válidos (`validos_1t`, `validos_2t`) | 119.300.788 | 124.082.273 |
| Comparecimento (`comparecimento_1t`, `comparecimento_2t`) | 125.275.835 | 128.236.074 |
| Eleitorado (`eleitorado_1t`, `eleitorado_2t`) | 158.745.502 | 158.745.502 |

As seções eleitorais (`dados/secoes_presidente.csv.gz`) são 499.248 e somam os mesmos totais. Para conferir tudo de uma vez, inclusive as impressões digitais:

```
python scripts/conferir_totais.py
```

## Fontes

- **TSE, resultados oficiais** do 1º e do 2º turno (eleições 6257 e 6258) e dos cargos estaduais (6259), em `resultados.tse.jus.br`.
- **TSE, dados abertos** (`cdn.tse.jus.br/estatistica/sead/odsele/`): votação por partido e município (`votacao_partido_munzona_2026.zip`), votação e detalhe por seção, e os boletins de urna do 2º turno.
- **IBGE:** Censo 2022 (SIDRA), PIB dos Municípios 2023 e Áreas Territoriais 2022.
- **Posição dos partidos:** Bolognesi, Ribeiro, Codato e Silva (2025), *Opinião Pública* 31, e31120, [doi:10.1590/1807-0191202531120](https://doi.org/10.1590/1807-0191202531120); dados em [doi:10.7910/DVN/MFIXKW](https://doi.org/10.7910/DVN/MFIXKW).
- **A noite da apuração:** as leituras gravadas pela página que acompanhou a contagem do 2º turno em 25/10/2026 ([apuracao-mesmas-urnas.pages.dev](https://apuracao-mesmas-urnas.pages.dev/)).

O endereço, a data e hora e a conferência de cada fonte estão em "Fontes", em Método e fontes, na página do estudo, e em [`dados/proveniencia/`](dados/proveniencia/).

## Limites

O que os dados não permitem dizer está em "Limites do estudo", na página. Em resumo:

- **Lugares, não pessoas.** Os dados são contagens por município e por seção. Uma associação entre lugares não diz como votou cada eleitor.
- **Onde e quanto, não por quê.** O estudo não atribui causas.
- **Saldo, não caminho.** As contas de onde vieram os votos dão o saldo de cada fonte, não o caminho de cada eleitor.
- **Estimativas com incerteza.** As regressões e as estimativas de onde vieram os votos têm intervalo de 95% e um critério de precisão; o que não passa no critério fica como "sem lado claro".
- **Não é o resultado oficial.** O oficial é o do TSE.

## Como citar

> MARTINS, Murilo Neves de. **Análise da virada**: o que mudou do 1º para o 2º turno da eleição presidencial de 2026, por estado e município. Versão 1.3.4. [S. l.], 31 out. 2026. Disponível em: https://analise-da-virada.pages.dev/. Dados e scripts: https://github.com/MuriloNM/analise-da-virada.

APA: Martins, M. N. de (2026). *Análise da virada: o que mudou do 1º para o 2º turno da eleição presidencial de 2026, por estado e município* (Versão 1.3.4). https://analise-da-virada.pages.dev/

O GitHub também mostra a citação pelo botão "Cite this repository" (arquivo [`CITATION.cff`](CITATION.cff)).

## Licenças

- **Dados tratados** (`dados/`, `planilha/`, os dicionários e o registro das hipóteses): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.pt_BR). Pode copiar, adaptar e redistribuir, inclusive para uso comercial, citando o estudo.
- **Código** (`scripts/` e `site-analise/`): [MIT](LICENSE). As fontes tipográficas da página têm a licença SIL OFL 1.1 (`site-analise/fontes/`), e as fotos dos candidatos são as divulgadas pelo TSE.
- **Dados de origem** do TSE e do IBGE: são dados públicos, com as condições de uso de cada órgão; cite a fonte. As bases da escala dos partidos (Harvard Dataverse) têm licença CC0.

Detalhes em [`LICENCA-DADOS.md`](LICENCA-DADOS.md).

## Versão e correções

**Versão 1.3.4, de 31/10/2026**: a primeira publicada, com uma correção de texto, a parte "Pergunte aos dados", o assistente "Pergunte ao estudo", gráficos com a tabela a um clique, o Mapa, a parte "Estudos externos", as regras dos comentários (que abrem depois) a 2ª rodada da exploração guiada, sobre quem votou e quem faltou, por idade, e, no capítulo 7, as projeções da apuração refeitas pela hora de chegada dos boletins, com a parte "Métodos parecidos", e o estudo inteiro em espanhol e em chinês simplificado, com a tradução chinesa revisada. A mesma versão da página e do PDF.

Achou um erro? Abra um pedido em [Issues](../../issues) ("Achei um erro") ou escreva pela caixa "Escrever ao autor", na página. Cada correção entra aqui e em "Versão e correções", na página, com a data, o que mudou e, se a pessoa quiser, quem avisou.

| Versão | Data | O que mudou |
|---|---|---|
| 1.3.4 | 31/10/2026 | Correção de texto, sem mudar nenhum número nem conclusão: na tabela de partidos, a nota sobre 2018 diz que a UP ainda não existia (por isso o campo da esquerda teria 8 partidos em vez de 11); nos estudos externos, "211 viradas para o Lula; uma para o Flávio". Também: três ajustes de redação em chinês e, nos gráficos com um nome por linha, a margem que cabe o nome mais comprido, em todas as línguas. |
| 1.3.3 | 31/10/2026 | Revisão da tradução em chinês, sem mudar nenhum número nem conclusão: leitura direta do chinês contra o português, chave a chave, com 125 correções de sentido local, terminologia e redação em https://analise-da-virada.pages.dev/zh/ e nos estudos externos (e `planilha/zh-Hans/` aqui). Feita por IA, ainda sem revisão de um falante nativo. |
| 1.3.2 | 30/10/2026 | Nova língua, sem mudar nenhum número nem conclusão: o estudo inteiro em chinês simplificado, com o PDF, em https://analise-da-virada.pages.dev/zh/ (e `planilha/zh-Hans/`, `SHUJU-ZIDIAN.md` aqui). A tradução foi feita por IA e conferida por tradução de volta e pelos números, sem revisão de um falante nativo. |
| 1.3.1 | 30/10/2026 | Nova língua, sem mudar nenhum número nem conclusão: o estudo inteiro em espanhol, com o PDF, em https://analise-da-virada.pages.dev/es/ (e `planilha/es/`, `DICCIONARIO.md` aqui). Na versão em inglês, o título de uma nota e a linha da versão 1.3, que tinham ficado em português, agora estão em inglês. |
| 1.3 | 29/10/2026 | Análise nova, exploratória, sem mudar nenhum número dos capítulos 1 a 6 nem das hipóteses: a apuração do 2º turno refeita pela hora em que o TSE recebeu cada boletim (o buraco do histórico preenchido, os estados leitura a leitura e a causa do salto da projeção às 19:43:31) e projeções que acertam o vencedor desde as primeiras urnas, testadas em 2022, 2018 e 2024 (capítulo 7, Figuras 7.2 e 7.3, e um achado no Resumo); a parte "Métodos parecidos" em Método e fontes; e a hora junto da data nas verificações dos estudos externos. Scripts novos: `reconstrucao_2t.py`, `projecoes_*.py`, `regra_*.py` e os `baixar_*.py` de 2018, 2022, 2024 e das pesquisas. |
| 1.2 | 28/10/2026 | Análise nova, exploratória: a 2ª rodada da exploração guiada no capítulo 9, com cinco perguntas sobre quem votou e quem faltou, por idade (perfil de comparecimento do TSE, só do 1º turno, e perfil do eleitorado por seção), registradas antes das contas (`docs/analise/HIPOTESES.md`, seção 8), e a nota N24. Dados e scripts novos: `perfil_idade*`. Nenhum número dos capítulos 1 a 8 mudou. |
| 1.1.2 | 28/10/2026 | Novo na página: as regras dos comentários, no fim do estudo (os comentários abrem depois), uma contagem de uso sem nenhum dado pessoal (downloads do PDF, partes e capítulos abertos, buscas da cidade) e a página de privacidade atualizada. Nenhum número, medida ou hipótese mudou. |
| 1.1.1 | 28/10/2026 | Novo na página: em Método e fontes, a parte "Estudos externos" compara, tema por tema, estudos de outras fontes sobre a mesma mudança com o que este estudo encontrou, com o link de cada um e a data da última verificação. Nenhum número, medida ou hipótese mudou. |
| 1.1 | 28/10/2026 | Novo na página: as tabelas do estudo ganharam um gráfico ao lado, com a mesma informação em tabela a um clique, e o menu ganhou o Mapa, para passear pelos estados e municípios. Nenhum número, medida ou hipótese mudou. |
| 1.0.3 | 27/10/2026 | Novo na página: o botão "Pergunte ao estudo", um assistente de inteligência artificial que lê o estudo inteiro e responde citando o trecho onde conferir; cada número da resposta é conferido com o estudo antes de sair. Nenhum número, medida ou hipótese mudou. |
| 1.0.2 | 27/10/2026 | Novo na página: "Pergunte aos dados", no Explorar, e cada endereço abre na sua língua. Nenhum número, medida ou hipótese mudou. |
| 1.0.1 | 27/10/2026 | Revisão de neutralidade: a manchete, a linha fina e 33 trechos reescritos sem o ponto de vista de um dos candidatos. Nenhum número, medida ou hipótese mudou. |
| 1.0 | 27/10/2026 | Primeira versão publicada |

## Sobre

Estudo independente de Murilo Neves de Martins ([LinkedIn](https://www.linkedin.com/in/murilomartins/)), sem vínculo com partido, candidato ou campanha. A maior parte do trabalho (código, contas e rascunho dos textos) foi feita com o Claude, da Anthropic; as perguntas, as regras fixadas antes das contas e cada decisão sobre os dados passaram pelo autor. Mais em "Sobre este estudo", na página.
