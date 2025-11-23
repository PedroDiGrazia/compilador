#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import subprocess

def criar_executaveis():
    # Cria executáveis Windows usando PyInstaller.
    
    print("=" * 70)
    print("CRIANDO EXECUTÁVEIS WINDOWS")
    print("=" * 70)
    
    # Verifica se PyInstaller está instalado
    try:
        import PyInstaller
        print("[OK] PyInstaller encontrado")
    except ImportError:
        print("[AVISO] PyInstaller não encontrado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("[OK] PyInstaller instalado")
    
    print("\n" + "=" * 70)
    print("1. Criando compilador.exe...")
    print("=" * 70)
    
    # Criar executável do compilador
    cmd_compilador = [
        sys.executable,   
            "-m", "PyInstaller",
            "--onefile",
            "--name=compilador",
            "--clean",
            "main.py"
    ]
   
    result = subprocess.run(cmd_compilador, capture_output=True, text=True)
    if result.returncode == 0:
        print("[OK] compilador.exe criado com sucesso!")
    else:
        print(f"[ERRO] Erro ao criar compilador.exe:\n{result.stderr}")
        return False
    
    print("\n" + "=" * 70)
    print("2. Criando maquina_virtual.exe...")
    print("=" * 70)
    
    # Criar executável da máquina virtual
    cmd_mv = [
        sys.executable,
            "-m", 
            "PyInstaller",
            "--onefile",
            "--name=maquina_virtual",
            "--clean",
            "maquina_virtual.py"
    ]

    
    result = subprocess.run(cmd_mv, capture_output=True, text=True)
    if result.returncode == 0:
        print("[OK] maquina_virtual.exe criado com sucesso!")
    else:
        print(f"[ERRO] Erro ao criar maquina_virtual.exe:\n{result.stderr}")
        return False
    
    print("\n" + "=" * 70)
    print("[OK] EXECUTAVEIS CRIADOS COM SUCESSO!")
    print("=" * 70)
    print("\nArquivos gerados na pasta 'dist/':")
    print("  - dist/compilador.exe")
    print("  - dist/maquina_virtual.exe")
    print("\nEsses arquivos podem ser executados em Windows sem Python!")
    
    return True


if __name__ == '__main__':
    sucesso = criar_executaveis()
    sys.exit(0 if sucesso else 1)

