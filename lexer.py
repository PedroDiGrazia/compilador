# -----------------------------------------------------------------------------
# Analisador léxico da linguagem LPD.
# Responsabilidades:
# - Consumir o código-fonte (string) e produzir uma lista de tokens (Token).
# - Ignorar espaços em branco e comentários em bloco { ... }.
# - Reconhecer palavras-reservadas, identificadores, números e símbolos.
# - Reportar erros com linha/coluna via LexError (ex.: comentário não encerrado).
#
# Pontos-chave:
#   _skip_whitespace_and_comments: pula espaços/linhas e comentários.
#   _identifier_or_keyword: lê IDs e mapeia para KEYWORDS quando aplicável.
#   _number: lê literais inteiros.
#   tokens: motor principal de varredura e emissão de tokens.
# -----------------------------------------------------------------------------

from typing import List
from tokens import Token, TokenType, KEYWORDS, LexError

LETTER_CHARS = "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGIT_CHARS = "0123456789"
MAX_ID_LEN = 30  # LPD: até 30 caracteres

class Lexer:
    def __init__(self, source: str):
        self.src = source
        self.i = 0
        self.line = 1
        self.col = 1
        self.n = len(source)

    def _peek(self, k=0):
        j = self.i + k
        return self.src[j] if j < self.n else ""

    def _advance(self):
        ch = self._peek()
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        self.i += 1
        return ch

    def _match(self, expected: str):
        if self._peek() == expected:
            self._advance()
            return True
        return False

    def _skip_whitespace_and_comments(self):
        while True:
            ch = self._peek()
            
            while ch and ch.isspace():
                self._advance()
                ch = self._peek()
            
            if ch == "{":
                start_line, start_col = self.line, self.col
                self._advance()
                while True:
                    if self._peek() == "":
                        raise LexError("Comentário não encerrado '}'", start_line, start_col)
                    if self._peek() == "}":
                        self._advance()
                        break
                    self._advance()
                continue
            break

    def _identifier_or_keyword(self):
        start_line, start_col = self.line, self.col
        lex = ""

        if self._peek() not in LETTER_CHARS.replace("_", ""):
            raise LexError("Identificador deve iniciar com letra", start_line, start_col)
        while True:
            ch = self._peek()
            if ch and (ch in LETTER_CHARS or ch in DIGIT_CHARS):
                lex += self._advance()
                if len(lex) > MAX_ID_LEN:
                    raise LexError(f"Identificador excede {MAX_ID_LEN} caracteres", start_line, start_col)
            else:
                break
        low = lex.lower()
        if low in KEYWORDS:
            return Token(KEYWORDS[low], lex, start_line, start_col)
        return Token(TokenType.ID, lex, start_line, start_col, value=lex)

    def _number(self):
        start_line, start_col = self.line, self.col
        lex = ""
        if self._peek() not in DIGIT_CHARS:
            raise LexError("Número inválido", start_line, start_col)
        while self._peek() in DIGIT_CHARS:
            lex += self._advance()
        # LPD aceita apenas inteiros
        return Token(TokenType.NUM, lex, start_line, start_col, value=int(lex))

    def tokens(self) -> List[Token]:
        out: List[Token] = []
        while True:
            # <<< chamada atualizada >>>
            self._skip_whitespace_and_comments()
            ch = self._peek()
            if not ch:
                out.append(Token(TokenType.EOF, "", self.line, self.col))
                return out

            # Dois caracteres primeiro
            if ch == ":" and self._peek(1) == "=":
                line, col = self.line, self.col
                self._advance(); self._advance()
                out.append(Token(TokenType.ATRIB, ":=", line, col))
                continue
            if ch == "<" and self._peek(1) == "=":
                line, col = self.line, self.col
                self._advance(); self._advance()
                out.append(Token(TokenType.LE, "<=", line, col))
                continue
            if ch == ">" and self._peek(1) == "=":
                line, col = self.line, self.col
                self._advance(); self._advance()
                out.append(Token(TokenType.GE, ">=", line, col))
                continue
            if ch == "!" and self._peek(1) == "=":
                line, col = self.line, self.col
                self._advance(); self._advance()
                out.append(Token(TokenType.NEQ, "!=", line, col))
                continue

            if ch == "=":
                out.append(Token(TokenType.EQ, self._advance(), self.line, self.col-1)); continue
            if ch == "<":
                out.append(Token(TokenType.LT, self._advance(), self.line, self.col-1)); continue
            if ch == ">":
                out.append(Token(TokenType.GT, self._advance(), self.line, self.col-1)); continue
            if ch == "+":
                out.append(Token(TokenType.PLUS, self._advance(), self.line, self.col-1)); continue
            if ch == "-":
                out.append(Token(TokenType.MINUS, self._advance(), self.line, self.col-1)); continue
            if ch == "*":
                out.append(Token(TokenType.TIMES, self._advance(), self.line, self.col-1)); continue
            if ch == "/": 
                out.append(Token(TokenType.SLASH, self._advance(), self.line, self.col-1)); continue
            if ch == "(":
                out.append(Token(TokenType.LPAREN, self._advance(), self.line, self.col-1)); continue
            if ch == ")":
                out.append(Token(TokenType.RPAREN, self._advance(), self.line, self.col-1)); continue
            if ch == ":":
                out.append(Token(TokenType.COLON, self._advance(), self.line, self.col-1)); continue
            if ch == ";":
                out.append(Token(TokenType.SEMI, self._advance(), self.line, self.col-1)); continue
            if ch == ",":
                out.append(Token(TokenType.COMMA, self._advance(), self.line, self.col-1)); continue
            if ch == ".":
                out.append(Token(TokenType.DOT, self._advance(), self.line, self.col-1)); continue
            if ch == "[":  
                out.append(Token(TokenType.LBRACKET, self._advance(), self.line, self.col-1)); continue
            if ch == "]":   
                out.append(Token(TokenType.RBRACKET, self._advance(), self.line, self.col-1)); continue
            # ID / palavra-chave / número
            if ch in LETTER_CHARS.replace("_", ""):
                out.append(self._identifier_or_keyword()); continue
            if ch in DIGIT_CHARS:
                out.append(self._number()); continue

            raise LexError(f"Caractere inválido: '{ch}'", self.line, self.col)