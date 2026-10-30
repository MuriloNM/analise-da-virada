# Notas sobre os dados

> Cópia do registro das notas sobre os dados, como foi escrito durante o trabalho: o que aconteceu com um dado, como foi tratado e onde pesa. O texto para o leitor está em Método e fontes, na página do estudo; scripts/pagina_dados.py lê daqui os títulos das notas. Os códigos T (tarefas), D (diário), P (decisões do autor) e os nomes de sessão remetem ao registro interno de trabalho, que não está neste repositório.

Registro vivo das notas que vão para a página (seção 7.3 da especificação). Criado em 26/10/2026.

**O que é uma nota:** um comentário do tipo "tal dado foi considerado assim". Ela diz o que aconteceu, como foi tratado e onde pesa. Não explica a conta (isso é o "Como calculamos") nem o que não dá para concluir (isso é "Limites do estudo").

**Como usar:**
- todo ticket anota aqui a decisão que tomou sobre um dado, no mesmo momento em que decide;
- a numeração (N01, N02…) é a da ordem de criação; o T12 a manteve (os códigos já estão nos gráficos e nos endereços `#metodo/nota-N08`) e escreveu o texto para o leitor no catálogo (`site-analise/textos/pt-BR.js`, chaves `nt.N01.1`…). Nota nova pega o próximo número e ganha texto no catálogo;
- cada nota diz em quais gráficos e cartões aparece a marca "ver nota N", o que é preenchido no T08 e no T24;
- cada nota diz de quais fontes vem (campo "Fontes"), com o nome da linha no registro de fontes do T12. A tabela "Onde cada fonte entra no estudo", no T12, faz o caminho inverso: da fonte para as notas.

**Regra para anulação e sub judice:** todo caso de voto anulado depois da eleição ou sub judice vira uma nota. O tratamento é o mesmo para todos os partidos e candidatos e fica decidido no `HIPOTESES.md` antes das contas (T06).

---

### N01. Senador: dois votos por eleitor
- **O que aconteceu:** em 2026 havia duas vagas de senador em cada estado, e cada eleitor votou duas vezes.
- **Como foi tratado:** a soma dos votos de senador é usada como está. Ela passa do comparecimento: no Brasil, 207,0 milhões de votos válidos para 124,9 milhões de eleitores que compareceram, ou 1,66 voto por eleitor.
- **Onde pesa:** toda fatia de partido no senador (capítulo 5 e hipótese da seção 6). Os dois votos entram em cima e embaixo da conta.
- **Marca "ver nota" na página (T08):** Figura 2.5 (capítulo 5).
- **Fontes:** TSE, dados abertos `votacao_partido_munzona_2026.zip`, conferido com o JSON oficial por estado (registro do T12: "1º turno, cargos estaduais, por partido… (T04)"); comparecimento do 1º turno de `base_1t_municipios.json`.
- **Origem:** T04.

### N02. Votos sub judice
- **O que aconteceu:** quem tem o registro negado mas ainda recorre concorre "sub judice". O nome fica na urna e os votos são contados à parte. Se o registro for aceito no fim, os votos passam a válidos; se for negado em definitivo, passam a nulos. Em nenhum caso vão para outro candidato. Nos dados do TSE de 25/10/2026:
  - **senador no Acre:** 145.244 votos (16,6% dos votos de senador no estado), de um candidato do PP com registro negado pelo TRE-AC em 11/09/2026 e recurso pendente;
  - **Sergipe:** os votos do PSOL estão sub judice nos quatro cargos (governador, senador e deputados);
  - **municípios:** passam de 5% em 26 municípios no senador (os 22 do Acre, 3 de Sergipe e 1 de Roraima), 51 no deputado federal e 58 no estadual. O maior caso é Três Barras-SC, com 59,0% no deputado federal.
- **Como foi tratado:** fora dos votos válidos, como no resultado oficial, e guardados à parte (`sj` em `votos_partido_1t.json`).
  - **Regra final (T06),** fixada no `HIPOTESES.md` (5.4) antes das contas e aprovada pelo autor em 26/10/2026, 12:43, igual para todos os partidos: nas contas principais, os votos sub judice ficam fora dos válidos, e nenhum município sai da conta por ter muito voto sub judice.
  - **Duas conferências** no teste do voto dividido: com os votos sub judice somados aos válidos e aos partidos deles; e sem os municípios em que eles passam de 5% de (válidos + sub judice) no cargo. Saem 54 municípios no deputado federal, 58 no estadual e 26 no senador. O T04 contou 51 no federal porque só olhou municípios com pelo menos 1.000 válidos; a regra do T06 não tem esse piso.
  - **Quanto muda:** nada na conclusão. O teste do voto dividido fica inconclusivo nos três cargos, com e sem os votos sub judice (no deputado federal, −0,005 ponto de Δs por 10 pontos de vantagem pela regra principal e −0,006 pelas duas conferências).
  - **Presidente e governador:** não há voto sub judice de presidente; o governador (nota N03) não entra em nenhuma conta do T06.
- **Onde pesa:** capítulo 5 e hipótese da seção 6. Onde há muito voto sub judice, a fatia dos outros partidos entre os válidos fica maior do que seria com esses votos.
  - **No % de esquerda (T05):** somar os votos sub judice muda o % de esquerda em mais de 5 pontos em 1 município no senador (Xapuri-AC), 12 no deputado federal e 7 no estadual (municípios com pelo menos 1.000 válidos). As duas versões estão em `esquerda_1t_municipios.csv`, sem escolha entre elas.
- **Marca "ver nota" na página (T08):** Figura 2.5 e ressalvas do capítulo 5.
- **A atualizar:** se algum recurso for julgado, o TSE refaz os arquivos e esta nota muda.
- **Fontes:**
  - números: TSE, `votacao_partido_munzona_2026.zip` (colunas `QT_VOTOS_*_ANUL_SUBJUD`) e JSON oficial por estado (campo `vansj` e situação do voto `dvt` = "Anulado sub judice"), linhas do T04 no registro do T12;
  - contexto, sem números: TRE-AC (indeferimento de 11/09/2026), Rádio Senado (05/10/2026), Poder360 (12/09/2026) e, para Sergipe, Boca. Links na linha "Votos sub judice: contexto (T04)" do registro do T12.
- **Origem:** T04 (detalhes em "Votos sub judice: o que houve").

### N03. Votos anulados depois da eleição
- **O que aconteceu:** no Rio de Janeiro, o TSE anulou em 08/10/2026 os votos de um candidato a governador. O arquivo do estado foi refeito em 10/10, e os 274.411 votos dele passaram a nulos.
- **Como foi tratado:** os números usados são os do arquivo refeito, como no resultado oficial.
- **Onde pesa:** só no governador, que está guardado mas fora da especificação. Se o governador entrar em alguma conta, esta nota vai junto.
- **Fontes:** número: TSE, JSON oficial do governador do RJ refeito em 10/10/2026 (campo `vnt`, em `dados/tse_6259_uf/`). Contexto, sem números: Jornal Opção (linha "Votos sub judice: contexto (T04)" do registro do T12).
- **Origem:** T04.

### N04. Votos de legenda
- **O que aconteceu:** no deputado estadual, 16.884 votos nominais foram convertidos em votos de legenda.
- **Como foi tratado:** contados como legenda, como no total oficial do TSE.
- **Onde pesa:** pouco. Só muda a divisão entre voto no candidato e voto no partido; o total do partido é o mesmo.
- **Fontes:** TSE, `votacao_partido_munzona_2026.zip` (coluna `QT_VOTOS_NOM_CONVR_LEG_VALIDOS`), registro do T12, linha do T04.
- **Origem:** T04.

### N05. O eleitorado de um município muda entre os turnos
- **O que aconteceu:** o eleitorado do Brasil é o mesmo nos dois turnos (158.745.502), mas o de 3.725 municípios do Brasil muda, e o de 54 cidades do exterior também (3.779 ao todo: 2.294 com mais eleitores no 2º turno e 1.485 com menos; 19.048 eleitores em módulo). *(Corrigido no T32, 26/10/2026: a nota dizia "3.779 municípios", contando o exterior; parecer estatístico, m14.)* As maiores diferenças são São Paulo (+845), Brasília (+675) e Belém (−412). A causa não foi verificada; uma possibilidade é o voto em trânsito, que o eleitor pede para cada turno.
- **Como foi tratado:** a taxa de abstenção de cada turno usa o eleitorado daquele turno. O saldo de onde vieram os votos usa o comparecimento de cada turno como ele é. Num município, parte da variação do comparecimento pode vir de eleitores que votaram em outro lugar no outro turno; no Brasil, isso se cancela.
- **Onde pesa:** abstenção e comparecimento por município (capítulo 4, rankings do Explorar e ficha da cidade), sobretudo em municípios pequenos.
- **Marca "ver nota" na página (T08):** Figuras 2.4a e 2.4b e texto do capítulo 4; ficha da cidade (Resumo).
- **Origem:** T02.

### N06. Eleitores no exterior
- **O que aconteceu:** os 186 "municípios" do exterior só votam para presidente.
- **Como foi tratado:** entram nas contagens de presidente, no total do Brasil e na ficha, mas ficam fora dos cargos do 1º turno (capítulo 5) e dos cruzamentos com dados sociais, que não existem para eles.
  - **T06 (`HIPOTESES.md`, 2.1 e 5.1):** ficam fora também das regressões, do funil, da regressão ecológica e dos rankings de municípios, porque não têm estado (o grupo do erro padrão) e têm abstenção de outra ordem. Nos rankings, aparecem numa lista própria.
- **Onde pesa:** capítulo 5 e cruzamentos sociais (seção 6.1).
- **Marca "ver nota" na página (T08):** Figuras 2.1, 2.2, 2.3a e 2.3b.
- **Origem:** T02, T04.

### N07. Brancos e nulos no 1º turno
- **O que aconteceu:** a base do 1º turno tem brancos e nulos somados (comparecimento − válidos). A do 2º turno tem os dois separados.
- **Como foi tratado:** as contas entre os turnos usam a soma (BN), que existe nos dois. Brancos e nulos separados só aparecem no 2º turno.
- **Onde pesa:** capítulo 4 e "de onde vieram os votos".
- **Marca "ver nota" na página (T08):** Figuras 2.3b e 2.4b.
- **Origem:** T02.

### N08. Região, capital e porte dos municípios
- **O que aconteceu:** o estudo agrupa os municípios por região, capital × interior e porte. As bases de votos não trazem região nem porte.
- **Como foi tratado:**
  - **região:** tirada da UF, pelas cinco grandes regiões do IBGE. Conferida com o 1º dígito do código IBGE (`cdi`) da lista do TSE nos 5.571 municípios do Brasil, sem exceção;
  - **capital × interior:** campo `c` da lista do TSE (27 capitais, com Brasília), igual ao campo `cap` das duas bases;
  - **porte:** eleitorado apto do **1º turno**, em cinco faixas fixadas antes de ver os números por município (T03, 26/10/2026, 11:47): até 5 mil (1.434 municípios), de 5 mil a 10 mil (1.507), de 10 mil a 50 mil (2.134), de 50 mil a 200 mil (394) e mais de 200 mil (102). O limite de 10 mil é o piso dos rankings (especificação, seção 5); o de 200 mil é o do 2º turno para prefeito (Constituição, art. 29, II); 5 mil, 10 mil e 50 mil também são limites das classes de tamanho de município da MUNIC do IBGE. O porte é por eleitorado, não por população;
  - **exterior:** categoria própria ("Exterior") nas três classificações e fora das faixas de porte. Entra no total do Brasil, como no resultado oficial.
- **Onde pesa:** rankings por porte e gráfico de funil (seção 5), filtros do Explorar, peso de cada região na virada (capítulo 6) e ficha da cidade.
- **Marca "ver nota" na página (T08):** Figura 2.6 (ponte da virada).
- **Fontes:** lista de municípios do TSE e eleitorado de `base_1t_municipios.json` (registro do T12: "Lista de municípios do TSE" e "1º turno, presidente, municípios"); referências dos limites na linha "Faixas de porte: referências (T03)".
- **Origem:** T03.

### N09. Fatia e captura sem valor
- **O que aconteceu:** duas contas da seção 4 não têm valor em todas as unidades:
  - **fatia do Lula** (L ÷ (L + F)): no exterior, 41 cidades não tiveram voto em nenhum dos dois no 1º turno e 42 no 2º. Nelas, a fatia e a variação da fatia ficam sem valor (42 cidades);
  - **captura** (ΔL ÷ (ΔL + ΔF)): quando os dois juntos não ganharam votos do 1º para o 2º turno (ΔL + ΔF ≤ 0), a conta não mede a parte de um ganho. Isso acontece em 228 municípios (176 no Brasil e 52 no exterior) e em 3 UFs (Acre, Amapá e Roraima);
  - quando um dos dois perdeu votos e o outro ganhou mais do que isso, a captura passa de 100% ou fica abaixo de 0. Isso acontece em 777 municípios e em 3 UFs (Amazonas, Maranhão e Tocantins).
- **Como foi tratado:** valor que não existe fica vazio no CSV, sem virar zero e sem entrar em média, e a página mostra "—". A captura fora de 0% a 100% fica como a conta dá. A regra foi escrita no script antes da primeira rodada (26/10/2026, 11:49) e não mudou depois de ver as contagens. O peso na virada tem valor em toda unidade.
- **Onde pesa:** fatia e captura em mapas, rankings e ficha da cidade (capítulos 1, 2 e 6, grandes números das UFs e Explorar). Como os rankings tratam os vazios e as capturas fora de 0% a 100% fica para o T08 e o T24, com a mesma regra para os dois candidatos.
- **Marca "ver nota" na página (T08):** ficha da cidade (Resumo) e texto do capítulo 6; o cartão "Captura" já cita a nota no "Como calculamos". No T34, o teste da captura contra os dados sociais usa só os municípios com mais de 10 mil eleitores e ΔL + ΔF > 0 (2.548), como registrado na seção 6 do `HIPOTESES.md`; a marca vai na aba "Os votos a mais" da figura 8.2 e no "Como se chegou à conclusão" do capítulo 8. No T08, os rankings dos capítulos usam só municípios do Brasil com mais de 10 mil eleitores, em que a fatia sempre tem valor; a captura não entra em ranking e aparece como "—" na ficha e na tabela 2.6, igual para os dois.
- **Fontes:** bases dos dois turnos (registro do T12: "1º turno, presidente, municípios" e "2º turno, presidente, municípios e UFs (T02)").
- **Origem:** T03.

### N10. Partidos que mudaram depois da pesquisa com especialistas
- **O que aconteceu:** a posição de cada partido vem de uma pesquisa com cientistas políticos feita em julho de 2022. Entre 2022 e 2026, partidos se fundiram, incorporaram outros e mudaram de nome.
- **Como foi tratado:** com as regras do próprio artigo, fixadas antes das contas (T05, 26/10/2026, 11:52):
  - **fusão:** média das posições. PRD = média de PTB e Patriota;
  - **incorporação:** fica a posição de quem incorporou. Podemos (incorporou o PSC) e Solidariedade (incorporou o PROS);
  - **mudança de nome:** fica a posição do nome antigo. Mobiliza = PMN; Democrata = PMB;
  - **federações:** cada partido fica com a própria posição. Nas cinco federações de 2026, todos os partidos ficam do mesmo lado do corte "campo da esquerda".
- **Onde pesa:** % de esquerda e escala contínua (capítulo 5 e hipótese da seção 6) e tabela partido → posição na seção "Método e fontes". A posição de um partido pode ter mudado de 2022 a 2026; a pesquisa não mede isso.
- **Marca "ver nota" na página (T08):** Figura 2.5.
- **Fontes:** registro do T12, linhas "Classificação ideológica dos partidos, rodada de 2022 (T05)" e "Mudanças de partido: contexto (T05)".
- **Origem:** T05.

### N11. Partido sem posição na escala (Missão)
- **O que aconteceu:** o Partido Missão (14) foi registrado pelo TSE em 04/11/2025, depois da pesquisa com especialistas, e nenhuma fonte acadêmica o classifica.
- **Como foi tratado:** fica sem posição. No % de esquerda, os votos dele contam entre os válidos, mas fora do campo da esquerda, porque a fonte não o classifica como de esquerda; na escala contínua, saem da média. Regra fixada antes das contas (T05, 26/10/2026, 11:52). Cada linha de `esquerda_1t_municipios.csv` guarda os votos dele (`sem_posicao`).
- **Como foi decidido:**
  - **Ninguém escolhe o lado do Missão.** A posição de um partido só vem de fonte acadêmica (especificação, seção 6). Dizer que ele é de esquerda, de centro ou de direita seria julgamento próprio, e isso vale para o autor e para a sessão.
  - **Duas regras possíveis**, as duas sem julgar o partido:
    - **A, a usada:** os votos do Missão ficam no total de votos válidos, mas não contam como esquerda. A conta é "votos em partidos que a fonte põe no campo da esquerda ÷ todos os votos válidos", como no resultado oficial. Vale seja qual for a posição do Missão: quem votou nele não votou num partido do campo;
    - **B, a conferência:** os votos do Missão saem da conta, e o % de esquerda é calculado só entre os votos de partidos classificados. Essa regra supõe que o eleitor do Missão se divide entre os campos como o resto do município.
  - **Por que a A:** ela não precisa supor nada sobre o eleitor do Missão, usa o mesmo total de votos do resultado oficial e foi fixada antes de qualquer conta por município. A B fica como conferência, escrita no `HIPOTESES.md` (T06) antes de rodar o teste.
  - **Quanto muda:** pouco no Brasil (deputado federal: 26,3% pela A, 26,6% pela B). Muda onde o Missão foi forte: Vale do Sol-RS, deputado federal, 9,9% pela A e 12,3% pela B; Chapada Gaúcha-MG, deputado estadual, 20,1% e 26,7%.
  - Mantida depois de conversa com o autor (26/10/2026, sessão do T05), que pediu que a decisão ficasse documentada aqui.
- **Como vamos fazer:** a regra A entra nas colunas principais (`pct_esq`, `escala`, `vantagem`). A B se calcula das mesmas colunas: `esq` ÷ (`vv` − `sem_posicao`). Se uma rodada futura da pesquisa com especialistas classificar o Missão, ele ganha a posição dela, com nota datada no T05.
- **Onde pesa:** no Brasil, 1,1% dos votos para deputado federal, 0,7% no estadual, 0,8% no distrital e 0,3% no senador; no estado, São Paulo, com 2,8% no federal. No município (com pelo menos 1.000 votos válidos), passa de 5% em 28 municípios no deputado federal (18 acima de 10%, em GO, MG, RS e SP; o maior é Vale do Sol-RS, com 19,7%) e em 4 no estadual (o maior é Chapada Gaúcha-MG, com 24,6%). Nenhum no senador. Capítulo 5 e hipótese da seção 6.
- **Marca "ver nota" na página (T08):** Figura 2.5 e ressalvas do capítulo 5.
- **Fontes:** número do partido, votos e registro: TSE (`votacao_partido_munzona_2026.zip`, linha do T04 no registro do T12, e linha "Mudanças de partido: contexto (T05)").
- **Origem:** T05.

### N12. Partidos em que os especialistas concordam menos
- **O que aconteceu:** a posição de cada partido é a média das notas dos especialistas, mas eles não concordam igualmente sobre todos. Na base aberta da pesquisa (rodada de 2022), dá para contar quantos puseram cada partido à esquerda (nota até 4), no centro (5) ou à direita (6 ou mais):
  - **quase unanimidade** (98% ou mais do mesmo lado): PSTU, PCO, PCB, PSOL, PCdoB e PT à esquerda; PL, Novo, União, Republicanos, PP, DC e Patriota à direita;
  - **menos consenso, mas com maioria clara:** do lado esquerdo, PV (75% à esquerda e 17% à direita), PDT (83% e 11%), Rede (87% e 8%), UP (87% e 9%) e PSB (90% e 6%); do lado direito, Solidariedade (64% à direita e 23% à esquerda), Cidadania (70% e 20%), Avante (75% e 17%) e Mobiliza, antigo PMN (76% e 17%);
  - **centro:** quase ninguém dá nota 5. O partido com mais notas 5 é o MDB, com 16%.
- **Como foi tratado:** todo partido classificado fica do lado em que a média dele cai, pelo corte do T05. Nenhum partido vira "indefinido": nenhum divide os especialistas ao meio, e um grupo "indefinido" pediria um limite (por exemplo, "menos de dois terços concordam") que seria escolhido agora, sem critério na fonte. A escala contínua, que é o teste de robustez, já leva em conta o quanto cada partido fica à esquerda ou à direita, sem dividir em dois lados.
- **Como foi decidido:** pergunta do autor na revisão do T05 (26/10/2026), com a contagem acima feita na base aberta. Se o autor quiser um grupo "indefinido", ele entra com nota datada no T05 e um critério fixado antes do T06.
- **Onde pesa:** % de esquerda (capítulo 5 e hipótese da seção 6). PV e Rede eram "centro" na rodada de 2018 e foram para a centro-esquerda em 2022; a conferência com 2018 mostra quanto isso pesa (no Brasil, deputado federal, 24,9% pela rodada de 2018 e 26,3% pela de 2022).
- **Marca "ver nota" na página (T08):** ressalvas do capítulo 5.
- **Fontes:** registro do T12, linha "Classificação ideológica dos partidos, rodada de 2022 (T05)" (base aberta `df_experts.csv`).
- **Origem:** T05.

### N13. Vantagem potencial com a fatia do Lula sobre os válidos
- **O que aconteceu:** a vantagem potencial (especificação 6) é o % de votos em partidos do campo da esquerda para deputado ou senador menos a fatia do Lula no 1º turno. Havia duas fatias possíveis: a entre os dois (L ÷ (L + F), a da seção 4 da especificação) e a sobre os válidos (L ÷ válidos), já que no 1º turno os outros candidatos tiveram 9,3 milhões de votos.
- **Como foi tratado:** a fatia sobre os válidos entra na vantagem e no controle da regressão do teste do voto dividido (H5). A fatia entre os dois fica como conferência. No espelho do Flávio, o mesmo: F ÷ válidos no principal e F ÷ (L + F) na conferência.
- **Como foi decidido:**
  - **alternativas:** (a) a fatia entre os dois; (b) a fatia sobre os válidos;
  - **por que a (b):** o % de esquerda divide pelos votos válidos do cargo, de todos os partidos; a fatia sobre os válidos de presidente divide do mesmo jeito, por todos os candidatos, e a vantagem vira a diferença entre duas parcelas comparáveis. Com a (a), quem votou num partido do campo para deputado e em outro candidato para presidente saía da base do Lula, e a vantagem ficava menor justamente onde os outros candidatos foram fortes;
  - decidido pelo autor em 26/10/2026, 12:43, antes das contas (decisão P14, conversa na sessão do T06; especificação 9; `HIPOTESES.md`, H5);
  - **quanto muda:** nada na conclusão. No deputado federal, −0,005 ponto de Δs por 10 pontos de vantagem pela (b) e +0,005 pela (a), os dois com intervalo em volta de zero.
- **Como vamos fazer:** a coluna `vantagem` de `esquerda_1t_municipios.csv` (T05) continua com a fatia entre os dois. A vantagem usada no estudo é calculada em `scripts/inferencia.py`: `pct_esq` − 100 × `lula_1t` ÷ `validos_1t` (de `analise_municipios.csv`). A página (T08 e T24) e o repositório (T15) mostram esta, com o nome "vantagem potencial", e a outra só em "Método e fontes".
- **Onde pesa:** capítulo 5, hipótese da seção 6 e Explorar ("voto dividido").
- **Marca "ver nota" na página (T08):** Figura 2.5.
- **Fontes:** bases do 1º turno (registro do T12: "1º turno, presidente, municípios") e linhas do T04 e do T05.
- **Origem:** T06.

### N14. O Distrito Federal fora da comparação dentro do estado
- **O que aconteceu:** o teste principal de cada hipótese compara municípios do mesmo estado (efeito fixo de UF; `HIPOTESES.md`, 2.5). O DF tem um município só, Brasília, que não tem com quem ser comparado dentro do estado.
- **Como foi tratado:** o DF fica fora das versões "dentro dos estados" (5.570 municípios e 26 UFs) e entra nas versões "Brasil" (5.571 e 27). Também fica fora da estimativa por estado da regressão ecológica, por ter menos de 30 municípios (nota N16). Brasília continua nas contagens, no funil e nos rankings.
- **Como foi decidido:** regra usual desse tipo de regressão (o pacote reghdfe faz o mesmo), escrita no script antes da primeira rodada. Um município sozinho no grupo fica igual à média do grupo e não muda a estimativa; mantê-lo só aumentaria a contagem de municípios e de grupos e deixaria o intervalo um pouco mais estreito sem informação nova.
- **Onde pesa:** capítulos 1, 3, 4 e 5 (H1, H3, H4 e H5).
- **Marca "ver nota" na página (T08):** Figuras 2.1, 2.3a e 2.5 e "Como se chegou à conclusão" dos capítulos 1, 3 e 4.
- **Origem:** T06.

### N15. Senador: Alagoas e Piauí fora do teste do voto dividido
- **O que aconteceu:** em Alagoas e no Piauí, só partidos pequenos do campo da esquerda tiveram candidato ao Senado. O campo teve 0,79% dos votos válidos de senador em Alagoas e 1,22% no Piauí (T05).
- **Como foi tratado:** os dois estados ficam fora do teste do voto dividido no senador (5.245 municípios e 25 UFs na versão Brasil; 5.244 e 24 na comparação dentro dos estados). Continuam nos testes de deputado e em todo o resto.
- **Como foi decidido:** regra geral fixada no `HIPOTESES.md` (H5) antes das contas e aprovada pelo autor em 26/10/2026, 12:43: ficam fora os estados em que o campo da esquerda teve menos de 5% dos votos válidos de senador no estado, porque ali o % de esquerda mede a falta de candidato do campo, e não o voto. A regra pegou só esses dois estados, sem escolha caso a caso.
- **Onde pesa:** capítulo 5, senador.
- **Marca "ver nota" na página (T08):** Figura 2.5.
- **Fontes:** linhas de estado de `esquerda_1t_municipios.csv` (T05).
- **Origem:** T06.

### N16. Estimativas que não deram
- **O que aconteceu:** a regressão ecológica estima, por região e estado, que parte de cada fonte do saldo (votos dos outros candidatos, variação do comparecimento e queda de brancos e nulos) ficou com cada candidato. A estimativa só aparece onde passa no critério de precisão fixado antes (`HIPOTESES.md`, 4.2): pelo menos 30 municípios, estimativa entre 0% e 100% e meia largura do intervalo de 95% de até 10 pontos. O critério dá o mesmo resultado para os dois candidatos, porque as partes deles somam 100%.
- **Correções do T32 (26/10/2026, depois do parecer estatístico; notas datadas no `HIPOTESES.md`):** (1) no Brasil e nas regiões, o intervalo passa a reamostrar estados inteiros, como o erro agrupado das hipóteses; nos estados, continua reamostrando municípios do estado, o que supõe municípios independentes e tende a dar um intervalo estreito demais (M2); (2) "fora de 0% a 100%" passa a vir antes da meia largura, porque é sinal de que o modelo não descreve o lugar, não falta de precisão; e, quando uma fonte sai de 0% a 100%, todas as fontes daquele lugar ganham a marca † na página, mesmo as que passam (m1). Antes do T32, 55 estimativas não davam.
- **Como foi tratado:** na conta entre municípios (até o T35), 62 das 99 estimativas (Brasil, 5 regiões e 27 estados, × 3 fontes) não passaram; com a conta por seção, que a página usa desde o T35, são 17 (ver abaixo; revisão final, 27/10/2026). Onde não passou, a página diz "não deu para estimar com segurança" e o motivo, o da primeira regra que falha:
  - **variação do comparecimento** (capítulo 4): deu no Nordeste e em 16 dos 27 estados. Não deu no Brasil, no Norte, no Centro-Oeste, em RO e TO (resultados muito dispersos); no Sudeste, no Sul, em ES, PE, RS, SC e SE (variação pequena do comparecimento: os municípios do lugar mudaram pouco e de modo parecido); em AC, AP, DF e RR (poucos municípios);
  - **votos dos outros candidatos:** deu no Brasil, no Norte, no Nordeste, no Sul e em 16 estados. Não deu no Centro-Oeste, no Sudeste, em AL, AM, CE, PI e SE (resultados muito dispersos); em PE e RN (variação pequena dos votos dos outros); em AC, AP, DF e RR (poucos municípios);
  - **queda de brancos e nulos:** não deu em nenhum lugar. No Brasil, no Nordeste, no Sudeste, no Sul e em 18 estados, a estimativa sai de 0% a 100%; no Norte, no Centro-Oeste, na BA, no PA e no TO, os resultados são muito dispersos; em ES e RO, a variação é pequena; em AC, AP, DF e RR, há poucos municípios;
  - **marca †:** os 22 lugares em que a parte dos brancos e nulos sai de 0% a 100% (Brasil, Nordeste, Sudeste, Sul, AL, AM, CE, GO, MA, MG, MS, MT, PB, PE, PI, PR, RJ, RN, RS, SC, SE e SP) levam a marca nas estimativas que passam.
- **No Brasil:** a parte dos outros candidatos passa, com a marca †. A do comparecimento dá 57% para o Lula e 43% para o Flávio, mas o intervalo (de 44% a 68%) passa de 10 pontos para cada lado e inclui a metade. A dos brancos e nulos dá 156% para o Lula e −56% para o Flávio. O critério da 4.2 tinha sido escrito para região e estado; o autor decidiu aplicá-lo também ao Brasil depois de ver o resultado dos brancos e nulos (decisão P17, 26/10/2026, 13:03; nota datada no `HIPOTESES.md`). Os votos dos outros aparecem ainda em duas contas de conferência (com intercepto e matriz de transição), que dão divisões diferentes: o capítulo 3 mostra as três.
- **Onde pesa:** capítulos 3 e 4, Explorar ("de onde vieram os votos" e "para onde foi o saldo do comparecimento") e a lista "Estimativas que não deram" em "Método e fontes".
- **Marca "ver nota" na página (T08):** Figuras 2.3b e 2.4b e tabela 2.3b.
- **Fontes:** bases dos dois turnos via `analise_municipios.csv` (T03); cálculo em `scripts/inferencia.py`, saída em `dados/inferencia.json` (`por_lugar` e `nao_deu`).
- **Contas por seção (T35, 27/10/2026; regra em `HIPOTESES.md`, 4.5, escrita antes):** comparando seções do mesmo município, só **17 das 99** estimativas não dão: as 12 de AC, AP, DF e RR (poucos municípios), o comparecimento no Norte (resultados muito dispersos), os votos dos outros no AM (resultados muito dispersos) e em MT e SP (as duas contas dão lados opostos: "depende da comparação, municípios ou seções") e os brancos e nulos no RJ (resultados muito dispersos). Nenhuma estimativa sai de 0% a 100%: a marca † some. **Desde a decisão P28 do autor (27/10/2026, 09:42; D59), a página usa a conta por seção** nos capítulos 3 (as outras duas fontes e a quarta conta dos votos dos outros) e 4, no Explorar e em "Estimativas que não deram"; a conta por município fica como conferência, na tabela do "Ver detalhes" do capítulo 4 e em `por_lugar_municipios` do `inferencia.json`. Saída em `dados/secoes_inferencia.json` (`scripts/secoes_inferencia.py`), levada ao `inferencia.json`. Texto da nota na página: `nt.N16.3`.
- **Origem:** T06; corrigida no T32; conta por seção no T35.

### N17. Histórico da apuração ao vivo: a última leitura e o buraco
- **O que aconteceu:** o histórico da apuração ao vivo do 2º turno tem 115 leituras, de 8,31% a 100% das urnas apuradas. A de 100% é o próprio resultado final. Entre 60,85% e 68,8% não há leitura.
- **Como foi tratado:** o erro da projeção (projeção − 51,785%) é medido nas 114 leituras antes da final, que fica fora por ser a referência. As faixas de 10 pontos de % apurado foram fixadas antes (`HIPOTESES.md`, 4.4). A faixa de 60% a 70% tem só 3 leituras, e o buraco fica escrito no gráfico.
- **Na página Apuração ao vivo (T28):** as 115 leituras aparecem como a página as gravou, com 3 casas, sem arredondar de novo (arredondar 51,785 para duas casas daria 51,78 ou 51,79 conforme a conta, e o resultado final, do valor completo, é 51,79%). O buraco aparece como faixa "sem leituras" nas duas figuras. As listas de estados e dos 40 maiores municípios não foram gravadas leitura a leitura (só o último retrato, com 99,77% apurado, em `dados/ultimo_retrato_2t.json`): a página mostra essas tabelas com o resultado final, de `dados.js`. A contagem do 1º turno no mesmo % apurado é interpolada em linha reta entre dois pontos da curva `t1c`. O buraco foi quando o site do TSE passou a recusar parte das consultas da página, que pedia muitos arquivos em pouco tempo (comentário do autor, D38). A Figura A2 da página mostra a projeção com uma faixa do maior erro que ela teve de cada leitura até o fim: a faixa usa o resultado final, então só pode ser traçada depois, e não é intervalo de confiança. O salto da projeção às 19:43:31 (51,921%, numa leitura só) tem nota própria na página: sem os estados gravados leitura a leitura, a causa não pode ser confirmada, e a nota dá as duas explicações possíveis pela forma da conta.
- **Onde pesa:** capítulo 7, Explorar ("erro da projeção") e a página Apuração ao vivo (T28).
- **Marca "ver nota" na página (T08):** Figura 2.7 (capítulo 7).
- **Fontes:** `dados/historico_2t.csv` (linha "Histórico da noite do 2º turno" da tabela "Onde cada fonte entra no estudo" do T12).
- **Reconstrução (T41; na página no T42, 29/10/2026):** a apuração foi refeita pela hora de recebimento de cada boletim (`DT_BU_RECEBIDO` do `bweb_2t`, `scripts/reconstrucao_2t.py`, `dados/reconstrucao_2t/`). Bate com as 114 leituras (diferença no % do Lula de 0,004 ponto na mediana; atraso mediano de 28 s entre o recebimento e a leitura). Preenche o buraco com 13 leituras refeitas e dá os estados leitura a leitura. O salto de 19:43:31 não veio dos votos (projeção refeita: 50,648%): arquivos de UF mais velhos que os dos municípios, lidos na mesma consulta. Texto da nota na página: `nt.N17.3`; detalhe no T41, "Resultado da Parte 1". **Na Apuração ao vivo (T42, etapa 2b):** os estados de cada leitura gravada vêm da reconstrução (`uf_leituras` em `apuracao-dados.js`, de `leituras_uf.csv`), numa tabela que acompanha a leitura escolhida; o texto da nota na página (`nt.N17.2`) diz isso. As 13 leituras refeitas do buraco aparecem só nas figuras, em traço curto.
- **Origem:** T06. Título trocado no T08 (antes, "Histórico da noite"): o título vai para a página, e para o leitor é sempre "apuração ao vivo" (diário, D29).

### N18. Contas refeitas com o valor completo
- **O que aconteceu:** os CSV do T03 guardam fatias, variações, captura e taxas de abstenção com 4 casas. A página refaz essas contas a partir das contagens de votos, com o valor completo, e arredonda uma vez, na hora de mostrar (diário, D25).
- **Como foi tratado:** `scripts/pagina_dados.py` confere que as contas refeitas batem com o CSV (diferença de até 0,00006) em todas as unidades e nos 5.757 municípios. Num município, Ribeirão do Largo (BA), a variação da fatia do Lula é de −0,00002 ponto (de 72,5053% para 72,5053%, com votos de 4.425 × 1.678 e 4.781 × 1.813): o CSV mostra 0,0000, e a página conta o município entre os 160 em que a fatia do Flávio subiu. Pelo CSV, seriam 159. A regra é a mesma para os dois candidatos: o sinal vem do valor completo.
- **Onde pesa:** a contagem de municípios do capítulo 2 ("a fatia dele subiu em 160 municípios") e a cor do ponto de Ribeirão do Largo nas dispersões dos capítulos 1 e 3.
- **Marca "ver nota" na página (T08):** texto do capítulo 2 ("Ver detalhes").
- **Fontes:** `dados/analise_municipios.csv` (T03).
- **Origem:** T08.

---

### N19. Dados sociais: anos e universos diferentes
- **O que aconteceu:** os dados sociais dos municípios vêm de fontes e anos diferentes dos da eleição de 2026: o Censo 2022 (idade, alfabetização, renda, densidade, religião e cor ou raça) e o PIB dos Municípios de 2023, o mais recente publicado. Cada variável também tem o próprio universo: a alfabetização é das pessoas de 15 anos ou mais; a religião, das pessoas de 10 anos ou mais, porque é assim que o Censo 2022 perguntou; a renda, dos moradores em domicílios particulares permanentes (99,5% da população); as outras, da população inteira. A religião e a renda vêm da amostra do Censo (estimativas, não contagem); a soma dos municípios difere do Brasil publicado em até 34 pessoas por arredondamento. Na categoria "evangélicas" do IBGE entram as igrejas de missão, como a luterana, e não só as pentecostais.
- **Como foi tratado:** cada variável é usada como o IBGE publicou, com o ano e a fonte ao lado (`dados/dados_sociais_municipios.json`, campo `meta.variaveis`). O PIB por habitante é o publicado pelo IBGE, que divide o PIB de 2023 pela população do Censo 2022. A pobreza entra pela renda do Censo 2022 (moradores com renda domiciliar per capita de até meio salário mínimo, com os sem rendimento), e não pelo CadÚnico de 2026, como estava registrado: o site do MDS saiu do ar em 21/10/2026, e a troca foi feita antes de qualquer cruzamento com a eleição (decisão do autor, P26, 26/10/2026, 23:41).
- **Onde pesa:** o capítulo novo "Como eram os lugares onde cada um cresceu?" (T34) e os dados sociais no Explorar. O ano fica escrito em cada gráfico. Associação entre lugares não diz como votou cada pessoa (especificação 6.1).
- **Marca "ver nota" na página (T34):** fonte das figuras 8.1 e 8.2; "Os dados sociais", no "Ver detalhes" do capítulo 8; perfil do município na ficha da cidade (Resumo e Explorar); figura E5 do Explorar (eixos à escolha); limite 8 de Método e fontes.
- **Fontes:** linhas "Censo 2022…" e "PIB dos Municípios 2023 (T26)" do registro do T12.
- **Origem:** T26.

### N20. Boa Esperança do Norte (MT) sem dados sociais
- **O que aconteceu:** o TSE tem 5.571 municípios no Brasil, e o IBGE, 5.570 no Censo 2022 e no PIB de 2023. A diferença é Boa Esperança do Norte (MT, código IBGE 5101837), criado em 2000 a partir de Sorriso e Nova Ubiratã e instalado em 2025, depois do Censo. Os outros 5.570 casam pelo código IBGE da lista do TSE, um a um, sem sobra.
- **Como foi tratado:** o município fica no arquivo dos dados sociais, com todas as variáveis vazias, e fora dos testes com dados sociais (5.570 municípios). Nada foi repartido dos municípios de origem: não há como saber que parte da população e do PIB de Sorriso e de Nova Ubiratã ficou com ele.
- **Onde pesa:** só nos cruzamentos com dados sociais (T34) e no Explorar. Nas contas da eleição ele continua.
- **Marca "ver nota" na página (T34):** fonte das figuras 8.1 e 8.2; "Como se chegou à conclusão" e "Os dados sociais", no "Ver detalhes" do capítulo 8; ficha da cidade de Boa Esperança do Norte (sem o perfil); figura E5 do Explorar, que deixa o município fora quando o eixo é um dado social.
- **Fontes:** lista de municípios do TSE (`dados/tse_config/mun-e006258-cm.json`) e as tabelas do Censo 2022 e do PIB dos Municípios (registro do T12). Criação: [Lei estadual 7.264/2000 de Mato Grosso](https://www.al.mt.gov.br/storage/webdisco/leis/lei-7264-2000.pdf); a validação pelo STF (ADPF 819, 2023) e a instalação em 1º/01/2025 foram vistas pela busca, em notícias, sem abrir a decisão.
- **Origem:** T26.

### N21. Presidente, 1º turno: os votos do candidato 28 são nulos técnicos
- **O que aconteceu:** no 1º turno, o candidato a presidente de número 28 teve 5.246 votos que o resultado oficial não conta como válidos: são "nulos técnicos" (voto em candidato com o registro cancelado ou negado em definitivo, que continuava na urna). No arquivo oficial do Brasil, os nulos somam 3.674.249 = 3.669.003 votos nulos + 5.246 nulos técnicos (`tvn` = `vn` + `vnt`). Nos arquivos por seção do TSE, esses votos aparecem como votos do candidato: na votação por seção (número 28) e nos votos nominais do detalhe da apuração. Não há voto sub judice de presidente (N02).
- **Como foi tratado:** como no resultado oficial. Na tabela por seção (T27, `dados/secoes_presidente.csv.gz`), os votos do 28 ficam numa coluna própria (`t1_28`), fora dos válidos; brancos e nulos oficiais = brancos + nulos + votos do 28. Assim a soma das seções bate com a base municipal em todos os municípios. As bases municipais (T03) já seguiam o oficial: os "outros candidatos" do 1º turno não incluem o 28.
- **Onde pesa:** nada muda nos números do estudo. São 0,004% do comparecimento, espalhados por 5.145 seções. Vale para as contas por seção (ticket a criar, antes do T33).
- **Marca "ver nota" na página:** figuras 3.2, 4.2, 9.1, E11, E12, E13 e E14 (conferido na revisão final, 27/10/2026).
- **Nas contas por seção (T35, 27/10/2026):** os votos do 28 entram nos brancos e nulos do 1º turno, fora dos válidos e dos "outros candidatos", como no oficial: 5.123 nas seções do Brasil (os outros 123 são do exterior, que fica fora das contas). A soma das seções bate com a base municipal nos 5.571 municípios. São 0,004% do comparecimento e não mexem em nenhum número. **Marca na página (T35):** figuras 3.2 e 4.2 e figuras E11 a E14 do Explorar, e o "Como calculamos" da figura 4.2; texto da nota na página em `nt.N21.1` e `nt.N21.2`.
- **Fontes:** linhas do T27 no registro do T12 ("Votação por seção, presidente" e "Detalhe da apuração por seção"); arquivo oficial do Brasil do 1º turno, `resultados.tse.jus.br/oficial/ele2026/6257/dados/br/br-c0001-e006257-u.json` (campos `vn`, `vnt` e `tvn`).
- **Origem:** T27.

### N22. Seções eleitorais: as mesmas nos dois turnos, com agregadas e aptos que mudam
- **O que aconteceu:** o TSE lista 499.248 seções de presidente em cada turno, as mesmas nos dois (casadas por UF, município, zona e seção). Delas:
  - 41, no exterior, não foram instaladas em nenhum dos turnos: têm 423 aptos (no 1º turno), que entram no eleitorado, e nenhum comparecimento;
  - 17.931 seções foram agregadas a outras 16.142 no 2º turno: os eleitores votaram na seção que as recebeu, e elas não aparecem como seção própria em nenhum dos turnos. A lista das agregadas do 1º turno está só no boletim de urna do 1º turno, que não foi baixado (P11), mas a lista de seções é a mesma nos dois turnos;
  - 2 seções do exterior instaladas não tiveram nenhum comparecimento (1 nos dois turnos e 1 só no 2º);
  - os aptos mudam entre os turnos em 55.722 seções (11%): em 54.925 delas, em até 5 eleitores; a maior mudança é de 84. No Brasil, o eleitorado é o mesmo nos dois turnos (158.745.502), redistribuído entre seções e municípios (T02).
- **Como foi tratado:** uma linha por seção, com os dois turnos lado a lado e os aptos de cada turno como o TSE informa. Nenhuma seção ficou sem par. As agregadas do 2º turno estão na coluna `t2_agregadas` da seção que as recebeu.
- **Onde pesa:** só nas contas por seção (ticket a criar, antes do T33). A variação do comparecimento por seção tem de usar os aptos de cada turno.
- **Marca "ver nota" na página:** figuras 3.2, 4.2, 9.1, 9.3, E11, E12, E13 e E14 (conferido na revisão final, 27/10/2026).
- **Nas contas por seção (T35, 27/10/2026; `HIPOTESES.md`, 4.5):** entram as 497.897 seções do Brasil, todas instaladas e com aptos nos dois turnos (o exterior fica fora, como nas contas por município). As agregadas entram dentro da seção que as recebeu, como o TSE publica: as 14.926 seções do Brasil que receberam agregadas têm, em média, os mesmos aptos nos dois turnos (323,06 e 323,07), sinal de que a agregação foi a mesma. Os aptos ficam como o TSE informa, com os do 1º turno como peso e divisor. Duas conferências, que não mudam a leitura: sem as 797 seções cujos aptos mudam mais de 5 eleitores e sem as 14.926 que receberam agregadas. **Marca na página (T35):** figuras 3.2 e 4.2, figuras E11 a E14 do Explorar, o "Como calculamos" da figura 4.2 e o limite 6 de Método e fontes; texto da nota na página em `nt.N22.1` e `nt.N22.2`.
- **Fontes:** linhas do T27 no registro do T12 (boletins de urna do 2º turno e detalhe da apuração por seção).
- **Origem:** T27.

### N23. Exploração guiada: candidatos agrupados, estados com 2º turno para governador e seções que entram
- **O que aconteceu:** as cinco perguntas da exploração guiada (T33; `HIPOTESES.md`, seção 8, rodada 1) usam os votos de cada candidato do 1º turno por seção, a situação dos candidatos a governador e recortes de seções que as contas anteriores não usavam.
- **Como foi tratado:** (1) os outros candidatos entram separados só os três com mais votos (Augusto Cury, Avante, 70; Renan Santos, Missão, 14; Ronaldo Caiado, PSD, 55); os outros sete (30, 80, 16, 27, 21, 35 e 29) entram juntos, porque cada um tem poucos votos para uma estimativa sozinho; os votos do 28 continuam fora dos válidos (N21). Os nomes são os de urna, conferidos no arquivo de votação por seção do TSE. (2) Os estados "com 2º turno para governador" são os que têm algum candidato com a situação "2º turno" no resultado oficial do 1º turno de governador: AC, AM, DF, ES, RN e TO. (3) Na pergunta 4, entram as seções com votos para o Lula e para o Flávio no 1º turno; na 5, as com votos para os dois nos dois turnos (sem isso, a fatia não existe). As agregadas e os aptos que mudam seguem a N22, com as mesmas duas conferências.
- **Onde pesa:** só no capítulo 9. Nenhum número dos capítulos 1 a 8 muda.
- **Marca "ver nota" na página:** figuras 9.1 e 9.3; texto da nota na página em `nt.N23.1` e `nt.N23.2`.
- **Fontes:** linhas "Exploração guiada (T33)" na tabela "Onde cada fonte entra no estudo" do T12 (dados por seção do T27 e JSON oficial do governador do T04).
- **Origem:** T33.

### N24. Perfil por idade: só o 1º turno, eleitores em trânsito, analfabetos, falecidos no cadastro e seções do cadastro
- **O que aconteceu:** o perfil de comparecimento e abstenção do TSE (extração de 13/10/2026) só tem o 1º turno; o 2º não está publicado em lugar nenhum (dados abertos e painel de estatísticas, 28/10/2026). Os totais do Brasil batem com o oficial quase exatamente (aptos 158.745.463 × 158.745.502; comparecimento 125.277.230 × 125.275.835), mas 5.652 municípios diferem: o perfil conta os 595.156 eleitores em transferência temporária (trânsito) na cidade de origem, e o resultado, onde votaram. O voto é facultativo para os analfabetos em qualquer idade: de 18 a 69 anos, 3.315.540 aptos estão na coluna de voto facultativo. O cadastro ainda tem eleitores que morreram e não foram tirados: há 297.977 aptos de 100 anos ou mais, e 0,7% votaram. O perfil do eleitorado por seção é do cadastro fechado (gerado em 14/07/2026): 2.043.134 inscritos estão em seções que não existem no resultado (criadas, juntadas ou renumeradas depois), 389 seções do resultado não têm perfil e 19.073 diferem dos aptos do 1º turno em mais de 5%. 23.335 aptos de 18 anos ou mais não têm gênero no cadastro.
- **Como foi tratado:** só o 1º turno, dito assim. As contagens por idade saem no Brasil, nas regiões e nos estados, nunca por município. Os grupos de idade são pela idade, não pela coluna de voto facultativo. Os falecidos não são corrigidos: a abstenção das faixas de cima é dita como maior que a real. Na comparação de seções (I5b), as 389 sem perfil saem e as 19.073 que diferem saem numa conferência, sem mudar o resultado. O gênero não informado fica à parte.
- **Onde pesa:** só na exploração guiada, rodada 2 (T37; `HIPOTESES.md`, seção 8; capítulo 9, perguntas 6 a 10). Nenhum número dos capítulos 1 a 8 muda.
- **Marca "ver nota" na página:** figuras 9.4, 9.5 e 9.6 e o "Ver detalhes" do capítulo 9, pergunta 6; texto da nota na página em `nt.N24.1` e `nt.N24.2`.
- **Fontes:** linhas "Perfil de comparecimento e abstenção (T37)" e "Perfil do eleitorado por seção (T37, I5b)" do registro do T12.
- **Origem:** T37.

### N25. Projeções refeitas: a ordem de chegada dos boletins em 2026, 2022, 2018 e 2024
- **O que aconteceu:** as projeções refeitas do capítulo 7 (T41, exploratório) precisam da hora em que o TSE recebeu cada boletim. Em 2026 e 2022 ela está no boletim de urna (`DT_BU_RECEBIDO`); em 2018, só no `detalhe_votacao_secao_2018.zip` (`DT_RECEBIMENTO_BU_HOR_TSE`, preenchida nas 454.490 seções dos dois turnos). Em 2022, os dois campos são iguais seção a seção (AC: 7.925 de 7.925). Em 2014, nem o detalhe nem o boletim têm a hora.
- **Como foi tratado:** 2018 entra com a ordem pelo detalhe; 2014 fica de fora. Em 2024, entram as 51 cidades com prefeito no 2º turno (eleição ordinária; o arquivo `_BRASIL` do detalhe repete as UFs e ficou de fora). Todas as seções do 2º turno têm hora e par no 1º turno. Numa cidade só, (a) vira a contagem e (d) fica quase igual a (c): o teste do prefeito é mais fraco para esses dois. Métodos, pisos e variáveis fixados antes de rodar; regras de cada teste escritas antes (T41).
- **Onde pesa:** só no "Ver detalhes" do capítulo 7, seção "Projeções refeitas depois (exploratório)". Nenhum número dos capítulos 1 a 6 muda.
- **Marca "ver nota" na página:** "Ver detalhes" do capítulo 7; texto da nota na página em `nt.N25.1` e `nt.N25.2`.
- **Fontes:** linhas "Projeções refeitas: 2022, 2018 e 2024 (T41)" do registro do T12 (com os `baixados.json` de `dados/tse_2022/`, `dados/tse_2018/` e `dados/tse_2024/`).
- **Origem:** T41; na página no T42.
