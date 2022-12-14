from antlr4 import InputStream, CommonTokenStream
from pylasu.validation.validation import Result, IssueType

from entity_parser.AntlrEntityLexer import AntlrEntityLexer
from entity_parser.AntlrEntityParser import AntlrEntityParser
from interpreter.MyListener import MyListener

from interpreter.entities_parser.entities_parsetree_converter import to_ast


class EntitiesPylasuParser:

    def parse(self, code: str) -> Result:
        issues = []

        input = InputStream(code)

        lexer = AntlrEntityLexer(input)
        lexer.removeErrorListeners()
        lexer.addErrorListener(MyListener(issues, IssueType.LEXICAL))

        token_stream = CommonTokenStream(lexer)
        parser = AntlrEntityParser(token_stream)
        parser.removeErrorListeners()
        parser.addErrorListener(MyListener(issues, IssueType.SYNTACTIC))
        parse_tree = parser.module()

        ast = parse_tree.to_ast(issues)
        ast.assign_parents()

        return Result(root=ast, issues=issues)