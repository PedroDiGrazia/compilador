"""
Semantic Analyzer - Analisador Semântico
Realiza análise semântica da AST: verificação de tipos, declarações e compatibilidade.
"""

from ast_nodes import *
from symbol_table import SymbolTable, Symbol


class SemanticError(Exception):
    """Exceção para erros semânticos."""
    def __init__(self, message: str):
        # message aqui é só o texto "limpo"; o prefixo é adicionado aqui
        super().__init__(f"Erro semântico: {message}")


class SemanticAnalyzer:
    """
    Analisador semântico que percorre a AST verificando:
    - Declaração antes do uso
    - Tipos compatíveis
    - Declaração única (aproximação, sem escopos reais)
    - Operadores compatíveis com tipos
    """
    
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []
    
    def analyze(self, program: Program) -> SymbolTable:
        """
        Analisa semanticamente o programa e retorna a tabela de símbolos.
        Se houver erros, levanta SemanticError com todos eles.
        """
        try:
            self.visit_program(program)
        except SemanticError as e:
            # Remove prefixo duplicado se existir
            msg = str(e)
            prefix = "Erro semântico: "
            if msg.startswith(prefix):
                msg = msg[len(prefix):]
            self.errors.append(msg)
        
        if self.errors:
            # Junta todos os erros em uma única mensagem
            raise SemanticError("\n".join(self.errors))
        
        return self.symbol_table
    
    # ==================== PROGRAMA ====================
    
    def visit_program(self, node: Program):
        """
        Programa LPD:
          - declara variáveis globais
          - declara cabeçalhos de procedimentos e funções
          - declara variáveis locais de TODOS os blocos de subrotinas
          - analisa o comando composto principal
        """
        # 1) Variáveis globais
        if node.var_declarations:
            self.visit_var_declarations(node.var_declarations)

        # 2) Cabeçalhos de procedimentos de topo
        for proc in node.procedures:
            try:
                # categoria = 'procedimento', tipo simbólico genérico
                self.symbol_table.declare(proc.name, "procedimento", "procedimento")
            except Exception as e:
                raise SemanticError(str(e))

        # 3) Cabeçalhos de funções de topo
        for func in node.functions:
            try:
                # symbol_type = tipo de retorno ('inteiro' ou 'booleano')
                self.symbol_table.declare(func.name, func.return_type, "funcao")
            except Exception as e:
                raise SemanticError(str(e))

        # 4) Declara variáveis locais (aproximação, sem escopo real) em TODAS as subrotinas
        self._declare_locals_in_block_list(node.procedures, node.functions)

        # 5) Analisa apenas o corpo principal (o codegen trata o corpo das subrotinas)
        self.visit_compound_command(node.compound_command)

    # ---------- Helpers para variáveis locais em blocos ----------

    def _declare_locals_in_block_list(self, procedures: list, functions: list):
        """
        Declara variáveis locais recursivamente em todos os blocos de
        procedimentos e funções (incluindo os aninhados).
        """
        for proc in procedures:
            self._declare_locals_in_block(proc.block)
        for func in functions:
            self._declare_locals_in_block(func.block)

    def _declare_locals_in_block(self, block: Block):
        """
        Declara variáveis locais de um bloco e depois entra recursivamente
        nos procedimentos/funções declarados dentro dele.
        """
        if block.var_declarations:
            self.visit_local_var_declarations(block.var_declarations)

        # Procedimentos e funções aninhados
        self._declare_locals_in_block_list(block.procedures, block.functions)
    
    # ==================== DECLARAÇÕES DE VARIÁVEIS ====================
    
    def visit_var_declarations(self, node: VarDeclarations):
        """Declarações de variáveis globais."""
        for decl in node.declarations:
            self.visit_var_declaration(decl)
    
    def visit_var_declaration(self, node: VarDeclaration):
        """Declara uma declaração de variável (global)."""
        for identifier in node.identifiers:
            try:
                self.symbol_table.declare(identifier, node.var_type, 'var')
            except Exception as e:
                # Duplicata global ainda é erro
                raise SemanticError(str(e))

    # ---- Versão para variáveis locais (subrotinas) ----
    def visit_local_var_declarations(self, node: VarDeclarations):
        for decl in node.declarations:
            self.visit_local_var_declaration(decl)

    def visit_local_var_declaration(self, node: VarDeclaration):
        """
        Declara variáveis locais de funções/procedimentos.

        Aproximação: se o identificador já existe na tabela (por exemplo, global),
        não redeclara para evitar erro de duplicata em uma tabela sem escopos.
        No exemplo da apostila (mesmo nome global/local), isso faz o nome usar
        o endereço global.
        """
        for identifier in node.identifiers:
            # Se já existe algum símbolo com esse nome, não redeclara
            if self.symbol_table.lookup(identifier) is not None:
                continue

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

