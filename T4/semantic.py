import sys
from antlr4 import *
from LAParser import LAParser
from LALexer import LALexer
from LAListener import LAListener

TIPOS_VALIDOS = {'literal', 'inteiro', 'real', 'logico'}

class AnalisadorSemantico(LAListener):
  # Analisador semântico para a linguagem LA
  # Realiza checagem de tipos, validação de escopo e consistência de identificadores.

  def __init__(self, token_stream):
    self.simbolos = {}
    self.erros = []
    self.tokens = token_stream
    self.tipos_definidos = {}
    self.campos_registro = {}
    self.funcoes = {}
    self.procedimentos = {}
    self.escopo_atual = 'global'
    self.simbolos_locais = {}
    self.constantes = {}

  def linha_token(self, token):
    # Retorna o número da linha de um token para formatação de erros.
    return token.line

  def tipo_expressao(self, ctx):
    # Avalia recursivamente o tipo de uma expressão ou subexpressão na AST.
    # Retorna o tipo resultante (ex: 'inteiro', 'real', 'logico', 'literal') ou None se inválido.
    if isinstance(ctx, LAParser.ExpressaoContext):
      return self.tipo_expressao(ctx.expressao_logica())

    elif isinstance(ctx, LAParser.Expressao_logicaContext):
      tipos = [self.tipo_expressao(child) for child in ctx.expressao_relacional()]
      if len(tipos) == 1:
        return tipos[0]
      if all(t == 'logico' for t in tipos):
        return 'logico'
      return None

    elif isinstance(ctx, LAParser.Expressao_relacionalContext):
      if ctx.getChildCount() == 1:
        return self.tipo_expressao(ctx.expressao_aritmetica(0))
      else:
        tipo_esq = self.tipo_expressao(ctx.expressao_aritmetica(0))
        tipo_dir = self.tipo_expressao(ctx.expressao_aritmetica(1))
        if tipo_esq in ('inteiro','real') and tipo_dir in ('inteiro','real'):
          return 'logico'
        if tipo_esq == tipo_dir:
          return 'logico'
        return None

    elif isinstance(ctx, LAParser.Expressao_aritmeticaContext):
      tipos = [self.tipo_expressao(term) for term in ctx.termo()]
      tipo_acumulado = tipos[0]
      for t in tipos[1:]:
        if tipo_acumulado in ('inteiro','real') and t in ('inteiro','real'):
          tipo_acumulado = 'real' if 'real' in (tipo_acumulado, t) else 'inteiro'
        elif tipo_acumulado == 'literal' and t == 'literal':
          tipo_acumulado = 'literal'
        else:
          return None
      return tipo_acumulado

    elif isinstance(ctx, LAParser.TermoContext):
      tipos = [self.tipo_expressao(fat) for fat in ctx.fator()]
      tipo_acumulado = tipos[0]
      for t in tipos[1:]:
        if tipo_acumulado in ('inteiro','real') and t in ('inteiro','real'):
          tipo_acumulado = 'real' if 'real' in (tipo_acumulado, t) else 'inteiro'
        else:
          return None
      return tipo_acumulado

    elif isinstance(ctx, LAParser.FatorContext):
      if ctx.IDENT():
        nome = ctx.IDENT().getText()
        tipo_var = self.simbolos_locais.get(nome) or self.simbolos.get(nome)
        if tipo_var is None:
          self.erros.append(f"Linha {ctx.start.line}: identificador {nome} nao declarado")
          return None
        return tipo_var

      if ctx.NUM_INT():
        return 'inteiro'
      if ctx.NUM_REAL():
        return 'real'
      if ctx.CADEIA():
        return 'literal'
      if ctx.getText() in ('verdadeiro', 'falso'):
        return 'logico'
      if ctx.ABREPAR():
        return self.tipo_expressao(ctx.expressao())
      if ctx.getChildCount() == 2 and ctx.getChild(0).getText() == '-':
        return self.tipo_expressao(ctx.fator())
      if ctx.getChildCount() == 2 and ctx.getChild(0).getText().lower() == 'nao':
        return 'logico' if self.tipo_expressao(ctx.fator()) == 'logico' else None
      if ctx.getChildCount() == 2 and ctx.getChild(0).getText() == '&':
        return 'endereco'
      if ctx.CIRCUNFLEXO():
        nome = ctx.IDENT().getText()
        return self.simbolos.get(nome)
      if ctx.chamada_funcao():
        return self.tipo_funcao(ctx.chamada_funcao())
      if ctx.acesso_campo():
        return self.tipo_acesso_campo(ctx.acesso_campo())
      if hasattr(ctx, 'acesso_array') and ctx.acesso_array():
        return self.tipo_acesso_array(ctx.acesso_array())
      return None

    if isinstance(ctx, LAParser.Acesso_campoContext):
      return self.tipo_acesso_campo(ctx)
    if hasattr(LAParser, 'Acesso_arrayContext') and isinstance(ctx, LAParser.Acesso_arrayContext):
      return self.tipo_acesso_array(ctx)
    return None

  def tipo_acesso_campo(self, ctx):
    # Determina o tipo de um campo interno pertencente a um registro.
    if hasattr(ctx, 'IDENT') and ctx.IDENT():
      nome_var = ctx.IDENT(0).getText()
      nome_campo = ctx.IDENT(1).getText()

      if nome_var not in self.simbolos_locais and nome_var not in self.simbolos:
        self.erros.append(f"Linha {ctx.start.line}: identificador {nome_var}.{nome_campo} nao declarado")
        return None

      if nome_var in self.campos_registro:
        campos = self.campos_registro[nome_var]
        if nome_campo in campos:
          return campos[nome_campo]

      self.erros.append(f"Linha {ctx.start.line}: identificador {nome_var}.{nome_campo} nao declarado")
      return None
    return None

  def tipo_acesso_array(self, ctx):
    # Valida o índice e infere o tipo base de uma variável do tipo vetor (array).
    if hasattr(ctx, 'IDENT') and ctx.IDENT():
      nome_var = ctx.IDENT().getText()

      if nome_var not in self.simbolos_locais and nome_var not in self.simbolos:
        self.erros.append(f"Linha {ctx.start.line}: identificador {nome_var} nao declarado")
        return None

      self.tipo_expressao(ctx.expressao())
      return self.simbolos_locais.get(nome_var) or self.simbolos.get(nome_var)
    return None

  def tipo_funcao(self, ctx):
    # Valida os argumentos passados a uma função e retorna o tipo do seu retorno.
    if hasattr(ctx, 'IDENT') and ctx.IDENT():
      nome_funcao = ctx.IDENT().getText()

      if nome_funcao not in self.funcoes:
        self.erros.append(f"Linha {ctx.start.line}: identificador {nome_funcao} nao declarado")
        return None

      info_funcao = self.funcoes[nome_funcao]
      parametros_esperados = info_funcao['parametros']
      parametros_passados = []

      if ctx.lista_expressao():
        for exp in ctx.lista_expressao().expressao():
          parametros_passados.append(self.tipo_expressao(exp))

      if len(parametros_passados) != len(parametros_esperados):
        self.erros.append(f"Linha {ctx.start.line}: incompatibilidade de parametros na chamada de {nome_funcao}")
        return info_funcao['tipo_retorno']

      for i, (tipo_passado, (_, tipo_esperado)) in enumerate(zip(parametros_passados, parametros_esperados)):
        if tipo_passado and tipo_passado != tipo_esperado:
          self.erros.append(f"Linha {ctx.start.line}: incompatibilidade de parametros na chamada de {nome_funcao}")
          break

      return info_funcao['tipo_retorno']
    return None

  def eh_compativel(self, tipo_var, tipo_exp):
    # Verifica a compatibilidade de atribuição entre tipos (permite coerção de inteiro para real).
    if tipo_var == tipo_exp:
      return True
    if tipo_var == 'real' and tipo_exp == 'inteiro':
      return True
    return False

  def enterAtribuicao(self, ctx:LAParser.AtribuicaoContext):
    # Valida se o tipo do lado direito é compatível com o identificador do lado esquerdo.
    lado_esquerdo = ctx.getChild(0)
    lado_esquerdo_texto = lado_esquerdo.getText()

    if lado_esquerdo_texto == '^':
      ident_node = ctx.getChild(1)
      nome_ponteiro = ident_node.getText()
      tipo_ponteiro = self.simbolos_locais.get(nome_ponteiro) or self.simbolos.get(nome_ponteiro)
      nome_var = f"^{nome_ponteiro}"
      token_var = ident_node.getSymbol()

      if tipo_ponteiro is None:
        self.erros.append(f"Linha {token_var.line}: identificador {nome_ponteiro} nao declarado")
        return
      tipo_var = tipo_ponteiro
    elif hasattr(lado_esquerdo, 'getSymbol'):
      nome_var = lado_esquerdo.getText()
      tipo_var = self.simbolos_locais.get(nome_var) or self.simbolos.get(nome_var)
      token_var = lado_esquerdo.getSymbol()

      if tipo_var is None:
        self.erros.append(f"Linha {token_var.line}: identificador {nome_var} nao declarado")
        return
    elif hasattr(lado_esquerdo, 'IDENT') and lado_esquerdo.IDENT():
      nome_var = lado_esquerdo.getText()
      if hasattr(lado_esquerdo, 'ABRE_COLCHETE'):
        tipo_var = self.tipo_acesso_array(lado_esquerdo)
        token_var = lado_esquerdo.IDENT().getSymbol()
      else:
        tipo_var = self.tipo_acesso_campo(lado_esquerdo)
        token_var = lado_esquerdo.IDENT(0).getSymbol()
      if tipo_var is None:
        return
    else:
      nome_var = lado_esquerdo.getText()
      self.erros.append(f"Linha {ctx.start.line}: identificador {nome_var} nao declarado")
      return

    tipo_exp = self.tipo_expressao(ctx.expressao())

    if tipo_var is not None and tipo_exp is not None and not self.eh_compativel(tipo_var, tipo_exp):
      linha = token_var.line if hasattr(token_var, 'line') else ctx.start.line
      self.erros.append(f"Linha {linha}: atribuicao nao compativel para {nome_var}")

  def enterDeclaracoes_locais(self, ctx:LAParser.Declaracoes_locaisContext):
    # Inicia o processamento das variáveis locais declaradas.
    if hasattr(ctx, 'lista_variaveis'):
      for lista_vars in ctx.lista_variaveis():
        self.process_lista_variaveis(lista_vars)

  def extract_variable_names(self, var_ctx):
    # Extrai os nomes de variáveis de um nó eliminando delimitadores e dimensões de arrays.
    variable_names = []
    children = [var_ctx.getChild(i) for i in range(var_ctx.getChildCount())]

    i = 0
    while i < len(children):
      child = children[i]
      if hasattr(child, 'getSymbol') and child.getSymbol().type == LALexer.IDENT:
        variable_names.append(child.getText())
        if i + 1 < len(children) and hasattr(children[i + 1], 'getSymbol') and children[i + 1].getSymbol().type == LALexer.ABRE_COLCHETE:
          i += 3
        else:
          i += 1
      else:
        i += 1
    return variable_names

  def process_lista_variaveis(self, lista_vars_ctx):
    # Itera e encaminha cada variável da lista para o processamento individual.
    for var_ctx in lista_vars_ctx.variavel():
      self.process_variavel(var_ctx)

  def process_variavel(self, var_ctx):
    # Registra a variável na tabela de símbolos adequada, validando escopo e duplicidade.
    tipo_ctx = var_ctx.tipo()
    if tipo_ctx is None:
      return

    if hasattr(tipo_ctx, 'tipo_registro') and tipo_ctx.tipo_registro():
      registro_ctx = tipo_ctx.tipo_registro()
      tipo_texto = 'registro'
      campos = {}

      for campo_ctx in registro_ctx.lista_campos().campo():
        tipo_campo = campo_ctx.tipo_base().getText().replace("^", "")
        if tipo_campo not in TIPOS_VALIDOS:
          self.erros.append(f"Linha {self.linha_token(campo_ctx.tipo_base().start)}: tipo {tipo_campo} nao declarado")

        for j in range(campo_ctx.IDENT().__len__()):
          campos[campo_ctx.IDENT(j).getText()] = tipo_campo

      for i in range(var_ctx.IDENT().__len__()):
        nome_var = var_ctx.IDENT(i).getText()
        conflict_found = (nome_var in self.simbolos_locais or nome_var in self.simbolos) if self.escopo_atual in ['funcao', 'procedimento'] else (nome_var in self.simbolos)

        if conflict_found:
          self.erros.append(f"Linha {self.linha_token(var_ctx.IDENT(i).getSymbol())}: identificador {nome_var} ja declarado anteriormente")
        else:
          if self.escopo_atual in ['funcao', 'procedimento']:
            self.simbolos_locais[nome_var] = tipo_texto
          else:
            self.simbolos[nome_var] = tipo_texto
          self.campos_registro[nome_var] = campos
    else:
      if hasattr(tipo_ctx, 'tipo_base') and tipo_ctx.tipo_base():
        tipo_texto = tipo_ctx.tipo_base().getText().replace("^", "")
      elif hasattr(tipo_ctx, 'tipo_identificado') and tipo_ctx.tipo_identificado():
        tipo_texto = tipo_ctx.tipo_identificado().getText().replace("^", "")
      else:
        tipo_texto = tipo_ctx.getText().replace("^", "")

      if tipo_texto not in TIPOS_VALIDOS and tipo_texto not in self.tipos_definidos:
        self.erros.append(f"Linha {self.linha_token(tipo_ctx.start)}: tipo {tipo_texto} nao declarado")

      for nome_var in self.extract_variable_names(var_ctx):
        if self.escopo_atual in ['funcao', 'procedimento']:
          conflict_found = (nome_var in self.simbolos_locais or nome_var in self.simbolos or nome_var in self.tipos_definidos or nome_var in self.funcoes or nome_var in self.procedimentos or nome_var in self.constantes)
        else:
          conflict_found = (nome_var in self.simbolos or nome_var in self.tipos_definidos or nome_var in self.funcoes or nome_var in self.procedimentos or nome_var in self.constantes)

        if conflict_found:
          token_var = next((var_ctx.IDENT(j).getSymbol() for j in range(var_ctx.IDENT().__len__()) if var_ctx.IDENT(j).getText() == nome_var), None)
          if token_var:
            self.erros.append(f"Linha {self.linha_token(token_var)}: identificador {nome_var} ja declarado anteriormente")
        elif nome_var not in self.constantes:
          if self.escopo_atual in ['funcao', 'procedimento']:
            self.simbolos_locais[nome_var] = tipo_texto
          else:
            self.simbolos[nome_var] = tipo_texto
          if tipo_texto in self.tipos_definidos and tipo_texto in self.campos_registro:
            self.campos_registro[nome_var] = self.campos_registro[tipo_texto]

  def enterDeclaracao(self, ctx:LAParser.DeclaracaoContext):
    # Garante o processamento das variáveis mapeadas no bloco de declarações.
    for var_ctx in ctx.lista_variaveis().variavel():
      self.process_variavel(var_ctx)

  def enterDeclaracao_tipo(self, ctx:LAParser.Declaracao_tipoContext):
    # Insere um novo tipo customizado (geralmente um registro estruturado) no escopo global.
    nome_tipo = ctx.IDENT().getText()

    if nome_tipo in self.tipos_definidos or nome_tipo in self.simbolos:
      self.erros.append(f"Linha {self.linha_token(ctx.IDENT().getSymbol())}: identificador {nome_tipo} ja declarado anteriormente")
    else:
      self.tipos_definidos[nome_tipo] = 'tipo_personalizado'
      if hasattr(ctx, 'tipo_registro') and ctx.tipo_registro():
        campos = {}
        for campo_ctx in ctx.tipo_registro().lista_campos().campo():
          tipo_campo = campo_ctx.tipo_base().getText().replace("^", "")
          if tipo_campo not in TIPOS_VALIDOS:
            self.erros.append(f"Linha {self.linha_token(campo_ctx.tipo_base().start)}: tipo {tipo_campo} nao declarado")
          for j in range(campo_ctx.IDENT().__len__()):
            campos[campo_ctx.IDENT(j).getText()] = tipo_campo
        self.campos_registro[nome_tipo] = campos

  def enterDeclaracao_constante(self, ctx:LAParser.Declaracao_constanteContext):
    # Armazena e valida o identificador único para uma nova constante global.
    nome_constante = ctx.IDENT().getText()
    tipo_constante = ctx.tipo_base().getText().replace("^", "")

    if nome_constante in self.constantes or nome_constante in self.simbolos or nome_constante in self.tipos_definidos:
      self.erros.append(f"Linha {self.linha_token(ctx.IDENT().getSymbol())}: identificador {nome_constante} ja declarado anteriormente")
    else:
      self.constantes[nome_constante] = tipo_constante
      self.simbolos[nome_constante] = tipo_constante

  def enterDeclaracao_funcao(self, ctx:LAParser.Declaracao_funcaoContext):
    # Valida a assinatura da função e migra temporariamente para o escopo local de função.
    nome_funcao = ctx.IDENT().getText()
    tipo_retorno = ctx.tipo_base().getText().replace("^", "")

    if nome_funcao in self.funcoes or nome_funcao in self.procedimentos or nome_funcao in self.simbolos:
      self.erros.append(f"Linha {self.linha_token(ctx.IDENT().getSymbol())}: identificador {nome_funcao} ja declarado anteriormente")
    else:
      parametros = []
      if ctx.parametros():
        for param_ctx in ctx.parametros().parametro():
          nome_param = param_ctx.IDENT().getText()
          tipo_param = param_ctx.tipo_base().getText().replace("^", "") if param_ctx.tipo_base() else param_ctx.tipo_identificado().getText().replace("^", "")
          parametros.append((nome_param, tipo_param))

      self.funcoes[nome_funcao] = {'tipo_retorno': tipo_retorno, 'parametros': parametros}

    self.escopo_atual = 'funcao'
    self.simbolos_locais = {}

    if ctx.parametros():
      for param_ctx in ctx.parametros().parametro():
        nome_param = param_ctx.IDENT().getText()
        tipo_param = param_ctx.tipo_base().getText().replace("^", "") if param_ctx.tipo_base() else param_ctx.tipo_identificado().getText().replace("^", "")
        self.simbolos_locais[nome_param] = tipo_param
        if tipo_param in self.tipos_definidos and tipo_param in self.campos_registro:
          self.campos_registro[nome_param] = self.campos_registro[tipo_param]

  def exitDeclaracao_funcao(self, ctx:LAParser.Declaracao_funcaoContext):
    # Restaura o escopo para o ambiente global ao finalizar o bloco da função.
    self.escopo_atual = 'global'
    self.simbolos_locais = {}

  def enterDeclaracao_procedimento(self, ctx:LAParser.Declaracao_procedimentoContext):
    # Valida a assinatura do procedimento e chaveia o contexto para o escopo local.
    nome_procedimento = ctx.IDENT().getText()

    if nome_procedimento in self.procedimentos or nome_procedimento in self.funcoes or nome_procedimento in self.simbolos:
      self.erros.append(f"Linha {self.linha_token(ctx.IDENT().getSymbol())}: identificador {nome_procedimento} ja declarado anteriormente")
    else:
      parametros = []
      if ctx.parametros():
        for param_ctx in ctx.parametros().parametro():
          nome_param = param_ctx.IDENT().getText()
          tipo_param = param_ctx.tipo_base().getText().replace("^", "") if param_ctx.tipo_base() else param_ctx.tipo_identificado().getText().replace("^", "")
          parametros.append((nome_param, tipo_param))
      self.procedimentos[nome_procedimento] = {'parametros': parametros}

    self.escopo_atual = 'procedimento'
    self.simbolos_locais = {}

    if ctx.parametros():
      for param_ctx in ctx.parametros().parametro():
        nome_param = param_ctx.IDENT().getText()
        tipo_param = param_ctx.tipo_base().getText().replace("^", "") if param_ctx.tipo_base() else param_ctx.tipo_identificado().getText().replace("^", "")
        self.simbolos_locais[nome_param] = tipo_param
        if tipo_param in self.tipos_definidos and tipo_param in self.campos_registro:
          self.campos_registro[nome_param] = self.campos_registro[tipo_param]

  def exitDeclaracao_procedimento(self, ctx:LAParser.Declaracao_procedimentoContext):
    # Restaura o escopo para o ambiente global ao finalizar o bloco do procedimento.
    self.escopo_atual = 'global'
    self.simbolos_locais = {}

  def enterRetorne(self, ctx:LAParser.RetorneContext):
    # Valida se a instrução de retorno está sendo chamada estritamente dentro de uma função.
    if self.escopo_atual != 'funcao':
      self.erros.append(f"Linha {ctx.start.line}: comando retorne nao permitido nesse escopo")
    self.tipo_expressao(ctx.expressao())

  def enterComandoenquanto(self, ctx: LAParser.ComandoenquantoContext):
    # Garante que a expressão condicional do laço de repetição seja avaliada.
    self.tipo_expressao(ctx.expressao())

  def enterComandose(self, ctx: LAParser.ComandoseContext):
    # Garante que a expressão de controle condicional do desvio seja avaliada.
    self.tipo_expressao(ctx.expressao())

  def enterLeitura(self, ctx:LAParser.LeituraContext):
    # Valida se todas as variáveis passadas no comando de entrada ('leia') foram devidamente declaradas.
    lista_ids = ctx.lista_identificadores()
    for child in lista_ids.children:
      if child.getText() == ',':
        continue
      if isinstance(child, LAParser.Acesso_campoContext):
        self.validar_acesso_campo(child)
      elif hasattr(LAParser, 'Acesso_arrayContext') and isinstance(child, LAParser.Acesso_arrayContext):
        self.validar_acesso_array(child)
      else:
        nome = child.getText()
        if nome not in self.simbolos_locais and nome not in self.simbolos:
          self.erros.append(f"Linha {self.linha_token(child.getSymbol())}: identificador {nome} nao declarado")

  def validar_acesso_campo(self, ctx):
    # Checa se o identificador e o membro de registro acessado no comando de leitura existem.
    if hasattr(ctx, 'IDENT') and ctx.IDENT():
      nome_var = ctx.IDENT(0).getText()
      nome_campo = ctx.IDENT(1).getText()

      if nome_var not in self.simbolos_locais and nome_var not in self.simbolos:
        self.erros.append(f"Linha {self.linha_token(ctx.IDENT(0).getSymbol())}: identificador {nome_var}.{nome_campo} nao declarado")
        return

      if nome_var in self.campos_registro:
        if nome_campo not in self.campos_registro[nome_var]:
          self.erros.append(f"Linha {self.linha_token(ctx.IDENT(1).getSymbol())}: identificador {nome_var}.{nome_campo} nao declarado")
      else:
        self.erros.append(f"Linha {self.linha_token(ctx.IDENT(1).getSymbol())}: identificador {nome_var}.{nome_campo} nao declarado")

  def validar_acesso_array(self, ctx):
    # Checa se o identificador do array acessado no comando de leitura existe e valida o índice.
    if hasattr(ctx, 'IDENT') and ctx.IDENT():
      nome_var = ctx.IDENT().getText()

      if nome_var not in self.simbolos_locais and nome_var not in self.simbolos:
        self.erros.append(f"Linha {self.linha_token(ctx.IDENT().getSymbol())}: identificador {nome_var} nao declarado")
        return
      self.tipo_expressao(ctx.expressao())

  def enterChamada_procedimento(self, ctx:LAParser.Chamada_procedimentoContext):
    # Valida a existência do procedimento e se os parâmetros fornecidos batem com sua assinatura.
    nome_procedimento = ctx.IDENT().getText()

    if nome_procedimento not in self.procedimentos:
      self.erros.append(f"Linha {ctx.start.line}: identificador {nome_procedimento} nao declarado")
      return

    info_procedimento = self.procedimentos[nome_procedimento]
    parametros_esperados = info_procedimento['parametros']
    parametros_passados = []

    if ctx.lista_expressao():
      for exp in ctx.lista_expressao().expressao():
        parametros_passados.append(self.tipo_expressao(exp))

    if len(parametros_passados) != len(parametros_esperados):
      self.erros.append(f"Linha {ctx.start.line}: incompatibilidade de parametros na chamada de {nome_procedimento}")
      return

    for i, (tipo_passado, (_, tipo_esperado)) in enumerate(zip(parametros_passados, parametros_esperados)):
      if tipo_passado and tipo_passado != tipo_esperado:
        self.erros.append(f"Linha {ctx.start.line}: incompatibilidade de parametros na chamada de {nome_procedimento}")
        break

  def enterEscrita(self, ctx:LAParser.EscritaContext):
    # Valida e checa os tipos de todas as expressões enviadas para a instrução de saída ('escreva').
    for exp in ctx.expressao():
      self.tipo_expressao(exp)

def main():
  if len(sys.argv) != 3:
    print("Uso: python3 analisador_semantico.py entrada.txt saida.txt")
    return

  arquivo_entrada = sys.argv[1]
  arquivo_saida = sys.argv[2]

  input_stream = FileStream(arquivo_entrada, encoding='utf-8')
  lexer = LALexer(input_stream)
  token_stream = CommonTokenStream(lexer)
  parser = LAParser(token_stream)
  tree = parser.programa()

  analisador = AnalisadorSemantico(token_stream)
  walker = ParseTreeWalker()
  walker.walk(analisador, tree)

  with open(arquivo_saida, 'w', encoding='utf-8') as f:
    for erro in analisador.erros:
      f.write(erro + '\n')
    f.write("Fim da compilacao\n")

if __name__ == "__main__":
  main()
