"""
AST (Abstract Syntax Tree) - Nós da Árvore Sintática Abstrata
Representa a estrutura hierárquica do programa LPD após análise sintática.
"""

from dataclasses import dataclass
from typing import List, Optional


# Classe base para todos os nós da AST
class ASTNode:
    """Classe base para todos os nós da árvore sintática abstrata."""
    pass


# ==================== PROGRAMA ====================

@dataclass
class Program(ASTNode):
    """Nó raiz: programa nome; declarações comandos."""
    name: str
    var_declarations: Optional['VarDeclarations']
    procedures: List['Procedure']
    functions: List['Function']
    compound_command: 'CompoundCommand'


# ==================== DECLARAÇÕES ====================

@dataclass
class VarDeclarations(ASTNode):
    """Declarações de variáveis: var declarações;"""
    declarations: List['VarDeclaration']


@dataclass
class VarDeclaration(ASTNode):
    """Declaração individual: ids : tipo"""
    identifiers: List[str]
    var_type: str  # 'inteiro' ou 'booleano'


@dataclass
class Procedure(ASTNode):
    """Procedimento (para implementação futura)"""
    name: str
    parameters: List['Parameter']
    block: 'Block'


@dataclass
class Function(ASTNode):
    """Função (para implementação futura)"""
    name: str
    parameters: List['Parameter']
    return_type: str
    block: 'Block'


@dataclass
class Parameter(ASTNode):
    """Parâmetro de procedimento/função"""
    identifiers: List[str]
    param_type: str


@dataclass
class Block(ASTNode):
    """Bloco de código"""
    var_declarations: Optional[VarDeclarations]
    procedures: List[Procedure]
    functions: List[Function]
    compound_command: 'CompoundCommand'


# ==================== COMANDOS ====================

@dataclass
class CompoundCommand(ASTNode):
    """Comando composto: inicio comandos fim"""
    commands: List['Command']


class Command(ASTNode):
    """Classe base para todos os comandos."""
    pass


@dataclass
class Assignment(Command):
    """Atribuição: id := expressão"""
    identifier: str
    expression: 'Expression'


@dataclass
class ReadCommand(Command):
    """Comando de leitura: leia(id)"""
    identifier: str


@dataclass
class WriteCommand(Command):
    """Comando de escrita: escreva(expressão)"""
    expression: 'Expression'


@dataclass
class IfCommand(Command):
    """Comando condicional: se expressão entao comando [senao comando]"""
    condition: 'Expression'
    then_command: Command
    else_command: Optional[Command] = None


@dataclass
class WhileCommand(Command):
    """Comando de repetição: enquanto expressão faca comando"""
    condition: 'Expression'
    body: Command


@dataclass
class EmptyCommand(Command):
    """Comando vazio."""
    pass


# ==================== EXPRESSÕES ====================

class Expression(ASTNode):
    """Classe base para todas as expressões."""
    expr_type: Optional[str] = None  # 'inteiro' ou 'booleano' (preenchido na análise semântica)


@dataclass
class BinaryOp(Expression):
    """Operação binária: expressão operador expressão"""
    left: Expression
    operator: str  # '+', '-', '*', 'div', 'e', 'ou', '=', '!=', '<', '<=', '>', '>='
    right: Expression
    expr_type: Optional[str] = None


@dataclass
class UnaryOp(Expression):
    """Operação unária: operador expressão"""
    operator: str  # 'nao', '-'
    operand: Expression
    expr_type: Optional[str] = None


@dataclass
class Identifier(Expression):
    """Identificador: nome de variável"""
    name: str
    expr_type: Optional[str] = None


@dataclass
class Number(Expression):
    """Número literal"""
    value: int
    expr_type: str = 'inteiro'


@dataclass
class Boolean(Expression):
    """Booleano literal: verdadeiro ou falso"""
    value: bool
    expr_type: str = 'booleano'


# ==================== UTILITÁRIOS ====================

def ast_to_string(node: ASTNode, indent: int = 0) -> str:
    """Converte a AST para string formatada (para debug)."""
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
    
    else:
        return f"{prefix}{node.__class__.__name__}\n"

