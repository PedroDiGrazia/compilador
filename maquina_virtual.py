#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Máquina Virtual Didática (MVD)
Implementação da máquina virtual para executar código assembly gerado pelo compilador LPD.
"""

import sys
from typing import List, Tuple, Optional


class ErroMVD(Exception):
    """Exceção base para erros da MVD."""
    pass


class MaquinaVirtual:
    """
    Máquina Virtual Didática (MVD) - Executa código assembly gerado pelo compilador LPD.
    
    Características:
    - Máquina a pilha
    - Memória de dados M (pilha)
    - Memória de programa P (instruções)
    - Registrador i (endereço da próxima instrução)
    - Registrador s (topo da pilha)
    
    Instruções suportadas:
    - START: Inicializa programa
    - ALLOC m,n: Aloca n posições a partir de m
    - DALLOC m,n: Desaloca n posições
    - LDC k: Carrega constante k
    - LDV n: Carrega valor de M[n]
    - STR n: Armazena valor em M[n]
    - ADD, SUB, MULT, DIVI: Operações aritméticas
    - INV: Inverte sinal
    - AND, OR, NEG: Operações lógicas
    - CME, CMA, CEQ, CDIF, CMEQ, CMAQ: Comparações
    - JMP p, JMPF p: Desvios
    - NULL: Marcador de label
    - RD: Leitura
    - PRN: Impressão
    - CALL p: Chama procedimento/função
    - RETURN, RETURNF: Retorna de procedimento/função
    - HLT: Para execução
    """
    
    def __init__(self, tamanho_pilha: int = 10000):
        """
        Inicializa a Máquina Virtual.
        
        Args:
            tamanho_pilha: Tamanho máximo da pilha de dados
        """
        # Memória de dados (pilha)
        self.M: List[int] = [0] * tamanho_pilha
        
        # Memória de programa (instruções)
        self.P: List[Tuple[str, List]] = []
        
        # Labels para desvios
        self.labels: dict = {}
        
        # Registradores
        self.i: int = 0  # Program counter
        self.s: int = -1  # Stack pointer
        
        # Estado
        self.executando: bool = False
        self.debug: bool = False
        
    def carregar_programa(self, arquivo_asm: str):
        """
        Carrega programa assembly na memória.
        
        Args:
            arquivo_asm: Caminho para o arquivo .asm
        """
        try:
            with open(arquivo_asm, 'r', encoding='utf-8') as f:
                linhas = f.readlines()
        except FileNotFoundError:
            raise ErroMVD(f"Arquivo não encontrado: {arquivo_asm}")
        
        endereco = 0
        for num_linha, linha in enumerate(linhas, 1):
            linha = linha.strip()
            
            # Ignora linhas vazias e comentários
            if not linha or linha.startswith('#') or linha.startswith(';'):
                continue
            
            # Remove comentários inline
            if '#' in linha:
                linha = linha[:linha.index('#')].strip()
            if ';' in linha:
                linha = linha[:linha.index(';')].strip()
            
            # Processa labels (formato: "LABEL:" ou "LABEL NULL")
            if linha.endswith(':'):
                label = linha[:-1]
                self.labels[label] = endereco
                continue
            
            # Parseia instrução
            partes = linha.split()
            if not partes:
                continue
            
            # Verifica se é um label seguido de instrução (ex: "L0 NULL")
            if len(partes) >= 2 and not partes[0].upper() in ['START', 'ALLOC', 'DALLOC', 'LDC', 'LDV', 'STR', 
                                                                 'ADD', 'SUB', 'MULT', 'DIVI', 'INV',
                                                                 'AND', 'OR', 'NEG',
                                                                 'CME', 'CMA', 'CEQ', 'CDIF', 'CMEQ', 'CMAQ',
                                                                 'JMP', 'JMPF', 'NULL', 'RD', 'PRN',
                                                                 'CALL', 'RETURN', 'RETURNF', 'HLT']:
                # É um label seguido de instrução
                label = partes[0]
                self.labels[label] = endereco
                partes = partes[1:]  # Remove o label
            
            instrucao = partes[0].upper()
            operandos = []
            
            # Processa operandos
            if len(partes) > 1:
                # Junta o resto
                resto = ' '.join(partes[1:])
                
                # Suporta separação por vírgula OU espaço
                # Primeiro tenta separar por vírgula, se não houver vírgula, usa espaço
                if ',' in resto:
                    ops_list = resto.split(',')
                else:
                    ops_list = resto.split()
                
                for op in ops_list:
                    op = op.strip()
                    if op:
                        # Tenta converter para inteiro, senão mantém como string (label)
                        try:
                            operandos.append(int(op))
                        except ValueError:
                            operandos.append(op)
            
            self.P.append((instrucao, operandos))
            endereco += 1
        
        if self.debug:
            print(f"Programa carregado: {len(self.P)} instruções")
            print(f"Labels: {self.labels}")
    
    def executar(self, entrada: Optional[List[int]] = None, debug: bool = False):
        """
        Executa o programa carregado.
        
        Args:
            entrada: Lista de valores inteiros para entrada (comandos RD)
            debug: Se True, imprime informações de debug
        
        Returns:
            Lista de valores impressos (comandos PRN)
        """
        self.debug = debug
        self.executando = True
        self.i = 0
        self.s = -1
        
        # Fila de entrada
        self.entrada = entrada if entrada else []
        self.indice_entrada = 0
        
        # Saída
        self.saida = []
        
        try:
            while self.executando and self.i < len(self.P):
                instrucao, operandos = self.P[self.i]
                
                if self.debug:
                    print(f"[{self.i:3d}] {instrucao:8s} {operandos} | s={self.s} | M[s]={self.M[self.s] if self.s >= 0 else 'N/A'}")
                
                # Decodifica e executa instrução
                self._executar_instrucao(instrucao, operandos)
                
        except Exception as e:
            raise ErroMVD(f"Erro na linha {self.i}: {instrucao} {operandos} - {str(e)}")
        
        return self.saida
    
    def _executar_instrucao(self, instr: str, ops: List):
        """Executa uma instrução específica."""
        
        # START - Inicializa programa
        if instr == 'START':
            self.s = -1
            self.i += 1
        
        # ALLOC m,n - Aloca memória
        elif instr == 'ALLOC':
            if len(ops) != 2:
                raise ErroMVD(f"ALLOC espera 2 operandos, recebeu {len(ops)}")
            m, n = ops[0], ops[1]
            for k in range(n):
                self.s += 1
                if self.s >= len(self.M):
                    raise ErroMVD("Stack overflow")
                self.M[self.s] = self.M[m + k]
            self.i += 1
        
        # DALLOC m,n - Desaloca memória
        elif instr == 'DALLOC':
            if len(ops) != 2:
                raise ErroMVD(f"DALLOC espera 2 operandos, recebeu {len(ops)}")
            m, n = ops[0], ops[1]
            for k in range(n - 1, -1, -1):
                if self.s < 0:
                    raise ErroMVD("Stack underflow")
                self.M[m + k] = self.M[self.s]
                self.s -= 1
            self.i += 1
        
        # LDC k - Carrega constante
        elif instr == 'LDC':
            if len(ops) != 1:
                raise ErroMVD(f"LDC espera 1 operando")
            self.s += 1
            if self.s >= len(self.M):
                raise ErroMVD("Stack overflow")
            self.M[self.s] = ops[0]
            self.i += 1
        
        # LDV n - Carrega valor
        elif instr == 'LDV':
            if len(ops) != 1:
                raise ErroMVD(f"LDV espera 1 operando")
            self.s += 1
            if self.s >= len(self.M):
                raise ErroMVD("Stack overflow")
            self.M[self.s] = self.M[ops[0]]
            self.i += 1
        
        # STR n - Armazena valor
        elif instr == 'STR':
            if len(ops) != 1:
                raise ErroMVD(f"STR espera 1 operando")
            if self.s < 0:
                raise ErroMVD("Stack underflow")
            self.M[ops[0]] = self.M[self.s]
            self.s -= 1
            self.i += 1
        
        # ADD - Adição
        elif instr == 'ADD':
            if self.s < 1:
                raise ErroMVD("Stack underflow em ADD")
            self.M[self.s - 1] = self.M[self.s - 1] + self.M[self.s]
            self.s -= 1
            self.i += 1
        
        # SUB - Subtração
        elif instr == 'SUB':
            if self.s < 1:
                raise ErroMVD("Stack underflow em SUB")
            self.M[self.s - 1] = self.M[self.s - 1] - self.M[self.s]
            self.s -= 1
            self.i += 1
        
        # MULT - Multiplicação
        elif instr == 'MULT':
            if self.s < 1:
                raise ErroMVD("Stack underflow em MULT")
            self.M[self.s - 1] = self.M[self.s - 1] * self.M[self.s]
            self.s -= 1
            self.i += 1
        
        # DIVI - Divisão inteira
        elif instr == 'DIVI':
            if self.s < 1:
                raise ErroMVD("Stack underflow em DIVI")
            if self.M[self.s] == 0:
                raise ErroMVD("Divisão por zero")
            self.M[self.s - 1] = self.M[self.s - 1] // self.M[self.s]
            self.s -= 1
            self.i += 1
        
        # INV - Inverte sinal
        elif instr == 'INV':
            if self.s < 0:
                raise ErroMVD("Stack underflow em INV")
            self.M[self.s] = -self.M[self.s]
            self.i += 1
        
        # AND - Conjunção lógica
        elif instr == 'AND':
            if self.s < 1:
                raise ErroMVD("Stack underflow em AND")
            self.M[self.s - 1] = 1 if (self.M[self.s - 1] == 1 and self.M[self.s] == 1) else 0
            self.s -= 1
            self.i += 1
        
        # OR - Disjunção lógica
        elif instr == 'OR':
            if self.s < 1:
                raise ErroMVD("Stack underflow em OR")
            self.M[self.s - 1] = 1 if (self.M[self.s - 1] == 1 or self.M[self.s] == 1) else 0
            self.s -= 1
            self.i += 1
        
        # NEG - Negação lógica
        elif instr == 'NEG':
            if self.s < 0:
                raise ErroMVD("Stack underflow em NEG")
            self.M[self.s] = 1 - self.M[self.s]
            self.i += 1
        
        # CME - Comparar menor
        elif instr == 'CME':
            if self.s < 1:
                raise ErroMVD("Stack underflow em CME")
            self.M[self.s - 1] = 1 if self.M[self.s - 1] < self.M[self.s] else 0
            self.s -= 1
            self.i += 1
        
        # CMA - Comparar maior
        elif instr == 'CMA':
            if self.s < 1:
                raise ErroMVD("Stack underflow em CMA")
            self.M[self.s - 1] = 1 if self.M[self.s - 1] > self.M[self.s] else 0
            self.s -= 1
            self.i += 1
        
        # CEQ - Comparar igual
        elif instr == 'CEQ':
            if self.s < 1:
                raise ErroMVD("Stack underflow em CEQ")
            self.M[self.s - 1] = 1 if self.M[self.s - 1] == self.M[self.s] else 0
            self.s -= 1
            self.i += 1
        
        # CDIF - Comparar diferente
        elif instr == 'CDIF':
            if self.s < 1:
                raise ErroMVD("Stack underflow em CDIF")
            self.M[self.s - 1] = 1 if self.M[self.s - 1] != self.M[self.s] else 0
            self.s -= 1
            self.i += 1
        
        # CMEQ - Comparar menor ou igual
        elif instr == 'CMEQ':
            if self.s < 1:
                raise ErroMVD("Stack underflow em CMEQ")
            self.M[self.s - 1] = 1 if self.M[self.s - 1] <= self.M[self.s] else 0
            self.s -= 1
            self.i += 1
        
        # CMAQ - Comparar maior ou igual
        elif instr == 'CMAQ':
            if self.s < 1:
                raise ErroMVD("Stack underflow em CMAQ")
            self.M[self.s - 1] = 1 if self.M[self.s - 1] >= self.M[self.s] else 0
            self.s -= 1
            self.i += 1
        
        # JMP p - Desvio incondicional
        elif instr == 'JMP':
            if len(ops) != 1:
                raise ErroMVD(f"JMP espera 1 operando")
            label = ops[0]
            # Tenta buscar como string primeiro (labels numéricos são armazenados como string)
            label_str = str(label)
            if label_str in self.labels:
                self.i = self.labels[label_str]
            elif isinstance(label, str) and label in self.labels:
                self.i = self.labels[label]
            else:
                # Assume que é um endereço direto
                self.i = int(label) if isinstance(label, str) else label
        
        # JMPF p - Desvio se falso
        elif instr == 'JMPF':
            if len(ops) != 1:
                raise ErroMVD(f"JMPF espera 1 operando")
            if self.s < 0:
                raise ErroMVD("Stack underflow em JMPF")
            
            label = ops[0]
            if self.M[self.s] == 0:
                # Tenta buscar como string primeiro (labels numéricos são armazenados como string)
                label_str = str(label)
                if label_str in self.labels:
                    self.i = self.labels[label_str]
                elif isinstance(label, str) and label in self.labels:
                    self.i = self.labels[label]
                else:
                    self.i = int(label) if isinstance(label, str) else label
            else:
                self.i += 1
            self.s -= 1
        
        # NULL - Nada (marcador de label)
        elif instr == 'NULL':
            self.i += 1
        
        # RD - Leitura
        elif instr == 'RD':
            self.s += 1
            if self.s >= len(self.M):
                raise ErroMVD("Stack overflow")
            
            if self.indice_entrada < len(self.entrada):
                self.M[self.s] = self.entrada[self.indice_entrada]
                self.indice_entrada += 1
            else:
                # Lê da entrada padrão
                try:
                    valor = int(input("Digite um valor inteiro: "))
                    self.M[self.s] = valor
                except ValueError:
                    raise ErroMVD("Entrada inválida: esperado inteiro")
            self.i += 1
        
        # PRN - Impressão
        elif instr == 'PRN':
            if self.s < 0:
                raise ErroMVD("Stack underflow em PRN")
            print(self.M[self.s])
            self.saida.append(self.M[self.s])
            self.s -= 1
            self.i += 1
        
        # CALL p - Chama procedimento/função
        elif instr == 'CALL':
            if len(ops) != 1:
                raise ErroMVD(f"CALL espera 1 operando")
            self.s += 1
            if self.s >= len(self.M):
                raise ErroMVD("Stack overflow")
            self.M[self.s] = self.i + 1
            
            label = ops[0]
            # Tenta buscar como string primeiro (labels numéricos são armazenados como string)
            label_str = str(label)
            if label_str in self.labels:
                self.i = self.labels[label_str]
            elif isinstance(label, str) and label in self.labels:
                self.i = self.labels[label]
            else:
                self.i = int(label) if isinstance(label, str) else label
        
        # RETURN - Retorna de procedimento
        elif instr == 'RETURN':
            if self.s < 0:
                raise ErroMVD("Stack underflow em RETURN")
            self.i = self.M[self.s]
            self.s -= 1
        
                # RETURNF - Retorna de função (com valor)
        elif instr == 'RETURNF':
            if self.s < 1:
                raise ErroMVD("Stack underflow em RETURNF")
            # Convenção:
            #   antes do RETURNF:
            #       M[s-1] = endereço de retorno (empilhado pelo CALL)
            #       M[s]   = valor de retorno
            valor_retorno = self.M[self.s]
            endereco_retorno = self.M[self.s - 1]
            # move o valor de retorno para a posição do endereço
            self.M[self.s - 1] = valor_retorno
            # ajusta topo da pilha
            self.s -= 1
            # volta para o ponto de chamada
            self.i = endereco_retorno
       
        # HLT - Para execução
        elif instr == 'HLT':
            self.executando = False
        
        else:
            raise ErroMVD(f"Instrução desconhecida: {instr}")


def main():
    """Função principal para executar a MVD via linha de comando."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Máquina Virtual Didática (MVD) - Executa código assembly LPD'
    )
    parser.add_argument('arquivo', help='Arquivo .asm para executar')
    parser.add_argument('-d', '--debug', action='store_true', help='Modo debug')
    parser.add_argument('-i', '--input', nargs='*', type=int, help='Valores de entrada')
    
    args = parser.parse_args()
    
    try:
        mv = MaquinaVirtual()
        mv.carregar_programa(args.arquivo)
        
        print("=" * 60)
        print("Máquina Virtual Didática (MVD)")
        print("=" * 60)
        print(f"Arquivo: {args.arquivo}")
        print(f"Instruções carregadas: {len(mv.P)}")
        print("=" * 60)
        
        if args.input:
            print(f"Entrada: {args.input}")
            print("=" * 60)
        
        print("\nSaída do programa:\n")
        saida = mv.executar(entrada=args.input, debug=args.debug)
        
        print("\n" + "=" * 60)
        print("Execução concluída com sucesso!")
        print("=" * 60)
        
    except ErroMVD as e:
        print(f"\n[ERRO] Erro na MVD: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n[AVISO] Execução interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERRO] Erro inesperado: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

