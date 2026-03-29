from typing import List

KEYWORDS: List[str] = [
    "algoritmo",
    "fim_algoritmo",
    "declare",
    "leia",
    "escreva",
    # Tipos
    "literal",
    "inteiro",
    "real",
    "logico",
    "constante",
    "verdadeiro",
    "falso",
    # Controle de fluxo
    "se",
    "entao",
    "senao",
    "fim_se",
    "caso",
    "seja",
    "fim_caso",
    # Laços
    "para",
    "ate",
    "faca",
    "fim_para",
    "enquanto",
    "fim_enquanto",
    # Declarações
    "registro",
    "fim_registro",
    "tipo",
    "var",
    "procedimento",
    "funcao",
    "retorne",
    "fim_procedimento",
    "fim_funcao",
    # Lógicos
    "e",
    "ou",
    "nao"
]

TOKEN_REGEX: List[str] = [
    # (r'\{[^\n]*\}', None),
    (r'"[^"\n]*"', "CADEIA"),
    (r'\d+\.\d+', "NUM_REAL"),
    (r'\d+', "NUM_INT"),
    (r'[a-zA-Z_]\w*', "IDENT_OR_KEYWORD"),
    (r'<-|<=|>=|<>|!=|==|\.\.', "SYMBOL"),
    (r'[:(),.+\-*/=<>.^&%[\]]', "SYMBOL"),
]
