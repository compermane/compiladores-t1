# Generated from DOTA2.g4 by ANTLR 4.13.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,12,53,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,1,0,1,
        0,1,0,1,0,1,0,1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,2,1,2,1,2,1,2,1,2,1,
        3,1,3,1,3,5,3,33,8,3,10,3,12,3,36,9,3,1,4,5,4,39,8,4,10,4,12,4,42,
        9,4,1,5,1,5,1,5,1,5,1,5,1,5,1,5,3,5,51,8,5,1,5,0,0,6,0,2,4,6,8,10,
        0,0,49,0,12,1,0,0,0,2,19,1,0,0,0,4,24,1,0,0,0,6,29,1,0,0,0,8,40,
        1,0,0,0,10,50,1,0,0,0,12,13,5,1,0,0,13,14,3,2,1,0,14,15,3,4,2,0,
        15,16,3,8,4,0,16,17,5,6,0,0,17,18,5,0,0,1,18,1,1,0,0,0,19,20,5,2,
        0,0,20,21,5,7,0,0,21,22,3,6,3,0,22,23,5,9,0,0,23,3,1,0,0,0,24,25,
        5,3,0,0,25,26,5,7,0,0,26,27,3,6,3,0,27,28,5,9,0,0,28,5,1,0,0,0,29,
        34,5,10,0,0,30,31,5,8,0,0,31,33,5,10,0,0,32,30,1,0,0,0,33,36,1,0,
        0,0,34,32,1,0,0,0,34,35,1,0,0,0,35,7,1,0,0,0,36,34,1,0,0,0,37,39,
        3,10,5,0,38,37,1,0,0,0,39,42,1,0,0,0,40,38,1,0,0,0,40,41,1,0,0,0,
        41,9,1,0,0,0,42,40,1,0,0,0,43,44,5,4,0,0,44,45,5,10,0,0,45,51,5,
        9,0,0,46,47,5,10,0,0,47,48,5,5,0,0,48,49,5,10,0,0,49,51,5,9,0,0,
        50,43,1,0,0,0,50,46,1,0,0,0,51,11,1,0,0,0,3,34,40,50
    ]

class DOTA2Parser ( Parser ):

    grammarFileName = "DOTA2.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'partida'", "'aliados'", "'rivais'", 
                     "'analisar'", "'constroi'", "'fim_partida'", "':'", 
                     "','", "';'" ]

    symbolicNames = [ "<INVALID>", "PARTIDA", "ALIADOS", "RIVAIS", "ANALISAR", 
                      "CONSTROI", "FIM_PARTIDA", "COLON", "COMMA", "SEMICOLON", 
                      "IDENT", "WS", "ERROR" ]

    RULE_programa = 0
    RULE_bloco_aliados = 1
    RULE_bloco_rivais = 2
    RULE_lista_herois = 3
    RULE_comandos = 4
    RULE_comando = 5

    ruleNames =  [ "programa", "bloco_aliados", "bloco_rivais", "lista_herois", 
                   "comandos", "comando" ]

    EOF = Token.EOF
    PARTIDA=1
    ALIADOS=2
    RIVAIS=3
    ANALISAR=4
    CONSTROI=5
    FIM_PARTIDA=6
    COLON=7
    COMMA=8
    SEMICOLON=9
    IDENT=10
    WS=11
    ERROR=12

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class ProgramaContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def PARTIDA(self):
            return self.getToken(DOTA2Parser.PARTIDA, 0)

        def bloco_aliados(self):
            return self.getTypedRuleContext(DOTA2Parser.Bloco_aliadosContext,0)


        def bloco_rivais(self):
            return self.getTypedRuleContext(DOTA2Parser.Bloco_rivaisContext,0)


        def comandos(self):
            return self.getTypedRuleContext(DOTA2Parser.ComandosContext,0)


        def FIM_PARTIDA(self):
            return self.getToken(DOTA2Parser.FIM_PARTIDA, 0)

        def EOF(self):
            return self.getToken(DOTA2Parser.EOF, 0)

        def getRuleIndex(self):
            return DOTA2Parser.RULE_programa

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPrograma" ):
                listener.enterPrograma(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPrograma" ):
                listener.exitPrograma(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPrograma" ):
                return visitor.visitPrograma(self)
            else:
                return visitor.visitChildren(self)




    def programa(self):

        localctx = DOTA2Parser.ProgramaContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_programa)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 12
            self.match(DOTA2Parser.PARTIDA)
            self.state = 13
            self.bloco_aliados()
            self.state = 14
            self.bloco_rivais()
            self.state = 15
            self.comandos()
            self.state = 16
            self.match(DOTA2Parser.FIM_PARTIDA)
            self.state = 17
            self.match(DOTA2Parser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Bloco_aliadosContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ALIADOS(self):
            return self.getToken(DOTA2Parser.ALIADOS, 0)

        def COLON(self):
            return self.getToken(DOTA2Parser.COLON, 0)

        def lista_herois(self):
            return self.getTypedRuleContext(DOTA2Parser.Lista_heroisContext,0)


        def SEMICOLON(self):
            return self.getToken(DOTA2Parser.SEMICOLON, 0)

        def getRuleIndex(self):
            return DOTA2Parser.RULE_bloco_aliados

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBloco_aliados" ):
                listener.enterBloco_aliados(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBloco_aliados" ):
                listener.exitBloco_aliados(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBloco_aliados" ):
                return visitor.visitBloco_aliados(self)
            else:
                return visitor.visitChildren(self)




    def bloco_aliados(self):

        localctx = DOTA2Parser.Bloco_aliadosContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_bloco_aliados)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 19
            self.match(DOTA2Parser.ALIADOS)
            self.state = 20
            self.match(DOTA2Parser.COLON)
            self.state = 21
            self.lista_herois()
            self.state = 22
            self.match(DOTA2Parser.SEMICOLON)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Bloco_rivaisContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def RIVAIS(self):
            return self.getToken(DOTA2Parser.RIVAIS, 0)

        def COLON(self):
            return self.getToken(DOTA2Parser.COLON, 0)

        def lista_herois(self):
            return self.getTypedRuleContext(DOTA2Parser.Lista_heroisContext,0)


        def SEMICOLON(self):
            return self.getToken(DOTA2Parser.SEMICOLON, 0)

        def getRuleIndex(self):
            return DOTA2Parser.RULE_bloco_rivais

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBloco_rivais" ):
                listener.enterBloco_rivais(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBloco_rivais" ):
                listener.exitBloco_rivais(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBloco_rivais" ):
                return visitor.visitBloco_rivais(self)
            else:
                return visitor.visitChildren(self)




    def bloco_rivais(self):

        localctx = DOTA2Parser.Bloco_rivaisContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_bloco_rivais)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 24
            self.match(DOTA2Parser.RIVAIS)
            self.state = 25
            self.match(DOTA2Parser.COLON)
            self.state = 26
            self.lista_herois()
            self.state = 27
            self.match(DOTA2Parser.SEMICOLON)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Lista_heroisContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENT(self, i:int=None):
            if i is None:
                return self.getTokens(DOTA2Parser.IDENT)
            else:
                return self.getToken(DOTA2Parser.IDENT, i)

        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(DOTA2Parser.COMMA)
            else:
                return self.getToken(DOTA2Parser.COMMA, i)

        def getRuleIndex(self):
            return DOTA2Parser.RULE_lista_herois

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLista_herois" ):
                listener.enterLista_herois(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLista_herois" ):
                listener.exitLista_herois(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLista_herois" ):
                return visitor.visitLista_herois(self)
            else:
                return visitor.visitChildren(self)




    def lista_herois(self):

        localctx = DOTA2Parser.Lista_heroisContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_lista_herois)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 29
            self.match(DOTA2Parser.IDENT)
            self.state = 34
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==8:
                self.state = 30
                self.match(DOTA2Parser.COMMA)
                self.state = 31
                self.match(DOTA2Parser.IDENT)
                self.state = 36
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ComandosContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def comando(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(DOTA2Parser.ComandoContext)
            else:
                return self.getTypedRuleContext(DOTA2Parser.ComandoContext,i)


        def getRuleIndex(self):
            return DOTA2Parser.RULE_comandos

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterComandos" ):
                listener.enterComandos(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitComandos" ):
                listener.exitComandos(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitComandos" ):
                return visitor.visitComandos(self)
            else:
                return visitor.visitChildren(self)




    def comandos(self):

        localctx = DOTA2Parser.ComandosContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_comandos)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 40
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==4 or _la==10:
                self.state = 37
                self.comando()
                self.state = 42
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ComandoContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ANALISAR(self):
            return self.getToken(DOTA2Parser.ANALISAR, 0)

        def IDENT(self, i:int=None):
            if i is None:
                return self.getTokens(DOTA2Parser.IDENT)
            else:
                return self.getToken(DOTA2Parser.IDENT, i)

        def SEMICOLON(self):
            return self.getToken(DOTA2Parser.SEMICOLON, 0)

        def CONSTROI(self):
            return self.getToken(DOTA2Parser.CONSTROI, 0)

        def getRuleIndex(self):
            return DOTA2Parser.RULE_comando

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterComando" ):
                listener.enterComando(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitComando" ):
                listener.exitComando(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitComando" ):
                return visitor.visitComando(self)
            else:
                return visitor.visitChildren(self)




    def comando(self):

        localctx = DOTA2Parser.ComandoContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_comando)
        try:
            self.state = 50
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [4]:
                self.enterOuterAlt(localctx, 1)
                self.state = 43
                self.match(DOTA2Parser.ANALISAR)
                self.state = 44
                self.match(DOTA2Parser.IDENT)
                self.state = 45
                self.match(DOTA2Parser.SEMICOLON)
                pass
            elif token in [10]:
                self.enterOuterAlt(localctx, 2)
                self.state = 46
                self.match(DOTA2Parser.IDENT)
                self.state = 47
                self.match(DOTA2Parser.CONSTROI)
                self.state = 48
                self.match(DOTA2Parser.IDENT)
                self.state = 49
                self.match(DOTA2Parser.SEMICOLON)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





