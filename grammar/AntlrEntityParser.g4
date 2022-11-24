parser grammar AntlrEntityParser;

options {
    tokenVocab=AntlrEntityLexer;
}

module:
    MODULE name=ID LCRLY
        entities+=entity*
    RCRLY
    EOF
    ;

entity:
    ENTITY name=ID LCRLY
        features+=feature*
    RCRLY
    ;

feature:
    name=ID COLON type=type_spec SEMI
    ;

type_spec
    : INTEGER   #integer_type
    | BOOLEAN   #boolean_type
    | STRING    #string_type
    | target=ID #entity_type
    ;