"""
Semantic Analyzer - Analisador Semântico
Realiza análise semântica da AST: verificação de tipos, declarações e compatibilidade.
Utiliza escopos hierárquicos para suportar variáveis locais e shadowing.
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
    - Declaração única por escopo (permite shadowing entre escopos)
    - Operadores compatíveis com tipos
    
    Implementa escopos hierárquicos conforme notas de aula (seção 7.7):
    - Cada função/procedimento cria um novo escopo
    - Variáveis locais podem ter mesmo nome que globais (shadowing)
    - Endereços são calculados sequencialmente por escopo
    """
    
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []
        self.current_function = None  # Nome da função atual (para verificar atribuição de retorno)
    
    def analyze(self, program: Program) -> SymbolTable:
        """
        Analisa semanticamente o programa e retorna a tabela de símbolos.
        Se houver erros, levanta SemanticError com todos eles.
        """
        try:
            self.visit_program(program)
        except SemanticError as e:
            msg = str(e)
            prefix = "Erro semântico: "
            if msg.startswith(prefix):
                msg = msg[len(prefix):]
            self.errors.append(msg)
        
        if self.errors:
            raise SemanticError("\n".join(self.errors))
        
        return self.symbol_table
    
    # ==================== PROGRAMA ====================
    
    def visit_program(self, node: Program):
        """
        Programa LPD:
          1. Reserva posições para retorno de funções do nível global
          2. Declara variáveis globais
          3. Processa funções e procedimentos (com seus escopos)
          4. Analisa o comando composto principal
        """
        # 1) Primeiro, reserva posições de retorno para TODAS as funções do nível global
        # Isso deve vir ANTES das variáveis globais
        for func in node.functions:
            try:
                self.symbol_table.declare_function_return(func.name, func.return_type)
            except Exception as e:
                raise SemanticError(str(e))
        
        # 2) Declara variáveis globais
        if node.var_declarations:
            self.visit_var_declarations(node.var_declarations)
        
        # 3) Declara procedimentos do nível global (sem alocação de memória)
        for proc in node.procedures:
            try:
                self.symbol_table.declare_procedure(proc.name)
            except Exception as e:
                raise SemanticError(str(e))
        
        # 4) Processa blocos de funções e procedimentos (com escopos aninhados)
        for func in node.functions:
            self.visit_function(func)
        
        for proc in node.procedures:
            self.visit_procedure(proc)
        
        # 5) Analisa o corpo principal
        self.visit_compound_command(node.compound_command)
    
    # ==================== FUNÇÕES E PROCEDIMENTOS ====================
    
    def visit_function(self, node: Function):
        """
        Processa uma função:
        - Entra em novo escopo
        - Declara variáveis locais
        - Processa subrotinas aninhadas
        - Analisa comandos
        - Sai do escopo
        """
        # Calcula endereço base para este escopo
        base_addr = self.symbol_table.get_next_address()
        
        # Entra no escopo da função
        self.symbol_table.enter_scope(base_addr)
        
        old_function = self.current_function
        self.current_function = node.name
        
        # Processa o bloco da função
        self._process_block(node.block)
        
        self.current_function = old_function
        
        # Sai do escopo
        self.symbol_table.exit_scope()
    
    def visit_procedure(self, node: Procedure):
        """
        Processa um procedimento:
        - Entra em novo escopo
        - Declara variáveis locais
        - Processa subrotinas aninhadas
        - Analisa comandos
        - Sai do escopo
        """
        # Calcula endereço base para este escopo
        base_addr = self.symbol_table.get_next_address()
        
        # Entra no escopo do procedimento
        self.symbol_table.enter_scope(base_addr)
        
        # Processa o bloco do procedimento
        self._process_block(node.block)
        
        # Sai do escopo
        self.symbol_table.exit_scope()
    
    def _process_block(self, block: Block):
        """
        Processa um bloco (comum a funções e procedimentos):
        - Reserva posições de retorno para funções aninhadas
        - Declara variáveis locais
        - Declara procedimentos aninhados
        - Processa subrotinas aninhadas recursivamente
        - Analisa comandos
        """
        # 1) Reserva posições de retorno para funções aninhadas
        for func in block.functions:
            try:
                self.symbol_table.declare_function_return(func.name, func.return_type)
            except Exception as e:
                raise SemanticError(str(e))
        
        # 2) Declara variáveis locais
        if block.var_declarations:
            self.visit_var_declarations(block.var_declarations)
        
        # 3) Declara procedimentos aninhados
        for proc in block.procedures:
            try:
                self.symbol_table.declare_procedure(proc.name)
            except Exception as e:
                raise SemanticError(str(e))
        
        # 4) Processa subrotinas aninhadas (recursivamente)
        for func in block.functions:
            self.visit_function(func)
        
        for proc in block.procedures:
            self.visit_procedure(proc)
        
        # 5) Analisa os comandos do bloco
        self.visit_compound_command(block.compound_command)
    
    # ==================== DECLARAÇÕES DE VARIÁVEIS ====================
    
    def visit_var_declarations(self, node: VarDeclarations):
        """Declarações de variáveis."""
        for decl in node.declarations:
            self.visit_var_declaration(decl)
    
    def visit_var_declaration(self, node: VarDeclaration):
        """
        Declara variáveis no escopo atual.
        Permite shadowing (variável local com mesmo nome que global).
        """
        for identifier in node.identifiers:
            try:
                self.symbol_table.declare(identifier, node.var_type, 'var')
            except Exception as e:
                raise SemanticError(str(e))
    
    # ==================== COMANDOS ====================
    
    def visit_compound_command(self, node: CompoundCommand):
        for command in node.commands:
            self.visit_command(command)
    
    def visit_command(self, node: Command):
        if isinstance(node, Assignment):
            self.visit_assignment(node)
        elif isinstance(node, ReadCommand):
            self.visit_read_command(node)
        elif isinstance(node, WriteCommand):
            self.visit_write_command(node)
        elif isinstance(node, IfCommand):
            self.visit_if_command(node)
        elif isinstance(node, WhileCommand):
            self.visit_while_command(node)
        elif isinstance(node, CompoundCommand):
            self.visit_compound_command(node)
        elif isinstance(node, ProcedureCall):
            self.visit_procedure_call(node)
        elif isinstance(node, EmptyCommand):
            pass
    
    def visit_assignment(self, node: Assignment):
        """
        Atribuição:
          - se id for variável  -> checa tipo
          - se id for função    -> trata como comando de retorno (soma := expr;)
        """
        symbol = self.symbol_table.lookup(node.identifier)
        if symbol is None:
            raise SemanticError(f"Identificador '{node.identifier}' não foi declarado")
        
        expr_type = self.visit_expression(node.expression)

        if symbol.category == 'var':
            if symbol.symbol_type != expr_type:
                raise SemanticError(
                    f"Tipo incompatível na atribuição: '{node.identifier}' é {symbol.symbol_type}, "
                    f"mas a expressão é {expr_type}"
                )

        elif symbol.category == 'funcao':
            # Comando de retorno da função
            if symbol.symbol_type != expr_type:
                raise SemanticError(
                    f"Tipo de retorno incompatível na função '{node.identifier}': "
                    f"esperado {symbol.symbol_type}, obtido {expr_type}"
                )

        else:
            raise SemanticError(
                f"'{node.identifier}' não pode receber atribuição (não é variável nem função)"
            )
    
    def visit_procedure_call(self, node: ProcedureCall):
        """Verifica chamada de procedimento."""
        symbol = self.symbol_table.lookup(node.name)
        if symbol is None:
            raise SemanticError(f"Procedimento '{node.name}' não foi declarado")
        if symbol.category != 'procedimento':
            raise SemanticError(f"'{node.name}' não é um procedimento")
    
    def visit_read_command(self, node: ReadCommand):
        symbol = self.symbol_table.lookup(node.identifier)
        if symbol is None:
            raise SemanticError(f"Variável '{node.identifier}' não foi declarada")
        if symbol.category != 'var':
            raise SemanticError(f"'{node.identifier}' não é uma variável")
    
    def visit_write_command(self, node: WriteCommand):
        self.visit_expression(node.expression)
    
    def visit_if_command(self, node: IfCommand):
        cond_type = self.visit_expression(node.condition)
        if cond_type != 'booleano':
            raise SemanticError(
                f"Condição do 'se' deve ser booleana, mas é {cond_type}"
            )
        self.visit_command(node.then_command)
        if node.else_command:
            self.visit_command(node.else_command)
    
    def visit_while_command(self, node: WhileCommand):
        cond_type = self.visit_expression(node.condition)
        if cond_type != 'booleano':
            raise SemanticError(
                f"Condição do 'enquanto' deve ser booleana, mas é {cond_type}"
            )
        self.visit_command(node.body)
    
    # ==================== EXPRESSÕES ====================
    
    def visit_expression(self, node: Expression) -> str:
        """
        Retorna o tipo da expressão: 'inteiro' ou 'booleano'.
        """
        if isinstance(node, BinaryOp):
            return self.visit_binary_op(node)
        elif isinstance(node, UnaryOp):
            return self.visit_unary_op(node)
        elif isinstance(node, Identifier):
            return self.visit_identifier(node)
        elif isinstance(node, Number):
            node.expr_type = 'inteiro'
            return 'inteiro'
        elif isinstance(node, Boolean):
            node.expr_type = 'booleano'
            return 'booleano'
        else:
            raise SemanticError(f"Tipo de expressão desconhecido: {type(node)}")
    
    def visit_binary_op(self, node: BinaryOp) -> str:
        left_type = self.visit_expression(node.left)
        right_type = self.visit_expression(node.right)
        op = node.operator
        
        # Operadores aritméticos
        if op in ['+', '-', '*', 'div']:
            if left_type != 'inteiro' or right_type != 'inteiro':
                raise SemanticError(
                    f"Operador '{op}' requer operandos inteiros, "
                    f"mas recebeu {left_type} e {right_type}"
                )
            node.expr_type = 'inteiro'
            return 'inteiro'
        
        # Operadores lógicos
        elif op in ['e', 'ou']:
            if left_type != 'booleano' or right_type != 'booleano':
                raise SemanticError(
                    f"Operador '{op}' requer operandos booleanos, "
                    f"mas recebeu {left_type} e {right_type}"
                )
            node.expr_type = 'booleano'
            return 'booleano'
        
        # Operadores relacionais
        elif op in ['=', '!=', '<', '<=', '>', '>=']:
            if left_type != right_type:
                raise SemanticError(
                    f"Operador '{op}' requer operandos do mesmo tipo, "
                    f"mas recebeu {left_type} e {right_type}"
                )
            if op in ['<', '<=', '>', '>='] and left_type != 'inteiro':
                raise SemanticError(
                    f"Operador '{op}' requer operandos inteiros, "
                    f"mas recebeu {left_type}"
                )
            node.expr_type = 'booleano'
            return 'booleano'
        
        else:
            raise SemanticError(f"Operador desconhecido: {op}")
    
    def visit_unary_op(self, node: UnaryOp) -> str:
        operand_type = self.visit_expression(node.operand)
        
        if node.operator == 'nao':
            if operand_type != 'booleano':
                raise SemanticError(
                    f"Operador 'nao' requer operando booleano, mas recebeu {operand_type}"
                )
            node.expr_type = 'booleano'
            return 'booleano'
        
        elif node.operator == '-':
            if operand_type != 'inteiro':
                raise SemanticError(
                    f"Operador '-' unário requer operando inteiro, mas recebeu {operand_type}"
                )
            node.expr_type = 'inteiro'
            return 'inteiro'
        
        else:
            raise SemanticError(f"Operador unário desconhecido: {node.operator}")
    
    def visit_identifier(self, node: Identifier) -> str:
        """
        Identificador pode ser:
          - variável (category='var')
          - função  (category='funcao') em expressão
        Procedimento não pode aparecer em expressão.
        """
        symbol = self.symbol_table.lookup(node.name)
        if symbol is None:
            raise SemanticError(f"Identificador '{node.name}' não foi declarado")
        
        if symbol.category == 'procedimento':
            raise SemanticError(f"Procedimento '{node.name}' não pode ser usado em expressões")
        
        node.expr_type = symbol.symbol_type
        return symbol.symbol_type
