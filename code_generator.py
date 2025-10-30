"""
Code Generator - Gerador de Código
Gera código intermediário (P-code style) a partir da AST anotada.
"""

from ast_nodes import *
from symbol_table import SymbolTable
from typing import List


class CodeGenerator:
    """
    Gerador de código intermediário para a linguagem LPD.
    Produz instruções conforme especificação das Notas de Aula (Máquina Virtual Didática - MVD).
    
    Instruções geradas (compatíveis com MVD):
    - START: Inicializa programa principal
    - HLT: Para execução
    - ALLOC m,n: Aloca memória (m=endereço base, n=quantidade)
    - DALLOC m,n: Desaloca memória
    - LDC k: Carrega constante k na pilha
    - LDV n: Carrega valor do endereço n na pilha
    - STR n: Armazena topo da pilha no endereço n
    - ADD: Soma (operação aritmética)
    - SUB: Subtração
    - MULT: Multiplicação
    - DIVI: Divisão inteira
    - INV: Inverte sinal (menos unário)
    - AND: Conjunção lógica
    - OR: Disjunção lógica
    - NEG: Negação lógica
    - CME: Comparar menor (<)
    - CMA: Comparar maior (>)
    - CEQ: Comparar igual (=)
    - CDIF: Comparar diferente (!=)
    - CMEQ: Comparar menor ou igual (<=)
    - CMAQ: Comparar maior ou igual (>=)
    - JMP p: Desvio incondicional para endereço p
    - JMPF p: Desvio condicional se falso
    - NULL: Nenhuma operação (marcador de label)
    - RD: Lê valor da entrada
    - PRN: Imprime topo da pilha
    - CALL p: Chama procedimento/função no endereço p
    - RETURN: Retorna de procedimento
    - RETURNF: Retorna de função (com valor no topo)
    """
    
    def __init__(self, symbol_table: SymbolTable):
        self.symbol_table = symbol_table
        self.instructions: List[str] = []
        self.label_counter = 0
    
    def generate(self, program: Program) -> List[str]:
        """
        Gera código para o programa completo.
        
        Args:
            program: Nó raiz da AST
        
        Returns:
            List[str]: Lista de instruções geradas
        """
        self.instructions = []
        
        # Inicializa programa principal
        self.emit("START")
        
        # Aloca memória para variáveis
        memory_size = self.symbol_table.get_memory_size()
        if memory_size > 0:
            # ALLOC m,n onde m=0 (base) e n=quantidade de variáveis
            self.emit(f"ALLOC 0,{memory_size}")
        
        # Gera código para o comando composto principal
        self.visit_compound_command(program.compound_command)
        
        # Desaloca memória
        if memory_size > 0:
            self.emit(f"DALLOC 0,{memory_size}")
        
        # Finaliza programa
        self.emit("HLT")
        
        return self.instructions
    
    def emit(self, instruction: str):
        """Emite uma instrução."""
        self.instructions.append(instruction)
    
    def new_label(self) -> str:
        """Gera um novo label único."""
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label
    
    # ==================== VISITADORES ====================
    
    def visit_compound_command(self, node: CompoundCommand):
        """Gera código para comando composto."""
        for command in node.commands:
            self.visit_command(command)
    
    def visit_command(self, node: Command):
        """Despacha para o visitador apropriado."""
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
        Gera código para atribuição: id := expressao
        Avalia expressão e armazena no endereço da variável.
        Instrução MVD: STR n
        """
        # Avalia a expressão (deixa resultado na pilha)
        self.visit_expression(node.expression)
        
        # Obtém endereço da variável
        symbol = self.symbol_table.lookup(node.identifier)
        address = symbol.memory_address
        
        # Armazena no endereço (STR conforme notas de aula)
        self.emit(f"STR {address}")
    
    def visit_read_command(self, node: ReadCommand):
        """
        Gera código para leitura: leia(id)
        Lê valor e armazena na variável.
        Instrução MVD: RD seguido de STR
        """
        # Lê valor (empilha) - RD conforme notas de aula
        self.emit("RD")
        
        # Obtém endereço da variável
        symbol = self.symbol_table.lookup(node.identifier)
        address = symbol.memory_address
        
        # Armazena (STR conforme notas de aula)
        self.emit(f"STR {address}")
    
    def visit_write_command(self, node: WriteCommand):
        """
        Gera código para escrita: escreva(expressao)
        Avalia expressão e imprime.
        Instrução MVD: PRN
        """
        # Avalia expressão (deixa resultado na pilha)
        self.visit_expression(node.expression)
        
        # Imprime (PRN conforme notas de aula)
        self.emit("PRN")
    
    def visit_if_command(self, node: IfCommand):
        """
        Gera código para condicional: se condição entao cmd1 [senao cmd2]
        Instruções MVD: JMPF (desvio se falso), JMP (desvio sempre), NULL (label)
        
        Estrutura conforme notas de aula:
            <avalia condição>
            JMPF label_else (ou label_fim se não tem else)
            <cmd then>
            JMP label_fim (se tem else)
        label_else:
            <cmd else>
        label_fim:
            NULL
        """
        label_else = self.new_label()
        label_fim = self.new_label()
        
        # Avalia condição
        self.visit_expression(node.condition)
        
        # Se falso, desvia (JMPF conforme notas de aula)
        if node.else_command:
            self.emit(f"JMPF {label_else}")
        else:
            self.emit(f"JMPF {label_fim}")
        
        # Comando then
        self.visit_command(node.then_command)
        
        # Se tem else, pula o else após executar then
        if node.else_command:
            self.emit(f"JMP {label_fim}")
            self.emit(f"{label_else} NULL")
            self.visit_command(node.else_command)
        
        # Label de fim (NULL conforme notas de aula)
        self.emit(f"{label_fim} NULL")
    
    def visit_while_command(self, node: WhileCommand):
        """
        Gera código para repetição: enquanto condição faca cmd
        Instruções MVD: JMPF, JMP, NULL
        
        Estrutura conforme notas de aula:
        label_inicio:
            <avalia condição>
            JMPF label_fim
            <cmd body>
            JMP label_inicio
        label_fim:
            NULL
        """
        label_inicio = self.new_label()
        label_fim = self.new_label()
        
        # Label de início do loop (NULL conforme notas de aula)
        self.emit(f"{label_inicio} NULL")
        
        # Avalia condição
        self.visit_expression(node.condition)
        
        # Se falso, sai do loop (JMPF conforme notas de aula)
        self.emit(f"JMPF {label_fim}")
        
        # Corpo do loop
        self.visit_command(node.body)
        
        # Volta para o início (JMP conforme notas de aula)
        self.emit(f"JMP {label_inicio}")
        
        # Label de fim (NULL conforme notas de aula)
        self.emit(f"{label_fim} NULL")
    
    def visit_expression(self, node: Expression):
        """Gera código para avaliar expressão (deixa resultado na pilha)."""
        if isinstance(node, BinaryOp):
            self.visit_binary_op(node)
        elif isinstance(node, UnaryOp):
            self.visit_unary_op(node)
        elif isinstance(node, Identifier):
            self.visit_identifier(node)
        elif isinstance(node, Number):
            # LDC conforme notas de aula (Load Constant)
            self.emit(f"LDC {node.value}")
        elif isinstance(node, Boolean):
            # True = 1, False = 0
            value = 1 if node.value else 0
            # LDC conforme notas de aula
            self.emit(f"LDC {value}")
    
    def visit_binary_op(self, node: BinaryOp):
        """
        Gera código para operação binária.
        Avalia operandos (empilha) e aplica operador.
        Instruções MVD conforme Notas de Aula.
        """
        # Avalia operandos
        self.visit_expression(node.left)
        self.visit_expression(node.right)
        
        # Aplica operador (nomes EXATOS das notas de aula)
        op_map = {
            '+': 'ADD',      # Somar
            '-': 'SUB',      # Subtrair
            '*': 'MULT',     # Multiplicar
            'div': 'DIVI',   # Dividir
            'e': 'AND',      # Conjunção
            'ou': 'OR',      # Disjunção
            '=': 'CEQ',      # Comparar igual
            '!=': 'CDIF',    # Comparar diferente
            '<': 'CME',      # Comparar menor
            '<=': 'CMEQ',    # Comparar menor ou igual
            '>': 'CMA',      # Comparar maior
            '>=': 'CMAQ'     # Comparar maior ou igual
        }
        
        instruction = op_map.get(node.operator)
        if instruction:
            self.emit(instruction)
        else:
            raise Exception(f"Operador desconhecido: {node.operator}")
    
    def visit_unary_op(self, node: UnaryOp):
        """
        Gera código para operação unária.
        Avalia operando e aplica operador.
        Instruções MVD: NEG (negação lógica), INV (inverter sinal)
        """
        if node.operator == 'nao':
            # Negação lógica (NEG conforme notas de aula)
            self.visit_expression(node.operand)
            self.emit("NEG")
        elif node.operator == '-':
            # Menos unário (INV conforme notas de aula)
            # INV (Inverter sinal): M[s]:=-M[s]
            self.visit_expression(node.operand)
            self.emit("INV")
        else:
            raise Exception(f"Operador unário desconhecido: {node.operator}")
    
    def visit_identifier(self, node: Identifier):
        """
        Gera código para carregar valor de variável.
        Instrução MVD: LDV n (Load Value)
        """
        symbol = self.symbol_table.lookup(node.name)
        address = symbol.memory_address
        # LDV conforme notas de aula (Load Value from address)
        self.emit(f"LDV {address}")
    
    def get_code(self) -> str:
        """Retorna o código gerado como string."""
        return "\n".join(self.instructions)
    
    def save_to_file(self, filename: str):
        """Salva o código gerado em arquivo."""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(self.get_code())

