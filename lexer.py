import utils
import sys
import os
from typing import List

def lexer(entrada_path: str, saida_path: str) -> None:
  try:
    with open(entrada_path, 'r', encoding='utf-8') as f:
      linhas = f.readlines()
      f.close()
  except FileNotFoundError:
    sys.exit(1)

  # Abre o arquivo especificado e compila linha por linha
  # No fim, escreve no arquivo de saída o resultado da compilação
  saida = []
  for num_linha, linha in enumerate(linhas, 1):
    tokens, erro = utils.tokenize_line(linha, num_linha)
    if erro:
      for lexema, tipo in tokens:
        if tipo.isupper():
          saida.append(f"<'{lexema}',{tipo}>\n")
        else:
          saida.append(f"<'{lexema}','{tipo}'>\n")
      saida.append(f"{erro}\n")
      break
    for lexema, tipo in tokens:
        if tipo.isupper():
            saida.append(f"<'{lexema}',{tipo}>\n")
        else:
            saida.append(f"<'{lexema}','{tipo}'>\n")

  with open(saida_path, 'w', encoding='utf-8') as f_out:
      f_out.writelines(saida)
      f_out.close()

if __name__ == "__main__":
  if len(sys.argv) < 3:
    sys.exit()

  if "DEBUG" in sys.argv:
    arquivos: List[str] = [f for f in os.scandir("./casos-de-teste/casos-de-teste/1.casos_teste_t1/entrada") if f.is_file()]

    for i, arquivo in enumerate(arquivos):
      try:
        lexer(arquivo, f"saida-{arquivo.name}")
      except:
        print(f"Erro em saída-{arquivo.name}")
  else:
    entrada_path = sys.argv[1]
    saida_path = sys.argv[2]
    lexer(entrada_path, saida_path)

