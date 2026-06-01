#!/usr/bin/env python3

import sys
import os
import subprocess
import re
import shutil
from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener
from LALexer import LALexer
from LAParser import LAParser
from LAListener import LAListener

TIPOS_VALIDOS = {'literal', 'inteiro', 'real', 'logico'}

REGEX_E_NAO_LETRAS = re.compile(r'(\W)e(\W)')
REGEX_E_INICIO = re.compile(r'^e(\W)')
REGEX_E_FIM = re.compile(r'(\W)e$')
REGEX_NUM_E_NUM = re.compile(r'(\d)e(\d)')
REGEX_FECHA_E_ABRE = re.compile(r'(\))e(\()')
REGEX_FECHA_E_PALAVRA = re.compile(r'(\))e(\w)')
REGEX_PALAVRA_E_ABRE = re.compile(r'(\w)e(\()')
REGEX_OU = re.compile(r'\bou\b')
REGEX_NAO = re.compile(r'\bnao\b')
REGEX_VAR_VAR = re.compile(r'(\w+)\s*=\s*(\w+)')
REGEX_VAR_NUM = re.compile(r'(\w+)\s*=\s*(\d+)')
REGEX_NUM_VAR = re.compile(r'(\d+)\s*=\s*(\w+)')
REGEX_NUM_NUM = re.compile(r'(\d+)\s*=\s*(\d+)')
REGEX_VERDADEIRO = re.compile(r'\bverdadeiro\b')
REGEX_FALSO = re.compile(r'\bfalso\b')
REGEX_IDENTIFICADORES = re.compile(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b')

SUBSTITUICOES_EXPRESSAO = [
    (REGEX_E_NAO_LETRAS, r'\1&&\2'),
    (REGEX_E_INICIO, r'&&\1'),
    (REGEX_E_FIM, r'\1&&'),
    (REGEX_NUM_E_NUM, r'\1 && \2'),
    (REGEX_FECHA_E_ABRE, r'\1 && \2'),
    (REGEX_FECHA_E_PALAVRA, r'\1 && \2'),
    (REGEX_PALAVRA_E_ABRE, r'\1 && \2'),
    (REGEX_OU, '||'),
    (REGEX_NAO, '!'),
    (REGEX_VAR_VAR, r'\1 == \2'),
    (REGEX_VAR_NUM, r'\1 == \2'),
    (REGEX_NUM_VAR, r'\1 == \2'),
    (REGEX_NUM_NUM, r'\1 == \2'),
    (REGEX_VERDADEIRO, '1'),
    (REGEX_FALSO, '0')
]

class MeuErroListener(ErrorListener):
  def __init__(self):
    super(MeuErroListener, self).__init__()
    self.erros = []

  def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
    simbolo = offendingSymbol.text
    if simbolo == "<EOF>":
      simbolo = "EOF"

    if hasattr(recognizer, 'symbolicNames'):
      if offendingSymbol.type == LALexer.CADEIA_NAO_FECHADA:
        self.erros.append(f"Linha {line}: cadeia literal nao fechada")
        return
      elif offendingSymbol.type == LALexer.CARACTERE_INVALIDO:
        self.erros.append(f"Linha {line}: {simbolo} - simbolo nao identificado")
        return
      elif offendingSymbol.type == LALexer.COMENTARIO_NAO_FECHADO:
        self.erros.append(f"Linha {line}: comentario nao fechado")
        return

    self.erros.append(f"Linha {line}: erro sintatico proximo a {simbolo}")

class AnalisadorSemantico(LAListener):
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

  def tipo_expressao(self, ctx):
    """Determina o tipo de uma expressão"""
    from LAParser import LAParser

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
        tipo_var = self.simbolos.get(nome) or self.simbolos_locais.get(nome)
        if tipo_var is None:
          token = ctx.IDENT().getSymbol()
          self.erros.append(f"Linha {token.line}: identificador {nome} nao declarado")
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
        t = self.tipo_expressao(ctx.fator())
        return 'logico' if t == 'logico' else None
      return None
    return None

  def eh_compativel(self, tipo_var, tipo_exp):
    return tipo_var == tipo_exp or (tipo_var == 'real' and tipo_exp == 'inteiro')

  def enterDeclaracao(self, ctx):
    """Processa declaração de variáveis"""
    for var_ctx in ctx.lista_variaveis().variavel():
      tipo_ctx = var_ctx.tipo()

      if hasattr(tipo_ctx, 'tipo_registro') and tipo_ctx.tipo_registro():
        nome_tipo_temp = f"registro_inline_{id(var_ctx)}"
        campos = {}

        for campo_ctx in tipo_ctx.tipo_registro().lista_campos().campo():
          tipo_campo = campo_ctx.tipo_base().getText()

          if tipo_campo not in TIPOS_VALIDOS and tipo_campo not in self.tipos_definidos:
            token_tipo = campo_ctx.tipo_base().start
            self.erros.append(f"Linha {token_tipo.line}: tipo {tipo_campo} nao declarado")
            continue

          for ident in campo_ctx.IDENT():
            campos[ident.getText()] = tipo_campo

        self.tipos_definidos[nome_tipo_temp] = 'registro'
        self.campos_registro[nome_tipo_temp] = campos
        tipo_texto = nome_tipo_temp
      else:
        tipo_texto = tipo_ctx.getText().replace("^", "")

        if tipo_texto not in TIPOS_VALIDOS and tipo_texto not in self.tipos_definidos:
          token_tipo = tipo_ctx.start
          self.erros.append(f"Linha {token_tipo.line}: tipo {tipo_texto} nao declarado")

      variable_names = self.extract_variable_names(var_ctx)

      for nome_var in variable_names:
        if nome_var in self.simbolos or nome_var in self.simbolos_locais:
          for i in range(var_ctx.getChildCount()):
            child = var_ctx.getChild(i)
            if hasattr(child, 'getText') and child.getText() == nome_var:
              if hasattr(child, 'getSymbol'):
                token_var = child.getSymbol()
                self.erros.append(f"Linha {token_var.line}: identificador {nome_var} ja declarado")
              break
        else:
          if self.escopo_atual == 'global':
            self.simbolos[nome_var] = tipo_texto
          else:
            self.simbolos_locais[nome_var] = tipo_texto

  def extract_variable_names(self, var_ctx):
    """Extrai nomes de variáveis do contexto"""
    variable_names = []
    children = [var_ctx.getChild(i) for i in range(var_ctx.getChildCount())]

    i = 0
    while i < len(children):
      child = children[i]
      if hasattr(child, 'getSymbol') and child.getSymbol().type == LALexer.IDENT:
        if i + 1 < len(children) and hasattr(children[i + 1], 'getText') and children[i + 1].getText() == '[':
          variable_names.append(child.getText())
          i += 3
        elif i > 0 and hasattr(children[i - 1], 'getText') and children[i - 1].getText() == '[':
          i += 1
        elif hasattr(children[i - 1], 'getText') and children[i - 1].getText() in ['[', ']']:
          i += 1
        else:
          variable_names.append(child.getText())
          i += 1
      else:
        i += 1
    return variable_names

  def enterAtribuicao(self, ctx):
    """Verifica atribuições"""
    lado_esquerdo = ctx.getChild(0)

    if hasattr(lado_esquerdo, 'getRuleIndex'):
      from LAParser import LAParser
      if lado_esquerdo.getRuleIndex() == LAParser.RULE_acesso_campo:
        return
      elif lado_esquerdo.getRuleIndex() == LAParser.RULE_acesso_array:
        if hasattr(lado_esquerdo, 'IDENT'):
          nome_array = lado_esquerdo.IDENT().getText()
          tipo_var = self.simbolos.get(nome_array) or self.simbolos_locais.get(nome_array)
          if tipo_var is None:
            token_var = lado_esquerdo.IDENT().getSymbol()
            self.erros.append(f"Linha {token_var.line}: identificador {nome_array} nao declarado")
        return

    if hasattr(lado_esquerdo, 'getSymbol') and lado_esquerdo.getSymbol().text == '^':
      nome_var = ctx.getChild(1).getText() if ctx.getChildCount() > 1 and hasattr(ctx.getChild(1), 'getText') else ""
    else:
      lado_esquerdo_texto = lado_esquerdo.getText()
      if '[' in lado_esquerdo_texto and ']' in lado_esquerdo_texto:
        nome_var = lado_esquerdo_texto.split('[')[0]
      elif '.' in lado_esquerdo_texto:
        return
      elif lado_esquerdo_texto.startswith('^') or lado_esquerdo_texto.startswith('&'):
        nome_var = lado_esquerdo_texto[1:]
      else:
        nome_var = lado_esquerdo_texto

    if nome_var:
      tipo_var = self.simbolos.get(nome_var) or self.simbolos_locais.get(nome_var)
      if tipo_var is None:
        token_var = lado_esquerdo.getSymbol() if hasattr(lado_esquerdo, 'getSymbol') else (ctx.getChild(1).getSymbol() if ctx.getChildCount() > 1 and hasattr(ctx.getChild(1), 'getSymbol') else None)
        if token_var:
          self.erros.append(f"Linha {token_var.line}: identificador {nome_var} nao declarado")

      tipo_exp = self.tipo_expressao(ctx.expressao())
      if tipo_var is not None and tipo_exp is not None and not self.eh_compativel(tipo_var, tipo_exp):
        token_var = lado_esquerdo.getSymbol() if hasattr(lado_esquerdo, 'getSymbol') else (ctx.getChild(1).getSymbol() if ctx.getChildCount() > 1 and hasattr(ctx.getChild(1), 'getSymbol') else None)
        if token_var:
          self.erros.append(f"Linha {token_var.line}: atribuicao nao compativel para {nome_var}")

  def enterLeitura(self, ctx):
    """Verifica comando leia"""
    lista_ids = ctx.lista_identificadores()
    for child in lista_ids.children:
      if hasattr(child, 'getText') and child.getText() != ',':
        nome = child.getText()
        if nome not in self.simbolos and nome not in self.simbolos_locais:
          if hasattr(child, 'getSymbol'):
            token_id = child.getSymbol()
            self.erros.append(f"Linha {token_id.line}: identificador {nome} nao declarado")

  def enterEscrita(self, ctx):
    """Verifica comando escreva"""
    for exp in ctx.expressao():
      self.tipo_expressao(exp)

  def enterDeclaracao_procedimento(self, ctx):
    """Processa declaração de procedimento para análise semântica"""
    nome = ctx.IDENT().getText()
    self.procedimentos[nome] = {'parametros': []}

    if ctx.parametros():
      for param_ctx in ctx.parametros().parametro():
        param_nome = param_ctx.IDENT().getText()
        param_tipo = param_ctx.tipo_base().getText() if param_ctx.tipo_base() else param_ctx.tipo_identificado().getText()
        self.procedimentos[nome]['parametros'].append((param_nome, param_tipo))
        self.simbolos_locais[param_nome] = param_tipo

    self.escopo_atual = nome

  def exitDeclaracao_procedimento(self, ctx):
    self.escopo_atual = 'global'
    self.simbolos_locais.clear()

  def enterChamada_procedimento(self, ctx):
    """Verifica chamada de procedimento"""
    nome = ctx.IDENT().getText()

    if nome not in self.procedimentos:
      token = ctx.IDENT().getSymbol()
      self.erros.append(f"Linha {token.line}: identificador {nome} nao declarado")
      return

    num_args = len(ctx.lista_expressao().expressao()) if ctx.lista_expressao() else 0
    num_params = len(self.procedimentos[nome]['parametros'])
    if num_args != num_params:
      token = ctx.IDENT().getSymbol()
      self.erros.append(f"Linha {token.line}: incompatibilidade de parametros na chamada de {nome}")

  def enterDeclaracao_tipo(self, ctx):
    """Processa declarações de tipo (registros)"""
    nome_tipo = ctx.IDENT().getText()

    if nome_tipo in self.tipos_definidos:
      token = ctx.IDENT().getSymbol()
      self.erros.append(f"Linha {token.line}: tipo {nome_tipo} ja declarado")
      return

    if len(ctx.children) >= 4:
      tipo_def = ctx.children[3]

      if hasattr(tipo_def, 'lista_campos'):
        campos = {}
        for campo_ctx in tipo_def.lista_campos().campo():
          tipo_campo = campo_ctx.tipo_base().getText()

          if tipo_campo not in TIPOS_VALIDOS and tipo_campo not in self.tipos_definidos:
            token_tipo = campo_ctx.tipo_base().start
            self.erros.append(f"Linha {token_tipo.line}: tipo {tipo_campo} nao declarado")
            continue

          for ident in campo_ctx.IDENT():
            campos[ident.getText()] = tipo_campo

        self.tipos_definidos[nome_tipo] = 'registro'
        self.campos_registro[nome_tipo] = campos
      else:
        tipo_base = tipo_def.getText()
        if tipo_base not in TIPOS_VALIDOS and tipo_base not in self.tipos_definidos:
          token_tipo = tipo_def.start
          self.erros.append(f"Linha {token_tipo.line}: tipo {tipo_base} nao declarado")
        else:
          self.tipos_definidos[nome_tipo] = tipo_base

  def enterAcesso_campo(self, ctx):
    """Verifica acesso a campos de registro"""
    acesso_texto = ctx.getText()
    partes = acesso_texto.split('.')

    if len(partes) >= 2:
      nome_var, nome_campo = partes[0], partes[1]

      tipo_var = self.simbolos.get(nome_var) or self.simbolos_locais.get(nome_var)
      if tipo_var is None:
        self.erros.append(f"Linha {ctx.start.line}: identificador {nome_var} nao declarado")
        return

      if tipo_var not in self.campos_registro:
        self.erros.append(f"Linha {ctx.start.line}: {nome_var} nao e do tipo registro")
        return

      if nome_campo not in self.campos_registro[tipo_var]:
        self.erros.append(f"Linha {ctx.start.line}: campo {nome_campo} nao existe no registro {tipo_var}")

  def enterAcesso_array(self, ctx):
    """Verifica acesso a arrays"""
    nome_array = ctx.IDENT().getText()

    tipo_var = self.simbolos.get(nome_array) or self.simbolos_locais.get(nome_array)
    if tipo_var is None:
      token = ctx.IDENT().getSymbol()
      self.erros.append(f"Linha {token.line}: identificador {nome_array} nao declarado")
      return

    tipo_indice = self.tipo_expressao(ctx.expressao())
    if tipo_indice is not None and tipo_indice != 'inteiro':
      self.erros.append(f"Linha {ctx.start.line}: indice de array deve ser inteiro")

class GeradorCodigo(LAListener):
  def __init__(self):
    self.codigo = []
    self.declaracoes = []
    self.defines = []
    self.tipos_structs = []
    self.funcoes = []
    self.procedimentos = []
    self.tabela_simbolos = {}
    self.escopo_atual = 'global'
    self.em_funcao = False
    self.em_procedimento = False
    self.nivel_escopo = 0
    self.constantes = {}
    self.contextos_processados = set()
    self.bloqueando_automatico = False

  def adicionar_codigo(self, linha, indent=0):
    linha_formatada = '\t' * indent + linha
    if self.em_funcao:
      self.funcoes.append(linha_formatada)
    elif self.em_procedimento:
      self.procedimentos.append(linha_formatada)
    else:
      self.codigo.append(linha_formatada)

  def adicionar_declaracao(self, linha):
    self.declaracoes.append('\t' + linha)

  def traduzir_tipo(self, tipo_la, eh_parametro=False):
    tipos = {
        'inteiro': 'int',
        'real': 'float',
        'literal': 'char*' if eh_parametro else 'char',
        'logico': 'int'
    }

    if tipo_la.startswith('^'):
      tipo_base = tipo_la[1:]
      if tipo_base in tipos:
        base_tipo = tipos[tipo_base]
        return 'char**' if tipo_base == 'literal' and eh_parametro else base_tipo + '*'
      return tipo_base + '*'
    return tipos.get(tipo_la, tipo_la)

  def obter_formato_printf(self, tipo):
    formatos = {'int': '%d', 'float': '%f', 'char': '%s', 'char*': '%s'}
    return formatos.get(tipo, '%d')

  def exitPrograma(self, ctx):
    """Fim do programa - gera código completo"""
    codigo_final = ['#include <stdio.h>', '#include <stdlib.h>', '#include <string.h>', '']

    codigo_final.extend(self.defines)
    if self.defines:
      codigo_final.append('')

    codigo_final.extend(self.tipos_structs)
    if self.tipos_structs:
      codigo_final.append('')

    codigo_final.extend(self.funcoes)
    codigo_final.extend(self.procedimentos)

    codigo_final.append('int main() {')
    codigo_final.extend(self.declaracoes)
    codigo_final.extend(self.codigo)
    codigo_final.append('\treturn 0;')
    codigo_final.append('}')

    self.codigo = codigo_final

  def enterDeclaracao(self, ctx):
    if not self.em_funcao and not self.em_procedimento:
      self.processar_declaracao_variaveis(ctx.lista_variaveis())

  def enterDeclaracao_constante(self, ctx):
    nome_constante = ctx.IDENT().getText()
    valor_constante = ctx.valor_constante()

    if valor_constante.NUM_INT():
      valor = int(valor_constante.NUM_INT().getText())
    elif valor_constante.NUM_REAL():
      valor = float(valor_constante.NUM_REAL().getText())
    elif valor_constante.CADEIA():
      valor = valor_constante.CADEIA().getText()
    elif valor_constante.getText() == 'verdadeiro':
      valor = 1
    elif valor_constante.getText() == 'falso':
      valor = 0
    else:
      valor = valor_constante.getText()

    self.constantes[nome_constante] = valor
    self.defines.append(f'#define {nome_constante} {valor}')

  def enterDeclaracao_tipo(self, ctx):
    nome_tipo = ctx.IDENT().getText()

    if ctx.tipo_registro():
      campos = []
      for campo_ctx in ctx.tipo_registro().lista_campos().campo():
        tipo_campo_c = self.traduzir_tipo(campo_ctx.tipo_base().getText())

        for ident in campo_ctx.IDENT():
          nome_campo = ident.getText()
          if tipo_campo_c == 'char':
            campos.append(f'\t{tipo_campo_c} {nome_campo}[80];')
          else:
            campos.append(f'\t{tipo_campo_c} {nome_campo};')

      struct_def = f'typedef struct {{\n' + '\n'.join(campos) + f'\n}} {nome_tipo};'
      self.tipos_structs.append(struct_def)

    elif ctx.tipo_identificado():
      tipo_base = self.traduzir_tipo(ctx.tipo_identificado().getText())
      self.tipos_structs.append(f'typedef {tipo_base} {nome_tipo};')

  def processar_declaracao_variaveis(self, ctx_lista):
    for variavel_ctx in ctx_lista.variavel():
      tipo_ctx = variavel_ctx.tipo()
      tipo_c = self.processar_tipo(tipo_ctx)
      nome = variavel_ctx.IDENT(0).getText()

      if variavel_ctx.ABRE_COLCHETE():
        tamanho = variavel_ctx.NUM_INT(0).getText() if variavel_ctx.NUM_INT() else variavel_ctx.IDENT(1).getText()
        suffix = f'[{tamanho}]' if tipo_c != 'char' else '[80]'
        self.adicionar_declaracao(f'{tipo_c} {nome}{suffix};')
      else:
        suffix = '[80]' if tipo_c == 'char' else ''
        self.adicionar_declaracao(f'{tipo_c} {nome}{suffix};')

      self.tabela_simbolos[nome] = tipo_c

      for i in range(1, len(variavel_ctx.IDENT())):
        nome_extra = variavel_ctx.IDENT(i).getText()
        suffix_extra = '[80]' if tipo_c == 'char' else ''
        self.adicionar_declaracao(f'{tipo_c} {nome_extra}{suffix_extra};')
        self.tabela_simbolos[nome_extra] = tipo_c

  def processar_tipo(self, ctx_tipo):
    if hasattr(ctx_tipo, 'tipo_registro') and ctx_tipo.tipo_registro():
      campos = []
      for campo_ctx in ctx_tipo.tipo_registro().lista_campos().campo():
        tipo_campo_c = self.traduzir_tipo(campo_ctx.tipo_base().getText())

        for ident in campo_ctx.IDENT():
          nome_campo = ident.getText()
          if tipo_campo_c == 'char':
            campos.append(f'\t{tipo_campo_c} {nome_campo}[80];')
          else:
            campos.append(f'\t{tipo_campo_c} {nome_campo};')

      return 'struct {\n' + '\n'.join(campos) + '\n}'

    return self.traduzir_tipo(ctx_tipo.getText())

  def enterDeclaracao_funcao(self, ctx):
    self.em_funcao = True
    nome = ctx.IDENT().getText()
    tipo_retorno = self.traduzir_tipo(ctx.tipo_base().getText())

    parametros = []
    if ctx.parametros():
      for param_ctx in ctx.parametros().parametro():
        param_nome = param_ctx.IDENT().getText()
        param_tipo = self.traduzir_tipo(param_ctx.tipo_base().getText() if param_ctx.tipo_base() else param_ctx.tipo_identificado().getText(), eh_parametro=True)
        parametros.append(f'{param_tipo} {param_nome}')
        self.tabela_simbolos[param_nome] = param_tipo.replace('*', '')

    params_str = ', '.join(parametros) if parametros else ''
    self.funcoes.append(f'{tipo_retorno} {nome}({params_str}) {{')

    self.declaracoes_temp = self.declaracoes
    self.declaracoes = []

    if ctx.declaracoes_locais():
      for decl_ctx in ctx.declaracoes_locais().lista_variaveis():
        self.processar_declaracao_variaveis(decl_ctx)

  def exitDeclaracao_funcao(self, ctx):
    self.funcoes.extend(self.declaracoes)
    self.funcoes.append('}')
    self.funcoes.append('')
    self.declaracoes = self.declaracoes_temp
    self.em_funcao = False

  def enterDeclaracao_procedimento(self, ctx):
    self.em_procedimento = True
    nome = ctx.IDENT().getText()

    parametros = []
    if ctx.parametros():
      for param_ctx in ctx.parametros().parametro():
        param_nome = param_ctx.IDENT().getText()
        param_tipo = self.traduzir_tipo(param_ctx.tipo_base().getText() if param_ctx.tipo_base() else param_ctx.tipo_identificado().getText(), eh_parametro=True)
        parametros.append(f'{param_tipo} {param_nome}')
        self.tabela_simbolos[param_nome] = param_tipo.replace('*', '')

    params_str = ', '.join(parametros) if parametros else ''
    self.procedimentos.append(f'void {nome}({params_str}) {{')

    self.declaracoes_temp = self.declaracoes
    self.declaracoes = []

    if ctx.declaracoes_locais():
      for decl_ctx in ctx.declaracoes_locais().lista_variaveis():
        self.processar_declaracao_variaveis(decl_ctx)

  def exitDeclaracao_procedimento(self, ctx):
    self.procedimentos.extend(self.declaracoes)
    self.procedimentos.append('}')
    self.procedimentos.append('')
    self.declaracoes = self.declaracoes_temp
    self.em_procedimento = False

  def enterChamada_procedimento(self, ctx):
    nome = ctx.IDENT().getText()

    argumentos = []
    if ctx.lista_expressao():
      for expr_ctx in ctx.lista_expressao().expressao():
        argumentos.append(self.processar_expressao(expr_ctx))

    args_str = ', '.join(argumentos) if argumentos else ''
    linha = f'{nome}({args_str});'

    if self.em_funcao:
      self.funcoes.append(f'\t{linha}')
    elif self.em_procedimento:
      self.procedimentos.append(f'\t{linha}')
    else:
      self.adicionar_codigo(linha, 1)

  def enterRetorne(self, ctx):
    expressao = self.processar_expressao(ctx.expressao())
    if self.em_funcao:
      self.funcoes.append(f'\treturn {expressao};')
    else:
      self.adicionar_codigo(f'return {expressao};', 1)

  def enterLeitura(self, ctx):
    if self.bloqueando_automatico:
      return

    for ident_ctx in ctx.lista_identificadores().children:
      if hasattr(ident_ctx, 'getText') and ident_ctx.getText() != ',':
        nome = ident_ctx.getText()
        tipo = self.tabela_simbolos.get(nome, 'int')
        formato = self.obter_formato_printf(tipo)

        if tipo == 'char':
          self.adicionar_codigo(f'fgets({nome}, 80, stdin);', 1)
          self.adicionar_codigo(f'{nome}[strcspn({nome}, "\\n")] = \'\\0\';', 1)
        else:
          self.adicionar_codigo(f'scanf("{formato}",&{nome});', 1)

  def enterEscrita(self, ctx):
    ctx_id = (id(ctx), ctx.start.line, ctx.start.column)
    if ctx_id in self.contextos_processados or (hasattr(self, 'bloqueando_automatico') and self.bloqueando_automatico):
      return

    expressoes = []
    formatos = []

    for expr_ctx in ctx.expressao():
      expr_text = self.processar_expressao(expr_ctx)

      if expr_text.startswith('"') and expr_text.endswith('"'):
        formatos.append('%s')
        expressoes.append(expr_text)
      elif '.' in expr_text:
        partes = expr_text.split('.')
        if len(partes) == 2:
          nome_campo = partes[1].lower()
          if 'nome' in nome_campo or 'titulo' in nome_campo or 'descricao' in nome_campo:
            formatos.append('%s')
          elif 'idade' in nome_campo or 'numero' in nome_campo or 'valor' in nome_campo:
            formatos.append('%d')
          else:
            formatos.append('%s')
        else:
          formatos.append('%s')
        expressoes.append(expr_text)
      elif expr_text in self.tabela_simbolos:
        tipo = self.tabela_simbolos[expr_text]
        formatos.append(self.obter_formato_printf(tipo))
        expressoes.append(expr_text)
      elif expr_text in self.constantes:
        valor = self.constantes[expr_text]
        formatos.append('%d' if str(valor).isdigit() else '%s')
        expressoes.append(str(valor))
      else:
        if expr_text.replace('.','').replace('-','').isdigit() and '.' in expr_text:
          formatos.append('%f')
          expressoes.append(expr_text)
        elif expr_text.replace('-','').isdigit():
          formatos.append('%d')
          expressoes.append(expr_text)
        else:
          formatos.append(self.inferir_tipo_expressao(expr_text))
          expressoes.append(expr_text)

    formato_str = ''.join(formatos)
    linha = f'printf("{formato_str}",{",".join(expressoes)});' if expressoes else f'printf("{formato_str}");'
    self.adicionar_codigo(linha, 1)

  def inferir_tipo_expressao(self, expr_text):
    identificadores = REGEX_IDENTIFICADORES.findall(expr_text)
    tem_real = any(self.tabela_simbolos.get(ident, '') == 'float' for ident in identificadores)
    return '%f' if tem_real else '%d'

  def enterAtribuicao(self, ctx):
    if self.bloqueando_automatico:
      return

    var = '*' + ctx.getChild(1).getText() if ctx.getChildCount() >= 3 and ctx.getChild(0).getText() == '^' else ctx.children[0].getText()
    expr = self.processar_expressao(ctx.expressao())
    linha = f'strcpy({var}, {expr});' if '.' in var and expr.startswith('"') and expr.endswith('"') else f'{var} = {expr};'
    self.adicionar_codigo(linha, 1)

  def enterComandose(self, ctx):
    self.bloqueando_automatico = True
    condicao = self.processar_expressao(ctx.expressao())

    dest = self.funcoes if self.em_funcao else (self.procedimentos if self.em_procedimento else None)
    if dest is not None:
      dest.append(f'\tif ({condicao}) {{')
    else:
      self.adicionar_codigo(f'if ({condicao}) {{', 1)

    for comando in ctx.comandos(0).comando():
      self.processar_comando_manual(comando)

    if len(ctx.comandos()) > 1:
      if dest is not None:
        dest.append('\t} else {')
      else:
        self.adicionar_codigo('} else {', 1)

      for comando in ctx.comandos(1).comando():
        self.processar_comando_manual(comando)

    if dest is not None:
      dest.append('\t}')
    else:
      self.adicionar_codigo('}', 1)

    self.bloqueando_automatico = False

  def enterComandocaso(self, ctx):
    if not hasattr(self, 'contextos_processados'):
      self.contextos_processados = set()
    self.contextos_processados.add(ctx)

    expr_result = self.processar_expressao(ctx.expressao())
    dest = self.funcoes if self.em_funcao else (self.procedimentos if self.em_procedimento else None)

    if dest is not None:
      dest.append(f'\tswitch ({expr_result}) {{')
    else:
      self.adicionar_codigo(f'switch ({expr_result}) {{', 1)

    for selecao in ctx.selecao():
      self.processar_selecao(selecao)

    if ctx.comandos():
      if dest is not None:
        dest.append('\t\tdefault:')
      else:
        self.adicionar_codigo('default:', 2)

      for comando in ctx.comandos().comando():
        self.processar_comando_manual(comando)

      if dest is not None:
        dest.append('\t\t\tbreak;')
      else:
        self.adicionar_codigo('break;', 3)

    if dest is not None:
      dest.append('\t}')
    else:
      self.adicionar_codigo('}', 1)

  def processar_selecao(self, selecao_ctx):
    constantes = selecao_ctx.constantes()
    dest = self.funcoes if self.em_funcao else (self.procedimentos if self.em_procedimento else None)

    for constante in constantes.constante():
      if constante.NUM_INT():
        if len(constante.NUM_INT()) == 1:
          valor = constante.NUM_INT(0).getText()
          if dest is not None:
            dest.append(f'\t\tcase {valor}:')
          else:
            self.adicionar_codigo(f'case {valor}:', 2)
        else:
          inicio = int(constante.NUM_INT(0).getText())
          fim = int(constante.NUM_INT(1).getText())
          for valor in range(inicio, fim + 1):
            if dest is not None:
              dest.append(f'\t\tcase {valor}:')
            else:
              self.adicionar_codigo(f'case {valor}:', 2)

    for comando in selecao_ctx.comandos().comando():
      self.processar_comando_manual(comando)

    if dest is not None:
      dest.append('\t\t\tbreak;')
    else:
      self.adicionar_codigo('break;', 3)

  def processar_comando_manual(self, comando_ctx):
    if comando_ctx.escrita():
      self.processar_escrita_manual(comando_ctx.escrita())
    elif comando_ctx.leitura():
      self.processar_leitura_manual(comando_ctx.leitura())
    elif comando_ctx.atribuicao():
      self.processar_atribuicao_manual(comando_ctx.atribuicao())

  def processar_escrita_manual(self, ctx):
    ctx_id = (id(ctx), ctx.start.line, ctx.start.column)
    self.contextos_processados.add(ctx_id)

    expressoes = []
    formatos = []

    for expr_ctx in ctx.expressao():
      expr_text = self.processar_expressao(expr_ctx)

      if expr_text.startswith('"') and expr_text.endswith('"'):
        formatos.append('%s')
        expressoes.append(expr_text)
      elif expr_text in self.tabela_simbolos:
        tipo = self.tabela_simbolos[expr_text]
        formatos.append(self.obter_formato_printf(tipo))
        expressoes.append(expr_text)
      elif expr_text in self.constantes:
        valor = self.constantes[expr_text]
        formatos.append('%d' if str(valor).isdigit() else '%s')
        expressoes.append(str(valor))
      else:
        if expr_text.replace('.','').replace('-','').isdigit() and '.' in expr_text:
          formatos.append('%f')
          expressoes.append(expr_text)
        elif expr_text.replace('-','').isdigit():
          formatos.append('%d')
          expressoes.append(expr_text)
        else:
          formatos.append(self.inferir_tipo_expressao(expr_text))
          expressoes.append(expr_text)

    formato_str = ''.join(formatos)
    linha = f'printf("{formato_str}",{",".join(expressoes)});' if expressoes else f'printf("{formato_str}");'

    if self.em_funcao:
      self.funcoes.append(f'\t\t{linha}')
    elif self.em_procedimento:
      self.procedimentos.append(f'\t\t{linha}')
    else:
      self.adicionar_codigo(linha, 2)

  def processar_leitura_manual(self, ctx):
    for ident_ctx in ctx.lista_identificadores().children:
      if hasattr(ident_ctx, 'getText') and ident_ctx.getText() != ',':
        nome = ident_ctx.getText()
        tipo = self.tabela_simbolos.get(nome, 'int')
        formato = self.obter_formato_printf(tipo)

        if tipo == 'char':
          linha = f'fgets({nome}, 80, stdin);'
          if self.em_funcao:
            self.funcoes.append(f'\t\t{linha}')
            self.funcoes.append(f'\t\t{nome}[strcspn({nome}, "\\n")] = \'\\0\';')
          elif self.em_procedimento:
            self.procedimentos.append(f'\t\t{linha}')
            self.procedimentos.append(f'\t\t{nome}[strcspn({nome}, "\\n")] = \'\\0\';')
          else:
            self.adicionar_codigo(linha, 2)
            self.adicionar_codigo(f'{nome}[strcspn({nome}, "\\n")] = \'\\0\';', 2)
        else:
          linha = f'scanf("{formato}",&{nome});'
          if self.em_funcao:
            self.funcoes.append(f'\t\t{linha}')
          elif self.em_procedimento:
            self.procedimentos.append(f'\t\t{linha}')
          else:
            self.adicionar_codigo(linha, 2)

  def processar_atribuicao_manual(self, ctx):
    var = '*' + ctx.getChild(1).getText() if ctx.getChildCount() >= 3 and ctx.getChild(0).getText() == '^' else ctx.children[0].getText()
    expr = self.processar_expressao(ctx.expressao())
    linha = f'{var} = {expr};'

    if self.em_funcao:
      self.funcoes.append(f'\t\t{linha}')
    elif self.em_procedimento:
      self.procedimentos.append(f'\t\t{linha}')
    else:
      self.adicionar_codigo(linha, 2)

  def exitComandose(self, ctx):
    pass

  def enterComandopara(self, ctx):
    var = ctx.IDENT().getText()
    inicio = self.processar_expressao(ctx.expressao(0))
    fim = self.processar_expressao(ctx.expressao(1))
    linha = f'for ({var} = {inicio}; {var} <= {fim}; {var}++) {{'

    if self.em_funcao:
      self.funcoes.append(f'\t{linha}')
    elif self.em_procedimento:
      self.procedimentos.append(f'\t{linha}')
    else:
      self.adicionar_codigo(linha, 1)
    self.nivel_escopo += 1

  def exitComandopara(self, ctx):
    self.nivel_escopo -= 1
    if self.em_funcao:
      self.funcoes.append('\t}')
    elif self.em_procedimento:
      self.procedimentos.append('\t}')
    else:
      self.adicionar_codigo('}', 1)

  def enterComandoenquanto(self, ctx):
    condicao = self.processar_expressao(ctx.expressao())
    linha = f'while ({condicao}) {{'

    if self.em_funcao:
      self.funcoes.append(f'\t{linha}')
    elif self.em_procedimento:
      self.procedimentos.append(f'\t{linha}')
    else:
      self.adicionar_codigo(linha, 1)
    self.nivel_escopo += 1

  def exitComandoenquanto(self, ctx):
    self.nivel_escopo -= 1
    if self.em_funcao:
      self.funcoes.append('\t}')
    elif self.em_procedimento:
      self.procedimentos.append('\t}')
    else:
      self.adicionar_codigo('}', 1)

  def enterComandofaca(self, ctx):
    if self.em_funcao:
      self.funcoes.append('\tdo {')
    elif self.em_procedimento:
      self.procedimentos.append('\tdo {')
    else:
      self.adicionar_codigo('do {', 1)
    self.nivel_escopo += 1

  def exitComandofaca(self, ctx):
    self.nivel_escopo -= 1
    condicao = self.processar_expressao(ctx.expressao())

    if self.em_funcao:
      self.funcoes.append(f'\t}} while ({condicao});')
    elif self.em_procedimento:
      self.procedimentos.append(f'\t}} while ({condicao});')
    else:
      self.adicionar_codigo(f'}} while ({condicao});', 1)

  def processar_expressao(self, ctx):
    """Processa expressão e retorna código C (Melhorado estruturalmente)"""
    if not ctx:
      return ""

    texto = ctx.getText()
    if texto.startswith('"') and texto.endswith('"'):
      return texto

    # Loops de substituição unificados mapeados (Clarity & Clean code)
    for regex, substituicao in SUBSTITUICOES_EXPRESSAO:
      texto = regex.sub(substituicao, texto)

    texto = texto.replace('<>', '!=')

    for const_nome, const_valor in self.constantes.items():
      texto = re.sub(r'\b' + re.escape(const_nome) + r'\b', str(const_valor), texto)

    return texto

def main():
  if len(sys.argv) != 3:
    print("Uso: python compilador.py <arquivo_entrada> <arquivo_saida>")
    sys.exit(1)

  arquivo_entrada = sys.argv[1]
  arquivo_saida = sys.argv[2]

  # Cláusula utilitária para centralizar a saída de erros (Evita repetição de código)
  def gravar_erro_e_sair(erros_list):
    with open(arquivo_saida, 'w', encoding='utf-8') as f:
      for erro in erros_list:
        f.write(erro + '\n')
      f.write("Fim da compilacao\n")

  try:
    input_stream = FileStream(arquivo_entrada, encoding='utf-8')
    lexer = LALexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = LAParser(token_stream)

    erro_listener = MeuErroListener()
    lexer.removeErrorListeners()
    lexer.addErrorListener(erro_listener)
    parser.removeErrorListeners()
    parser.addErrorListener(erro_listener)

    tree = parser.programa()

    if erro_listener.erros:
      gravar_erro_e_sair(erro_listener.erros)
      return

    walker = ParseTreeWalker()

    analisador_semantico = AnalisadorSemantico(token_stream)
    walker.walk(analisador_semantico, tree)

    if analisador_semantico.erros:
      gravar_erro_e_sair(analisador_semantico.erros)
      return

    gerador = GeradorCodigo()
    walker.walk(gerador, tree)

    with open(arquivo_saida, 'w', encoding='utf-8') as f:
      for linha in gerador.codigo:
        f.write(linha + '\n')

    # Validação do GCC modificada para evitar exceção de subprocesso indisponível
    if arquivo_saida.endswith('.c') and shutil.which('gcc'):
      arquivo_executavel = arquivo_saida.rsplit('.c', 1)[0] + '.out'
      resultado = subprocess.run(['gcc', arquivo_saida, '-o', arquivo_executavel],
                               capture_output=True, text=True)
      if resultado.returncode != 0:
        with open(arquivo_saida, 'w', encoding='utf-8') as f:
          f.write(f"Erro na compilacao: {resultado.stderr}\n")
          f.write("Fim da compilacao\n")

  except Exception as e:
    gravar_erro_e_sair([f"Erro durante a compilacao: {str(e)}"])

if __name__ == '__main__':
  main()
