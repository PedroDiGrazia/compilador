"""
Script para criar executáveis do Compilador LPD e Máquina Virtual.
Utiliza PyInstaller para gerar executáveis standalone.

Uso:
    python3 criar_executaveis.py

Pré-requisitos:
    pip install pyinstaller
"""

import subprocess
import sys
import os


def criar_executavel(script: str, nome: str):
    """Cria um executável a partir de um script Python."""
    print(f"\n{'='*50}")
    print(f"Criando executável: {nome}")
    print(f"{'='*50}")
    
    comando = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--name', nome,
        '--clean',
        script
    ]
    
    try:
        resultado = subprocess.run(comando, check=True)
        print(f"\n[OK] Executável '{nome}' criado com sucesso!")
        print(f"     Localização: dist/{nome}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[ERRO] Falha ao criar executável '{nome}'")
        print(f"       Código de erro: {e.returncode}")
        return False
    except FileNotFoundError:
        print("\n[ERRO] PyInstaller não encontrado!")
        print("       Instale com: pip install pyinstaller")
        return False


def main():
    """Função principal."""
    print("=" * 60)
    print("GERADOR DE EXECUTÁVEIS - COMPILADOR LPD")
    print("=" * 60)
    
    # Verifica se os arquivos existem
    arquivos = [
        ('compilador.py', 'compilador_lpd'),
        ('maquina_virtual.py', 'maquina_virtual'),
        ('interface.py', 'interface_lpd')
    ]
    
    for script, _ in arquivos:
        if not os.path.exists(script):
            print(f"\n[ERRO] Arquivo '{script}' não encontrado!")
            print("       Execute este script na pasta do projeto.")
            sys.exit(1)
    
    # Cria os executáveis
    sucessos = 0
    for script, nome in arquivos:
        if criar_executavel(script, nome):
            sucessos += 1
    
    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO")
    print("=" * 60)
    print(f"Executáveis criados: {sucessos}/{len(arquivos)}")
    
    if sucessos == len(arquivos):
        print("\n[OK] Todos os executáveis foram criados com sucesso!")
        print("\nExecutáveis disponíveis em:")
        print("  - dist/compilador_lpd")
        print("  - dist/maquina_virtual")
        print("  - dist/interface_lpd")
    else:
        print("\n[AVISO] Alguns executáveis não foram criados.")
        sys.exit(1)


if __name__ == '__main__':
    main()
