lexer grammar AntlrEntityLexer;

// Tokens for types
INTEGER: 'integer';
BOOLEAN: 'boolean';
STRING: 'string';


// Keywords
ENTITY: 'entity';
MODULE: 'module';

// Punctuation
COLON: ':';
SEMI: ';';
LSQRD: '[';
RSQRD: ']';
LCRLY: '{';
RCRLY: '}';


ID: [A-Z]+;

WS: [ \r\n\t]+ -> channel(HIDDEN);