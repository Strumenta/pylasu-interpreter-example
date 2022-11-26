from antlr4.error.ErrorListener import ErrorListener
from pylasu.model import Position, Point
from pylasu.validation import Issue, IssueType


class MyListener(ErrorListener):
    issues: list[Issue]
    issue_type: IssueType

    def __init__(self, issues: list[Issue], issue_type: IssueType):
        self.issues = issues
        self.issue_type = issue_type

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.issues.append(Issue(message=str(msg),
                                 type=self.issue_type, position=Position(start=Point(line=line, column=column),
                                                                         end=Point(line=line, column=column))))

    def reportAmbiguity(self, recognizer, dfa, startIndex, stopIndex, exact, ambigAlts, configs):
        pass

    def reportAttemptingFullContext(self, recognizer, dfa, startIndex, stopIndex, conflictingAlts, configs):
        pass

    def reportContextSensitivity(self, recognizer, dfa, startIndex, stopIndex, prediction, configs):
        pass
