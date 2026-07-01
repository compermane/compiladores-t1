# Generated from DOTA2.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .DOTA2Parser import DOTA2Parser
else:
    from DOTA2Parser import DOTA2Parser

# This class defines a complete generic visitor for a parse tree produced by DOTA2Parser.

class DOTA2Visitor(ParseTreeVisitor):

    # Visit a parse tree produced by DOTA2Parser#programa.
    def visitPrograma(self, ctx:DOTA2Parser.ProgramaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DOTA2Parser#bloco_aliados.
    def visitBloco_aliados(self, ctx:DOTA2Parser.Bloco_aliadosContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DOTA2Parser#bloco_rivais.
    def visitBloco_rivais(self, ctx:DOTA2Parser.Bloco_rivaisContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DOTA2Parser#lista_herois.
    def visitLista_herois(self, ctx:DOTA2Parser.Lista_heroisContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DOTA2Parser#comandos.
    def visitComandos(self, ctx:DOTA2Parser.ComandosContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DOTA2Parser#comando.
    def visitComando(self, ctx:DOTA2Parser.ComandoContext):
        return self.visitChildren(ctx)



del DOTA2Parser