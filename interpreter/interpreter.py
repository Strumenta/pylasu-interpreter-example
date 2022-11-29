from dataclasses import dataclass
from typing import Any, List, Optional


from pylasu.validation import Issue, IssueType
from pylasu.model.traversing import walk_leaves_first


from interpreter.entities_parser.entities_ast import Entity, Module, StringType, BooleanType, IntegerType, \
    EntityRefType, Type
from interpreter.script_parser.script_ast import CreateStatement, Script, SetStatement, ReferenceExpression, \
    StringLiteralExpression, \
    PrintStatement, GetInstanceExpression, IntLiteralExpression, DivisionExpression, SumExpression, ConcatExpression, \
    GetFeatureValueExpression, MultiplicationExpression
from interpreter.types import calc_type, REntityRefType


class EntityInstance:
    id: int
    entity: Entity
    values: dict

    def __str__(self) -> str:
        for k in self.values.keys():
            if k.name == 'name':
                return str(self.values[k])
        return super().__str__()

    def __getitem__(self, name: str) -> Any:
        for k in self.values.keys():
            if k.name == name:
                return self.values[k]
        raise Exception("Unknown feature %s" % name)

    def set_feature(self, feature, value):
        self.values[feature] = value



class Interpreter:
    module: Module
    instances_by_entity: dict
    output: List[str]

    def __init__(self, module: Module, verbose: bool = True):
        self.module = module
        issues = []
        self.__resolve_entities__(self.module, issues)
        self.instances_by_entity = {}
        self.next_id = 1
        self.verbose = verbose
        if self.verbose:
            self.output = ['Interpreter initialized']
        else:
            self.output = []

    def instantiate_entity(self, entity: Entity) -> None:
        new_instance = EntityInstance()
        new_instance.id = self.next_id
        self.next_id = self.next_id + 1
        new_instance.entity = entity
        new_instance.values = {}
        for feature in entity.features:
            if feature.many:
                feature_value = []
            elif isinstance(feature.type, StringType):
                feature_value = "<unspecified>"
            elif isinstance(feature.type, BooleanType):
                feature_value = False
            elif isinstance(feature.type, IntegerType):
                feature_value = 0
            elif isinstance(feature.type, EntityRefType):
                feature_value = None
            else:
                raise Exception("Unsupported type %s (feature: %s)" % (str(feature.type), str(feature)))
            new_instance.set_feature(feature, feature_value)
        if entity not in self.instances_by_entity:
            self.instances_by_entity[entity] = []
        self.instances_by_entity[entity].append(new_instance)
        if self.verbose:
            self.output.append("Added instance of %s: %s" % (entity, new_instance))
        return new_instance

    def set_value(self, entity: Entity, feature_name: str, value: Any) -> None:
        pass

    def instances_by_entity_name(self, entity_name):
        e = self.module.get_entity_by_name(entity_name)
        if e not in self.instances_by_entity:
            self.instances_by_entity[e] = []
        return self.instances_by_entity[e]

    def instances_by_id(self, entity_name, instance_id) -> Optional[EntityInstance]:
        e = self.module.get_entity_by_name(entity_name)
        if e not in self.instances_by_entity:
            return None
        matches = [i for i in self.instances_by_entity[e] if i.id == instance_id]
        if len(matches) != 1:
            raise Exception("one instance expected")
        return matches[0]

    def __resolve_entities__(self, module: Module, issues: list[Issue]):
        for t in module.walk_descendants(restrict_to=EntityRefType):
            resolved = t.entity.try_to_resolve(module.entities)
            if not resolved:
                issues.append(Issue(type=IssueType.SEMANTIC, message="Cannot find entity named %s" % t.entity.name))

    def __check_types__(self, script: Script, issues: list[Issue]):
        for s in script.walk_descendants(restrict_to=SetStatement):
            feature_type = calc_type(s.feature.referred, issues)
            value_type = calc_type(s.value, issues)
            if feature_type is not None and value_type is not None:
                if not feature_type.can_be_assigned(value_type):
                    issues.append(Issue(type=IssueType.SEMANTIC,
                                        position=s.position,
                                        message="Cannot assign %s (type %s) to feature %s (type %s)"
                                                % (str(s.value), str(value_type), str(s.feature.referred), str(feature_type))))

    def __resolve_script__(self, script: Script, issues: list[Issue]):

        # Resolving references to elements outside the script
        for s in script.walk_descendants(restrict_to=GetInstanceExpression):
            resolved = s.entity.try_to_resolve(self.module.entities)
            if not resolved:
                issues.append(Issue(type=IssueType.SEMANTIC, message="Cannot find entity named %s" % s.entity.name))
        for s in script.walk_descendants(restrict_to=CreateStatement):
            resolved = s.entity.try_to_resolve(self.module.entities)
            if not resolved:
                issues.append(Issue(type=IssueType.SEMANTIC, message="Cannot find entity named %s" % s.entity.name))

        # Resolving references to elements inside the script
        for e in script.walk_descendants(restrict_to=ReferenceExpression):
            e.what.try_to_resolve(script.walk_descendants(restrict_to=CreateStatement))
            if not resolved:
                issues.append(Issue(type=IssueType.SEMANTIC, message="Cannot find variable named %s" % e.what.name))

        # Resolutions involving type calculation
        for s in script.walk_descendants(restrict_to=SetStatement):
            assert s.instance is not None
            t = calc_type(s.instance, issues)
            assert t is not None
            assert isinstance(t, REntityRefType), f"type of an instance should be an REntityRefType while it is: {t}" \
                                                  f" (type: {type(t)})"
            assert t.entity is not None
            entity = t.entity
            resolved = s.feature.try_to_resolve(entity.features)
            if not resolved:
                issues.append(Issue(type=IssueType.SEMANTIC, message="Unable to resolve feature reference %s in %s. Candidates: %s" % (s.feature.name, str(s),
                                                                                      str(entity.features))))

        for s in script.walk_descendants(walker=walk_leaves_first, restrict_to=GetFeatureValueExpression):
            t = calc_type(s.instance, issues)
            if t is None:
                issues.append(Issue(type=IssueType.SEMANTIC, message=f"Unable to resolve feature reference in '{s.source_text}', "
                                                                     f"because we cannot calculate the type of {s.instance}"))
            else:
                assert isinstance(t, REntityRefType), \
                    f"type of an instance should be an REntityRefType while it is: {t}"
                e = t.entity
                resolved = s.feature.try_to_resolve(e.features)
                if not resolved:
                    issues.append(Issue(type=IssueType.SEMANTIC, message="Unable to resolve feature reference %s in %s. Candidates: %s" % (s.feature.name, str(s),
                                                                                      str(entity.features))))

    def run_script(self, script) -> list[Issue]:
        issues = []
        self.__resolve_script__(script, issues)
        self.__check_types__(script, issues)
        symbol_table = {}
        for s in script.statements:
            self.execute_statement(s, symbol_table, issues)
        return issues

    def evaluate_expression(self, expression, symbol_table, issues: list[Issue]) -> Any:
        if isinstance(expression, ReferenceExpression):
            if expression.what.referred is None:
                raise Exception("Unresolved expression %s" % str(expression))
            if expression.what.referred not in symbol_table:
                raise Exception("I cannot find %s in symbol table %s" % (str(expression.what.referred), str(symbol_table)))
            return symbol_table[expression.what.referred]
        elif isinstance(expression, StringLiteralExpression):
            return expression.value
        elif isinstance(expression, IntLiteralExpression):
            return expression.value
        elif isinstance(expression, DivisionExpression):
            left = self.evaluate_expression(expression.left, symbol_table, issues)
            right = self.evaluate_expression(expression.right, symbol_table, issues)
            return int(left/right)
        elif isinstance(expression, MultiplicationExpression):
            left = self.evaluate_expression(expression.left, symbol_table, issues)
            right = self.evaluate_expression(expression.right, symbol_table, issues)
            return left*right
        elif isinstance(expression, SumExpression):
            left = self.evaluate_expression(expression.left, symbol_table, issues)
            right = self.evaluate_expression(expression.right, symbol_table, issues)
            return left+right
        elif isinstance(expression, ConcatExpression):
            left = self.evaluate_expression(expression.left, symbol_table, issues)
            right = self.evaluate_expression(expression.right, symbol_table, issues)
            return str(left)+str(right)
        elif isinstance(expression, GetInstanceExpression):
            id = self.evaluate_expression(expression.id, symbol_table, issues)
            matching = [i for i in self.instances_by_entity[expression.entity.referred] if i.id == id]
            if len(matching) != 1:
                raise Exception("Expected one match but found %s" % str(len(matching)))
            return matching[0]
        elif isinstance(expression, GetFeatureValueExpression):
            instance = self.evaluate_expression(expression.instance, symbol_table, issues)
            if not expression.feature.resolved():
                issues.append(Issue(type=IssueType.SEMANTIC, message=f"Cannot evaluate expression %{expression}"))
                return None
            else:
                return instance.values[expression.feature.referred]
        else:
            raise Exception("Unable to evaluate expression %s" % str(expression))

    def execute_statement(self, statement, symbol_table, issues: list[Issue]):
        if isinstance(statement, CreateStatement):
            if statement.entity.referred is None:
                issues.append(Issue(type=IssueType.SEMANTIC, message="Cannot instantiate entity named %s" % statement.entity.name))
                return
            instance = self.instantiate_entity(statement.entity.referred)
            if statement.name is not None:
                symbol_table[statement] = instance
        elif isinstance(statement, SetStatement):
            instance = self.evaluate_expression(statement.instance, symbol_table, issues)
            value = self.evaluate_expression(statement.value, symbol_table, issues)
            instance.set_feature(statement.feature.referred, value)
        elif isinstance(statement, PrintStatement):
            message = self.evaluate_expression(statement.message, symbol_table, issues)
            self.output.append(message)
        else:
            raise Exception("Unable to execute statement %s" % str(statement))

    def clear_logs(self):
        self.output = []


