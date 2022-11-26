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


ID: [a-zA-Z][a-zA-Z0-9_]*;

WS: [ \r\n\t]+ -> channel(HIDDEN);