"""
Módulo de Tokens e Erros do Compilador LPD
Define os tipos de tokens, palavras reservadas e classes de exceção.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


class TipoToken(Enum):
    """Enumeração dos tipos de tokens da linguagem LPD."""
    # Estruturais / pontuação
    PROGRAMA = auto()
    VAR = auto()
    INICIO = auto()
    FIM = auto()
    PROCEDIMENTO = auto()
    FUNCAO = auto()
    ENQUANTO = auto()
    FACA = auto()
    SE = auto()
    ENTAO = auto()
    SENAO = auto()
    LEIA = auto()
    ESCREVA = auto()
    INTEIRO = auto()
    BOOLEANO = auto()
    VERDADEIRO = auto()
    FALSO = auto()
    E = auto()
    OU = auto()
    NAO = auto()
    IDENTIFICADOR = auto()
    NUMERO = auto()
    # Operadores e símbolos
    ATRIBUICAO = auto()       # :=
    MAIS = auto()             # +
    MENOS = auto()            # -
    MULTIPLICACAO = auto()    # *
    DIVISAO = auto()          # div
    DIFERENTE = auto()        # !=
    IGUAL = auto()            # =
    MENOR = auto()            # <
    MENOR_IGUAL = auto()      # <=
    MAIOR = auto()            # >
    MAIOR_IGUAL = auto()      # >=
    ABRE_PARENTESES = auto()  # (
    FECHA_PARENTESES = auto() # )
    DOIS_PONTOS = auto()      # :
    PONTO_VIRGULA = auto()    # ;
    VIRGULA = auto()          # ,
    PONTO = auto()            # .
    FIM_ARQUIVO = auto()      # EOF


PALAVRAS_RESERVADAS = {
    "programa": TipoToken.PROGRAMA,
    "var": TipoToken.VAR,
    "inicio": TipoToken.INICIO,
    "fim": TipoToken.FIM,
    "procedimento": TipoToken.PROCEDIMENTO,
    "funcao": TipoToken.FUNCAO,
    "enquanto": TipoToken.ENQUANTO,
    "faca": TipoToken.FACA,
    "se": TipoToken.SE,
    "entao": TipoToken.ENTAO,
    "senao": TipoToken.SENAO,
    "leia": TipoToken.LEIA,
    "escreva": TipoToken.ESCREVA,
    "inteiro": TipoToken.INTEIRO,
    "booleano": TipoToken.BOOLEANO,
    "verdadeiro": TipoToken.VERDADEIRO,
    "falso": TipoToken.FALSO,
    "e": TipoToken.E,
    "ou": TipoToken.OU,
    "nao": TipoToken.NAO,
    "div": TipoToken.DIVISAO,
}


@dataclass
class Token:
    """Representa um token (átomo) reconhecido pelo analisador léxico."""
    tipo: TipoToken
    lexema: str
    linha: int
    coluna: int
    valor: Optional[object] = None  # para NUMERO, IDENTIFICADOR, etc.


class ErroLexico(Exception):
    """Exceção para erros durante a análise léxica."""
    def __init__(self, mensagem: str, linha: int, coluna: int):
        super().__init__(f"[{linha}:{coluna}] {mensagem}")
        self.linha = linha
        self.coluna = coluna


class ErroSintatico(Exception):
    """Exceção para erros durante a análise sintática."""
    def __init__(self, mensagem: str, linha: int = 0, coluna: int = 0):
        super().__init__(f"[{linha}:{coluna}] {mensagem}" if linha else mensagem)
        self.linha = linha
        self.coluna = coluna


class ErroSemantico(Exception):
    """Exceção para erros durante a análise semântica."""
    def __init__(self, mensagem: str, linha: int = 0, coluna: int = 0):
        super().__init__(f"[{linha}:{coluna}] {mensagem}" if linha else mensagem)
        self.linha = linha
        self.coluna = coluna
