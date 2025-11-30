#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compilador LPD - Linguagem de Programação Didática
Implementa todas as fases de compilação: léxica, sintática, semântica e geração de código.
"""

import sys
import os
from analisador_lexico import AnalisadorLexico
from tokens import TipoToken, ErroLexico, ErroSintatico, ErroSemantico
from analisador_sintatico import AnalisadorSintatico
from analisador_semantico import AnalisadorSemantico
from gerador_codigo import GeradorCodigo
from arvore_sintatica import arvore_para_string


def imprimir_uso():
    """Imprime instruções de uso."""
    print("""
Uso: python3 compilador.py <arquivo.txt> [opções]

Opções:
  --lexico           Apenas análise léxica (lista tokens)
  --sintatico        Análise léxica + sintática (mostra AST)
  --semantico        Análise léxica + sintática + semântica (mostra tabela de símbolos)
  --ajuda            Mostra esta mensagem

Exemplos:
  python3 compilador.py programa.txt              # Compilação completa
  python3 compilador.py programa.txt --lexico     # Apenas tokens
  python3 compilador.py programa.txt --sintatico  # Mostra AST

O arquivo compilado é gerado na mesma pasta do compilador.
""")


def executar_lexico(codigo_fonte: str):
    """Executa apenas a análise léxica."""
    tokens = AnalisadorLexico(codigo_fonte).obter_tokens()
    
    print("=== ANÁLISE LÉXICA ===\n")
    for t in tokens:
        if t.tipo is not TipoToken.FIM_ARQUIVO:
            valor_str = f" -> {t.valor}" if t.valor is not None else ""
            print(f"{t.linha:3d}:{t.coluna:<3d} {t.tipo.name:12s} {t.lexema!r}{valor_str}")
    print(f"\nTotal de tokens: {len([t for t in tokens if t.tipo != TipoToken.FIM_ARQUIVO])}")


def executar_sintatico(codigo_fonte: str):
    """Executa análise léxica e sintática."""
    print("=== ANÁLISE LÉXICA ===")
    tokens = AnalisadorLexico(codigo_fonte).obter_tokens()
    print(f"[OK] Análise léxica concluída: {len([t for t in tokens if t.tipo != TipoToken.FIM_ARQUIVO])} tokens\n")
    
    print("=== ANÁLISE SINTÁTICA ===")
    ast = AnalisadorSintatico(tokens).analisar()
    print("[OK] Análise sintática concluída\n")
    
    print("=== ÁRVORE SINTÁTICA ABSTRATA (AST) ===")
    print(arvore_para_string(ast))


def executar_semantico(codigo_fonte: str):
    """Executa análise léxica, sintática e semântica."""
    print("=== ANÁLISE LÉXICA ===")
    tokens = AnalisadorLexico(codigo_fonte).obter_tokens()
    print(f"[OK] Análise léxica concluída: {len([t for t in tokens if t.tipo != TipoToken.FIM_ARQUIVO])} tokens\n")
    
    print("=== ANÁLISE SINTÁTICA ===")
    ast = AnalisadorSintatico(tokens).analisar()
    print("[OK] Análise sintática concluída\n")
    
    print("=== ANÁLISE SEMÂNTICA ===")
    analisador = AnalisadorSemantico()
    tabela_simbolos = analisador.analisar(ast)
    print("[OK] Análise semântica concluída\n")
    
    print("=== TABELA DE SÍMBOLOS ===")
    print(tabela_simbolos)


def compilar_programa(codigo_fonte: str, arquivo_saida: str = "saida.obj"):
    """Executa compilação completa."""
    print("=== COMPILADOR LPD ===\n")
    
    # Análise Léxica
    print("[1/4] Análise Léxica...", end=" ")
    tokens = AnalisadorLexico(codigo_fonte).obter_tokens()
    print(f"OK ({len([t for t in tokens if t.tipo != TipoToken.FIM_ARQUIVO])} tokens)")
    
    # Análise Sintática
    print("[2/4] Análise Sintática...", end=" ")
    ast = AnalisadorSintatico(tokens).analisar()
    print("OK")
    
    # Análise Semântica
    print("[3/4] Análise Semântica...", end=" ")
    analisador = AnalisadorSemantico()
    tabela_simbolos = analisador.analisar(ast)
    print(f"OK ({tabela_simbolos.obter_tamanho_memoria()} variáveis)")
    
    # Geração de Código
    print("[4/4] Geração de Código...", end=" ")
    gerador = GeradorCodigo()
    instrucoes = gerador.gerar(ast, tabela_simbolos)
    print(f"OK ({len(instrucoes)} instruções)")
    
    # Salva código gerado
    gerador.salvar_em_arquivo(arquivo_saida)
    print(f"\n[OK] Compilação concluída com sucesso!")
    print(f"      Código gerado em: {arquivo_saida}")
    
    # Mostra código gerado
    print(f"\n=== CÓDIGO GERADO ===")
    print(gerador.obter_codigo())


def main():
    """Função principal."""
    # Se não tem argumentos, mostra ajuda
    if len(sys.argv) < 2:
        imprimir_uso()
        sys.exit(1)
    
    # Se pede ajuda
    if "--ajuda" in sys.argv or "-a" in sys.argv:
        imprimir_uso()
        sys.exit(0)
    
    # Arquivo de entrada
    arquivo_entrada = sys.argv[1]
    
    # Lê arquivo fonte
    try:
        with open(arquivo_entrada, "r", encoding="utf-8") as f:
            codigo_fonte = f.read()
    except FileNotFoundError:
        print(f"Erro: Arquivo '{arquivo_entrada}' não encontrado")
        sys.exit(1)
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        sys.exit(1)
    
    # Determina modo de operação
    modo = "compilar"  # padrão
    
    if "--lexico" in sys.argv:
        modo = "lexico"
    elif "--sintatico" in sys.argv:
        modo = "sintatico"
    elif "--semantico" in sys.argv:
        modo = "semantico"
    
    # Define arquivo de saída na mesma pasta do compilador
    nome_base = os.path.basename(arquivo_entrada).replace('.txt', '.obj')
    arquivo_saida = nome_base
    
    # Executa compilação
    try:
        if modo == "lexico":
            executar_lexico(codigo_fonte)
        elif modo == "sintatico":
            executar_sintatico(codigo_fonte)
        elif modo == "semantico":
            executar_semantico(codigo_fonte)
        else:  # compilar
            compilar_programa(codigo_fonte, arquivo_saida)
    
    except ErroLexico as e:
        print(f"\n[ERRO] ERRO LÉXICO: {e}")
        sys.exit(2)
    except ErroSintatico as e:
        print(f"\n[ERRO] ERRO SINTÁTICO: {e}")
        sys.exit(3)
    except ErroSemantico as e:
        print(f"\n[ERRO] ERRO SEMÂNTICO: {e}")
        sys.exit(4)
    except Exception as e:
        print(f"\n[ERRO] ERRO INTERNO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(5)


if __name__ == "__main__":
    main()
