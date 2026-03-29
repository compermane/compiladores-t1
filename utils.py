import constants
import re
from typing import Tuple, List

def tokenize_line(line: str, line_number: int) -> Tuple[List[str], str]:
  tokens: List[Tuple[str, str]] = []
  i: int = 0
  line = line.rstrip('\n\r')

  while i < len(line):
    ch = line[i]

    if ch in ' \t':
      i += 1
      continue

    if ch == '}':
      return tokens, "Linha {}: }} - simbolo nao identificado".format(line_number)

    if ch == '{':
      i += 1
      while i < len(line) and line[i] != '}':
        i += 1

      if i >= len(line):
        return tokens, f"Linha {line_number}: comentario nao fechado"

      i += 1
      continue

    if ch == '"':
      end = line.find('"', i + 1)
      if end == -1:
        return tokens, f"Linha {line_number}: cadeia literal nao fechada"
      lexeme = line[i:end + 1]
      tokens.append((lexeme, "CADEIA"))
      i = end + 1
      continue

    match = None
    for regex, token_type in constants.TOKEN_REGEX:
      pattern = re.compile(regex)
      match = pattern.match(line, i)
      if match:
        lexeme = match.group()
        if token_type == "IDENT_OR_KEYWORD":
          token_type = lexeme if lexeme in constants.KEYWORDS else "IDENT"
        elif token_type == "SYMBOL":
          token_type = lexeme
        tokens.append((lexeme, token_type))
        i = match.end()
        break

    if not match:
      return tokens, f"Linha {line_number}: {ch} - simbolo nao identificado"

  return tokens, None
