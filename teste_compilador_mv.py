#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste integrado: Compilador + Máquina Virtual
Testa o fluxo completo de compilação e execução de programas LPD.

Uso:
    python3 teste_compilador_mv.py programa.lpd
"""

import sys
import os
import subprocess
from pathlib import Path


def executar_teste(arquivo_lpd: str):
    """
    Executa teste completo: compila e executa programa LPD.
    
    Args:
        arquivo_lpd: Caminho para o arquivo .lpd
    """
    print("=" * 70)
    print("TESTE COMPLETO: COMPILADOR + MÁQUINA VIRTUAL")
    print("=" * 70)
    print(f"Arquivo fonte: {arquivo_lpd}\n")
    
    # Verifica se arquivo existe
    if not os.path.exists(arquivo_lpd):
        print(f"❌ Erro: Arquivo não encontrado: {arquivo_lpd}")
        return False
    
    # Define nome do arquivo assembly (compilador gera saida.asm por padrão)
    nome_base = os.path.basename(arquivo_lpd).replace('.lpd', '')
    arquivo_asm = f"{nome_base}.asm"
    
    # Passo 1: Compilação
    print("=" * 70)
    print("PASSO 1: COMPILAÇÃO")
    print("=" * 70)
    cmd_compilar = f"python3 main.py {arquivo_lpd} -o {arquivo_asm}"
    print(f"Comando: {cmd_compilar}\n")
    
    result = subprocess.run(cmd_compilar, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ ERRO NA COMPILAÇÃO:")
        print(result.stderr)
        return False
    
    print(result.stdout)
    print("✅ Compilação concluída com sucesso!\n")
    
    # Verifica se arquivo .asm foi gerado
    if not os.path.exists(arquivo_asm):
        print(f"❌ Erro: Arquivo assembly não foi gerado: {arquivo_asm}")
        return False
    
    # Passo 2: Execução na Máquina Virtual
    print("=" * 70)
    print("PASSO 2: EXECUÇÃO NA MÁQUINA VIRTUAL")
    print("=" * 70)
    cmd_executar = f"python3 maquina_virtual.py {arquivo_asm}"
    print(f"Comando: {cmd_executar}\n")
    
    result = subprocess.run(cmd_executar, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ ERRO NA EXECUÇÃO:")
        print(result.stderr)
        return False
    
    print(result.stdout)
    print("✅ Execução concluída com sucesso!\n")
    
    # Passo 3: Mostra código assembly gerado
    print("=" * 70)
    print("CÓDIGO ASSEMBLY GERADO:")
    print("=" * 70)
    with open(arquivo_asm, 'r') as f:
        conteudo = f.read()
        print(conteudo)
    
    print("\n" + "=" * 70)
    print("✅ TESTE COMPLETO: SUCESSO!")
    print("=" * 70)
    return True


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 teste_compilador_mv.py <arquivo.lpd>")
        print("\nExemplos:")
        print("  python3 teste_compilador_mv.py exemplos/prog1.lpd")
        print("  python3 teste_compilador_mv.py exemplos/prog3.lpd")
        sys.exit(1)
    
    arquivo = sys.argv[1]
    sucesso = executar_teste(arquivo)
    
    sys.exit(0 if sucesso else 1)


if __name__ == '__main__':
    main()

