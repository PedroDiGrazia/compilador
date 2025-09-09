from typing import List
from tokens import Token, TokenType, KEYWORDS, LexError

LETTER_CHARS = "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGIT_CHARS = "0123456789"
MAX_ID_LEN = 30  # LPD: up to 30 characters

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
        """Skip spaces/tabs/newlines and block comments delimited by { }."""
        while True:
            ch = self._peek()
            # skip whitespace
            while ch and ch.isspace():
                self._advance()
                ch = self._peek()
            # skip comments { ... }
            if ch == "{":
                start_line, start_col = self.line, self.col
                self._advance()  # consume '{'
                while True:
                    if self._peek() == "":
                        raise LexError("Unterminated comment '}'", start_line, start_col)
                    if self._peek() == "}":
                        self._advance()  # consume '}'
                        break
                    self._advance()
                continue
            break

    def _identifier_or_keyword(self):
        start_line, start_col = self.line, self.col
        lex = ""
        # first char must be a letter (underscore not allowed to start)
        if self._peek() not in LETTER_CHARS.replace("_", ""):
            raise LexError("Identifier must start with a letter", start_line, start_col)
        while True:
            ch = self._peek()
            if ch and (ch in LETTER_CHARS or ch in DIGIT_CHARS):
                lex += self._advance()
                if len(lex) > MAX_ID_LEN:
                    raise LexError(f"Identifier exceeds {MAX_ID_LEN} characters", start_line, start_col)
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
            raise LexError("Invalid number", start_line, start_col)
        while self._peek() in DIGIT_CHARS:
            lex += self._advance()
        # LPD accepts only integer literals
        return Token(TokenType.NUM, lex, start_line, start_col, value=int(lex))

    def tokens(self) -> List[Token]:
        out: List[Token] = []
        while True:
            self._skip_whitespace_and_comments()
            ch = self._peek()
            if not ch:
                out.append(Token(TokenType.EOF, "", self.line, self.col))
                return out

            # Two-character tokens first
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

            # Single-character tokens
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

            # ID / keyword / number
            if ch in LETTER_CHARS.replace("_", ""):
                out.append(self._identifier_or_keyword()); continue
            if ch in DIGIT_CHARS:
                out.append(self._number()); continue

            # Unrecognized character
            raise LexError(
                f"Unrecognized symbol: '{ch}'. This symbol is not part of the LPD token set.",
                self.line,
                self.col,
            )
