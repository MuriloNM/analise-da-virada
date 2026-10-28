# Hipóteses e regras fixadas antes das contas

> Cópia do registro das hipóteses do estudo, como foi escrito durante o trabalho: as regras de cada teste, fixadas antes das contas, e as mudanças depois da aprovação, com data e motivo. Os códigos T (tarefas), D (diário), P (decisões do autor) e os nomes de sessão remetem ao registro interno de trabalho, que não está neste repositório.

**Situação:** **aprovado pelo autor em 26/10/2026, 12:43, como estava**, com a fatia do Lula sobre os válidos na vantagem potencial (P14; conversa na sessão t06-inferencia; especificação 9; diário D20) · Escrito em 26/10/2026, 12:36, sessão t06-inferencia (ticket T06) · Diretrizes 1.1.2 e 1.1.3 da especificação.

Cada hipótese tem o teste e o que conta como confirmação, como resultado contrário e como inconclusivo. Os cortes e as regras de dados também ficam aqui. **Depois da aprovação, este arquivo só muda com uma nota datada na seção "Mudanças depois da aprovação", dizendo o porquê, e antes de ver o resultado que a mudança afeta.** O resultado aparece na página mesmo quando a hipótese não se confirma.

## Em uma tela: o que o autor precisava olhar (aprovado em 26/10/2026, 12:43)

1. **P14 (fatia do Lula na vantagem potencial):** decidido pelo autor como recomendado: usar a fatia sobre os válidos (L ÷ válidos), com a fatia entre os dois (L ÷ (L + F)) como conferência. Seção 3, H5.
2. **Teste principal "dentro dos estados":** cada hipótese é testada comparando municípios do mesmo estado (efeito fixo de UF); a versão "Brasil", com todos juntos, como na especificação, sai ao lado. É uma escolha a mais em relação à especificação. Motivo: a tabela das UFs já foi vista (seção 1), e a comparação dentro do estado não foi vista por ninguém. Seção 2.5.
3. **Critério de precisão por lugar:** pelo menos 30 municípios, meia largura do intervalo de 95% de até 10 pontos e estimativa entre 0% e 100%. Seção 4.2.
4. **Votos sub judice:** fora dos válidos, como no oficial; duas conferências. Seção 5.4.
5. **Missão:** regra A nas contas principais, regra B como conferência (nota N11). Seção 3, H5.
6. **Senador:** só comparação dentro do estado, sem os estados em que o campo da esquerda teve menos de 5% dos votos de senador. Seção 3, H5.
7. **Versão espelho para o Flávio** no teste do voto dividido, com a mesma conta para o campo da direita. É um acréscimo à especificação, pela neutralidade. Seção 3, H5.
8. **Inferência ecológica por município (PyEI) fica fora desta rodada.** Seção 4.5.
9. **Dados sociais:** lista curta provisória de 7 variáveis, que só vale se o T26 entrar (decisão P11). Seção 6.
10. **P13** fica resolvida com a aprovação deste arquivo: ele foi escrito antes de qualquer conta com o 2º turno por município.

## 1. O que já tinha sido visto antes de escrever

Para o leitor saber de que lugar as hipóteses foram escritas:
- **Visto:** os totais do Brasil (especificação, seção 2, e relatório do T03), inclusive a captura de 73,6%; a **tabela das UFs** do relatório do T03 (fatia, Δs, ΔM, peso, captura e abstenção nos dois turnos, por estado); no T05, o % de esquerda do Brasil por cargo e alguns municípios citados nas ressalvas de sub judice e do Missão, só com números do 1º turno.
- **Não visto:** nenhum número de 2º turno por município, nenhum cruzamento dos votos por partido com o 2º turno e nenhuma regressão. Esta sessão não abriu `dados/analise_municipios.csv`, `dados/esquerda_1t_municipios.csv` nem `dados/historico_2t.*`; olhou só o cabeçalho do histórico e o comentário do `scripts/collector.py` que descreve a projeção.
- **Consequência:** as direções de H1, H3 e H4 podem ter sido influenciadas pela tabela das UFs. Por isso, o teste que decide é o de **dentro dos estados** (seção 2.5), que compara municípios do mesmo estado e que ninguém viu.

## 2. Regras gerais (valem para todos os testes)

### 2.1 Quem entra
- **Os 5.571 municípios do Brasil.** Os 186 do exterior ficam fora das regressões, do funil e da regressão ecológica: não têm estado (que é o grupo do erro padrão), só votam para presidente e têm abstenção de outra ordem (nota N06). Continuam em todas as contagens e no total do Brasil.
- Nenhum município do Brasil fica sem fatia ou sem Δs (os vazios da nota N09 são todos do exterior, menos a captura).

### 2.2 Medidas
- **s1, s2:** fatia do Lula entre os dois, em % (especificação, seção 4). **Δs** = s2 − s1, em pontos percentuais (p.p.). A fatia do Flávio é 100 − s, e a variação dela é −Δs.
- **o:** votos dos outros candidatos no 1º turno ÷ votos válidos do 1º turno (O1 ÷ vv1), em %.
- **Δa:** variação da taxa de abstenção, em p.p., cada turno com o próprio eleitorado (nota N05).
- **Votos ganhos por eleitor:** ΔL ÷ E1 e ΔF ÷ E1, em % do eleitorado do 1º turno (E1), para comparar municípios de tamanhos diferentes.

### 2.3 Peso
- Regressão **ponderada pelo eleitorado do 1º turno** (E1), como na especificação (seção 5). O 1º turno é o mesmo usado no porte (nota N08).
- Conferência: a mesma regressão sem peso, em que cada município conta igual.

### 2.4 Erro padrão e intervalo
- **Erro padrão agrupado por estado** (27 grupos), com a correção para poucos grupos (CR1) e intervalo de 95% pela distribuição t com G − 1 graus de liberdade: 25 na versão principal (26 estados, porque o DF, com um município só, não tem comparação dentro do estado) e 26 na versão Brasil. *(Corrigido em 26/10/2026, 22:31, T32: o texto dizia "26 graus de liberdade"; o script sempre usou G − 1. Ver "Mudanças depois da aprovação".)*
- **Conferência para poucos grupos:** com 27 estados de tamanhos muito diferentes, o erro agrupado pode sair estreito demais. Por isso, cada teste de hipótese também tem o valor-p do bootstrap selvagem por grupo (*wild cluster bootstrap*, pesos de Webb, 9.999 repetições, hipótese nula imposta; Cameron, Gelbach e Miller, 2008; Webb, 2023).
- Semente fixa de todos os sorteios: **20261026**, gravada no `dados/inferencia.json`.

### 2.5 Duas versões de cada padrão
- **Dentro dos estados (principal):** a regressão com efeito fixo de UF, que compara cada município com outros do mesmo estado. Tira da conta o que é comum a todo o estado: os candidatos a governador e a senador, a força de cada partido no estado e o 2º turno para governador. É a versão que decide a classificação.
- **Brasil:** todos os municípios juntos, sem efeito fixo, como está na especificação. Sai ao lado, com a mesma classificação. Se as duas discordarem, o texto diz isso ("No Brasil como um todo… ; comparando municípios do mesmo estado…").
- R²: na versão Brasil, o R² comum; na versão dentro dos estados, o R² dentro dos estados (só a variação entre municípios do mesmo estado).

### 2.6 Classificação de cada hipótese
- **Confirmada:** o intervalo de 95% fica inteiro do lado previsto e o valor-p do bootstrap selvagem fica abaixo de 0,05.
- **Contrária:** o intervalo fica inteiro do lado oposto ao previsto e o valor-p fica abaixo de 0,05.
- **Inconclusiva:** o intervalo inclui zero, ou os dois métodos discordam (um diz que há associação e o outro não).
- **Tamanho:** junto de toda associação sai o **efeito interquartil**, a diferença prevista de Δs entre um município no quartil de baixo e um no quartil de cima da variável (quartis ponderados por E1; na versão dentro dos estados, depois de tirar a média de cada estado). Abaixo de 0,5 p.p. (cerca de um sexto da variação do Brasil, 2,80 p.p.), o texto chama a associação de "pequena". O tamanho muda só a palavra, não a classificação.

### 2.7 Várias hipóteses e várias versões
- São quatro hipóteses (H1, H3, H4 e H5), uma por capítulo, cada uma com o próprio teste principal. Não há correção para comparações múltiplas entre elas, porque cada uma responde a uma pergunta diferente.
- As conferências (sem peso, Brasil, outras escalas, outras regras de dados) não mudam a classificação. A página diz em quantas versões o resultado se mantém ("se mantém em 9 de 11 versões") e lista as que não mantêm.

### 2.8 Linguagem
- Sempre "municípios onde…", nunca "eleitores que…": associação entre lugares não diz como votou cada pessoa (diretriz 1.1.5).
- Cada frase passa pelo teste da troca: seria escrita igual se o resultado favorecesse o outro candidato.

## 3. Hipóteses

O número é o do capítulo da aba Análise (especificação 7.2). Os capítulos 2 (onde o Flávio cresceu) e 6 (peso na virada) são contagem, sem hipótese; o 7 (projeção) é erro medido (seção 4.4).

**Um modelo simples por trás de H1, H3 e H4.** Se, em todo município, o saldo que os dois ganharam no 2º turno (S = ΔL + ΔF, que soma os votos dos outros, a variação do comparecimento e a queda de brancos e nulos) se dividisse na mesma proporção *a* para o Lula, a variação da fatia seria Δs = g × (a − s1), em que g = S ÷ (L2 + F2) é o peso desse saldo nos votos do 2º turno. Daí saem três previsões: Δs menor onde s1 é maior (H1); e, onde *a* é maior que s1, Δs maior onde há mais saldo, seja dos outros candidatos (H3), seja do comparecimento (H4). No Brasil, *a* foi 73,6% (a captura), acima da fatia do 1º turno no Brasil (48,989%) e em quase todos os estados. As hipóteses vêm desse modelo e desse número nacional, não de preferência: se a captura tivesse sido do Flávio, as mesmas contas preveriam os sinais opostos, e as hipóteses seriam escritas para ele.

### H1. Capítulo 1: onde o Lula cresceu mais, onde já era forte ou onde era fraco?
- **Hipótese:** a fatia do Lula subiu mais onde ela era menor no 1º turno. Dito para os dois: **cada candidato ganhou mais fatia (ou perdeu menos) onde era mais fraco no 1º turno.** As duas frases são a mesma conta, porque a fatia do Flávio é 100 − s.
- **Teste:** Δs = α + β × s1, ponderado por E1, erro agrupado por UF; principal dentro dos estados.
- **Confirmação:** β < 0 pelo critério da seção 2.6. **Contrária:** β > 0. **Inconclusiva:** como na 2.6.
- **Mostrar:** β por 10 p.p. de s1, intervalo, R², efeito interquartil, nas duas versões.
- **Limite:** pelo modelo da seção 3, essa direção é esperada mesmo sem nenhuma mudança de comportamento. O que o teste informa é o tamanho e se vale dentro dos estados.
- **Complemento, sem hipótese:** votos ganhos por eleitor de cada um (ΔL ÷ E1 e ΔF ÷ E1) contra a fatia de cada um no 1º turno, com a mesma regressão, para mostrar o crescimento em votos ao lado do crescimento em fatia.

### H3. Capítulo 3: os votos dos outros candidatos do 1º turno explicam o crescimento?
- **Hipótese:** a fatia do Lula subiu mais (e a do Flávio caiu mais) onde os outros candidatos tiveram mais votos no 1º turno.
- **Teste:** Δs = α + β × o, ponderado por E1, erro agrupado por UF; principal dentro dos estados.
- **Confirmação:** β > 0. **Contrária:** β < 0. **Inconclusiva:** como na 2.6.
- **Mostrar:** β por 10 p.p. de o, intervalo, R² e efeito interquartil.
- **Conferência:** modelo conjunto Δs = α + β1 × s1 + β2 × o + β3 × Δa, para ver se cada associação se mantém com as outras duas na conta (vale para H1, H3 e H4).
- A parte "de onde vieram os votos" (quanto do saldo dos outros foi para cada um) é estimativa, sem hipótese: seção 4.1.

### H4. Capítulo 4: o comparecimento mudou?
- **O fato não precisa de hipótese:** onde a abstenção subiu e caiu é contagem (Δa, do T03), mostrada sempre.
- **Hipótese:** a fatia do Lula subiu mais (e a do Flávio caiu mais) onde a abstenção caiu mais.
- **Teste:** Δs = α + β × Δa, ponderado por E1, erro agrupado por UF; principal dentro dos estados.
- **Confirmação:** β < 0 (Δa mais negativo, Δs maior). **Contrária:** β > 0. **Inconclusiva:** como na 2.6.
- **Complemento, sem hipótese, igual para os dois:** ΔL ÷ E1 e ΔF ÷ E1 contra Δa, cada um com a mesma regressão. Mostra quanto cada um ganhou em votos onde a abstenção caiu ou subiu.
- **Limite:** o eleitorado de um município muda entre os turnos (nota N05), e parte da variação do comparecimento de um lugar pode ser de eleitores que votaram em outro lugar no outro turno.
- Para onde foi o saldo do comparecimento, por região e estado, é estimativa, só onde for precisa: seção 4.2.

### H5. Capítulo 5 e especificação 6: o voto para deputado e senador já apontava para isso?
- **Hipótese (especificação 6):** onde o eleitor já votava em partidos do campo da esquerda para deputado ou senador, mas não no Lula para presidente no 1º turno, o Lula cresceu mais no 2º turno.
- **Medidas** (T05, sem mudança):
  - **% de esquerda** do cargo: votos dos partidos com posição até 4,49 na rodada de 2022 da pesquisa com especialistas ÷ votos válidos do cargo (`pct_esq`);
  - **vantagem potencial** V = % de esquerda − fatia do Lula no 1º turno, em p.p.
- **Qual fatia do Lula entra em V (decisão P14).** Recomendação: **sobre os válidos, L ÷ vv1**.
  - Por quê: o % de esquerda divide pelos votos válidos de deputado (todos os partidos). A fatia sobre os válidos de presidente divide do mesmo jeito (todos os candidatos), e V vira a diferença entre duas parcelas comparáveis: "dos votos válidos para deputado, quantos % foram para partidos do campo" menos "dos votos válidos para presidente, quantos % foram para o Lula". Com a fatia entre os dois, quem votou num partido do campo para deputado e num outro candidato para presidente sai da base do Lula, e V fica menor justamente onde os outros candidatos foram fortes.
  - A outra, **L ÷ (L + F)**, a da seção 4 e a que está hoje na coluna `vantagem` do T05, fica como conferência.
  - O controle da regressão é a **mesma** fatia usada em V. Assim, β mede a associação do % de esquerda com Δs entre municípios com a mesma fatia do Lula no 1º turno.
  - Para o Flávio, na versão espelho (abaixo), vale a mesma escolha: F ÷ vv1 no principal e F ÷ (L + F) na conferência.
- **Teste principal, para cada cargo:** Δs = α_UF + β × V + γ × (fatia do Lula no 1º turno), ponderado por E1, erro agrupado por UF, com efeito fixo de UF. A versão Brasil (sem efeito fixo) sai ao lado, como está na especificação.
  - Por que dentro dos estados aqui também: os candidatos a deputado e a senador são os mesmos em todo o estado, e a oferta de candidatos de cada partido muda de um estado para outro. Comparar municípios do mesmo estado separa o voto do eleitor da oferta de candidatos.
- **Confirmação:** β > 0. **Contrária:** β < 0. **Inconclusiva:** como na 2.6.
- **Três cargos, três classificações:** deputado federal (o principal, porque existe em todo o país, inclusive no DF, e tem um voto por eleitor), deputado estadual (o distrital no DF) e senador. A página diz o resultado de cada um.
- **Senador, regras próprias:**
  - dois votos por eleitor, contados em cima e embaixo da conta, como no T05 (nota N01);
  - **ficam fora os estados em que o campo da esquerda teve menos de 5% dos votos válidos de senador no estado.** Ali o % de esquerda mede a falta de candidato do campo, e não o voto. Pelo T05, Alagoas (0,8%) e Piauí (1,2%) estão nessa situação; o script lista todos os que caem na regra, sem escolher caso a caso;
  - como no resto, só a comparação dentro do estado decide, porque os candidatos a senador são os mesmos no estado inteiro.
- **Missão (nota N11):** regra A nas contas principais (votos do Missão dentro dos válidos e fora do campo). Regra B como conferência (votos do Missão fora da conta: `esq` ÷ (`vv` − `sem_posicao`)).
- **Votos sub judice:** regra da seção 5.4.
- **Conferências, para cada cargo** (não mudam a classificação; seção 2.7):
  1. versão Brasil, sem efeito fixo;
  2. sem peso;
  3. **escala contínua** no lugar do % de esquerda (média das posições ponderada pelos votos; quanto menor, mais à esquerda): Δs = α_UF + β × escala + γ × fatia, com a previsão β < 0;
  4. fatia entre os dois (L ÷ (L + F)) em V e no controle;
  5. Missão pela regra B;
  6. votos sub judice somados aos válidos e aos partidos deles (`pct_esq_com_sj`);
  7. sem os municípios em que os votos sub judice passam de 5% de (válidos + sub judice) no cargo;
  8. com os outros candidatos do 1º turno (o) também no controle;
  9. escala da rodada de 2018 da mesma pesquisa (`conf_2018_pct_esq`);
  10. **espelho para o Flávio** (abaixo).
- **Espelho para o Flávio:** a mesma pergunta virada para o outro lado. "Onde o eleitor já votava em partidos do campo da direita para deputado ou senador, mas não no Flávio, o Flávio perdeu menos fatia (ou ganhou mais)?"
  - % de direita = votos dos partidos com posição acima do corte ÷ válidos do cargo = 100 − % de esquerda − % do Missão. Pela escala, não há partido de centro (nenhum entre 4,12 e 6,01; T05), e o Missão fica fora dos dois campos, pela mesma regra A;
  - vantagem do Flávio = % de direita − F ÷ vv1;
  - teste: −Δs = α_UF + β × vantagem do Flávio + γ × F ÷ vv1, com a previsão β > 0.
  - O espelho não é a mesma conta do principal com o sinal trocado (o controle muda), e por isso pode dar outro resultado. Sai ao lado do principal, com a mesma classificação.
- **Limite:** associação entre municípios. Não diz que os eleitores que votaram num partido do campo para deputado foram os que mudaram o voto para presidente.

## 4. Estimativas sem hipótese (sempre com intervalo)

### 4.1 De onde vieram os votos (capítulo 3 e Explorar)
- **Regressão ecológica** (Goodman, 1953) entre municípios, com as variáveis divididas pelo eleitorado do 1º turno, ponderada por E1 e **sem intercepto**:
  - ΔL ÷ E1 = b_O × O1 ÷ E1 + b_C × ΔC ÷ E1 + b_R × R ÷ E1, em que R = −ΔBN (a queda de brancos e nulos);
  - a mesma conta para ΔF.
- Como ΔL + ΔF = O1 + ΔC + R em todo município (identidade do T03), os coeficientes dos dois somam 1 em cada fonte (b_O do Lula + b_O do Flávio = 1, e assim por diante). A conta é a mesma para os dois, e a divisão de cada fonte entre eles fecha em 100%.
- **Leitura:** "de cada 100 votos do saldo de uma fonte, tantos ficaram, em termos líquidos, com cada um". Tudo é saldo: parte de quem votou no 1º turno faltou no 2º, e vice-versa, e os dados não mostram pessoas. **Aviso fixo: vale para lugares, não para pessoas.**
- **Intervalo:** bootstrap de 1.000 repetições, reamostrando municípios dentro de cada estado (a quantidade de cada estado fica igual), intervalo de percentis 2,5 e 97,5.
- **Conferências:** (a) com intercepto: um intercepto diferente de zero quer dizer que parte da mudança não acompanha nenhuma das três fontes, o que acontece, por exemplo, se houve troca direta entre os dois candidatos; (b) bootstrap reamostrando estados inteiros, que leva em conta a semelhança entre municípios vizinhos; (c) sem peso.
- **Limite:** a regressão supõe que cada fonte se divide do mesmo jeito em todos os municípios do grupo. Se a divisão muda de lugar para lugar junto com o tamanho da fonte, a estimativa erra (viés de agregação), e o intervalo não mostra isso.

### 4.2 Para onde foi o saldo do comparecimento, por lugar (capítulo 4)
- A mesma regressão da 4.1, separada por **região** (bootstrap reamostrando dentro de cada estado da região) e por **estado** (bootstrap reamostrando os municípios do estado).
- **Critério de precisão, fixado aqui e igual para os dois candidatos.** Uma estimativa por lugar (b_C e, se for mostrado, b_O e b_R) só sai como resultado se:
  1. o lugar tem **pelo menos 30 municípios**;
  2. a **meia largura do intervalo de 95% é de até 10 pontos** (por exemplo, "entre 55% e 75%");
  3. a estimativa fica **entre 0% e 100%**. Fora disso, o modelo não descreve bem o lugar (uma divisão "acima de 100%" para um quer dizer "abaixo de 0%" para o outro).
  Como as estimativas dos dois somam 100%, o intervalo tem a mesma largura para os dois, e o critério dá o mesmo resultado para o Lula e para o Flávio.
- **Onde não passa**, a estimativa vai para a lista "Estimativas que não deram" (especificação 7.3), com o motivo, pela primeira regra que falhar, nesta ordem:
  - **poucos municípios:** menos de 30 (pelo número de municípios: Roraima, Amapá, Acre e Distrito Federal);
  - **variação pequena do comparecimento:** o desvio padrão de ΔC ÷ E1 entre os municípios do lugar (ponderado por E1) é menor que a metade do mesmo desvio no Brasil;
  - **resultados muito dispersos:** nos outros casos em que o intervalo passa de 10 pontos;
  - **fora de 0% a 100%:** quando só a regra 3 falha.
- **Leitura na página:** "a maior parte do saldo foi para X" só quando o intervalo inteiro fica acima de 50% para X. Quando o intervalo inclui 50%, o texto diz que o saldo se dividiu sem lado claro. Onde o comparecimento caiu no total do lugar, o texto fala da perda ("de cada 100 eleitores a menos…").
- Toda estimativa que não deu também vira item da nota "Estimativas que não deram" no `NOTAS.md`.

### 4.3 Funil (Explorar e "Ver detalhes" dos capítulos 1 e 4)
- **Para que serve:** mostrar quanto um município pode variar só por ser pequeno, para ninguém ler o topo de um ranking de cidades pequenas como um padrão.
- **Eixos:** Δs (p.p.) contra o eleitorado do 1º turno (escala logarítmica). Um segundo funil, com o mesmo método, para Δa.
- **Centro:** a variação do conjunto dos municípios do Brasil (Δs e Δa somando os 5.571, sem o exterior).
- **Faixa:** modelo de Spiegelhalter (2005) para indicadores com dispersão maior que a do acaso:
  - parte do acaso: o erro de uma diferença de fatias num município daquele tamanho, √(θ1(1 − θ1) ÷ n1 + θ2(1 − θ2) ÷ n2), com θ as fatias do Brasil e n = E × (votos dos dois ÷ eleitorado, no Brasil) em cada turno. A faixa depende só do eleitorado, e o gráfico e a lista usam a mesma conta; os dois turnos são tratados como independentes, o que deixa a faixa um pouco mais larga nos municípios pequenos;
  - parte que não é acaso: uma variação τ² comum a todos os municípios, estimada pelo método dos momentos com as distâncias padronizadas cortadas nos percentis 10 e 90 (*winsorização*), como no artigo;
  - faixa final: centro ± z × √(erro² + τ²), com z = 1,96 (95%) e 3,09 (99,8%).
  - Para Δa, a mesma conta com as taxas de abstenção do Brasil em cada turno e o eleitorado do 1º turno nos dois termos, para a faixa depender só dele.
- **Lista:** os municípios fora da faixa de 99,8%, dos dois lados, com o eleitorado, o valor e a faixa. Os nomes dos lados são simétricos: "a fatia do Lula subiu mais que o esperado" e "a fatia do Flávio subiu mais que o esperado". Também a contagem fora da faixa de 95% (pelo modelo, cerca de 5% ficariam fora por acaso).
- **Conferência:** a mesma lista com o erro de cada município calculado com os votos dele (e não pela razão do Brasil), dizendo quantos mudam de lado da faixa.
- **No gráfico:** "A faixa vem de um modelo: mostra quanto um município desse tamanho costuma variar."

### 4.4 Erro da projeção da noite (capítulo 7)
- **O que é a projeção:** a que o site ao vivo mostrou (`projecao_final_pct` em `dados/historico_2t.csv`). Pelo `scripts/collector.py`: o que falta apurar em cada unidade segue o 1º turno mais a variação já observada (da unidade; se não houver, da UF; se não houver, do Brasil).
- **Erro** = projeção − 51,785%, em p.p., em cada leitura do histórico.
- **Faixas de % apurado, fixadas aqui:** de 0% a 10%, de 10% a 20%, …, de 90% a 100% (limite de baixo incluído). Por faixa: número de leituras, erro médio, erro absoluto médio e maior erro absoluto. A leitura de 100% fica fora, porque é o próprio resultado final.
- **Comparação, com a mesma conta:** o erro da contagem parcial (`lula_2t_pct` − 51,785%), para mostrar quanto a projeção corrigiu em relação a só olhar o que já tinha sido apurado.
- O buraco do histórico entre 60,85% e 68,8% fica escrito no gráfico.
- É erro medido, não estimativa: sai sem "±".

### 4.5 Fora desta rodada
- **Inferência ecológica por município (PyEI) e limites da conta por município**, que a especificação deixa como opcionais. Ficam fora porque (a) o PyEI pede instalar um pacote grande de estatística (PyMC), (b) a conta deste estudo é de saldo, que pode ser negativo, e os limites clássicos da conta (Duncan e Davis, 1953) pedem casas não negativas na tabela de cada área *(corrigido em 26/10/2026, 22:31, T32: o texto dizia "supõem contagens que não diminuem"; ver "Mudanças depois da aprovação")*, e (c) a estimativa por município herda a mesma hipótese da 4.1 e não fica mais precisa só por ser por município. Se o autor quiser, entram num ticket próprio, com regras escritas aqui antes.
- **Estimativa por seção eleitoral:** só se o T27 for feito, com as mesmas regras da 4.2 aplicadas às seções de cada município. *(O T27 foi feito; a regra está logo abaixo, em "Regra por seção".)*

#### Regra por seção (T35; escrita em 27/10/2026, 09:34, sessão t35-contas-por-secao, antes de qualquer conta com os votos das seções)
**O que já foi visto ao escrever:** as estimativas por município da 4.2, todas (estão na página e no `inferencia.json`); da tabela por seção (`dados/secoes_presidente.csv.gz`, T27), só a estrutura: aptos de cada turno, seções agregadas, seções instaladas, seções por município e zonas por município. Nenhum voto, comparecimento, branco ou nulo por seção. Achados da estrutura que pesam na regra: as 497.897 seções do Brasil estão instaladas nos dois turnos e têm aptos; todos os 5.571 municípios têm pelo menos 2 seções (mediana de 32); as 14.926 seções do Brasil que receberam agregadas têm, em média, os mesmos aptos nos dois turnos (323,06 e 323,07), sinal de que a agregação foi a mesma nos dois; só 2 municípios têm 30 zonas ou mais.

**Para que serve:** refazer a estimativa da 4.2 (para onde foi o saldo do comparecimento e, na mesma conta, das outras duas fontes) comparando seções do mesmo município, e não municípios. Comparar vizinhos tira da conta o que é comum ao município inteiro (a campanha local, o prefeito, o transporte no dia), que o parecer apontou como o ponto mais fraco da conta por município (M1, item 1, e M2). Como já diz o T35, a conta por seção passa a ser a **principal** para a 4.2, se o autor aprovar depois de ver o resultado; a de municípios fica como conferência.

1. **Medidas por seção**, como no T03 e na 4.1, com os votos do candidato 28 fora dos válidos (nota N21): E1 = aptos do 1º turno; L1, F1 = votos de 13 e 22 no 1º turno; O1 = votos dos outros 10 candidatos (sem o 28); BN1 = brancos + nulos + votos do 28; L2, F2, BN2 (brancos + nulos) e C1, C2 (comparecimento) de cada turno. ΔL = L2 − L1, ΔF = F2 − F1, ΔC = C2 − C1, R = BN1 − BN2. A identidade ΔL + ΔF = O1 + ΔC + R tem de fechar em toda seção; o script confere.
2. **Modelo:** o da 4.1, nas seções, com um **efeito de município**: ΔL ÷ E1 = α_município + b_O × O1 ÷ E1 + b_C × ΔC ÷ E1 + b_R × R ÷ E1, peso E1, e a mesma conta para ΔF. Estimado tirando a média ponderada de cada município (efeito fixo). O efeito de município absorve o que é comum às seções da cidade; os coeficientes vêm só das diferenças entre seções da mesma cidade. As partes do Lula e do Flávio continuam somando 100% em cada fonte (e os dois efeitos de cada município somam zero).
3. **Lugares:** os mesmos da 4.2 (Brasil, as 5 regiões e os 27 estados), cada um com as seções dos seus municípios. Cidades sozinhas ficam fora: o erro precisaria de grupos dentro da cidade (zonas), e só 2 municípios têm 30 zonas ou mais.
4. **Unidade do erro e intervalo:** bootstrap de 1.000 repetições, intervalo de percentis 2,5 e 97,5, semente 20261026. Brasil e regiões: **estados inteiros** reamostrados, como na 4.2 depois do T32 (M2). Estados: **municípios inteiros** reamostrados, cada um com todas as suas seções; o grupo do erro é o município, porque seções da mesma cidade se parecem.
5. **Seções que entram:** as do Brasil (o exterior fica fora, como na 2.1), instaladas nos dois turnos, com aptos nos dois. **Seções agregadas:** entram dentro da seção que as recebeu, como o TSE publica (a agregação foi a mesma nos dois turnos, pela estrutura acima). **Aptos que mudam entre os turnos** (nota N22): ficam como o TSE informa; E1 é o peso e o divisor, como no município (nota N05).
6. **Critério de precisão:** o mesmo da 4.2, com a ordem do T32 (m1): (1) pelo menos 30 municípios no lugar (o número de grupos do erro; ficam fora, de novo, Acre, Amapá, Roraima e Distrito Federal); (2) estimativa entre 0% e 100%, e, se uma fonte sai, todas as fontes do lugar ganham o aviso "o modelo não descreve bem este lugar"; (3) meia largura do intervalo de até 10 pontos. Motivo de "variação pequena": o desvio padrão da fonte entre as seções do lugar, depois de tirar a média de cada município (ponderado por E1), é menor que a metade do mesmo desvio no Brasil. A leitura "a maior parte foi para X" só com o intervalo inteiro acima de 50% para X.
7. **Conferências** (não mudam a leitura; o ticket diz em quantas versões ela se mantém): (a) sem o efeito de município (o modelo da 4.1, sem intercepto, nas seções); (b) sem as seções em que os aptos mudam mais de 5 eleitores entre os turnos; (c) sem as seções que receberam agregadas; (d) sem peso; (e) no Brasil e nas regiões, municípios inteiros reamostrados dentro de cada estado.
8. **"Confirma" ou "muda".** Para cada lugar e cada fonte, a leitura é uma de quatro: "não deu" (com o motivo), "maior parte para o Lula", "maior parte para o Flávio" ou "sem lado claro". A leitura por seção é comparada com a de municípios (`dados/inferencia.json`, como está) e cada par fica numa de quatro classes: **igual**; **ganha** (não deu por município, deu por seção); **perde** (deu por município, não deu por seção); **muda de lado** (as duas deram, com leituras diferentes). O que decide é o comparecimento (fonte C), nos 33 lugares, que é o que o capítulo 4 mostra:
   - **a conta por seção confirma** a atual se os 33 lugares ficam "igual";
   - **confirma e acrescenta** se nenhum lugar "perde" nem "muda de lado" e algum "ganha";
   - **muda** se algum lugar "perde" ou "muda de lado".
   Onde as duas contas dão lados opostos (uma "Lula", a outra "Flávio"), o lugar vai para "não deu", com o motivo "depende da comparação (municípios ou seções)": duas contas razoáveis que discordam no lado não sustentam nenhum dos dois. As fontes O e R recebem a mesma comparação, que vale para o Explorar. Também saem, para cada lugar, se a estimativa por seção cai dentro do intervalo da de municípios e a razão entre as duas meias larguras.
9. **Brasil, votos dos outros (capítulo 3):** a parte dos votos dos outros por seção entra como **quarta especificação** ao lado das três do T32 (M1). O capítulo 3 já diz que essa divisão depende do modelo; o texto dele não muda sem o autor.
10. **Página:** nada muda antes de o autor ver o resultado. Manchete e achados do Resumo não mudam sem ele (regra 13).

## 5. Cortes e regras de dados

### 5.1 Piso dos rankings
- **Rankings em pontos percentuais** (Δs, Δa e captura, se houver): só municípios com **mais de 10.000 eleitores no 1º turno**, as faixas de porte 3 a 5 do T03. A especificação diz "piso de 10 mil eleitores"; fica escrito como "mais de 10 mil", igual às faixas (nota N08).
- Os municípios das faixas 1 e 2 (até 10.000) aparecem em rankings separados por faixa, com o funil ao lado.
- **Rankings em votos** (ΔL, ΔF, ΔM e peso na virada): sem piso, porque o número de votos já acompanha o tamanho.
- O exterior fica fora dos rankings de municípios e aparece numa lista própria.
- Valor vazio (nota N09) não entra no ranking daquele indicador.

### 5.2 Faixas de porte
As do T03, sem mudança (nota N08).

### 5.3 Corte "campo da esquerda"
O do T05, sem mudança: posição até 4,49 na rodada de 2022 (nota N10). Escala contínua como robustez e rodada de 2018 como conferência.

### 5.4 Votos sub judice e anulados (nota N02)
- **Regra principal, igual para todos os partidos e candidatos:** os votos sub judice ficam **fora dos votos válidos**, como no resultado oficial do TSE (colunas sem `_com_sj` do T05).
- **Nenhum município sai da conta principal** por ter muito voto sub judice.
- **Duas conferências** (H5, itens 6 e 7): (a) com os votos sub judice somados aos válidos e aos partidos deles; (b) sem os municípios em que os votos sub judice passam de 5% de (válidos + sub judice) no cargo. Os 5% são o mesmo limite usado para medir o peso no T04 (nota N02).
- **Presidente:** não há voto sub judice nem anulado depois da eleição; as contas de presidente usam o resultado oficial como está.
- **Governador** (votos anulados no RJ, nota N03): não entra em nenhuma conta do T06.
- Se o TSE julgar os recursos antes da publicação, as contas são refeitas com os arquivos novos, e a nota N02 muda.

### 5.5 Partido Missão
Regra A nas contas principais e regra B como conferência (seção 3, H5; nota N11).

### 5.6 Senador
Dois votos por eleitor (nota N01); só a comparação dentro do estado; ficam fora os estados com menos de 5% de votos de senador no campo da esquerda (seção 3, H5).

### 5.7 Exterior
Fora das regressões, do funil, da regressão ecológica e dos rankings de municípios; dentro das contagens e do total do Brasil (seção 2.1; nota N06).

## 6. Dados sociais (só se o T26 entrar; decisão P11)

**Lista curta provisória**, para o T26 confirmar que o dado existe por município. O T26 só pode trocar uma variável se ela não existir, com nota datada aqui, antes de qualquer cruzamento.

| # | Variável | Fonte e ano |
|---|---|---|
| 1 | % da população com 60 anos ou mais | IBGE, Censo 2022 |
| 2 | Taxa de alfabetização, 15 anos ou mais | IBGE, Censo 2022 |
| 3 | % de moradores com rendimento domiciliar per capita de até 1/2 salário mínimo, incluindo os sem rendimento (trocada em 26/10/2026, 23:41, antes de qualquer cruzamento; era "% da população em famílias do CadÚnico em situação de pobreza", MDS, 2026; ver "Mudanças depois da aprovação") | IBGE, Censo 2022 (rendimento, amostra) |
| 4 | PIB por habitante (em logaritmo) | IBGE, PIB dos Municípios, 2023 |
| 5 | Densidade demográfica (em logaritmo) | IBGE, Censo 2022 |
| 6 | % de evangélicos | IBGE, Censo 2022 (religiões) |
| 7 | % de pretos e pardos | IBGE, Censo 2022 |

- **Direção:** nenhuma prevista. Todas são testadas nos dois sentidos (teste bilateral), para que o tema (religião, pobreza, cor ou raça) não leve a uma expectativa sobre um candidato.
- **Desfechos:** Δs, ΔL ÷ E1, ΔF ÷ E1, captura e Δa. A captura só entra nos municípios com mais de 10.000 eleitores e ΔL + ΔF > 0 (nota N09).
- **Teste:** uma variável por vez, com a mesma regressão da seção 2, dentro dos estados (principal) e Brasil.
- **Muitas comparações:** 7 variáveis × 5 desfechos = 35 testes. Só se diz que há associação quando o valor-p corrigido pelo método de Holm fica abaixo de 0,05 na versão dentro dos estados. O resto sai como "sem associação clara".
- **Fora da lista:** tudo é exploratório, com o aviso de que alguma associação pode surgir por acaso (especificação, seção 5). Isso inclui a fatia do Lula em 2022 e o 2º turno para governador de 2026, que é comum a todo o estado e já sai na comparação dentro dos estados.
- Sempre "municípios com…", nunca "pessoas que…", e o mesmo gráfico para os dois candidatos (especificação 6.1).

## 7. Saídas do T06
- `dados/inferencia.json`: cada estimativa com o intervalo, o número de municípios, o método, a versão (principal ou conferência) e a classificação.
- Um script em `scripts/`, rodado com `python -I`, que refaz tudo a partir de `dados/analise_municipios.csv` e `dados/esquerda_1t_municipios.csv`.
- No ticket T06: a tabela de resultados e uma frase simples por resultado, com o limite de interpretação, para o autor revisar.

## 8. Fase exploratória (regras fixadas em 26/10/2026, 22:10, antes de qualquer conta nova; D46)

Depois do parecer estatístico (`parecer/PARECER-2026-10-26.md`), o autor abriu uma fase para procurar o que os dados contam e o estudo ainda não conta (T33). Tudo o que nascer nela foi pensado depois de ver os resultados das seções 3 e 4, e por isso é **exploratório**. As regras abaixo valem para toda conta nova dessa fase.
- **Registro antes da conta:** cada pergunta entra nesta seção, com data e hora, antes de rodar: a pergunta, o teste, as versões de conferência, o que contaria como achado e o que já foi visto sobre ela.
- **Tudo o que for registrado sai**, com o resultado, mesmo sem achado.
- **No máximo 5 perguntas** por rodada, escolhidas com o autor antes das contas.
- **Na página**, sempre com o rótulo "exploratório, não registrado antes das contas", junto do resultado.
- **Resumo:** só entra achado exploratório que seja contagem, ou estimativa que se mantém em todas as versões razoáveis, com o rótulo no próprio achado. **Nunca na manchete.**
- Valem as regras gerais da seção 2 (peso, erro, linguagem, teste da troca) e a mesma régua para os dois candidatos.

### Perguntas registradas

#### Rodada 1 (T33; registrada em 27/10/2026, 10:40, sessão t33-exploracao, antes de qualquer conta)
O autor escolheu as 5 perguntas às 10:37, na conversa da sessão (a sessão recomendou rodar quatro e deixar a E5 de fora, pelo risco da regressão à média; o autor quis as cinco). Valem para todas:
- **Script e saídas:** `scripts/exploracao.py`, rodado com `python -I`, grava `dados/exploracao.json`; relatório em `docs/analise/exploracao/EXPLORACAO-2026-10-27.md`. Semente **20261026**. Dados: `dados/secoes_presidente.csv.gz` (T27), `dados/analise_municipios.csv` (T03), `dados/tse_6259_uf/` (T01) e, na E3, o funil do `dados/inferencia.json`. Nada novo é baixado.
- **Seções:** as mesmas da regra por seção (4.5): as 497.897 do Brasil, instaladas e com aptos nos dois turnos, com as agregadas dentro da que as recebeu e os votos do 28 fora dos válidos (N21). E1 = aptos do 1º turno é o peso e o divisor.
- **Bootstrap:** 1.000 repetições, intervalo de percentis 2,5 e 97,5; no Brasil e nas regiões, estados inteiros reamostrados; nos estados, municípios inteiros (como no T35).
- **Várias perguntas:** não há correção entre as cinco, porque cada uma responde a uma pergunta diferente; a página diz que foram registradas cinco e que, entre várias perguntas feitas depois de ver os dados, alguma pode dar por acaso. Dentro de cada pergunta, o que se corrige está escrito nela.
- **Página:** as cinco saem juntas, num lugar só, cada uma com o resultado (achado ou não) e o rótulo "exploratório, não registrado antes das contas"; o capítulo de cada assunto ganha só um link para lá. Nada muda no Resumo nem nas respostas curtas sem o autor; manchete, nunca.
- **Linguagem:** "municípios onde…", "seções onde…", nunca "eleitores que…"; sem causas; mesma régua e mesmo gráfico para os dois candidatos.

**E1. Para onde foram, em saldo, os votos de cada um dos outros candidatos?**
- **Já visto:** os votos de cada candidato no 1º turno (totais com o exterior: Avante, 70, 3.448.569; Missão, 14, 2.675.887; PSD, 55, 2.605.148; os outros sete, juntos, 587.143); a divisão dos outros juntos pela conta por seção (T35: Brasil 49,9% para o Lula, sem lado claro; Norte e Nordeste para o Lula, Centro-Oeste e Sul para o Flávio, Sudeste sem lado claro). Nenhuma conta por candidato.
- **Conta:** a da regra por seção (4.5), com o efeito de município, trocando a fonte "outros" por quatro: V70, V14, V55 e "resto" (30, 80, 16, 27, 21, 35 e 29): ΔL ÷ E1 = α_município + Σ b_k × V_k ÷ E1 + b_C × ΔC ÷ E1 + b_R × R ÷ E1, peso E1, e a mesma conta para ΔF; as partes dos dois somam 100% em cada fonte. **Lugares:** Brasil e as 5 regiões.
- **Critério e leitura:** os da 4.2 com a ordem do T32 (estimativa entre 0% e 100%; meia largura de até 10 pontos); "a maior parte foi para X" só com o intervalo inteiro acima de 50% para X; senão, "sem lado claro". Conferência de código: somando as quatro fontes numa só, a conta tem de reproduzir o T35.
- **Conferências:** (a) sem peso; (b) no Brasil e nas regiões, municípios inteiros reamostrados dentro de cada estado; (c) sem as seções que receberam agregadas; (d) sem as seções em que os aptos mudam mais de 5 eleitores entre os turnos.
- **Conta como achado:** um candidato com "maior parte para X" no Brasil que se mantém nas quatro conferências; e, em especial, dois candidatos com lados opostos no Brasil, os dois mantidos. O resto sai como "sem lado claro" ou "não deu", com o motivo.

**E2. Em quantos municípios um passou o outro do 1º para o 2º turno?**
- **Já visto:** a variação da fatia por estado (tabela do T03) e por município nas figuras e nas regressões (capítulo 1, funil, Explorar), sem que ninguém contasse as trocas de lado. A manchete ("Lula cresceu nos 27 estados") é contagem por estado.
- **Conta (contagem, sem estimativa):** nos 5.571 municípios do Brasil, quem teve mais votos entre os dois no 1º turno e no 2º: Lula → Lula, Flávio → Flávio, Flávio → Lula, Lula → Flávio, e os empates à parte. Também: em quantos municípios a fatia do Lula subiu, caiu ou ficou igual (Δs > 0, < 0, = 0), e quantos eleitores do 1º turno moram nos municípios de cada casa. Por estado e no Brasil. O exterior (186) sai à parte.
- **Conferências:** (a) vencedor do 1º turno entre todos os candidatos (se algum outro candidato ganhou em algum município, ele aparece); (b) a mesma contagem por seção; (c) com o exterior.
- **Conta como achado:** é contagem: o número sai como é. É a única das cinco que, pela regra desta seção, pode ir ao Resumo, com o rótulo no próprio achado, se o autor quiser.

**E3. A abstenção mudou de outro jeito nos estados com 2º turno para governador?**
- **Grupo:** os 6 estados em que o governador foi para o 2º turno, pela situação dos candidatos no resultado do 1º turno (eleição 6259, `dados/tse_6259_uf/*-c0003-*`): AC, AM, DF, ES, RN e TO. A especificação (6.1) previa esse controle; nunca foi testado.
- **Já visto:** a tabela da abstenção por estado nos dois turnos (T03) e, na página, os estados em que a abstenção subiu (capítulo 4); o funil da abstenção, com a cauda de cima longa (T32, M3). A direção pode ser adivinhada da tabela; por isso a pergunta é exploratória.
- **Conta:** Δa = a + b × (estado com 2º turno de governador), nos municípios do Brasil, peso E1. Desfecho principal: Δa (p.p.); segundo desfecho: Δs (p.p.). **Valor-p por permutação exata:** as 296.010 maneiras de escolher 6 dos 27 estados, com b recalculado em cada uma; bilateral. Holm sobre os dois desfechos.
- **Conferências:** (a) sem peso; (b) sem o DF (um município só); (c) com efeito fixo de região (a permutação continua entre os 27 estados); (d) erro agrupado por estado e bootstrap selvagem (pesos de Webb, 9.999), com o aviso de que, com 6 estados tratados, ele não é confiável (MacKinnon e Webb, 2017). E, descritivo: dos municípios acima da faixa de 99,8% no funil da abstenção, quantos ficam nos 6 estados, contra o que se esperaria pelo número de municípios deles.
- **Conta como achado:** p da permutação, corrigido por Holm, abaixo de 0,05, com o mesmo sinal nas conferências (a) a (c); abaixo de 0,5 p.p. de diferença, "pequena".

**E4. O comparecimento subiu mais nas seções onde o Lula era mais forte ou onde o Flávio era mais forte?**
- **Já visto:** a H4 (por município, a fatia do Lula contra a variação da abstenção: inconclusiva); a parte do saldo do comparecimento para cada um pela conta por seção (T35: 59% para o Lula no Brasil); o funil da abstenção. Nenhuma conta da abstenção contra a força de cada um.
- **Conta:** Δa da seção (p.p., cada turno com os próprios aptos) = α_município + β × s1 da seção (fatia do Lula entre os dois no 1º turno), peso E1, seções com votos para os dois no 1º turno. β por 10 pontos de s1. Para o Flávio, a variável é 100 − s1 e β troca de sinal: é a mesma reta, lida dos dois lados. **Lugares:** Brasil, as 5 regiões e os estados com pelo menos 30 municípios. Tamanho: o efeito interquartil da 2.6 (quartis ponderados, depois de tirar a média de cada município).
- **Conferências:** (a) sem peso; (b) sem as seções que receberam agregadas; (c) sem as seções em que os aptos mudam mais de 5; (d) com a fatia do Lula entre todos os votos válidos do 1º turno no lugar de s1; (e) erro agrupado por estado (CR1) no Brasil. Sai também, como contexto e não como conferência, a mesma conta sem o efeito de município (que compara cidades, outra pergunta).
- **Conta como achado:** no Brasil, o intervalo de 95% inteiro de um lado de zero, com o mesmo sinal em (a) a (e); abaixo de 0,5 p.p. de efeito interquartil, "pequena".

**E5. Cada um cresceu mais onde era mais fraco também comparando seções da mesma cidade?**
- **Já visto:** a H1 por município (dentro dos estados, −0,51 ponto por 10) e a referência da divisão igual (M4: −0,92 esperado). Nenhuma conta por seção.
- **O problema:** numa seção de 300 eleitores, o acaso pesa na fatia do 1º turno, e o acaso sozinho já faz a fatia cair onde saiu alta e subir onde saiu baixa (regressão à média). Por isso a conta principal é corrigida.
- **Conta:** Δs da seção = α_município + β × s1, peso E1, seções com votos para os dois nos dois turnos; β por 10 pontos. **Principal, corrigida:** β somado à parte que o acaso explica, var(e) ÷ var(s1), com var(e) a variância binomial média da fatia do 1º turno, s1(1 − s1) ÷ (L1 + F1), e var(s1) a variância de s1 depois de tirar a média de cada município (as duas ponderadas por E1). Intervalo: bootstrap de estados inteiros, refazendo a correção em cada repetição. Para o Flávio, a mesma reta lida do outro lado (β é o mesmo).
- **Conferências:** (a) sem a correção (a conta bruta, que exagera a queda); (b) a referência da divisão igual da M4, na seção: a mesma regressão aplicada ao Δs que a divisão igual daria (captura do Brasil, 73,67%), e a diferença observada − esperada; (c) só seções com pelo menos 200 votos nos dois no 1º turno; (d) sem peso; (e) sem as seções que receberam agregadas.
- **Conta como achado:** o β corrigido com o intervalo inteiro abaixo de zero (ou acima) e o mesmo sinal em (b) a (e); a conta bruta não decide. A página compara com a H1 por município.

#### Rodada 2 (T37; registrada em 28/10/2026, 13:40, sessão t37-perfil-idade, antes de qualquer conta de idade)
O autor perguntou se os idosos, em sua maioria, votaram ou faltaram, e o que mudou no 2º turno (D87). Escolheu I1 a I4 e a I5b às 13:3x, na conversa da sessão (a sessão recomendou as cinco; a I5 original, por município, ficou de fora, trocada pela I5b, por seção). Valem para todas:
- **Script e saídas:** `scripts/perfil_idade.py`, rodado com `python -I`, grava `dados/perfil_idade.json`; relatório em `docs/analise/exploracao/PERFIL-IDADE-2026-10-28.md`. Semente **20261026**.
- **Dados:** I1 a I4, `dados/perfil_idade.csv.gz` (soma do perfil de comparecimento e abstenção do TSE, extração de 13/10/2026, **só o 1º turno**: o TSE não publicou o 2º, nem nos dados abertos nem no painel de estatísticas, consultados em 28/10), por `scripts/perfil_idade_base.py`. I5b, o perfil do eleitorado por seção do TSE (cadastro fechado; gerado em 14/07/2026), em `dados/tse_perfil_eleitor_secao/`, e as seções do T27 (`dados/secoes_presidente.csv.gz`).
- **Já conferido antes do registro (só totais):** perfil × T03 no Brasil, 1º turno: aptos 158.745.463 × 158.745.502, comparecimento 125.277.230 × 125.275.835; nenhuma taxa por idade calculada. Por município, a diferença (320.025 aptos em módulo) cabe nos 595.156 eleitores em transferência temporária (trânsito), que o perfil conta na cidade de origem. Por isso, I1 a I4 saem no Brasil, nas regiões e nos estados, e nunca por município.
- **Já visto:** as reportagens de 17/10/2026 com o 1º turno por idade (dados do TSE reunidos pelo Movimento Voto 70+; Agência Brasil e Times Brasil): comparecimento de 68,77% entre 70 e 74 anos, 52,23% entre 75 e 79, 37,12% entre 80 e 84, 24,30% entre 85 e 89, 13,46% entre 90 e 94 e 4,34% entre 95 e 99; abstenção dos 70 ou mais 49,1% (58,8% em 2022); e o painel do TSE (voto facultativo: 56,15% de comparecimento; obrigatório: 82,62%). No estudo: capítulo 8 (Censo, por município: onde há mais gente de 60 ou mais, a fatia do Lula variou um pouco menos, −0,27 ponto entre quartis, e a abstenção sem diferença clara) e a E4 (seções da mesma cidade: a abstenção caiu um pouco mais onde o Lula era mais forte). O reel do Radar do Voto que o autor viu pergunta "jovem ou idoso?" no 2º turno; o resultado dele não foi visto.
- **Aviso em todas:** o cadastro ainda tem eleitores que morreram e não foram tirados, mais comuns nas faixas de cima; a abstenção medida nelas é maior que a real, e isso não se corrige aqui.
- **Linguagem:** I1 a I4 são contagens de pessoas, agregadas: "dos eleitores de 70 anos ou mais, X% votaram" pode ser dito; em quem votaram, nunca. Na I5b, "seções com mais inscritos de 60 anos ou mais…", nunca "os idosos…"; mesma reta, lida dos dois lados, para os dois candidatos.
- **Página:** as cinco saem juntas, com o resultado de todas e o rótulo "exploratório, não registrado antes das contas"; onde entra, com o autor depois do relatório. Manchete, nunca; Resumo, só contagem, com o rótulo, se o autor quiser.

**I1. Os eleitores de cada idade, em sua maioria, votaram ou faltaram no 1º turno?**
- **Conta (contagem):** taxa de comparecimento = comparecimento ÷ aptos do perfil, nas faixas do TSE (16, 17, 18, 19, 20, 21–24… 95–99, 100 ou mais; "inválido" à parte) e em cinco grupos: 16 e 17 (facultativo), 18 a 59, 60 a 69, 70 ou mais (facultativo) e 60 ou mais. No Brasil (sem o exterior), no exterior à parte, nas 5 regiões e nos 27 estados. "A maioria votou" se a taxa passa de 50%.
- **Conferências:** soma das faixas = total do perfil em cada lugar; nos 16, 17 e 70 ou mais, comparecimento = coluna de voto facultativo, e nos 18 a 69, = obrigatório; o total do perfil contra o T03 por estado (diferença dita).
- **Conta como achado:** é contagem; sai como é.

**I2. Entre os de 70 anos ou mais, a partir de que idade a maioria faltou?**
- **Conta (contagem):** a taxa da I1 em 70–74, 75–79… 100 ou mais, no Brasil e nas regiões; a primeira faixa abaixo de 50%. Nos estados, a faixa em que cada um cruza 50%.
- **Conta como achado:** contagem; sai como é.

**I3. De quem é a abstenção do 1º turno?**
- **Conta (contagem):** dos que faltaram, a parte com 60 ou mais e com 70 ou mais, contra a parte deles entre os aptos (e a razão entre as duas); o mesmo para 16 e 17 e para 18 a 59. Brasil e regiões.
- **Conta como achado:** contagem; sai como é.

**I4. Entre os de 60 anos ou mais, mulheres e homens votaram na mesma proporção?**
- **Conta (contagem):** a taxa da I1 em 60–69, 70 ou mais e nas faixas de 70–74 a 100 ou mais, separando mulheres e homens (gênero do cadastro; "não informado" à parte, se houver); 18 a 59 como referência. Brasil e regiões.
- **Conta como achado:** contagem; sai como é.

**I5b. Nas seções com mais inscritos de 60 anos ou mais, a abstenção e a fatia do Lula mudaram diferente do 1º para o 2º turno, comparando seções da mesma cidade?**
- **Variável:** p60 = inscritos de 60 anos ou mais ÷ inscritos da seção, no perfil do eleitorado por seção (faixa "inválido" fora do numerador e dentro do denominador), em pontos percentuais. Casada às seções do T27 por UF, município, zona e seção. Seções: as da regra por seção (4.5), as 497.897 do Brasil, com perfil; as sem perfil saem e são contadas.
- **Conta:** dois desfechos por seção: Δa (p.p., cada turno com os próprios aptos, como na E4) e Δs (p.p., fatia do Lula entre os dois, como na E5, seções com votos para os dois nos dois turnos). Δ = α_município + β × p60, peso E1. β por 10 pontos de p60. Lugares: Brasil e as 5 regiões. Intervalo: bootstrap de estados inteiros, 1.000 repetições, percentis; com dois desfechos, o intervalo é de **97,5%** (percentis 1,25 e 98,75; Bonferroni). Tamanho: efeito interquartil (quartis ponderados de p60 depois de tirar a média de cada município). Para o Flávio, Δs troca de sinal: a mesma reta, lida dos dois lados.
- **Conferências:** (a) sem peso; (b) sem as seções que receberam agregadas; (c) sem as seções em que os aptos mudam mais de 5 entre os turnos; (d) p70 (70 ou mais, voto facultativo) no lugar de p60; (e) erro agrupado por estado (CR1) no Brasil; (f) sem as seções em que os inscritos do perfil e os aptos do 1º turno diferem mais de 5%. Saem também, como contexto e não como conferência: a mesma conta sem o efeito de município; e com a fatia do Lula no 1º turno (s1) junto de p60, para ver se a ligação com a idade é a mesma que a da força de cada um (E4).
- **Conta como achado:** em cada desfecho, no Brasil, o intervalo de 97,5% inteiro de um lado de zero, com o mesmo sinal e o intervalo do mesmo lado em (a) a (f); abaixo de 0,5 p.p. de efeito interquartil, "pequena". Comparação com o capítulo 8 (município, Censo) e com a E4, sem decidir nada.

## Referências do método
- Cameron, A. C.; Gelbach, J. B.; Miller, D. L. (2008). Bootstrap-based improvements for inference with clustered errors. *Review of Economics and Statistics*, 90(3), 414–427.
- Duncan, O. D.; Davis, B. (1953). An alternative to ecological correlation. *American Sociological Review*, 18(6), 665–666.
- Goodman, L. A. (1953). Ecological regressions and behavior of individuals. *American Sociological Review*, 18(6), 663–664.
- Spiegelhalter, D. J. (2005). Funnel plots for comparing institutional performance. *Statistics in Medicine*, 24(8), 1185–1202; e Handling over-dispersion of performance indicators. *Quality and Safety in Health Care*, 14(5), 347–351.
- Webb, M. D. (2023). Reworking wild bootstrap-based inference for clustered errors. *Canadian Journal of Economics*, 56(3), 839–858.
- Holm, S. (1979). A simple sequentially rejective multiple test procedure. *Scandinavian Journal of Statistics*, 6(2), 65–70.

Acrescentadas no T32 (referências propostas pelo parecer estatístico e aprovadas pelo autor em 26/10/2026, 22:26; lista com DOI em `parecer/REFERENCIAS-PROPOSTAS.md`): Robinson (1950); Goodman (1959); King (1997); Freedman, Klein, Sacks, Smyth e Everett (1991); Romero, Pavía, Martín e Romero (2020); Plescia e De Sio (2018); MacKinnon e Webb (2017); MacKinnon, Nielsen e Webb (2023); Carter, Schnepel e Steigerwald (2017); Cameron e Miller (2015); Bester, Conley e Hansen (2011); Solon, Haider e Wooldridge (2015); Spiegelhalter, Sherlaw-Johnson, Bardsley, Blunt, Wood e Grigg (2012); Xia, He, Li e Kalbfleisch (2022); Nosek, Ebersole, DeHaven e Mellor (2018); Rubin (2021); Barnett, van der Pols e Dobson (2005); Zucco e Power (2024). DOIs de Goodman (1953), 10.2307/2088121, e de Duncan e Davis (1953), 10.2307/2088122.

## Mudanças depois da aprovação

- **26/10/2026, 13:03 · critério de precisão também para o Brasil (decisão P17 do autor, na sessão t06-inferencia).** A seção 4.2 escreveu o critério de precisão para região e estado. Depois da primeira rodada, o resultado do Brasil na regressão ecológica mostrou a parte dos brancos e nulos fora de 0% a 100% (156% para o Lula e −56% para o Flávio). O autor decidiu aplicar ao Brasil o mesmo critério, sem mudar nenhuma das três regras: a parte dos outros candidatos e a do comparecimento passam, e a dos brancos e nulos vai para a lista "Estimativas que não deram", com o motivo "estimativa fora de 0% a 100%". A mudança foi decidida depois de ver o resultado e só tira uma estimativa da página; não muda nenhuma conta nem nenhuma classificação de hipótese.
- **26/10/2026, 22:10 · regras da fase exploratória (decisão do autor, na sessão do parecer estatístico; D46).** Nova seção 8, que não muda nenhuma regra das seções 2 a 7. As correções do parecer (T32) entram aqui, cada uma com a própria nota datada, quando forem feitas.
- **26/10/2026, 22:31 · correções do parecer estatístico (T32; decisão do autor de aplicar todas, 22:10, D46).** Todas vieram **depois de ver os resultados** e o parecer (`parecer/PARECER-2026-10-26.md`), e por isso estão declaradas aqui, uma por uma. **Nenhuma classificação de hipótese muda.** As contas estão no `scripts/inferencia.py`; os scripts do parecer serviram de ponto de partida e de conferência.
  - **M5 · intervalo do bootstrap selvagem (2.4 e 2.6).** Cada versão de cada teste ganha também o intervalo de 95% do próprio bootstrap selvagem, por inversão do teste (os valores do coeficiente que o teste com a nula imposta não rejeita a 5%; os mesmos sorteios em todo valor). A regra de classificação não muda: como o intervalo por inversão exclui zero quando o valor-p fica abaixo de 0,05, "confirmada" é o mesmo que "os dois intervalos, o do erro agrupado e o do bootstrap, ficam inteiros do lado previsto". Muda o intervalo **mostrado**: os gráficos de floresta e as respostas curtas mostram o do bootstrap, e as tabelas, os dois. Motivo: com peso pelo eleitorado, o peso se concentra em poucos estados (São Paulo tem 21,6%; os oito maiores, 67%), e o número efetivo de grupos (Carter, Schnepel e Steigerwald, 2017) fica entre 1,3 e 16 nas três hipóteses, longe de 26; o intervalo do erro agrupado com t(25) tende a sair estreito. Na H3, ele excluía zero (de +0,06 a +2,82 por 10) com a hipótese inconclusiva; o do bootstrap vai de −0,13 a +3,04 e conta a mesma história da classificação. Também saem, como conferência, o número efetivo de grupos e as contas tirando um estado por vez: a H1 se mantém sem qualquer estado (de −0,54 a −0,49 por 10); a H3 fica confirmada sem São Paulo (+2,09, p = 0,0007) e mais fraca sem a Bahia ou sem Minas (p de 0,13 e 0,14); a H4 não muda. Os complementos (votos por eleitor) também ganham o intervalo do bootstrap, para a página usar o mesmo intervalo em todo lugar.
  - **M4 · H1 contra a divisão igual (seção 3), exploratória.** A mesma regressão da H1 aplicada ao Δs que o modelo simples da seção 3 daria em cada município, com o saldo S = ΔL + ΔF dividido na proporção do Brasil (captura sem o exterior, 73,67%): Δs do modelo = 100 × (L1 + 0,7367 × S) ÷ (L1 + F1 + S) − s1. Dentro dos estados, a inclinação esperada é −0,92 por 10 (−1,05 a −0,80); a observada, −0,51; a diferença, +0,41 (bootstrap: +0,24 a +0,53). A fatia caiu cerca de metade do que a divisão igual daria. Não muda a classificação da H1 (o teste registrado é contra zero); sai na página com o rótulo de exploratória e com a ressalva sobre regressão à média (Barnett, van der Pols e Dobson, 2005).
  - **M2 · intervalo da regressão ecológica (4.1 e 4.2).** No Brasil e nas regiões, o intervalo principal passa a reamostrar **estados inteiros** (a conferência (b) da 4.1), coerente com o erro agrupado por estado da 2.4; sortear municípios dentro de cada estado vira conferência. Nos estados, continua o sorteio de municípios do estado (com um estado só, não há grupos para reamostrar), e a página diz que esse intervalo supõe municípios independentes dentro do estado e por isso tende a sair estreito. Reamostrar por microrregião do IBGE ficou de fora: pediria baixar a tabela de microrregiões, e o autor não pediu. Consequência pelo critério da 4.2: a parte do comparecimento no Brasil (57% para o Lula, de 44% a 68%) passa a "não deu" (resultados muito dispersos); nas regiões, passam só os votos dos outros no Norte, no Nordeste e no Sul (no Sul, sem lado claro) e o comparecimento no Nordeste. Estimativas que não deram: 62 de 99 (eram 55).
  - **m1 · critério de precisão (4.2).** "Fora de 0% a 100%" deixa de ser a última regra e passa a vir antes da meia largura: é sinal de que o modelo não descreve o lugar, não falta de precisão. Quando uma fonte do lugar sai de 0% a 100%, **todas as fontes daquele lugar** ganham um aviso ("o modelo não descreve bem este lugar"), inclusive as que passam no critério, porque a premissa da divisão igual vale para o modelo inteiro. Em 22 dos 29 lugares com pelo menos 30 municípios, alguma fonte sai de 0% a 100% (quase sempre a dos brancos e nulos).
  - **M1 · matriz de transição (4.1), conferência.** A regressão de Goodman em níveis, como na literatura de fluxos entre eleições (Goodman, 1953 e 1959; Romero et al., 2020): as cinco categorias do 1º turno (Lula, Flávio, outros, brancos e nulos, abstenção) explicam as quatro do 2º (Lula, Flávio, brancos e nulos, abstenção), tudo dividido por E1, peso E1, sem intercepto; intervalo por estados inteiros. Dos votos dos outros que foram para um dos dois, 49,7% para o Lula (44,5% a 59,9%); 7 das 20 células ficam fora de 0% a 100%. Com a versão principal (61,3%) e a com intercepto (45,5%), são três especificações razoáveis, dos dois lados de 50%: a divisão dos votos dos outros **depende do modelo**, e a página passa a dizer isso no lugar do "61 de cada 100", no capítulo 3 e no Resumo. O achado do Resumo que entra no lugar segue a seção 8: é contagem (a captura).
  - **m3 · limites de Duncan e Davis (4.5).** A razão dada estava errada: os limites pedem casas não negativas na tabela de cada área, não "contagens que só crescem". Na formulação em níveis, eles passam a ser possíveis e foram calculados para a parte dos votos dos outros que foi para o Lula: dão de 0% a 100% nos 5.571 municípios, isto é, não informam nada (as outras categorias do 1º turno, juntas, sempre poderiam explicar os votos do Lula no 2º).
  - **M3 · funil (4.3).** τ² passa a ser estimado **sem winsorizar** as distâncias padronizadas (o método dos momentos da 4.3, com todos os municípios). Motivo: o erro do acaso é minúsculo nos municípios médios e grandes, e os maiores z são os deles; cortar 10% de cada ponta tirava a informação que mede τ², e a faixa marcava como fora três vezes mais municípios do que o modelo promete, sobretudo os grandes. Conferência por faixa de porte, que fica na página: na variação da fatia, ficam fora da faixa de 95% 5,1% dos municípios (de 1,4% a 8,2% por porte; eram 16,3%, de 3% a 36%), e fora da de 99,8%, 12 municípios (eram 180). Na abstenção, 8,3% ficam fora da faixa de 95% (eram 22,9%), mas 438 dos 462 estão acima: a distribuição tem a cauda de cima longa, e a faixa simétrica não serve para ela; a página diz isso no gráfico. Fora da de 99,8%, 153 (eram 601). A versão winsorizada fica no `inferencia.json` como conferência. Se o artigo de Spiegelhalter (2005) pede um fator de correção do φ winsorizado não foi confirmado (os textos integrais não abriram; a documentação do pacote FunnelPlotR confirma só os 10% em cada ponta); com a winsorização fora da conta principal, a pergunta deixa de pesar.
  - **m2 · graus de liberdade (2.4).** O texto dizia "26 graus de liberdade"; a versão principal tem 26 grupos e usa 25 (G − 1), como o script sempre fez. Corrigido no próprio texto da 2.4, com a marca da data.
- **26/10/2026, 23:30 · dados sociais (T26): a variável 3 está sem dado; nenhuma variável trocada.** Antes de qualquer cruzamento com a eleição. As variáveis 1, 2 e 4 a 7 existem por município e estão em `dados/dados_sociais_municipios.json` como registradas na seção 6, com estas definições operacionais (só detalham o que a tabela já dizia): % de 60 anos ou mais sobre a população residente; alfabetização como a taxa publicada pelo IBGE para 15 anos ou mais; PIB por habitante de 2023 como publicado pelo IBGE (que divide pela população do Censo 2022); densidade como publicada pelo IBGE (população ÷ área do município); % de evangélicos sobre as **pessoas de 10 anos ou mais**, o universo da pergunta de religião no Censo 2022; % de pretos e pardos sobre a população residente. Boa Esperança do Norte (MT), criado depois do Censo 2022, não tem nenhum dos dados e fica fora dos 35 testes (nota N20): os testes usam 5.570 municípios. **A variável 3** (% da população em famílias do CadÚnico em situação de pobreza, MDS, 2026) existe por município, mas a fonte (VIS DATA / MI Social, em `aplicacoes.mds.gov.br`) está fora do ar desde 21/10/2026, em manutenção, e não há cópia de 2026 em outro lugar. Como a regra só permite trocar uma variável que não exista, a troca é decisão do autor (P26). O arquivo já traz, **fora da lista curta e sem uso até a decisão**, a reserva: % de moradores com rendimento domiciliar per capita de até meio salário mínimo, incluindo os sem rendimento (IBGE, Censo 2022, amostra, tabela 10296). Enquanto a P26 não for decidida, o número de testes continua 35 e a correção de Holm só pode rodar com as 7 variáveis.
- **26/10/2026, 23:41 · variável 3 trocada (decisão do autor na conversa da sessão t26-dados-sociais, P26).** Antes de qualquer cruzamento com a eleição: ninguém abriu os dados sociais junto com os resultados. A pobreza do CadÚnico (MDS, 2026) ficou sem fonte: o MDS está fora do ar desde 21/10/2026, em manutenção de segurança, sem data para voltar. Entra no lugar o **% de moradores com rendimento domiciliar per capita de até 1/2 salário mínimo, incluindo os sem rendimento** (IBGE, Censo 2022, amostra, tabela 10296; universo: moradores em domicílios particulares permanentes ocupados). Motivos, além da falta da fonte: mede a renda da população inteira, sem depender de quanto cada prefeitura cadastra; e o CadÚnico é a porta de entrada do Bolsa Família, programa do governo de um dos candidatos, o que se prestaria a uma leitura enviesada. Custo: o dado é de 2022, o ano das outras variáveis do Censo, e não de 2026. O resto da seção 6 não muda: 7 variáveis, 5 desfechos, 35 testes, Holm, teste bilateral, 5.570 municípios.
- **26/10/2026, 23:56 · dados sociais (T34): como os 35 testes da seção 6 são rodados, escrito antes de rodar.** Ninguém cruzou os dados sociais com a eleição até aqui. Só detalha o que a seção 6 e a 2 já dizem; onde a seção 6 não diz, vale a regra mais próxima da seção 2, escrita aqui antes do resultado.
  - **Quem entra:** os 5.570 municípios com dados (sem Boa Esperança do Norte, N20); na versão dentro dos estados, sai o DF, que tem um município só (como nas hipóteses). **Captura:** só os municípios com mais de 10.000 eleitores no 1º turno e ΔL + ΔF > 0 (N09); estado que ficar com um município só nessa amostra sai da versão dentro dos estados, pela mesma regra.
  - **Conta:** para cada variável e cada desfecho, desfecho = α_UF + β × variável, peso E1, erro agrupado por UF (CR1, t com G − 1 graus de liberdade), valor-p do bootstrap selvagem (9.999 repetições, pesos de Webb, nula imposta) e o intervalo dele por inversão do teste (T32, M5). A versão Brasil é a mesma conta sem o efeito fixo. As variáveis entram como estão no `dados/dados_sociais_municipios.json` (PIB por habitante e densidade em logaritmo natural).
  - **Holm:** sobre os 35 valores-p do bootstrap selvagem da versão dentro dos estados. "Há associação" só quando o p corrigido fica abaixo de 0,05 **e**, como na 2.6 (os dois métodos têm de concordar), o p do erro agrupado corrigido por Holm nos mesmos 35 também fica abaixo de 0,05. O resto é "sem associação clara". A direção é o sinal do coeficiente; não há direção prevista (bilateral). A versão Brasil ganha a mesma correção, só para informar: não muda o resultado.
  - **Tamanho:** o efeito interquartil da 2.6, na unidade de cada desfecho (pontos percentuais para Δs, Δa e captura; pontos do eleitorado do 1º turno para ΔL ÷ E1 e ΔF ÷ E1). A palavra "pequena", abaixo de 0,5 ponto, vale para os cinco desfechos com a mesma régua (a 2.6 só a fixou para Δs). O tamanho muda só a palavra.
  - **Os dois candidatos:** para o Flávio, a variação da fatia é −Δs e a captura é 100 − captura; o coeficiente troca de sinal e o valor-p é o mesmo. ΔL ÷ E1 e ΔF ÷ E1 são dois testes, um para cada um, e saem lado a lado no mesmo gráfico.
- **27/10/2026, 09:34 · regra por seção (T35), escrita antes de qualquer conta com os votos das seções.** Nova subseção "Regra por seção" na 4.5, que detalha o que a 4.5 já previa ("as mesmas regras da 4.2 aplicadas às seções de cada município"): o modelo com efeito de município, o grupo do erro (estados inteiros no Brasil e nas regiões; municípios inteiros nos estados), as seções agregadas e os aptos que mudam (N22), os votos do candidato 28 (N21), as conferências e o que conta como "confirma" ou "muda". Não muda nenhuma regra das seções 2 a 4.4. Foi escrita depois de ver as estimativas por município (publicadas) e só a estrutura das seções (aptos, agregadas, instaladas), sem nenhum voto por seção.
- **27/10/2026, 09:43 · conta por seção como principal da 4.2 (decisão P28 do autor, na sessão t35-contas-por-secao; D59).** Depois de ver o resultado da regra por seção (4.5), que, pela regra 8 dela, **muda** a estimativa do comparecimento, o autor decidiu levá-la à página. A estimativa por lugar da 4.2 (Brasil, regiões e estados, as três fontes) passa a ser a por seção, com efeito de município; a por município fica como conferência, ao lado. O critério de precisão e a leitura não mudam. Onde as duas dão lados opostos (votos dos outros em MT e SP), "não deu", pela regra 8. A 4.1 do Brasil (capítulo 3) continua com as três contas por município e ganha a por seção como quarta. Decidida depois do resultado, mas a regra que a previa (4.5, 09:34) foi escrita antes.
- **27/10/2026, 10:40 · fase exploratória, rodada 1 (T33).** As cinco perguntas escolhidas com o autor (E1 a E5) estão em "Perguntas registradas", na seção 8, escritas antes de qualquer conta. Não muda nenhuma regra das seções 2 a 7.
- **27/10/2026, 19:4x · de onde vieram os votos a mais, no Resumo (recado do autor, D73; sessão sobre-estudo).** Não é hipótese nem estimativa nova: é uma conta de soma com as contagens do TSE. Os votos que os dois ganharam do 1º para o 2º turno = aumento do comparecimento + votos dos outros candidatos no 1º turno + queda de brancos e nulos (Brasil: 2.960.239 + 9.316.747 + 1.821.246 = 14.098.232; `scripts/pagina_dados.py` confere no Brasil, nas regiões e nas UFs). Vale para o saldo, não para pessoas. Como cada parte se dividiu entre os dois continua sendo a estimativa da 4.2, sem mudança. Não muda nenhuma regra nem classificação.
