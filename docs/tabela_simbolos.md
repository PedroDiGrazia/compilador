# Tabela de Símbolos - Documentação

## Introdução e Teoria

### Base Teórica

A **Tabela de Símbolos** é uma estrutura de dados essencial do compilador que registra os identificadores usados no programa fonte e armazena informações sobre seus atributos. Conforme as notas de aula (seção 4), a tabela de símbolos serve para:

1. **Registrar identificadores**: Armazenar nomes de variáveis, procedimentos e funções
2. **Coletar atributos**: Guardar tipo, escopo, endereço de memória, etc.
3. **Suportar análise semântica**: Verificar declarações e tipos
4. **Suportar geração de código**: Fornecer endereços de memória para variáveis

### Função da Tabela de Símbolos

Segundo as notas de aula (seção 4):
> "Uma tabela de símbolos é uma estrutura de dados contendo um registro para cada identificador, com os campos contendo os atributos do identificador."

As informações são coletadas durante as fases de análise e utilizadas na fase de síntese (geração de código).

### Escopos e Visibilidade

A linguagem LPD suporta **escopos hierárquicos** (aninhados):
- **Escopo global**: Variáveis declaradas no programa principal
- **Escopos locais**: Variáveis declaradas em procedimentos e funções
- **Aninhamento**: Procedimentos e funções podem ser declarados dentro de outros

A tabela de símbolos deve refletir a **visibilidade** dos símbolos:
- Símbolos locais são visíveis apenas dentro de seu escopo
- Símbolos externos são visíveis em escopos internos
- Se um nome está definido em múltiplos escopos, a definição mais interna prevalece (shadowing)

### Endereçamento de Memória

A tabela de símbolos também gerencia o **endereçamento de memória** para variáveis:
- Cada variável recebe um endereço único
- Variáveis de diferentes escopos podem compartilhar endereços (quando o escopo anterior termina)
- O endereço base de um escopo filho = último endereço usado pelo escopo pai + 1

## Estrutura do Código

### Classe `Simbolo`

Representa um símbolo na tabela de símbolos.

**Atributos:**
- `nome: str` - Nome do identificador (lexema)
- `tipo: str` - Tipo do símbolo (`'inteiro'`, `'booleano'`, `'procedimento'`, `'funcao'`)
- `categoria: str` - Categoria (`'variavel'`, `'procedimento'`, `'funcao'`)
- `nivel_escopo: int` - Nível do escopo onde foi declarado (0 = global)
- `endereco_memoria: Optional[int]` - Endereço de memória alocado (None para procedimentos)

### Classe `InfoEscopo`

Armazena informações sobre um escopo específico.

**Atributos:**
- `endereco_base: int` - Endereço inicial deste escopo
- `quantidade_variaveis: int` - Quantidade de variáveis declaradas neste escopo
- `simbolos: Dict[str, Simbolo]` - Dicionário de símbolos deste escopo (chave = nome)

**Método:**
- `obter_info_alocacao() -> Tuple[int, int]`: Retorna `(endereco_base, quantidade)` para ALLOC/DALLOC

### Classe Principal: `TabelaSimbolos`

Gerencia a tabela de símbolos com suporte a escopos hierárquicos.

#### Atributos da Classe

```python
def __init__(self):
    self.escopos: List[InfoEscopo] = [InfoEscopo(endereco_base=0)]  # Lista de escopos
    self.nivel_escopo_atual = 0      # Nível do escopo atual (0 = global)
    self.proximo_endereco = 0        # Próximo endereço disponível globalmente
    self.pilha_alocacao: List[Tuple[int, int]] = []  # Pilha para ALLOC/DALLOC
```

**Estrutura:**
- `escopos`: Lista de escopos, onde cada escopo contém seus símbolos
- `nivel_escopo_atual`: Indica qual escopo está ativo
- `proximo_endereco`: Controla alocação global de memória
- `pilha_alocacao`: Rastreia alocações para gerar DALLOC na ordem correta

## Detalhamento das Funções

### Gerenciamento de Escopos

#### `entrar_escopo(endereco_base: Optional[int] = None)`

Entra em um novo escopo (ex: ao iniciar função ou procedimento).

**Parâmetros:**
- `endereco_base`: Endereço base para este escopo. Se `None`, usa o próximo endereço disponível.

**Processo:**
1. Calcula endereço base (se não fornecido)
2. Cria novo `InfoEscopo` com esse endereço base
3. Adiciona à lista de escopos
4. Incrementa `nivel_escopo_atual`

**Uso:** Chamado ao entrar em função, procedimento ou bloco aninhado.

#### `sair_escopo() -> Tuple[int, int]`

Sai do escopo atual (ex: ao terminar função ou procedimento).

**Retorno:** `(endereco_base, quantidade)` do escopo que está saindo (para DALLOC)

**Processo:**
1. Remove o escopo mais interno da lista
2. Decrementa `nivel_escopo_atual`
3. Retorna informações de alocação do escopo removido

**Uso:** Chamado ao sair de função, procedimento ou bloco.

### Declaração de Símbolos

#### `declarar(nome: str, tipo: str, categoria: str = 'variavel') -> Simbolo`

Declara um novo símbolo no escopo atual.

**Parâmetros:**
- `nome`: Nome do identificador
- `tipo`: Tipo (`'inteiro'`, `'booleano'`, etc.)
- `categoria`: Categoria (`'variavel'`, `'procedimento'`, `'funcao'`)

**Retorno:** `Simbolo` criado

**Processo:**
1. Verifica duplicidade no escopo atual (permite shadowing entre escopos)
2. Se for variável, aloca endereço de memória:
   - Endereço = `endereco_base` + `quantidade_variaveis` (offset)
   - Incrementa `quantidade_variaveis` do escopo
   - Atualiza `proximo_endereco` se necessário
3. Cria e armazena símbolo no escopo atual

**Erros:**
- `Exception`: Se o nome já existe no escopo atual

**Uso:** Declarar variáveis, procedimentos e funções.

#### `declarar_retorno_funcao(nome_funcao: str, tipo_retorno: str) -> Simbolo`

Reserva uma posição de memória para o valor de retorno de uma função.

**Parâmetros:**
- `nome_funcao`: Nome da função
- `tipo_retorno`: Tipo de retorno

**Retorno:** `Simbolo` representando a função

**Processo:**
1. Verifica duplicidade
2. Aloca endereço para valor de retorno (como se fosse uma variável)
3. Cria símbolo com categoria `'funcao'`

**Uso:** Declarar funções (que precisam de espaço para retorno).

#### `declarar_procedimento(nome_procedimento: str) -> Simbolo`

Declara um procedimento (sem alocação de memória).

**Parâmetros:**
- `nome_procedimento`: Nome do procedimento

**Retorno:** `Simbolo` representando o procedimento

**Processo:**
1. Verifica duplicidade
2. Cria símbolo com categoria `'procedimento'` e `endereco_memoria=None`

**Uso:** Declarar procedimentos.

### Busca de Símbolos

#### `buscar(nome: str) -> Optional[Simbolo]`

Busca um símbolo nos escopos (do mais interno ao mais externo).

**Parâmetros:**
- `nome`: Nome do identificador a buscar

**Retorno:** `Simbolo` encontrado ou `None` se não encontrado

**Processo:**
1. Começa do escopo mais interno (`nivel_escopo_atual`)
2. Procura em cada escopo até o global (nível 0)
3. Retorna o primeiro símbolo encontrado (shadowing)

**Uso:** Verificar se identificador foi declarado e obter suas informações.

#### `buscar_escopo_atual(nome: str) -> Optional[Simbolo]`

Busca um símbolo apenas no escopo atual.

**Retorno:** `Simbolo` do escopo atual ou `None`

**Uso:** Verificar duplicidade antes de declarar.

### Informações de Alocação

#### `obter_info_alocacao_escopo_atual() -> Tuple[int, int]`

Retorna informações de alocação do escopo atual.

**Retorno:** `(endereco_base, quantidade_variaveis)`

**Uso:** Gerar instrução ALLOC.

#### `obter_proximo_endereco() -> int`

Retorna o próximo endereço disponível (para calcular base de escopo filho).

**Retorno:** `endereco_base + quantidade_variaveis` do escopo atual

**Uso:** Calcular endereço base para escopo filho.

#### `obter_tamanho_memoria() -> int`

Retorna o tamanho total de memória necessária.

**Retorno:** `proximo_endereco` (último endereço usado + 1)

**Uso:** Estimar memória total necessária.

### Pilha de Alocação

#### `empilhar_info_alocacao(endereco_base: int, quantidade: int)`

Empilha informação de ALLOC para posterior DALLOC.

**Uso:** Rastrear alocações para gerar DALLOC na ordem inversa.

#### `desempilhar_info_alocacao() -> Tuple[int, int]`

Desempilha informação de ALLOC para gerar DALLOC.

**Retorno:** `(endereco_base, quantidade)` do último ALLOC

**Uso:** Gerar DALLOC na ordem correta (LIFO).

## Integração

### Uso pelo Analisador Semântico

O `AnalisadorSemantico` utiliza a tabela de símbolos para:
- Verificar declarações de identificadores
- Verificar tipos em expressões
- Gerenciar escopos durante análise

```python
analisador_semantico = AnalisadorSemantico()
tabela_simbolos = analisador_semantico.analisar(ast)
```

### Uso pelo Gerador de Código

O `GeradorCodigo` utiliza a tabela de símbolos para:
- Obter endereços de memória de variáveis
- Gerar instruções ALLOC/DALLOC
- Identificar funções e procedimentos

```python
gerador = GeradorCodigo()
instrucoes = gerador.gerar(ast, tabela_simbolos)
```

### Fluxo de Dados

```
AST (Programa)
    ↓
AnalisadorSemantico.analisar()
    ↓
TabelaSimbolos (populada)
    ↓
GeradorCodigo.gerar()
    ↓
Código Assembly (com endereços)
```

## Exemplos Práticos

### Exemplo 1: Declaração de Variáveis Globais

```python
from tabela_simbolos import TabelaSimbolos

tabela = TabelaSimbolos()

# Declara variáveis globais
tabela.declarar("x", "inteiro", "variavel")  # Endereço 0
tabela.declarar("y", "inteiro", "variavel")  # Endereço 1
tabela.declarar("flag", "booleano", "variavel")  # Endereço 2

# Busca símbolo
simbolo = tabela.buscar("x")
print(f"x: tipo={simbolo.tipo}, endereco={simbolo.endereco_memoria}")
# Saída: x: tipo=inteiro, endereco=0
```

### Exemplo 2: Escopos Aninhados

```python
tabela = TabelaSimbolos()

# Escopo global
tabela.declarar("global", "inteiro", "variavel")  # Endereço 0

# Entra em função
endereco_base = tabela.obter_proximo_endereco()  # 1
tabela.entrar_escopo(endereco_base)

# Variáveis locais da função
tabela.declarar("local", "inteiro", "variavel")  # Endereço 1
tabela.declarar("temp", "inteiro", "variavel")   # Endereço 2

# Busca: shadowing funciona
simbolo_local = tabela.buscar("local")  # Encontra local (nível 1)
simbolo_global = tabela.buscar("global")  # Encontra global (nível 0)

# Sai da função
info = tabela.sair_escopo()  # (1, 2) - para DALLOC
```

### Exemplo 3: Função com Retorno

```python
tabela = TabelaSimbolos()

# Reserva espaço para retorno da função
tabela.declarar_retorno_funcao("soma", "inteiro")  # Endereço 0

# Entra no escopo da função
tabela.entrar_escopo(1)

# Parâmetros e variáveis locais
tabela.declarar("a", "inteiro", "variavel")  # Endereço 1
tabela.declarar("b", "inteiro", "variavel")  # Endereço 2

# Busca função (para atribuição de retorno)
funcao = tabela.buscar("soma")  # Encontra no escopo global
print(f"Retorno de {funcao.nome}: endereco={funcao.endereco_memoria}")
# Saída: Retorno de soma: endereco=0
```

### Exemplo 4: Visualização da Tabela

```python
tabela = TabelaSimbolos()

# Popula tabela
tabela.declarar("x", "inteiro")
tabela.declarar_procedimento("proc1")
tabela.entrar_escopo(1)
tabela.declarar("y", "booleano")

# Visualiza estrutura
print(tabela)
```

**Saída:**
```
=== Tabela de Símbolos ===
Escopo 0 (base=0, vars=1):
  x: inteiro (variavel) @ 0
  proc1: procedimento (procedimento)
Escopo 1 (base=1, vars=1):
  y: booleano (variavel) @ 1
```

## Análise Detalhada do Código

### Método `entrar_escopo` - Análise Detalhada

```python
def entrar_escopo(self, endereco_base: Optional[int] = None):
    if endereco_base is None:
        endereco_base = self.proximo_endereco
    
    self.escopos.append(InfoEscopo(endereco_base=endereco_base))
    self.nivel_escopo_atual += 1
```

**Explicação linha por linha:**
- `if endereco_base is None`: Verifica se endereço base foi fornecido
  - `endereco_base = self.proximo_endereco`: Se não fornecido, usa próximo endereço disponível
  - Isso garante que escopos não se sobreponham na memória
- `self.escopos.append(InfoEscopo(...))`: Adiciona novo escopo à lista
  - `InfoEscopo` é criado com endereço base fornecido
  - Escopo começa vazio (sem símbolos, quantidade_variaveis=0)
- `self.nivel_escopo_atual += 1`: Incrementa nível do escopo atual
  - Escopo global é nível 0
  - Cada escopo aninhado incrementa o nível

**Exemplo de execução:**
```python
# Estado inicial: nivel_escopo_atual=0, proximo_endereco=0
tabela.entrar_escopo()  # endereco_base=0 (usa proximo_endereco)
# Agora: nivel_escopo_atual=1, escopos tem 2 elementos (global + novo)
```

### Método `sair_escopo` - Análise Detalhada

```python
def sair_escopo(self) -> Tuple[int, int]:
    if self.nivel_escopo_atual > 0:
        info_escopo = self.escopos.pop()
        self.nivel_escopo_atual -= 1
        return info_escopo.obter_info_alocacao()
    return (0, 0)
```

**Explicação linha por linha:**
- `if self.nivel_escopo_atual > 0`: Verifica se não está no escopo global
  - Não pode sair do escopo global (nível 0)
- `info_escopo = self.escopos.pop()`: Remove último escopo da lista (LIFO)
  - `pop()` remove e retorna último elemento
  - Escopo mais interno é sempre o último na lista
- `self.nivel_escopo_atual -= 1`: Decrementa nível
- `return info_escopo.obter_info_alocacao()`: Retorna `(endereco_base, quantidade)` para DALLOC
- `return (0, 0)`: Se tentar sair do global, retorna valores neutros

**Modelo de pilha:**
- Escopos são empilhados: entrar = push, sair = pop
- Último a entrar é primeiro a sair (LIFO)
- Garante que símbolos locais são removidos na ordem correta

### Método `declarar` - Análise Detalhada

```python
def declarar(self, nome: str, tipo: str, categoria: str = 'variavel') -> Simbolo:
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
```

**Explicação linha por linha:**

**1. Obter escopo atual:**
- `escopo_atual = self.escopos[self.nivel_escopo_atual]`: Obtém escopo atual da lista
  - `nivel_escopo_atual` é o índice do escopo atual

**2. Verificar duplicidade:**
- `if nome in escopo_atual.simbolos`: Verifica se nome já existe no escopo atual
  - Verifica apenas no escopo atual (permite shadowing entre escopos)
  - `escopo_atual.simbolos` é um dicionário (busca O(1))
- `raise Exception(...)`: Erro se duplicado no mesmo escopo

**3. Alocar endereço (apenas para variáveis):**
- `endereco = None`: Inicializa como None (procedimentos não têm endereço)
- `if categoria == 'variavel'`: Apenas variáveis precisam de endereço
  - `endereco = escopo_atual.endereco_base + escopo_atual.quantidade_variaveis`:
    - Endereço = base do escopo + offset (quantidade de variáveis já alocadas)
    - Primeira variável: offset=0, segunda: offset=1, etc.
  - `escopo_atual.quantidade_variaveis += 1`: Incrementa contador
  - `if endereco >= self.proximo_endereco`: Atualiza próximo endereço global
    - Garante que `proximo_endereco` sempre aponta para próximo endereço livre

**4. Criar símbolo:**
- `Simbolo(...)`: Cria objeto símbolo com todas as informações
  - `nivel_escopo=self.nivel_escopo_atual`: Armazena nível onde foi declarado
  - `endereco_memoria=endereco`: Endereço alocado (None para procedimentos)

**5. Armazenar:**
- `escopo_atual.simbolos[nome] = simbolo`: Adiciona ao dicionário do escopo
  - Chave = nome (permite busca rápida)
  - Valor = objeto Simbolo completo

**Exemplo de alocação:**
```python
# Escopo base=0, quantidade_variaveis=0
tabela.declarar("x", "inteiro")  # endereco = 0 + 0 = 0
# quantidade_variaveis = 1
tabela.declarar("y", "inteiro")  # endereco = 0 + 1 = 1
# quantidade_variaveis = 2
```

### Método `buscar` - Análise Detalhada

```python
def buscar(self, nome: str) -> Optional[Simbolo]:
    """
    Busca um símbolo nos escopos (do mais interno ao mais externo).
    """
    # Procura do escopo mais interno para o mais externo
    for nivel in range(self.nivel_escopo_atual, -1, -1):
        if nome in self.escopos[nivel].simbolos:
            return self.escopos[nivel].simbolos[nome]
    return None
```

**Explicação linha por linha:**
- `for nivel in range(self.nivel_escopo_atual, -1, -1)`: Loop do mais interno ao mais externo
  - `range(inicio, fim, passo)`: 
    - `inicio = nivel_escopo_atual`: Começa no escopo atual (mais interno)
    - `fim = -1`: Para antes de -1 (ou seja, inclui 0)
    - `passo = -1`: Decrementa (vai de maior para menor)
  - Exemplo: se `nivel_escopo_atual=2`, itera: 2, 1, 0
- `if nome in self.escopos[nivel].simbolos`: Verifica se nome existe neste escopo
  - Busca em dicionário é O(1)
- `return self.escopos[nivel].simbolos[nome]`: Retorna símbolo encontrado
  - Retorna primeiro encontrado (mais interno)
- `return None`: Se não encontrou em nenhum escopo

**Shadowing (sombreamento):**
```python
# Escopo 0: x (endereco=0)
# Escopo 1: x (endereco=3)  # Shadowing!
tabela.buscar("x")  # Retorna x do escopo 1 (mais interno)
```

**Por que buscar do interno para externo:**
- Implementa regra de shadowing: símbolo mais interno prevalece
- Segue regras de escopo da linguagem LPD
- Primeiro encontrado é o correto (mais próximo do uso)

### Método `declarar_retorno_funcao` - Análise Detalhada

```python
def declarar_retorno_funcao(self, nome_funcao: str, tipo_retorno: str) -> Simbolo:
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
```

**Explicação:**
- Similar a `declarar()`, mas específico para funções
- **Diferença principal:** `categoria='funcao'` (não `'variavel'`)
- Aloca endereço para valor de retorno (como se fosse variável)
- Endereço é usado quando função retorna valor (`funcao := valor`)

**Por que alocar endereço para retorno:**
- Funções retornam valores através de atribuição ao nome da função
- Precisa de espaço de memória para armazenar valor de retorno
- Endereço é usado pelo gerador de código para `STR endereco_retorno`

### Método `obter_proximo_endereco` - Análise Detalhada

```python
def obter_proximo_endereco(self) -> int:
    """Retorna o próximo endereço disponível (para calcular base de escopo filho)."""
    escopo = self.escopos[self.nivel_escopo_atual]
    return escopo.endereco_base + escopo.quantidade_variaveis
```

**Explicação:**
- `escopo = self.escopos[self.nivel_escopo_atual]`: Obtém escopo atual
- `return escopo.endereco_base + escopo.quantidade_variaveis`: Calcula próximo endereço
  - Se escopo tem base=0 e 3 variáveis, próximo endereço é 3
  - Este será o endereço base do escopo filho

**Uso típico:**
```python
# Escopo atual: base=0, quantidade=2 (endereços 0 e 1 usados)
proximo = tabela.obter_proximo_endereco()  # 2
tabela.entrar_escopo(proximo)  # Novo escopo começa em endereço 2
```

**Por que calcular assim:**
- Garante que escopos não se sobreponham
- Escopo filho começa onde escopo pai termina
- Endereçamento sequencial e contíguo

## Relação com as Notas de Aula

### Estrutura de Registro

Conforme as notas de aula (seção 4.5), cada entrada na tabela deve conter:
- **Nome do identificador** (lexema) → `Simbolo.nome`
- **Escopo** (nível de declaração) → `Simbolo.nivel_escopo`
- **Tipo** (padrão do identificador) → `Simbolo.tipo`
- **Memória** (endereço de memória alocado) → `Simbolo.endereco_memoria`

A implementação adiciona `categoria` para distinguir variáveis, procedimentos e funções.

### Modelo de Escopos

A implementação utiliza o **modelo de pilha** descrito nas notas de aula (seção 4.4):
- Escopos são organizados como uma pilha
- Ao entrar em escopo, adiciona à pilha
- Ao sair de escopo, remove da pilha
- Busca é feita do mais interno para o mais externo

### Visibilidade

Conforme as notas de aula (seção 4.3):
- Símbolos locais são visíveis apenas em seu escopo
- Símbolos externos são visíveis em escopos internos
- Shadowing: definição mais interna prevalece

A implementação garante isso através da busca do mais interno para o mais externo em `buscar()`.

### Endereçamento por Escopo

A implementação segue o modelo descrito nas notas de aula para geração de código:
- Cada escopo tem um endereço base
- Variáveis são alocadas sequencialmente a partir do endereço base
- Endereço base do escopo filho = último endereço usado pelo escopo pai + 1

Isso permite gerar instruções ALLOC/DALLOC corretas para cada escopo.

