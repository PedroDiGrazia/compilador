"""
Gerador de Código do Compilador LPD
Implementa geração de código para a MVD conforme notas de aula (seção 7.7)
"""

from arvore_sintatica import (
    Programa, Bloco, DeclaracoesVariaveis, DeclaracaoVariavel,
    Procedimento, Funcao, ComandoComposto, Comando, Atribuicao,
    ChamadaProcedimento, ComandoLeitura, ComandoEscrita, ComandoSe,
    ComandoEnquanto, ComandoVazio, Expressao, OperacaoBinaria,
    OperacaoUnaria, Identificador, Numero, Booleano
)
from tabela_simbolos import TabelaSimbolos
from typing import List, Dict, Optional, Tuple


class GeradorCodigo:
    """
    Gerador de código para a Máquina Virtual Didática (MVD).
    
    Implementa a estrutura de geração conforme notas de aula:
    - ALLOC/DALLOC separados por escopo
    - Subrotinas aninhadas geradas DENTRO da subrotina pai
    - Retorno de função via STR para endereço reservado + RETURN
    
    A tabela de símbolos é reconstruída durante a geração de código
    para manter os escopos corretos.
    """
    
    def __init__(self):
        self.instrucoes: List[str] = []
        self.contador_rotulos = 1  # Começa em 1 conforme exemplo do professor
        
        # Mapeia nome de procedimento/função -> rótulo numérico
        self.rotulos_subrotinas: Dict[str, int] = {}
        
        # Nome da função atual (para tratar atribuição de retorno)
        self.funcao_atual: Optional[str] = None
        
        # Tabela de símbolos (reconstruída durante geração)
        self.tabela_simbolos: TabelaSimbolos = None
        
        # Pilha de informações de ALLOC para gerar DALLOC
        self.pilha_alocacao: List[Tuple[int, int]] = []
    
    # ========== Infraestrutura básica ==========
    
    def emitir(self, instrucao: str):
        """Emite uma instrução assembly."""
        self.instrucoes.append(instrucao)
    
    def novo_rotulo(self) -> int:
        """Gera um novo rótulo numérico."""
        rotulo = self.contador_rotulos
        self.contador_rotulos += 1
        return rotulo
    
    def obter_rotulo_subrotina(self, nome: str) -> int:
        """Retorna (ou cria) o rótulo associado à função/procedimento."""
        if nome not in self.rotulos_subrotinas:
            self.rotulos_subrotinas[nome] = self.novo_rotulo()
        return self.rotulos_subrotinas[nome]
    
    def emitir_alloc(self, endereco_base: int, quantidade: int):
        """Emite ALLOC e registra para posterior DALLOC."""
        if quantidade > 0:
            self.emitir(f"ALLOC {endereco_base} {quantidade}")
            self.pilha_alocacao.append((endereco_base, quantidade))
    
    def emitir_dalloc_da_pilha(self):
        """Emite DALLOC para o último ALLOC da pilha."""
        if self.pilha_alocacao:
            endereco_base, quantidade = self.pilha_alocacao.pop()
            if quantidade > 0:
                self.emitir(f"DALLOC {endereco_base} {quantidade}")
    
    # ========== Geração principal ==========
    
    def gerar(self, programa: Programa, tabela_simbolos: TabelaSimbolos = None) -> List[str]:
        """
        Gera código para o programa completo.
        
        Estrutura conforme notas de aula (seção 7.7):
        
        START
        ALLOC m,n      ; retorno de funções (se houver)
        ALLOC m,n      ; variáveis globais
        JMP Lmain      ; pula subrotinas
        
        [código das subrotinas]
        
        Lmain NULL
        [comandos principais]
        DALLOC m,n     ; variáveis globais
        DALLOC m,n     ; retorno de funções
        HLT
        """
        self.instrucoes = []
        self.contador_rotulos = 1
        self.rotulos_subrotinas = {}
        self.funcao_atual = None
        self.pilha_alocacao = []
        
        # Cria uma nova tabela de símbolos para a geração de código
        self.tabela_simbolos = TabelaSimbolos()
        
        # START
        self.emitir("START")
        
        # Calcula informações de alocação do escopo global
        qtd_retorno_funcoes = len(programa.funcoes)
        qtd_variaveis_globais = self._contar_declaracoes_variaveis(programa.declaracoes_variaveis)
        
        # Reserva posições de retorno para funções do nível global
        for func in programa.funcoes:
            self.tabela_simbolos.declarar_retorno_funcao(func.nome, func.tipo_retorno)
        
        # Declara variáveis globais na tabela
        if programa.declaracoes_variaveis:
            self._declarar_variaveis(programa.declaracoes_variaveis)
        
        # Declara procedimentos do nível global
        for proc in programa.procedimentos:
            self.tabela_simbolos.declarar_procedimento(proc.nome)
        
        # ALLOC para retorno de funções (se houver funções no nível global)
        if qtd_retorno_funcoes > 0:
            self.emitir_alloc(0, qtd_retorno_funcoes)
        
        # ALLOC para variáveis globais
        if qtd_variaveis_globais > 0:
            base = qtd_retorno_funcoes  # Começa após retornos de funções
            self.emitir_alloc(base, qtd_variaveis_globais)
        
        # Verifica se há subrotinas
        tem_subrotinas = len(programa.procedimentos) > 0 or len(programa.funcoes) > 0
        
        # JMP para o corpo principal (pula subrotinas)
        rotulo_principal = self.novo_rotulo()
        if tem_subrotinas:
            self.emitir(f"JMP {rotulo_principal}")
        
        # Gera código das subrotinas
        proximo_endereco = qtd_retorno_funcoes + qtd_variaveis_globais
        for func in programa.funcoes:
            self._gerar_funcao(func, proximo_endereco)
        
        for proc in programa.procedimentos:
            self._gerar_procedimento(proc, proximo_endereco)
        
        # Corpo principal
        self.emitir(f"{rotulo_principal} \tNULL")
        self.gera_comando_composto(programa.comando_composto)
        
        # DALLOC na ordem inversa
        while self.pilha_alocacao:
            self.emitir_dalloc_da_pilha()
        
        # HLT
        self.emitir("HLT")
        
        return self.instrucoes
    
    def _contar_declaracoes_variaveis(self, declaracoes_var: Optional[DeclaracoesVariaveis]) -> int:
        """Conta quantas variáveis são declaradas."""
        if declaracoes_var is None:
            return 0
        quantidade = 0
        for decl in declaracoes_var.declaracoes:
            quantidade += len(decl.identificadores)
        return quantidade
    
    def _declarar_variaveis(self, declaracoes_var: DeclaracoesVariaveis):
        """Declara variáveis na tabela de símbolos."""
        for decl in declaracoes_var.declaracoes:
            for identificador in decl.identificadores:
                self.tabela_simbolos.declarar(identificador, decl.tipo, 'variavel')
    
    def _gerar_funcao(self, no: Funcao, endereco_pai: int):
        """
        Gera código para uma função.
        
        Estrutura:
        Lx NULL
        ALLOC m,n          ; variáveis locais
        JMP Lcorpo         ; pula subrotinas aninhadas (só se houver)
        [subrotinas aninhadas]
        Lcorpo NULL        ; (só se houver subrotinas aninhadas)
        [comandos]
        DALLOC m,n
        RETURN
        """
        rotulo = self.obter_rotulo_subrotina(no.nome)
        self.emitir(f"{rotulo} \tNULL")
        
        # Entra no escopo da função
        self.tabela_simbolos.entrar_escopo(endereco_pai)
        
        # Conta e declara variáveis locais (funções aninhadas + variáveis declaradas)
        qtd_retorno_funcoes = len(no.bloco.funcoes)
        qtd_variaveis_locais = self._contar_declaracoes_variaveis(no.bloco.declaracoes_variaveis)
        total_locais = qtd_retorno_funcoes + qtd_variaveis_locais
        
        # Declara funções aninhadas (retorno)
        for func in no.bloco.funcoes:
            self.tabela_simbolos.declarar_retorno_funcao(func.nome, func.tipo_retorno)
        
        # Declara variáveis locais
        if no.bloco.declaracoes_variaveis:
            self._declarar_variaveis(no.bloco.declaracoes_variaveis)
        
        # Declara procedimentos aninhados
        for proc in no.bloco.procedimentos:
            self.tabela_simbolos.declarar_procedimento(proc.nome)
        
        # ALLOC para variáveis locais
        base_local = endereco_pai
        if total_locais > 0:
            self.emitir(f"ALLOC {base_local} {total_locais}")
        
        # Verifica se há subrotinas aninhadas
        tem_aninhadas = len(no.bloco.procedimentos) > 0 or len(no.bloco.funcoes) > 0
        
        # JMP para o corpo (pula subrotinas aninhadas) - só se houver
        rotulo_corpo = None
        if tem_aninhadas:
            rotulo_corpo = self.novo_rotulo()
            self.emitir(f"JMP {rotulo_corpo}")
        
        # Subrotinas aninhadas
        proximo_endereco = base_local + total_locais
        for func in no.bloco.funcoes:
            self._gerar_funcao(func, proximo_endereco)
        for proc in no.bloco.procedimentos:
            self._gerar_procedimento(proc, proximo_endereco)
        
        # Rótulo do corpo da função (só se houver subrotinas aninhadas)
        if tem_aninhadas:
            self.emitir(f"{rotulo_corpo} \tNULL")
        
        funcao_anterior = self.funcao_atual
        self.funcao_atual = no.nome
        
        self.gera_comando_composto(no.bloco.comando_composto)
        
        self.funcao_atual = funcao_anterior
        
        # DALLOC e RETURN
        if total_locais > 0:
            self.emitir(f"DALLOC {base_local} {total_locais}")
        self.emitir("RETURN")
        
        # Sai do escopo
        self.tabela_simbolos.sair_escopo()
    
    def _gerar_procedimento(self, no: Procedimento, endereco_pai: int):
        """
        Gera código para um procedimento.
        
        Estrutura similar à função, mas sem valor de retorno.
        """
        rotulo = self.obter_rotulo_subrotina(no.nome)
        self.emitir(f"{rotulo} \tNULL")
        
        # Entra no escopo do procedimento
        self.tabela_simbolos.entrar_escopo(endereco_pai)
        
        # Conta e declara variáveis locais
        qtd_retorno_funcoes = len(no.bloco.funcoes)
        qtd_variaveis_locais = self._contar_declaracoes_variaveis(no.bloco.declaracoes_variaveis)
        total_locais = qtd_retorno_funcoes + qtd_variaveis_locais
        
        # Declara funções aninhadas (retorno)
        for func in no.bloco.funcoes:
            self.tabela_simbolos.declarar_retorno_funcao(func.nome, func.tipo_retorno)
        
        # Declara variáveis locais
        if no.bloco.declaracoes_variaveis:
            self._declarar_variaveis(no.bloco.declaracoes_variaveis)
        
        # Declara procedimentos aninhados
        for proc in no.bloco.procedimentos:
            self.tabela_simbolos.declarar_procedimento(proc.nome)
        
        # ALLOC para variáveis locais
        base_local = endereco_pai
        if total_locais > 0:
            self.emitir(f"ALLOC {base_local} {total_locais}")
        
        # Verifica se há subrotinas aninhadas
        tem_aninhadas = len(no.bloco.procedimentos) > 0 or len(no.bloco.funcoes) > 0
        
        # JMP para o corpo (só se houver subrotinas aninhadas)
        rotulo_corpo = None
        if tem_aninhadas:
            rotulo_corpo = self.novo_rotulo()
            self.emitir(f"JMP {rotulo_corpo}")
        
        # Subrotinas aninhadas
        proximo_endereco = base_local + total_locais
        for func in no.bloco.funcoes:
            self._gerar_funcao(func, proximo_endereco)
        for proc in no.bloco.procedimentos:
            self._gerar_procedimento(proc, proximo_endereco)
        
        # Rótulo do corpo do procedimento (só se houver subrotinas aninhadas)
        if tem_aninhadas:
            self.emitir(f"{rotulo_corpo} \tNULL")
        
        self.gera_comando_composto(no.bloco.comando_composto)
        
        # DALLOC e RETURN
        if total_locais > 0:
            self.emitir(f"DALLOC {base_local} {total_locais}")
        self.emitir("RETURN")
        
        # Sai do escopo
        self.tabela_simbolos.sair_escopo()
    
    # ========== Comandos ==========
    
    def gera_comando_composto(self, no: ComandoComposto):
        for comando in no.comandos:
            self.gera_comando(comando)
    
    def gera_comando(self, no: Comando):
        if isinstance(no, Atribuicao):
            self.gera_atribuicao(no)
        elif isinstance(no, ComandoLeitura):
            self.gera_comando_leitura(no)
        elif isinstance(no, ComandoEscrita):
            self.gera_comando_escrita(no)
        elif isinstance(no, ComandoSe):
            self.gera_comando_se(no)
        elif isinstance(no, ComandoEnquanto):
            self.gera_comando_enquanto(no)
        elif isinstance(no, ComandoComposto):
            self.gera_comando_composto(no)
        elif isinstance(no, ChamadaProcedimento):
            self.gera_chamada_procedimento(no)
        elif isinstance(no, ComandoVazio):
            pass
    
    def gera_atribuicao(self, no: Atribuicao):
        """
        Atribuição:
        - Variável: avalia expressão + STR addr
        - Função (retorno): avalia expressão + STR addr_retorno
          (o RETURN será gerado no final da função)
        """
        simbolo = self.tabela_simbolos.buscar(no.identificador)
        if simbolo is None:
            raise Exception(f"Identificador '{no.identificador}' não declarado (gerador)")
        
        # Avalia a expressão
        self.gera_expressao(no.expressao)
        
        # Armazena no endereço (funciona para variável e retorno de função)
        endereco = simbolo.endereco_memoria
        self.emitir(f"STR {endereco}")
    
    def gera_comando_leitura(self, no: ComandoLeitura):
        """
        Gera código para leitura: leia(id)
        """
        self.emitir("RD")
        
        simbolo = self.tabela_simbolos.buscar(no.identificador)
        if simbolo is None:
            raise Exception(f"Identificador '{no.identificador}' não declarado (gerador)")
        
        self.emitir(f"STR {simbolo.endereco_memoria}")
    
    def gera_comando_escrita(self, no: ComandoEscrita):
        self.gera_expressao(no.expressao)
        self.emitir("PRN")
    
    def gera_comando_se(self, no: ComandoSe):
        """
        se E entao C1 [senao C2]
        """
        if no.comando_senao:
            rotulo_senao = self.novo_rotulo()
            rotulo_fim = self.novo_rotulo()
            
            self.gera_expressao(no.condicao)
            self.emitir(f"JMPF {rotulo_senao}")
            self.gera_comando(no.comando_entao)
            self.emitir(f"JMP {rotulo_fim}")
            self.emitir(f"{rotulo_senao} \tNULL")
            self.gera_comando(no.comando_senao)
            self.emitir(f"{rotulo_fim} \tNULL")
        else:
            rotulo_fim = self.novo_rotulo()
            
            self.gera_expressao(no.condicao)
            self.emitir(f"JMPF {rotulo_fim}")
            self.gera_comando(no.comando_entao)
            self.emitir(f"{rotulo_fim} \tNULL")
    
    def gera_comando_enquanto(self, no: ComandoEnquanto):
        """
        enquanto E faca C
        """
        rotulo_inicio = self.novo_rotulo()
        rotulo_fim = self.novo_rotulo()
        
        self.emitir(f"{rotulo_inicio} \tNULL")
        self.gera_expressao(no.condicao)
        self.emitir(f"JMPF {rotulo_fim}")
        self.gera_comando(no.corpo)
        self.emitir(f"JMP {rotulo_inicio}")
        self.emitir(f"{rotulo_fim} \tNULL")
    
    def gera_chamada_procedimento(self, no: ChamadaProcedimento):
        rotulo = self.obter_rotulo_subrotina(no.nome)
        self.emitir(f"CALL {rotulo}")
    
    # ========== Expressões ==========
    
    def gera_expressao(self, no: Expressao):
        if isinstance(no, OperacaoBinaria):
            self.gera_operacao_binaria(no)
        elif isinstance(no, OperacaoUnaria):
            self.gera_operacao_unaria(no)
        elif isinstance(no, Identificador):
            self.gera_identificador(no)
        elif isinstance(no, Numero):
            self.emitir(f"LDC {no.valor}")
        elif isinstance(no, Booleano):
            valor = 1 if no.valor else 0
            self.emitir(f"LDC {valor}")
    
    def gera_operacao_binaria(self, no: OperacaoBinaria):
        self.gera_expressao(no.esquerda)
        self.gera_expressao(no.direita)
        
        mapa_operadores = {
            '+': 'ADD',
            '-': 'SUB',
            '*': 'MULT',
            'div': 'DIVI',
            'e': 'AND',
            'ou': 'OR',
            '=': 'CEQ',
            '!=': 'CDIF',
            '<': 'CME',
            '<=': 'CMEQ',
            '>': 'CMA',
            '>=': 'CMAQ'
        }
        instrucao = mapa_operadores.get(no.operador)
        if not instrucao:
            raise Exception(f"Operador desconhecido: {no.operador}")
        self.emitir(instrucao)
    
    def gera_operacao_unaria(self, no: OperacaoUnaria):
        self.gera_expressao(no.operando)
        if no.operador == 'nao':
            self.emitir("NEG")
        elif no.operador == '-':
            self.emitir("INV")
        else:
            raise Exception(f"Operador unário desconhecido: {no.operador}")
    
    def gera_identificador(self, no: Identificador):
        """
        Identificador em expressão:
        - Variável: LDV addr
        - Função: CALL Lfunc, depois LDV addr_retorno
        """
        simbolo = self.tabela_simbolos.buscar(no.nome)
        if simbolo is None:
            raise Exception(f"Identificador '{no.nome}' não declarado (gerador)")
        
        if simbolo.categoria == 'variavel':
            self.emitir(f"LDV {simbolo.endereco_memoria}")
        
        elif simbolo.categoria == 'funcao':
            # Chamada de função em expressão
            # 1. CALL para executar a função (que armazena resultado em addr_retorno)
            # 2. LDV para carregar o valor de retorno
            rotulo = self.obter_rotulo_subrotina(no.nome)
            self.emitir(f"CALL {rotulo}")
            self.emitir(f"LDV {simbolo.endereco_memoria}")
        
        else:
            raise Exception(f"'{no.nome}' não pode ser usado como expressão")
    
    def obter_codigo(self) -> str:
        """Retorna o código gerado como string."""
        return "\n".join(self.instrucoes)
    
    def salvar_em_arquivo(self, nome_arquivo: str):
        """Salva o código em um arquivo."""
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            f.write(self.obter_codigo())
