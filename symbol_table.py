"""
Symbol Table - Tabela de Símbolos
Gerencia declarações de variáveis, procedimentos e funções com suporte a escopos.
"""

from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, field


@dataclass
class Symbol:
    """Representa um símbolo na tabela."""
    name: str
    symbol_type: str  # 'inteiro', 'booleano', 'procedimento', 'funcao'
    category: str  # 'var', 'procedimento', 'funcao'
    scope_level: int
    memory_address: Optional[int] = None  # Endereço de memória (para geração de código)


@dataclass
class ScopeInfo:
    """Informações sobre um escopo para geração de ALLOC/DALLOC."""
    base_address: int  # Endereço inicial deste escopo
    var_count: int = 0  # Quantidade de variáveis declaradas neste escopo
    symbols: Dict[str, Symbol] = field(default_factory=dict)
    
    def get_alloc_info(self) -> Tuple[int, int]:
        """Retorna (endereço_base, quantidade) para ALLOC/DALLOC."""
        return (self.base_address, self.var_count)


class SymbolTable:
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
        self.scopes: List[ScopeInfo] = [ScopeInfo(base_address=0)]
        self.current_scope_level = 0
        self.next_address = 0  # Próximo endereço de memória global disponível
        
        # Lista de informações de alocação para gerar DALLOC na ordem correta
        # Cada entrada: (base_address, count) para cada ALLOC gerado
        self.alloc_stack: List[Tuple[int, int]] = []
    
    def enter_scope(self, base_address: Optional[int] = None):
        """
        Entra em um novo escopo (ex: função, procedimento).
        
        Args:
            base_address: Endereço base para este escopo. 
                         Se None, usa o próximo endereço disponível.
        """
        if base_address is None:
            base_address = self.next_address
        
        self.scopes.append(ScopeInfo(base_address=base_address))
        self.current_scope_level += 1
    
    def exit_scope(self) -> Tuple[int, int]:
        """
        Sai do escopo atual.
        
        Returns:
            Tuple[int, int]: (endereço_base, quantidade) de variáveis do escopo que está saindo
        """
        if self.current_scope_level > 0:
            scope_info = self.scopes.pop()
            self.current_scope_level -= 1
            return scope_info.get_alloc_info()
        return (0, 0)
    
    def get_current_scope_alloc_info(self) -> Tuple[int, int]:
        """Retorna informações de alocação do escopo atual."""
        return self.scopes[self.current_scope_level].get_alloc_info()
    
    def declare(self, name: str, symbol_type: str, category: str = 'var') -> Symbol:
        """
        Declara um novo símbolo no escopo atual.
        
        Args:
            name: Nome do identificador
            symbol_type: Tipo ('inteiro', 'booleano', etc)
            category: Categoria ('var', 'procedimento', 'funcao')
        
        Returns:
            Symbol: O símbolo criado
        
        Raises:
            Exception: Se o símbolo já foi declarado no escopo atual
        """
        current_scope = self.scopes[self.current_scope_level]
        
        # Verifica duplicidade apenas no escopo atual (permite shadowing)
        if name in current_scope.symbols:
            raise Exception(f"Identificador '{name}' já foi declarado neste escopo")
        
        # Aloca endereço de memória para variáveis
        address = None
        if category == 'var':
            # Endereço = base do escopo + offset
            address = current_scope.base_address + current_scope.var_count
            current_scope.var_count += 1
            # Atualiza o próximo endereço global
            if address >= self.next_address:
                self.next_address = address + 1
        
        symbol = Symbol(
            name=name,
            symbol_type=symbol_type,
            category=category,
            scope_level=self.current_scope_level,
            memory_address=address
        )
        
        current_scope.symbols[name] = symbol
        return symbol
    
    def declare_function_return(self, func_name: str, return_type: str) -> Symbol:
        """
        Reserva uma posição de memória para o valor de retorno de uma função.
        O símbolo é declarado com categoria 'funcao'.
        
        Args:
            func_name: Nome da função
            return_type: Tipo de retorno ('inteiro' ou 'booleano')
        
        Returns:
            Symbol: O símbolo da função com endereço de retorno
        """
        current_scope = self.scopes[self.current_scope_level]
        
        if func_name in current_scope.symbols:
            raise Exception(f"Identificador '{func_name}' já foi declarado neste escopo")
        
        # Aloca endereço para o valor de retorno
        address = current_scope.base_address + current_scope.var_count
        current_scope.var_count += 1
        if address >= self.next_address:
            self.next_address = address + 1
        
        symbol = Symbol(
            name=func_name,
            symbol_type=return_type,
            category='funcao',
            scope_level=self.current_scope_level,
            memory_address=address
        )
        
        current_scope.symbols[func_name] = symbol
        return symbol
    
    def declare_procedure(self, proc_name: str) -> Symbol:
        """
        Declara um procedimento (sem alocação de memória).
        
        Args:
            proc_name: Nome do procedimento
        
        Returns:
            Symbol: O símbolo do procedimento
        """
        current_scope = self.scopes[self.current_scope_level]
        
        if proc_name in current_scope.symbols:
            raise Exception(f"Identificador '{proc_name}' já foi declarado neste escopo")
        
        symbol = Symbol(
            name=proc_name,
            symbol_type='procedimento',
            category='procedimento',
            scope_level=self.current_scope_level,
            memory_address=None
        )
        
        current_scope.symbols[proc_name] = symbol
        return symbol
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """
        Busca um símbolo nos escopos (do mais interno ao mais externo).
        
        Args:
            name: Nome do identificador a buscar
        
        Returns:
            Symbol ou None: O símbolo encontrado ou None se não existir
        """
        # Procura do escopo mais interno para o mais externo
        for level in range(self.current_scope_level, -1, -1):
            if name in self.scopes[level].symbols:
                return self.scopes[level].symbols[name]
        return None
    
    def lookup_current_scope(self, name: str) -> Optional[Symbol]:
        """Busca um símbolo apenas no escopo atual."""
        return self.scopes[self.current_scope_level].symbols.get(name)
    
    def get_all_symbols(self) -> List[Symbol]:
        """Retorna todos os símbolos de todos os escopos."""
        symbols = []
        for scope in self.scopes:
            symbols.extend(scope.symbols.values())
        return symbols
    
    def get_current_scope_symbols(self) -> List[Symbol]:
        """Retorna todos os símbolos do escopo atual."""
        return list(self.scopes[self.current_scope_level].symbols.values())
    
    def get_current_scope_var_count(self) -> int:
        """Retorna a quantidade de variáveis no escopo atual."""
        return self.scopes[self.current_scope_level].var_count
    
    def get_current_base_address(self) -> int:
        """Retorna o endereço base do escopo atual."""
        return self.scopes[self.current_scope_level].base_address
    
    def get_next_address(self) -> int:
        """Retorna o próximo endereço disponível (para calcular base de escopo filho)."""
        scope = self.scopes[self.current_scope_level]
        return scope.base_address + scope.var_count
    
    def get_memory_size(self) -> int:
        """Retorna o tamanho total de memória necessária."""
        return self.next_address
    
    def push_alloc_info(self, base_addr: int, count: int):
        """Empilha informação de ALLOC para posterior DALLOC."""
        self.alloc_stack.append((base_addr, count))
    
    def pop_alloc_info(self) -> Tuple[int, int]:
        """Desempilha informação de ALLOC para gerar DALLOC."""
        if self.alloc_stack:
            return self.alloc_stack.pop()
        return (0, 0)
    
    def get_alloc_stack(self) -> List[Tuple[int, int]]:
        """Retorna a pilha de alocações atual."""
        return self.alloc_stack.copy()
    
    def __str__(self) -> str:
        """Representação em string da tabela de símbolos."""
        result = "=== Tabela de Símbolos ===\n"
        for level, scope in enumerate(self.scopes):
            result += f"Escopo {level} (base={scope.base_address}, vars={scope.var_count}):\n"
            for name, symbol in scope.symbols.items():
                result += f"  {name}: {symbol.symbol_type} ({symbol.category})"
                if symbol.memory_address is not None:
                    result += f" @ {symbol.memory_address}"
                result += "\n"
        return result
