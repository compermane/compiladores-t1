#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'antlr_gen'))
from antlr4 import *
from DOTA2Lexer import DOTA2Lexer
from DOTA2Parser import DOTA2Parser
from analisador_semantico import AnalisadorSemantico, gerar_html


def main():
    if len(sys.argv) != 3:
        print("Uso: python3 compilador.py entrada.txt saida.html")
        print("Exemplo: python3 compilador.py testes/sucesso.txt saida.html")
        sys.exit(1)

    arquivo_entrada = sys.argv[1]
    arquivo_saida = sys.argv[2]

    if not os.path.exists(arquivo_entrada):
        print(f"Erro: Arquivo '{arquivo_entrada}' nao encontrado")
        sys.exit(1)

    input_stream = FileStream(arquivo_entrada, encoding='utf-8')
    lexer = DOTA2Lexer(input_stream)
    lexer.removeErrorListeners()

    erros_lex = []
    class ErrorCapture:
        def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
            if offendingSymbol and offendingSymbol.text:
                if offendingSymbol.type == DOTA2Lexer.ERROR:
                    erros_lex.append(f"Linha {line}: simbolo nao identificado - {offendingSymbol.text}")
                else:
                    erros_lex.append(f"Linha {line}: erro sintatico proximo a {offendingSymbol.text}")
            else:
                erros_lex.append(f"Linha {line}: erro sintatico proximo a EOF")

    error_capture = ErrorCapture()
    lexer.addErrorListener(error_capture)

    stream = CommonTokenStream(lexer)
    parser = DOTA2Parser(stream)
    parser.removeErrorListeners()
    parser.addErrorListener(error_capture)

    tree = parser.programa()

    if erros_lex:
        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            for e in erros_lex:
                f.write(e + '\n')
            f.write("Fim da compilacao\n")
        sys.exit(1)

    walker = ParseTreeWalker()
    analisador = AnalisadorSemantico()
    walker.walk(analisador, tree)

    erros_sem = analisador.analisar()

    if erros_sem:
        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            for e in erros_sem:
                f.write(e + '\n')
            f.write("Fim da compilacao\n")
        sys.exit(1)

    html = gerar_html(analisador)

    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        f.write(html + '\n')

    print(f"Compilacao concluida. HTML gerado: {arquivo_saida}")


if __name__ == '__main__':
    main()
