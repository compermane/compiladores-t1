## Dados
Nome: Eugênio Akinori Kisi Nishimiya
RA: 811598

## Tecnologias utilizadas

- Python 3
- ANTLR4
- antlr4-python3-runtime

## Como executar

### Pré requisitos
- Java Development Kit (JDK): Versão 11 ou superior
- Python: Versão 3.11.2 ou superior
- ANTLR 4 Complete JAR: Versão 4.13.2

### 1. Clonar o Repositório
```bash
git clone https://github.com/compermane/compiladores-t1
cd T5
```

### 2. Criar ambiente virtual (opcional, recomendado)
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependências
```bash
pip install antlr4-python3-runtime
```

### 4. Executar o corretor automático na raiz do repositório
Com o corretor automático e os casos de testes na raiz do repositório, execute (na raiz):
```bash
java -jar "compiladores-corretor-automatico-1.0-SNAPSHOT-jar-with-dependencies.jar" \
    "python3 ./T5/compiler.py" \
    /usr/bin/gcc \
    "temp" \
    "casos-de-teste/casos-de-teste" \
    "811598" "t5"
```
