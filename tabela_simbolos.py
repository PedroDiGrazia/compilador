"""
Tabela de Símbolos do Compilador LPD
Gerencia declarações de variáveis, procedimentos e funções com suporte a escopos.
"""

from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, field


@dataclass
class Simbolo:
    """Representa um símbolo na tabela."""
    nome: str
    tipo: str  # 'inteiro', 'booleano', 'procedimento', 'funcao'
    categoria: str  # 'variavel', 'procedimento', 'funcao'
    nivel_escopo: int
    endereco_memoria: Optional[int] = None  # Endereço de memória (para geração de código)


@dataclass
class InfoEscopo:
    """Informações sobre um escopo para geração de ALLOC/DALLOC."""
    endereco_base: int  # Endereço inicial deste escopo
    quantidade_variaveis: int = 0  # Quantidade de variáveis declaradas neste escopo
    simbolos: Dict[str, Simbolo] = field(default_factory=dict)
    
    def obter_info_alocacao(self) -> Tuple[int, int]:
        """Retorna (endereço_base, quantidade) para ALLOC/DALLOC."""
        return (self.endereco_base, self.quantidade_variaveis)


class TabelaSimbolos:
    """
    Tabela de símbolos com suporte a escopos hierárquicos.
    Gerencia declarações e verifica uso correto de identificadores.
    
    Implementa endereçamento por escopo conforme notas de aula:
    - Cada escopo tem um endereço base
    - Variáveis são alocadas sequencialmente a partir do endereço base
    - O endereço base de um escopo filho = último endereço usado pelo escopo pai + 1
    """
    
    def __init__(self):
        # Lista de escopos com suas informações
        self.escopos: List[InfoEscopo] = [InfoEscopo(endereco_base=0)]
        self.nivel_escopo_atual = 0
        self.proximo_endereco = 0  # Próximo endereço de memória global disponível
        
        # Lista de informações de alocação para gerar DALLOC na ordem correta
        # Cada entrada: (endereco_base, quantidade) para cada ALLOC gerado
        self.pilha_alocacao: List[Tuple[int, int]] = []
    
    def entrar_escopo(self, endereco_base: Optional[int] = None):
        """
        Entra em um novo escopo (ex: função, procedimento).
        
        Args:
            endereco_base: Endereço base para este escopo. 
                          Se None, usa o próximo endereço disponível.
        """
        if endereco_base is None:
            endereco_base = self.proximo_endereco
        
        self.escopos.append(InfoEscopo(endereco_base=endereco_base))
        self.nivel_escopo_atual += 1
    
    def sair_escopo(self) -> Tuple[int, int]:
        """
        Sai do escopo atual.
        
        Returns:
            Tuple[int, int]: (endereco_base, quantidade) de variáveis do escopo que está saindo
        """
        if self.nivel_escopo_atual > 0:
            info_escopo = self.escopos.pop()
            self.nivel_escopo_atual -= 1
            return info_escopo.obter_info_alocacao()
        return (0, 0)
    
    def obter_info_alocacao_escopo_atual(self) -> Tuple[int, int]:
        """Retorna informações de alocação do escopo atual."""
        return self.escopos[self.nivel_escopo_atual].obter_info_alocacao()
    
    def declarar(self, nome: str, tipo: str, categoria: str = 'variavel') -> Simbolo:
        """
        Declara um novo símbolo no escopo atual.
        """
        escopo_atual = self.escopos[self.nivel_escopo_atual]
        
        # Verifica duplicidade apenas no escopo atual (permite shadowing)
        if nome in escopo_atual.simbolos:
            raise Exception(f"Identificador '{nome}' já foi declarado neste escopo")
        
        # Aloca endereço de memória para variáveis
        endereco = None
        if categoria == 'variavel':
            # Endereço = base do escopo + offset
            endereco = escopo_atual.endereco_base + escopo_atual.quantidade_variaveis
            escopo_atual.quantidade_variaveis += 1
            # Atualiza o próximo endereço global
            if endereco >= self.proximo_endereco:
                self.proximo_endereco = endereco + 1
        
        simbolo = Simbolo(
            nome=nome,
            tipo=tipo,
            categoria=categoria,
            nivel_escopo=self.nivel_escopo_atual,
            endereco_memoria=endereco
        )
        
        escopo_atual.simbolos[nome] = simbolo
        return simbolo
    
    def declarar_retorno_funcao(self, nome_funcao: str, tipo_retorno: str) -> Simbolo:
        """
        Reserva uma posição de memória para o valor de retorno de uma função.
        O símbolo é declarado com categoria 'funcao'.
        """
        escopo_atual = self.escopos[self.nivel_escopo_atual]
        
        if nome_funcao in escopo_atual.simbolos:
            raise Exception(f"Identificador '{nome_funcao}' já foi declarado neste escopo")
        
        # Aloca endereço para o valor de retorno
        endereco = escopo_atual.endereco_base + escopo_atual.quantidade_variaveis
        escopo_atual.quantidade_variaveis += 1
        if endereco >= self.proximo_endereco:
            self.proximo_endereco = endereco + 1
        
        simbolo = Simbolo(
            nome=nome_funcao,
            tipo=tipo_retorno,
            categoria='funcao',
            nivel_escopo=self.nivel_escopo_atual,
            endereco_memoria=endereco
        )
        
        escopo_atual.simbolos[nome_funcao] = simbolo
        return simbolo
    
    def declarar_procedimento(self, nome_procedimento: str) -> Simbolo:
        """
        Declara um procedimento (sem alocação de memória).
        """
        escopo_atual = self.escopos[self.nivel_escopo_atual]
        
        if nome_procedimento in escopo_atual.simbolos:
            raise Exception(f"Identificador '{nome_procedimento}' já foi declarado neste escopo")
        
        simbolo = Simbolo(
            nome=nome_procedimento,
            tipo='procedimento',
            categoria='procedimento',
            nivel_escopo=self.nivel_escopo_atual,
            endereco_memoria=None
        )
        
        escopo_atual.simbolos[nome_procedimento] = simbolo
        return simbolo
    
    def buscar(self, nome: str) -> Optional[Simbolo]:
        """
        Busca um símbolo nos escopos (do mais interno ao mais externo).
        """
        # Procura do escopo mais interno para o mais externo
        for nivel in range(self.nivel_escopo_atual, -1, -1):
            if nome in self.escopos[nivel].simbolos:
                return self.escopos[nivel].simbolos[nome]
        return None
    
    def buscar_escopo_atual(self, nome: str) -> Optional[Simbolo]:
        """Busca um símbolo apenas no escopo atual."""
        return self.escopos[self.nivel_escopo_atual].simbolos.get(nome)
    
    def obter_todos_simbolos(self) -> List[Simbolo]:
        """Retorna todos os símbolos de todos os escopos."""
        simbolos = []
        for escopo in self.escopos:
            simbolos.extend(escopo.simbolos.values())
        return simbolos
    
    def obter_simbolos_escopo_atual(self) -> List[Simbolo]:
        """Retorna todos os símbolos do escopo atual."""
        return list(self.escopos[self.nivel_escopo_atual].simbolos.values())
    
    def obter_quantidade_variaveis_escopo_atual(self) -> int:
        """Retorna a quantidade de variáveis no escopo atual."""
        return self.escopos[self.nivel_escopo_atual].quantidade_variaveis
    
    def obter_endereco_base_atual(self) -> int:
        """Retorna o endereço base do escopo atual."""
        return self.escopos[self.nivel_escopo_atual].endereco_base
    
    def obter_proximo_endereco(self) -> int:
        """Retorna o próximo endereço disponível (para calcular base de escopo filho)."""
        escopo = self.escopos[self.nivel_escopo_atual]
        return escopo.endereco_base + escopo.quantidade_variaveis
    
    def obter_tamanho_memoria(self) -> int:
        """Retorna o tamanho total de memória necessária."""
        return self.proximo_endereco
    
    def empilhar_info_alocacao(self, endereco_base: int, quantidade: int):
        """Empilha informação de ALLOC para posterior DALLOC."""
        self.pilha_alocacao.append((endereco_base, quantidade))
    
    def desempilhar_info_alocacao(self) -> Tuple[int, int]:
        """Desempilha informação de ALLOC para gerar DALLOC."""
        if self.pilha_alocacao:
            return self.pilha_alocacao.pop()
        return (0, 0)
    
    def obter_pilha_alocacao(self) -> List[Tuple[int, int]]:
        """Retorna a pilha de alocações atual."""
        return self.pilha_alocacao.copy()
    
    def __str__(self) -> str:
        """Representação em string da tabela de símbolos."""
        resultado = "=== Tabela de Símbolos ===\n"
        for nivel, escopo in enumerate(self.escopos):
            resultado += f"Escopo {nivel} (base={escopo.endereco_base}, vars={escopo.quantidade_variaveis}):\n"
            for nome, simbolo in escopo.simbolos.items():
                resultado += f"  {nome}: {simbolo.tipo} ({simbolo.categoria})"
                if simbolo.endereco_memoria is not None:
                    resultado += f" @ {simbolo.endereco_memoria}"
                resultado += "\n"
        return resultado
