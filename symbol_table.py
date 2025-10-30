"""
Symbol Table - Tabela de Símbolos
Gerencia declarações de variáveis, procedimentos e funções com suporte a escopos.
"""

from typing import Optional, Dict, List
from dataclasses import dataclass


@dataclass
class Symbol:
    """Representa um símbolo na tabela."""
    name: str
    symbol_type: str  # 'inteiro', 'booleano', 'procedimento', 'funcao'
    category: str  # 'var', 'procedure', 'function'
    scope_level: int
    memory_address: Optional[int] = None  # Endereço de memória (para geração de código)


class SymbolTable:
    """
    Tabela de símbolos com suporte a escopos hierárquicos.
    Gerencia declarações e verifica uso correto de identificadores.
    """
    
    def __init__(self):
        self.scopes: List[Dict[str, Symbol]] = [{}]  # Lista de escopos (dicionários)
        self.current_scope_level = 0
        self.next_address = 0  # Próximo endereço de memória disponível
    
    def enter_scope(self):
        """Entra em um novo escopo (ex: função, procedimento)."""
        self.scopes.append({})
        self.current_scope_level += 1
    
    def exit_scope(self):
        """Sai do escopo atual."""
        if self.current_scope_level > 0:
            self.scopes.pop()
            self.current_scope_level -= 1
    
    def declare(self, name: str, symbol_type: str, category: str = 'var') -> Symbol:
        """
        Declara um novo símbolo no escopo atual.
        
        Args:
            name: Nome do identificador
            symbol_type: Tipo ('inteiro', 'booleano', etc)
            category: Categoria ('var', 'procedure', 'function')
        
        Returns:
            Symbol: O símbolo criado
        
        Raises:
            Exception: Se o símbolo já foi declarado no escopo atual
        """
        current_scope = self.scopes[self.current_scope_level]
        
        if name in current_scope:
            raise Exception(f"Identificador '{name}' já foi declarado neste escopo")
        
        # Aloca endereço de memória para variáveis
        address = None
        if category == 'var':
            address = self.next_address
            self.next_address += 1
        
        symbol = Symbol(
            name=name,
            symbol_type=symbol_type,
            category=category,
            scope_level=self.current_scope_level,
            memory_address=address
        )
        
        current_scope[name] = symbol
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
            if name in self.scopes[level]:
                return self.scopes[level][name]
        return None
    
    def lookup_current_scope(self, name: str) -> Optional[Symbol]:
        """Busca um símbolo apenas no escopo atual."""
        return self.scopes[self.current_scope_level].get(name)
    
    def get_all_symbols(self) -> List[Symbol]:
        """Retorna todos os símbolos de todos os escopos."""
        symbols = []
        for scope in self.scopes:
            symbols.extend(scope.values())
        return symbols
    
    def get_current_scope_symbols(self) -> List[Symbol]:
        """Retorna todos os símbolos do escopo atual."""
        return list(self.scopes[self.current_scope_level].values())
    
    def get_memory_size(self) -> int:
        """Retorna o tamanho total de memória necessária."""
        return self.next_address
    
    def __str__(self) -> str:
        """Representação em string da tabela de símbolos."""
        result = "=== Tabela de Símbolos ===\n"
        for level, scope in enumerate(self.scopes):
            result += f"Escopo {level}:\n"
            for name, symbol in scope.items():
                result += f"  {name}: {symbol.symbol_type} ({symbol.category})"
                if symbol.memory_address is not None:
                    result += f" @ {symbol.memory_address}"
                result += "\n"
        return result

