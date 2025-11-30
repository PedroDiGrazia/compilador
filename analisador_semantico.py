"""
Analisador Semântico do Compilador LPD
Realiza análise semântica da AST: verificação de tipos, declarações e compatibilidade.
Utiliza escopos.
"""

from arvore_sintatica import (
    Programa, Bloco, DeclaracoesVariaveis, DeclaracaoVariavel,
    Procedimento, Funcao, ComandoComposto, Comando, Atribuicao,
    ChamadaProcedimento, ComandoLeitura, ComandoEscrita, ComandoSe,
    ComandoEnquanto, ComandoVazio, Expressao, OperacaoBinaria,
    OperacaoUnaria, Identificador, Numero, Booleano
)
from tabela_simbolos import TabelaSimbolos, Simbolo
from tokens import ErroSemantico


class AnalisadorSemantico:
    """
    Analisador semântico que percorre a AST.
    Implementa escopos hierárquicos.
    """
    
    def __init__(self):
        self.tabela_simbolos = TabelaSimbolos()
        self.erros = []
        self.funcao_atual = None  # Nome da função atual (para verificar atribuição de retorno)
    
    def analisar(self, programa: Programa) -> TabelaSimbolos:
        """
        Analisa semanticamente o programa e retorna a tabela de símbolos.
        Se houver erros, levanta ErroSemantico com todos eles.
        """
        try:
            self.analisa_programa(programa)
        except ErroSemantico as e:
            msg = str(e)
            prefixo = "Erro semântico: "
            if msg.startswith(prefixo):
                msg = msg[len(prefixo):]
            self.erros.append(msg)
        
        if self.erros:
            raise ErroSemantico("\n".join(self.erros))
        
        return self.tabela_simbolos
    
    # ==================== PROGRAMA ====================
    
    def analisa_programa(self, no: Programa):
        """
        Programa LPD:
          1. Reserva posições para retorno de funções do nível global
          2. Declara variáveis globais
          3. Processa funções e procedimentos (com seus escopos)
          4. Analisa o comando composto principal
        """
        # Reserva posições de retorno para todas as funções do nível global
        for func in no.funcoes:
            try:
                self.tabela_simbolos.declarar_retorno_funcao(func.nome, func.tipo_retorno)
            except Exception as e:
                raise ErroSemantico(str(e))
        
        # Declara variáveis globais
        if no.declaracoes_variaveis:
            self.analisa_declaracoes_variaveis(no.declaracoes_variaveis)
        
        # Declara procedimentos do nível global (sem alocação de memória)
        for proc in no.procedimentos:
            try:
                self.tabela_simbolos.declarar_procedimento(proc.nome)
            except Exception as e:
                raise ErroSemantico(str(e))
        
        # Processa blocos de funções e procedimentos (com escopos aninhados)
        for func in no.funcoes:
            self.analisa_funcao(func)
        
        for proc in no.procedimentos:
            self.analisa_procedimento(proc)
        
        # Analisa o corpo principal
        self.analisa_comando_composto(no.comando_composto)
    
    # ==================== FUNÇÕES E PROCEDIMENTOS ====================
    
    def analisa_funcao(self, no: Funcao):
        """
        Processa uma função:
        - Entra em novo escopo
        - Declara variáveis locais
        - Processa subrotinas aninhadas
        - Analisa comandos
        - Sai do escopo
        """
        # Calcula endereço base para este escopo
        endereco_base = self.tabela_simbolos.obter_proximo_endereco()
        
        # Entra no escopo da função
        self.tabela_simbolos.entrar_escopo(endereco_base)
        
        funcao_anterior = self.funcao_atual
        self.funcao_atual = no.nome
        
        # Processa o bloco da função
        self._processar_bloco(no.bloco)
        
        self.funcao_atual = funcao_anterior
        
        # Sai do escopo
        self.tabela_simbolos.sair_escopo()
    
    def analisa_procedimento(self, no: Procedimento):
        """
        Processa um procedimento:
        - Entra em novo escopo
        - Declara variáveis locais
        - Processa subrotinas aninhadas
        - Analisa comandos
        - Sai do escopo
        """
        # Calcula endereço base para este escopo
        endereco_base = self.tabela_simbolos.obter_proximo_endereco()
        
        # Entra no escopo do procedimento
        self.tabela_simbolos.entrar_escopo(endereco_base)
        
        # Processa o bloco do procedimento
        self._processar_bloco(no.bloco)
        
        # Sai do escopo
        self.tabela_simbolos.sair_escopo()
    
    def _processar_bloco(self, bloco: Bloco):
        """
        Processa um bloco (comum a funções e procedimentos):
        - Reserva posições de retorno para funções aninhadas
        - Declara variáveis locais
        - Declara procedimentos aninhados
        - Processa subrotinas aninhadas recursivamente
        - Analisa comandos
        """
        # 1) Reserva posições de retorno para funções aninhadas
        for func in bloco.funcoes:
            try:
                self.tabela_simbolos.declarar_retorno_funcao(func.nome, func.tipo_retorno)
            except Exception as e:
                raise ErroSemantico(str(e))
        
        # 2) Declara variáveis locais
        if bloco.declaracoes_variaveis:
            self.analisa_declaracoes_variaveis(bloco.declaracoes_variaveis)
        
        # 3) Declara procedimentos aninhados
        for proc in bloco.procedimentos:
            try:
                self.tabela_simbolos.declarar_procedimento(proc.nome)
            except Exception as e:
                raise ErroSemantico(str(e))
        
        # 4) Processa subrotinas aninhadas (recursivamente)
        for func in bloco.funcoes:
            self.analisa_funcao(func)
        
        for proc in bloco.procedimentos:
            self.analisa_procedimento(proc)
        
        # 5) Analisa os comandos do bloco
        self.analisa_comando_composto(bloco.comando_composto)
    
    # ==================== DECLARAÇÕES DE VARIÁVEIS ====================
    
    def analisa_declaracoes_variaveis(self, no: DeclaracoesVariaveis):
        """Declarações de variáveis."""
        for decl in no.declaracoes:
            self.analisa_declaracao_variavel(decl)
    
    def analisa_declaracao_variavel(self, no: DeclaracaoVariavel):
        """
        Declara variáveis no escopo atual.
        """
        for identificador in no.identificadores:
            try:
                self.tabela_simbolos.declarar(identificador, no.tipo, 'variavel')
            except Exception as e:
                raise ErroSemantico(str(e))
    
    # ==================== COMANDOS ====================
    
    def analisa_comando_composto(self, no: ComandoComposto):
        for comando in no.comandos:
            self.analisa_comando(comando)
    
    def analisa_comando(self, no: Comando):
        if isinstance(no, Atribuicao):
            self.analisa_atribuicao(no)
        elif isinstance(no, ComandoLeitura):
            self.analisa_comando_leitura(no)
        elif isinstance(no, ComandoEscrita):
            self.analisa_comando_escrita(no)
        elif isinstance(no, ComandoSe):
            self.analisa_comando_se(no)
        elif isinstance(no, ComandoEnquanto):
            self.analisa_comando_enquanto(no)
        elif isinstance(no, ComandoComposto):
            self.analisa_comando_composto(no)
        elif isinstance(no, ChamadaProcedimento):
            self.analisa_chamada_procedimento(no)
        elif isinstance(no, ComandoVazio):
            pass
    
    def analisa_atribuicao(self, no: Atribuicao):
        """
        Atribuição:
          - se id for variável  -> checa tipo
          - se id for função    -> trata como comando de retorno (soma := expr;)
        """
        simbolo = self.tabela_simbolos.buscar(no.identificador)
        if simbolo is None:
            raise ErroSemantico(f"Identificador '{no.identificador}' não foi declarado")
        
        tipo_expressao = self.analisa_expressao(no.expressao)

        if simbolo.categoria == 'variavel':
            if simbolo.tipo != tipo_expressao:
                raise ErroSemantico(
                    f"Tipo incompatível na atribuição: '{no.identificador}' é {simbolo.tipo}, "
                    f"mas a expressão é {tipo_expressao}"
                )

        elif simbolo.categoria == 'funcao':
            # Comando de retorno da função
            if simbolo.tipo != tipo_expressao:
                raise ErroSemantico(
                    f"Tipo de retorno incompatível na função '{no.identificador}': "
                    f"esperado {simbolo.tipo}, obtido {tipo_expressao}"
                )

        else:
            raise ErroSemantico(
                f"'{no.identificador}' não pode receber atribuição (não é variável nem função)"
            )
    
    def analisa_chamada_procedimento(self, no: ChamadaProcedimento):
        """Verifica chamada de procedimento."""
        simbolo = self.tabela_simbolos.buscar(no.nome)
        if simbolo is None:
            raise ErroSemantico(f"Procedimento '{no.nome}' não foi declarado")
        if simbolo.categoria != 'procedimento':
            raise ErroSemantico(f"'{no.nome}' não é um procedimento")
    
    def analisa_comando_leitura(self, no: ComandoLeitura):
        simbolo = self.tabela_simbolos.buscar(no.identificador)
        if simbolo is None:
            raise ErroSemantico(f"Variável '{no.identificador}' não foi declarada")
        if simbolo.categoria != 'variavel':
            raise ErroSemantico(f"'{no.identificador}' não é uma variável")
    
    def analisa_comando_escrita(self, no: ComandoEscrita):
        self.analisa_expressao(no.expressao)
    
    def analisa_comando_se(self, no: ComandoSe):
        tipo_condicao = self.analisa_expressao(no.condicao)
        if tipo_condicao != 'booleano':
            raise ErroSemantico(
                f"Condição do 'se' deve ser booleana, mas é {tipo_condicao}"
            )
        self.analisa_comando(no.comando_entao)
        if no.comando_senao:
            self.analisa_comando(no.comando_senao)
    
    def analisa_comando_enquanto(self, no: ComandoEnquanto):
        tipo_condicao = self.analisa_expressao(no.condicao)
        if tipo_condicao != 'booleano':
            raise ErroSemantico(
                f"Condição do 'enquanto' deve ser booleana, mas é {tipo_condicao}"
            )
        self.analisa_comando(no.corpo)
    
    # ==================== EXPRESSÕES ====================
    
    def analisa_expressao(self, no: Expressao) -> str:
        """
        Retorna o tipo da expressão: 'inteiro' ou 'booleano'.
        """
        if isinstance(no, OperacaoBinaria):
            return self.analisa_operacao_binaria(no)
        elif isinstance(no, OperacaoUnaria):
            return self.analisa_operacao_unaria(no)
        elif isinstance(no, Identificador):
            return self.analisa_identificador(no)
        elif isinstance(no, Numero):
            no.tipo_expressao = 'inteiro'
            return 'inteiro'
        elif isinstance(no, Booleano):
            no.tipo_expressao = 'booleano'
            return 'booleano'
        else:
            raise ErroSemantico(f"Tipo de expressão desconhecido: {type(no)}")
    
    def analisa_operacao_binaria(self, no: OperacaoBinaria) -> str:
        tipo_esquerda = self.analisa_expressao(no.esquerda)
        tipo_direita = self.analisa_expressao(no.direita)
        operador = no.operador
        
        # Operadores aritméticos
        if operador in ['+', '-', '*', 'div']:
            if tipo_esquerda != 'inteiro' or tipo_direita != 'inteiro':
                raise ErroSemantico(
                    f"Operador '{operador}' requer operandos inteiros, "
                    f"mas recebeu {tipo_esquerda} e {tipo_direita}"
                )
            no.tipo_expressao = 'inteiro'
            return 'inteiro'
        
        # Operadores lógicos
        elif operador in ['e', 'ou']:
            if tipo_esquerda != 'booleano' or tipo_direita != 'booleano':
                raise ErroSemantico(
                    f"Operador '{operador}' requer operandos booleanos, "
                    f"mas recebeu {tipo_esquerda} e {tipo_direita}"
                )
            no.tipo_expressao = 'booleano'
            return 'booleano'
        
        # Operadores relacionais
        elif operador in ['=', '!=', '<', '<=', '>', '>=']:
            if tipo_esquerda != tipo_direita:
                raise ErroSemantico(
                    f"Operador '{operador}' requer operandos do mesmo tipo, "
                    f"mas recebeu {tipo_esquerda} e {tipo_direita}"
                )
            if operador in ['<', '<=', '>', '>='] and tipo_esquerda != 'inteiro':
                raise ErroSemantico(
                    f"Operador '{operador}' requer operandos inteiros, "
                    f"mas recebeu {tipo_esquerda}"
                )
            no.tipo_expressao = 'booleano'
            return 'booleano'
        
        else:
            raise ErroSemantico(f"Operador desconhecido: {operador}")
    
    def analisa_operacao_unaria(self, no: OperacaoUnaria) -> str:
        tipo_operando = self.analisa_expressao(no.operando)
        
        if no.operador == 'nao':
            if tipo_operando != 'booleano':
                raise ErroSemantico(
                    f"Operador 'nao' requer operando booleano, mas recebeu {tipo_operando}"
                )
            no.tipo_expressao = 'booleano'
            return 'booleano'
        
        elif no.operador == '-':
            if tipo_operando != 'inteiro':
                raise ErroSemantico(
                    f"Operador '-' unário requer operando inteiro, mas recebeu {tipo_operando}"
                )
            no.tipo_expressao = 'inteiro'
            return 'inteiro'
        
        else:
            raise ErroSemantico(f"Operador unário desconhecido: {no.operador}")
    
    def analisa_identificador(self, no: Identificador) -> str:
        """
        Identificador pode ser:
          - variável (categoria='variavel')
          - função  (categoria='funcao') em expressão
        Procedimento não pode aparecer em expressão.
        """
        simbolo = self.tabela_simbolos.buscar(no.nome)
        if simbolo is None:
            raise ErroSemantico(f"Identificador '{no.nome}' não foi declarado")
        
        if simbolo.categoria == 'procedimento':
            raise ErroSemantico(f"Procedimento '{no.nome}' não pode ser usado em expressões")
        
        no.tipo_expressao = simbolo.tipo
        return simbolo.tipo
