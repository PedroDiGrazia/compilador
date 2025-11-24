# Code Generator - Gerador de Código

from ast_nodes import *
from symbol_table import SymbolTable
from typing import List, Dict, Optional


class CodeGenerator:
    def __init__(self, symbol_table: SymbolTable):
        self.symbol_table = symbol_table
        self.instructions: List[str] = []
        self.label_counter = 0

        # mapeia nome de procedimento/função -> label (L0, L1, ...)
        self.subroutine_labels: Dict[str, str] = {}
        # nome da função em cujo corpo estamos (para tratar retorno)
        self.current_function: Optional[str] = None
    
    # ========== Infra básica ==========

    def emit(self, instruction: str):
        self.instructions.append(instruction)
    
    def new_label(self) -> str:
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label
    
    def get_subroutine_label(self, name: str) -> str:
        """Retorna (ou cria) o label associado à função/procedimento."""
        if name not in self.subroutine_labels:
            self.subroutine_labels[name] = self.new_label()
        return self.subroutine_labels[name]

    # ========== Geração principal ==========

    def generate(self, program: Program) -> List[str]:
        """
        Tradução semelhante às notas de aula:

        START
        ALLOC 0,k      ; variáveis globais
        JMP Lmain      ; pula corpo das subrotinas

        Lx NULL        ; procedimentos/funções
        ...
        RETURN / RETURNF

        Lmain NULL
        ... corpo principal ...
        DALLOC 0,k
        HLT
        """
        self.instructions = []
        self.label_counter = 0
        self.subroutine_labels = {}
        self.current_function = None
        
        # START
        self.emit("START")
        
        # Aloca memória para as variáveis (globais + o que sua SymbolTable contabiliza)
        memory_size = self.symbol_table.get_memory_size()
        if memory_size > 0:
            self.emit(f"ALLOC 0,{memory_size}")
        
        # Label para o corpo principal (como nas notas: pula subrotinas)
        main_label = self.new_label()
        self.emit(f"JMP {main_label}")
        
        # Gera código das sub-rotinas (se você tiver Program.procedures/functions)
        # Aqui assumo que o Program tem listas 'procedures' e 'functions'
        self._generate_subroutines(program.procedures, program.functions)
        
        # Corpo principal
        self.emit(f"{main_label} NULL")
        self.visit_compound_command(program.compound_command)
        
        # Desaloca memória e finaliza
        if memory_size > 0:
            self.emit(f"DALLOC 0,{memory_size}")
        self.emit("HLT")
        
        return self.instructions

    def _generate_subroutines(self, procedures: List[Procedure], functions: List[Function]):
        """Gera código para procedimentos e funções (nível atual)."""
        for proc in procedures:
            self.visit_procedure(proc)
        for func in functions:
            self.visit_function(func)

    def visit_procedure(self, node: Procedure):
        """
        procedimento Nome;
        var ...
        inicio
           ...
        fim;
        """
        label = self.get_subroutine_label(node.name)
        self.emit(f"{label} NULL")

        # Se quiser seguir 100% as notas, aqui entrariam ALLOC/DALLOC das variáveis locais.
        # Como não temos a contagem de locais por bloco na SymbolTable, não invento nada.
        # Parto da mesma convenção que você já usa: todos endereços vêm prontos da SymbolTable.

        # Corpo do procedimento
        self.visit_compound_command(node.block.compound_command)

        # Retorno de procedimento (sem valor)
        self.emit("RETURN")

        # Se houver subrotinas aninhadas, gera aqui:
        self._generate_subroutines(node.block.procedures, node.block.functions)

    def visit_function(self, node: Function):
        """
        funcao Nome: tipo;
        var ...
        inicio
           ...
        fim;
        """
        label = self.get_subroutine_label(node.name)
        self.emit(f"{label} NULL")

        old_function = self.current_function
        self.current_function = node.name

        # Corpo da função
        self.visit_compound_command(node.block.compound_command)

        # De acordo com as notas, a função termina com um comando de atribuição ao
        # próprio nome da função (Exp := Resultado;), que nós traduzimos como RETURNF.
        # Então aqui não preciso forçar RETURNF extra: assumo que o programador obedece
        # o padrão da apostila.

        self.current_function = old_function

        # Sub-rotinas aninhadas dentro da função (como ler/loop dentro de soma)
        self._generate_subroutines(node.block.procedures, node.block.functions)

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
        # chamada de procedimento (comando)
        elif isinstance(node, ProcedureCall):
            self.visit_procedure_call(node)
        elif isinstance(node, EmptyCommand):
            pass
    
    def visit_assignment(self, node: Assignment):
        """
        atribuicao ::= ID ":=" expressao

        Caso 1: ID é variável normal -> avalia expressão + STR addr
        Caso 2: ID é nome de função (dentro do corpo da função) -> avalia expressão + RETURNF
        """
        symbol = self.symbol_table.lookup(node.identifier)
        if symbol is None:
            raise Exception(f"Identificador '{node.identifier}' não declarado (codegen)")
        
        # Caso função: comando de retorno da função
        if symbol.category == 'funcao' and self.current_function == node.identifier:
            # avalia expressão (deixa valor de retorno no topo da pilha)
            self.visit_expression(node.expression)
            # RETURNF vai:
            #   - pegar M[s] = valor
            #   - M[s-1] = endereço de retorno (empilhado pelo CALL)
            #   - mover valor para a posição do endereço e voltar
            self.emit("RETURNF")
            return

        # Caso padrão: variável
        if symbol.category != 'var':
            raise Exception(f"'{node.identifier}' não pode receber atribuição aqui")

        # Avalia a expressão
        self.visit_expression(node.expression)
        
        # Obtém endereço e salva
        address = symbol.memory_address
        self.emit(f"STR {address}")
    
    def visit_read_command(self, node: ReadCommand):
        """
        Gera código para leitura: leia(id)
        Lê valor e armazena na variável.
        Instrução MVD: RD seguido de STR
        """
        # Lê valor (empilha)
        self.emit("RD")

        # Obtém endereço da variável
        symbol = self.symbol_table.lookup(node.identifier)
        if symbol is None:
            raise Exception(f"Identificador '{node.identifier}' não declarado (codegen)")

        address = symbol.memory_address

        # Armazena
        self.emit(f"STR {address}")

    def visit_write_command(self, node: WriteCommand):
        self.visit_expression(node.expression)
        self.emit("PRN")
    
    def visit_if_command(self, node: IfCommand):
        label_else = self.new_label()
        label_fim = self.new_label()
        
        self.visit_expression(node.condition)
        
        if node.else_command:
            self.emit(f"JMPF {label_else}")
        else:
            self.emit(f"JMPF {label_fim}")
        
        self.visit_command(node.then_command)
        
        if node.else_command:
            self.emit(f"JMP {label_fim}")
            self.emit(f"{label_else} NULL")
            self.visit_command(node.else_command)
        
        self.emit(f"{label_fim} NULL")
    
    def visit_while_command(self, node: WhileCommand):
        label_inicio = self.new_label()
        label_fim = self.new_label()
        
        self.emit(f"{label_inicio} NULL")
        self.visit_expression(node.condition)
        self.emit(f"JMPF {label_fim}")
        self.visit_command(node.body)
        self.emit(f"JMP {label_inicio}")
        self.emit(f"{label_fim} NULL")

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
        if node.operator == 'nao':
            self.visit_expression(node.operand)
            self.emit("NEG")
        elif node.operator == '-':
            self.visit_expression(node.operand)
            self.emit("INV")
        else:
            raise Exception(f"Operador unário desconhecido: {node.operator}")
    
    def visit_identifier(self, node: Identifier):
        """
        Se for variável -> LDV addr
        Se for função  -> CALL Lfunc
        (chamada de função conforme gramática: <chamada de função> ::= <identificador>)
        """
        symbol = self.symbol_table.lookup(node.name)
        if symbol is None:
            raise Exception(f"Identificador '{node.name}' não declarado (codegen)")
        
        # variável: carrega valor da memória
        if symbol.category == 'var':
            address = symbol.memory_address
            self.emit(f"LDV {address}")
        
        # função: gera chamada de função (CALL Lfunc),
        # RETURNF lá dentro vai deixar o valor de retorno no topo da pilha
        elif symbol.category == 'funcao':
            label = self.get_subroutine_label(node.name)
            self.emit(f"CALL {label}")
        
        # procedimento não pode aparecer em expressão
        else:  # 'procedimento' ou outra coisa
            raise Exception(f"'{node.name}' não pode ser usado como expressão aqui")

    def get_code(self) -> str:
        return "\n".join(self.instructions)
    
    def save_to_file(self, filename: str):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(self.get_code())

