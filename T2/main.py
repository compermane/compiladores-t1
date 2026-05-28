"""
Script principal para análise sintática utilizando ANTLR.

Este programa:
1. Lê um arquivo de entrada contendo código fonte.
2. Executa a análise léxica e sintática usando LALexer e LAParser.
3. Intercepta erros personalizados através de um ErrorListener.
4. Escreve o resultado (sucesso ou erro) em um arquivo de saída.

Uso:
  python3 main.py <arquivo_entrada> <arquivo_saida>
"""

from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener
from LALexer import LALexer
from LAParser import LAParser
import sys

class MeuErroListener(ErrorListener):
  """
  Esse listener sobrescreve o método `syntaxError` para tratar diferentes tipos de erro
  e escrever mensagens específicas no arquivo de saída.
  """

  def __init__(self, output_file, lexer):
    """
    output_file (str): Caminho do arquivo onde os erros serão escritos.
    lexer (LALexer): Instância do lexer, usada para identificar tipos de tokens.
    """
    super(MeuErroListener, self).__init__()
    self.output_file = output_file
    self.lexer = lexer

  def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
    """
    offendingSymbol: Token que causou o erro.
    line (int): Número da linha onde ocorreu o erro.
    """
    simbolo = offendingSymbol.text

    if simbolo == "<EOF>":
      simbolo = "EOF"

    # Tratamento de erros léxicos específicos
    if offendingSymbol.type == self.lexer.CADEIA_NAO_FECHADA:
      with open(self.output_file, 'w', encoding='utf-8') as f:
        f.write(f"Linha {line}: cadeia literal nao fechada\n")
        f.write("Fim da compilacao\n")

    elif offendingSymbol.type == self.lexer.CARACTERE_INVALIDO:
      with open(self.output_file, 'w', encoding='utf-8') as f:
        f.write(f"Linha {line}: {simbolo} - simbolo nao identificado\n")
        f.write("Fim da compilacao\n")

    elif offendingSymbol.type == self.lexer.COMENTARIO_NAO_FECHADO:
      with open(self.output_file, 'w', encoding='utf-8') as f:
        f.write(f"Linha {line}: comentario nao fechado\n")
        f.write("Fim da compilacao\n")

    # Tratamento de erro sintático genérico
    else:
      with open(self.output_file, 'w', encoding='utf-8') as f:
        f.write(f"Linha {line}: erro sintatico proximo a {simbolo}\n")
        f.write("Fim da compilacao\n")

    # Interrompe a execução após o primeiro erro
    sys.exit(1)

def main():
  # Verifica se os argumentos foram passados corretamente
  if len(sys.argv) < 3:
    print("Uso: python3 main.py <entrada> <saida>")
    sys.exit(1)

  entrada_path = sys.argv[1]
  saida_path = sys.argv[2]

  try:
    # Cria o fluxo de entrada a partir do arquivo
    input_stream = FileStream(entrada_path, encoding='utf-8')

    # Inicializa o lexer
    lexer = LALexer(input_stream)

    # Cria o fluxo de tokens a partir do lexer
    token_stream = CommonTokenStream(lexer)

    # Inicializa o parser com os tokens
    parser = LAParser(token_stream)

    # Força o preenchimento de todos os tokens (executa o lexer)
    token_stream.fill()

    # Remove listeners padrão do ANTLR
    parser.removeErrorListeners()

    # Adiciona o listener personalizado
    parser.addErrorListener(MeuErroListener(saida_path, lexer))

    # Inicia a análise sintática a partir da regra inicial 'programa'
    parser.programa()

    # Caso não haja erros, escreve mensagem de sucesso
    with open(saida_path, 'w', encoding='utf-8') as f:
      f.write("Programa sintaticamente correto.\n")

  except Exception as e:
    # Tratamento genérico de exceções inesperadas
    with open(saida_path, 'w', encoding='utf-8') as f:
      f.write(f"Erro durante a análise sintática: {str(e)}\n")
    sys.exit(1)

if __name__ == '__main__':
  main()
