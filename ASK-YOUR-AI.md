# Use the study with your AI

**Português:** [PERGUNTE-A-SUA-IA.md](PERGUNTE-A-SUA-IA.md)

Three ways to use the study **[Brazil's runoff reversal](https://analise-da-virada.pages.dev/en/)** with ChatGPT, Claude, Gemini or another AI:

1. **Ask** (any chat): the text right below.
2. **Review, as a second pair of eyes:** the AI checks the numbers against the sources and reruns the calculations. Section "Review the study".
3. **Rebuild or extend:** the AI rebuilds the datasets and the page from the sources, or runs a new analysis under the same rules. Section "Rebuild or extend".

For 2 and 3 the AI needs to run code: a coding assistant opened on a copy of the repository (Claude Code, Codex, Cursor…) or a chat that runs Python on attached files (ChatGPT data analysis, Claude with files). Its full guide is [`AGENTS.md`](AGENTS.md) (in Portuguese, with an English summary): the repository map, how the data flow from one script to the next, how to read each file and the list of checks. Coding assistants read it on their own.

## Ask

Copy the text in the box below, paste it into a new conversation and write your question at the end.

**If your AI cannot open links** (it says it cannot access the internet, or it makes up numbers): download the files in the table "Which file answers what" (the "Download raw file" button on each one, or "Download the data" on the study page), attach them to the conversation and paste the same text. Start with `municipios.csv`, `estados.csv` and `dicionario.csv`.

**Careful:** the AI may get a calculation wrong or read the wrong column. Check any number that matters in the file or on the study page before using it.

````text
You will answer questions about the study "Brazil's runoff reversal" by Murilo Neves de Martins (version 1.0.2, 27 October 2026): what changed from the first round to the runoff of Brazil's 2026 presidential election, between Lula and Flávio Bolsonaro, by state and municipality. Page: https://analise-da-virada.pages.dev/en/ · Data and scripts: https://github.com/MuriloNM/analise-da-virada

Use only the study's files. Read them at these addresses (plain text):
- Column dictionary: https://raw.githubusercontent.com/MuriloNM/analise-da-virada/main/planilha/en/dicionario.csv
- Municipalities (both rounds side by side, 5,757 rows): https://raw.githubusercontent.com/MuriloNM/analise-da-virada/main/planilha/en/municipios.csv
- Brazil, regions and states: https://raw.githubusercontent.com/MuriloNM/analise-da-virada/main/planilha/en/estados.csv
- Hypotheses tested: https://raw.githubusercontent.com/MuriloNM/analise-da-virada/main/planilha/en/hipoteses.csv
- Where each candidate's vote gains came from: https://raw.githubusercontent.com/MuriloNM/analise-da-virada/main/planilha/en/de_onde_vieram.csv
- Social data of the municipalities and the 35 tests: https://raw.githubusercontent.com/MuriloNM/analise-da-virada/main/planilha/en/dados_sociais.csv and https://raw.githubusercontent.com/MuriloNM/analise-da-virada/main/planilha/en/testes_sociais.csv
- Parties and the left-bloc vote: https://raw.githubusercontent.com/MuriloNM/analise-da-virada/main/planilha/en/partidos.csv and https://raw.githubusercontent.com/MuriloNM/analise-da-virada/main/planilha/en/esquerda_municipios.csv
- Election night: https://raw.githubusercontent.com/MuriloNM/analise-da-virada/main/planilha/en/apuracao_ao_vivo.csv
- Rules of the tests, set before the calculations (in Portuguese): https://raw.githubusercontent.com/MuriloNM/analise-da-virada/main/docs/analise/HIPOTESES.md

The CSV files use commas between fields and a dot for decimals; percentages are already multiplied by 100; an empty cell is a calculation with no value. The TSE code (tse_code) has 5 digits and may start with a zero: read it as text. Rows with state "ZZ" are abroad.

To check that you read the whole files: the sum of lula_r2 in municipios.csv is 64,256,232 and that of flavio_r2 is 59,826,041. If it does not match, say you could not read the complete file and do not answer with numbers.

Rules for the answer:
1. The data are counts by place (municipality, state, polling station), not by person. Never say how a voter or a group of people voted or switched: say what happened in the place ("in the municipalities where…"). The calculations of where the votes came from give the net balance of each source, not the path of each voter.
2. Do not attribute causes (campaign, debate, alliance, social media, economy). The study says where and how much, not why.
3. Treat both candidates the same way: whatever you say about one, the same question applies to the other, in the same words.
4. Cite the file, column and row (or filter) of every number you use. If you do a calculation, show how.
5. Estimates with a 95% confidence interval that failed the precision criterion have "no clear side": do not treat them as results.
6. If the files do not answer the question, say so. Do not fill in with knowledge from outside the study without warning.
7. The official result is the TSE's (Superior Electoral Court); the study may contain errors. If you find one, suggest reporting it at https://github.com/MuriloNM/analise-da-virada/issues

My question:
````

## Which file answers what

| Question | File (in `planilha/en/`) |
|---|---|
| How many votes each candidate got in a municipality, state or region, and how much it changed | `municipios.csv`, `estados.csv` |
| Where did abstention, blank and null votes change? | `municipios.csv`, `estados.csv` |
| Where the extra votes came from (turnout, other candidates, blank and null) | `de_onde_vieram.csv` |
| Were the hypotheses of chapters 1, 3, 4 and 5 confirmed? | `hipoteses.csv` |
| Income, age, religion, race, density and the vote | `dados_sociais.csv`, `testes_sociais.csv` |
| Party votes for deputy and senator in the first round | `votos_partido_1t.csv`, `partidos.csv`, `esquerda_municipios.csv` |
| How the runoff count went on election night | `apuracao_ao_vivo.csv` |
| What each column means | `dicionario.csv` and [`DATA-DICTIONARY.md`](DATA-DICTIONARY.md) |

`votos_partido_1t.csv` is 20 MB: many AIs cannot read a file that size from a link. If you need it, filter the state or municipality in a spreadsheet before attaching it.

## Review the study

To ask an AI to check the work, as a reviewer would. In a coding assistant, first download the repository (`git clone https://github.com/MuriloNM/analise-da-virada`, or "Code" → "Download ZIP" on GitHub) and open the folder in it. In a chat that runs Python, attach the ZIP. Then paste:

````text
You will review the study "Brazil's runoff reversal" (https://analise-da-virada.pages.dev/en/), whose data, scripts and page are in this folder (or in the attached ZIP, from https://github.com/MuriloNM/analise-da-virada). First read AGENTS.md in full (it is in Portuguese, with an English summary; file and column names are in Portuguese, and DATA-DICTIONARY.md translates the columns), and follow section 5.2 ("Revisar", review) item by item. Your goal is to find errors, not to confirm what is written.

Work on a copy: the scripts overwrite files in dados/ and site-analise/. Do not fix anything.

Deliver a table with each check, what you ran or compared and the result (matches / does not match / could not check, and why). For each possible error: the file and row, the number written, what you expected and how you got there. Separate errors of numbers, of method (the technique or the conclusion goes beyond what the data allow) and of wording (a sentence that attributes a cause, talks about people instead of places, or treats one candidate differently from the other).

Answer in English. If you want to focus on one part, do only this: [write it here, e.g. "chapter 4, where the votes came from" or "the 35 social data tests"].
````

Found an error? Open an [issue](https://github.com/MuriloNM/analise-da-virada/issues) with the "I found an error" template, with what the AI found and how you checked.

## Rebuild or extend

To rebuild the datasets and the page, or run a new analysis on the same data, in a coding assistant opened on a copy of the repository:

````text
This folder is the repository of the study "Brazil's runoff reversal" (https://github.com/MuriloNM/analise-da-virada). First read AGENTS.md in full (in Portuguese, with an English summary) and scripts/LEIA-ME.md.

I want: [pick one]
(a) to rebuild the datasets from the TSE and IBGE sources and compare them with those in dados/, file by file;
(b) to rebuild the page from the datasets and open it on my computer;
(c) a new analysis: [describe the question].

For (c): before looking at any number, write down in a dated file the question, the variable, the test, the weights and what counts as a result, following the rules in docs/analise/HIPOTESES.md, and show it to me. Only then run it, in a new script that reads dados/ and writes a new file, without changing the existing ones. Anything done after seeing the data is exploratory: say so.

Throughout: follow the rules in section 6 of AGENTS.md (places, not people; no causes; both candidates treated alike; 95% interval and precision criterion). Download the TSE files slowly, as the scripts already do. Before each long step, say what you are going to do. Answer in English.
````

Anyone who publishes a rebuilt or extended version cites the study (CC BY 4.0 license) and makes clear it is not the author's page.
