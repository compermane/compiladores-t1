## Dados
Nome: Eugênio Akinori Kisi Nishimiya
RA: 811598

## Descrição

O objetivo deste trabalho é implementar um **analisador sintático** para a linguagem LA utilizando a ferramenta ANTLR.

O programa recebe um arquivo de entrada contendo um código fonte e verifica se ele está sintaticamente correto de acordo com a gramática definida. Em caso de erro, mensagens específicas são geradas.

---

## Tecnologias utilizadas

- Python 3
- ANTLR4
- antlr4-python3-runtime

---

## Estrutura

- `main.py` → programa principal
- `LALexer.py` → analisador léxico (gerado pelo ANTLR)
- `LAParser.py` → analisador sintático (gerado pelo ANTLR)
- `LA.g4` → gramática da linguagem

---

## Como executar

### Pré requisitos
- Java Development Kit (JDK): Versão 11 ou superior
- Python: Versão 3.11.2 ou superior
- ANTLR 4 Complete JAR: Versão 4.13.2

### Clonar o repositório e entrar na pasta T2
```bash
git clone https://github.com/gabrielcavalca/Compiladores.T2
cd T2
```

### 1. Criar ambiente virtual (opcional, recomendado)

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalar dependências
```bash
pip install antlr4-python3-runtime
```

### 3. Compilar a linguagem LA.g4
```bash
java -jar caminho/para/o/antlr/antlr-4.13.2-complete.jar -Dlanguage=Python3 LA.g4 -visitor -o .
```

### 4. Executar o corretor automático na raiz de T2
```bash
java -jar caminho/para/compiladores-corretor-automatico-1.0-SNAPSHOT-jar-with-dependencies.jar "python3 main.py" gcc temp caminho/para/casos/de/teste "811598" "t2"
```
