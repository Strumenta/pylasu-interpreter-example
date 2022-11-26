from antlr4 import InputStream, CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener
from pylasu.model import Position, Point
from pylasu.validation.validation import Result, Issue, IssueType

from entity_parser.AntlrEntityLexer import AntlrEntityLexer
from entity_parser.AntlrEntityParser import AntlrEntityParser
from interpreter.MyListener import MyListener
from interpreter.entities_parser.entities_ast import Module
from interpreter.script_parser.script_parsetree_converter import to_ast
from script_parser.AntlrScriptLexer import AntlrScriptLexer
from script_parser.AntlrScriptParser import AntlrScriptParser


class ScriptPylasuParser:

    def parse(self, code: str) -> Result:
        issues = []

        input = InputStream(code)

        lexer = AntlrScriptLexer(input)
        lexer.removeErrorListeners()
        lexer.addErrorListener(MyListener(issues, IssueType.LEXICAL))

        token_stream = CommonTokenStream(lexer)
        parser = AntlrScriptParser(token_stream)
        parser.removeErrorListeners()
        parser.addErrorListener(MyListener(issues, IssueType.SYNTACTIC))
        parse_tree = parser.script()

        ast = parse_tree.to_ast(issues)
        ast.assign_parents()

        return Result(root=ast, issues=issues)
