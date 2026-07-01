#!/bin/bash
# Script para regenerar os arquivos ANTLR a partir da gramatica DOTA2.g4
# Uso: ./gera_antlr.sh

set -e

ANTLR_JAR="/tmp/antlr-4.13.2-complete.jar"
ANTLR_URL="https://www.antlr.org/download/antlr-4.13.2-complete.jar"

# Baixa o ANTLR se nao existir
if [ ! -f "$ANTLR_JAR" ]; then
    echo "Baixando ANTLR 4.13.2..."
    curl -sL -o "$ANTLR_JAR" "$ANTLR_URL"
fi

echo "Gerando arquivos ANTLR a partir de DOTA2.g4..."
java -jar "$ANTLR_JAR" \
    -Dlanguage=Python3 \
    DOTA2.g4 \
    -listener \
    -visitor \
    -o antlr_gen

echo "Arquivos gerados em antlr_gen/:"
ls -la antlr_gen/

echo ""
echo "Certifique-se de ter o runtime Python instalado:"
echo "  pip install antlr4-python3-runtime"
