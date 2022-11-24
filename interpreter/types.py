from dataclasses import dataclass

from pylasu.model import Node
from pylasu.validation import Issue, IssueType
from pylasu.support import extension_method

from interpreter.entities_parser.entities_ast import Type, Entity, StringType, IntegerType, EntityRefType
from interpreter.script_parser.script_ast import ReferenceExpression, GetInstanceExpression, GetFeatureValueExpression


@dataclass
class RType(Node):
    def can_be_assigned(self, other_type: 'RType') -> bool:
        return self == other_type

    @classmethod
    def from_type(cls, type: Type):
        if isinstance(type, StringType):
            return RStringType()
        elif isinstance(type, IntegerType):
            return RIntegerType()
        elif isinstance(type, EntityRefType):
            if type.entity.resolved():
                return REntityRefType(type.entity.referred)
            else:
                return None
        else:
            raise Exception("%s is not supported" % str(type))


@dataclass
class RStringType(RType):
    pass


@dataclass
class RIntegerType(RType):
    pass


@dataclass
class RBooleanType(RType):
    pass


@dataclass
class REntityRefType(RType):
    entity: Entity

    def __post_init__(self):
        if self.entity is None:
            raise Exception("Unresolved")


@extension_method(Type)
def to_rtype(self: Type) -> RType:
    return RType.from_type(self)


def calc_type(node: Node, issues: list[Issue]) -> RType:
    if isinstance(node, ReferenceExpression):
        if node.what.referred.entity.referred is None:
            issues.append(Issue(type=IssueType.SEMANTIC, message=f"Unresolved entity {node.what.referred.entity.name},"
                                                                 f" unable to calculate type of {node}"))
            return None
        return REntityRefType(node.what.referred.entity.referred)
    elif isinstance(node, GetInstanceExpression):
        return REntityRefType(node.entity.referred)
    elif isinstance(node, GetFeatureValueExpression):
        if node.feature.resolved():
            return node.feature.referred.type.to_rtype()
        else:
            issues.append(Issue(type=IssueType.SEMANTIC, message=f"Unresolved feature {node.feature.name},"
                                                                 f" unable to calculate type of {node}"))
            return None
    else:
        raise Exception("Unable to calculate type for %s" % (str(node)))