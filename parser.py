# -----------------------------------------------------------------------------
# parser.py
# Analisador sintático (descida recursiva) para a linguagem LPD.
# - Recebe a lista de tokens do lexer e valida a sintaxe conforme a gramática.
# - Constrói uma AST simples (nós como dicionários) opcionalmente.
# - Emite ParseError com linha/coluna/mensagem ao primeiro erro encontrado.
# Cobertura:
#   Programa:  programa ID ; [var-decls] inicio stmt-list fim .
#   Declarações: var id (, id)* : (inteiro|booleano) ;
#   Comandos: atrib, leia, escreva, se/entao/[senao], enquanto/faca, bloco
#   Expressões: OU / E / (== != < <= > >=) / + - / * / / div / unários (+ - nao) / fator
#   Localização: ID ["[" expr "]"]
# -----------------------------------------------------------------------------

from dataclasses import dataclass
from typing import List, Optional, Any
from tokens import Token, TokenType, LexError  # LexError reutilizado p/ padronizar base
                                               # (ParseError abaixo é específico do parser)

# ------------------------- Erro sintático -------------------------------------
class ParseError(Exception):
    def __init__(self, message: str, line: int, col: int):
        super().__init__(f"[{line}:{col}] {message}")
        self.line, self.col = line, col

# ------------------------- Parser ---------------------------------------------
@dataclass
class Parser:
    tokens: List[Token]
    build_ast: bool = False

    def __post_init__(self):
        self.i = 0

    # Utilitários de navegação
    def _current(self) -> Token:
        return self.tokens[self.i] if self.i < len(self.tokens) else self.tokens[-1]

    def _check(self, *types: TokenType) -> bool:
        if self.i >= len(self.tokens):
            return False
        return self._current().type in types

    def _advance(self) -> Token:
        if self.i < len(self.tokens):
            self.i += 1
        return self.tokens[self.i - 1]

    def _match(self, *types: TokenType) -> Optional[Token]:
        if self._check(*types):
            return self._advance()
        return None

    def _expect(self, t: TokenType, msg: str) -> Token:
        if self._check(t):
            return self._advance()
        cur = self._current()
        raise ParseError(f"{msg} (found {cur.type.name} '{cur.lexeme}')", cur.line, cur.col)

    # -------------------- Ponto de entrada ------------------------------------
    def parse(self) -> Optional[Any]:
        """programa ID ; [var-decls] inicio stmt-list fim . EOF"""
        ast = self._parse_program()
        # deve terminar em EOF
        self._expect(TokenType.EOF, "Expected end of file")
        return ast if self.build_ast else None

    # programa
    def _parse_program(self):
        prog_tok = self._expect(TokenType.PROGRAM, "Expected 'programa'")
        name_tok = self._expect(TokenType.ID, "Expected program name (identifier)")
        self._expect(TokenType.SEMI, "Expected ';' after program header")

        decls = self._parse_var_section_opt()
        self._expect(TokenType.INICIO, "Expected 'inicio' to start program block")
        stmts = self._parse_stmt_list()
        self._expect(TokenType.FIM, "Expected 'fim' to close program block")
        self._expect(TokenType.DOT, "Expected '.' after 'fim'")

        if not self.build_ast:
            return None
        return {
            "type": "Program",
            "name": name_tok.lexeme,
            "decls": decls,
            "body": stmts
        }

    # var-seção (opcional)
    def _parse_var_section_opt(self):
        decls = []
        if self._match(TokenType.VAR):
            # var id (, id)* : tipo ;
            while self._check(TokenType.ID):
                decls.append(self._parse_var_decl())
                self._expect(TokenType.SEMI, "Expected ';' after variable declaration")
        return decls

    def _parse_var_decl(self):
        ids = [self._expect(TokenType.ID, "Expected identifier").lexeme]
        while self._match(TokenType.COMMA):
            ids.append(self._expect(TokenType.ID, "Expected identifier after ','").lexeme)
        self._expect(TokenType.COLON, "Expected ':' after identifiers")
        if self._match(TokenType.INTEIRO):
            ty = "inteiro"
        elif self._match(TokenType.BOOLEANO):
            ty = "booleano"
        else:
            cur = self._current()
            raise ParseError("Expected type 'inteiro' or 'booleano'", cur.line, cur.col)
        if not self.build_ast:
            return None
        return {"type": "VarDecl", "ids": ids, "varType": ty}

    # lista de comandos (zero ou mais, separados por ';')
    def _parse_stmt_list(self):
        stmts = []
        # FIM encerra bloco; DOT e EOF não aparecem aqui normalmente
        while not self._check(TokenType.FIM) and not self._check(TokenType.EOF):
            stmts.append(self._parse_statement())
            # ; é obrigatório após comandos simples
            if self._match(TokenType.SEMI):
                # permite múltiplos ;; (vimos isso nos seus testes)
                while self._match(TokenType.SEMI):
                    pass
            else:
                # Permite que FIM feche bloco sem ; final
                if not self._check(TokenType.FIM):
                    cur = self._current()
                    raise ParseError("Expected ';' after statement", cur.line, cur.col)
        return stmts if self.build_ast else None

    # comando
    def _parse_statement(self):
        # bloco
        if self._match(TokenType.INICIO):
            inner = self._parse_stmt_list()
            self._expect(TokenType.FIM, "Expected 'fim' to close block")
            return {"type": "Block", "stmts": inner} if self.build_ast else None

        # se expr entao stmt [senao stmt]
        if self._match(TokenType.SE):
            cond = self._parse_expr()
            self._expect(TokenType.ENTAO, "Expected 'entao' after condition")
            then_s = self._parse_statement()
            else_s = None
            if self._match(TokenType.SENAO):
                else_s = self._parse_statement()
            if self.build_ast:
                return {"type": "If", "cond": cond, "then": then_s, "else": else_s}
            return None

        # enquanto expr faca stmt
        if self._match(TokenType.ENQUANTO):
            cond = self._parse_expr()
            self._expect(TokenType.FACA, "Expected 'faca' after condition")
            body = self._parse_statement()
            if self.build_ast:
                return {"type": "While", "cond": cond, "body": body}
            return None

        # escreva(expr)
        if self._match(TokenType.ESCREVA):
            self._expect(TokenType.LPAREN, "Expected '(' after 'escreva'")
            e = self._parse_expr()
            self._expect(TokenType.RPAREN, "Expected ')' after argument")
            return {"type": "Write", "expr": e} if self.build_ast else None

        # leia(location)
        if self._match(TokenType.LEIA):
            self._expect(TokenType.LPAREN, "Expected '(' after 'leia'")
            loc = self._parse_location()
            self._expect(TokenType.RPAREN, "Expected ')' after argument")
            return {"type": "Read", "loc": loc} if self.build_ast else None

        # atribuição: location := expr
        # (começa com ID)
        if self._check(TokenType.ID):
            loc = self._parse_location()
            self._expect(TokenType.ATRIB, "Expected ':=' in assignment")
            e = self._parse_expr()
            return {"type": "Assign", "loc": loc, "expr": e} if self.build_ast else None

        cur = self._current()
        raise ParseError("Expected a statement", cur.line, cur.col)

    # location: ID ["[" expr "]"]
    def _parse_location(self):
        id_tok = self._expect(TokenType.ID, "Expected identifier")
        idx = None
        if self._match(TokenType.LBRACKET):
            idx = self._parse_expr()
            self._expect(TokenType.RBRACKET, "Expected ']' after index expression")
        return {"type": "Location", "name": id_tok.lexeme, "index": idx} if self.build_ast else None

    # ------------------ Expressões com precedência -----------------------------
    # expr := or_expr
    def _parse_expr(self):
        return self._parse_or()

    # or_expr := and_expr ( OU and_expr )*
    def _parse_or(self):
        left = self._parse_and()
        if not self.build_ast:
            while self._match(TokenType.OU):
                self._parse_and()
            return None
        while self._match(TokenType.OU):
            right = self._parse_and()
            left = {"type": "BinOp", "op": "ou", "left": left, "right": right}
        return left

    # and_expr := equality ( E equality )*
    def _parse_and(self):
        left = self._parse_equality()
        if not self.build_ast:
            while self._match(TokenType.E):
                self._parse_equality()
            return None
        while self._match(TokenType.E):
            right = self._parse_equality()
            left = {"type": "BinOp", "op": "e", "left": left, "right": right}
        return left

    # equality := relational ( (== | !=) relational )*
    def _parse_equality(self):
        left = self._parse_relational()
        if not self.build_ast:
            while self._match(TokenType.EQ, TokenType.NEQ):
                self._parse_relational()
            return None
        while True:
            if self._match(TokenType.EQ):
                right = self._parse_relational()
                left = {"type": "BinOp", "op": "=", "left": left, "right": right}
            elif self._match(TokenType.NEQ):
                right = self._parse_relational()
                left = {"type": "BinOp", "op": "!=", "left": left, "right": right}
            else:
                break
        return left

    # relational := additive ( (< | <= | > | >=) additive )*
    def _parse_relational(self):
        left = self._parse_additive()
        if not self.build_ast:
            while self._match(TokenType.LT, TokenType.LE, TokenType.GT, TokenType.GE):
                self._parse_additive()
            return None
        while True:
            if self._match(TokenType.LT):
                right = self._parse_additive()
                left = {"type": "BinOp", "op": "<", "left": left, "right": right}
            elif self._match(TokenType.LE):
                right = self._parse_additive()
                left = {"type": "BinOp", "op": "<=", "left": left, "right": right}
            elif self._match(TokenType.GT):
                right = self._parse_additive()
                left = {"type": "BinOp", "op": ">", "left": left, "right": right}
            elif self._match(TokenType.GE):
                right = self._parse_additive()
                left = {"type": "BinOp", "op": ">=", "left": left, "right": right}
            else:
                break
        return left

    # additive := term ( (+ | -) term )*
    def _parse_additive(self):
        left = self._parse_term()
        if not self.build_ast:
            while self._match(TokenType.PLUS, TokenType.MINUS):
                self._parse_term()
            return None
        while True:
            if self._match(TokenType.PLUS):
                right = self._parse_term()
                left = {"type": "BinOp", "op": "+", "left": left, "right": right}
            elif self._match(TokenType.MINUS):
                right = self._parse_term()
                left = {"type": "BinOp", "op": "-", "left": left, "right": right}
            else:
                break
        return left

    # term := factor ( (* | / | div) factor )*
    def _parse_term(self):
        left = self._parse_unary()
        if not self.build_ast:
            while self._match(TokenType.TIMES, TokenType.SLASH, TokenType.DIV):
                self._parse_unary()
            return None
        while True:
            if self._match(TokenType.TIMES):
                right = self._parse_unary()
                left = {"type": "BinOp", "op": "*", "left": left, "right": right}
            elif self._match(TokenType.SLASH):
                right = self._parse_unary()
                left = {"type": "BinOp", "op": "/", "left": left, "right": right}
            elif self._match(TokenType.DIV):
                right = self._parse_unary()
                left = {"type": "BinOp", "op": "div", "left": left, "right": right}
            else:
                break
        return left

    # unary := ( + | - | nao ) unary | primary
    def _parse_unary(self):
        if self._match(TokenType.PLUS):
            expr = self._parse_unary()
            return {"type": "Unary", "op": "+", "expr": expr} if self.build_ast else None
        if self._match(TokenType.MINUS):
            expr = self._parse_unary()
            return {"type": "Unary", "op": "-", "expr": expr} if self.build_ast else None
        if self._match(TokenType.NAO):
            expr = self._parse_unary()
            return {"type": "Unary", "op": "nao", "expr": expr} if self.build_ast else None
        return self._parse_primary()

    # primary := NUM | VERDADEIRO | FALSO | location | '(' expr ')'
    def _parse_primary(self):
        if self._match(TokenType.NUM):
            tok = self.tokens[self.i - 1]
            return {"type": "Num", "value": int(tok.lexeme)} if self.build_ast else None
        if self._match(TokenType.VERDADEIRO):
            return {"type": "Bool", "value": True} if self.build_ast else None
        if self._match(TokenType.FALSO):
            return {"type": "Bool", "value": False} if self.build_ast else None
        if self._check(TokenType.ID):
            return self._parse_location()
        if self._match(TokenType.LPAREN):
            e = self._parse_expr()
            self._expect(TokenType.RPAREN, "Expected ')'")
            return e
        cur = self._current()
        raise ParseError("Expected expression", cur.line, cur.col)
