# Data dictionary

Português: [DICIONARIO.md](DICIONARIO.md)

The files in `planilha/`, column by column. The files in `planilha/pt-BR/` and `planilha/en/` hold the same numbers; only the header language, the field separator and the decimal mark change. Each column's unit and formula are in its description. This file is generated from `planilha/en/dicionario.csv`.

## municipios.csv

Both rounds side by side in the 5,757 municipalities (5,571 in Brazil and 186 abroad), with the study's indicators.

- **Source:** TSE, official results (resultados.tse.jus.br, elections 6257 and 6258)
- **Made by:** `scripts/base1t.py`, `scripts/base2t.py`, `scripts/analise_base.py` → `dados/analise_municipios.csv`
- **Rows:** 5,757

| column | description |
|---|---|
| `tse_code` | municipality code at the TSE, 5 digits |
| `ibge_code` | municipality code at IBGE, 7 digits; empty abroad |
| `state, municipality` | state abbreviation (ZZ abroad) and municipality name |
| `region` | Norte, Nordeste, Centro-Oeste, Sudeste, Sul or Exterior (North, Northeast, Central-West, Southeast, South or abroad; note N08) |
| `capital_or_interior` | capital, interior or exterior (state capital, rest of the state or abroad; note N08) |
| `size_class, size_band` | size band by first-round registered voters: code from 1 to 5 (X abroad) and name, in Portuguese (note N08) |
| `electorate_r1, electorate_r2` | eligible registered voters in each round (note N05) |
| `turnout_r1, turnout_r2` | turnout (votes cast) |
| `abstentions_r1, abstentions_r2` | abstention: registered voters − turnout |
| `valid_votes_r1, valid_votes_r2` | valid votes |
| `blank_null_r1, blank_null_r2` | blank and null votes: turnout − valid votes (combined in the first round: note N07) |
| `blank_r2, null_r2` | blank and null votes separately, runoff only |
| `lula_r1, flavio_r1, lula_r2, flavio_r2` | votes for each candidate |
| `others_r1` | votes for the other candidates in the first round: valid − Lula − Flávio |
| `lula_share_r1_pct, lula_share_r2_pct` | Lula's share of the two-candidate vote, Lula ÷ (Lula + Flávio), in %; empty when neither got votes (note N09). Flávio's is 100 − share |
| `chg_share_pp` | change in Lula's share, runoff − first round, in percentage points |
| `chg_lula, chg_flavio` | votes gained by each candidate from the first round to the runoff |
| `margin_r1, margin_r2, chg_margin` | margin Lula − Flávio in each round and its change |
| `reversal_weight_pct` | share of the reversal: change in the unit's margin ÷ the change in Brazil's, in % |
| `lula_capture_pct` | Lula's share of the combined gain: votes gained by Lula ÷ votes gained by both, in %; empty when the two together gained no votes; can exceed 100 or fall below 0 (note N09) |
| `chg_turnout` | change in turnout, runoff − first round |
| `chg_blank_null` | change in blank and null votes, runoff − first round |
| `chg_electorate` | change in registered voters, runoff − first round, registration changes only (note N05) |
| `abstention_rate_r1_pct, abstention_rate_r2_pct` | abstention rate: abstention ÷ registered voters, in %, each round with its own registered voters (note N05) |
| `chg_abstention_rate_pp` | change in the abstention rate, in percentage points |
| `identity_residual` | check: (votes gained by both) − (other first-round votes + change in turnout − change in blank and null votes); it is zero in every row |

## estados.csv

The same columns for Brazil, the 5 regions, abroad and the 27 states (abroad as ZZ).

- **Source:** TSE, official results (resultados.tse.jus.br, elections 6257 and 6258)
- **Made by:** `scripts/base1t.py`, `scripts/base2t.py`, `scripts/analise_base.py` → `dados/analise_estados.csv`
- **Rows:** 35

| column | description |
|---|---|
| `level` | brasil, regiao or uf (Brazil, region or state) |
| `code, name` | code (BR, region or state abbreviation; ZZ and EX for abroad) and name |
| `region` | the state's region; empty for Brazil |
| `municipalities` | how many municipalities the unit adds up |
| `electorate_r1, electorate_r2` | eligible registered voters in each round (note N05) |
| `turnout_r1, turnout_r2` | turnout (votes cast) |
| `abstentions_r1, abstentions_r2` | abstention: registered voters − turnout |
| `valid_votes_r1, valid_votes_r2` | valid votes |
| `blank_null_r1, blank_null_r2` | blank and null votes: turnout − valid votes (combined in the first round: note N07) |
| `blank_r2, null_r2` | blank and null votes separately, runoff only |
| `lula_r1, flavio_r1, lula_r2, flavio_r2` | votes for each candidate |
| `others_r1` | votes for the other candidates in the first round: valid − Lula − Flávio |
| `lula_share_r1_pct, lula_share_r2_pct` | Lula's share of the two-candidate vote, Lula ÷ (Lula + Flávio), in %; empty when neither got votes (note N09). Flávio's is 100 − share |
| `chg_share_pp` | change in Lula's share, runoff − first round, in percentage points |
| `chg_lula, chg_flavio` | votes gained by each candidate from the first round to the runoff |
| `margin_r1, margin_r2, chg_margin` | margin Lula − Flávio in each round and its change |
| `reversal_weight_pct` | share of the reversal: change in the unit's margin ÷ the change in Brazil's, in % |
| `lula_capture_pct` | Lula's share of the combined gain: votes gained by Lula ÷ votes gained by both, in %; empty when the two together gained no votes; can exceed 100 or fall below 0 (note N09) |
| `chg_turnout` | change in turnout, runoff − first round |
| `chg_blank_null` | change in blank and null votes, runoff − first round |
| `chg_electorate` | change in registered voters, runoff − first round, registration changes only (note N05) |
| `abstention_rate_r1_pct, abstention_rate_r2_pct` | abstention rate: abstention ÷ registered voters, in %, each round with its own registered voters (note N05) |
| `chg_abstention_rate_pp` | change in the abstention rate, in percentage points |
| `identity_residual` | check: (votes gained by both) − (other first-round votes + change in turnout − change in blank and null votes); it is zero in every row |

## partidos.csv

The 30 parties of 2026, with their placement on the expert-survey scale (0 to 10), the left bloc and the rules applied.

- **Source:** Bolognesi, Ribeiro, Codato e Silva (2025), doi:10.7910/DVN/MFIXKW
- **Made by:** `scripts/escala_partidos.py` → `dados/escala_partidos.csv`
- **Rows:** 30

| column | description |
|---|---|
| `number, abbreviation, name` | the party's number, abbreviation and name in 2026 |
| `federation_2026` | the federation the party belongs to in 2026, if any |
| `position` | placement on the expert-survey left–right scale, 2022 wave: from 0 (far left) to 10 (far right); empty for Missão (note N11) |
| `category` | category in the source article, in Portuguese (extrema esquerda, esquerda, centro-esquerda, centro, centro-direita, direita, extrema direita: far left to far right) |
| `left_camp` | yes for a placement up to 4.49 (far left, left and center-left) |
| `rule, rule_explained` | rule used to link the 2026 party to the survey's party (mergers, name changes, new parties: note N10) |
| `abbreviation_in_survey` | the party's abbreviation in the survey dataset |
| `experts, std_dev` | how many experts gave a score and the standard deviation of the scores (note N12) |
| `source` | the publication and the dataset |
| `check_2018_position, check_2018_left_camp, check_2018_rule, check_2018_explained` | check against the 2018 wave of the same survey |
| `check_zucco_power_2021` | check against the Zucco and Power scale (survey of federal deputies, 2021), from about −1 to +1; only the order is comparable |

## esquerda_municipios.csv

Left-bloc vote for deputy and senator in the first round, by municipality, state and Brazil (chapter 5).

- **Source:** TSE, open data, votacao_partido_munzona_2026.zip; scale in partidos.csv
- **Made by:** `scripts/votos_partido_1t.py`, `scripts/escala_partidos.py` → `dados/esquerda_1t_municipios.csv`
- **Rows:** 16,798

| column | description |
|---|---|
| `level` | mu (municipality), uf (state) or br (Brazil) |
| `code, state, name` | TSE municipality code (empty for state and Brazil), state and name |
| `office, office_name` | 5 senador (senator), 6 deputado federal (federal deputy), 7 deputado estadual (state deputy), 8 deputado distrital (Federal District deputy) |
| `valid_votes, left, left_pct` | valid votes for the office, votes for left-bloc parties and their percentage of the valid votes, in % |
| `no_position, no_position_pct` | votes for the party with no placement on the scale (Missão) and their percentage of the valid votes (note N11) |
| `scale` | average of the parties' placements, weighted by votes, from 0 to 10, only among the votes with a placement |
| `lula_r1, flavio_r1, lula_share_r1` | presidential votes in the first round and Lula's share of the two-candidate vote, in % |
| `advantage` | left_pct − Lula's share of the two-candidate vote, in percentage points. The chapter 5 test uses his percentage of the valid votes (HIPOTESES.md, P14); this column is the robustness check's |
| `sub_judice, sub_judice_left, left_pct_with_sj, scale_with_sj, advantage_with_sj` | the version with the sub judice votes added to the valid votes and to their parties (note N02) |
| `check_2018_left_pct, check_2018_no_position, check_2018_scale, check_2018_advantage` | check against the 2018 wave of the scale |

## votos_partido_1t.csv

Flattened from `dados/votos_partido_1t.json`, only in this repository: one row per municipality × office × party with any first-round vote (a party with no votes in a place has no row).

- **Source:** TSE, open data, votacao_partido_munzona_2026.zip
- **Made by:** `scripts/votos_partido_1t.py` → `dados/votos_partido_1t.json`
- **Rows:** 318,397

| column | description |
|---|---|
| `state` | state abbreviation |
| `tse_code` | municipality code at the TSE, 5 digits (the same as in municipios.csv) |
| `municipality` | municipality name in the TSE list |
| `office_code, office` | office in the first round: 3 governor, 5 senator, 6 federal deputy, 7 state deputy, 8 district deputy (Federal District only, in place of state deputy) |
| `party_number, party_abbrev` | party number and abbreviation |
| `federation_abbrev` | party federation the party belongs to; empty outside a federation |
| `nominal_votes` | valid votes for the party's candidates (TSE field QT_VOTOS_NOMINAIS_VALIDOS) |
| `party_label_votes` | valid votes cast for the party number only, including nominal votes converted to the party (QT_TOTAL_VOTOS_LEG_VALIDOS) |
| `valid_votes` | valid votes for the party: nominal_votes + party_label_votes. The sum for an office in a municipality equals the valid votes in the official result. Senator: two seats in 2026, each voter voted twice, so valid votes exceed turnout |
| `annulled_sub_judice` | votes annulled sub judice (nominal + party), outside valid votes as in the official result; may change with a court decision (notes on the data, in Method and sources) |
| `annulled` | annulled votes (nominal + party), outside valid votes |

## hipoteses.csv

The tests of the hypotheses in chapters 1, 3, 4 and 5: the main test and the robustness checks, with 95% confidence interval, p-value and classification.

- **Source:** municipios.csv and esquerda_municipios.csv
- **Made by:** `scripts/inferencia.py` → `dados/inferencia.json`
- **Rows:** 59

| column | description |
|---|---|
| `hypothesis, chapter` | the hypothesis (H1, H3, H4, H5) and the chapter where it appears |
| `office` | in chapter 5, the office (deputado federal, deputado estadual or senador: federal deputy, state deputy or senator) |
| `version` | the main test or a robustness check |
| `within_states` | yes: compares municipalities in the same state (state fixed effect); no: all municipalities together |
| `weight` | weight of each municipality in the regression |
| `variable, controls` | the variable tested and the controls |
| `n, groups` | how many municipalities and how many states are included |
| `coef, std_error` | coefficient (points of change in Lula's share per point of the variable; in the supplementary rows, which have no hypothesis, votes gained by the candidate as % of first-round registered voters per point of the variable) and standard error clustered by state |
| `ci95_low, ci95_high` | 95% confidence interval of the coefficient from the clustered error (t with the number of states minus 1 degrees of freedom) |
| `wild_ci95_low, wild_ci95_high` | 95% confidence interval from the wild cluster bootstrap, by test inversion: the one the charts show (T32) |
| `p_cr1, p_wild` | p-value from the clustered error and from the wild cluster bootstrap (empty where not calculated) |
| `r2, r2_type` | R² and its type (comum or dentro dos estados: ordinary or within states) |
| `interquartile_effect_pp` | predicted difference in the change in Lula's share between a municipality in the bottom quartile and one in the top quartile of the variable, in points |
| `predicted, classification, small` | sign predicted before the calculations, the classification (confirmada, contrária or inconclusiva: supported, contradicted or inconclusive) and whether the association is small (less than 0.5 point) |

## de_onde_vieram.csv

Where each candidate's vote gains came from, in Brazil, by region and by state, comparing polling stations in the same city, with the 95% confidence interval and the precision criterion.

- **Source:** TSE, open data and voting machine reports by polling station (dados/secoes_presidente.csv.gz)
- **Made by:** `scripts/secoes_baixar.py`, `scripts/secoes.py`, `scripts/secoes_inferencia.py`, `scripts/inferencia.py` → `dados/inferencia.json`
- **Rows:** 99

| column | description |
|---|---|
| `level, place, n` | Brazil, region or state, and how many municipalities are included (with all their polling stations) |
| `source` | the source of vote gains: votes for the other first-round candidates, change in turnout or drop in blank and null votes |
| `lula, lula_ci95_low, lula_ci95_high` | the part of the source that went, on net, to Lula (from 0 to 1) and the 95% confidence interval by bootstrap (see the intervalo column) |
| `flavio, flavio_ci95_low, flavio_ci95_high` | the same for Flávio (the two parts add up to 1) |
| `half_width` | half the width of the 95% confidence interval, from 0 to 1 |
| `passes_criterion` | yes when it meets the precision criterion (at least 30 municipalities, estimate between 0 and 1 and half-width up to 0.10; HIPOTESES.md 4.2, in the order set in T32) |
| `larger_share, reason` | who got the larger part, when it passes; the reason, when it does not (note N16) |
| `interval` | what the bootstrap resampled: whole states (Brazil and regions) or whole municipalities, with all their polling stations (states) |
| `model_warning` | yes when any source for the place falls outside 0 to 1: the model does not describe the place well, and all its sources carry the warning (marked † on the page) |

## apuracao_ao_vivo.csv

The readings recorded by the runoff live count page: % counted, time, count, first round in the same voting machines and projection (chapter 7 and Live count).

- **Source:** readings recorded by the live count page (resultados.tse.jus.br, election 6258), 25 October 2026
- **Made by:** `scripts/collector.py` → `dados/historico_2t.json`
- **Rows:** 115

| column | description |
|---|---|
| `machines_counted_pct, tse_time` | % of voting machines counted at the reading and the time of the reading at the TSE |
| `lula_r2_pct` | Lula's share of the two-candidate vote in the runoff count up to that reading, in % |
| `lula_r1_same_machines_pct` | Lula's first-round share in the same voting machines already counted in the runoff, in % |
| `final_projection_pct` | projection of the final result shown live, in % (Lula's share) |
| `lula_r1_by_state_pct` | Lula's first-round share in the same voting machines, taken by state only, in % (check of the live page) |

## testes_sociais.csv

The 35 tests of the social data in chapter 8 (7 characteristics × 5 measures), within states and nationwide, with 95% confidence interval, p-value, Holm-corrected p-value and result.

- **Source:** municipios.csv and dados_sociais.csv
- **Made by:** `scripts/inferencia.py` → `dados/inferencia.json`
- **Rows:** 70

| column | description |
|---|---|
| `variable, outcome` | the municipality characteristic and the election measure: ds (change in Lula's share), gL and gF (votes gained by Lula and by Flávio, as % of first-round registered voters), cap (Lula's share of the combined gain) and da (change in abstention) |
| `within_states` | yes: compares municipalities in the same state (the deciding version); no: all municipalities together |
| `n, groups` | how many municipalities and how many states are included |
| `coef, std_error` | coefficient (points of the measure per 1 point of the characteristic; per 1 log unit for GDP per capita and density) and standard error clustered by state |
| `ci95_low, ci95_high` | 95% confidence interval of the coefficient from the clustered error |
| `wild_ci95_low, wild_ci95_high` | 95% confidence interval from the wild cluster bootstrap, by test inversion |
| `p_cr1, p_wild` | p-value from the clustered error and from the wild cluster bootstrap |
| `p_holm, p_cr1_holm` | the two p-values corrected by the Holm method across the 35 tests of the same version |
| `interquartile_effect` | predicted difference in the measure between a municipality in the bottom quartile and one in the top quartile of the characteristic, in points |
| `association, direction, small` | yes when both corrected p-values are below 0.05; the direction (positiva or negativa: positive or negative) and whether it is small (less than 0.5 point between quartiles) |

## dados_sociais.csv

The 7 characteristics of each municipality in chapter 8 (IBGE, 2022 Census and Municipal GDP 2023), with the denominators of each one.

- **Source:** IBGE: 2022 Census (SIDRA), Municipal GDP 2023, Territorial Areas 2022
- **Made by:** `scripts/sociais_baixar.py`, `scripts/dados_sociais.py` → `dados/dados_sociais_municipios.json`
- **Rows:** 5,571

| column | description |
|---|---|
| `tse_code, ibge_code, state, municipality` | municipality code at the TSE (5 digits) and at IBGE (7 digits), state and name |
| `pct_aged_60plus` | % of the resident population aged 60 or over (2022 Census) |
| `literacy_15plus` | literacy rate of people aged 15 or over, in %, as published by IBGE (2022 Census) |
| `pct_income_up_to_half_mw` | % of residents in permanent private households with per capita household income of up to half a minimum wage, including those with no income (2022 Census, sample) |
| `gdp_pc, ln_gdp_pc` | GDP per capita in 2023, in reais, as published by IBGE, and its natural logarithm, which is the one used in the tests |
| `density, ln_density` | inhabitants per km² (2022 Census), as published by IBGE, and its natural logarithm, used in the tests |
| `pct_evangelical` | % of evangelicals among people aged 10 or over (2022 Census, sample; note N19) |
| `pct_black_brown` | % of Black and pardo (mixed-race) people in the resident population (2022 Census) |
| `pop, pop15, pop10, area_km2, gdp_thousand` | the denominators: resident population, aged 15 or over and aged 10 or over, area in km² and 2023 GDP in thousands of reais; all empty for Boa Esperança do Norte (MT), note N20 |
