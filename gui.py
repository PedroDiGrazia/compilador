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
import threading

# Importa a máquina virtual para execução direta
from maquina_virtual import MaquinaVirtual, MVDError


class CompiladorGUI:
    """Interface Gráfica do Compilador LPD."""
    
    def __init__(self, root):
        """Inicializa a interface gráfica."""
        self.root = root
        self.root.title("Compilador LPD")
        self.root.geometry("800x600")
        
        # Variáveis
        self.arquivo_lpd = tk.StringVar()
        self.arquivo_asm = tk.StringVar()
        self.entrada_usuario = tk.StringVar()
        
        # Estado da MV
        self.mv = None
        self.mv_thread = None
        self.aguardando_input = False
        self.input_event = threading.Event()
        self.valor_input = None
        
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
        main_frame.rowconfigure(2, weight=1)
        
        # ==== SEÇÃO 1: Seleção de Arquivo ====
        arquivo_frame = ttk.LabelFrame(main_frame, text="1. Arquivo Fonte (.txt)", padding="10")
        arquivo_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        arquivo_frame.columnconfigure(1, weight=1)
        
        ttk.Label(arquivo_frame, text="Arquivo:").grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Entry(arquivo_frame, textvariable=self.arquivo_lpd, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(arquivo_frame, text="Procurar...", command=self.selecionar_arquivo).grid(row=0, column=2, padx=5)
        
        # ==== SEÇÃO 2: Compilar ====
        compilar_frame = ttk.LabelFrame(main_frame, text="2. Compilar", padding="10")
        compilar_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Linha 1: Analisadores individuais
        analise_frame = ttk.Frame(compilar_frame)
        analise_frame.pack(fill=tk.X)
        
        ttk.Button(analise_frame, text="Léxico", command=self.executar_lexico, width=15).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(analise_frame, text="Sintático", command=self.executar_sintatico, width=15).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(analise_frame, text="Semântico", command=self.executar_semantico, width=15).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Linha 2: Compilar e Executar
        btn_frame = ttk.Frame(compilar_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="COMPILAR", command=self.compilar, width=20).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(btn_frame, text="EXECUTAR VM", command=self.executar_mv, width=20).pack(side=tk.LEFT, padx=5, pady=5)
        
        # ==== SEÇÃO 3: Saída / Terminal ====
        saida_frame = ttk.LabelFrame(main_frame, text="3. Saída", padding="10")
        saida_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        saida_frame.columnconfigure(0, weight=1)
        saida_frame.rowconfigure(0, weight=1)
        
        # Área de texto com scroll
        self.texto_saida = scrolledtext.ScrolledText(saida_frame, height=20, wrap=tk.WORD, 
                                                      bg='white', fg='black',
                                                      insertbackground='black',
                                                      font=('Consolas', 10))
        self.texto_saida.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Frame de entrada (para inputs interativos)
        input_frame = ttk.Frame(saida_frame)
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        input_frame.columnconfigure(1, weight=1)
        
        self.label_input = ttk.Label(input_frame, text="")
        self.label_input.grid(row=0, column=0, sticky=tk.W, padx=5)
        
        self.entry_input = ttk.Entry(input_frame, textvariable=self.entrada_usuario, width=50)
        self.entry_input.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        self.entry_input.bind('<Return>', self.enviar_input)
        
        self.btn_enviar = ttk.Button(input_frame, text="Enviar", command=self.enviar_input, state=tk.DISABLED)
        self.btn_enviar.grid(row=0, column=2, padx=5)
        
        # ==== BARRA DE STATUS ====
        self.status = tk.StringVar(value="Pronto")
        status_bar = ttk.Label(self.root, textvariable=self.status, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Mensagem inicial
        self.adicionar_saida("Compilador LPD - Selecione um arquivo .txt para começar\n", "info")
        
    def selecionar_arquivo(self):
        """Abre diálogo para selecionar arquivo .txt."""
        filename = filedialog.askopenfilename(
            title="Selecionar arquivo LPD",
            filetypes=[("Arquivos LPD", "*.txt"), ("Todos os arquivos", "*.*")]
        )
        if filename:
            self.arquivo_lpd.set(filename)
            # Salva .obj na pasta compilado
            dir_fonte = os.path.dirname(filename)
            nome_base = os.path.basename(filename).replace('.txt', '.obj')
            pasta_compilado = os.path.join(dir_fonte, 'compilado')
            os.makedirs(pasta_compilado, exist_ok=True)
            self.arquivo_asm.set(os.path.join(pasta_compilado, nome_base))
            self.status.set(f"Arquivo: {os.path.basename(filename)}")
            self.adicionar_saida(f"\n> Arquivo carregado: {filename}\n", "sucesso")
            
    def adicionar_saida(self, texto, tag=None):
        """Adiciona texto à área de saída."""
        self.texto_saida.insert(tk.END, texto, tag)
        self.texto_saida.see(tk.END)
        self.root.update_idletasks()
        
    def limpar_saida(self):
        """Limpa a área de saída."""
        self.texto_saida.delete(1.0, tk.END)
        self.status.set("Pronto")
        
    def executar_comando(self, comando, titulo):
        """Executa um comando e mostra o resultado."""
        if not self.arquivo_lpd.get():
            messagebox.showwarning("Aviso", "Selecione um arquivo .txt primeiro!")
            return
            
        self.adicionar_saida(f"\n{'='*50}\n", "info")
        self.adicionar_saida(f"{titulo}\n", "info")
        self.adicionar_saida(f"{'='*50}\n", "info")
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
                self.adicionar_saida(f"\n[OK] {titulo} concluído\n", "sucesso")
                self.status.set(f"{titulo} - OK")
            else:
                self.adicionar_saida(f"\n[ERRO] {titulo} falhou\n", "erro")
                self.status.set(f"{titulo} - Erro")
                
        except Exception as e:
            self.adicionar_saida(f"\n[ERRO] {str(e)}\n", "erro")
            self.status.set("Erro")
            
    def executar_lexico(self):
        """Executa apenas análise léxica."""
        cmd = f"python3 main.py {self.arquivo_lpd.get()} --lex"
        self.executar_comando(cmd, "Análise Léxica")
        
    def executar_sintatico(self):
        """Executa análise sintática."""
        cmd = f"python3 main.py {self.arquivo_lpd.get()} --parse"
        self.executar_comando(cmd, "Análise Sintática")
        
    def executar_semantico(self):
        """Executa análise semântica."""
        cmd = f"python3 main.py {self.arquivo_lpd.get()} --semantic"
        self.executar_comando(cmd, "Análise Semântica")
        
    def compilar(self):
        """Compila o programa."""
        if not self.arquivo_lpd.get():
            messagebox.showwarning("Aviso", "Selecione um arquivo .txt primeiro!")
            return
            
        if not self.arquivo_asm.get():
            # Salva .obj na pasta compilado
            dir_fonte = os.path.dirname(self.arquivo_lpd.get())
            nome_base = os.path.basename(self.arquivo_lpd.get()).replace('.txt', '.obj')
            pasta_compilado = os.path.join(dir_fonte, 'compilado')
            os.makedirs(pasta_compilado, exist_ok=True)
            self.arquivo_asm.set(os.path.join(pasta_compilado, nome_base))
            
        cmd = f"python3 main.py {self.arquivo_lpd.get()} -o {self.arquivo_asm.get()}"
        self.executar_comando(cmd, "Compilação")
        
    def executar_mv(self):
        """Executa na Máquina Virtual de forma interativa."""
        if not self.arquivo_asm.get() or not os.path.exists(self.arquivo_asm.get()):
            messagebox.showwarning("Aviso", "Compile o programa primeiro!")
            return
        
        # Inicia execução em thread separada
        self.mv_thread = threading.Thread(target=self._executar_mv_thread, daemon=True)
        self.mv_thread.start()
        
    def _executar_mv_thread(self):
        """Executa a MV em thread separada para não travar a GUI."""
        try:
            self.adicionar_saida(f"\n{'='*50}\n", "info")
            self.adicionar_saida("Execução na Máquina Virtual\n", "info")
            self.adicionar_saida(f"{'='*50}\n", "info")
            
            # Carrega e configura a MV
            self.mv = MaquinaVirtual()
            self.mv.carregar_programa(self.arquivo_asm.get())
            
            self.adicionar_saida(f"Programa carregado: {len(self.mv.P)} instruções\n\n", "info")
            
            # Executa com callback para input
            self._executar_mv_interativo()
            
            self.adicionar_saida("\n[OK] Execução concluída\n", "sucesso")
            self.status.set("Execução concluída")
            
        except MVDError as e:
            self.adicionar_saida(f"\n[ERRO] {str(e)}\n", "erro")
            self.status.set("Erro na execução")
        except Exception as e:
            self.adicionar_saida(f"\n[ERRO] {str(e)}\n", "erro")
            self.status.set("Erro")
        finally:
            self._desabilitar_input()
    
    def _executar_mv_interativo(self):
        """Executa a MV instrução por instrução com suporte a input interativo."""
        self.mv.executando = True
        self.mv.i = 0
        self.mv.s = -1
        self.mv.saida = []
        
        while self.mv.executando and self.mv.i < len(self.mv.P):
            instrucao, operandos = self.mv.P[self.mv.i]
            
            # Tratamento especial para RD (leitura)
            if instrucao == 'RD':
                self._habilitar_input()
                self.adicionar_saida("Digite um valor inteiro: ", "prompt")
                
                # Aguarda input do usuário
                self.input_event.clear()
                self.input_event.wait()
                
                # Processa o valor
                try:
                    valor = int(self.valor_input)
                    self.mv.s += 1
                    self.mv.M[self.mv.s] = valor
                    self.adicionar_saida(f"{valor}\n", "input")
                    self.mv.i += 1
                except (ValueError, TypeError):
                    raise MVDError("Entrada inválida: esperado inteiro")
                    
                self._desabilitar_input()
                
            # Tratamento especial para PRN (impressão)
            elif instrucao == 'PRN':
                if self.mv.s < 0:
                    raise MVDError("Stack underflow em PRN")
                valor = self.mv.M[self.mv.s]
                self.adicionar_saida(f"{valor}\n", "output")
                self.mv.saida.append(valor)
                self.mv.s -= 1
                self.mv.i += 1
                
            # Outras instruções
            else:
                self.mv._executar_instrucao(instrucao, operandos)
    
    def _habilitar_input(self):
        """Habilita o campo de entrada."""
        self.aguardando_input = True
        self.root.after(0, lambda: self._set_input_state(True))
        
    def _desabilitar_input(self):
        """Desabilita o campo de entrada."""
        self.aguardando_input = False
        self.root.after(0, lambda: self._set_input_state(False))
        
    def _set_input_state(self, habilitado):
        """Define o estado do campo de entrada (thread-safe)."""
        if habilitado:
            self.label_input.config(text="Entrada:")
            self.btn_enviar.config(state=tk.NORMAL)
            self.entry_input.config(state=tk.NORMAL)
            self.entry_input.focus_set()
        else:
            self.label_input.config(text="")
            self.btn_enviar.config(state=tk.DISABLED)
            self.entrada_usuario.set("")
            
    def enviar_input(self, event=None):
        """Envia o valor digitado para a MV."""
        if self.aguardando_input:
            self.valor_input = self.entrada_usuario.get().strip()
            self.entrada_usuario.set("")
            self.input_event.set()


def main():
    """Função principal para iniciar a GUI."""
    root = tk.Tk()
    
    # Tentar usar tema moderno
    try:
        style = ttk.Style()
        style.theme_use('clam')
    except Exception:
        pass
    
    app = CompiladorGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
