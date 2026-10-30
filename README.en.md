# Brazil's runoff reversal: data and scripts

**Português:** [README.md](README.md)

The processed data and the scripts of the study **[Brazil's runoff reversal](https://analise-da-virada.pages.dev/en/)**: what changed from the first round to the runoff of the 2026 presidential election, by state and municipality. Among the votes cast for the two candidates, Lula went from 48.99% to 51.79%, and Flávio Bolsonaro from 51.01% to 48.21%. The study shows where and by how much this changed, with the official TSE (Superior Electoral Court) data, the same treatment for both candidates and without attributing causes.

Everything needed to check the calculations or run your own study is here, without reprocessing the raw TSE files: spreadsheet-ready CSV files, the datasets the scripts write, the scripts that rebuild everything from the sources, the code of the page, and the record of the hypotheses, written before the calculations. An AI can also do this work with you, asking, reviewing or extending the study: see [`ASK-YOUR-AI.md`](ASK-YOUR-AI.md).

## What is here

| Folder or file | What it is |
|---|---|
| [`planilha/en/`](planilha/en/) | CSV files for Excel in English (commas between fields, dot for decimals). The same files the page offers under "Download the data", plus `votos_partido_1t.csv` |
| [`planilha/pt-BR/`](planilha/pt-BR/) | The same numbers with Portuguese headers, semicolons between fields and a decimal comma |
| [`DATA-DICTIONARY.md`](DATA-DICTIONARY.md) | Every column of every CSV: description, unit, formula, source and the script that makes it (also in `planilha/*/dicionario.csv`) |
| [`dados/`](dados/) | The datasets as the scripts write them (CSV with a decimal dot, JSON and the polling stations in `.csv.gz`). Guide (in Portuguese) in [`dados/LEIA-ME.md`](dados/LEIA-ME.md) |
| [`scripts/`](scripts/) | The Python scripts that download the sources and rebuild the datasets, in order. Guide (in Portuguese) in [`scripts/LEIA-ME.md`](scripts/LEIA-ME.md) |
| [`site-analise/`](site-analise/) | The code of the study page (HTML, CSS and JavaScript; texts in `site-analise/textos/`). The page scripts rebuild it from `dados/` |
| [`docs/analise/HIPOTESES.md`](docs/analise/HIPOTESES.md) | The record of the hypotheses and of the rules of each test, set before the calculations, with later changes dated (in Portuguese) |
| [`docs/analise/NOTAS.md`](docs/analise/NOTAS.md) | The notes on the data (N01, N02…): what happened to a piece of data and how it was handled (in Portuguese) |
| [`ASK-YOUR-AI.md`](ASK-YOUR-AI.md) | Ready-made prompts for ChatGPT, Claude, Gemini or another AI: to ask the study questions, to review it as a second pair of eyes, and to rebuild or extend it |
| [`AGENTS.md`](AGENTS.md) | The guide for an AI working with the repository: map, how the data flow from script to script, how to read each file, a reviewer's checklist and the study's rules (in Portuguese, with an English summary) |
| [`SHA256SUMS.txt`](SHA256SUMS.txt) | The fingerprint of each data file, to check that your copy matches the original |

File and column names are in Portuguese in `dados/` and in the scripts; `DATA-DICTIONARY.md` translates them.

## Totals to check

If the sum of a column in a downloaded file matches these totals, the file is complete. Brazil and abroad together, 5,757 municipalities (5,571 in Brazil and 186 abroad):

| | First round | Runoff |
|---|---:|---:|
| Lula (`lula_r1`, `lula_r2`) | 53,879,538 | 64,256,232 |
| Flávio Bolsonaro (`flavio_r1`, `flavio_r2`) | 56,104,503 | 59,826,041 |
| Valid votes (`valid_votes_r1`, `valid_votes_r2`) | 119,300,788 | 124,082,273 |
| Turnout (`turnout_r1`, `turnout_r2`) | 125,275,835 | 128,236,074 |
| Electorate (`electorate_r1`, `electorate_r2`) | 158,745,502 | 158,745,502 |

The polling stations (`dados/secoes_presidente.csv.gz`) number 499,248 and add up to the same totals. To check everything at once, fingerprints included:

```
python scripts/conferir_totais.py
```

## Sources

- **TSE, official results** of the first round and the runoff (elections 6257 and 6258) and of the state offices (6259), at `resultados.tse.jus.br`.
- **TSE, open data** (`cdn.tse.jus.br/estatistica/sead/odsele/`): votes by party and municipality (`votacao_partido_munzona_2026.zip`), votes and details by polling station, and the runoff voting machine reports.
- **IBGE** (Brazilian Institute of Geography and Statistics): 2022 Census (SIDRA), Municipal GDP 2023 and Territorial Areas 2022.
- **Party placement:** Bolognesi, Ribeiro, Codato and Silva (2025), *Opinião Pública* 31, e31120, [doi:10.1590/1807-0191202531120](https://doi.org/10.1590/1807-0191202531120); data at [doi:10.7910/DVN/MFIXKW](https://doi.org/10.7910/DVN/MFIXKW).
- **Election night:** the readings recorded by the page that followed the runoff count on 25 October 2026 ([apuracao-mesmas-urnas.pages.dev](https://apuracao-mesmas-urnas.pages.dev/)).

The address, date and time and the check of each source are under "Sources", in Method and sources, on the study page, and in [`dados/proveniencia/`](dados/proveniencia/).

## Limitations

What the data do not allow us to say is under "Limitations of the study", on the page. In short:

- **Places, not people.** The data are counts by municipality and polling station. An association between places does not say how each voter voted.
- **Where and how much, not why.** The study does not attribute causes.
- **Net balance, not paths.** The calculations of where the votes came from give the net balance of each source, not the path of each voter.
- **Estimates with uncertainty.** The regressions and the estimates of where the votes came from have a 95% confidence interval and a precision criterion; what fails the criterion is reported as having no clear side.
- **Not the official result.** The official one is the TSE's.

## How to cite

Martins, M. N. de (2026). *Brazil's runoff reversal: what changed from the first round to the runoff of the 2026 presidential election, by state and municipality* (Version 1.3). https://analise-da-virada.pages.dev/en/. Data and scripts: https://github.com/MuriloNM/analise-da-virada

GitHub also shows the citation through the "Cite this repository" button ([`CITATION.cff`](CITATION.cff)).

## Licenses

- **Processed data** (`dados/`, `planilha/`, the dictionaries and the record of the hypotheses): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). You may copy, adapt and redistribute them, including for commercial use, with credit to the study.
- **Code** (`scripts/` and `site-analise/`): [MIT](LICENSE). The page fonts are under the SIL OFL 1.1 license (`site-analise/fontes/`), and the candidate photos are those released by the TSE.
- **Source data** from the TSE and IBGE: public data, under each agency's terms of use; cite the source. The party-scale datasets (Harvard Dataverse) are CC0.

Details in [`LICENCA-DADOS.md`](LICENCA-DADOS.md).

## Version and corrections

**Version 1.3, 29 October 2026**: the first published version, with a text correction, the "Ask the data" section, the "Ask the study" assistant, charts with the table one click away, the Map, the "External studies" section, the comment rules (comments open later) the second round of the guided exploration, on who voted and who stayed away, by age, and, in chapter 7, the projections of the count recomputed from the time each voting machine report arrived, with the "Similar methods" section. The same version as the page and the PDF.

Found an error? Open an [issue](../../issues) ("I found an error") or write through the "Write to the author" box on the page. Every correction goes here and into "Version and corrections" on the page, with the date, what changed and, if the person wishes, who reported it.

## About

An independent study by Murilo Neves de Martins ([LinkedIn](https://www.linkedin.com/in/murilomartins/)), with no ties to any party, candidate or campaign. Most of the work (code, calculations and draft texts) was done with Claude, by Anthropic; the questions, the rules set before the calculations and every decision about the data went through the author. More under "About this study", on the page.
