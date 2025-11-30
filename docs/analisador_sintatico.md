# Analisador Sintático - Documentação

## Introdução e Teoria

### Base Teórica

O **Analisador Sintático** (também chamado de **Parser**) é a segunda fase do processo de compilação. Conforme as notas de aula (seção 1.3 e 5), sua principal função é verificar se a sequência de tokens fornecida pelo analisador léxico está de acordo com a gramática da linguagem LPD e construir a **Árvore Sintática Abstrata (AST)**.

#### Funções do Analisador Sintático

Segundo as notas de aula, o analisador sintático:
1. **Verifica a ordem de apresentação**: Confirma que os tokens seguem as regras gramaticais
2. **Constrói a árvore sintática**: Monta a estrutura hierárquica do programa
3. **Detecta erros sintáticos**: Identifica violações das regras gramaticais
4. **Reporta erros**: Informa claramente onde e qual erro foi encontrado

### Análise Sintática Descendente

O analisador implementado utiliza **análise sintática descendente** (top-down), conforme descrito nas notas de aula (seção 5.3). Neste método:
- A análise parte da **raiz** da árvore (símbolo inicial da gramática)
- Segue em direção às **folhas** (tokens)
- Substitui símbolos não-terminais até obter a sequência de tokens desejada

#### Gramáticas LL(1)

O analisador implementa uma estratégia de **parsing recursivo descendente** adequada para gramáticas LL(1):
- **L** (Left): Lê a entrada da esquerda para a direita
- **L** (Leftmost): Usa derivações mais à esquerda
- **1**: Olha apenas 1 token à frente para decidir qual produção usar

Nas gramáticas LL(1), cada regra de derivação apresenta símbolo inicial diferenciado, facilitando a escolha da produção correta.

### Gramática da Linguagem LPD

A gramática LPD segue a BNF descrita nas notas de aula (seção 2.1):

```
<programa> ::= programa <identificador> ; <bloco> .
<bloco> ::= [<declaração de variáveis>] [<declaração de subrotinas>] <comandos>
<comandos> ::= inicio <comando> {";" <comando>} [;] fim
```

## Estrutura do Código

### Classe Principal: `AnalisadorSintatico`

A classe `AnalisadorSintatico` implementa o parser recursivo descendente para LPD.

#### Atributos da Classe

```python
def __init__(self, tokens: List[Token]):
    self.tokens = tokens          # Lista completa de tokens
    self.posicao = 0              # Posição atual na lista de tokens
    self.atual = tokens[0]        # Token atual sendo analisado
```

### Métodos Auxiliares

#### `avancar()`

Avança para o próximo token na lista, atualizando `posicao` e `atual`.

**Uso:** Consome tokens durante o parsing.

#### `espiar(deslocamento: int = 1) -> Optional[Token]`

Olha adiante na lista de tokens sem consumir o token atual.

**Parâmetros:**
- `deslocamento`: Quantos tokens à frente olhar (padrão: 1)

**Retorno:** Token na posição especificada ou `None` se estiver além do fim

**Uso:** Essencial para decidir qual produção usar (lookahead).

#### `esperar(tipo_token: TipoToken, mensagem: str = None) -> Token`

Consome um token do tipo esperado ou lança `ErroSintatico`.

**Parâmetros:**
- `tipo_token`: Tipo de token esperado
- `mensagem`: Mensagem de erro personalizada (opcional)

**Retorno:** Token consumido

**Erros:**
- `ErroSintatico`: Se o token atual não corresponde ao esperado

**Uso:** Garante que tokens obrigatórios estejam presentes.

#### `corresponde(*tipos_token: TipoToken) -> bool`

Verifica se o token atual é de um dos tipos fornecidos.

**Parâmetros:**
- `*tipos_token`: Um ou mais tipos de token para verificar

**Retorno:** `True` se corresponde, `False` caso contrário

**Uso:** Decisões condicionais no parsing.

## Detalhamento das Funções de Parsing

### Método Principal

#### `analisar() -> Programa`

Ponto de entrada do analisador sintático. Inicia o parsing do programa completo.

**Retorno:** Nó `Programa` representando a AST completa

**Processo:**
1. Chama `programa()` para analisar o programa completo
2. Retorna a AST construída

### Parsing do Programa

#### `programa() -> Programa`

Analisa a estrutura completa do programa conforme a gramática:
```
programa ::= "programa" ID ";" bloco "."
```

**Processo:**
1. Espera token `PROGRAMA`
2. Espera token `IDENTIFICADOR` (nome do programa)
3. Espera token `PONTO_VIRGULA`
4. Chama `bloco()` para analisar o bloco principal
5. Espera token `PONTO` (final do programa)
6. Retorna nó `Programa` com todas as informações

**Retorno:** `Programa` com nome, declarações, subrotinas e comandos

#### `bloco() -> Bloco`

Analisa um bloco de código conforme a gramática:
```
bloco ::= [declaracao_variaveis] [declaracao_subrotinas] comando_composto
```

**Processo:**
1. Se encontrar `VAR`, chama `declaracao_variaveis()`
2. Enquanto encontrar `PROCEDIMENTO` ou `FUNCAO`, analisa subrotinas
3. Chama `comando_composto()` (obrigatório)
4. Retorna nó `Bloco` completo

**Retorno:** `Bloco` com declarações, subrotinas e comandos

### Parsing de Declarações

#### `declaracao_variaveis() -> DeclaracoesVariaveis`

Analisa seção `var` conforme a gramática:
```
declaracao_variaveis ::= "var" declaracao {";" declaracao} ";"
```

**Processo:**
1. Espera token `VAR`
2. Analisa primeira declaração
3. Espera `PONTO_VIRGULA`
4. Enquanto encontrar `IDENTIFICADOR`, continua analisando declarações
5. Retorna lista de declarações

**Retorno:** `DeclaracoesVariaveis` com lista de declarações

#### `declaracao() -> DeclaracaoVariavel`

Analisa uma declaração de variáveis:
```
declaracao ::= lista_ids ":" tipo
lista_ids ::= ID {"," ID}
```

**Processo:**
1. Lê primeiro identificador
2. Enquanto encontrar `VIRGULA`, lê mais identificadores
3. Espera `DOIS_PONTOS`
4. Chama `tipo()` para obter o tipo
5. Retorna declaração com lista de identificadores e tipo

**Retorno:** `DeclaracaoVariavel` com identificadores e tipo

#### `tipo() -> str`

Analisa tipo de variável:
```
tipo ::= "inteiro" | "booleano"
```

**Retorno:** String `"inteiro"` ou `"booleano"`

**Erros:**
- `ErroSintatico`: Se não encontrar tipo válido

### Parsing de Subrotinas

#### `declaracao_procedimento() -> Procedimento`

Analisa declaração de procedimento:
```
declaracao_procedimento ::= "procedimento" ID [ "(" lista_parametros ")" ] ";" bloco ";"
```

**Processo:**
1. Espera `PROCEDIMENTO`
2. Espera `IDENTIFICADOR` (nome)
3. Se encontrar `ABRE_PARENTESES`, analisa parâmetros
4. Espera `PONTO_VIRGULA`
5. Analisa bloco do procedimento
6. Espera `PONTO_VIRGULA` após `fim`
7. Retorna nó `Procedimento`

**Retorno:** `Procedimento` com nome, parâmetros e bloco

#### `declaracao_funcao() -> Funcao`

Analisa declaração de função:
```
declaracao_funcao ::= "funcao" ID [ "(" lista_parametros ")" ] ":" tipo ";" bloco ";"
```

**Processo:**
1. Espera `FUNCAO`
2. Espera `IDENTIFICADOR` (nome)
3. Se encontrar `ABRE_PARENTESES`, analisa parâmetros
4. Espera `DOIS_PONTOS`
5. Analisa tipo de retorno
6. Espera `PONTO_VIRGULA`
7. Analisa bloco da função
8. Espera `PONTO_VIRGULA` após `fim`
9. Retorna nó `Funcao`

**Retorno:** `Funcao` com nome, parâmetros, tipo de retorno e bloco

#### `lista_parametros() -> List[Parametro]`

Analisa lista de parâmetros:
```
lista_parametros ::= "(" parametro { ";" parametro } ")"
```

**Retorno:** Lista de `Parametro`

#### `parametro() -> Parametro`

Analisa um parâmetro:
```
parametro ::= lista_ids ":" tipo
```

**Retorno:** `Parametro` com identificadores e tipo

### Parsing de Comandos

#### `comando_composto() -> ComandoComposto`

Analisa sequência de comandos:
```
comando_composto ::= "inicio" comandos "fim"
comandos ::= comando {";" comando}
```

**Processo:**
1. Espera `INICIO`
2. Se não encontrar `FIM` imediatamente, analisa primeiro comando
3. Enquanto encontrar `PONTO_VIRGULA`:
   - Se não for `FIM`, analisa próximo comando
4. Espera `FIM`
5. Retorna nó `ComandoComposto`

**Retorno:** `ComandoComposto` com lista de comandos

#### `comando() -> Comando`

Analisa um comando individual. Usa lookahead para decidir qual tipo de comando:
- `IDENTIFICADOR` + `ATRIBUICAO` → Atribuição
- `IDENTIFICADOR` → Chamada de procedimento
- `LEIA` → Comando de leitura
- `ESCREVA` → Comando de escrita
- `SE` → Comando condicional
- `ENQUANTO` → Comando de repetição
- `INICIO` → Comando composto

**Retorno:** Nó `Comando` (subclasse apropriada)

#### `atribuicao() -> Atribuicao`

Analisa comando de atribuição:
```
atribuicao ::= ID ":=" expressao
```

**Retorno:** `Atribuicao` com identificador e expressão

#### `leitura() -> ComandoLeitura`

Analisa comando de leitura:
```
leitura ::= "leia" "(" ID ")"
```

**Retorno:** `ComandoLeitura` com identificador

#### `escrita() -> ComandoEscrita`

Analisa comando de escrita:
```
escrita ::= "escreva" "(" expressao ")"
```

**Retorno:** `ComandoEscrita` com expressão

#### `condicional() -> ComandoSe`

Analisa comando condicional:
```
condicional ::= "se" expressao "entao" comando ["senao" comando]
```

**Processo:**
1. Espera `SE`
2. Analisa expressão (condição)
3. Espera `ENTAO`
4. Analisa comando do `entao`
5. Se encontrar `SENAO`, analisa comando do `senao`
6. Retorna nó `ComandoSe`

**Retorno:** `ComandoSe` com condição e comandos

#### `repeticao() -> ComandoEnquanto`

Analisa comando de repetição:
```
repeticao ::= "enquanto" expressao "faca" comando
```

**Retorno:** `ComandoEnquanto` com condição e corpo

#### `chamada_procedimento() -> ChamadaProcedimento`

Analisa chamada de procedimento:
```
chamada_procedimento ::= ID ["(" lista_argumentos ")"]
lista_argumentos ::= expressao { "," expressao }
```

**Retorno:** `ChamadaProcedimento` com nome e argumentos

### Parsing de Expressões

A análise de expressões segue a precedência de operadores:

#### Precedência (da mais alta para mais baixa):
1. **Fatores**: Identificadores, números, booleanos, parênteses, negação
2. **Termos**: Multiplicação, divisão, `e` (lógico)
3. **Expressões simples**: Adição, subtração, `ou` (lógico)
4. **Expressões**: Operadores relacionais

#### `expressao() -> Expressao`

Analisa expressão completa:
```
expressao ::= expressao_simples [op_relacional expressao_simples]
op_relacional ::= "=" | "!=" | "<" | "<=" | ">" | ">="
```

**Retorno:** `Expressao` (pode ser `OperacaoBinaria` ou `expressao_simples`)

#### `expressao_simples() -> Expressao`

Analisa expressão simples:
```
expressao_simples ::= ["+"|"-"] termo {("+"|"-"|"ou") termo}
```

**Processo:**
1. Se encontrar `+` ou `-`, trata como sinal unário
2. Analisa primeiro termo
3. Enquanto encontrar `+`, `-` ou `ou`, analisa mais termos
4. Constrói árvore de operações binárias

**Retorno:** `Expressao` (pode ser `OperacaoUnaria` ou `OperacaoBinaria`)

#### `termo() -> Expressao`

Analisa termo:
```
termo ::= fator {("*"|"div"|"e") fator}
```

**Retorno:** `Expressao` (pode ser `fator` ou `OperacaoBinaria`)

#### `fator() -> Expressao`

Analisa fator:
```
fator ::= ID | NUM | "(" expressao ")" | "nao" fator | "verdadeiro" | "falso"
```

**Processo:**
1. Se `IDENTIFICADOR` → retorna `Identificador`
2. Se `NUMERO` → retorna `Numero`
3. Se `VERDADEIRO` → retorna `Booleano(True)`
4. Se `FALSO` → retorna `Booleano(False)`
5. Se `NAO` → retorna `OperacaoUnaria('nao', fator())`
6. Se `ABRE_PARENTESES` → analisa expressão e espera `FECHA_PARENTESES`

**Retorno:** `Expressao` (subclasse apropriada)

## Integração

### Uso pelo Compilador Principal

O `compilador.py` utiliza o analisador sintático assim:

```python
tokens = AnalisadorLexico(codigo_fonte).obter_tokens()
ast = AnalisadorSintatico(tokens).analisar()
```

### Fluxo de Dados

```
Lista de Tokens (Token[])
    ↓
AnalisadorSintatico(tokens).analisar()
    ↓
AST (Programa)
    ↓
AnalisadorSemantico.analisar(ast)
    ↓
AST Anotada + Tabela de Símbolos
```

### Dependências

- **`tokens`**: Importa `Token`, `TipoToken`, `ErroSintatico`
- **`arvore_sintatica`**: Importa todas as classes de nós da AST

### Tratamento de Erros

O analisador sintático lança `ErroSintatico` quando:
- Token esperado não é encontrado
- Sequência de tokens não corresponde à gramática
- Estrutura sintática está incorreta

A implementação atual **interrompe a compilação** ao encontrar um erro (conforme notas de aula, seção 5.6).

## Exemplos Práticos

### Exemplo 1: Parsing de Programa Simples

```python
from analisador_lexico import AnalisadorLexico
from analisador_sintatico import AnalisadorSintatico

codigo = """
programa exemplo;
var x: inteiro;
inicio
    x := 42;
fim.
"""

tokens = AnalisadorLexico(codigo).obter_tokens()
ast = AnalisadorSintatico(tokens).analisar()

print(f"Programa: {ast.nome}")
print(f"Variáveis globais: {len(ast.declaracoes_variaveis.declaracoes)}")
```

### Exemplo 2: Parsing de Expressão Aritmética

O analisador sintático constrói a AST respeitando a precedência:

```python
# Código: x := a + b * c
# AST construída:
Atribuicao(
    identificador="x",
    expressao=OperacaoBinaria(
        esquerda=Identificador("a"),
        operador="+",
        direita=OperacaoBinaria(
            esquerda=Identificador("b"),
            operador="*",
            direita=Identificador("c")
        )
    )
)
```

A precedência é respeitada: `*` tem precedência sobre `+`, então `b * c` fica como filho direito da adição.

### Exemplo 3: Tratamento de Erro Sintático

```python
codigo = "programa teste; var x: inteiro; inicio x := fim."

try:
    tokens = AnalisadorLexico(codigo).obter_tokens()
    ast = AnalisadorSintatico(tokens).analisar()
except ErroSintatico as e:
    print(f"Erro sintático: {e}")
```

**Saída:** `Erro sintático: [1:45] Esperado expressão, encontrado FIM`

## Análise Detalhada do Código

### Método `__init__`

```python
def __init__(self, tokens: List[Token]):
    self.tokens = tokens
    self.posicao = 0
    self.atual = tokens[0] if tokens else None
```

**Explicação linha por linha:**
- `self.tokens = tokens`: Armazena lista completa de tokens recebida do analisador léxico
- `self.posicao = 0`: Inicializa posição no primeiro token (índice 0)
- `self.atual = tokens[0] if tokens else None`: 
  - Se há tokens, pega o primeiro como token atual
  - Se lista vazia, `atual` é `None` (evita IndexError)

**Por que armazenar tokens completos:**
- Permite acesso aleatório (`tokens[posicao]`)
- Permite lookahead (`espiar()`)
- Mais simples que consumir tokens sob demanda

### Método `avancar`

```python
def avancar(self):
    """Avança para o próximo token."""
    if self.posicao < len(self.tokens) - 1:
        self.posicao += 1
        self.atual = self.tokens[self.posicao]
```

**Explicação linha por linha:**
- `if self.posicao < len(self.tokens) - 1`: Verifica se não está no último token
  - `len(self.tokens) - 1` é o índice do último token
  - Se `posicao` já está no último, não avança (evita IndexError)
- `self.posicao += 1`: Incrementa posição
- `self.atual = self.tokens[self.posicao]`: Atualiza token atual

**Por que verificar antes de avançar:**
- Evita `IndexError` ao tentar acessar token inexistente
- `atual` permanece no último token quando chega ao fim

### Método `espiar`

```python
def espiar(self, deslocamento: int = 1) -> Optional[Token]:
    """Olha adiante sem consumir tokens."""
    indice = self.posicao + deslocamento
    if indice < len(self.tokens):
        return self.tokens[indice]
    return None
```

**Explicação linha por linha:**
- `indice = self.posicao + deslocamento`: Calcula índice do token a olhar
  - `deslocamento=1` (padrão): próximo token
  - `deslocamento=2`: dois tokens à frente
- `if indice < len(self.tokens)`: Verifica se índice é válido
- `return self.tokens[indice]`: Retorna token naquela posição
- `return None`: Se índice inválido (fim da lista)

**Uso típico:**
```python
# Decidir entre atribuição e chamada de procedimento
if self.atual.tipo == TipoToken.IDENTIFICADOR:
    proximo = self.espiar()  # Olha próximo token
    if proximo and proximo.tipo == TipoToken.ATRIBUICAO:
        # É atribuição: x := ...
    else:
        # É chamada: x(...)
```

### Método `esperar`

```python
def esperar(self, tipo_token: TipoToken, mensagem: str = None) -> Token:
    """Consome um token do tipo esperado ou lança erro."""
    if self.atual.tipo != tipo_token:
        if mensagem is None:
            mensagem = f"Esperado {tipo_token.name}, encontrado {self.atual.tipo.name}"
        raise ErroSintatico(mensagem, self.atual.linha, self.atual.coluna)
    token = self.atual
    self.avancar()
    return token
```

**Explicação linha por linha:**
- `if self.atual.tipo != tipo_token`: Verifica se token atual é do tipo esperado
- `if mensagem is None`: Se não forneceu mensagem personalizada
  - `mensagem = f"Esperado {tipo_token.name}, encontrado {self.atual.tipo.name}"`: Gera mensagem padrão
- `raise ErroSintatico(...)`: Lança erro se tipo não corresponde
- `token = self.atual`: Salva token atual antes de avançar
- `self.avancar()`: Consome o token (avança)
- `return token`: Retorna token consumido

**Por que usar `esperar`:**
- Garante que tokens obrigatórios estão presentes
- Gera erros descritivos automaticamente
- Simplifica código (não precisa verificar e avançar separadamente)

**Exemplo:**
```python
# Espera token PROGRAMA
self.esperar(TipoToken.PROGRAMA, "Esperado 'programa'")
# Se não for PROGRAMA, lança ErroSintatico
# Se for, consome e continua
```

### Método `corresponde`

```python
def corresponde(self, *tipos_token: TipoToken) -> bool:
    """Verifica se o token atual é de um dos tipos dados."""
    return self.atual.tipo in tipos_token
```

**Explicação:**
- `*tipos_token`: Aceita múltiplos argumentos (varargs)
- `self.atual.tipo in tipos_token`: Verifica se tipo atual está na tupla de tipos
- Retorna `True` se corresponde, `False` caso contrário

**Uso:**
```python
# Verifica se é PROCEDIMENTO ou FUNCAO
if self.corresponde(TipoToken.PROCEDIMENTO, TipoToken.FUNCAO):
    # Processa subrotina
```

### Método `programa` - Análise Detalhada

```python
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
```

**Explicação linha por linha:**

**Gramática correspondente:**
```
programa ::= "programa" ID ";" bloco "."
```

**Processamento:**
1. `self.esperar(TipoToken.PROGRAMA, ...)`: Espera e consome token `programa`
   - Se não encontrar, lança erro: "Esperado 'programa'"
2. `token_nome = self.esperar(TipoToken.IDENTIFICADOR, ...)`: Espera identificador (nome do programa)
   - `token_nome` contém o token com o nome
3. `nome = token_nome.valor`: Extrai valor do token (string com nome)
   - `valor` foi preenchido pelo analisador léxico
4. `self.esperar(TipoToken.PONTO_VIRGULA, ...)`: Espera `;` após nome
5. `bloco = self.bloco()`: Chama método recursivo para analisar bloco
   - Retorna nó `Bloco` com declarações, subrotinas e comandos
6. `self.esperar(TipoToken.PONTO, ...)`: Espera `.` no final
7. `return Programa(...)`: Cria e retorna nó raiz da AST
   - Extrai componentes do bloco para estrutura do programa

**Estrutura retornada:**
- `nome`: Nome do programa (string)
- `declaracoes_variaveis`: Declarações globais (do bloco)
- `procedimentos`: Lista de procedimentos globais (do bloco)
- `funcoes`: Lista de funções globais (do bloco)
- `comando_composto`: Corpo principal (do bloco)

### Método `bloco` - Análise Detalhada

```python
def bloco(self) -> Bloco:
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
```

**Explicação linha por linha:**

**Gramática correspondente:**
```
bloco ::= [declaracao_variaveis] [declaracao_subrotinas] comando_composto
```

**Processamento:**

1. **Declarações de variáveis (opcional):**
   - `declaracoes_var = None`: Inicializa como None (pode não haver)
   - `if self.corresponde(TipoToken.VAR)`: Verifica se há token `var`
     - `corresponde()` não consome token (apenas verifica)
   - `declaracoes_var = self.declaracao_variaveis()`: Se há `var`, analisa declarações
     - Método consome o token `var` e processa declarações

2. **Subrotinas (zero ou mais):**
   - `procedimentos: List[Procedimento] = []`: Lista vazia
   - `funcoes: List[Funcao] = []`: Lista vazia
   - `while self.corresponde(TipoToken.PROCEDIMENTO, TipoToken.FUNCAO)`: Enquanto houver subrotinas
     - `if self.corresponde(TipoToken.PROCEDIMENTO)`: Se é procedimento
       - `procedimentos.append(self.declaracao_procedimento())`: Analisa e adiciona
     - `else`: Caso contrário é função
       - `funcoes.append(self.declaracao_funcao())`: Analisa e adiciona
   - Loop continua até não haver mais `PROCEDIMENTO` ou `FUNCAO`

3. **Comando composto (obrigatório):**
   - `comando_comp = self.comando_composto()`: Analisa comandos entre `inicio` e `fim`
   - Sempre deve haver (obrigatório na gramática)

4. **Retorno:**
   - `return Bloco(...)`: Cria nó Bloco com todos os componentes

**Por que usar `corresponde()` antes de chamar métodos:**
- `corresponde()` não consome token (apenas verifica)
- Permite decidir qual método chamar sem consumir token incorretamente
- Métodos especializados (`declaracao_variaveis()`, etc.) consomem seus próprios tokens

### Método `expressao` - Análise Detalhada

```python
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
            # ... mais mapeamentos
        }
        
        return OperacaoBinaria(esquerda=esquerda, operador=mapa_op[token_op.tipo], direita=direita)
    
    return esquerda
```

**Explicação linha por linha:**

**Gramática correspondente:**
```
expressao ::= expressao_simples [op_relacional expressao_simples]
```

**Processamento:**

1. **Analisa expressão simples:**
   - `esquerda = self.expressao_simples()`: Analisa primeira expressão simples
   - Pode ser número, variável, operação aritmética, etc.

2. **Verifica operador relacional (opcional):**
   - `if self.corresponde(...)`: Verifica se há operador relacional
   - Se não houver, retorna apenas `esquerda` (expressão simples)

3. **Se há operador relacional:**
   - `token_op = self.atual`: Salva token do operador
   - `self.avancar()`: Consome operador
   - `direita = self.expressao_simples()`: Analisa segunda expressão simples
   - `mapa_op = {...}`: Mapeia tipo de token para string do operador
   - `return OperacaoBinaria(...)`: Cria nó de operação binária

**Árvore construída:**
```
OperacaoBinaria
├── esquerda: Expressao (expressão simples)
├── operador: str ('=', '!=', '<', etc.)
└── direita: Expressao (expressão simples)
```

**Por que mapear para string:**
- AST armazena operador como string (mais flexível)
- Facilita geração de código posterior
- Independente de enumeração de tokens

### Método `expressao_simples` - Análise Detalhada

```python
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
```

**Explicação linha por linha:**

**Gramática correspondente:**
```
expressao_simples ::= ["+"|"-"] termo {("+"|"-"|"ou") termo}
```

**Processamento:**

1. **Sinal unário opcional:**
   - `if self.corresponde(TipoToken.MAIS, TipoToken.MENOS)`: Verifica sinal unário
   - `sinal = self.atual`: Salva token do sinal
   - `self.avancar()`: Consome sinal
   - `if sinal.tipo == TipoToken.MENOS`: Se é menos unário
     - `operando = self.termo()`: Analisa termo
     - `expressao = OperacaoUnaria(operador='-', operando=operando)`: Cria operação unária
   - `else`: Se é `+` unário
     - `expressao = self.termo()`: Ignora `+` (não cria nó, apenas analisa termo)
   - `else`: Sem sinal unário
     - `expressao = self.termo()`: Analisa termo diretamente

2. **Operadores aditivos e 'ou' (zero ou mais):**
   - `while self.corresponde(...)`: Enquanto houver `+`, `-` ou `ou`
   - `token_op = self.atual`: Salva operador
   - `self.avancar()`: Consome operador
   - `direita = self.termo()`: Analisa próximo termo
   - `expressao = OperacaoBinaria(...)`: Reconstrói árvore com nova operação
     - `esquerda=expressao`: Expressão acumulada até agora
     - `operador=mapa_op[token_op.tipo]`: Operador atual
     - `direita=direita`: Novo termo

**Árvore construída (exemplo: `a + b - c`):**
```
OperacaoBinaria('-',
    OperacaoBinaria('+',
        Identificador('a'),
        Identificador('b')
    ),
    Identificador('c')
)
```

**Por que reconstruir árvore:**
- Operadores têm associatividade à esquerda (`a + b + c` = `((a + b) + c)`)
- Cada iteração do `while` adiciona novo nível à árvore
- Árvore reflete precedência e associatividade corretas

### Método `termo` - Análise Detalhada

```python
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
```

**Explicação:**
- Similar a `expressao_simples()`, mas para operadores multiplicativos (`*`, `div`, `e`)
- Processa fatores e constrói árvore de operações
- Operadores têm precedência maior que aditivos (por isso em método separado)

**Precedência de operadores (da mais alta para mais baixa):**
1. Fatores (identificadores, números, parênteses, negação)
2. Termos (`*`, `div`, `e`)
3. Expressões simples (`+`, `-`, `ou`)
4. Expressões (operadores relacionais)

### Método `fator` - Análise Detalhada

```python
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
```

**Explicação linha por linha:**

**Gramática correspondente:**
```
fator ::= ID | NUM | "(" expressao ")" | "nao" fator | "verdadeiro" | "falso"
```

**Processamento (ordem de verificação):**

1. **Identificador:**
   - `if self.corresponde(TipoToken.IDENTIFICADOR)`: Verifica se é identificador
   - `token_id = self.atual`: Salva token
   - `self.avancar()`: Consome token
   - `return Identificador(nome=token_id.valor)`: Cria nó com nome

2. **Número:**
   - Similar a identificador, mas retorna `Numero(valor=token_num.valor)`

3. **Booleanos:**
   - `VERDADEIRO` → `Booleano(valor=True)`
   - `FALSO` → `Booleano(valor=False)`

4. **Negação lógica:**
   - `elif self.corresponde(TipoToken.NAO)`: Verifica operador `nao`
   - `self.avancar()`: Consome `nao`
   - `operando = self.fator()`: **Recursão!** Analisa fator (pode ser outro `nao`)
   - `return OperacaoUnaria(operador='nao', operando=operando)`: Cria operação unária

5. **Parênteses:**
   - `elif self.corresponde(TipoToken.ABRE_PARENTESES)`: Verifica `(`
   - `self.avancar()`: Consome `(`
   - `expressao = self.expressao()`: **Recursão!** Analisa expressão completa
   - `self.esperar(TipoToken.FECHA_PARENTESES, ...)`: Espera `)`
   - `return expressao`: Retorna expressão (sem criar nó extra)

6. **Erro:**
   - Se nenhum padrão correspondeu, lança erro

**Por que recursão em `nao` e parênteses:**
- `nao fator`: Permite `nao nao x` (negação dupla)
- `(expressao)`: Permite expressões aninhadas `(a + (b * c))`
- Recursão naturalmente lida com aninhamento arbitrário

## Relação com as Notas de Aula

### Algoritmo do Analisador Sintático

As notas de aula (seção 5.6) apresentam algoritmos pseudocódigo para o analisador sintático do CSD. A implementação Python segue esses algoritmos:

1. **Algoritmo `<programa>`**: Implementado em `programa()`
2. **Algoritmo `<bloco>`**: Implementado em `bloco()`
3. **Algoritmo `<comandos>`**: Implementado em `comando_composto()`
4. **Algoritmo `<comando>`**: Implementado em `comando()`
5. **Algoritmo `<expressao>`**: Implementado em `expressao()`, `expressao_simples()`, `termo()`, `fator()`

### Análise Descendente Recursiva

A implementação utiliza análise descendente recursiva, conforme descrito nas notas de aula (seção 5.3):
- Cada não-terminal da gramática vira um método
- Métodos chamam outros métodos recursivamente
- Tokens terminais são consumidos diretamente

### Tratamento de Erros

Conforme as notas de aula (seção 5.4), o analisador:
- Detecta erros tão logo possível (propriedade do prefixo viável)
- Reporta erros com linha e coluna
- Interrompe compilação ao encontrar erro (conforme seção 5.6)

A implementação atual não realiza recuperação de erros avançada, apenas reporta e interrompe, o que é adequado para um ambiente interativo moderno.

