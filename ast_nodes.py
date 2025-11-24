from dataclasses import dataclass
from typing import List, Optional


# Classe base para todos os nós da AST
class ASTNode:
    pass


# ==================== PROGRAMA ====================

@dataclass
class Program(ASTNode):
    name: str
    var_declarations: Optional['VarDeclarations']
    procedures: List['Procedure']
    functions: List['Function']
    compound_command: 'CompoundCommand'


# ==================== DECLARAÇÕES ====================

@dataclass
class VarDeclarations(ASTNode):
    declarations: List['VarDeclaration']


@dataclass
class VarDeclaration(ASTNode):
    identifiers: List[str]
    var_type: str  # 'inteiro' ou 'booleano'


@dataclass
class Procedure(ASTNode):
    name: str
    parameters: List['Parameter']
    block: 'Block'


@dataclass
class Function(ASTNode):
    name: str
    parameters: List['Parameter']
    return_type: str
    block: 'Block'


@dataclass
class Parameter(ASTNode):
    identifiers: List[str]
    param_type: str


@dataclass
class Block(ASTNode):
    var_declarations: Optional[VarDeclarations]
    procedures: List[Procedure]
    functions: List[Function]
    compound_command: 'CompoundCommand'

# ==================== DECLARAÇÕES DE SUBROTINAS ====================

def declaracao_procedimento(self) -> Procedure:
    """
    declaracao_procedimento ::=
        "procedimento" ID [ "(" lista_parametros ")" ] ";" bloco ";"
    """
    self.expect(TokenType.PROCEDIMENTO, "Esperado 'procedimento'")
    name_token = self.expect(TokenType.ID, "Esperado identificador do procedimento")
    name = name_token.value

    parameters: List[Parameter] = []

    # Parâmetros opcionais: procedimento P(a: inteiro; b: booleano);
    if self.match(TokenType.LPAREN):
        parameters = self.lista_parametros()

    self.expect(TokenType.SEMI, "Esperado ';' após cabeçalho do procedimento")

    block = self.bloco()

    # Exemplo da apostila: 'fim' do proc termina com ';'
    self.expect(TokenType.SEMI, "Esperado ';' após 'fim' do procedimento")

    return Procedure(name=name, parameters=parameters, block=block)


def declaracao_funcao(self) -> Function:
    """
    declaracao_funcao ::=
        "funcao" ID [ "(" lista_parametros ")" ] ":" tipo ";" bloco ";"
    """
    self.expect(TokenType.FUNCAO, "Esperado 'funcao'")
    name_token = self.expect(TokenType.ID, "Esperado identificador da função")
    name = name_token.value

    parameters: List[Parameter] = []

    # Parâmetros opcionais: funcao soma(a: inteiro; b: inteiro): inteiro;
    if self.match(TokenType.LPAREN):
        parameters = self.lista_parametros()

    self.expect(TokenType.COLON, "Esperado ':' após nome/parâmetros da função")

    return_type = self.tipo()  # 'inteiro' ou 'booleano'

    self.expect(TokenType.SEMI, "Esperado ';' após cabeçalho da função")

    block = self.bloco()

    self.expect(TokenType.SEMI, "Esperado ';' após 'fim' da função")

    return Function(
        name=name,
        parameters=parameters,
        return_type=return_type,
        block=block
    )

# Comandos

@dataclass
class CompoundCommand(ASTNode):
    commands: List['Command']


class Command(ASTNode):
    pass


@dataclass
class Assignment(Command):
    identifier: str
    expression: 'Expression'


@dataclass
class ProcedureCall(Command):
    name: str
    arguments: List['Expression']


@dataclass
class ReadCommand(Command):
    identifier: str


@dataclass
class WriteCommand(Command):
    expression: 'Expression'


@dataclass
class IfCommand(Command):
    condition: 'Expression'
    then_command: Command
    else_command: Optional[Command] = None


@dataclass
class WhileCommand(Command):
    condition: 'Expression'
    body: Command


@dataclass
class EmptyCommand(Command):
    pass


# Expressões

class Expression(ASTNode):
    expr_type: Optional[str] = None  # 'inteiro' ou 'booleano' (preenchido na análise semântica)


@dataclass
class BinaryOp(Expression):
    left: Expression
    operator: str  # '+', '-', '*', 'div', 'e', 'ou', '=', '!=', '<', '<=', '>', '>='
    right: Expression
    expr_type: Optional[str] = None


@dataclass
class UnaryOp(Expression):
    operator: str  # 'nao', '-'
    operand: Expression
    expr_type: Optional[str] = None


@dataclass
class Identifier(Expression):
    name: str
    expr_type: Optional[str] = None


@dataclass
class Number(Expression):
    value: int
    expr_type: str = 'inteiro'


@dataclass
class Boolean(Expression):
    value: bool
    expr_type: str = 'booleano'


@dataclass
class FunctionCall(Expression):
    name: str
    arguments: List['Expression']
    expr_type: Optional[str] = None


# ==================== UTILITÁRIOS ====================

def ast_to_string(node: ASTNode, indent: int = 0) -> str:
    prefix = "  " * indent
    
    if isinstance(node, Program):
        result = f"{prefix}Program({node.name})\n"
        if node.var_declarations:
            result += ast_to_string(node.var_declarations, indent + 1)
        result += ast_to_string(node.compound_command, indent + 1)
        return result
    
    elif isinstance(node, VarDeclarations):
        result = f"{prefix}VarDeclarations\n"
        for decl in node.declarations:
            result += ast_to_string(decl, indent + 1)
        return result
    
    elif isinstance(node, VarDeclaration):
        result = f"{prefix}VarDecl({', '.join(node.identifiers)}: {node.var_type})\n"
        return result
    
    elif isinstance(node, CompoundCommand):
        result = f"{prefix}CompoundCommand\n"
        for cmd in node.commands:
            result += ast_to_string(cmd, indent + 1)
        return result
    
    elif isinstance(node, Assignment):
        result = f"{prefix}Assignment({node.identifier} :=)\n"
        result += ast_to_string(node.expression, indent + 1)
        return result
    
    elif isinstance(node, ReadCommand):
        return f"{prefix}Read({node.identifier})\n"
    
    elif isinstance(node, WriteCommand):
        result = f"{prefix}Write\n"
        result += ast_to_string(node.expression, indent + 1)
        return result
    
    elif isinstance(node, IfCommand):
        result = f"{prefix}If\n"
        result += f"{prefix}  condition:\n"
        result += ast_to_string(node.condition, indent + 2)
        result += f"{prefix}  then:\n"
        result += ast_to_string(node.then_command, indent + 2)
        if node.else_command:
            result += f"{prefix}  else:\n"
            result += ast_to_string(node.else_command, indent + 2)
        return result
    
    elif isinstance(node, WhileCommand):
        result = f"{prefix}While\n"
        result += f"{prefix}  condition:\n"
        result += ast_to_string(node.condition, indent + 2)
        result += f"{prefix}  body:\n"
        result += ast_to_string(node.body, indent + 2)
        return result
    
    elif isinstance(node, BinaryOp):
        result = f"{prefix}BinaryOp({node.operator})\n"
        result += ast_to_string(node.left, indent + 1)
        result += ast_to_string(node.right, indent + 1)
        return result
    
    elif isinstance(node, UnaryOp):
        result = f"{prefix}UnaryOp({node.operator})\n"
        result += ast_to_string(node.operand, indent + 1)
        return result
    
    elif isinstance(node, Identifier):
        return f"{prefix}Id({node.name})\n"
    
    elif isinstance(node, Number):
        return f"{prefix}Num({node.value})\n"
    
    elif isinstance(node, Boolean):
        return f"{prefix}Bool({node.value})\n"
    
    elif isinstance(node, EmptyCommand):
        return f"{prefix}Empty\n"

    elif isinstance(node, ProcedureCall):
        result = f"{prefix}ProcCall({node.name})\n"
        for arg in node.arguments:
            result += ast_to_string(arg, indent + 1)
        return result

    elif isinstance(node, FunctionCall):
        result = f"{prefix}FuncCall({node.name})\n"
        for arg in node.arguments:
            result += ast_to_string(arg, indent + 1)
        return result

    
    else:
        return f"{prefix}{node.__class__.__name__}\n"

