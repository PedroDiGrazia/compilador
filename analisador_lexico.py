"""
Analisador Léxico do Compilador LPD
Responsável por ler o código fonte e gerar a sequência de tokens.
"""

from typing import List
from tokens import Token, TipoToken, PALAVRAS_RESERVADAS, ErroLexico

CARACTERES_LETRA = "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
CARACTERES_DIGITO = "0123456789"
TAMANHO_MAX_IDENTIFICADOR = 30  # LPD: até 30 caracteres


class AnalisadorLexico:
    """
    Analisador Léxico (Scanner) da linguagem LPD.
    Converte o código fonte em uma sequência de tokens.
    """
    
    def __init__(self, codigo_fonte: str):
        self.fonte = codigo_fonte
        self.posicao = 0
        self.linha = 1
        self.coluna = 1
        self.tamanho = len(codigo_fonte)

    def _espiar(self, deslocamento: int = 0) -> str:
        """Retorna o caractere na posição atual + deslocamento, sem avançar."""
        indice = self.posicao + deslocamento
        return self.fonte[indice] if indice < self.tamanho else ""

    def _avancar(self) -> str:
        """Avança para o próximo caractere e retorna o atual."""
        caractere = self._espiar()
        if caractere == "\n":
            self.linha += 1
            self.coluna = 1
        else:
            self.coluna += 1
        self.posicao += 1
        return caractere

    def _corresponde(self, esperado: str) -> bool:
        """Verifica se o caractere atual corresponde ao esperado e avança."""
        if self._espiar() == esperado:
            self._avancar()
            return True
        return False

    def _pular_espacos_e_comentarios(self):
        """Pula espaços em branco e comentários."""
        while True:
            caractere = self._espiar()
            # Espaços em branco
            while caractere and caractere.isspace():
                self._avancar()
                caractere = self._espiar()
            # Comentários { ... }
            if caractere == "{":
                linha_inicio, coluna_inicio = self.linha, self.coluna
                self._avancar()
                while True:
                    if self._espiar() == "":
                        raise ErroLexico("Comentário não encerrado '}'", linha_inicio, coluna_inicio)
                    if self._espiar() == "}":
                        self._avancar()
                        break
                    self._avancar()
                continue
            break

    def _ler_identificador_ou_palavra_reservada(self) -> Token:
        """Lê um identificador ou palavra reservada."""
        linha_inicio, coluna_inicio = self.linha, self.coluna
        lexema = ""
        # Primeira letra (não pode começar com _)
        if self._espiar() not in CARACTERES_LETRA.replace("_", ""):
            raise ErroLexico("Identificador deve iniciar com letra", linha_inicio, coluna_inicio)
        while True:
            caractere = self._espiar()
            if caractere and (caractere in CARACTERES_LETRA or caractere in CARACTERES_DIGITO):
                lexema += self._avancar()
                if len(lexema) > TAMANHO_MAX_IDENTIFICADOR:
                    raise ErroLexico(
                        f"Identificador excede {TAMANHO_MAX_IDENTIFICADOR} caracteres",
                        linha_inicio, coluna_inicio
                    )
            else:
                break
        minusculo = lexema.lower()
        if minusculo in PALAVRAS_RESERVADAS:
            return Token(PALAVRAS_RESERVADAS[minusculo], lexema, linha_inicio, coluna_inicio)
        return Token(TipoToken.IDENTIFICADOR, lexema, linha_inicio, coluna_inicio, valor=lexema)

    def _ler_numero(self) -> Token:
        """Lê um número inteiro."""
        linha_inicio, coluna_inicio = self.linha, self.coluna
        lexema = ""
        if self._espiar() not in CARACTERES_DIGITO:
            raise ErroLexico("Número inválido", linha_inicio, coluna_inicio)
        while self._espiar() in CARACTERES_DIGITO:
            lexema += self._avancar()
        # LPD aceita apenas inteiros
        return Token(TipoToken.NUMERO, lexema, linha_inicio, coluna_inicio, valor=int(lexema))

    def obter_tokens(self) -> List[Token]:
        """
        Analisa o código fonte e retorna a lista de tokens.
        
        Returns:
            List[Token]: Lista de todos os tokens encontrados no código fonte
        """
        tokens: List[Token] = []
        while True:
            self._pular_espacos_e_comentarios()
            caractere = self._espiar()
            if not caractere:
                tokens.append(Token(TipoToken.FIM_ARQUIVO, "", self.linha, self.coluna))
                return tokens

            # Operadores de dois caracteres (verificar primeiro)
            if caractere == ":" and self._espiar(1) == "=":
                linha, coluna = self.linha, self.coluna
                self._avancar()
                self._avancar()
                tokens.append(Token(TipoToken.ATRIBUICAO, ":=", linha, coluna))
                continue
            if caractere == "<" and self._espiar(1) == "=":
                linha, coluna = self.linha, self.coluna
                self._avancar()
                self._avancar()
                tokens.append(Token(TipoToken.MENOR_IGUAL, "<=", linha, coluna))
                continue
            if caractere == ">" and self._espiar(1) == "=":
                linha, coluna = self.linha, self.coluna
                self._avancar()
                self._avancar()
                tokens.append(Token(TipoToken.MAIOR_IGUAL, ">=", linha, coluna))
                continue
            if caractere == "!" and self._espiar(1) == "=":
                linha, coluna = self.linha, self.coluna
                self._avancar()
                self._avancar()
                tokens.append(Token(TipoToken.DIFERENTE, "!=", linha, coluna))
                continue

            # Operadores e símbolos de um caractere
            if caractere == "=":
                tokens.append(Token(TipoToken.IGUAL, self._avancar(), self.linha, self.coluna - 1))
                continue
            if caractere == "<":
                tokens.append(Token(TipoToken.MENOR, self._avancar(), self.linha, self.coluna - 1))
                continue
            if caractere == ">":
                tokens.append(Token(TipoToken.MAIOR, self._avancar(), self.linha, self.coluna - 1))
                continue
            if caractere == "+":
                tokens.append(Token(TipoToken.MAIS, self._avancar(), self.linha, self.coluna - 1))
                continue
            if caractere == "-":
                tokens.append(Token(TipoToken.MENOS, self._avancar(), self.linha, self.coluna - 1))
                continue
            if caractere == "*":
                tokens.append(Token(TipoToken.MULTIPLICACAO, self._avancar(), self.linha, self.coluna - 1))
                continue
            if caractere == "(":
                tokens.append(Token(TipoToken.ABRE_PARENTESES, self._avancar(), self.linha, self.coluna - 1))
                continue
            if caractere == ")":
                tokens.append(Token(TipoToken.FECHA_PARENTESES, self._avancar(), self.linha, self.coluna - 1))
                continue
            if caractere == ":":
                tokens.append(Token(TipoToken.DOIS_PONTOS, self._avancar(), self.linha, self.coluna - 1))
                continue
            if caractere == ";":
                tokens.append(Token(TipoToken.PONTO_VIRGULA, self._avancar(), self.linha, self.coluna - 1))
                continue
            if caractere == ",":
                tokens.append(Token(TipoToken.VIRGULA, self._avancar(), self.linha, self.coluna - 1))
                continue
            if caractere == ".":
                tokens.append(Token(TipoToken.PONTO, self._avancar(), self.linha, self.coluna - 1))
                continue

            # Identificador ou palavra reservada
            if caractere in CARACTERES_LETRA.replace("_", ""):
                tokens.append(self._ler_identificador_ou_palavra_reservada())
                continue
            # Número
            if caractere in CARACTERES_DIGITO:
                tokens.append(self._ler_numero())
                continue

            raise ErroLexico(f"Caractere inválido: '{caractere}'", self.linha, self.coluna)
