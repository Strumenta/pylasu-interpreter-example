lexer grammar AntlrScriptLexer;


INTEGER: 'integer';
BOOLEAN: 'boolean';
STRING: 'string';

ENTITY: 'entity';
MODULE: 'module';

COLON: ':';
SEMI: ';';
LSQRD: '[';
RSQRD: ']';
LCRLY: '{';
RCRLY: '}';
LPAREN: '(';
RPAREN: ')';

DIV: '/';
MULT: '*';
PLUS: '+';
MINUS: '-';
HASH: '#';

CREATE: 'create';
AS: 'as';
SET: 'set';
OF: 'of';
TO: 'to';
PRINT: 'print';
CONCAT: 'concat';
AND: 'and';

ID: [a-zA-Z][a-zA-Z0-9_]*;
INT_VALUE: '0'|[1-9][0-9]*;
STR_VALUE: '\'' ~['\r\n]* '\'';

WS: [ \r\n\t]+ -> channel(HIDDEN);