# -----------------------------------------------------------------------------
# main.py
# CLI do analisador léxico/sintático.
# - Sem flags: imprime tokens.
# - --json: imprime tokens (exceto EOF) em JSON.
# - --parse: valida sintaxe (imprime 'OK sintático' se tudo certo).
# - --ast-json: igual --parse, mas também imprime a AST em JSON (didático).
# -----------------------------------------------------------------------------

import sys, json, os
from lexer import Lexer, LexError
from tokens import TokenType
from parser import Parser, ParseError

def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py <arquivo.lpd|arquivo.txt> [--json] [--parse] [--ast-json]")
        sys.exit(1)

    path = sys.argv[1]
    to_json = "--json" in sys.argv
    do_parse = "--parse" in sys.argv or "--ast-json" in sys.argv
    want_ast = "--ast-json" in sys.argv

    # Aceita .lpd e .txt (avisa se for outra extensão, mas prossegue)
    ext = os.path.splitext(path)[1].lower()
    if ext not in (".lpd", ".txt") and not to_json:
        print(f"Aviso: extensão '{ext or '(sem extensão)'}' não é .lpd nem .txt; prosseguindo.", file=sys.stderr)

    with open(path, "r", encoding="utf-8") as f:
        src = f.read()

    try:
        # LÉXICO
        toks = Lexer(src).tokens()

        if do_parse:
            # SINTÁTICO
            parser = Parser(toks, build_ast=want_ast)
            ast = parser.parse()
            if want_ast:
                print(json.dumps(ast, ensure_ascii=False, indent=2))
            print("OK sintático")
            return

        if to_json:
            data = [
                {
                    "type": t.type.name,
                    "lexeme": t.lexeme,
                    "line": t.line,
                    "col": t.col,
                    "value": t.value,
                }
                for t in toks
                if t.type is not TokenType.EOF
            ]
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            # impressão alinhada com largura mínima do tipo
            max_type = max((len(t.type.name) for t in toks), default=0)
            for t in toks:
                s_val = f" -> {t.value}" if t.value is not None else ""
                print(f"{t.line}:{t.col} {t.type.name:<{max_type}} {t.lexeme!r}{s_val}")

    except LexError as e:
        print(f"ERRO LÉXICO {e}")
        sys.exit(2)
    except ParseError as e:
        print(f"ERRO SINTÁTICO {e}")
        sys.exit(3)

if __name__ == "__main__":
    main()
