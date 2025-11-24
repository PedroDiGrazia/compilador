# Code Generator - Gerador de Código
# Implementa geração de código para a MVD conforme notas de aula (seção 7.7)

from ast_nodes import *
from symbol_table import SymbolTable
from typing import List, Dict, Optional, Tuple


class CodeGenerator:
    """
    Gerador de código para a Máquina Virtual Didática (MVD).
    
    Implementa a estrutura de geração conforme notas de aula:
    - ALLOC/DALLOC separados por escopo
    - Subrotinas aninhadas geradas DENTRO da subrotina pai
    - Retorno de função via STR para endereço reservado + RETURN
    
    A tabela de símbolos é reconstruída durante a geração de código
    para manter os escopos corretos.
    """
    
    def __init__(self):
        self.instructions: List[str] = []
        self.label_counter = 1  # Começa em 1 conforme exemplo do professor
        
        # Mapeia nome de procedimento/função -> label numérico
        self.subroutine_labels: Dict[str, int] = {}
        
        # Nome da função atual (para tratar atribuição de retorno)
        self.current_function: Optional[str] = None
        
        # Tabela de símbolos (reconstruída durante geração)
        self.symbol_table: SymbolTable = None
        
        # Pilha de informações de ALLOC para gerar DALLOC
        self.alloc_stack: List[Tuple[int, int]] = []
    
    # ========== Infra básica ==========
    
    def emit(self, instruction: str):
        """Emite uma instrução."""
        self.instructions.append(instruction)
    
    def new_label(self) -> int:
        """Gera um novo label numérico."""
        label = self.label_counter
        self.label_counter += 1
        return label
    
    def get_subroutine_label(self, name: str) -> int:
        """Retorna (ou cria) o label associado à função/procedimento."""
        if name not in self.subroutine_labels:
            self.subroutine_labels[name] = self.new_label()
        return self.subroutine_labels[name]
    
    def emit_alloc(self, base_addr: int, count: int):
        """Emite ALLOC e registra para posterior DALLOC."""
        if count > 0:
            self.emit(f"ALLOC {base_addr} {count}")
            self.alloc_stack.append((base_addr, count))
    
    def emit_dalloc_from_stack(self):
        """Emite DALLOC para o último ALLOC da pilha."""
        if self.alloc_stack:
            base_addr, count = self.alloc_stack.pop()
            if count > 0:
                self.emit(f"DALLOC {base_addr} {count}")
    
    # ========== Geração principal ==========
    
    def generate(self, program: Program, symbol_table: SymbolTable = None) -> List[str]:
        """
        Gera código para o programa completo.
        
        Estrutura conforme notas de aula (seção 7.7):
        
        START
        ALLOC m,n      ; retorno de funções (se houver)
        ALLOC m,n      ; variáveis globais
        JMP Lmain      ; pula subrotinas
        
        [código das subrotinas]
        
        Lmain NULL
        [comandos principais]
        DALLOC m,n     ; variáveis globais
        DALLOC m,n     ; retorno de funções
        HLT
        """
        self.instructions = []
        self.label_counter = 1
        self.subroutine_labels = {}
        self.current_function = None
        self.alloc_stack = []
        
        # Cria uma nova tabela de símbolos para a geração de código
        self.symbol_table = SymbolTable()
        
        # START
        self.emit("START")
        
        # Calcula informações de alocação do escopo global
        func_return_count = len(program.functions)
        global_var_count = self._count_var_declarations(program.var_declarations)
        
        # Reserva posições de retorno para funções do nível global
        for func in program.functions:
            self.symbol_table.declare_function_return(func.name, func.return_type)
        
        # Declara variáveis globais na tabela
        if program.var_declarations:
            self._declare_vars(program.var_declarations)
        
        # Declara procedimentos do nível global
        for proc in program.procedures:
            self.symbol_table.declare_procedure(proc.name)
        
        # ALLOC para retorno de funções (se houver funções no nível global)
        if func_return_count > 0:
            self.emit_alloc(0, func_return_count)
        
        # ALLOC para variáveis globais
        if global_var_count > 0:
            base = func_return_count  # Começa após retornos de funções
            self.emit_alloc(base, global_var_count)
        
        # Verifica se há subrotinas
        has_subroutines = len(program.procedures) > 0 or len(program.functions) > 0
        
        # JMP para o corpo principal (pula subrotinas)
        main_label = self.new_label()
        if has_subroutines:
            self.emit(f"JMP {main_label}")
        
        # Gera código das subrotinas
        next_addr = func_return_count + global_var_count
        for func in program.functions:
            self._generate_function(func, next_addr)
        
        for proc in program.procedures:
            self._generate_procedure(proc, next_addr)
        
        # Corpo principal
        self.emit(f"{main_label} \tNULL")
        self.visit_compound_command(program.compound_command)
        
        # DALLOC na ordem inversa
        while self.alloc_stack:
            self.emit_dalloc_from_stack()
        
        # HLT
        self.emit("HLT")
        
        return self.instructions
    
    def _count_var_declarations(self, var_decls: Optional[VarDeclarations]) -> int:
        """Conta quantas variáveis são declaradas."""
        if var_decls is None:
            return 0
        count = 0
        for decl in var_decls.declarations:
            count += len(decl.identifiers)
        return count
    
    def _declare_vars(self, var_decls: VarDeclarations):
        """Declara variáveis na tabela de símbolos."""
        for decl in var_decls.declarations:
            for identifier in decl.identifiers:
                self.symbol_table.declare(identifier, decl.var_type, 'var')
    
    def _generate_function(self, node: Function, parent_next_addr: int):
        """
        Gera código para uma função.
        
        Estrutura:
        Lx NULL
        ALLOC m,n          ; variáveis locais
        JMP Lcorpo         ; pula subrotinas aninhadas (só se houver)
        [subrotinas aninhadas]
        Lcorpo NULL        ; (só se houver subrotinas aninhadas)
        [comandos]
        DALLOC m,n
        RETURN
        """
        label = self.get_subroutine_label(node.name)
        self.emit(f"{label} \tNULL")
        
        # Entra no escopo da função
        self.symbol_table.enter_scope(parent_next_addr)
        
        # Conta e declara variáveis locais (funções aninhadas + variáveis declaradas)
        func_return_count = len(node.block.functions)
        local_var_count = self._count_var_declarations(node.block.var_declarations)
        total_locals = func_return_count + local_var_count
        
        # Declara funções aninhadas (retorno)
        for func in node.block.functions:
            self.symbol_table.declare_function_return(func.name, func.return_type)
        
        # Declara variáveis locais
        if node.block.var_declarations:
            self._declare_vars(node.block.var_declarations)
        
        # Declara procedimentos aninhados
        for proc in node.block.procedures:
            self.symbol_table.declare_procedure(proc.name)
        
        # ALLOC para variáveis locais
        local_base = parent_next_addr
        if total_locals > 0:
            self.emit(f"ALLOC {local_base} {total_locals}")
        
        # Verifica se há subrotinas aninhadas
        has_nested = len(node.block.procedures) > 0 or len(node.block.functions) > 0
        
        # JMP para o corpo (pula subrotinas aninhadas) - só se houver
        body_label = None
        if has_nested:
            body_label = self.new_label()
            self.emit(f"JMP {body_label}")
        
        # Subrotinas aninhadas
        next_addr = local_base + total_locals
        for func in node.block.functions:
            self._generate_function(func, next_addr)
        for proc in node.block.procedures:
            self._generate_procedure(proc, next_addr)
        
        # Label do corpo da função (só se houver subrotinas aninhadas)
        if has_nested:
            self.emit(f"{body_label} \tNULL")
        
        old_function = self.current_function
        self.current_function = node.name
        
        self.visit_compound_command(node.block.compound_command)
        
        self.current_function = old_function
        
        # DALLOC e RETURN
        if total_locals > 0:
            self.emit(f"DALLOC {local_base} {total_locals}")
        self.emit("RETURN")
        
        # Sai do escopo
        self.symbol_table.exit_scope()
    
    def _generate_procedure(self, node: Procedure, parent_next_addr: int):
        """
        Gera código para um procedimento.
        
        Estrutura similar à função, mas sem valor de retorno.
        """
        label = self.get_subroutine_label(node.name)
        self.emit(f"{label} \tNULL")
        
        # Entra no escopo do procedimento
        self.symbol_table.enter_scope(parent_next_addr)
        
        # Conta e declara variáveis locais
        func_return_count = len(node.block.functions)
        local_var_count = self._count_var_declarations(node.block.var_declarations)
        total_locals = func_return_count + local_var_count
        
        # Declara funções aninhadas (retorno)
        for func in node.block.functions:
            self.symbol_table.declare_function_return(func.name, func.return_type)
        
        # Declara variáveis locais
        if node.block.var_declarations:
            self._declare_vars(node.block.var_declarations)
        
        # Declara procedimentos aninhados
        for proc in node.block.procedures:
            self.symbol_table.declare_procedure(proc.name)
        
        # ALLOC para variáveis locais
        local_base = parent_next_addr
        if total_locals > 0:
            self.emit(f"ALLOC {local_base} {total_locals}")
        
        # Verifica se há subrotinas aninhadas
        has_nested = len(node.block.procedures) > 0 or len(node.block.functions) > 0
        
        # JMP para o corpo (só se houver subrotinas aninhadas)
        body_label = None
        if has_nested:
            body_label = self.new_label()
            self.emit(f"JMP {body_label}")
        
        # Subrotinas aninhadas
        next_addr = local_base + total_locals
        for func in node.block.functions:
            self._generate_function(func, next_addr)
        for proc in node.block.procedures:
            self._generate_procedure(proc, next_addr)
        
        # Label do corpo do procedimento (só se houver subrotinas aninhadas)
        if has_nested:
            self.emit(f"{body_label} \tNULL")
        
        self.visit_compound_command(node.block.compound_command)
        
        # DALLOC e RETURN
        if total_locals > 0:
            self.emit(f"DALLOC {local_base} {total_locals}")
        self.emit("RETURN")
        
        # Sai do escopo
        self.symbol_table.exit_scope()
    
    # ========== Comandos ==========
    
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
        - Variável: avalia expressão + STR addr
        - Função (retorno): avalia expressão + STR addr_retorno
          (o RETURN será gerado no final da função)
        """
        symbol = self.symbol_table.lookup(node.identifier)
        if symbol is None:
            raise Exception(f"Identificador '{node.identifier}' não declarado (codegen)")
        
        # Avalia a expressão
        self.visit_expression(node.expression)
        
        # Armazena no endereço (funciona para variável e retorno de função)
        address = symbol.memory_address
        self.emit(f"STR {address}")
    
    def visit_read_command(self, node: ReadCommand):
        """
        Gera código para leitura: leia(id)
        """
        self.emit("RD")
        
        symbol = self.symbol_table.lookup(node.identifier)
        if symbol is None:
            raise Exception(f"Identificador '{node.identifier}' não declarado (codegen)")
        
        self.emit(f"STR {symbol.memory_address}")
    
    def visit_write_command(self, node: WriteCommand):
        self.visit_expression(node.expression)
        self.emit("PRN")
    
    def visit_if_command(self, node: IfCommand):
        """
        se E entao C1 [senao C2]
        """
        if node.else_command:
            label_else = self.new_label()
            label_fim = self.new_label()
            
            self.visit_expression(node.condition)
            self.emit(f"JMPF {label_else}")
            self.visit_command(node.then_command)
            self.emit(f"JMP {label_fim}")
            self.emit(f"{label_else} \tNULL")
            self.visit_command(node.else_command)
            self.emit(f"{label_fim} \tNULL")
        else:
            label_fim = self.new_label()
            
            self.visit_expression(node.condition)
            self.emit(f"JMPF {label_fim}")
            self.visit_command(node.then_command)
            self.emit(f"{label_fim} \tNULL")
    
    def visit_while_command(self, node: WhileCommand):
        """
        enquanto E faca C
        """
        label_inicio = self.new_label()
        label_fim = self.new_label()
        
        self.emit(f"{label_inicio} \tNULL")
        self.visit_expression(node.condition)
        self.emit(f"JMPF {label_fim}")
        self.visit_command(node.body)
        self.emit(f"JMP {label_inicio}")
        self.emit(f"{label_fim} \tNULL")
    
    def visit_procedure_call(self, node: ProcedureCall):
        label = self.get_subroutine_label(node.name)
        self.emit(f"CALL {label}")
    
    # ========== Expressões ==========
    
    def visit_expression(self, node: Expression):
        if isinstance(node, BinaryOp):
            self.visit_binary_op(node)
        elif isinstance(node, UnaryOp):
            self.visit_unary_op(node)
        elif isinstance(node, Identifier):
            self.visit_identifier(node)
        elif isinstance(node, Number):
            self.emit(f"LDC {node.value}")
        elif isinstance(node, Boolean):
            value = 1 if node.value else 0
            self.emit(f"LDC {value}")
    
    def visit_binary_op(self, node: BinaryOp):
        self.visit_expression(node.left)
        self.visit_expression(node.right)
        
        op_map = {
            '+': 'ADD',
            '-': 'SUB',
            '*': 'MULT',
            'div': 'DIVI',
            'e': 'AND',
            'ou': 'OR',
            '=': 'CEQ',
            '!=': 'CDIF',
            '<': 'CME',
            '<=': 'CMEQ',
            '>': 'CMA',
            '>=': 'CMAQ'
        }
        instr = op_map.get(node.operator)
        if not instr:
            raise Exception(f"Operador desconhecido: {node.operator}")
        self.emit(instr)
    
    def visit_unary_op(self, node: UnaryOp):
        self.visit_expression(node.operand)
        if node.operator == 'nao':
            self.emit("NEG")
        elif node.operator == '-':
            self.emit("INV")
        else:
            raise Exception(f"Operador unário desconhecido: {node.operator}")
    
    def visit_identifier(self, node: Identifier):
        """
        Identificador em expressão:
        - Variável: LDV addr
        - Função: CALL Lfunc, depois LDV addr_retorno
        """
        symbol = self.symbol_table.lookup(node.name)
        if symbol is None:
            raise Exception(f"Identificador '{node.name}' não declarado (codegen)")
        
        if symbol.category == 'var':
            self.emit(f"LDV {symbol.memory_address}")
        
        elif symbol.category == 'funcao':
            # Chamada de função em expressão
            # 1. CALL para executar a função (que armazena resultado em addr_retorno)
            # 2. LDV para carregar o valor de retorno
            label = self.get_subroutine_label(node.name)
            self.emit(f"CALL {label}")
            self.emit(f"LDV {symbol.memory_address}")
        
        else:
            raise Exception(f"'{node.name}' não pode ser usado como expressão")
    
    def get_code(self) -> str:
        """Retorna o código gerado como string."""
        return "\n".join(self.instructions)
    
    def save_to_file(self, filename: str):
        """Salva o código em um arquivo."""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(self.get_code())
