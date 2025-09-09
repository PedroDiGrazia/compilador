import sys, json
from lexer import Lexer, LexError
from tokens import TokenType

def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py <arquivo.lpd> [--json]")
        sys.exit(1)
    path = sys.argv[1]
    to_json = "--json" in sys.argv
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()
    try:
        toks = Lexer(src).tokens()
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
            for t in toks:
                print(f"{t.line}:{t.col}\t{t.type.name}\t{t.lexeme!r}{' -> '+str(t.value) if t.value is not None else ''}")
    except LexError as e:
        print(f"ERRO LÉXICO {e}")
        sys.exit(2)

if __name__ == "__main__":
    main()
