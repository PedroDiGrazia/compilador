"""
Parser - Analisador Sintático
Implementa análise descendente recursiva para a gramática LPD.
"""

from typing import List, Optional
from tokens import Token, TokenType
from ast_nodes import *


class ParseError(Exception):
    """Exceção para erros sintáticos."""
    def __init__(self, message: str, token: Token):
        super().__init__(f"[{token.line}:{token.col}] Erro sintático: {message}")
        self.token = token
        self.line = token.line
        self.col = token.col


class Parser:
    """Analisador sintático descendente recursivo para LPD."""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current = tokens[0] if tokens else None
    
    def advance(self):
        """Avança para o próximo token."""
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
            self.current = self.tokens[self.pos]
    
    def peek(self, offset: int = 1) -> Optional[Token]:
        """Olha adiante sem consumir tokens."""
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return None
    
    def expect(self, token_type: TokenType, message: str = None) -> Token:
        """Consome um token do tipo esperado ou lança erro."""
        if self.current.type != token_type:
            if message is None:
                message = f"Esperado {token_type.name}, encontrado {self.current.type.name}"
            raise ParseError(message, self.current)
        token = self.current
        self.advance()
        return token
    
    def match(self, *token_types: TokenType) -> bool:
        """Verifica se o token atual é de um dos tipos dados."""
        return self.current.type in token_types
    
    def parse(self) -> Program:
        """Ponto de entrada do parser."""
        return self.programa()
    
    # ==================== PROGRAMA ====================
    
    def programa(self) -> Program:
        """
        programa ::= "programa" ID ";" bloco "."
        """
        self.expect(TokenType.PROGRAM, "Esperado 'programa'")
        name_token = self.expect(TokenType.ID, "Esperado identificador após 'programa'")
        name = name_token.value
        self.expect(TokenType.SEMI, "Esperado ';' após nome do programa")
        
        block = self.bloco()
        
        self.expect(TokenType.DOT, "Esperado '.' no final do programa")
        
        return Program(
            name=name,
            var_declarations=block.var_declarations,
            procedures=block.procedures,
            functions=block.functions,
            compound_command=block.compound_command
        )
    
    def bloco(self) -> Block:
        """
        bloco ::= [declaracao_variaveis] [declaracao_subrotinas] comando_composto
        """
        var_decls = None
        if self.match(TokenType.VAR):
            var_decls = self.declaracao_variaveis()
        
        procedures = []
        functions = []
        # TODO: implementar procedimentos e funções no futuro
        
        compound_cmd = self.comando_composto()
        
        return Block(
            var_declarations=var_decls,
            procedures=procedures,
            functions=functions,
            compound_command=compound_cmd
        )
    
    # ==================== DECLARAÇÕES ====================
    
    def declaracao_variaveis(self) -> VarDeclarations:
        """
        declaracao_variaveis ::= "var" declaracao {";" declaracao} ";"
        """
        self.expect(TokenType.VAR)
        declarations = []
        
        declarations.append(self.declaracao())
        self.expect(TokenType.SEMI, "Esperado ';' após declaração de variável")
        
        # Continua lendo declarações enquanto encontrar ID
        while self.match(TokenType.ID):
            declarations.append(self.declaracao())
            self.expect(TokenType.SEMI, "Esperado ';' após declaração de variável")
        
        return VarDeclarations(declarations=declarations)
    
    def declaracao(self) -> VarDeclaration:
        """
        declaracao ::= lista_ids ":" tipo
        lista_ids ::= ID {"," ID}
        """
        identifiers = []
        
        id_token = self.expect(TokenType.ID, "Esperado identificador")
        identifiers.append(id_token.value)
        
        while self.match(TokenType.COMMA):
            self.advance()  # consome ','
            id_token = self.expect(TokenType.ID, "Esperado identificador após ','")
            identifiers.append(id_token.value)
        
        self.expect(TokenType.COLON, "Esperado ':' após lista de identificadores")
        
        var_type = self.tipo()
        
        return VarDeclaration(identifiers=identifiers, var_type=var_type)
    
    def tipo(self) -> str:
        """
        tipo ::= "inteiro" | "booleano"
        """
        if self.match(TokenType.INTEIRO):
            self.advance()
            return "inteiro"
        elif self.match(TokenType.BOOLEANO):
            self.advance()
            return "booleano"
        else:
            raise ParseError("Esperado tipo 'inteiro' ou 'booleano'", self.current)
    
    # ==================== COMANDOS ====================
    
    def comando_composto(self) -> CompoundCommand:
        """
        comando_composto ::= "inicio" comandos "fim"
        comandos ::= comando {";" comando}
        """
        self.expect(TokenType.INICIO, "Esperado 'inicio'")
        
        commands = []
        
        # Primeiro comando (pode ser vazio se próximo token for 'fim')
        if not self.match(TokenType.FIM):
            commands.append(self.comando())
            
            # Comandos adicionais separados por ';'
            while self.match(TokenType.SEMI):
                self.advance()  # consome ';'
                # Verifica se não chegou no 'fim'
                if not self.match(TokenType.FIM):
                    commands.append(self.comando())
        
        self.expect(TokenType.FIM, "Esperado 'fim'")
        
        return CompoundCommand(commands=commands)
    
    def comando(self) -> Command:
        """
        comando ::= atribuicao | leitura | escrita | condicional | repeticao | comando_composto
        """
        # Atribuição: ID := ...
        if self.match(TokenType.ID):
            return self.atribuicao()
        
        # Leitura: leia(...)
        elif self.match(TokenType.LEIA):
            return self.leitura()
        
        # Escrita: escreva(...)
        elif self.match(TokenType.ESCREVA):
            return self.escrita()
        
        # Condicional: se ... entao ...
        elif self.match(TokenType.SE):
            return self.condicional()
        
        # Repetição: enquanto ... faca ...
        elif self.match(TokenType.ENQUANTO):
            return self.repeticao()
        
        # Comando composto: inicio ... fim
        elif self.match(TokenType.INICIO):
            return self.comando_composto()
        
        else:
            raise ParseError(f"Comando inválido", self.current)
    
    def atribuicao(self) -> Assignment:
        """
        atribuicao ::= ID ":=" expressao
        """
        id_token = self.expect(TokenType.ID)
        identifier = id_token.value
        
        self.expect(TokenType.ATRIB, "Esperado ':=' para atribuição")
        
        expression = self.expressao()
        
        return Assignment(identifier=identifier, expression=expression)
    
    def leitura(self) -> ReadCommand:
        """
        leitura ::= "leia" "(" ID ")"
        """
        self.expect(TokenType.LEIA)
        self.expect(TokenType.LPAREN, "Esperado '(' após 'leia'")
        id_token = self.expect(TokenType.ID, "Esperado identificador em 'leia'")
        self.expect(TokenType.RPAREN, "Esperado ')' após identificador")
        
        return ReadCommand(identifier=id_token.value)
    
    def escrita(self) -> WriteCommand:
        """
        escrita ::= "escreva" "(" expressao ")"
        """
        self.expect(TokenType.ESCREVA)
        self.expect(TokenType.LPAREN, "Esperado '(' após 'escreva'")
        expression = self.expressao()
        self.expect(TokenType.RPAREN, "Esperado ')' após expressão")
        
        return WriteCommand(expression=expression)
    
    def condicional(self) -> IfCommand:
        """
        condicional ::= "se" expressao "entao" comando ["senao" comando]
        """
        self.expect(TokenType.SE)
        condition = self.expressao()
        self.expect(TokenType.ENTAO, "Esperado 'entao' após condição")
        then_command = self.comando()
        
        else_command = None
        if self.match(TokenType.SENAO):
            self.advance()
            else_command = self.comando()
        
        return IfCommand(
            condition=condition,
            then_command=then_command,
            else_command=else_command
        )
    
    def repeticao(self) -> WhileCommand:
        """
        repeticao ::= "enquanto" expressao "faca" comando
        """
        self.expect(TokenType.ENQUANTO)
        condition = self.expressao()
        self.expect(TokenType.FACA, "Esperado 'faca' após condição")
        body = self.comando()
        
        return WhileCommand(condition=condition, body=body)
    
    # ==================== EXPRESSÕES ====================
    
    def expressao(self) -> Expression:
        """
        expressao ::= expressao_simples [op_relacional expressao_simples]
        op_relacional ::= "=" | "!=" | "<" | "<=" | ">" | ">="
        """
        left = self.expressao_simples()
        
        # Operadores relacionais
        if self.match(TokenType.EQ, TokenType.NEQ, TokenType.LT, 
                     TokenType.LE, TokenType.GT, TokenType.GE):
            op_token = self.current
            self.advance()
            right = self.expressao_simples()
            
            # Mapeia token para string do operador
            op_map = {
                TokenType.EQ: '=',
                TokenType.NEQ: '!=',
                TokenType.LT: '<',
                TokenType.LE: '<=',
                TokenType.GT: '>',
                TokenType.GE: '>='
            }
            
            return BinaryOp(left=left, operator=op_map[op_token.type], right=right)
        
        return left
    
    def expressao_simples(self) -> Expression:
        """
        expressao_simples ::= ["+"|"-"] termo {("+"|"-"|"ou") termo}
        """
        # Sinal unário opcional
        if self.match(TokenType.PLUS, TokenType.MINUS):
            sign = self.current
            self.advance()
            if sign.type == TokenType.MINUS:
                operand = self.termo()
                expr = UnaryOp(operator='-', operand=operand)
            else:
                expr = self.termo()  # + unário é ignorado
        else:
            expr = self.termo()
        
        # Operadores aditivos e 'ou'
        while self.match(TokenType.PLUS, TokenType.MINUS, TokenType.OU):
            op_token = self.current
            self.advance()
            right = self.termo()
            
            op_map = {
                TokenType.PLUS: '+',
                TokenType.MINUS: '-',
                TokenType.OU: 'ou'
            }
            
            expr = BinaryOp(left=expr, operator=op_map[op_token.type], right=right)
        
        return expr
    
    def termo(self) -> Expression:
        """
        termo ::= fator {("*"|"div"|"e") fator}
        """
        expr = self.fator()
        
        # Operadores multiplicativos e 'e'
        while self.match(TokenType.TIMES, TokenType.DIV, TokenType.E):
            op_token = self.current
            self.advance()
            right = self.fator()
            
            op_map = {
                TokenType.TIMES: '*',
                TokenType.DIV: 'div',
                TokenType.E: 'e'
            }
            
            expr = BinaryOp(left=expr, operator=op_map[op_token.type], right=right)
        
        return expr
    
    def fator(self) -> Expression:
        """
        fator ::= ID | NUM | "(" expressao ")" | "nao" fator | "verdadeiro" | "falso"
        """
        # Identificador
        if self.match(TokenType.ID):
            id_token = self.current
            self.advance()
            return Identifier(name=id_token.value)
        
        # Número
        elif self.match(TokenType.NUM):
            num_token = self.current
            self.advance()
            return Number(value=num_token.value)
        
        # Verdadeiro
        elif self.match(TokenType.VERDADEIRO):
            self.advance()
            return Boolean(value=True)
        
        # Falso
        elif self.match(TokenType.FALSO):
            self.advance()
            return Boolean(value=False)
        
        # Negação lógica
        elif self.match(TokenType.NAO):
            self.advance()
            operand = self.fator()
            return UnaryOp(operator='nao', operand=operand)
        
        # Expressão entre parênteses
        elif self.match(TokenType.LPAREN):
            self.advance()
            expr = self.expressao()
            self.expect(TokenType.RPAREN, "Esperado ')' após expressão")
            return expr
        
        else:
            raise ParseError(f"Esperado expressão, encontrado {self.current.type.name}", self.current)

