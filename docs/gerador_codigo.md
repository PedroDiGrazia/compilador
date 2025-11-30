# Gerador de Código - Documentação

## Introdução e Teoria

### Base Teórica

O **Gerador de Código** é a fase final do processo de compilação. Conforme as notas de aula (seção 1.5 e 7), sua função é traduzir a AST anotada em código assembly para a **Máquina Virtual Didática (MVD)**.

#### Função do Gerador de Código

Segundo as notas de aula (seção 1.5):
> "A geração de códigos é a fase final da compilação. Uma geração de códigos ótima é sempre difícil, sendo importante destacar as dificuldades decorrentes das especificidades de cada máquina."

O gerador de código:
1. **Percorre a AST**: Visita nós da árvore sintática
2. **Gera instruções**: Emite código assembly para cada construção
3. **Gerencia memória**: Gera ALLOC/DALLOC para escopos
4. **Gerencia rótulos**: Gera rótulos para desvios e subrotinas

### Máquina Virtual Didática (MVD)

A MVD é uma **máquina a pilha** conforme descrito nas notas de aula (seção 7.1):
- **Memória de programa P**: Contém instruções
- **Memória de dados M**: Pilha de valores
- **Registrador i**: Endereço da próxima instrução
- **Registrador s**: Topo da pilha

### Estrutura de Geração

Conforme as notas de aula, a geração segue esta estrutura:
- **ALLOC/DALLOC**: Separados por escopo
- **Subrotinas aninhadas**: Geradas DENTRO da subrotina pai
- **Retorno de função**: Via STR para endereço reservado + RETURN

## Estrutura do Código

### Classe Principal: `GeradorCodigo`

A classe `GeradorCodigo` percorre a AST e gera código assembly para a MVD.

#### Atributos da Classe

```python
def __init__(self):
    self.instrucoes: List[str] = []              # Lista de instruções geradas
    self.contador_rotulos = 1                    # Contador de rótulos (começa em 1)
    self.rotulos_subrotinas: Dict[str, int] = {} # Mapeia nome → rótulo
    self.funcao_atual: Optional[str] = None      # Função atual (para retorno)
    self.tabela_simbolos: TabelaSimbolos = None  # Tabela reconstruída
    self.pilha_alocacao: List[Tuple[int, int]] = []  # Pilha para DALLOC
```

**Estrutura:**
- `instrucoes`: Lista de strings com código assembly gerado
- `contador_rotulos`: Gera rótulos numéricos únicos
- `rotulos_subrotinas`: Mapeia nomes de funções/procedimentos para rótulos
- `funcao_atual`: Rastreia função atual para tratar retorno
- `tabela_simbolos`: Reconstruída durante geração (para manter escopos corretos)
- `pilha_alocacao`: Rastreia ALLOCs para gerar DALLOCs na ordem inversa

### Métodos Auxiliares

#### `emitir(instrucao: str)`

Emite uma instrução assembly adicionando à lista.

**Parâmetros:**
- `instrucao`: String com instrução assembly

**Uso:** Adiciona instruções ao código gerado.

#### `novo_rotulo() -> int`

Gera um novo rótulo numérico único.

**Retorno:** Número do rótulo (incrementa contador)

**Uso:** Criar rótulos para desvios e subrotinas.

#### `obter_rotulo_subrotina(nome: str) -> int`

Retorna (ou cria) o rótulo associado à função/procedimento.

**Parâmetros:**
- `nome`: Nome da função ou procedimento

**Retorno:** Rótulo numérico

**Uso:** Obter rótulo para CALL.

#### `emitir_alloc(endereco_base: int, quantidade: int)`

Emite ALLOC e registra para posterior DALLOC.

**Parâmetros:**
- `endereco_base`: Endereço base do escopo
- `quantidade`: Quantidade de variáveis

**Processo:**
1. Se quantidade > 0, emite `ALLOC endereco_base quantidade`
2. Empilha informação na `pilha_alocacao`

**Uso:** Alocar memória para variáveis de um escopo.

#### `emitir_dalloc_da_pilha()`

Emite DALLOC para o último ALLOC da pilha.

**Processo:**
1. Desempilha informação de alocação
2. Se quantidade > 0, emite `DALLOC endereco_base quantidade`

**Uso:** Desalocar memória ao sair de escopo.

## Detalhamento das Funções

### Método Principal

#### `gerar(programa: Programa, tabela_simbolos: TabelaSimbolos = None) -> List[str]`

Gera código para o programa completo.

**Parâmetros:**
- `programa`: Nó `Programa` da AST
- `tabela_simbolos`: Tabela de símbolos (opcional, cria nova se None)

**Retorno:** Lista de strings com código assembly

**Processo:**
1. Inicializa estruturas
2. Cria nova tabela de símbolos (reconstrução)
3. Emite `START`
4. Calcula alocações do escopo global:
   - Reserva espaço para retorno de funções globais
   - Declara variáveis globais
   - Declara procedimentos globais
5. Gera ALLOCs para escopo global
6. Se houver subrotinas, emite JMP para pular para corpo principal
7. Gera código das subrotinas (funções e procedimentos)
8. Gera código do corpo principal
9. Gera DALLOCs na ordem inversa
10. Emite `HLT`

**Estrutura gerada:**
```
START
ALLOC ... (retornos de funções globais)
ALLOC ... (variáveis globais)
JMP L_principal (se houver subrotinas)
[subrotinas]
L_principal NULL
[corpo principal]
DALLOC ...
DALLOC ...
HLT
```

### Geração de Subrotinas

#### `_gerar_funcao(no: Funcao, endereco_pai: int)`

Gera código para uma função.

**Parâmetros:**
- `no`: Nó `Funcao` da AST
- `endereco_pai`: Endereço base do escopo pai

**Processo:**
1. Emite rótulo da função
2. Entra no escopo da função
3. Calcula variáveis locais (funções aninhadas + variáveis declaradas)
4. Declara símbolos no escopo
5. Gera ALLOC para variáveis locais
6. Se houver subrotinas aninhadas, emite JMP para pular
7. Gera código das subrotinas aninhadas
8. Gera código do corpo da função
9. Gera DALLOC e RETURN
10. Sai do escopo

**Estrutura gerada:**
```
L_func NULL
ALLOC base quantidade
JMP L_corpo (se houver aninhadas)
[subrotinas aninhadas]
L_corpo NULL
[corpo da função]
DALLOC base quantidade
RETURN
```

#### `_gerar_procedimento(no: Procedimento, endereco_pai: int)`

Gera código para um procedimento (similar a função, sem retorno).

**Processo:** Similar a `_gerar_funcao()`, mas sem espaço para retorno.

### Geração de Comandos

#### `gera_comando_composto(no: ComandoComposto)`

Gera código para sequência de comandos.

**Processo:** Itera sobre comandos e chama `gera_comando()` para cada um.

#### `gera_comando(no: Comando)`

Despacha para método específico baseado no tipo de comando.

#### `gera_atribuicao(no: Atribuicao)`

Gera código para atribuição: `identificador := expressao`

**Processo:**
1. Gera código da expressão (deixa resultado no topo da pilha)
2. Busca símbolo do identificador
3. Emite `STR endereco` para armazenar valor

**Uso:** Atribuição a variável ou retorno de função.

#### `gera_comando_leitura(no: ComandoLeitura)`

Gera código para `leia(identificador)`.

**Processo:**
1. Emite `RD` (lê valor e coloca no topo da pilha)
2. Busca endereço da variável
3. Emite `STR endereco`

**Instruções geradas:**
```
RD
STR endereco
```

#### `gera_comando_escrita(no: ComandoEscrita)`

Gera código para `escreva(expressao)`.

**Processo:**
1. Gera código da expressão
2. Emite `PRN` (imprime valor do topo da pilha)

**Instruções geradas:**
```
[expressao]
PRN
```

#### `gera_comando_se(no: ComandoSe)`

Gera código para `se ... entao ... [senao ...]`.

**Processo (com senao):**
1. Gera código da condição
2. Emite `JMPF rotulo_senao` (se falso, pula para senao)
3. Gera código do `entao`
4. Emite `JMP rotulo_fim` (pula fim do senao)
5. Emite rótulo do senao
6. Gera código do `senao`
7. Emite rótulo do fim

**Processo (sem senao):**
1. Gera código da condição
2. Emite `JMPF rotulo_fim` (se falso, pula fim)
3. Gera código do `entao`
4. Emite rótulo do fim

**Instruções geradas (com senao):**
```
[condição]
JMPF L_senao
[então]
JMP L_fim
L_senao NULL
[senao]
L_fim NULL
```

#### `gera_comando_enquanto(no: ComandoEnquanto)`

Gera código para `enquanto ... faca ...`.

**Processo:**
1. Emite rótulo do início do loop
2. Gera código da condição
3. Emite `JMPF rotulo_fim` (se falso, sai do loop)
4. Gera código do corpo
5. Emite `JMP rotulo_inicio` (volta ao início)
6. Emite rótulo do fim

**Instruções geradas:**
```
L_inicio NULL
[condição]
JMPF L_fim
[corpo]
JMP L_inicio
L_fim NULL
```

#### `gera_chamada_procedimento(no: ChamadaProcedimento)`

Gera código para chamada de procedimento.

**Processo:**
1. Obtém rótulo do procedimento
2. Emite `CALL rotulo`

**Instruções geradas:**
```
CALL L_proc
```

### Geração de Expressões

#### `gera_expressao(no: Expressao)`

Gera código para expressão (deixa resultado no topo da pilha).

**Processo:** Despacha para método específico baseado no tipo.

#### `gera_operacao_binaria(no: OperacaoBinaria)`

Gera código para operação binária.

**Processo:**
1. Gera código do operando esquerdo
2. Gera código do operando direito
3. Emite instrução correspondente ao operador

**Mapeamento de operadores:**
- `'+'` → `ADD`
- `'-'` → `SUB`
- `'*'` → `MULT`
- `'div'` → `DIVI`
- `'e'` → `AND`
- `'ou'` → `OR`
- `'='` → `CEQ`
- `'!='` → `CDIF`
- `'<'` → `CME`
- `'<='` → `CMEQ`
- `'>'` → `CMA`
- `'>='` → `CMAQ`

**Instruções geradas:**
```
[esquerda]
[direita]
OPERADOR
```

#### `gera_operacao_unaria(no: OperacaoUnaria)`

Gera código para operação unária.

**Mapeamento:**
- `'nao'` → `NEG`
- `'-'` → `INV`

**Instruções geradas:**
```
[operando]
OPERADOR
```

#### `gera_identificador(no: Identificador)`

Gera código para identificador em expressão.

**Processo:**
1. Busca símbolo na tabela
2. Se for **variável**: Emite `LDV endereco`
3. Se for **função**: 
   - Emite `CALL rotulo` (executa função)
   - Emite `LDV endereco_retorno` (carrega valor de retorno)

**Instruções geradas (variável):**
```
LDV endereco
```

**Instruções geradas (função):**
```
CALL L_func
LDV endereco_retorno
```

#### Geração de Literais

- **Número**: `LDC valor`
- **Booleano**: `LDC 1` (verdadeiro) ou `LDC 0` (falso)

## Integração

### Uso pelo Compilador Principal

O `compilador.py` utiliza o gerador assim:

```python
analisador_semantico = AnalisadorSemantico()
tabela_simbolos = analisador_semantico.analisar(ast)
gerador = GeradorCodigo()
instrucoes = gerador.gerar(ast, tabela_simbolos)
```

### Fluxo de Dados

```
AST Anotada + TabelaSimbolos
    ↓
GeradorCodigo.gerar()
    ↓
Lista de Instruções Assembly
    ↓
Arquivo .obj
    ↓
Máquina Virtual
```

### Dependências

- **`arvore_sintatica`**: Importa todas as classes de nós da AST
- **`tabela_simbolos`**: Importa `TabelaSimbolos`

## Exemplos Práticos

### Exemplo 1: Geração de Expressão Aritmética

```python
# Expressão: x + 5 * 2
# AST: OperacaoBinaria(Identificador("x"), "+", OperacaoBinaria(Numero(5), "*", Numero(2)))

# Código gerado:
LDV endereco_x    # Carrega x
LDC 5             # Carrega 5
LDC 2             # Carrega 2
MULT              # 5 * 2 = 10
ADD               # x + 10
```

### Exemplo 2: Geração de Comando Condicional

```python
# Comando: se x > 0 entao x := 1 senao x := 0

# Código gerado:
LDV endereco_x    # Carrega x
LDC 0             # Carrega 0
CMA               # x > 0? (resultado no topo)
JMPF L_senao      # Se falso, vai para senao
LDC 1             # Carrega 1
STR endereco_x    # x := 1
JMP L_fim         # Pula senao
L_senao NULL
LDC 0             # Carrega 0
STR endereco_x    # x := 0
L_fim NULL
```

### Exemplo 3: Geração de Função

```python
# Função: funcao soma: inteiro; inicio soma := 10; fim;

# Código gerado:
L_soma NULL       # Rótulo da função
ALLOC 1 1         # Aloca espaço para variáveis locais (se houver)
LDC 10            # Carrega 10
STR 0             # Armazena em endereço de retorno (endereço 0)
DALLOC 1 1        # Desaloca variáveis locais
RETURN            # Retorna
```

## Análise Detalhada do Código

### Método `gerar` - Análise Detalhada

```python
def gerar(self, programa: Programa, tabela_simbolos: TabelaSimbolos = None) -> List[str]:
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
```

**Explicação linha por linha:**

**1. Inicialização:**
- `self.instrucoes = []`: Limpa lista de instruções (permite reutilizar gerador)
- `self.contador_rotulos = 1`: Reseta contador de rótulos
- `self.rotulos_subrotinas = {}`: Limpa mapeamento de rótulos
- `self.funcao_atual = None`: Reseta função atual
- `self.pilha_alocacao = []`: Limpa pilha de alocações

**2. Criar nova tabela de símbolos:**
- `self.tabela_simbolos = TabelaSimbolos()`: Cria tabela nova (não usa a fornecida)
  - **Por quê?** Precisa reconstruir escopos durante geração
  - Escopos são reconstruídos na mesma ordem que análise semântica
  - Garante endereços corretos

**3. Emitir START:**
- `self.emitir("START")`: Primeira instrução do programa
  - Inicializa máquina virtual

**4. Calcular alocações globais:**
- `qtd_retorno_funcoes = len(programa.funcoes)`: Conta funções globais
- `qtd_variaveis_globais = self._contar_declaracoes_variaveis(...)`: Conta variáveis globais
  - Método auxiliar que soma quantidade de variáveis em todas as declarações

**5. Declarar símbolos globais:**
- `for func in programa.funcoes: self.tabela_simbolos.declarar_retorno_funcao(...)`: 
  - Declara funções globais (reserva espaço para retorno)
- `if programa.declaracoes_variaveis: self._declarar_variaveis(...)`: 
  - Declara variáveis globais na tabela
- `for proc in programa.procedimentos: self.tabela_simbolos.declarar_procedimento(...)`: 
  - Declara procedimentos globais

**6. Gerar ALLOCs globais:**
- `if qtd_retorno_funcoes > 0: self.emitir_alloc(0, qtd_retorno_funcoes)`: 
  - Aloca espaço para retornos de funções (endereços 0 até qtd-1)
- `if qtd_variaveis_globais > 0: self.emitir_alloc(base, qtd_variaveis_globais)`: 
  - `base = qtd_retorno_funcoes`: Variáveis começam após retornos
  - Aloca espaço para variáveis globais

**7. Gerar JMP para pular subrotinas:**
- `tem_subrotinas = len(programa.procedimentos) > 0 or len(programa.funcoes) > 0`: 
  - Verifica se há subrotinas
- `rotulo_principal = self.novo_rotulo()`: Gera rótulo para corpo principal
- `if tem_subrotinas: self.emitir(f"JMP {rotulo_principal}")`: 
  - Se há subrotinas, pula para corpo principal
  - Subrotinas serão geradas antes do corpo

**8. Gerar código das subrotinas:**
- `proximo_endereco = qtd_retorno_funcoes + qtd_variaveis_globais`: 
  - Calcula endereço base para escopos das subrotinas
- `for func in programa.funcoes: self._gerar_funcao(func, proximo_endereco)`: 
  - Gera código de cada função
- `for proc in programa.procedimentos: self._gerar_procedimento(proc, proximo_endereco)`: 
  - Gera código de cada procedimento

**9. Gerar corpo principal:**
- `self.emitir(f"{rotulo_principal} \tNULL")`: Emite rótulo do corpo principal
  - `\tNULL` é formato para rótulo (espaço + NULL)
- `self.gera_comando_composto(programa.comando_composto)`: Gera comandos do programa

**10. Gerar DALLOCs:**
- `while self.pilha_alocacao: self.emitir_dalloc_da_pilha()`: 
  - Desempilha e gera DALLOCs na ordem inversa (LIFO)
  - Último ALLOC é primeiro DALLOC

**11. Finalizar:**
- `self.emitir("HLT")`: Emite instrução de parada
- `return self.instrucoes`: Retorna lista completa

**Estrutura gerada:**
```
START
ALLOC 0 n1          # Retornos de funções
ALLOC n1 n2         # Variáveis globais
JMP L_principal     # Pula subrotinas
L_func1 NULL        # Função 1
  ...
L_proc1 NULL        # Procedimento 1
  ...
L_principal NULL    # Corpo principal
  [comandos]
DALLOC n1 n2        # Desaloca variáveis globais
DALLOC 0 n1         # Desaloca retornos
HLT
```

### Método `gera_atribuicao` - Análise Detalhada

```python
def gera_atribuicao(self, no: Atribuicao):
    simbolo = self.tabela_simbolos.buscar(no.identificador)
    if simbolo is None:
        raise Exception(f"Identificador '{no.identificador}' não declarado (gerador)")
    
    # Avalia a expressão
    self.gera_expressao(no.expressao)
    
    # Armazena no endereço (funciona para variável e retorno de função)
    endereco = simbolo.endereco_memoria
    self.emitir(f"STR {endereco}")
```

**Explicação linha por linha:**
- `simbolo = self.tabela_simbolos.buscar(no.identificador)`: Busca símbolo na tabela
  - Tabela foi reconstruída durante geração, mantendo escopos corretos
- `if simbolo is None`: Verifica se encontrado (não deveria acontecer se semântica OK)
- `self.gera_expressao(no.expressao)`: Gera código da expressão
  - Expressão é avaliada e resultado fica no topo da pilha
- `endereco = simbolo.endereco_memoria`: Obtém endereço do símbolo
  - Para variável: endereço da variável
  - Para função: endereço de retorno
- `self.emitir(f"STR {endereco}")`: Emite instrução STR
  - `STR` remove valor do topo da pilha e armazena no endereço

**Código gerado (exemplo: `x := 5`):**
```
LDC 5              # Carrega 5 na pilha
STR 0              # Armazena em endereço 0 (x)
```

### Método `gera_comando_se` - Análise Detalhada

```python
def gera_comando_se(self, no: ComandoSe):
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
```

**Explicação linha por linha (com senao):**

**1. Gerar rótulos:**
- `rotulo_senao = self.novo_rotulo()`: Rótulo para bloco `senao`
- `rotulo_fim = self.novo_rotulo()`: Rótulo para fim do comando

**2. Gerar código:**
- `self.gera_expressao(no.condicao)`: Gera código da condição
  - Resultado booleano fica no topo da pilha (1=verdadeiro, 0=falso)
- `self.emitir(f"JMPF {rotulo_senao}")`: Se falso (0), pula para `senao`
  - `JMPF` remove valor do topo e pula se for 0
- `self.gera_comando(no.comando_entao)`: Gera código do `entao`
  - Executado se condição verdadeira
- `self.emitir(f"JMP {rotulo_fim}`)`: Pula fim do `senao` (já executou `entao`)
- `self.emitir(f"{rotulo_senao} \tNULL")`: Rótulo do `senao`
- `self.gera_comando(no.comando_senao)`: Gera código do `senao`
- `self.emitir(f"{rotulo_fim} \tNULL")`: Rótulo do fim

**Código gerado (exemplo: `se x > 0 entao x := 1 senao x := 0`):**
```
LDV 0              # Carrega x
LDC 0              # Carrega 0
CMA                # Compara: x > 0? (resultado no topo)
JMPF L_senao       # Se falso, pula para senao
LDC 1              # Carrega 1
STR 0              # x := 1
JMP L_fim          # Pula fim
L_senao NULL       # Rótulo senao
LDC 0              # Carrega 0
STR 0              # x := 0
L_fim NULL         # Rótulo fim
```

**Explicação (sem senao):**
- Similar, mas sem bloco `senao`
- Apenas pula fim se condição falsa

### Método `gera_comando_enquanto` - Análise Detalhada

```python
def gera_comando_enquanto(self, no: ComandoEnquanto):
    rotulo_inicio = self.novo_rotulo()
    rotulo_fim = self.novo_rotulo()
    
    self.emitir(f"{rotulo_inicio} \tNULL")
    self.gera_expressao(no.condicao)
    self.emitir(f"JMPF {rotulo_fim}")
    self.gera_comando(no.corpo)
    self.emitir(f"JMP {rotulo_inicio}")
    self.emitir(f"{rotulo_fim} \tNULL")
```

**Explicação linha por linha:**
- `rotulo_inicio = self.novo_rotulo()`: Rótulo para início do loop
- `rotulo_fim = self.novo_rotulo()`: Rótulo para fim do loop
- `self.emitir(f"{rotulo_inicio} \tNULL")`: Emite rótulo de início
  - Ponto de retorno do loop
- `self.gera_expressao(no.condicao)`: Gera código da condição
- `self.emitir(f"JMPF {rotulo_fim}")`: Se falso, sai do loop
- `self.gera_comando(no.corpo)`: Gera código do corpo
- `self.emitir(f"JMP {rotulo_inicio}")`: Volta ao início (loop)
- `self.emitir(f"{rotulo_fim} \tNULL")`: Rótulo de fim

**Código gerado (exemplo: `enquanto x < 10 faca x := x + 1`):**
```
L_inicio NULL      # Início do loop
LDV 0              # Carrega x
LDC 10             # Carrega 10
CME                # Compara: x < 10?
JMPF L_fim         # Se falso, sai
LDV 0              # Carrega x
LDC 1              # Carrega 1
ADD                # x + 1
STR 0              # x := x + 1
JMP L_inicio       # Volta ao início
L_fim NULL         # Fim do loop
```

### Método `gera_operacao_binaria` - Análise Detalhada

```python
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
```

**Explicação linha por linha:**
- `self.gera_expressao(no.esquerda)`: Gera código do operando esquerdo
  - Resultado fica no topo da pilha
- `self.gera_expressao(no.direita)`: Gera código do operando direito
  - Resultado fica no topo da pilha (empurra esquerda para baixo)
- `mapa_operadores = {...}`: Mapeia operador (string) para instrução MVD
- `instrucao = mapa_operadores.get(no.operador)`: Obtém instrução correspondente
- `if not instrucao`: Verifica se operador é válido
- `self.emitir(instrucao)`: Emite instrução
  - Instrução consome dois valores do topo e deixa resultado no topo

**Estado da pilha:**
```
Antes de gera_expressao(esquerda):
  [pilha anterior]

Depois de gera_expressao(esquerda):
  [pilha anterior]
  [valor_esquerda]  ← topo

Depois de gera_expressao(direita):
  [pilha anterior]
  [valor_esquerda]
  [valor_direita]   ← topo

Depois de ADD (ou outra operação):
  [pilha anterior]
  [resultado]       ← topo
```

**Por que gerar esquerda antes de direita:**
- MVD é máquina a pilha
- Operações consomem valores do topo
- Ordem: esquerda primeiro (fica embaixo), direita depois (fica em cima)
- Operação consome direita e esquerda, deixa resultado

### Método `gera_identificador` - Análise Detalhada

```python
def gera_identificador(self, no: Identificador):
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
```

**Explicação linha por linha:**

**1. Buscar símbolo:**
- `simbolo = self.tabela_simbolos.buscar(no.nome)`: Busca na tabela
- `if simbolo is None`: Erro se não encontrado

**2. Gerar código por categoria:**

**a) Variável:**
- `if simbolo.categoria == 'variavel'`: Verifica se é variável
- `self.emitir(f"LDV {simbolo.endereco_memoria}")`: Emite LDV
  - `LDV` carrega valor de `M[endereco]` e coloca no topo da pilha

**b) Função:**
- `elif simbolo.categoria == 'funcao'`: Verifica se é função
- `rotulo = self.obter_rotulo_subrotina(no.nome)`: Obtém rótulo da função
- `self.emitir(f"CALL {rotulo}")`: Chama função
  - `CALL` executa função, que armazena resultado em `endereco_retorno`
- `self.emitir(f"LDV {simbolo.endereco_memoria}")`: Carrega valor de retorno
  - `LDV` carrega valor de `M[endereco_retorno]` para o topo da pilha

**c) Erro:**
- `else`: Se não é variável nem função (ex: procedimento)
- `raise Exception(...)`: Erro (procedimentos não podem aparecer em expressões)

**Código gerado (exemplo: `x` como variável):**
```
LDV 0              # Carrega valor de M[0] (x)
```

**Código gerado (exemplo: `soma()` como função):**
```
CALL L_soma        # Executa função soma
LDV 0              # Carrega valor de retorno de M[0]
```

## Relação com as Notas de Aula

### Avaliação de Expressões

Conforme as notas de aula (seção 7.2), expressões são avaliadas usando a pilha:
- Valores intermediários ficam no topo da pilha
- Operadores consomem operandos da pilha e deixam resultado no topo
- O código gerado segue notação pós-fixa

A implementação gera código que segue exatamente esse modelo.

### ALLOC/DALLOC

Conforme as notas de aula (seção 7.7), variáveis locais são alocadas com ALLOC:
- `ALLOC m,n`: Aloca n posições a partir de m
- `DALLOC m,n`: Desaloca n posições

A implementação gera ALLOC ao entrar em escopo e DALLOC ao sair, na ordem inversa (LIFO).

### Subrotinas Aninhadas

Conforme as notas de aula, subrotinas aninhadas são geradas DENTRO da subrotina pai:
- Código das subrotinas aninhadas vem antes do corpo da subrotina pai
- JMP é usado para pular as subrotinas aninhadas e ir direto ao corpo

A implementação segue essa estrutura exatamente.

### Retorno de Função

Conforme as notas de aula, funções retornam valores através de:
- Espaço reservado para retorno (declarado antes da função)
- Atribuição ao nome da função armazena no endereço de retorno
- RETURN retorna ao ponto de chamada

A implementação segue esse modelo: `soma := expr` gera código que armazena em `endereco_retorno`.

