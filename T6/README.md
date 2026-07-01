# DOTA2Lang — Compilador para Configuração de Partidas de Dota 2

**DOTA2Lang** é uma linguagem de domínio específico (DSL) para declarar escalações de partidas de Dota 2 e validar a composição tática dos times. O compilador analisa léxica, sintática e semanticamente o arquivo de entrada, e produz um relatório tático detalhado com a análise da partida.

## Motivação

Montar uma composição de time competitiva em Dota 2 envolve respeitar diversas restrições:

- Máximo de 5 heróis por time
- Equilíbrio entre heróis farm-dependentes (carries) e suportes
- Sinergia entre habilidades de heróis (ex: Magnus precisa de aliados corpo a corpo)
- Conflito de rotas (dois heróis que disputam midlane não podem coexistir)
- Compatibilidade de itens com o tipo de ataque do herói

DOTA2Lang automatiza a validação dessas regras, permitindo que o jogador foque na estratégia.

## Exemplo Rápido

```
partida
aliados: pa, magnus, earthshaker, crystal_maiden, lion;
rivais: pudge, axe, sniper, witch_doctor, disruptor;
analisar pa;
pa constroi battle_fury;
fim_partida
```

Saída do compilador:

Arquivo HTML com as informações relevantes da partida descrita.

## Índice

- [Linguagem](#linguagem)
  - [Estrutura do Programa](#estrutura-do-programa)
  - [Palavras-chave](#palavras-chave)
  - [Símbolos](#símbolos)
  - [Identificadores](#identificadores)
  - [Gramática (ANTLR)](#gramática-antlr)
- [Compilador](#compilador)
  - [Pré-requisitos](#pré-requisitos)
  - [Como usar](#como-usar)
  - [Como compilar o compilador](#como-compilar-o-compilador)
  - [Arquitetura](#arquitetura)
- [Análise Semântica](#análise-semântica)
  - [Regras Implementadas](#regras-implementadas)
- [Casos de Teste](#casos-de-teste)
- [Vídeo Demonstrativo](#vídeo-demonstrativo)

## Linguagem

### Estrutura do Programa

```
partida
aliados: heroi1, heroi2, ...;
rivais:  heroi1, heroi2, ...;
comandos_opcionais...
fim_partida
```

O programa é dividido em 4 seções obrigatórias:

| Seção | Descrição |
|-------|-----------|
| `partida` | Palavra-chave que inicia o programa |
| `aliados :` | Lista de heróis do time aliado (separados por vírgula, terminada com `;`) |
| `rivais :` | Lista de heróis do time rival (separados por vírgula, terminada com `;`) |
| `fim_partida` | Palavra-chave que encerra o programa |

Após a declaração dos times, comandos opcionais podem ser executados.

### Palavras-chave

| Palavra | Função |
|---------|--------|
| `partida` | Inicia o programa |
| `aliados` | Declara o bloco de heróis aliados |
| `rivais` | Declara o bloco de heróis rivais |
| `analisar` | Comando para analisar um herói |
| `constroi` | Comando para atribuir um item a um herói |
| `fim_partida` | Encerra o programa |

### Símbolos

| Símbolo | Função |
|---------|--------|
| `:` | Separa a keyword do escopo (ex: `aliados:`) |
| `,` | Separa elementos de uma lista |
| `;` | Encerra comandos e declarações |

### Identificadores

Sequências que casam com `[a-zA-Z_][a-zA-Z0-9_]*`. Servem para nomear heróis (ex: `pa`, `lion`, `storm_spirit`) e itens (ex: `battle_fury`, `blink_dagger`).

### Comandos

Dois tipos de comando são suportados:

**Análise isolada:**
```
analisar <heroi>;
```

**Atribuição de item:**
```
<heroi> constroi <item>;
```

### Gramática (ANTLR)

A gramática completa está definida em [`DOTA2.g4`](DOTA2.g4) no formato ANTLR:

```antlr
grammar DOTA2;

programa:
    PARTIDA bloco_aliados bloco_rivais comandos FIM_PARTIDA EOF
    ;

bloco_aliados:
    ALIADOS COLON lista_herois SEMICOLON
    ;

bloco_rivais:
    RIVAIS COLON lista_herois SEMICOLON
    ;

lista_herois:
    IDENT (COMMA IDENT)*
    ;

comandos:
    comando*
    ;

comando:
    ANALISAR IDENT SEMICOLON
    | IDENT CONSTROI IDENT SEMICOLON
    ;

PARTIDA:     'partida';
ALIADOS:     'aliados';
RIVAIS:      'rivais';
ANALISAR:    'analisar';
CONSTROI:    'constroi';
FIM_PARTIDA: 'fim_partida';
COLON:      ':';
COMMA:      ',';
SEMICOLON:  ';';
IDENT: [a-zA-Z_][a-zA-Z0-9_]*;
WS: [ \t\r\n]+ -> skip;
ERROR: .;
```

## Compilador

### Pré-requisitos

- Python 3.8 ou superior
- Java 11 ou superior (para regenerar os arquivos ANTLR)
- ANTLR 4.13.2 (runtime Python + gerador Java)
- Pip (gerenciador de pacotes Python)

### Como usar

```bash
python3 compilador.py <entrada.txt> <saida.html>
```

- `<entrada.txt>`: arquivo fonte com o programa em DOTA2Lang
- `<saida.html>`: arquivo HTML onde o relatório será gerado

**Exemplos:**

```bash
# Compilar um caso de sucesso
python3 compilador.py testes/sucesso.txt /tmp/saida.html

# Compilar um caso com erro semântico
python3 compilador.py testes/erro_conflito_midlane.txt /tmp/saida.html
```

### Como compilar o compilador

O compilador usa ANTLR para geração do lexer e parser. Para regenerar os arquivos a partir da gramática:

```bash
# 1. Baixar o ANTLR (se não tiver)
curl -sL -o /tmp/antlr-4.13.2-complete.jar \
  https://www.antlr.org/download/antlr-4.13.2-complete.jar

# 2. Gerar os arquivos Python (opcional, já disponível no repositório)
java -jar /tmp/antlr-4.13.2-complete.jar \
  -Dlanguage=Python3 DOTA2.g4 \
  -listener -visitor -o antlr_gen

# 4. Criar um ambiente virtual (opcional, mas recomendado)
cd T6
python3 -m venv venv
source venv/bin/activate

# 3. Instalar o runtime Python do ANTLR
pip install antlr4-python3-runtime
```

### Arquitetura

O compilador é dividido em 4 fases, executadas sequencialmente:

```
Entrada (.txt)
    |
    v
[1. LEXER] (ANTLR DOTA2Lexer)
    |  Tokeniza o código fonte
    |  Erro: "Linha X: simbolo nao identificado - TOKEN"
    v
[2. PARSER] (ANTLR DOTA2Parser)
    |  Constrói a parse tree
    |  Erro: "Linha X: erro sintatico proximo a TOKEN"
    v
[3. ANALISADOR SEMÂNTICO] (AnalisadorSemantico — listener ANTLR)
    |  10 verificações de conformidade
    |  Erro: "Linha X: mensagem" + "Fim da compilacao"
    v
[4. GERADOR HTML] (função gerar_html)
    |  Produz relatório tático em página HTML estilizada
    v
Saída (.html)
```

**Classes principais:**

| Classe/Arquivo | Função |
|----------------|--------|
| `compilador.py` | Driver principal: orquestra lexer, parser, walker e geração |
| `analisador_semantico.py` | Listener ANTLR com 10 verificações semânticas |
| `DOTA2Lexer` (gerado) | Analisador léxico ANTLR |
| `DOTA2Parser` (gerado) | Analisador sintático ANTLR |

## Análise Semântica

### Regras Implementadas

O compilador realiza **10 verificações semânticas** sobre o programa:

| # | Regra | Descrição | Mensagem de Erro |
|---|-------|-----------|-------------------|
| 1 | **Existência de Herói** | Todo herói usado deve estar na `HERO_DATABASE` | `Linha X: heroi Y nao encontrado na base de dados` |
| 2 | **Existência de Item** | Todo item usado deve estar na `ITEM_DATABASE` | `Linha X: item Y nao encontrado na base de dados` |
| 3 | **Unicidade no Time** | Um herói não pode aparecer duas vezes no mesmo time | `Linha X: heroi Y repetido no time aliados/rivais` |
| 4 | **Exclusividade entre Times** | Um herói não pode estar nos dois times | `Linha X: heroi Y ja foi escalado no time aliado` |
| 5 | **Limite de Jogadores** | Cada time tem no máximo 5 heróis | `Linha X: time Y excede o limite de 5 herois` |
| 6 | **Farm-dependentes** | Máximo 3 heróis com posição 1-3 no time aliado | `Linha X: time aliado possui mais de 3 herois farm-dependentes` |
| 7 | **Suporte Mínimo** | Mínimo 1 herói de posição 5 (hard support) no time aliado | `Linha X: time aliado nao possui suporte suficiente (minimo 1)` |
| 8 | **Sinergia Magnus** | Se Magnus está no time aliado, deve haver ao menos 1 aliado corpo a corpo | `Linha X: magnus exige ao menos um aliado corpo a corpo` |
| 9 | **Conflito de Rota** | Heróis que disputam midlane não podem coexistir no mesmo time | `Linha X: conflito de rota - herois X disputam midlane` |
| 10 | **Type Mismatch** | Item deve ser compatível com o tipo de ataque do herói | `Linha X: item Y incompativel com heroi Z` |

### Bases de Dados

**HERO_DATABASE** — 30 heróis reais de Dota 2 cadastrados:

`antimage`, `axe`, `crystal_maiden`, `disruptor`, `drow_ranger`, `earthshaker`, `faceless_void`, `invoker`, `juggernaut`, `legion_commander`, `lina`, `lion`, `magnus`, `morphling`, `ogre_magi`, `pa`, `phantom_assassin`, `phantom_lancer`, `pudge`, `riki`, `rubick`, `sf`, `skywrath_mage`, `sniper`, `storm_spirit`, `tidehunter`, `tinker`, `vengeful_spirit`, `witch_doctor`, `zeus`

Cada herói possui os atributos: `ataque` (melee/ranged), `posicao` (1-5), `alcance` (melee/ranged).

**ITEM_DATABASE** — 24 itens cadastrados:

`aghanims_scepter`, `assault_cuirass`, `battle_fury`, `black_king_bar`, `blink_dagger`, `bloodstone`, `daedalus`, `desolator`, `echo_sabre`, `force_staff`, `heart_of_tarrasque`, `hurricane_pike`, `magic_wand`, `manta_style`, `moon_shard`, `phase_boots`, `pipe_of_insight`, `power_treads`, `radiance`, `sange_and_yasha`, `shadow_blade`, `shivas_guard`, `silver_edge`, `skadi`, `soul_ring`

Cada item possui o atributo: `restricao` (None = livre, `'melee'` = apenas corpo a corpo, `'ranged'` = apenas à distância).

## Casos de Teste

O diretório [`testes/`](testes/) contém **18 casos de teste** (14 erro + 4 sucesso):

### Casos de Sucesso

| Arquivo | Descrição |
|---------|-----------|
| `sucesso.txt` | Partida completa com 5 heróis por time, comandos `analisar` e `constroi` |
| `sucesso_simples.txt` | Partida sem comandos, apenas escalação |
| `sucesso_analisar_fora_time.txt` | Comando `analisar` para herói na base mas não escalado |
| `sucesso_complexo.txt` | Composição variada com sinergias e itens |

### Casos de Erro

| Arquivo | Regra Violada |
|---------|---------------|
| `erro_lexico.txt` | Caractere `@` não reconhecido |
| `erro_sintatico.txt` | Ponto e vírgula ausente |
| `erro_heroi_inexistente.txt` | Herói `batman` fora da base |
| `erro_item_inexistente.txt` | Item `infinity_edge` fora da base |
| `erro_repetido_time.txt` | `pa` aparece duas vezes nos aliados |
| `erro_duplicado_entre_times.txt` | `pa` aparece nos dois times |
| `erro_limite_time.txt` | 6 heróis no time aliado |
| `erro_composicao_farm_demais.txt` | 4 farm-dependentes (pos 1-3) |
| `erro_sem_suporte.txt` | Nenhum suporte (pos 5) no time aliado |
| `erro_magnus_sem_melee.txt` | Magnus sem aliado corpo a corpo |
| `erro_conflito_midlane.txt` | Tinker e Storm Spirit no mesmo time |
| `erro_type_mismatch.txt` | Battle Fury (item melee) em Lion (herói ranged) |
| `erro_analisar_inexistente.txt` | `analisar batman` (herói fora da base) |

Para executar todos os testes automaticamente:

```bash
python3 testa_tudo.py
```

## Vídeo Demonstrativo

[Link para o vídeo demonstrativo](https://drive.google.com/file/d/1lHsrVdNOxArsmv7bqlricU4b7x6oUR4P/view?usp=sharing)
