import sys
from antlr4 import *
from LAParser import LAParser
from LALexer import LALexer
from LAListener import LAListener

# Tipos primitivos aceitos pela linguagem
TIPOS_VALIDOS = {'literal', 'inteiro', 'real', 'logico'}

class AnalisadorSemantico(LAListener):
  def __init__(self, token_stream):
    # Tabela de símbolos: nome -> tipo
    self.simbolos = {}

    # Lista de erros semânticos encontrados
    self.erros = []

  # Retorna número da linha de um token (para mensagens de erro)
  def linha_token(self, token):
    return token.line

  # Inferência de tipo de expressão
  def tipo_expressao(self, ctx):
    if ctx is None:
      return None

    # expressao → expressao_logica
    if isinstance(ctx, LAParser.ExpressaoContext):
      return self.tipo_expressao(ctx.expressao_logica())

    # expressao_logica → expressao_relacional (e/ou ...)
    elif isinstance(ctx, LAParser.Expressao_logicaContext):
      tipos = [self.tipo_expressao(child) for child in ctx.expressao_relacional()]

      if not tipos:
        return None

      if len(tipos) == 1:
        return tipos[0]

      return 'logico' if all(t == 'logico' for t in tipos) else None

    # expressao_relacional
    elif isinstance(ctx, LAParser.Expressao_relacionalContext):
      if ctx.getChildCount() == 1:
        return self.tipo_expressao(ctx.expressao_aritmetica(0))

      tipo_esq = self.tipo_expressao(ctx.expressao_aritmetica(0))
      tipo_dir = self.tipo_expressao(ctx.expressao_aritmetica(1))

      if tipo_esq in ('inteiro', 'real') and tipo_dir in ('inteiro', 'real'):
        return 'logico'

      if tipo_esq == tipo_dir:
        return 'logico'

      return None

    # expressao_aritmetica
    elif isinstance(ctx, LAParser.Expressao_aritmeticaContext):
      termos = [self.tipo_expressao(t) for t in ctx.termo()]

      if not termos:
        return None

      tipo = termos[0]

      for t in termos[1:]:
        if tipo in ('inteiro', 'real') and t in ('inteiro', 'real'):
          tipo = 'real' if 'real' in (tipo, t) else 'inteiro'
        elif tipo == 'literal' and t == 'literal':
          tipo = 'literal'
        else:
          return None

      return tipo

    # termo (*, /, %)
    elif isinstance(ctx, LAParser.TermoContext):
      fatores = [self.tipo_expressao(f) for f in ctx.fator()]

      if not fatores:
        return None

      tipo = fatores[0]

      for t in fatores[1:]:
        if tipo in ('inteiro', 'real') and t in ('inteiro', 'real'):
          tipo = 'real' if 'real' in (tipo, t) else 'inteiro'
        else:
          return None

      return tipo

    # fator (casos base)
    elif isinstance(ctx, LAParser.FatorContext):

      # variável
      if ctx.IDENT():
        nome = ctx.IDENT().getText()
        tipo = self.simbolos.get(nome)

        if tipo is None:
          self.erros.append(f"Linha {ctx.start.line}: identificador {nome} nao declarado")
          return None

        return tipo

      # constantes
      if ctx.NUM_INT():
        return 'inteiro'

      if ctx.NUM_REAL():
        return 'real'

      if ctx.CADEIA():
        return 'literal'

      if ctx.getText() in ('verdadeiro', 'falso'):
        return 'logico'

      # (expressao)
      if ctx.ABREPAR():
        return self.tipo_expressao(ctx.expressao())

      # -fator
      if ctx.getChildCount() == 2 and ctx.getChild(0).getText() == '-':
        return self.tipo_expressao(ctx.fator())

      # nao fator
      if ctx.getChildCount() == 2 and ctx.getChild(0).getText().lower() == 'nao':
        t = self.tipo_expressao(ctx.fator())
        return 'logico' if t == 'logico' else None

      # &variavel (endereço)
      if ctx.getChildCount() == 2 and ctx.getChild(0).getText() == '&':
        return 'endereco'

      # ^variavel
      if ctx.CIRCUNFLEXO():
        nome = ctx.IDENT().getText()
        return self.simbolos.get(nome)

      # chamada de função (não implementado completamente)
      if ctx.chamada_funcao():
        return None  # melhoria futura: implementar tabela de funções

      # acesso a campo
      if ctx.acesso_campo():
        return self.tipo_expressao(ctx.acesso_campo())

      return None

    return None

  # Compatibilidade de tipos
  def eh_compatível(self, tipo_var, tipo_exp):
    if tipo_var == tipo_exp:
      return True

    # promoção implícita: inteiro -> real
    if tipo_var == 'real' and tipo_exp == 'inteiro':
      return True

    return False

  # Atribuição
  def enterAtribuicao(self, ctx: LAParser.AtribuicaoContext):
    nome = ctx.getChild(0).getText()
    tipo_var = self.simbolos.get(nome)

    if tipo_var is None:
      token = ctx.getChild(0).getSymbol()
      self.erros.append(f"Linha {token.line}: identificador {nome} nao declarado")
      return

    tipo_exp = self.tipo_expressao(ctx.expressao())

    if not self.eh_compatível(tipo_var, tipo_exp):
      token = ctx.getChild(0).getSymbol()
      self.erros.append(f"Linha {token.line}: atribuicao nao compativel para {nome}")

  # Declaração de variáveis
  def enterDeclaracao(self, ctx: LAParser.DeclaracaoContext):
    tipo_ctx = ctx.lista_variaveis().variavel(0).tipo()
    tipo = tipo_ctx.getText().replace("^", "")

    if tipo not in TIPOS_VALIDOS:
      self.erros.append(
        f"Linha {self.linha_token(tipo_ctx.start)}: tipo {tipo} nao declarado"
      )

    for var in ctx.lista_variaveis().variavel():
      for i in range(len(var.IDENT())):
        nome = var.IDENT(i).getText()

        if nome in self.simbolos:
          token = var.IDENT(i).getSymbol()
          self.erros.append(
            f"Linha {self.linha_token(token)}: identificador {nome} ja declarado anteriormente"
          )
        else:
          self.simbolos[nome] = tipo

  # Estruturas de controle
  def enterComandoenquanto(self, ctx: LAParser.ComandoenquantoContext):
    self.tipo_expressao(ctx.expressao())

  # Leitura
  def enterLeitura(self, ctx: LAParser.LeituraContext):
    for child in ctx.lista_identificadores().children:
      if child.getText() == ',':
        continue

      if isinstance(child, LAParser.Acesso_campoContext):
        continue

      nome = child.getText()

      if nome not in self.simbolos:
        token = child.getSymbol()
        self.erros.append(
          f"Linha {self.linha_token(token)}: identificador {nome} nao declarado"
        )

  # Escrita
  def enterEscrita(self, ctx: LAParser.EscritaContext):
    for exp in ctx.expressao():
      self.tipo_expressao(exp)

def main():
  entrada = sys.argv[1]
  saida = sys.argv[2]

  input_stream = FileStream(entrada, encoding='utf-8')
  lexer = LALexer(input_stream)
  tokens = CommonTokenStream(lexer)
  parser = LAParser(tokens)

  tree = parser.programa()

  analisador = AnalisadorSemantico(tokens)
  walker = ParseTreeWalker()
  walker.walk(analisador, tree)

  with open(saida, 'w', encoding='utf-8') as f:
    for erro in analisador.erros:
      f.write(erro + '\n')
    f.write("Fim da compilacao\n")

if __name__ == "__main__":
  main()
