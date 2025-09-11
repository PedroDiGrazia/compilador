# -----------------------------------------------------------------------------
# Definições de tokens e estruturas auxiliares da linguagem LPD.
# - TokenType: enum com todos os tipos de tokens reconhecidos.
# - KEYWORDS: mapa de palavras-reservadas (string -> TokenType).
# - Token: dataclass para carregar tipo, lexema, localização e valor.
# - LexError: exceção para erros léxicos (linha/coluna).
# -----------------------------------------------------------------------------

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

class TokenType(Enum):
    # Estruturais / pontuação
    PROGRAM = auto(); VAR = auto(); INICIO = auto(); FIM = auto()
    PROCEDIMENTO = auto(); FUNCAO = auto()
    ENQUANTO = auto(); FACA = auto(); SE = auto(); ENTAO = auto(); SENAO = auto()
    LEIA = auto(); ESCREVA = auto()
    INTEIRO = auto(); BOOLEANO = auto(); VERDADEIRO = auto(); FALSO = auto()
    E = auto(); OU = auto(); NAO = auto()
    ID = auto(); NUM = auto()
    # Operadores e símbolos
    ATRIB = auto()       # :=
    PLUS = auto(); MINUS = auto(); TIMES = auto()  # + - *
    SLASH = auto()        # /
    DIV = auto()         # div
    NEQ = auto(); EQ = auto(); LT = auto(); LE = auto(); GT = auto(); GE = auto()
    LPAREN = auto(); RPAREN = auto()
    LBRACKET = auto(); RBRACKET = auto() 
    COLON = auto(); SEMI = auto(); COMMA = auto(); DOT = auto()
    EOF = auto()

KEYWORDS = {
    "programa": TokenType.PROGRAM,
    "var": TokenType.VAR,
    "inicio": TokenType.INICIO,
    "fim": TokenType.FIM,
    "procedimento": TokenType.PROCEDIMENTO,
    "funcao": TokenType.FUNCAO,
    "enquanto": TokenType.ENQUANTO,
    "faca": TokenType.FACA,
    "se": TokenType.SE,
    "entao": TokenType.ENTAO,
    "senao": TokenType.SENAO,
    "leia": TokenType.LEIA,
    "escreva": TokenType.ESCREVA,
    "inteiro": TokenType.INTEIRO,
    "booleano": TokenType.BOOLEANO,
    "verdadeiro": TokenType.VERDADEIRO,
    "falso": TokenType.FALSO,
    "e": TokenType.E,
    "ou": TokenType.OU,
    "nao": TokenType.NAO,
    "div": TokenType.DIV,
}

@dataclass
class Token:
    type: TokenType
    lexeme: str
    line: int
    col: int
    value: Optional[object] = None  # p/ NUM, ID etc.

class LexError(Exception):
    def __init__(self, message, line, col):
        super().__init__(f"[{line}:{col}] {message}")
        self.line, self.col = line, col
