# Analisador Semântico - Documentação

## Introdução e Teoria

### Base Teórica

O **Analisador Semântico** é a terceira fase do processo de compilação. Conforme as notas de aula (seção 1.4 e 6), sua principal função é captar o **significado** das ações a serem tomadas no texto fonte e verificar a **consistência semântica** do programa.

#### Funções do Analisador Semântico

Segundo as notas de aula (seção 6.3), o analisador semântico realiza:

1. **Verificação de duplicidade**: Verifica se identificadores não foram declarados múltiplas vezes no mesmo escopo
2. **Verificação de declaração**: Verifica se identificadores usados foram declarados
3. **Verificação de compatibilidade de tipos**: Verifica se tipos são compatíveis em atribuições e operações
4. **Verificação de comandos**: Verifica uso correto de `leia`, `escreva`, chamadas de procedimentos/funções
5. **Verificação de operadores**: Verifica uso correto de operadores unários e binários

### Gramática com Atributos

Conforme as notas de aula (seção 6.1), o analisador semântico utiliza o conceito de **gramática com atributos**:
- Ações semânticas são atribuídas às produções da gramática
- Atributos são propagados pela árvore sintática
- A tabela de símbolos armazena informações sobre identificadores

### Análise Semântica e Tabela de Símbolos

O analisador semântico utiliza a tabela de símbolos para:
- Verificar declarações de identificadores
- Verificar escopo e visibilidade
- Verificar tipos de dados
- Gerenciar escopos hierárquicos

## Estrutura do Código

### Classe Principal: `AnalisadorSemantico`

A classe `AnalisadorSemantico` percorre a AST e realiza todas as verificações semânticas.

#### Atributos da Classe

```python
def __init__(self):
    self.tabela_simbolos = TabelaSimbolos()  # Tabela de símbolos
    self.erros = []                          # Lista de erros encontrados
    self.funcao_atual = None                 # Nome da função atual (para retorno)
```

**Estrutura:**
- `tabela_simbolos`: Gerencia declarações e escopos
- `erros`: Acumula mensagens de erro (para reportar todos de uma vez)
- `funcao_atual`: Rastreia função atual para verificar atribuição de retorno

### Método Principal

#### `analisar(programa: Programa) -> TabelaSimbolos`

Ponto de entrada do analisador semântico. Analisa semanticamente o programa completo.

**Parâmetros:**
- `programa`: Nó `Programa` da AST

**Retorno:** `TabelaSimbolos` populada com todos os símbolos

**Processo:**
1. Chama `analisa_programa()` para iniciar análise
2. Se houver erros, lança `ErroSemantico` com todas as mensagens
3. Retorna tabela de símbolos populada

**Erros:**
- `ErroSemantico`: Se encontrar erros semânticos

## Detalhamento das Funções

### Análise do Programa

#### `analisa_programa(no: Programa)`

Analisa o programa completo seguindo esta ordem:

1. **Reserva posições de retorno** para todas as funções do nível global
2. **Declara variáveis globais** (se houver)
3. **Declara procedimentos** do nível global
4. **Processa funções e procedimentos** (com seus escopos aninhados)
5. **Analisa o comando composto** principal

**Processo:**
- Funções precisam de espaço para retorno (declaradas antes de serem processadas)
- Variáveis globais são declaradas no escopo 0
- Subrotinas são processadas recursivamente com seus próprios escopos

### Análise de Funções e Procedimentos

#### `analisa_funcao(no: Funcao)`

Processa uma função completa:

**Processo:**
1. Calcula endereço base para o escopo da função
2. Entra no escopo da função
3. Define `funcao_atual` (para verificar retorno)
4. Processa o bloco da função (`_processar_bloco`)
5. Restaura `funcao_atual` anterior
6. Sai do escopo

**Uso:** Analisa funções globais e aninhadas.

#### `analisa_procedimento(no: Procedimento)`

Processa um procedimento completo:

**Processo:**
1. Calcula endereço base para o escopo do procedimento
2. Entra no escopo do procedimento
3. Processa o bloco do procedimento (`_processar_bloco`)
4. Sai do escopo

**Uso:** Analisa procedimentos globais e aninhados.

#### `_processar_bloco(bloco: Bloco)`

Processa um bloco (comum a funções e procedimentos):

**Processo:**
1. **Reserva posições de retorno** para funções aninhadas
2. **Declara variáveis locais**
3. **Declara procedimentos aninhados**
4. **Processa subrotinas aninhadas** recursivamente
5. **Analisa comandos** do bloco

**Uso:** Processa blocos de funções, procedimentos e programa principal.

### Análise de Declarações

#### `analisa_declaracoes_variaveis(no: DeclaracoesVariaveis)`

Processa múltiplas declarações de variáveis.

**Processo:** Itera sobre declarações e chama `analisa_declaracao_variavel()` para cada uma.

#### `analisa_declaracao_variavel(no: DeclaracaoVariavel)`

Declara variáveis no escopo atual.

**Processo:**
1. Para cada identificador na declaração:
   - Chama `tabela_simbolos.declarar()` com tipo e categoria `'variavel'`
   - Se houver erro (duplicidade), lança `ErroSemantico`

**Erros:**
- `ErroSemantico`: Se identificador já foi declarado no escopo atual

### Análise de Comandos

#### `analisa_comando_composto(no: ComandoComposto)`

Analisa sequência de comandos.

**Processo:** Itera sobre comandos e chama `analisa_comando()` para cada um.

#### `analisa_comando(no: Comando)`

Despacha para método específico baseado no tipo de comando.

**Tipos suportados:**
- `Atribuicao` → `analisa_atribuicao()`
- `ComandoLeitura` → `analisa_comando_leitura()`
- `ComandoEscrita` → `analisa_comando_escrita()`
- `ComandoSe` → `analisa_comando_se()`
- `ComandoEnquanto` → `analisa_comando_enquanto()`
- `ComandoComposto` → `analisa_comando_composto()` (recursivo)
- `ChamadaProcedimento` → `analisa_chamada_procedimento()`
- `ComandoVazio` → Nada (comando vazio)

#### `analisa_atribuicao(no: Atribuicao)`

Analisa comando de atribuição: `identificador := expressao`

**Processo:**
1. Busca símbolo do identificador na tabela
2. Analisa expressão e obtém seu tipo
3. Verifica compatibilidade:
   - Se for **variável**: tipos devem ser iguais
   - Se for **função**: trata como retorno (tipos devem ser iguais)
   - Caso contrário: erro

**Erros:**
- `ErroSemantico`: Se identificador não declarado, incompatibilidade de tipos, ou uso incorreto

#### `analisa_chamada_procedimento(no: ChamadaProcedimento)`

Verifica chamada de procedimento.

**Processo:**
1. Busca símbolo do procedimento
2. Verifica se é realmente um procedimento (categoria `'procedimento'`)

**Erros:**
- `ErroSemantico`: Se procedimento não declarado ou não é procedimento

#### `analisa_comando_leitura(no: ComandoLeitura)`

Verifica comando `leia(identificador)`.

**Processo:**
1. Busca símbolo do identificador
2. Verifica se é variável (categoria `'variavel'`)

**Erros:**
- `ErroSemantico`: Se identificador não declarado ou não é variável

#### `analisa_comando_escrita(no: ComandoEscrita)`

Verifica comando `escreva(expressao)`.

**Processo:** Apenas analisa a expressão (qualquer tipo pode ser escrito).

#### `analisa_comando_se(no: ComandoSe)`

Verifica comando condicional `se ... entao ... [senao ...]`.

**Processo:**
1. Analisa condição e verifica se é booleana
2. Analisa comando do `entao`
3. Se houver `senao`, analisa comando do `senao`

**Erros:**
- `ErroSemantico`: Se condição não for booleana

#### `analisa_comando_enquanto(no: ComandoEnquanto)`

Verifica comando de repetição `enquanto ... faca ...`.

**Processo:**
1. Analisa condição e verifica se é booleana
2. Analisa corpo do comando

**Erros:**
- `ErroSemantico`: Se condição não for booleana

### Análise de Expressões

#### `analisa_expressao(no: Expressao) -> str`

Analisa uma expressão e retorna seu tipo.

**Retorno:** `'inteiro'` ou `'booleano'`

**Processo:** Despacha para método específico baseado no tipo de expressão.

**Tipos suportados:**
- `OperacaoBinaria` → `analisa_operacao_binaria()`
- `OperacaoUnaria` → `analisa_operacao_unaria()`
- `Identificador` → `analisa_identificador()`
- `Numero` → Retorna `'inteiro'` (anota AST)
- `Booleano` → Retorna `'booleano'` (anota AST)

#### `analisa_operacao_binaria(no: OperacaoBinaria) -> str`

Analisa operação binária e verifica tipos dos operandos.

**Processo:**
1. Analisa operandos esquerdo e direito
2. Verifica compatibilidade de tipos conforme operador:
   - **Aritméticos** (`+`, `-`, `*`, `div`): Ambos devem ser `'inteiro'` → resultado `'inteiro'`
   - **Lógicos** (`e`, `ou`): Ambos devem ser `'booleano'` → resultado `'booleano'`
   - **Relacionais** (`=`, `!=`, `<`, `<=`, `>`, `>=`): Devem ser do mesmo tipo → resultado `'booleano'`
     - Operadores `<`, `<=`, `>`, `>=` requerem operandos `'inteiro'`
3. Anota tipo na AST (`no.tipo_expressao`)
4. Retorna tipo resultante

**Erros:**
- `ErroSemantico`: Se tipos incompatíveis ou operador desconhecido

#### `analisa_operacao_unaria(no: OperacaoUnaria) -> str`

Analisa operação unária.

**Operadores:**
- `'nao'`: Operando deve ser `'booleano'` → resultado `'booleano'`
- `'-'`: Operando deve ser `'inteiro'` → resultado `'inteiro'`

**Erros:**
- `ErroSemantico`: Se tipo incompatível ou operador desconhecido

#### `analisa_identificador(no: Identificador) -> str`

Analisa referência a identificador.

**Processo:**
1. Busca símbolo na tabela
2. Verifica se não é procedimento (procedimentos não podem aparecer em expressões)
3. Anota tipo na AST (`no.tipo_expressao = simbolo.tipo`)
4. Retorna tipo do símbolo

**Erros:**
- `ErroSemantico`: Se identificador não declarado ou é procedimento

## Integração

### Uso pelo Compilador Principal

O `compilador.py` utiliza o analisador semântico assim:

```python
ast = AnalisadorSintatico(tokens).analisar()
analisador_semantico = AnalisadorSemantico()
tabela_simbolos = analisador_semantico.analisar(ast)
```

### Fluxo de Dados

```
AST (Programa)
    ↓
AnalisadorSemantico.analisar()
    ↓
AST Anotada (com tipos) + TabelaSimbolos (populada)
    ↓
GeradorCodigo.gerar()
```

### Dependências

- **`arvore_sintatica`**: Importa todas as classes de nós da AST
- **`tabela_simbolos`**: Importa `TabelaSimbolos` e `Simbolo`
- **`tokens`**: Importa `ErroSemantico`

### Anotação da AST

O analisador semântico **anota** a AST com informações de tipo:
- `Expressao.tipo_expressao`: Preenchido com `'inteiro'` ou `'booleano'`
- Essas informações são usadas pelo gerador de código

## Exemplos Práticos

### Exemplo 1: Verificação de Declaração

```python
from analisador_semantico import AnalisadorSemantico
from analisador_sintatico import AnalisadorSintatico
from analisador_lexico import AnalisadorLexico

codigo = """
programa teste;
inicio
    x := 5;
fim.
"""

try:
    tokens = AnalisadorLexico(codigo).obter_tokens()
    ast = AnalisadorSintatico(tokens).analisar()
    analisador = AnalisadorSemantico()
    tabela = analisador.analisar(ast)
except ErroSemantico as e:
    print(f"Erro semântico: {e}")
```

**Saída:** `Erro semântico: Identificador 'x' não foi declarado`

### Exemplo 2: Verificação de Tipo

```python
codigo = """
programa teste;
var x: booleano;
inicio
    x := 42;
fim.
"""

try:
    # ... análise ...
except ErroSemantico as e:
    print(f"Erro: {e}")
```

**Saída:** `Erro semântico: Tipo incompatível na atribuição: 'x' é booleano, mas a expressão é inteiro`

### Exemplo 3: Verificação de Retorno de Função

```python
codigo = """
programa teste;
funcao soma: inteiro;
inicio
    soma := verdadeiro;
fim;
inicio
fim.
"""

try:
    # ... análise ...
except ErroSemantico as e:
    print(f"Erro: {e}")
```

**Saída:** `Erro semântico: Tipo de retorno incompatível na função 'soma': esperado inteiro, obtido booleano`

### Exemplo 4: Verificação de Condição Booleana

```python
codigo = """
programa teste;
var x: inteiro;
inicio
    se x entao
        x := 10;
fim.
"""

try:
    # ... análise ...
except ErroSemantico as e:
    print(f"Erro: {e}")
```

**Saída:** `Erro semântico: Condição do 'se' deve ser booleana, mas é inteiro`

## Análise Detalhada do Código

### Método `analisa_atribuicao` - Análise Detalhada

```python
def analisa_atribuicao(self, no: Atribuicao):
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
```

**Explicação linha por linha:**

**1. Buscar símbolo:**
- `simbolo = self.tabela_simbolos.buscar(no.identificador)`: Busca identificador na tabela
  - `buscar()` procura do escopo mais interno ao mais externo
  - Retorna `Simbolo` ou `None`
- `if simbolo is None`: Verifica se não foi encontrado
  - `raise ErroSemantico(...)`: Erro se identificador não declarado

**2. Analisar expressão:**
- `tipo_expressao = self.analisa_expressao(no.expressao)`: Analisa expressão recursivamente
  - Retorna tipo da expressão (`'inteiro'` ou `'booleano'`)
  - Anota AST com tipo (`no.expressao.tipo_expressao`)

**3. Verificar compatibilidade por categoria:**

**a) Variável:**
- `if simbolo.categoria == 'variavel'`: Verifica se é variável
- `if simbolo.tipo != tipo_expressao`: Compara tipos
  - `simbolo.tipo`: Tipo declarado da variável
  - `tipo_expressao`: Tipo inferido da expressão
- `raise ErroSemantico(...)`: Erro se tipos incompatíveis

**b) Função (retorno):**
- `elif simbolo.categoria == 'funcao'`: Verifica se é função
- `if simbolo.tipo != tipo_expressao`: Compara tipo de retorno
  - `simbolo.tipo`: Tipo de retorno declarado da função
  - `tipo_expressao`: Tipo da expressão atribuída
- Em LPD, retorno de função é feito via `funcao := expressao`

**c) Outros:**
- `else`: Se não é variável nem função (ex: procedimento)
- `raise ErroSemantico(...)`: Erro (procedimentos não podem receber atribuição)

**Exemplo de execução:**
```python
# Código: x := 5
# no.identificador = "x"
# simbolo = Simbolo(nome="x", tipo="inteiro", categoria="variavel")
# tipo_expressao = "inteiro" (de Numero(5))
# Compara: "inteiro" == "inteiro" ✓ OK

# Código: x := verdadeiro
# tipo_expressao = "booleano"
# Compara: "inteiro" != "booleano" ✗ ERRO
```

### Método `analisa_operacao_binaria` - Análise Detalhada

```python
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
```

**Explicação linha por linha:**

**1. Analisar operandos:**
- `tipo_esquerda = self.analisa_expressao(no.esquerda)`: Analisa operando esquerdo recursivamente
- `tipo_direita = self.analisa_expressao(no.direita)`: Analisa operando direito recursivamente
- `operador = no.operador`: Obtém operador (string: `'+'`, `'e'`, `'='`, etc.)

**2. Verificar por categoria de operador:**

**a) Operadores aritméticos (`+`, `-`, `*`, `div`):**
- `if operador in ['+', '-', '*', 'div']`: Verifica se é aritmético
- `if tipo_esquerda != 'inteiro' or tipo_direita != 'inteiro'`: Ambos devem ser inteiros
  - `or`: Se qualquer um não for inteiro, erro
- `no.tipo_expressao = 'inteiro'`: Anota tipo na AST
- `return 'inteiro'`: Retorna tipo resultante

**b) Operadores lógicos (`e`, `ou`):**
- `elif operador in ['e', 'ou']`: Verifica se é lógico
- `if tipo_esquerda != 'booleano' or tipo_direita != 'booleano'`: Ambos devem ser booleanos
- `no.tipo_expressao = 'booleano'`: Anota tipo
- `return 'booleano'`: Retorna tipo booleano

**c) Operadores relacionais (`=`, `!=`, `<`, `<=`, `>`, `>=`):**
- `elif operador in [...]`: Verifica se é relacional
- `if tipo_esquerda != tipo_direita`: Devem ser do mesmo tipo
  - Permite comparar inteiros com inteiros OU booleanos com booleanos
- `if operador in ['<', '<=', '>', '>='] and tipo_esquerda != 'inteiro'`: 
  - Operadores de ordem (`<`, `>`, etc.) requerem inteiros
  - Operadores de igualdade (`=`, `!=`) podem comparar booleanos também
- `no.tipo_expressao = 'booleano'`: Comparações sempre retornam booleano
- `return 'booleano'`: Retorna tipo booleano

**3. Erro:**
- `else`: Operador desconhecido (não deveria acontecer se AST está correta)

**Exemplo de execução:**
```python
# Expressão: 5 + 3
# tipo_esquerda = "inteiro", tipo_direita = "inteiro"
# operador = "+"
# Verifica: ambos inteiros ✓
# Retorna: "inteiro"

# Expressão: verdadeiro e falso
# tipo_esquerda = "booleano", tipo_direita = "booleano"
# operador = "e"
# Verifica: ambos booleanos ✓
# Retorna: "booleano"

# Expressão: 5 < 3
# tipo_esquerda = "inteiro", tipo_direita = "inteiro"
# operador = "<"
# Verifica: mesmo tipo ✓, ambos inteiros ✓
# Retorna: "booleano"

# Expressão: 5 e verdadeiro
# tipo_esquerda = "inteiro", tipo_direita = "booleano"
# operador = "e"
# Verifica: ambos booleanos? ✗ ERRO
```

### Método `analisa_identificador` - Análise Detalhada

```python
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
```

**Explicação linha por linha:**
- `simbolo = self.tabela_simbolos.buscar(no.nome)`: Busca identificador na tabela
- `if simbolo is None`: Verifica se não foi encontrado
  - `raise ErroSemantico(...)`: Erro se não declarado
- `if simbolo.categoria == 'procedimento'`: Verifica se é procedimento
  - `raise ErroSemantico(...)`: Erro (procedimentos não podem aparecer em expressões)
  - Procedimentos são chamados como comandos, não expressões
- `no.tipo_expressao = simbolo.tipo`: Anota tipo na AST
  - Tipo do identificador = tipo do símbolo encontrado
- `return simbolo.tipo`: Retorna tipo

**Por que verificar categoria:**
- Variáveis: podem aparecer em expressões (retornam seu valor)
- Funções: podem aparecer em expressões (retornam valor de retorno)
- Procedimentos: NÃO podem aparecer em expressões (são comandos)

### Método `_processar_bloco` - Análise Detalhada

```python
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
```

**Explicação linha por linha:**

**Ordem de processamento (importante!):**

**1. Reservar retornos de funções:**
- `for func in bloco.funcoes`: Itera sobre funções aninhadas
- `self.tabela_simbolos.declarar_retorno_funcao(...)`: Declara função ANTES de processar
  - Necessário porque função pode ser chamada antes de ser definida (em alguns casos)
  - Reserva espaço para retorno

**2. Declarar variáveis locais:**
- `if bloco.declaracoes_variaveis`: Verifica se há declarações
- `self.analisa_declaracoes_variaveis(...)`: Declara todas as variáveis
  - Variáveis são declaradas antes de serem usadas

**3. Declarar procedimentos:**
- `for proc in bloco.procedimentos`: Itera sobre procedimentos aninhados
- `self.tabela_simbolos.declarar_procedimento(...)`: Declara procedimento
  - Procedimentos não precisam de espaço de memória (apenas nome)

**4. Processar subrotinas recursivamente:**
- `for func in bloco.funcoes: self.analisa_funcao(func)`: Analisa cada função
  - `analisa_funcao()` entra em novo escopo e processa bloco da função
- `for proc in bloco.procedimentos: self.analisa_procedimento(proc)`: Analisa cada procedimento
  - Similar a funções, mas sem retorno

**5. Analisar comandos:**
- `self.analisa_comando_composto(...)`: Analisa comandos do bloco atual
  - Comandos são analisados por último (após todas as declarações)

**Por que essa ordem:**
1. Funções primeiro: podem ser chamadas antes de serem definidas
2. Variáveis: devem ser declaradas antes de uso
3. Procedimentos: declarados antes de uso
4. Subrotinas processadas: analisa seus corpos recursivamente
5. Comandos: analisados por último (podem usar tudo declarado acima)

## Relação com as Notas de Aula

### Tarefas da Análise Semântica

Conforme as notas de aula (seção 6.3), o analisador semântico realiza:

1. **Verificação de duplicidade**: Implementado em `declarar()` da tabela de símbolos
2. **Verificação de uso não declarado**: Implementado em `buscar()` antes de usar identificador
3. **Verificação de compatibilidade de tipos**: Implementado em `analisa_atribuicao()` e `analisa_operacao_binaria()`
4. **Verificação de comandos**: Implementado em `analisa_comando_leitura()`, `analisa_comando_escrita()`, etc.
5. **Verificação de operadores**: Implementado em `analisa_operacao_unaria()` e `analisa_operacao_binaria()`

### Gramática com Atributos

Conforme as notas de aula (seção 6.1):
- Ações semânticas são executadas durante a análise da AST
- Atributos (tipos) são propagados pela árvore
- A tabela de símbolos armazena informações sobre identificadores

A implementação segue esse modelo:
- Tipos são inferidos e anotados na AST (`tipo_expressao`)
- A tabela de símbolos é populada durante a análise
- Verificações são feitas conforme a árvore é percorrida

### Escopos e Visibilidade

Conforme as notas de aula (seção 4.3):
- Símbolos locais são visíveis apenas em seu escopo
- Símbolos externos são visíveis em escopos internos
- Shadowing: definição mais interna prevalece

A implementação gerencia escopos através de `entrar_escopo()` e `sair_escopo()` da tabela de símbolos, garantindo visibilidade correta.

