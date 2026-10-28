# Análise da virada: dados e scripts

**English:** [README.en.md](README.en.md)

Os dados tratados e os scripts do estudo **[Análise da virada](https://analise-da-virada.pages.dev/)**: o que mudou do 1º para o 2º turno da eleição presidencial de 2026, por estado e município. Entre os votos dados aos dois candidatos, o Lula passou de 48,99% para 51,79%, e o Flávio Bolsonaro, de 51,01% para 48,21%. O estudo mostra onde e quanto isso mudou, com os dados oficiais do TSE, o mesmo tratamento para os dois e sem atribuir causas.

Aqui está tudo para conferir as contas ou fazer o seu próprio estudo, sem precisar reprocessar os arquivos brutos do TSE: os CSV prontos para planilha, as bases que os scripts gravam, os scripts que refazem tudo a partir das fontes, o código da página e o registro das hipóteses, escrito antes das contas. Uma IA também consegue fazer esse trabalho com você, perguntando, revisando ou continuando o estudo: veja [`PERGUNTE-A-SUA-IA.md`](PERGUNTE-A-SUA-IA.md).

## O que tem aqui

| Pasta ou arquivo | O que é |
|---|---|
| [`planilha/pt-BR/`](planilha/pt-BR/) | Os CSV para abrir no Excel em português (ponto e vírgula entre os campos, vírgula decimal). São os mesmos que a página oferece em "Baixar os dados", mais `votos_partido_1t.csv` |
| [`planilha/en/`](planilha/en/) | Os mesmos números, com cabeçalhos em inglês, vírgula entre os campos e ponto decimal |
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

> MARTINS, Murilo Neves de. **Análise da virada**: o que mudou do 1º para o 2º turno da eleição presidencial de 2026, por estado e município. Versão 1.0.2. [S. l.], 27 out. 2026. Disponível em: https://analise-da-virada.pages.dev/. Dados e scripts: https://github.com/MuriloNM/analise-da-virada.

APA: Martins, M. N. de (2026). *Análise da virada: o que mudou do 1º para o 2º turno da eleição presidencial de 2026, por estado e município* (Versão 1.0.2). https://analise-da-virada.pages.dev/

O GitHub também mostra a citação pelo botão "Cite this repository" (arquivo [`CITATION.cff`](CITATION.cff)).

## Licenças

- **Dados tratados** (`dados/`, `planilha/`, os dicionários e o registro das hipóteses): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.pt_BR). Pode copiar, adaptar e redistribuir, inclusive para uso comercial, citando o estudo.
- **Código** (`scripts/` e `site-analise/`): [MIT](LICENSE). As fontes tipográficas da página têm a licença SIL OFL 1.1 (`site-analise/fontes/`), e as fotos dos candidatos são as divulgadas pelo TSE.
- **Dados de origem** do TSE e do IBGE: são dados públicos, com as condições de uso de cada órgão; cite a fonte. As bases da escala dos partidos (Harvard Dataverse) têm licença CC0.

Detalhes em [`LICENCA-DADOS.md`](LICENCA-DADOS.md).

## Versão e correções

**Versão 1.0.2, de 27/10/2026**: a primeira publicada, com uma correção de texto e a parte "Pergunte aos dados". A mesma versão da página e do PDF.

Achou um erro? Abra um pedido em [Issues](../../issues) ("Achei um erro") ou escreva pela caixa "Escrever ao autor", na página. Cada correção entra aqui e em "Versão e correções", na página, com a data, o que mudou e, se a pessoa quiser, quem avisou.

| Versão | Data | O que mudou |
|---|---|---|
| 1.0.2 | 27/10/2026 | Novo na página: "Pergunte aos dados", no Explorar, e cada endereço abre na sua língua. Nenhum número, medida ou hipótese mudou. |
| 1.0.1 | 27/10/2026 | Revisão de neutralidade: a manchete, a linha fina e 33 trechos reescritos sem o ponto de vista de um dos candidatos. Nenhum número, medida ou hipótese mudou. |
| 1.0 | 27/10/2026 | Primeira versão publicada |

## Sobre

Estudo independente de Murilo Neves de Martins ([LinkedIn](https://www.linkedin.com/in/murilomartins/)), sem vínculo com partido, candidato ou campanha. A maior parte do trabalho (código, contas e rascunho dos textos) foi feita com o Claude, da Anthropic; as perguntas, as regras fixadas antes das contas e cada decisão sobre os dados passaram pelo autor. Mais em "Sobre este estudo", na página.
