# Use o estudo com a sua IA

**English:** [ASK-YOUR-AI.md](ASK-YOUR-AI.md)

Três jeitos de usar o estudo **[Análise da virada](https://analise-da-virada.pages.dev/)** com o ChatGPT, o Claude, o Gemini ou outra IA:

1. **Perguntar** (qualquer chat): o texto logo abaixo.
2. **Revisar, como um segundo par de olhos:** a IA confere os números contra as fontes e roda as contas de novo. Seção "Revisar o estudo".
3. **Refazer ou continuar:** a IA refaz as bases e a página a partir das fontes, ou faz uma análise nova com as mesmas regras. Seção "Refazer ou continuar".

Para os jeitos 2 e 3, a IA precisa rodar código: um assistente de programação aberto numa cópia do repositório (Claude Code, Codex, Cursor…) ou um chat que roda Python nos arquivos anexados (a análise de dados do ChatGPT, o Claude com arquivos). O guia completo para ela é o [`AGENTS.md`](AGENTS.md): o mapa do repositório, como os dados passam de um script para outro, como ler cada arquivo e a lista de conferências. Os assistentes de programação o leem sozinhos.

## Perguntar

Copie o texto do quadro abaixo, cole numa conversa nova e escreva a sua pergunta no fim.

**Se a sua IA não abre links** (ela diz que não consegue acessar a internet ou inventa números): baixe os arquivos da tabela "Que arquivo responde a quê" (botão "Download raw file" em cada um, ou "Baixar os dados" na página do estudo), anexe na conversa e cole o mesmo texto. Comece por `municipios.csv`, `estados.csv` e `dicionario.csv`.

**Cuidado:** a IA pode errar uma conta ou ler uma coluna errada. Confira o número que importa no arquivo ou na página do estudo antes de usar.

````text
Você vai responder perguntas sobre o estudo "Análise da virada", de Murilo Neves de Martins (versão 1.0.1, 27/10/2026): o que mudou do 1º para o 2º turno da eleição presidencial de 2026 no Brasil, entre Lula e Flávio Bolsonaro, por estado e município. Página: https://analise-da-virada.pages.dev/ · Dados e scripts: https://github.com/MuriloNM/analise-da-virada

Use só os arquivos do estudo. Leia-os nestes endereços (texto puro):
- Dicionário das colunas: https://raw.githubusercontent.com/MuriloNM/analise-da-virada/main/planilha/pt-BR/dicionario.csv
- Municípios (os dois turnos lado a lado, 5.757 linhas): https://raw.githubusercontent.com/MuriloNM/analise-da-virada/main/planilha/pt-BR/municipios.csv
- Brasil, regiões e estados: https://raw.githubusercontent.com/MuriloNM/analise-da-virada/main/planilha/pt-BR/estados.csv
- Hipóteses testadas: https://raw.githubusercontent.com/MuriloNM/analise-da-virada/main/planilha/pt-BR/hipoteses.csv
- De onde vieram os votos de cada um: https://raw.githubusercontent.com/MuriloNM/analise-da-virada/main/planilha/pt-BR/de_onde_vieram.csv
- Dados sociais dos municípios e os 35 testes: https://raw.githubusercontent.com/MuriloNM/analise-da-virada/main/planilha/pt-BR/dados_sociais.csv e https://raw.githubusercontent.com/MuriloNM/analise-da-virada/main/planilha/pt-BR/testes_sociais.csv
- Partidos e voto no campo da esquerda: https://raw.githubusercontent.com/MuriloNM/analise-da-virada/main/planilha/pt-BR/partidos.csv e https://raw.githubusercontent.com/MuriloNM/analise-da-virada/main/planilha/pt-BR/esquerda_municipios.csv
- A noite da apuração: https://raw.githubusercontent.com/MuriloNM/analise-da-virada/main/planilha/pt-BR/apuracao_ao_vivo.csv
- Regras dos testes, fixadas antes das contas: https://raw.githubusercontent.com/MuriloNM/analise-da-virada/main/docs/analise/HIPOTESES.md

Os CSV usam ponto e vírgula entre os campos e vírgula decimal; as porcentagens já estão multiplicadas por 100; célula vazia é conta sem valor. O código do TSE (cd_tse) tem 5 dígitos e pode começar com zero: leia como texto. As linhas com uf "ZZ" são o exterior.

Para conferir que leu os arquivos inteiros: a soma de lula_2t em municipios.csv é 64.256.232 e a de flavio_2t, 59.826.041. Se não bater, diga que não conseguiu ler o arquivo completo e não responda com números.

Regras da resposta:
1. Os dados são contagens por lugar (município, estado, seção eleitoral), não por pessoa. Nunca diga como um eleitor ou um grupo de pessoas votou ou mudou de voto: diga o que aconteceu no lugar ("nos municípios em que…"). As contas de onde vieram os votos dão o saldo de cada fonte, não o caminho de cada eleitor.
2. Não atribua causas (campanha, debate, aliança, rede social, economia). O estudo diz onde e quanto, não por quê.
3. Trate os dois candidatos do mesmo jeito: se disser algo de um, a mesma pergunta vale para o outro, com as mesmas palavras.
4. Cite o arquivo, a coluna e a linha (ou o filtro) de cada número que usar. Se fizer uma conta, mostre como fez.
5. Estimativas com intervalo de 95% que não passaram no critério de precisão são "sem lado claro": não as trate como resultado.
6. Se os arquivos não respondem à pergunta, diga isso. Não complete com o que você sabe de fora do estudo sem avisar.
7. O resultado oficial é o do TSE; o estudo pode ter erros. Se achar um, sugira avisar em https://github.com/MuriloNM/analise-da-virada/issues

Minha pergunta:
````

## Que arquivo responde a quê

| Pergunta | Arquivo (em `planilha/pt-BR/`) |
|---|---|
| Quanto cada um teve num município, estado ou região, e quanto mudou | `municipios.csv`, `estados.csv` |
| A abstenção, os brancos e os nulos mudaram onde? | `municipios.csv`, `estados.csv` |
| De onde vieram os votos a mais (comparecimento, outros candidatos, brancos e nulos) | `de_onde_vieram.csv` |
| As hipóteses dos capítulos 1, 3, 4 e 5 se confirmaram? | `hipoteses.csv` |
| Renda, idade, religião, cor ou raça, densidade e o voto | `dados_sociais.csv`, `testes_sociais.csv` |
| Voto em partido para deputado e senador no 1º turno | `votos_partido_1t.csv`, `partidos.csv`, `esquerda_municipios.csv` |
| Como foi a contagem na noite do 2º turno | `apuracao_ao_vivo.csv` |
| O que é cada coluna | `dicionario.csv` e [`DICIONARIO.md`](DICIONARIO.md) |

`votos_partido_1t.csv` tem 21 MB: muitas IAs não leem um arquivo desse tamanho por link. Se precisar dele, filtre na planilha o estado ou o município antes de anexar.

## Revisar o estudo

Para pedir a uma IA que confira o trabalho, como um revisor. Num assistente de programação, baixe antes o repositório (`git clone https://github.com/MuriloNM/analise-da-virada`, ou o botão "Code" → "Download ZIP" no GitHub) e abra a pasta nele. Num chat que roda Python, anexe o ZIP. Depois cole:

````text
Você vai revisar o estudo "Análise da virada" (https://analise-da-virada.pages.dev/), cujos dados, scripts e página estão nesta pasta (ou no ZIP anexado, de https://github.com/MuriloNM/analise-da-virada). Leia primeiro o AGENTS.md, inteiro, e siga a seção 5.2 ("Revisar"), item por item. O objetivo é achar erros, não confirmar o que está escrito.

Trabalhe numa cópia: os scripts gravam por cima dos arquivos de dados/ e site-analise/. Não corrija nada.

Entregue uma tabela com cada conferência, o que você rodou ou comparou e o resultado (confere / não confere / não deu para conferir, e por quê). Para cada possível erro: o arquivo e a linha, o número escrito, o que você esperava e como chegou lá. Separe erro de número, de método (a técnica ou a conclusão vão além do que os dados permitem) e de texto (frase que atribui causa, que fala de pessoas em vez de lugares ou que trata um candidato diferente do outro).

Se quiser focar numa parte, faça só esta: [escreva aqui, por exemplo "o capítulo 4, de onde vieram os votos" ou "os 35 testes dos dados sociais"].
````

Achou um erro? Abra um pedido em [Issues](https://github.com/MuriloNM/analise-da-virada/issues), no modelo "Achei um erro", com o que a IA encontrou e como você conferiu.

## Refazer ou continuar

Para refazer as bases e a página, ou fazer uma análise nova com os mesmos dados, num assistente de programação aberto numa cópia do repositório:

````text
Esta pasta é o repositório do estudo "Análise da virada" (https://github.com/MuriloNM/analise-da-virada). Leia primeiro o AGENTS.md, inteiro, e o scripts/LEIA-ME.md.

Quero: [escolha uma]
(a) refazer as bases a partir das fontes do TSE e do IBGE e comparar com as de dados/, arquivo por arquivo;
(b) refazer a página a partir das bases e abri-la no meu computador;
(c) uma análise nova: [descreva a pergunta].

Para (c): antes de olhar qualquer número, escreva num arquivo com data a pergunta, a variável, o teste, o peso e o que conta como resultado, seguindo as regras de docs/analise/HIPOTESES.md, e me mostre. Só depois rode, num script novo que lê dados/ e grava um arquivo novo, sem mudar os existentes. O que vier depois de ver os dados é exploratório: diga isso.

Em tudo: siga as regras da seção 6 do AGENTS.md (lugares, não pessoas; sem atribuir causa; os dois candidatos do mesmo jeito; intervalo de 95% e critério de precisão). Baixe os arquivos do TSE devagar, como os scripts já fazem. Antes de cada passo demorado, diga o que vai fazer.
````

Quem publicar uma versão refeita ou continuada cita o estudo (licença CC BY 4.0) e deixa claro que não é a página do autor.
