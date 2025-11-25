"""
Módulo da Árvore Sintática Abstrata (AST) do Compilador LPD
Define todos os nós que representam as estruturas da linguagem.
"""

from dataclasses import dataclass
from typing import List, Optional


# ==================== CLASSE BASE ====================

class No:
    """Classe base para todos os nós da AST."""
    pass


# ==================== PROGRAMA ====================

@dataclass
class Programa(No):
    """Nó raiz que representa o programa completo."""
    nome: str
    declaracoes_variaveis: Optional['DeclaracoesVariaveis']
    procedimentos: List['Procedimento']
    funcoes: List['Funcao']
    comando_composto: 'ComandoComposto'


# ==================== DECLARAÇÕES ====================

@dataclass
class DeclaracoesVariaveis(No):
    """Lista de declarações de variáveis."""
    declaracoes: List['DeclaracaoVariavel']


@dataclass
class DeclaracaoVariavel(No):
    """Declaração de uma ou mais variáveis de um tipo."""
    identificadores: List[str]
    tipo: str  # 'inteiro' ou 'booleano'


@dataclass
class Procedimento(No):
    """Declaração de um procedimento."""
    nome: str
    parametros: List['Parametro']
    bloco: 'Bloco'


@dataclass
class Funcao(No):
    """Declaração de uma função."""
    nome: str
    parametros: List['Parametro']
    tipo_retorno: str
    bloco: 'Bloco'


@dataclass
class Parametro(No):
    """Parâmetro de procedimento ou função."""
    identificadores: List[str]
    tipo: str


@dataclass
class Bloco(No):
    """Bloco de código com declarações e comandos."""
    declaracoes_variaveis: Optional[DeclaracoesVariaveis]
    procedimentos: List[Procedimento]
    funcoes: List[Funcao]
    comando_composto: 'ComandoComposto'


# ==================== COMANDOS ====================

@dataclass
class ComandoComposto(No):
    """Sequência de comandos entre 'inicio' e 'fim'."""
    comandos: List['Comando']


class Comando(No):
    """Classe base para todos os comandos."""
    pass


@dataclass
class Atribuicao(Comando):
    """Comando de atribuição: identificador := expressao"""
    identificador: str
    expressao: 'Expressao'


@dataclass
class ChamadaProcedimento(Comando):
    """Chamada de procedimento."""
    nome: str
    argumentos: List['Expressao']


@dataclass
class ComandoLeitura(Comando):
    """Comando leia(identificador)."""
    identificador: str


@dataclass
class ComandoEscrita(Comando):
    """Comando escreva(expressao)."""
    expressao: 'Expressao'


@dataclass
class ComandoSe(Comando):
    """Comando condicional se-entao-senao."""
    condicao: 'Expressao'
    comando_entao: Comando
    comando_senao: Optional[Comando] = None


@dataclass
class ComandoEnquanto(Comando):
    """Comando de repetição enquanto-faca."""
    condicao: 'Expressao'
    corpo: Comando


@dataclass
class ComandoVazio(Comando):
    """Comando vazio (nenhuma operação)."""
    pass


# ==================== EXPRESSÕES ====================

class Expressao(No):
    """Classe base para todas as expressões."""
    tipo_expressao: Optional[str] = None  # 'inteiro' ou 'booleano' (preenchido na análise semântica)


@dataclass
class OperacaoBinaria(Expressao):
    """Operação binária: esquerda operador direita"""
    esquerda: Expressao
    operador: str  # '+', '-', '*', 'div', 'e', 'ou', '=', '!=', '<', '<=', '>', '>='
    direita: Expressao
    tipo_expressao: Optional[str] = None


@dataclass
class OperacaoUnaria(Expressao):
    """Operação unária: operador operando"""
    operador: str  # 'nao', '-'
    operando: Expressao
    tipo_expressao: Optional[str] = None


@dataclass
class Identificador(Expressao):
    """Referência a uma variável ou função."""
    nome: str
    tipo_expressao: Optional[str] = None


@dataclass
class Numero(Expressao):
    """Literal numérico inteiro."""
    valor: int
    tipo_expressao: str = 'inteiro'


@dataclass
class Booleano(Expressao):
    """Literal booleano (verdadeiro/falso)."""
    valor: bool
    tipo_expressao: str = 'booleano'


@dataclass
class ChamadaFuncao(Expressao):
    """Chamada de função como expressão."""
    nome: str
    argumentos: List['Expressao']
    tipo_expressao: Optional[str] = None


# ==================== UTILITÁRIOS ====================

def arvore_para_string(no: No, recuo: int = 0) -> str:
    """Converte um nó da AST para representação em string (para debug)."""
    prefixo = "  " * recuo
    
    if isinstance(no, Programa):
        resultado = f"{prefixo}Programa({no.nome})\n"
        if no.declaracoes_variaveis:
            resultado += arvore_para_string(no.declaracoes_variaveis, recuo + 1)
        for proc in no.procedimentos:
            resultado += arvore_para_string(proc, recuo + 1)
        for func in no.funcoes:
            resultado += arvore_para_string(func, recuo + 1)
        resultado += arvore_para_string(no.comando_composto, recuo + 1)
        return resultado
    
    elif isinstance(no, DeclaracoesVariaveis):
        resultado = f"{prefixo}DeclaracoesVariaveis\n"
        for decl in no.declaracoes:
            resultado += arvore_para_string(decl, recuo + 1)
        return resultado
    
    elif isinstance(no, DeclaracaoVariavel):
        return f"{prefixo}DeclaracaoVar({', '.join(no.identificadores)}: {no.tipo})\n"
    
    elif isinstance(no, Procedimento):
        resultado = f"{prefixo}Procedimento({no.nome})\n"
        resultado += arvore_para_string(no.bloco, recuo + 1)
        return resultado
    
    elif isinstance(no, Funcao):
        resultado = f"{prefixo}Funcao({no.nome}): {no.tipo_retorno}\n"
        resultado += arvore_para_string(no.bloco, recuo + 1)
        return resultado
    
    elif isinstance(no, Bloco):
        resultado = f"{prefixo}Bloco\n"
        if no.declaracoes_variaveis:
            resultado += arvore_para_string(no.declaracoes_variaveis, recuo + 1)
        for proc in no.procedimentos:
            resultado += arvore_para_string(proc, recuo + 1)
        for func in no.funcoes:
            resultado += arvore_para_string(func, recuo + 1)
        resultado += arvore_para_string(no.comando_composto, recuo + 1)
        return resultado
    
    elif isinstance(no, ComandoComposto):
        resultado = f"{prefixo}ComandoComposto\n"
        for cmd in no.comandos:
            resultado += arvore_para_string(cmd, recuo + 1)
        return resultado
    
    elif isinstance(no, Atribuicao):
        resultado = f"{prefixo}Atribuicao({no.identificador} :=)\n"
        resultado += arvore_para_string(no.expressao, recuo + 1)
        return resultado
    
    elif isinstance(no, ComandoLeitura):
        return f"{prefixo}Leitura({no.identificador})\n"
    
    elif isinstance(no, ComandoEscrita):
        resultado = f"{prefixo}Escrita\n"
        resultado += arvore_para_string(no.expressao, recuo + 1)
        return resultado
    
    elif isinstance(no, ComandoSe):
        resultado = f"{prefixo}Se\n"
        resultado += f"{prefixo}  condicao:\n"
        resultado += arvore_para_string(no.condicao, recuo + 2)
        resultado += f"{prefixo}  entao:\n"
        resultado += arvore_para_string(no.comando_entao, recuo + 2)
        if no.comando_senao:
            resultado += f"{prefixo}  senao:\n"
            resultado += arvore_para_string(no.comando_senao, recuo + 2)
        return resultado
    
    elif isinstance(no, ComandoEnquanto):
        resultado = f"{prefixo}Enquanto\n"
        resultado += f"{prefixo}  condicao:\n"
        resultado += arvore_para_string(no.condicao, recuo + 2)
        resultado += f"{prefixo}  corpo:\n"
        resultado += arvore_para_string(no.corpo, recuo + 2)
        return resultado
    
    elif isinstance(no, OperacaoBinaria):
        resultado = f"{prefixo}OperacaoBinaria({no.operador})\n"
        resultado += arvore_para_string(no.esquerda, recuo + 1)
        resultado += arvore_para_string(no.direita, recuo + 1)
        return resultado
    
    elif isinstance(no, OperacaoUnaria):
        resultado = f"{prefixo}OperacaoUnaria({no.operador})\n"
        resultado += arvore_para_string(no.operando, recuo + 1)
        return resultado
    
    elif isinstance(no, Identificador):
        return f"{prefixo}Identificador({no.nome})\n"
    
    elif isinstance(no, Numero):
        return f"{prefixo}Numero({no.valor})\n"
    
    elif isinstance(no, Booleano):
        return f"{prefixo}Booleano({no.valor})\n"
    
    elif isinstance(no, ComandoVazio):
        return f"{prefixo}ComandoVazio\n"

    elif isinstance(no, ChamadaProcedimento):
        resultado = f"{prefixo}ChamadaProcedimento({no.nome})\n"
        for arg in no.argumentos:
            resultado += arvore_para_string(arg, recuo + 1)
        return resultado

    elif isinstance(no, ChamadaFuncao):
        resultado = f"{prefixo}ChamadaFuncao({no.nome})\n"
        for arg in no.argumentos:
            resultado += arvore_para_string(arg, recuo + 1)
        return resultado
    
    else:
        return f"{prefixo}{no.__class__.__name__}\n"
