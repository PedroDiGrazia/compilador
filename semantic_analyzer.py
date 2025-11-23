"""
Semantic Analyzer - Analisador Semântico
Realiza análise semântica da AST: verificação de tipos, declarações e compatibilidade.
"""

from ast_nodes import *
from symbol_table import SymbolTable, Symbol


class SemanticError(Exception):
    """Exceção para erros semânticos."""
    def __init__(self, message: str):
        super().__init__(f"Erro semântico: {message}")


class SemanticAnalyzer:
    """
    Analisador semântico que percorre a AST verificando:
    - Declaração antes do uso
    - Tipos compatíveis
    - Declaração única no mesmo escopo
    - Operadores compatíveis com tipos
    """
    
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []
    
    def analyze(self, program: Program) -> SymbolTable:
        """
        Analisa semanticamente o programa.
        
        Args:
            program: Nó raiz da AST
        
        Returns:
            SymbolTable: Tabela de símbolos preenchida
        
        Raises:
            SemanticError: Se houver erros semânticos
        """
        try:
            self.analisar_programa(program)
        except SemanticError as e:
            self.errors.append(str(e))
        
        if self.errors:
            raise SemanticError("\n".join(self.errors))
        
        return self.symbol_table
    
    # ==================== MÉTODOS DE ANÁLISE ====================
    
    def analisar_programa(self, node: Program):
        """Analisa semanticamente o programa."""
        # Declarações de variáveis
        if node.var_declarations:
            self.analisar_declaracoes_variaveis(node.var_declarations)
        
        # TODO: Procedimentos e funções no futuro
        
        # Comando composto principal
        self.analisar_comando_composto(node.compound_command)
    
    def analisar_declaracoes_variaveis(self, node: VarDeclarations):
        """Analisa as declarações de variáveis."""
        for decl in node.declarations:
            self.analisar_declaracao_variavel(decl)
    
    def analisar_declaracao_variavel(self, node: VarDeclaration):
        """Analisa uma declaração de variável."""
        for identifier in node.identifiers:
            try:
                self.symbol_table.declare(identifier, node.var_type, 'var')
            except Exception as e:
                raise SemanticError(str(e))
    
    def analisar_comando_composto(self, node: CompoundCommand):
        """Analisa um comando composto."""
        for command in node.commands:
            self.analisar_comando(command)
    
    def analisar_comando(self, node: Command):
        """Analisa um comando (despacha para o tipo específico)."""
        if isinstance(node, Assignment):
            self.analisar_atribuicao(node)
        elif isinstance(node, ReadCommand):
            self.analisar_comando_leitura(node)
        elif isinstance(node, WriteCommand):
            self.analisar_comando_escrita(node)
        elif isinstance(node, IfCommand):
            self.analisar_comando_se(node)
        elif isinstance(node, WhileCommand):
            self.analisar_comando_enquanto(node)
        elif isinstance(node, CompoundCommand):
            self.analisar_comando_composto(node)
        elif isinstance(node, EmptyCommand):
            pass  # Comando vazio, nada a fazer
    
    def analisar_atribuicao(self, node: Assignment):
        """Analisa uma atribuição."""
        # Verifica se a variável foi declarada
        symbol = self.symbol_table.lookup(node.identifier)
        if symbol is None:
            raise SemanticError(f"Variável '{node.identifier}' não foi declarada")
        
        if symbol.category != 'var':
            raise SemanticError(f"'{node.identifier}' não é uma variável")
        
        # Analisa a expressão e obtém seu tipo
        expr_type = self.analisar_expressao(node.expression)
        
        # Verifica compatibilidade de tipos
        if symbol.symbol_type != expr_type:
            raise SemanticError(
                f"Tipo incompatível na atribuição: '{node.identifier}' é {symbol.symbol_type}, "
                f"mas a expressão é {expr_type}"
            )
    
    def analisar_comando_leitura(self, node: ReadCommand):
        """Analisa um comando de leitura."""
        symbol = self.symbol_table.lookup(node.identifier)
        if symbol is None:
            raise SemanticError(f"Variável '{node.identifier}' não foi declarada")
        
        if symbol.category != 'var':
            raise SemanticError(f"'{node.identifier}' não é uma variável")
    
    def analisar_comando_escrita(self, node: WriteCommand):
        """Analisa um comando de escrita."""
        self.analisar_expressao(node.expression)
    
    def analisar_comando_se(self, node: IfCommand):
        """Analisa um comando condicional."""
        # A condição deve ser booleana
        condition_type = self.analisar_expressao(node.condition)
        if condition_type != 'booleano':
            raise SemanticError(
                f"Condição do 'se' deve ser booleana, mas é {condition_type}"
            )
        
        # Analisa os comandos
        self.analisar_comando(node.then_command)
        if node.else_command:
            self.analisar_comando(node.else_command)
    
    def analisar_comando_enquanto(self, node: WhileCommand):
        """Analisa um comando de repetição."""
        # A condição deve ser booleana
        condition_type = self.analisar_expressao(node.condition)
        if condition_type != 'booleano':
            raise SemanticError(
                f"Condição do 'enquanto' deve ser booleana, mas é {condition_type}"
            )
        
        # Analisa o corpo
        self.analisar_comando(node.body)
    
    def analisar_expressao(self, node: Expression) -> str:
        """
        Analisa uma expressão e retorna seu tipo.
        
        Returns:
            str: O tipo da expressão ('inteiro' ou 'booleano')
        """
        if isinstance(node, BinaryOp):
            return self.analisar_operacao_binaria(node)
        elif isinstance(node, UnaryOp):
            return self.analisar_operacao_unaria(node)
        elif isinstance(node, Identifier):
            return self.analisar_identificador(node)
        elif isinstance(node, Number):
            node.expr_type = 'inteiro'
            return 'inteiro'
        elif isinstance(node, Boolean):
            node.expr_type = 'booleano'
            return 'booleano'
        else:
            raise SemanticError(f"Tipo de expressão desconhecido: {type(node)}")
    
    def analisar_operacao_binaria(self, node: BinaryOp) -> str:
        """Analisa uma operação binária e retorna seu tipo."""
        left_type = self.analisar_expressao(node.left)
        right_type = self.analisar_expressao(node.right)
        
        op = node.operator
        
        # Operadores aritméticos: +, -, *, div (inteiro -> inteiro)
        if op in ['+', '-', '*', 'div']:
            if left_type != 'inteiro' or right_type != 'inteiro':
                raise SemanticError(
                    f"Operador '{op}' requer operandos inteiros, "
                    f"mas recebeu {left_type} e {right_type}"
                )
            node.expr_type = 'inteiro'
            return 'inteiro'
        
        # Operadores lógicos: e, ou (booleano -> booleano)
        elif op in ['e', 'ou']:
            if left_type != 'booleano' or right_type != 'booleano':
                raise SemanticError(
                    f"Operador '{op}' requer operandos booleanos, "
                    f"mas recebeu {left_type} e {right_type}"
                )
            node.expr_type = 'booleano'
            return 'booleano'
        
        # Operadores relacionais: =, !=, <, <=, >, >= (mesmo tipo -> booleano)
        elif op in ['=', '!=', '<', '<=', '>', '>=']:
            if left_type != right_type:
                raise SemanticError(
                    f"Operador '{op}' requer operandos do mesmo tipo, "
                    f"mas recebeu {left_type} e {right_type}"
                )
            # Operadores de ordem (<, <=, >, >=) só para inteiros
            if op in ['<', '<=', '>', '>='] and left_type != 'inteiro':
                raise SemanticError(
                    f"Operador '{op}' requer operandos inteiros, "
                    f"mas recebeu {left_type}"
                )
            node.expr_type = 'booleano'
            return 'booleano'
        
        else:
            raise SemanticError(f"Operador desconhecido: {op}")
    
    def analisar_operacao_unaria(self, node: UnaryOp) -> str:
        """Analisa uma operação unária e retorna seu tipo."""
        operand_type = self.analisar_expressao(node.operand)
        
        if node.operator == 'nao':
            # Negação lógica: booleano -> booleano
            if operand_type != 'booleano':
                raise SemanticError(
                    f"Operador 'nao' requer operando booleano, mas recebeu {operand_type}"
                )
            node.expr_type = 'booleano'
            return 'booleano'
        
        elif node.operator == '-':
            # Menos unário: inteiro -> inteiro
            if operand_type != 'inteiro':
                raise SemanticError(
                    f"Operador '-' unário requer operando inteiro, mas recebeu {operand_type}"
                )
            node.expr_type = 'inteiro'
            return 'inteiro'
        
        else:
            raise SemanticError(f"Operador unário desconhecido: {node.operator}")
    
    def analisar_identificador(self, node: Identifier) -> str:
        """Analisa um identificador e retorna seu tipo."""
        symbol = self.symbol_table.lookup(node.name)
        if symbol is None:
            raise SemanticError(f"Variável '{node.name}' não foi declarada")
        
        if symbol.category != 'var':
            raise SemanticError(f"'{node.name}' não é uma variável")
        
        node.expr_type = symbol.symbol_type
        return symbol.symbol_type

