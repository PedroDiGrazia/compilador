# Máquina Virtual Didática (MVD) - Documentação

## Introdução e Teoria

### Base Teórica

A **Máquina Virtual Didática (MVD)** é uma máquina hipotética projetada para executar código assembly gerado pelo compilador LPD. Conforme as notas de aula (seção 7), a MVD foi criada para simplificar a geração de código, evitando as complexidades de máquinas reais.

#### Características da MVD

Segundo as notas de aula (seção 7.1):
- **Máquina a pilha**: Utiliza pilha para avaliação de expressões e gerenciamento de memória
- **Duas regiões de memória**:
  - **P (Programa)**: Contém instruções
  - **M (Dados)**: Pilha de valores
- **Dois registradores**:
  - **i**: Endereço da próxima instrução (program counter)
  - **s**: Topo da pilha (stack pointer)

### Arquitetura da MVD

A MVD é uma **máquina a pilha** porque:
- LPD permite procedimentos recursivos
- Recursão está intimamente ligada ao uso de pilha
- Avaliação de expressões é natural em máquina a pilha

## Estrutura do Código

### Classe Principal: `MaquinaVirtual`

A classe `MaquinaVirtual` implementa a execução da MVD.

#### Atributos da Classe

```python
def __init__(self, tamanho_pilha: int = 10000):
    self.M: List[int] = [0] * tamanho_pilha    # Memória de dados (pilha)
    self.P: List[Tuple[str, List]] = []         # Memória de programa (instruções)
    self.labels: dict = {}                      # Labels para desvios
    self.i: int = 0                             # Program counter
    self.s: int = -1                            # Stack pointer
    self.executando: bool = False               # Estado de execução
    self.debug: bool = False                    # Modo debug
```

**Estrutura:**
- `M`: Array de inteiros representando a pilha de dados
- `P`: Lista de tuplas `(instrucao, operandos)` representando o programa
- `labels`: Dicionário mapeando nomes de rótulos para endereços
- `i`: Registrador de programa (endereço da próxima instrução)
- `s`: Registrador de pilha (índice do topo, -1 = pilha vazia)
- `executando`: Flag de controle de execução
- `debug`: Flag para modo debug (imprime estado)

### Métodos Principais

#### `carregar_programa(arquivo_asm: str)`

Carrega programa assembly na memória de programa.

**Parâmetros:**
- `arquivo_asm`: Caminho do arquivo .obj ou .asm

**Processo:**
1. Lê arquivo linha por linha
2. Ignora linhas vazias e comentários (`#` ou `;`)
3. Processa rótulos (formato: `LABEL:` ou `LABEL NULL`)
4. Parseia instruções e operandos
5. Armazena em `P` e atualiza `labels`

**Formato de rótulo:**
- `LABEL:` (com dois pontos)
- `LABEL NULL` (rótulo seguido de NULL)

**Formato de instrução:**
- `INSTRUCAO operando1 operando2`
- Operandos podem ser separados por espaço ou vírgula

#### `executar(entrada: Optional[List[int]] = None, debug: bool = False) -> List[int]`

Executa o programa carregado.

**Parâmetros:**
- `entrada`: Lista de valores inteiros para leitura (opcional)
- `debug`: Se `True`, imprime estado a cada instrução

**Retorno:** Lista de valores impressos (saída do programa)

**Processo:**
1. Inicializa registradores (`i=0`, `s=-1`)
2. Loop principal:
   - Lê instrução atual `P[i]`
   - Se debug, imprime estado
   - Executa instrução (`_executar_instrucao`)
   - Continua até `executando=False` ou fim do programa
3. Retorna lista de saída

## Detalhamento das Instruções

### Instruções de Controle

#### `START`

Inicializa programa.

**Efeito:** `s := -1` (pilha vazia), `i := i + 1`

**Uso:** Primeira instrução do programa.

#### `HLT`

Para execução.

**Efeito:** `executando := False`

**Uso:** Última instrução do programa.

#### `NULL`

Marcador de rótulo (não faz nada).

**Efeito:** `i := i + 1`

**Uso:** Marca posição de rótulo.

### Instruções de Memória

#### `ALLOC m,n`

Aloca n posições a partir de m.

**Efeito:**
```
Para k de 0 até n-1:
    s := s + 1
    M[s] := M[m + k]
```

**Uso:** Alocar memória para variáveis de um escopo.

#### `DALLOC m,n`

Desaloca n posições.

**Efeito:**
```
Para k de n-1 até 0:
    M[m + k] := M[s]
    s := s - 1
```

**Uso:** Desalocar memória ao sair de escopo.

### Instruções de Carga

#### `LDC k`

Carrega constante k na pilha.

**Efeito:** `s := s + 1`, `M[s] := k`

**Uso:** Carregar literais (números, booleanos).

#### `LDV n`

Carrega valor de M[n] na pilha.

**Efeito:** `s := s + 1`, `M[s] := M[n]`

**Uso:** Carregar valor de variável.

#### `STR n`

Armazena valor do topo da pilha em M[n].

**Efeito:** `M[n] := M[s]`, `s := s - 1`

**Uso:** Armazenar em variável ou retorno de função.

### Instruções Aritméticas

#### `ADD`

Adição: `M[s-1] := M[s-1] + M[s]`, `s := s - 1`

#### `SUB`

Subtração: `M[s-1] := M[s-1] - M[s]`, `s := s - 1`

#### `MULT`

Multiplicação: `M[s-1] := M[s-1] * M[s]`, `s := s - 1`

#### `DIVI`

Divisão inteira: `M[s-1] := M[s-1] // M[s]`, `s := s - 1`

**Erro:** Se `M[s] == 0` (divisão por zero)

#### `INV`

Inverte sinal: `M[s] := -M[s]`

**Uso:** Operador unário `-`.

### Instruções Lógicas

#### `AND`

Conjunção: Se `M[s-1]==1` e `M[s]==1` então `M[s-1]:=1` senão `M[s-1]:=0`, `s := s - 1`

#### `OR`

Disjunção: Se `M[s-1]==1` ou `M[s]==1` então `M[s-1]:=1` senão `M[s-1]:=0`, `s := s - 1`

#### `NEG`

Negação: `M[s] := 1 - M[s]`

**Uso:** Operador unário `nao`.

### Instruções de Comparação

#### `CME`

Comparar menor: Se `M[s-1] < M[s]` então `M[s-1]:=1` senão `M[s-1]:=0`, `s := s - 1`

#### `CMA`

Comparar maior: Se `M[s-1] > M[s]` então `M[s-1]:=1` senão `M[s-1]:=0`, `s := s - 1`

#### `CEQ`

Comparar igual: Se `M[s-1] == M[s]` então `M[s-1]:=1` senão `M[s-1]:=0`, `s := s - 1`

#### `CDIF`

Comparar diferente: Se `M[s-1] != M[s]` então `M[s-1]:=1` senão `M[s-1]:=0`, `s := s - 1`

#### `CMEQ`

Comparar menor ou igual: Se `M[s-1] <= M[s]` então `M[s-1]:=1` senão `M[s-1]:=0`, `s := s - 1`

#### `CMAQ`

Comparar maior ou igual: Se `M[s-1] >= M[s]` então `M[s-1]:=1` senão `M[s-1]:=0`, `s := s - 1`

### Instruções de Desvio

#### `JMP p`

Desvio incondicional para rótulo p.

**Efeito:** `i := endereco_do_rotulo`

**Uso:** Desvios incondicionais, loops.

#### `JMPF p`

Desvio se falso: Se `M[s] == 0` então `i := endereco_do_rotulo` senão `i := i + 1`, `s := s - 1`

**Uso:** Comandos condicionais (`se`, `enquanto`).

### Instruções de I/O

#### `RD`

Leitura: Lê valor inteiro e coloca no topo da pilha.

**Efeito:** `s := s + 1`, `M[s] := valor_lido`

**Processo:**
1. Se houver entrada fornecida, usa próximo valor
2. Caso contrário, lê da entrada padrão (`input()`)

**Uso:** Comando `leia()`.

#### `PRN`

Impressão: Imprime valor do topo da pilha.

**Efeito:** `print(M[s])`, `s := s - 1`, adiciona à lista de saída

**Uso:** Comando `escreva()`.

### Instruções de Subrotinas

#### `CALL p`

Chama procedimento/função no rótulo p.

**Efeito:**
```
s := s + 1
M[s] := i + 1  (endereço de retorno)
i := endereco_do_rotulo
```

**Uso:** Chamada de procedimento ou função.

#### `RETURN`

Retorna de procedimento.

**Efeito:** `i := M[s]`, `s := s - 1`

**Uso:** Final de procedimento ou função.

#### `RETURNF`

Retorna de função com valor (não usado na implementação atual).

**Nota:** A implementação atual usa `RETURN` para funções também, pois o valor de retorno já foi armazenado antes do RETURN.

## Integração

### Uso pelo Compilador

O código gerado pelo `GeradorCodigo` é salvo em arquivo `.obj` e executado pela MVD:

```python
gerador = GeradorCodigo()
instrucoes = gerador.gerar(ast, tabela_simbolos)
gerador.salvar_em_arquivo("programa.obj")

mv = MaquinaVirtual()
mv.carregar_programa("programa.obj")
saida = mv.executar(entrada=[10, 20], debug=False)
```

### Uso pela Interface Gráfica

A `interface.py` utiliza a MVD para execução interativa:
- Carrega programa compilado
- Executa instrução por instrução
- Trata `RD` de forma interativa (aguarda entrada do usuário)
- Exibe saída de `PRN` na interface

## Exemplos Práticos

### Exemplo 1: Execução Simples

```python
from maquina_virtual import MaquinaVirtual

# Programa: LDC 5; PRN; HLT
mv = MaquinaVirtual()
mv.P = [
    ("START", []),
    ("LDC", [5]),
    ("PRN", []),
    ("HLT", [])
]

saida = mv.executar()
print(saida)  # [5]
```

### Exemplo 2: Expressão Aritmética

```python
# Programa: LDC 10; LDC 5; ADD; PRN; HLT
mv = MaquinaVirtual()
mv.P = [
    ("START", []),
    ("LDC", [10]),
    ("LDC", [5]),
    ("ADD", []),
    ("PRN", []),
    ("HLT", [])
]

saida = mv.executar()
print(saida)  # [15]
```

### Exemplo 3: Comando Condicional

```python
# Programa: LDC 1; JMPF L_fim; LDC 42; PRN; L_fim NULL; HLT
mv = MaquinaVirtual()
mv.P = [
    ("START", []),
    ("LDC", [1]),      # Verdadeiro
    ("JMPF", ["L_fim"]),
    ("LDC", [42]),
    ("PRN", []),
    ("NULL", []),      # L_fim
    ("HLT", [])
]
mv.labels = {"L_fim": 5}

saida = mv.executar()
print(saida)  # [42]
```

### Exemplo 4: Modo Debug

```python
mv = MaquinaVirtual()
mv.carregar_programa("programa.obj")
saida = mv.executar(debug=True)
```

**Saída (exemplo):**
```
[  0] START     [] | s=-1 | M[s]=N/A
[  1] LDC       [5] | s=0 | M[s]=5
[  2] PRN       [] | s=0 | M[s]=5
5
[  3] HLT       [] | s=-1 | M[s]=N/A
```

## Análise Detalhada do Código

### Método `_executar_instrucao` - Análise Detalhada

Este método é o núcleo da máquina virtual, executando cada instrução individualmente.

#### Instrução `LDC` (Carregar Constante)

```python
elif instr == 'LDC':
    if len(ops) != 1:
        raise ErroMVD(f"LDC espera 1 operando")
    self.s += 1
    if self.s >= len(self.M):
        raise ErroMVD("Stack overflow")
    self.M[self.s] = ops[0]
    self.i += 1
```

**Explicação linha por linha:**
- `if len(ops) != 1`: Valida que há exatamente 1 operando (a constante)
- `self.s += 1`: Incrementa topo da pilha (prepara espaço)
- `if self.s >= len(self.M)`: Verifica overflow (pilha cheia)
- `self.M[self.s] = ops[0]`: Armazena constante no topo da pilha
- `self.i += 1`: Avança para próxima instrução

**Estado da pilha:**
```
Antes: s = 2, M[2] = valor_anterior
Depois: s = 3, M[3] = constante
```

#### Instrução `LDV` (Carregar Valor)

```python
elif instr == 'LDV':
    if len(ops) != 1:
        raise ErroMVD(f"LDV espera 1 operando")
    self.s += 1
    if self.s >= len(self.M):
        raise ErroMVD("Stack overflow")
    self.M[self.s] = self.M[ops[0]]
    self.i += 1
```

**Explicação linha por linha:**
- `self.s += 1`: Incrementa topo da pilha
- `self.M[self.s] = self.M[ops[0]]`: Copia valor de `M[endereco]` para topo
  - `ops[0]` é o endereço da variável
  - `M[ops[0]]` é o valor armazenado naquele endereço
- `self.i += 1`: Avança

**Exemplo:**
```python
# M[5] = 42 (variável x está no endereço 5)
# LDV 5
# Depois: M[s] = 42 (valor copiado para topo)
```

#### Instrução `STR` (Armazenar)

```python
elif instr == 'STR':
    if len(ops) != 1:
        raise ErroMVD(f"STR espera 1 operando")
    if self.s < 0:
        raise ErroMVD("Stack underflow")
    self.M[ops[0]] = self.M[self.s]
    self.s -= 1
    self.i += 1
```

**Explicação linha por linha:**
- `if self.s < 0`: Verifica se pilha não está vazia
- `self.M[ops[0]] = self.M[self.s]`: Copia valor do topo para endereço
  - `M[self.s]` é valor no topo da pilha
  - `M[ops[0]]` é endereço de destino
- `self.s -= 1`: Decrementa topo (remove valor da pilha)
- `self.i += 1`: Avança

**Estado da pilha:**
```
Antes: s = 3, M[3] = valor, M[5] = antigo_valor
STR 5
Depois: s = 2, M[5] = valor (atualizado), M[3] ainda tem valor (mas não é mais topo)
```

#### Instrução `ADD` (Adição)

```python
elif instr == 'ADD':
    if self.s < 1:
        raise ErroMVD("Stack underflow em ADD")
    self.M[self.s - 1] = self.M[self.s - 1] + self.M[self.s]
    self.s -= 1
    self.i += 1
```

**Explicação linha por linha:**
- `if self.s < 1`: Verifica se há pelo menos 2 valores na pilha
  - Precisa de 2 operandos (s-1 e s)
- `self.M[self.s - 1] = self.M[self.s - 1] + self.M[self.s]`: 
  - Soma valores: `M[s-1]` (operando esquerdo) + `M[s]` (operando direito)
  - Armazena resultado em `M[s-1]` (substitui operando esquerdo)
- `self.s -= 1`: Decrementa topo (remove operando direito)
  - Resultado fica no novo topo (`M[s-1]` que agora é `M[s]`)

**Estado da pilha:**
```
Antes: s = 3
  M[2] = 10  (operando esquerdo)
  M[3] = 5   (operando direito, topo)
ADD
Depois: s = 2
  M[2] = 15  (resultado, agora topo)
  M[3] = 5   (ainda existe, mas não é mais topo)
```

**Por que armazenar em s-1:**
- Resultado substitui operando esquerdo
- Operando direito é removido (s decrementado)
- Resultado fica no topo após operação

#### Instrução `JMPF` (Desvio Se Falso)

```python
elif instr == 'JMPF':
    if len(ops) != 1:
        raise ErroMVD(f"JMPF espera 1 operando")
    if self.s < 0:
        raise ErroMVD("Stack underflow em JMPF")
    
    label = ops[0]
    if self.M[self.s] == 0:
        # Tenta buscar como string primeiro
        label_str = str(label)
        if label_str in self.labels:
            self.i = self.labels[label_str]
        elif isinstance(label, str) and label in self.labels:
            self.i = self.labels[label]
        else:
            self.i = int(label) if isinstance(label, str) else label
    else:
        self.i += 1
    self.s -= 1
```

**Explicação linha por linha:**
- `if self.s < 0`: Verifica se há valor no topo
- `label = ops[0]`: Obtém rótulo de destino
- `if self.M[self.s] == 0`: Verifica se valor no topo é falso (0)
  - `0` = falso, qualquer outro valor = verdadeiro
- **Se falso (pula):**
  - `label_str = str(label)`: Converte rótulo para string
  - `if label_str in self.labels`: Verifica se rótulo existe no dicionário
    - `self.i = self.labels[label_str]`: Define program counter para rótulo
  - `elif isinstance(label, str) and label in self.labels`: Tenta como string diretamente
  - `else`: Assume que é endereço direto (número)
- **Se verdadeiro (não pula):**
  - `self.i += 1`: Avança normalmente
- `self.s -= 1`: Sempre remove valor do topo (foi consumido)

**Exemplo:**
```python
# Pilha: M[s] = 0 (falso)
# JMPF L_fim
# Se M[s] == 0: i = endereco_de_L_fim (pula)
# Se M[s] != 0: i = i + 1 (continua)
# Sempre: s = s - 1 (remove valor)
```

#### Instrução `CALL` (Chamar Subrotina)

```python
elif instr == 'CALL':
    if len(ops) != 1:
        raise ErroMVD(f"CALL espera 1 operando")
    self.s += 1
    if self.s >= len(self.M):
        raise ErroMVD("Stack overflow")
    self.M[self.s] = self.i + 1
    
    label = ops[0]
    # Tenta buscar como string primeiro
    label_str = str(label)
    if label_str in self.labels:
        self.i = self.labels[label_str]
    elif isinstance(label, str) and label in self.labels:
        self.i = self.labels[label]
    else:
        self.i = int(label) if isinstance(label, str) else label
```

**Explicação linha por linha:**
- `self.s += 1`: Incrementa topo da pilha
- `self.M[self.s] = self.i + 1`: Armazena endereço de retorno no topo
  - `self.i + 1` é a próxima instrução após CALL
  - Será usado por RETURN para voltar
- **Buscar rótulo:** Similar a JMP, busca rótulo e define `self.i`

**Estado da pilha:**
```
Antes CALL: s = 5, i = 10
CALL L_func
Depois: s = 6, M[6] = 11 (endereço de retorno), i = endereco_L_func
```

**Por que armazenar endereço de retorno:**
- RETURN precisa saber para onde voltar
- Endereço é empilhado antes de desviar
- RETURN desempilha e usa como novo `i`

#### Instrução `RETURN` (Retornar)

```python
elif instr == 'RETURN':
    if self.s < 0:
        raise ErroMVD("Stack underflow em RETURN")
    self.i = self.M[self.s]
    self.s -= 1
```

**Explicação linha por linha:**
- `if self.s < 0`: Verifica se há endereço de retorno na pilha
- `self.i = self.M[self.s]`: Define program counter para endereço de retorno
  - `M[s]` contém endereço empilhado pelo CALL
- `self.s -= 1`: Remove endereço da pilha

**Fluxo completo CALL/RETURN:**
```
# Instrução 10: CALL L_func
#   s=5 → s=6, M[6]=11, i=endereco_L_func

# [executa função]

# Instrução no final da função: RETURN
#   i=M[6]=11, s=6 → s=5
# Continua execução na instrução 11
```

#### Instrução `ALLOC` - Análise Detalhada

```python
elif instr == 'ALLOC':
    if len(ops) != 2:
        raise ErroMVD(f"ALLOC espera 2 operandos, recebeu {len(ops)}")
    m, n = ops[0], ops[1]
    for k in range(n):
        self.s += 1
        if self.s >= len(self.M):
            raise ErroMVD("Stack overflow")
        self.M[self.s] = self.M[m + k]
    self.i += 1
```

**Explicação linha por linha:**
- `m, n = ops[0], ops[1]`: `m` = endereço base, `n` = quantidade
- `for k in range(n)`: Loop para alocar n posições
  - `k` vai de 0 até n-1
- `self.s += 1`: Incrementa topo (aloca nova posição)
- `if self.s >= len(self.M)`: Verifica overflow
- `self.M[self.s] = self.M[m + k]`: Copia valor de `M[m+k]` para topo
  - Inicialmente `M[m+k]` pode ser 0 ou valor anterior
  - Após ALLOC, valores ficam na pilha

**Exemplo:**
```python
# ALLOC 0 3 (aloca 3 posições a partir de 0)
# Antes: s = 5, M[0]=0, M[1]=0, M[2]=0
# k=0: s=6, M[6]=M[0]=0
# k=1: s=7, M[7]=M[1]=0
# k=2: s=8, M[8]=M[2]=0
# Depois: s = 8, 3 posições alocadas na pilha
```

**Por que copiar de M[m+k]:**
- Inicializa variáveis com valores existentes (ou 0)
- Permite inicialização de variáveis locais com valores do escopo pai

#### Instrução `DALLOC` - Análise Detalhada

```python
elif instr == 'DALLOC':
    if len(ops) != 2:
        raise ErroMVD(f"DALLOC espera 2 operandos, recebeu {len(ops)}")
    m, n = ops[0], ops[1]
    for k in range(n - 1, -1, -1):
        if self.s < 0:
            raise ErroMVD("Stack underflow")
        self.M[m + k] = self.M[self.s]
        self.s -= 1
    self.i += 1
```

**Explicação linha por linha:**
- `m, n = ops[0], ops[1]`: `m` = endereço base, `n` = quantidade
- `for k in range(n - 1, -1, -1)`: Loop de n-1 até 0 (ordem inversa!)
  - `range(n-1, -1, -1)`: Decrementa (ex: se n=3, k = 2, 1, 0)
- `if self.s < 0`: Verifica se há valores na pilha
- `self.M[m + k] = self.M[self.s]`: Copia valor do topo para `M[m+k]`
  - Salva valores de volta nas posições originais
- `self.s -= 1`: Decrementa topo (remove valor da pilha)

**Por que ordem inversa:**
- Valores foram empilhados na ordem 0, 1, 2, ...
- Topo da pilha tem último valor (índice n-1)
- Desempilha do último para o primeiro (ordem inversa)

**Exemplo:**
```python
# DALLOC 0 3 (desaloca 3 posições)
# Antes: s = 8, M[6]=valor0, M[7]=valor1, M[8]=valor2
# k=2: M[0+2]=M[8]=valor2, s=8 → s=7
# k=1: M[0+1]=M[7]=valor1, s=7 → s=6
# k=0: M[0+0]=M[6]=valor0, s=6 → s=5
# Depois: s = 5, valores salvos em M[0], M[1], M[2]
```

#### Instrução `SUB` (Subtração)

```python
elif instr == 'SUB':
    if self.s < 1:
        raise ErroMVD("Stack underflow em SUB")
    self.M[self.s - 1] = self.M[self.s - 1] - self.M[self.s]
    self.s -= 1
    self.i += 1
```

**Explicação:**
- Similar a `ADD`, mas realiza subtração: `M[s-1] - M[s]`
- Resultado armazenado em `M[s-1]`, operando direito removido

#### Instrução `MULT` (Multiplicação)

```python
elif instr == 'MULT':
    if self.s < 1:
        raise ErroMVD("Stack underflow em MULT")
    self.M[self.s - 1] = self.M[self.s - 1] * self.M[self.s]
    self.s -= 1
    self.i += 1
```

**Explicação:**
- Multiplica: `M[s-1] * M[s]`
- Resultado em `M[s-1]`, topo decrementado

#### Instrução `DIVI` (Divisão Inteira)

```python
elif instr == 'DIVI':
    if self.s < 1:
        raise ErroMVD("Stack underflow em DIVI")
    if self.M[self.s] == 0:
        raise ErroMVD("Divisão por zero")
    self.M[self.s - 1] = self.M[self.s - 1] // self.M[self.s]
    self.s -= 1
    self.i += 1
```

**Explicação:**
- Divide: `M[s-1] // M[s]` (divisão inteira)
- **Verifica divisão por zero** antes de executar
- Usa `//` (divisão inteira Python)

#### Instrução `INV` (Inverter Sinal)

```python
elif instr == 'INV':
    if self.s < 0:
        raise ErroMVD("Stack underflow em INV")
    self.M[self.s] = -self.M[self.s]
    self.i += 1
```

**Explicação:**
- Operação unária: inverte sinal do topo
- `M[s] = -M[s]`
- Não decrementa `s` (apenas 1 operando)

#### Instrução `AND` (Conjunção Lógica)

```python
elif instr == 'AND':
    if self.s < 1:
        raise ErroMVD("Stack underflow em AND")
    self.M[self.s - 1] = 1 if (self.M[self.s - 1] == 1 and self.M[self.s] == 1) else 0
    self.s -= 1
    self.i += 1
```

**Explicação:**
- Operação lógica: `M[s-1] AND M[s]`
- Resultado: `1` se ambos são `1`, senão `0`
- Usa comparação explícita (`== 1`) para garantir valores booleanos

#### Instrução `OR` (Disjunção Lógica)

```python
elif instr == 'OR':
    if self.s < 1:
        raise ErroMVD("Stack underflow em OR")
    self.M[self.s - 1] = 1 if (self.M[self.s - 1] == 1 or self.M[self.s] == 1) else 0
    self.s -= 1
    self.i += 1
```

**Explicação:**
- Operação lógica: `M[s-1] OR M[s]`
- Resultado: `1` se qualquer um é `1`, senão `0`

#### Instrução `NEG` (Negação Lógica)

```python
elif instr == 'NEG':
    if self.s < 0:
        raise ErroMVD("Stack underflow em NEG")
    self.M[self.s] = 1 - self.M[self.s]
    self.i += 1
```

**Explicação:**
- Operação unária: negação lógica
- `M[s] = 1 - M[s]` (inverte: 0→1, 1→0)
- Não decrementa `s`

#### Instrução `CME` (Comparar Menor)

```python
elif instr == 'CME':
    if self.s < 1:
        raise ErroMVD("Stack underflow em CME")
    self.M[self.s - 1] = 1 if self.M[self.s - 1] < self.M[self.s] else 0
    self.s -= 1
    self.i += 1
```

**Explicação:**
- Compara: `M[s-1] < M[s]`
- Resultado: `1` se verdadeiro, `0` se falso
- Decrementa `s` (consome 2 operandos, deixa 1 resultado)

#### Instrução `CMA` (Comparar Maior)

```python
elif instr == 'CMA':
    if self.s < 1:
        raise ErroMVD("Stack underflow em CMA")
    self.M[self.s - 1] = 1 if self.M[self.s - 1] > self.M[self.s] else 0
    self.s -= 1
    self.i += 1
```

**Explicação:**
- Compara: `M[s-1] > M[s]`
- Similar a `CME`, mas operador `>`

#### Instrução `CEQ` (Comparar Igual)

```python
elif instr == 'CEQ':
    if self.s < 1:
        raise ErroMVD("Stack underflow em CEQ")
    self.M[self.s - 1] = 1 if self.M[self.s - 1] == self.M[self.s] else 0
    self.s -= 1
    self.i += 1
```

**Explicação:**
- Compara: `M[s-1] == M[s]`
- Resultado booleano no topo

#### Instrução `CDIF` (Comparar Diferente)

```python
elif instr == 'CDIF':
    if self.s < 1:
        raise ErroMVD("Stack underflow em CDIF")
    self.M[self.s - 1] = 1 if self.M[self.s - 1] != self.M[self.s] else 0
    self.s -= 1
    self.i += 1
```

**Explicação:**
- Compara: `M[s-1] != M[s]`
- Resultado `1` se diferentes, `0` se iguais

#### Instrução `CMEQ` (Comparar Menor ou Igual)

```python
elif instr == 'CMEQ':
    if self.s < 1:
        raise ErroMVD("Stack underflow em CMEQ")
    self.M[self.s - 1] = 1 if self.M[self.s - 1] <= self.M[self.s] else 0
    self.s -= 1
    self.i += 1
```

**Explicação:**
- Compara: `M[s-1] <= M[s]`
- Combinação de `<` ou `==`

#### Instrução `CMAQ` (Comparar Maior ou Igual)

```python
elif instr == 'CMAQ':
    if self.s < 1:
        raise ErroMVD("Stack underflow em CMAQ")
    self.M[self.s - 1] = 1 if self.M[self.s - 1] >= self.M[self.s] else 0
    self.s -= 1
    self.i += 1
```

**Explicação:**
- Compara: `M[s-1] >= M[s]`
- Combinação de `>` ou `==`

#### Instrução `JMP` (Desvio Incondicional)

```python
elif instr == 'JMP':
    if len(ops) != 1:
        raise ErroMVD(f"JMP espera 1 operando")
    label = ops[0]
    label_str = str(label)
    if label_str in self.labels:
        self.i = self.labels[label_str]
    elif isinstance(label, str) and label in self.labels:
        self.i = self.labels[label]
    else:
        self.i = int(label) if isinstance(label, str) else label
```

**Explicação:**
- Desvio incondicional (sempre pula)
- Busca rótulo similar a `JMPF`, mas não verifica condição
- Não consome valor da pilha (diferente de `JMPF`)

#### Instrução `NULL` (Marcador de Rótulo)

```python
elif instr == 'NULL':
    self.i += 1
```

**Explicação:**
- Instrução vazia (não faz nada)
- Usada como marcador de rótulo quando rótulo está na mesma linha da instrução
- Apenas avança para próxima instrução

#### Instrução `RD` (Leitura)

```python
elif instr == 'RD':
    self.s += 1
    if self.s >= len(self.M):
        raise ErroMVD("Stack overflow")
    
    if self.indice_entrada < len(self.entrada):
        self.M[self.s] = self.entrada[self.indice_entrada]
        self.indice_entrada += 1
    else:
        try:
            valor = int(input("Digite um valor inteiro: "))
            self.M[self.s] = valor
        except ValueError:
            raise ErroMVD("Entrada inválida: esperado inteiro")
    self.i += 1
```

**Explicação linha por linha:**
- `self.s += 1`: Incrementa topo (prepara espaço)
- `if self.indice_entrada < len(self.entrada)`: Verifica se há entrada fornecida
  - `self.M[self.s] = self.entrada[self.indice_entrada]`: Usa valor da lista
  - `self.indice_entrada += 1`: Avança índice
- `else`: Se não há entrada fornecida
  - `valor = int(input(...))`: Lê da entrada padrão
  - `self.M[self.s] = valor`: Armazena no topo
- `self.i += 1`: Avança

**Por que duas formas de entrada:**
- Lista de entrada: permite execução automatizada (testes)
- `input()`: permite execução interativa

#### Instrução `PRN` (Impressão)

```python
elif instr == 'PRN':
    if self.s < 0:
        raise ErroMVD("Stack underflow em PRN")
    print(self.M[self.s])
    self.saida.append(self.M[self.s])
    self.s -= 1
    self.i += 1
```

**Explicação linha por linha:**
- `if self.s < 0`: Verifica se pilha não está vazia
- `print(self.M[self.s])`: Imprime valor no terminal
- `self.saida.append(self.M[self.s])`: Adiciona à lista de saída
  - Lista é retornada por `executar()` para uso programático
- `self.s -= 1`: Remove valor da pilha
- `self.i += 1`: Avança

#### Instrução `RETURNF` (Retornar de Função com Valor)

```python
elif instr == 'RETURNF':
    if self.s < 1:
        raise ErroMVD("Stack underflow em RETURNF")
    valor_retorno = self.M[self.s]
    endereco_retorno = self.M[self.s - 1]
    self.M[self.s - 1] = valor_retorno
    self.s -= 1
    self.i = endereco_retorno
```

**Explicação linha por linha:**
- `if self.s < 1`: Verifica se há pelo menos 2 valores (endereço + valor)
- `valor_retorno = self.M[self.s]`: Obtém valor de retorno (topo)
- `endereco_retorno = self.M[self.s - 1]`: Obtém endereço de retorno
- `self.M[self.s - 1] = valor_retorno`: Move valor para posição do endereço
  - Valor fica no topo após remover endereço
- `self.s -= 1`: Remove endereço (valor fica no topo)
- `self.i = endereco_retorno`: Volta para ponto de chamada

**Convenção:**
- Antes de `RETURNF`: `M[s-1]` = endereço, `M[s]` = valor
- Depois: `M[s-1]` = valor (novo topo), `i` = endereço

**Nota:** Esta instrução não é usada na implementação atual (funções usam `RETURN` após armazenar valor).

#### Instrução `HLT` (Parar Execução)

```python
elif instr == 'HLT':
    self.executando = False
```

**Explicação:**
- Para execução do programa
- Define `executando = False`
- Loop principal em `executar()` verifica essa flag e para
- Não avança `i` (programa terminou)

#### Instrução `START` (Inicializar)

```python
if instr == 'START':
    self.s = -1
    self.i += 1
```

**Explicação:**
- Primeira instrução do programa
- `self.s = -1`: Inicializa stack pointer (pilha vazia)
- `self.i += 1`: Avança para próxima instrução

### Método `__init__` - Análise Detalhada

```python
def __init__(self, tamanho_pilha: int = 10000):
    self.M: List[int] = [0] * tamanho_pilha
    self.P: List[Tuple[str, List]] = []
    self.labels: dict = {}
    self.i: int = 0
    self.s: int = -1
    self.executando: bool = False
    self.debug: bool = False
```

**Explicação linha por linha:**
- `tamanho_pilha: int = 10000`: Tamanho padrão da memória (configurável)
- `self.M: List[int] = [0] * tamanho_pilha`: Inicializa memória com zeros
  - `[0] * tamanho_pilha` cria lista com 10000 zeros
- `self.P: List[Tuple[str, List]] = []`: Memória de programa vazia
  - Cada tupla: `(instrucao, operandos)`
- `self.labels: dict = {}`: Dicionário de rótulos (vazio inicialmente)
- `self.i: int = 0`: Program counter (começa em 0)
- `self.s: int = -1`: Stack pointer (pilha vazia = -1)
- `self.executando: bool = False`: Flag de controle
- `self.debug: bool = False`: Modo debug desativado

### Método `carregar_programa` - Análise Detalhada

```python
def carregar_programa(self, arquivo_asm: str):
    with open(arquivo_asm, 'r', encoding='utf-8') as f:
        linhas = f.readlines()
    
    endereco = 0
    for num_linha, linha in enumerate(linhas, 1):
        linha = linha.strip()
        
        # Ignora linhas vazias e comentários
        if not linha or linha.startswith('#') or linha.startswith(';'):
            continue
        
        # Remove comentários inline
        if '#' in linha:
            linha = linha[:linha.index('#')].strip()
        if ';' in linha:
            linha = linha[:linha.index(';')].strip()
        
        # Processa labels (formato: "LABEL:" ou "LABEL NULL")
        if linha.endswith(':'):
            label = linha[:-1]
            self.labels[label] = endereco
            continue
        
        # Parseia instrução
        partes = linha.split()
        if not partes:
            continue
        
        # Verifica se é um label seguido de instrução
        if len(partes) >= 2 and not partes[0].upper() in [...]:
            label = partes[0]
            self.labels[label] = endereco
            partes = partes[1:]
        
        instrucao = partes[0].upper()
        operandos = []
        
        # Processa operandos
        if len(partes) > 1:
            resto = ' '.join(partes[1:])
            if ',' in resto:
                ops_list = resto.split(',')
            else:
                ops_list = resto.split()
            
            for op in ops_list:
                op = op.strip()
                if op:
                    try:
                        operandos.append(int(op))
                    except ValueError:
                        operandos.append(op)
        
        self.P.append((instrucao, operandos))
        endereco += 1
```

**Explicação linha por linha:**

**1. Leitura do arquivo:**
- `with open(...)`: Abre arquivo assembly
- `f.readlines()`: Lê todas as linhas

**2. Processamento de cada linha:**
- `endereco = 0`: Contador de endereços (índice na memória P)
- `linha.strip()`: Remove espaços no início/fim

**3. Ignorar comentários e linhas vazias:**
- `if not linha`: Linha vazia
- `linha.startswith('#')` ou `linha.startswith(';')`: Comentário no início
- `continue`: Pula para próxima linha

**4. Remover comentários inline:**
- `if '#' in linha`: Encontra `#` na linha
- `linha[:linha.index('#')]`: Pega parte antes do `#`
- Similar para `;`

**5. Processar rótulos:**
- `if linha.endswith(':')`: Rótulo na forma `LABEL:`
- `label = linha[:-1]`: Remove `:`
- `self.labels[label] = endereco`: Armazena endereço do rótulo
- `continue`: Não adiciona instrução (rótulo não é instrução)

**6. Parsear instrução:**
- `partes = linha.split()`: Divide linha em palavras
- `if not partes`: Se vazio, pula

**7. Verificar rótulo + instrução:**
- `if len(partes) >= 2 and not partes[0].upper() in [...]`: 
  - Se primeira palavra não é instrução conhecida, é rótulo
- `label = partes[0]`: Primeira palavra é rótulo
- `self.labels[label] = endereco`: Armazena rótulo
- `partes = partes[1:]`: Remove rótulo, mantém instrução

**8. Extrair instrução e operandos:**
- `instrucao = partes[0].upper()`: Primeira palavra (maiúscula)
- `operandos = []`: Lista vazia

**9. Processar operandos:**
- `if len(partes) > 1`: Se há operandos
- `resto = ' '.join(partes[1:])`: Junta operandos em string
- `if ',' in resto`: Separa por vírgula OU espaço
- `for op in ops_list`: Itera operandos
- `try: int(op)`: Tenta converter para inteiro
  - Se sucesso: adiciona inteiro
  - Se falha: mantém como string (rótulo)

**10. Adicionar à memória:**
- `self.P.append((instrucao, operandos))`: Adiciona tupla
- `endereco += 1`: Incrementa contador

### Método `executar` - Análise Detalhada

```python
def executar(self, entrada: Optional[List[int]] = None, debug: bool = False):
    self.debug = debug
    self.executando = True
    self.i = 0
    self.s = -1
    
    self.entrada = entrada if entrada else []
    self.indice_entrada = 0
    
    self.saida = []
    
    try:
        while self.executando and self.i < len(self.P):
            instrucao, operandos = self.P[self.i]
            
            if self.debug:
                print(f"[{self.i:3d}] {instrucao:8s} {operandos} | s={self.s} | M[s]={self.M[self.s] if self.s >= 0 else 'N/A'}")
            
            self._executar_instrucao(instrucao, operandos)
            
    except Exception as e:
        raise ErroMVD(f"Erro na linha {self.i}: {instrucao} {operandos} - {str(e)}")
    
    return self.saida
```

**Explicação linha por linha:**

**1. Inicialização:**
- `self.debug = debug`: Ativa/desativa modo debug
- `self.executando = True`: Flag de controle
- `self.i = 0`: Program counter no início
- `self.s = -1`: Stack pointer (pilha vazia)

**2. Configurar entrada:**
- `self.entrada = entrada if entrada else []`: Lista de valores ou vazia
- `self.indice_entrada = 0`: Índice para próxima entrada

**3. Inicializar saída:**
- `self.saida = []`: Lista vazia para acumular valores de `PRN`

**4. Loop principal:**
- `while self.executando and self.i < len(self.P)`: 
  - Continua enquanto `executando=True` E há instruções
  - `executando` vira `False` quando encontra `HLT`
- `instrucao, operandos = self.P[self.i]`: Lê instrução atual
- `if self.debug`: Se modo debug, imprime estado
  - Formato: `[endereco] instrucao operandos | s=valor | M[s]=valor`
- `self._executar_instrucao(instrucao, operandos)`: Executa instrução
  - Método atualiza estado (i, s, M)

**5. Tratamento de erros:**
- `except Exception as e`: Captura qualquer erro
- `raise ErroMVD(...)`: Relança com contexto (linha, instrução)

**6. Retorno:**
- `return self.saida`: Retorna lista de valores impressos

## Relação com as Notas de Aula

### Arquitetura da MVD

Conforme as notas de aula (seção 7.1):
- Máquina a pilha
- Memória P (programa) e M (dados)
- Registradores i e s

A implementação segue essa arquitetura exatamente.

### Instruções da MVD

Todas as instruções descritas nas notas de aula (seção 7.2-7.7) estão implementadas:
- Instruções de carga: `LDC`, `LDV`
- Instruções de armazenamento: `STR`
- Instruções aritméticas: `ADD`, `SUB`, `MULT`, `DIVI`, `INV`
- Instruções lógicas: `AND`, `OR`, `NEG`
- Instruções de comparação: `CME`, `CMA`, `CEQ`, `CDIF`, `CMEQ`, `CMAQ`
- Instruções de desvio: `JMP`, `JMPF`
- Instruções de I/O: `RD`, `PRN`
- Instruções de subrotinas: `CALL`, `RETURN`
- Instruções de memória: `ALLOC`, `DALLOC`
- Instruções de controle: `START`, `HLT`, `NULL`

### Avaliação de Expressões

Conforme as notas de aula (seção 7.2), expressões são avaliadas usando a pilha:
- Valores intermediários ficam no topo
- Operadores consomem operandos e deixam resultado

A implementação executa código gerado que segue esse modelo.

### Convenção de Valores Booleanos

Conforme as notas de aula:
- `verdadeiro` = 1
- `falso` = 0

A implementação segue essa convenção em todas as operações lógicas e comparações.

