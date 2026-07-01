grammar DOTA2;

programa:
    PARTIDA bloco_aliados bloco_rivais comandos FIM_PARTIDA EOF
    ;

bloco_aliados:
    ALIADOS COLON lista_herois SEMICOLON
    ;

bloco_rivais:
    RIVAIS COLON lista_herois SEMICOLON
    ;

lista_herois:
    IDENT (COMMA IDENT)*
    ;

comandos:
    comando*
    ;

comando:
    ANALISAR IDENT SEMICOLON
    | IDENT CONSTROI IDENT SEMICOLON
    ;

// Palavras-chave
PARTIDA:     'partida';
ALIADOS:     'aliados';
RIVAIS:      'rivais';
ANALISAR:    'analisar';
CONSTROI:    'constroi';
FIM_PARTIDA: 'fim_partida';

// Simbolos
COLON:      ':';
COMMA:      ',';
SEMICOLON:  ';';

// Identificadores
IDENT: [a-zA-Z_][a-zA-Z0-9_]*;

// Espacos em branco (ignorados)
WS: [ \t\r\n]+ -> skip;

// Erro: qualquer outro caractere
ERROR: .;
