# -----------------------------------------------------------------------------
# Interface de linha de comando (CLI) do analisador léxico.
# - Lê um arquivo .lpd ou .txt do caminho passado como argumento.
# - Invoca o Lexer para gerar tokens.
# - Imprime os tokens em texto (ou JSON com --json).
# - Em caso de erro léxico, mostra mensagem com linha/coluna e sai (código 2).
# -----------------------------------------------------------------------------

import sys, json, os
from lexer import Lexer, LexError
from tokens import TokenType

def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py <arquivo.lpd|arquivo.txt> [--json]")
        sys.exit(1)

    path = sys.argv[1]
    to_json = "--json" in sys.argv

    # Aceita .lpd e .txt (avisa se for outra extensão, mas prossegue)
    ext = os.path.splitext(path)[1].lower()
    if ext not in (".lpd", ".txt") and not to_json:
        print(f"Aviso: extensão '{ext or '(sem extensão)'}' não é .lpd nem .txt; prosseguindo mesmo assim.", file=sys.stderr)

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
            # impressão compacta com pequeno alinhamento do tipo
            max_type = max((len(t.type.name) for t in toks), default=0)
            for t in toks:
                s_val = f" -> {t.value}" if t.value is not None else ""
                print(f"{t.line}:{t.col} {t.type.name:<{max_type}} {t.lexeme!r}{s_val}")
    except LexError as e:
        print(f"ERRO LÉXICO {e}")
        sys.exit(2)

if __name__ == "__main__":
    main()