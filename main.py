"""
Compilador LPD - Linguagem de Programação Didática
Implementa todas as fases de compilação: léxica, sintática, semântica e geração de código.
"""

import sys
import json
import argparse
from lexer import Lexer, LexError
from tokens import TokenType
from parser import Parser, ParseError
from semantic_analyzer import SemanticAnalyzer, SemanticError
from code_generator import CodeGenerator
from ast_nodes import ast_to_string


def print_usage():
    """Imprime instruções de uso."""
    print("""
Uso: python3 main.py <arquivo.lpd> [opções]

Opções:
  --lex              Apenas análise léxica (lista tokens)
  --lex-json         Análise léxica com saída em JSON
  --parse            Análise léxica + sintática (mostra AST)
  --semantic         Análise léxica + sintática + semântica (mostra tabela de símbolos)
  --compile          Compilação completa (padrão)
  -o <arquivo>       Especifica arquivo de saída para código gerado (padrão: saida.asm)
  --help, -h         Mostra esta mensagem

Exemplos:
  python3 main.py programa.lpd                    # Compilação completa
  python3 main.py programa.lpd --lex              # Apenas tokens
  python3 main.py programa.lpd --parse            # Mostra AST
  python3 main.py programa.lpd -o programa.asm    # Especifica saída
""")


def run_lexer(source: str, as_json: bool = False):
    """Executa apenas a análise léxica."""
    tokens = Lexer(source).tokens()
    
    if as_json:
        data = [
            {
                "type": t.type.name,
                "lexeme": t.lexeme,
                "line": t.line,
                "col": t.col,
                "value": t.value,
            }
            for t in tokens
            if t.type is not TokenType.EOF
        ]
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print("=== ANÁLISE LÉXICA ===\n")
        for t in tokens:
            if t.type is not TokenType.EOF:
                value_str = f" -> {t.value}" if t.value is not None else ""
                print(f"{t.line:3d}:{t.col:<3d} {t.type.name:12s} {t.lexeme!r}{value_str}")
        print(f"\nTotal de tokens: {len([t for t in tokens if t.type != TokenType.EOF])}")


def run_parser(source: str):
    """Executa análise léxica e sintática."""
    print("=== ANÁLISE LÉXICA ===")
    tokens = Lexer(source).tokens()
    print(f"[OK] Análise léxica concluída: {len([t for t in tokens if t.type != TokenType.EOF])} tokens\n")
    
    print("=== ANÁLISE SINTÁTICA ===")
    ast = Parser(tokens).parse()
    print("[OK] Análise sintática concluída\n")
    
    print("=== ÁRVORE SINTÁTICA ABSTRATA (AST) ===")
    print(ast_to_string(ast))


def run_semantic(source: str):
    """Executa análise léxica, sintática e semântica."""
    print("=== ANÁLISE LÉXICA ===")
    tokens = Lexer(source).tokens()
    print(f"[OK] Análise léxica concluída: {len([t for t in tokens if t.type != TokenType.EOF])} tokens\n")
    
    print("=== ANÁLISE SINTÁTICA ===")
    ast = Parser(tokens).parse()
    print("[OK] Análise sintática concluída\n")
    
    print("=== ANÁLISE SEMÂNTICA ===")
    analyzer = SemanticAnalyzer()
    symbol_table = analyzer.analyze(ast)
    print("[OK] Análise semântica concluída\n")
    
    print("=== TABELA DE SÍMBOLOS ===")
    print(symbol_table)


def compile_program(source: str, output_file: str = "saida.asm"):
    """Executa compilação completa."""
    print("=== COMPILADOR LPD ===\n")
    
    # Análise Léxica
    print("[1/4] Análise Léxica...", end=" ")
    tokens = Lexer(source).tokens()
    print(f"OK ({len([t for t in tokens if t.type != TokenType.EOF])} tokens)")
    
    # Análise Sintática
    print("[2/4] Análise Sintática...", end=" ")
    ast = Parser(tokens).parse()
    print("OK")
    
    # Análise Semântica
    print("[3/4] Análise Semântica...", end=" ")
    analyzer = SemanticAnalyzer()
    symbol_table = analyzer.analyze(ast)
    print(f"OK ({symbol_table.get_memory_size()} variáveis)")
    
    # Geração de Código
    print("[4/4] Geração de Código...", end=" ")
    generator = CodeGenerator()
    instructions = generator.generate(ast, symbol_table)
    print(f"OK ({len(instructions)} instruções)")
    
    # Salva código gerado
    generator.save_to_file(output_file)
    print(f"\n[OK] Compilação concluída com sucesso!")
    print(f"      Código gerado em: {output_file}")
    
    # Mostra código gerado
    print(f"\n=== CÓDIGO GERADO ===")
    print(generator.get_code())


def main():
    """Função principal."""
    # Se não tem argumentos, mostra ajuda
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    # Se pede ajuda
    if "--help" in sys.argv or "-h" in sys.argv:
        print_usage()
        sys.exit(0)
    
    # Arquivo de entrada
    input_file = sys.argv[1]
    
    # Lê arquivo fonte
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Erro: Arquivo '{input_file}' não encontrado")
        sys.exit(1)
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        sys.exit(1)
    
    # Determina modo de operação
    mode = "compile"  # padrão
    output_file = "saida.asm"
    
    if "--lex" in sys.argv:
        mode = "lex"
    elif "--lex-json" in sys.argv:
        mode = "lex-json"
    elif "--parse" in sys.argv:
        mode = "parse"
    elif "--semantic" in sys.argv:
        mode = "semantic"
    
    # Verifica se tem arquivo de saída customizado
    if "-o" in sys.argv:
        try:
            idx = sys.argv.index("-o")
            output_file = sys.argv[idx + 1]
        except (IndexError, ValueError):
            print("Erro: Opção -o requer nome de arquivo")
            sys.exit(1)
    
    # Executa compilação
    try:
        if mode == "lex":
            run_lexer(source, as_json=False)
        elif mode == "lex-json":
            run_lexer(source, as_json=True)
        elif mode == "parse":
            run_parser(source)
        elif mode == "semantic":
            run_semantic(source)
        else:  # compile
            compile_program(source, output_file)
    
    except LexError as e:
        print(f"\n[ERRO] ERRO LEXICO: {e}")
        sys.exit(2)
    except ParseError as e:
        print(f"\n[ERRO] ERRO SINTATICO: {e}")
        sys.exit(3)
    except SemanticError as e:
        print(f"\n[ERRO] ERRO SEMANTICO: {e}")
        sys.exit(4)
    except Exception as e:
        print(f"\n[ERRO] ERRO INTERNO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(5)


if __name__ == "__main__":
    main()
