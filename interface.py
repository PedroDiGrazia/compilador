#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface Gráfica para o Compilador LPD + Máquina Virtual
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import subprocess
import os
import threading

# Importa a máquina virtual para execução direta
from maquina_virtual import MaquinaVirtual, ErroMVD


class InterfaceCompilador:
    """Interface Gráfica do Compilador LPD."""
    
    def __init__(self, janela):
        """Inicializa a interface gráfica."""
        self.janela = janela
        self.janela.title("Compilador LPD")
        self.janela.geometry("800x600")
        
        # Variáveis
        self.arquivo_fonte = tk.StringVar()
        self.arquivo_objeto = tk.StringVar()
        self.entrada_usuario = tk.StringVar()
        
        # Estado da MV
        self.mv = None
        self.thread_mv = None
        self.aguardando_entrada = False
        self.evento_entrada = threading.Event()
        self.valor_entrada = None
        
        # Configurar interface
        self.criar_interface()
        
    def criar_interface(self):
        """Cria os componentes da interface."""
        
        # Frame principal
        frame_principal = ttk.Frame(self.janela, padding="10")
        frame_principal.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.janela.columnconfigure(0, weight=1)
        self.janela.rowconfigure(0, weight=1)
        frame_principal.columnconfigure(0, weight=1)
        frame_principal.rowconfigure(2, weight=1)
        
        # ==== SEÇÃO 1: Seleção de Arquivo ====
        frame_arquivo = ttk.LabelFrame(frame_principal, text="1. Arquivo Fonte (.txt)", padding="10")
        frame_arquivo.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        frame_arquivo.columnconfigure(1, weight=1)
        
        ttk.Label(frame_arquivo, text="Arquivo:").grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Entry(frame_arquivo, textvariable=self.arquivo_fonte, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(frame_arquivo, text="Procurar...", command=self.selecionar_arquivo).grid(row=0, column=2, padx=5)
        
        # ==== SEÇÃO 2: Compilar ====
        frame_compilar = ttk.LabelFrame(frame_principal, text="2. Compilar", padding="10")
        frame_compilar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Linha 1: Analisadores individuais
        frame_analise = ttk.Frame(frame_compilar)
        frame_analise.pack(fill=tk.X)
        
        ttk.Button(frame_analise, text="Léxico", command=self.executar_lexico, width=15).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(frame_analise, text="Sintático", command=self.executar_sintatico, width=15).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(frame_analise, text="Semântico", command=self.executar_semantico, width=15).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Linha 2: Compilar e Executar
        frame_botoes = ttk.Frame(frame_compilar)
        frame_botoes.pack(fill=tk.X)
        
        ttk.Button(frame_botoes, text="COMPILAR", command=self.compilar, width=20).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(frame_botoes, text="EXECUTAR VM", command=self.executar_mv, width=20).pack(side=tk.LEFT, padx=5, pady=5)
        
        # ==== SEÇÃO 3: Saída / Terminal ====
        frame_saida = ttk.LabelFrame(frame_principal, text="3. Saída", padding="10")
        frame_saida.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        frame_saida.columnconfigure(0, weight=1)
        frame_saida.rowconfigure(0, weight=1)
        
        # Área de texto com scroll
        self.texto_saida = scrolledtext.ScrolledText(frame_saida, height=20, wrap=tk.WORD, 
                                                      bg='white', fg='black',
                                                      insertbackground='black',
                                                      font=('Consolas', 10))
        self.texto_saida.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Frame de entrada (para inputs interativos)
        frame_entrada = ttk.Frame(frame_saida)
        frame_entrada.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        frame_entrada.columnconfigure(1, weight=1)
        
        self.label_entrada = ttk.Label(frame_entrada, text="")
        self.label_entrada.grid(row=0, column=0, sticky=tk.W, padx=5)
        
        self.campo_entrada = ttk.Entry(frame_entrada, textvariable=self.entrada_usuario, width=50)
        self.campo_entrada.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        self.campo_entrada.bind('<Return>', self.enviar_entrada)
        
        self.btn_enviar = ttk.Button(frame_entrada, text="Enviar", command=self.enviar_entrada, state=tk.DISABLED)
        self.btn_enviar.grid(row=0, column=2, padx=5)
        
        # ==== BARRA DE STATUS ====
        self.status = tk.StringVar(value="Pronto")
        barra_status = ttk.Label(self.janela, textvariable=self.status, relief=tk.SUNKEN, anchor=tk.W)
        barra_status.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Mensagem inicial
        self.adicionar_saida("Compilador LPD - Selecione um arquivo .txt para começar\n", "info")
        
    def selecionar_arquivo(self):
        """Abre diálogo para selecionar arquivo .txt."""
        nome_arquivo = filedialog.askopenfilename(
            title="Selecionar arquivo LPD",
            filetypes=[("Arquivos LPD", "*.txt"), ("Todos os arquivos", "*.*")]
        )
        if nome_arquivo:
            self.arquivo_fonte.set(nome_arquivo)
            # Salva .obj na mesma pasta do executável
            nome_base = os.path.basename(nome_arquivo).replace('.txt', '.obj')
            self.arquivo_objeto.set(nome_base)
            self.status.set(f"Arquivo: {os.path.basename(nome_arquivo)}")
            self.adicionar_saida(f"\n> Arquivo carregado: {nome_arquivo}\n", "sucesso")
            
    def adicionar_saida(self, texto, tag=None):
        """Adiciona texto à área de saída."""
        self.texto_saida.insert(tk.END, texto, tag)
        self.texto_saida.see(tk.END)
        self.janela.update_idletasks()
        
    def limpar_saida(self):
        """Limpa a área de saída."""
        self.texto_saida.delete(1.0, tk.END)
        self.status.set("Pronto")
        
    def executar_comando(self, comando, titulo):
        """Executa um comando e mostra o resultado."""
        if not self.arquivo_fonte.get():
            messagebox.showwarning("Aviso", "Selecione um arquivo .txt primeiro!")
            return
            
        self.adicionar_saida(f"\n{'='*50}\n", "info")
        self.adicionar_saida(f"{titulo}\n", "info")
        self.adicionar_saida(f"{'='*50}\n", "info")
        self.status.set(f"Executando: {titulo}...")
        self.janela.update()
        
        try:
            resultado = subprocess.run(
                comando,
                shell=True,
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            if resultado.stdout:
                self.adicionar_saida(resultado.stdout)
                
            if resultado.stderr:
                self.adicionar_saida(resultado.stderr, "erro")
                
            if resultado.returncode == 0:
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
        cmd = f"python3 compilador.py {self.arquivo_fonte.get()} --lexico"
        self.executar_comando(cmd, "Análise Léxica")
        
    def executar_sintatico(self):
        """Executa análise sintática."""
        cmd = f"python3 compilador.py {self.arquivo_fonte.get()} --sintatico"
        self.executar_comando(cmd, "Análise Sintática")
        
    def executar_semantico(self):
        """Executa análise semântica."""
        cmd = f"python3 compilador.py {self.arquivo_fonte.get()} --semantico"
        self.executar_comando(cmd, "Análise Semântica")
        
    def compilar(self):
        """Compila o programa."""
        if not self.arquivo_fonte.get():
            messagebox.showwarning("Aviso", "Selecione um arquivo .txt primeiro!")
            return
            
        if not self.arquivo_objeto.get():
            # Salva .obj na mesma pasta do executável
            nome_base = os.path.basename(self.arquivo_fonte.get()).replace('.txt', '.obj')
            self.arquivo_objeto.set(nome_base)
            
        cmd = f"python3 compilador.py {self.arquivo_fonte.get()}"
        self.executar_comando(cmd, "Compilação")
        
    def executar_mv(self):
        """Executa na Máquina Virtual de forma interativa."""
        if not self.arquivo_objeto.get() or not os.path.exists(self.arquivo_objeto.get()):
            messagebox.showwarning("Aviso", "Compile o programa primeiro!")
            return
        
        # Inicia execução em thread separada
        self.thread_mv = threading.Thread(target=self._executar_mv_thread, daemon=True)
        self.thread_mv.start()
        
    def _executar_mv_thread(self):
        """Executa a MV em thread separada para não travar a GUI."""
        try:
            self.adicionar_saida(f"\n{'='*50}\n", "info")
            self.adicionar_saida("Execução na Máquina Virtual\n", "info")
            self.adicionar_saida(f"{'='*50}\n", "info")
            
            # Carrega e configura a MV
            self.mv = MaquinaVirtual()
            self.mv.carregar_programa(self.arquivo_objeto.get())
            
            self.adicionar_saida(f"Programa carregado: {len(self.mv.P)} instruções\n\n", "info")
            
            # Executa com callback para input
            self._executar_mv_interativo()
            
            self.adicionar_saida("\n[OK] Execução concluída\n", "sucesso")
            self.status.set("Execução concluída")
            
        except ErroMVD as e:
            self.adicionar_saida(f"\n[ERRO] {str(e)}\n", "erro")
            self.status.set("Erro na execução")
        except Exception as e:
            self.adicionar_saida(f"\n[ERRO] {str(e)}\n", "erro")
            self.status.set("Erro")
        finally:
            self._desabilitar_entrada()
    
    def _executar_mv_interativo(self):
        """Executa a MV instrução por instrução com suporte a entrada interativa."""
        self.mv.executando = True
        self.mv.i = 0
        self.mv.s = -1
        self.mv.saida = []
        
        while self.mv.executando and self.mv.i < len(self.mv.P):
            instrucao, operandos = self.mv.P[self.mv.i]
            
            # Tratamento especial para RD (leitura)
            if instrucao == 'RD':
                self._habilitar_entrada()
                self.adicionar_saida("Digite um valor inteiro: ", "prompt")
                
                # Aguarda entrada do usuário
                self.evento_entrada.clear()
                self.evento_entrada.wait()
                
                # Processa o valor
                try:
                    valor = int(self.valor_entrada)
                    self.mv.s += 1
                    self.mv.M[self.mv.s] = valor
                    self.adicionar_saida(f"{valor}\n", "input")
                    self.mv.i += 1
                except (ValueError, TypeError):
                    raise ErroMVD("Entrada inválida: esperado inteiro")
                    
                self._desabilitar_entrada()
                
            # Tratamento especial para PRN (impressão)
            elif instrucao == 'PRN':
                if self.mv.s < 0:
                    raise ErroMVD("Stack underflow em PRN")
                valor = self.mv.M[self.mv.s]
                self.adicionar_saida(f"{valor}\n", "output")
                self.mv.saida.append(valor)
                self.mv.s -= 1
                self.mv.i += 1
                
            # Outras instruções
            else:
                self.mv._executar_instrucao(instrucao, operandos)
    
    def _habilitar_entrada(self):
        """Habilita o campo de entrada."""
        self.aguardando_entrada = True
        self.janela.after(0, lambda: self._definir_estado_entrada(True))
        
    def _desabilitar_entrada(self):
        """Desabilita o campo de entrada."""
        self.aguardando_entrada = False
        self.janela.after(0, lambda: self._definir_estado_entrada(False))
        
    def _definir_estado_entrada(self, habilitado):
        """Define o estado do campo de entrada (thread-safe)."""
        if habilitado:
            self.label_entrada.config(text="Entrada:")
            self.btn_enviar.config(state=tk.NORMAL)
            self.campo_entrada.config(state=tk.NORMAL)
            self.campo_entrada.focus_set()
        else:
            self.label_entrada.config(text="")
            self.btn_enviar.config(state=tk.DISABLED)
            self.entrada_usuario.set("")
            
    def enviar_entrada(self, evento=None):
        """Envia o valor digitado para a MV."""
        if self.aguardando_entrada:
            self.valor_entrada = self.entrada_usuario.get().strip()
            self.entrada_usuario.set("")
            self.evento_entrada.set()


def main():
    """Função principal para iniciar a GUI."""
    janela = tk.Tk()
    
    # Tentar usar tema moderno
    try:
        estilo = ttk.Style()
        estilo.theme_use('clam')
    except Exception:
        pass
    
    app = InterfaceCompilador(janela)
    janela.mainloop()


if __name__ == '__main__':
    main()
