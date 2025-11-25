"""
Analisador Sintático do Compilador LPD
Implementa análise descendente recursiva para a gramática da linguagem.
"""

from typing import List, Optional
from tokens import Token, TipoToken, ErroSintatico
from arvore_sintatica import (
    Programa, Bloco, DeclaracoesVariaveis, DeclaracaoVariavel,
    Procedimento, Funcao, Parametro, ComandoComposto, Comando,
    Atribuicao, ChamadaProcedimento, ComandoLeitura, ComandoEscrita,
    ComandoSe, ComandoEnquanto, Expressao, OperacaoBinaria,
    OperacaoUnaria, Identificador, Numero, Booleano
)


class AnalisadorSintatico:
    """Analisador sintático descendente recursivo para LPD."""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.posicao = 0
        self.atual = tokens[0] if tokens else None
    
    def avancar(self):
        """Avança para o próximo token."""
        if self.posicao < len(self.tokens) - 1:
            self.posicao += 1
            self.atual = self.tokens[self.posicao]
    
    def espiar(self, deslocamento: int = 1) -> Optional[Token]:
        """Olha adiante sem consumir tokens."""
        indice = self.posicao + deslocamento
        if indice < len(self.tokens):
            return self.tokens[indice]
        return None
    
    def esperar(self, tipo_token: TipoToken, mensagem: str = None) -> Token:
        """Consome um token do tipo esperado ou lança erro."""
        if self.atual.tipo != tipo_token:
            if mensagem is None:
                mensagem = f"Esperado {tipo_token.name}, encontrado {self.atual.tipo.name}"
            raise ErroSintatico(mensagem, self.atual.linha, self.atual.coluna)
        token = self.atual
        self.avancar()
        return token
    
    def corresponde(self, *tipos_token: TipoToken) -> bool:
        """Verifica se o token atual é de um dos tipos dados."""
        return self.atual.tipo in tipos_token
    
    def analisar(self) -> Programa:
        """Ponto de entrada do analisador sintático."""
        return self.programa()
    
    # ==================== PROGRAMA ====================
    
    def programa(self) -> Programa:
        """
        programa ::= "programa" ID ";" bloco "."
        """
        self.esperar(TipoToken.PROGRAMA, "Esperado 'programa'")
        token_nome = self.esperar(TipoToken.IDENTIFICADOR, "Esperado identificador após 'programa'")
        nome = token_nome.valor
        self.esperar(TipoToken.PONTO_VIRGULA, "Esperado ';' após nome do programa")
        
        bloco = self.bloco()
        
        self.esperar(TipoToken.PONTO, "Esperado '.' no final do programa")
        
        return Programa(
            nome=nome,
            declaracoes_variaveis=bloco.declaracoes_variaveis,
            procedimentos=bloco.procedimentos,
            funcoes=bloco.funcoes,
            comando_composto=bloco.comando_composto
        )
    
    def bloco(self) -> Bloco:
        """
        bloco ::= [declaracao_variaveis] [declaracao_subrotinas] comando_composto
        declaracao_subrotinas ::= { declaracao_procedimento | declaracao_funcao }
        """
        declaracoes_var = None
        if self.corresponde(TipoToken.VAR):
            declaracoes_var = self.declaracao_variaveis()
        
        procedimentos: List[Procedimento] = []
        funcoes: List[Funcao] = []
        
        # Zero ou mais declarações de procedimentos/funções
        while self.corresponde(TipoToken.PROCEDIMENTO, TipoToken.FUNCAO):
            if self.corresponde(TipoToken.PROCEDIMENTO):
                procedimentos.append(self.declaracao_procedimento())
            else:
                funcoes.append(self.declaracao_funcao())
        
        # Depois disso obrigatoriamente vem um comando_composto (inicio ... fim)
        comando_comp = self.comando_composto()
        
        return Bloco(
            declaracoes_variaveis=declaracoes_var,
            procedimentos=procedimentos,
            funcoes=funcoes,
            comando_composto=comando_comp
        )

    # ==================== DECLARAÇÕES ====================
    
    def declaracao_variaveis(self) -> DeclaracoesVariaveis:
        """
        declaracao_variaveis ::= "var" declaracao {";" declaracao} ";"
        """
        self.esperar(TipoToken.VAR)
        declaracoes = []
        
        declaracoes.append(self.declaracao())
        self.esperar(TipoToken.PONTO_VIRGULA, "Esperado ';' após declaração de variável")
        
        # Continua lendo declarações enquanto encontrar IDENTIFICADOR
        while self.corresponde(TipoToken.IDENTIFICADOR):
            declaracoes.append(self.declaracao())
            self.esperar(TipoToken.PONTO_VIRGULA, "Esperado ';' após declaração de variável")
        
        return DeclaracoesVariaveis(declaracoes=declaracoes)
    
    def declaracao(self) -> DeclaracaoVariavel:
        """
        declaracao ::= lista_ids ":" tipo
        lista_ids ::= ID {"," ID}
        """
        identificadores = []
        
        token_id = self.esperar(TipoToken.IDENTIFICADOR, "Esperado identificador")
        identificadores.append(token_id.valor)
        
        while self.corresponde(TipoToken.VIRGULA):
            self.avancar()  # consome ','
            token_id = self.esperar(TipoToken.IDENTIFICADOR, "Esperado identificador após ','")
            identificadores.append(token_id.valor)
        
        self.esperar(TipoToken.DOIS_PONTOS, "Esperado ':' após lista de identificadores")
        
        tipo_var = self.tipo()
        
        return DeclaracaoVariavel(identificadores=identificadores, tipo=tipo_var)
    
    def tipo(self) -> str:
        """
        tipo ::= "inteiro" | "booleano"
        """
        if self.corresponde(TipoToken.INTEIRO):
            self.avancar()
            return "inteiro"
        elif self.corresponde(TipoToken.BOOLEANO):
            self.avancar()
            return "booleano"
        else:
            raise ErroSintatico("Esperado tipo 'inteiro' ou 'booleano'", 
                               self.atual.linha, self.atual.coluna)

    # ==================== DECLARAÇÕES DE SUBROTINAS ====================

    def declaracao_procedimento(self) -> Procedimento:
        """
        declaracao_procedimento ::=
            "procedimento" ID [ "(" lista_parametros ")" ] ";" bloco ";"
        """
        self.esperar(TipoToken.PROCEDIMENTO, "Esperado 'procedimento'")
        token_nome = self.esperar(TipoToken.IDENTIFICADOR, "Esperado identificador do procedimento")
        nome = token_nome.valor

        parametros: List[Parametro] = []

        # Parâmetros opcionais: procedimento P(a: inteiro; b: booleano);
        if self.corresponde(TipoToken.ABRE_PARENTESES):
            parametros = self.lista_parametros()

        self.esperar(TipoToken.PONTO_VIRGULA, "Esperado ';' após cabeçalho do procedimento")

        bloco = self.bloco()

        # Após 'fim' do bloco do procedimento, espera ';'
        self.esperar(TipoToken.PONTO_VIRGULA, "Esperado ';' após 'fim' do procedimento")

        return Procedimento(nome=nome, parametros=parametros, bloco=bloco)

    def declaracao_funcao(self) -> Funcao:
        """
        declaracao_funcao ::=
            "funcao" ID [ "(" lista_parametros ")" ] ":" tipo ";" bloco ";"
        """
        self.esperar(TipoToken.FUNCAO, "Esperado 'funcao'")
        token_nome = self.esperar(TipoToken.IDENTIFICADOR, "Esperado identificador da função")
        nome = token_nome.valor

        parametros: List[Parametro] = []

        # Parâmetros opcionais: funcao soma(a: inteiro; b: inteiro): inteiro;
        if self.corresponde(TipoToken.ABRE_PARENTESES):
            parametros = self.lista_parametros()

        self.esperar(TipoToken.DOIS_PONTOS, "Esperado ':' após nome/parâmetros da função")

        tipo_retorno = self.tipo()  # 'inteiro' ou 'booleano'

        self.esperar(TipoToken.PONTO_VIRGULA, "Esperado ';' após cabeçalho da função")

        bloco = self.bloco()

        self.esperar(TipoToken.PONTO_VIRGULA, "Esperado ';' após 'fim' da função")

        return Funcao(
            nome=nome,
            parametros=parametros,
            tipo_retorno=tipo_retorno,
            bloco=bloco
        )

    def lista_parametros(self) -> List[Parametro]:
        """
        lista_parametros ::= "(" parametro { ";" parametro } ")"
        """
        parametros: List[Parametro] = []

        self.esperar(TipoToken.ABRE_PARENTESES, "Esperado '(' na lista de parâmetros")

        parametros.append(self.parametro())

        while self.corresponde(TipoToken.PONTO_VIRGULA):
            self.avancar()
            parametros.append(self.parametro())

        self.esperar(TipoToken.FECHA_PARENTESES, "Esperado ')' ao final da lista de parâmetros")

        return parametros

    def parametro(self) -> Parametro:
        """
        parametro ::= lista_ids ":" tipo
        """
        identificadores: List[str] = []

        token_id = self.esperar(TipoToken.IDENTIFICADOR, "Esperado identificador de parâmetro")
        identificadores.append(token_id.valor)

        while self.corresponde(TipoToken.VIRGULA):
            self.avancar()
            token_id = self.esperar(TipoToken.IDENTIFICADOR, "Esperado identificador após ','")
            identificadores.append(token_id.valor)

        self.esperar(TipoToken.DOIS_PONTOS, "Esperado ':' após lista de parâmetros")

        tipo_param = self.tipo()

        return Parametro(identificadores=identificadores, tipo=tipo_param)
    
    # ==================== COMANDOS ====================
    
    def comando_composto(self) -> ComandoComposto:
        """
        comando_composto ::= "inicio" comandos "fim"
        comandos ::= comando {";" comando}
        """
        self.esperar(TipoToken.INICIO, "Esperado 'inicio'")
        
        comandos = []
        
        # Primeiro comando (pode ser vazio se próximo token for 'fim')
        if not self.corresponde(TipoToken.FIM):
            comandos.append(self.comando())
            
            # Comandos adicionais separados por ';'
            while self.corresponde(TipoToken.PONTO_VIRGULA):
                self.avancar()  # consome ';'
                # Verifica se não chegou no 'fim'
                if not self.corresponde(TipoToken.FIM):
                    comandos.append(self.comando())
        
        self.esperar(TipoToken.FIM, "Esperado 'fim'")
        
        return ComandoComposto(comandos=comandos)
    
    def comando(self) -> Comando:
        """
        comando ::= atribuicao | chamada_procedimento | leitura | escrita
                    | condicional | repeticao | comando_composto
        """
        # Pode ser atribuição ou chamada de procedimento
        if self.corresponde(TipoToken.IDENTIFICADOR):
            # Olha o próximo token para decidir
            proximo = self.espiar()
            if proximo and proximo.tipo == TipoToken.ATRIBUICAO:
                return self.atribuicao()
            else:
                return self.chamada_procedimento()

        # Leitura: leia(...)
        elif self.corresponde(TipoToken.LEIA):
            return self.leitura()
        
        # Escrita: escreva(...)
        elif self.corresponde(TipoToken.ESCREVA):
            return self.escrita()
        
        # Condicional: se ... entao ...
        elif self.corresponde(TipoToken.SE):
            return self.condicional()
        
        # Repetição: enquanto ... faca ...
        elif self.corresponde(TipoToken.ENQUANTO):
            return self.repeticao()
        
        # Comando composto: inicio ... fim
        elif self.corresponde(TipoToken.INICIO):
            return self.comando_composto()
        
        else:
            raise ErroSintatico("Comando inválido", self.atual.linha, self.atual.coluna)
    
    def atribuicao(self) -> Atribuicao:
        """
        atribuicao ::= ID ":=" expressao
        """
        token_id = self.esperar(TipoToken.IDENTIFICADOR)
        identificador = token_id.valor
        
        self.esperar(TipoToken.ATRIBUICAO, "Esperado ':=' para atribuição")
        
        expressao = self.expressao()
        
        return Atribuicao(identificador=identificador, expressao=expressao)
    
    def leitura(self) -> ComandoLeitura:
        """
        leitura ::= "leia" "(" ID ")"
        """
        self.esperar(TipoToken.LEIA)
        self.esperar(TipoToken.ABRE_PARENTESES, "Esperado '(' após 'leia'")
        token_id = self.esperar(TipoToken.IDENTIFICADOR, "Esperado identificador em 'leia'")
        self.esperar(TipoToken.FECHA_PARENTESES, "Esperado ')' após identificador")
        
        return ComandoLeitura(identificador=token_id.valor)
    
    def escrita(self) -> ComandoEscrita:
        """
        escrita ::= "escreva" "(" expressao ")"
        """
        self.esperar(TipoToken.ESCREVA)
        self.esperar(TipoToken.ABRE_PARENTESES, "Esperado '(' após 'escreva'")
        expressao = self.expressao()
        self.esperar(TipoToken.FECHA_PARENTESES, "Esperado ')' após expressão")
        
        return ComandoEscrita(expressao=expressao)
    
    def condicional(self) -> ComandoSe:
        """
        condicional ::= "se" expressao "entao" comando ["senao" comando]
        """
        self.esperar(TipoToken.SE)
        condicao = self.expressao()
        self.esperar(TipoToken.ENTAO, "Esperado 'entao' após condição")
        comando_entao = self.comando()
        
        comando_senao = None
        if self.corresponde(TipoToken.SENAO):
            self.avancar()
            comando_senao = self.comando()
        
        return ComandoSe(
            condicao=condicao,
            comando_entao=comando_entao,
            comando_senao=comando_senao
        )
    
    def repeticao(self) -> ComandoEnquanto:
        """
        repeticao ::= "enquanto" expressao "faca" comando
        """
        self.esperar(TipoToken.ENQUANTO)
        condicao = self.expressao()
        self.esperar(TipoToken.FACA, "Esperado 'faca' após condição")
        corpo = self.comando()
        
        return ComandoEnquanto(condicao=condicao, corpo=corpo)
    
    # ==================== EXPRESSÕES ====================
    
    def expressao(self) -> Expressao:
        """
        expressao ::= expressao_simples [op_relacional expressao_simples]
        op_relacional ::= "=" | "!=" | "<" | "<=" | ">" | ">="
        """
        esquerda = self.expressao_simples()
        
        # Operadores relacionais
        if self.corresponde(TipoToken.IGUAL, TipoToken.DIFERENTE, TipoToken.MENOR, 
                           TipoToken.MENOR_IGUAL, TipoToken.MAIOR, TipoToken.MAIOR_IGUAL):
            token_op = self.atual
            self.avancar()
            direita = self.expressao_simples()
            
            # Mapeia token para string do operador
            mapa_op = {
                TipoToken.IGUAL: '=',
                TipoToken.DIFERENTE: '!=',
                TipoToken.MENOR: '<',
                TipoToken.MENOR_IGUAL: '<=',
                TipoToken.MAIOR: '>',
                TipoToken.MAIOR_IGUAL: '>='
            }
            
            return OperacaoBinaria(esquerda=esquerda, operador=mapa_op[token_op.tipo], direita=direita)
        
        return esquerda
    
    def expressao_simples(self) -> Expressao:
        """
        expressao_simples ::= ["+"|"-"] termo {("+"|"-"|"ou") termo}
        """
        # Sinal unário opcional
        if self.corresponde(TipoToken.MAIS, TipoToken.MENOS):
            sinal = self.atual
            self.avancar()
            if sinal.tipo == TipoToken.MENOS:
                operando = self.termo()
                expressao = OperacaoUnaria(operador='-', operando=operando)
            else:
                expressao = self.termo()  # + unário é ignorado
        else:
            expressao = self.termo()
        
        # Operadores aditivos e 'ou'
        while self.corresponde(TipoToken.MAIS, TipoToken.MENOS, TipoToken.OU):
            token_op = self.atual
            self.avancar()
            direita = self.termo()
            
            mapa_op = {
                TipoToken.MAIS: '+',
                TipoToken.MENOS: '-',
                TipoToken.OU: 'ou'
            }
            
            expressao = OperacaoBinaria(esquerda=expressao, operador=mapa_op[token_op.tipo], direita=direita)
        
        return expressao
    
    def termo(self) -> Expressao:
        """
        termo ::= fator {("*"|"div"|"e") fator}
        """
        expressao = self.fator()
        
        # Operadores multiplicativos e 'e'
        while self.corresponde(TipoToken.MULTIPLICACAO, TipoToken.DIVISAO, TipoToken.E):
            token_op = self.atual
            self.avancar()
            direita = self.fator()
            
            mapa_op = {
                TipoToken.MULTIPLICACAO: '*',
                TipoToken.DIVISAO: 'div',
                TipoToken.E: 'e'
            }
            
            expressao = OperacaoBinaria(esquerda=expressao, operador=mapa_op[token_op.tipo], direita=direita)
        
        return expressao
    
    def fator(self) -> Expressao:
        """
        fator ::= ID | NUM | "(" expressao ")" | "nao" fator | "verdadeiro" | "falso"
        """
        # Identificador
        if self.corresponde(TipoToken.IDENTIFICADOR):
            token_id = self.atual
            self.avancar()
            return Identificador(nome=token_id.valor)
        
        # Número
        elif self.corresponde(TipoToken.NUMERO):
            token_num = self.atual
            self.avancar()
            return Numero(valor=token_num.valor)
        
        # Verdadeiro
        elif self.corresponde(TipoToken.VERDADEIRO):
            self.avancar()
            return Booleano(valor=True)
        
        # Falso
        elif self.corresponde(TipoToken.FALSO):
            self.avancar()
            return Booleano(valor=False)
        
        # Negação lógica
        elif self.corresponde(TipoToken.NAO):
            self.avancar()
            operando = self.fator()
            return OperacaoUnaria(operador='nao', operando=operando)
        
        # Expressão entre parênteses
        elif self.corresponde(TipoToken.ABRE_PARENTESES):
            self.avancar()
            expressao = self.expressao()
            self.esperar(TipoToken.FECHA_PARENTESES, "Esperado ')' após expressão")
            return expressao
        
        else:
            raise ErroSintatico(
                f"Esperado expressão, encontrado {self.atual.tipo.name}",
                self.atual.linha, self.atual.coluna
            )

    def chamada_procedimento(self) -> ChamadaProcedimento:
        """
        chamada_procedimento ::= ID ["(" lista_argumentos ")"]
        lista_argumentos     ::= expressao { "," expressao }
        """
        token_nome = self.esperar(TipoToken.IDENTIFICADOR, "Esperado identificador do procedimento")
        nome = token_nome.valor

        argumentos: List[Expressao] = []

        # Chamada com argumentos: proc(a, b)
        if self.corresponde(TipoToken.ABRE_PARENTESES):
            self.avancar()  # consome '('

            # Pode não ter argumentos: proc()
            if not self.corresponde(TipoToken.FECHA_PARENTESES):
                argumentos.append(self.expressao())
                while self.corresponde(TipoToken.VIRGULA):
                    self.avancar()
                    argumentos.append(self.expressao())

            self.esperar(TipoToken.FECHA_PARENTESES, "Esperado ')' ao final da chamada de procedimento")

        return ChamadaProcedimento(nome=nome, argumentos=argumentos)
