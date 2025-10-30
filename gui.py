#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface Gráfica para o Compilador LPD + Máquina Virtual

Interface gráfica simples usando tkinter para facilitar o uso do compilador
e da máquina virtual de forma visual e intuitiva.

Autor: Projeto Compiladores - PUC
Data: 2025
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import subprocess
import os
from pathlib import Path


class CompiladorGUI:
    """Interface Gráfica do Compilador LPD."""
    
    def __init__(self, root):
        """Inicializa a interface gráfica."""
        self.root = root
        self.root.title("Compilador LPD + Máquina Virtual")
        self.root.geometry("900x700")
        
        # Variáveis
        self.arquivo_lpd = tk.StringVar()
        self.arquivo_asm = tk.StringVar()
        
        # Configurar interface
        self.criar_interface()
        
    def criar_interface(self):
        """Cria os componentes da interface."""
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # ==== SEÇÃO 1: Seleção de Arquivo ====
        arquivo_frame = ttk.LabelFrame(main_frame, text="1. Arquivo Fonte (.lpd)", padding="10")
        arquivo_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        arquivo_frame.columnconfigure(1, weight=1)
        
        ttk.Label(arquivo_frame, text="Arquivo:").grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Entry(arquivo_frame, textvariable=self.arquivo_lpd, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(arquivo_frame, text="Procurar...", command=self.selecionar_arquivo).grid(row=0, column=2, padx=5)
        
        # Exemplos rápidos
        exemplos_frame = ttk.Frame(arquivo_frame)
        exemplos_frame.grid(row=1, column=0, columnspan=3, pady=5)
        ttk.Label(exemplos_frame, text="Exemplos:").pack(side=tk.LEFT, padx=5)
        ttk.Button(exemplos_frame, text="prog1.lpd", command=lambda: self.carregar_exemplo("prog1.lpd")).pack(side=tk.LEFT, padx=2)
        ttk.Button(exemplos_frame, text="prog3.lpd", command=lambda: self.carregar_exemplo("prog3.lpd")).pack(side=tk.LEFT, padx=2)
        ttk.Button(exemplos_frame, text="teste_completo.lpd", command=lambda: self.carregar_exemplo("teste_completo.lpd")).pack(side=tk.LEFT, padx=2)
        
        # ==== SEÇÃO 2: Ações ====
        acoes_frame = ttk.LabelFrame(main_frame, text="2. Ações", padding="10")
        acoes_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Botões de ação
        btn_frame = ttk.Frame(acoes_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="📝 Apenas Léxico", command=self.executar_lexico, width=20).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(btn_frame, text="🔍 Apenas Sintático", command=self.executar_sintatico, width=20).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(btn_frame, text="✓ Apenas Semântico", command=self.executar_semantico, width=20).pack(side=tk.LEFT, padx=5, pady=5)
        
        btn_frame2 = ttk.Frame(acoes_frame)
        btn_frame2.pack(fill=tk.X)
        
        ttk.Button(btn_frame2, text="⚙️ COMPILAR", command=self.compilar, width=30, style="Accent.TButton").pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(btn_frame2, text="▶️ EXECUTAR NA MV", command=self.executar_mv, width=30, style="Accent.TButton").pack(side=tk.LEFT, padx=5, pady=5)
        
        btn_frame3 = ttk.Frame(acoes_frame)
        btn_frame3.pack(fill=tk.X)
        
        ttk.Button(btn_frame3, text="🚀 COMPILAR + EXECUTAR", command=self.compilar_e_executar, width=40).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(btn_frame3, text="🗑️ Limpar", command=self.limpar_saida, width=15).pack(side=tk.LEFT, padx=5, pady=5)
        
        # ==== SEÇÃO 3: Resultado ====
        resultado_frame = ttk.LabelFrame(main_frame, text="3. Resultado", padding="10")
        resultado_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        resultado_frame.columnconfigure(1, weight=1)
        
        ttk.Label(resultado_frame, text="Assembly gerado:").grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Entry(resultado_frame, textvariable=self.arquivo_asm, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(resultado_frame, text="Ver Código", command=self.ver_codigo_asm).grid(row=0, column=2, padx=5)
        
        # ==== SEÇÃO 4: Saída ====
        saida_frame = ttk.LabelFrame(main_frame, text="4. Saída / Log", padding="10")
        saida_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        saida_frame.columnconfigure(0, weight=1)
        saida_frame.rowconfigure(0, weight=1)
        
        # Área de texto com scroll
        self.texto_saida = scrolledtext.ScrolledText(saida_frame, height=20, wrap=tk.WORD)
        self.texto_saida.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar tags para cores
        self.texto_saida.tag_config("erro", foreground="red")
        self.texto_saida.tag_config("sucesso", foreground="green")
        self.texto_saida.tag_config("info", foreground="blue")
        
        # ==== BARRA DE STATUS ====
        self.status = tk.StringVar(value="Pronto")
        status_bar = ttk.Label(self.root, textvariable=self.status, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Menu
        self.criar_menu()
        
        # Mensagem inicial
        self.adicionar_saida("=== Compilador LPD + Máquina Virtual ===\n", "info")
        self.adicionar_saida("Selecione um arquivo .lpd ou escolha um exemplo para começar.\n\n", "info")
        
    def criar_menu(self):
        """Cria a barra de menu."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Arquivo
        menu_arquivo = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=menu_arquivo)
        menu_arquivo.add_command(label="Abrir...", command=self.selecionar_arquivo)
        menu_arquivo.add_separator()
        menu_arquivo.add_command(label="Sair", command=self.root.quit)
        
        # Menu Exemplos
        menu_exemplos = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Exemplos", menu=menu_exemplos)
        menu_exemplos.add_command(label="prog1.lpd (Básico)", command=lambda: self.carregar_exemplo("prog1.lpd"))
        menu_exemplos.add_command(label="prog2.lpd (Condicional)", command=lambda: self.carregar_exemplo("prog2.lpd"))
        menu_exemplos.add_command(label="prog3.lpd (Loop)", command=lambda: self.carregar_exemplo("prog3.lpd"))
        menu_exemplos.add_command(label="teste_completo.lpd (Completo)", command=lambda: self.carregar_exemplo("teste_completo.lpd"))
        menu_exemplos.add_command(label="teste_unario.lpd (Operador Unário)", command=lambda: self.carregar_exemplo("teste_unario.lpd"))
        menu_exemplos.add_separator()
        menu_exemplos.add_command(label="erro.lpd (Erro Léxico)", command=lambda: self.carregar_exemplo("erro.lpd"))
        
        # Menu Ajuda
        menu_ajuda = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=menu_ajuda)
        menu_ajuda.add_command(label="Como Usar", command=self.mostrar_ajuda)
        menu_ajuda.add_command(label="Sobre", command=self.mostrar_sobre)
        
    def selecionar_arquivo(self):
        """Abre diálogo para selecionar arquivo .lpd."""
        filename = filedialog.askopenfilename(
            title="Selecionar arquivo LPD",
            filetypes=[("Arquivos LPD", "*.lpd"), ("Todos os arquivos", "*.*")]
        )
        if filename:
            self.arquivo_lpd.set(filename)
            self.arquivo_asm.set(filename.replace('.lpd', '.asm'))
            self.status.set(f"Arquivo carregado: {os.path.basename(filename)}")
            self.adicionar_saida(f"\n✓ Arquivo carregado: {filename}\n", "sucesso")
            
    def carregar_exemplo(self, exemplo):
        """Carrega um arquivo de exemplo."""
        caminho = Path("exemplos") / exemplo
        if caminho.exists():
            self.arquivo_lpd.set(str(caminho))
            self.arquivo_asm.set(exemplo.replace('.lpd', '.asm'))
            self.status.set(f"Exemplo carregado: {exemplo}")
            self.adicionar_saida(f"\n✓ Exemplo carregado: {exemplo}\n", "sucesso")
        else:
            messagebox.showerror("Erro", f"Arquivo de exemplo não encontrado: {caminho}")
            
    def adicionar_saida(self, texto, tag=None):
        """Adiciona texto à área de saída."""
        self.texto_saida.insert(tk.END, texto, tag)
        self.texto_saida.see(tk.END)
        
    def limpar_saida(self):
        """Limpa a área de saída."""
        self.texto_saida.delete(1.0, tk.END)
        self.status.set("Saída limpa")
        
    def executar_comando(self, comando, titulo):
        """Executa um comando e mostra o resultado."""
        if not self.arquivo_lpd.get():
            messagebox.showwarning("Aviso", "Selecione um arquivo .lpd primeiro!")
            return
            
        self.adicionar_saida(f"\n{'='*60}\n", "info")
        self.adicionar_saida(f"{titulo}\n", "info")
        self.adicionar_saida(f"{'='*60}\n", "info")
        self.status.set(f"Executando: {titulo}...")
        self.root.update()
        
        try:
            result = subprocess.run(
                comando,
                shell=True,
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            if result.stdout:
                self.adicionar_saida(result.stdout)
                
            if result.stderr:
                self.adicionar_saida(result.stderr, "erro")
                
            if result.returncode == 0:
                self.adicionar_saida(f"\n✓ {titulo} concluído com sucesso!\n", "sucesso")
                self.status.set(f"{titulo} - Sucesso")
            else:
                self.adicionar_saida(f"\n✗ {titulo} falhou!\n", "erro")
                self.status.set(f"{titulo} - Erro")
                
        except Exception as e:
            self.adicionar_saida(f"\n✗ Erro ao executar: {str(e)}\n", "erro")
            self.status.set("Erro na execução")
            
    def executar_lexico(self):
        """Executa apenas análise léxica."""
        cmd = f"python3 main.py {self.arquivo_lpd.get()} --lex"
        self.executar_comando(cmd, "ANÁLISE LÉXICA")
        
    def executar_sintatico(self):
        """Executa análise sintática."""
        cmd = f"python3 main.py {self.arquivo_lpd.get()} --parse"
        self.executar_comando(cmd, "ANÁLISE SINTÁTICA")
        
    def executar_semantico(self):
        """Executa análise semântica."""
        cmd = f"python3 main.py {self.arquivo_lpd.get()} --semantic"
        self.executar_comando(cmd, "ANÁLISE SEMÂNTICA")
        
    def compilar(self):
        """Compila o programa."""
        if not self.arquivo_asm.get():
            self.arquivo_asm.set(self.arquivo_lpd.get().replace('.lpd', '.asm'))
            
        cmd = f"python3 main.py {self.arquivo_lpd.get()} -o {self.arquivo_asm.get()}"
        self.executar_comando(cmd, "COMPILAÇÃO COMPLETA")
        
    def executar_mv(self):
        """Executa na Máquina Virtual."""
        if not self.arquivo_asm.get() or not os.path.exists(self.arquivo_asm.get()):
            messagebox.showwarning("Aviso", "Compile o programa primeiro!")
            return
            
        cmd = f"python3 maquina_virtual.py {self.arquivo_asm.get()}"
        self.executar_comando(cmd, "EXECUÇÃO NA MÁQUINA VIRTUAL")
        
    def compilar_e_executar(self):
        """Compila e executa o programa."""
        self.compilar()
        self.root.after(500, self.executar_mv)  # Aguarda 500ms antes de executar
        
    def ver_codigo_asm(self):
        """Mostra o código assembly gerado."""
        if not self.arquivo_asm.get() or not os.path.exists(self.arquivo_asm.get()):
            messagebox.showwarning("Aviso", "Nenhum código assembly gerado ainda!")
            return
            
        try:
            with open(self.arquivo_asm.get(), 'r') as f:
                codigo = f.read()
                
            # Criar janela para mostrar código
            janela = tk.Toplevel(self.root)
            janela.title(f"Código Assembly - {os.path.basename(self.arquivo_asm.get())}")
            janela.geometry("600x500")
            
            texto = scrolledtext.ScrolledText(janela, wrap=tk.WORD)
            texto.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            texto.insert(1.0, codigo)
            texto.config(state=tk.DISABLED)
            
            ttk.Button(janela, text="Fechar", command=janela.destroy).pack(pady=5)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ler arquivo: {str(e)}")
            
    def mostrar_ajuda(self):
        """Mostra ajuda sobre como usar."""
        ajuda = """
        COMO USAR O COMPILADOR LPD
        
        1. SELECIONAR ARQUIVO
           - Clique em "Procurar..." ou use o menu Arquivo > Abrir
           - Ou escolha um exemplo nos botões rápidos
        
        2. COMPILAR
           - Clique em "COMPILAR" para gerar código assembly
           - Ou use os botões individuais para cada fase
        
        3. EXECUTAR
           - Clique em "EXECUTAR NA MV" para rodar o programa
           - Ou use "COMPILAR + EXECUTAR" para fazer tudo de uma vez
        
        4. VER RESULTADOS
           - O log mostra todas as mensagens
           - Clique em "Ver Código" para ver o assembly gerado
        
        ATALHOS:
        - Exemplos no menu para teste rápido
        - "Limpar" para limpar a área de saída
        
        Para mais informações, consulte o MANUAL.md
        """
        
        janela = tk.Toplevel(self.root)
        janela.title("Como Usar")
        janela.geometry("500x400")
        
        texto = scrolledtext.ScrolledText(janela, wrap=tk.WORD)
        texto.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        texto.insert(1.0, ajuda)
        texto.config(state=tk.DISABLED)
        
        ttk.Button(janela, text="Fechar", command=janela.destroy).pack(pady=5)
        
    def mostrar_sobre(self):
        """Mostra informações sobre o projeto."""
        sobre = """
        COMPILADOR LPD + MÁQUINA VIRTUAL DIDÁTICA
        
        Versão: 1.0
        
        Projeto acadêmico para a disciplina de Compiladores.
        
        Implementa:
        • Análise Léxica
        • Análise Sintática (Parser Descendente Recursivo)
        • Análise Semântica
        • Geração de Código (Assembly MVD)
        • Máquina Virtual para execução
        
        100% compatível com as especificações das
        "Notas de Aula de Compiladores"
        
        PUC - Compiladores 2025
        """
        
        messagebox.showinfo("Sobre", sobre)


def main():
    """Função principal para iniciar a GUI."""
    root = tk.Tk()
    
    # Tentar usar tema moderno
    try:
        style = ttk.Style()
        style.theme_use('clam')  # Tema mais moderno
    except:
        pass
    
    app = CompiladorGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()

