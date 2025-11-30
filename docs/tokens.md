# Módulo Tokens - Documentação

## Introdução e Teoria

### Base Teórica

O módulo `tokens.py` implementa a definição fundamental dos **tokens** (átomos) da linguagem LPD. Conforme as notas de aula, o Analisador Léxico tem como função fragmentar o programa fonte em componentes básicos e completos chamados tokens.

Segundo as notas de aula:
- **Token**: É um símbolo terminal da gramática que representa uma classe de lexemas
- **Lexema**: É a sequência de caracteres no programa-fonte que corresponde ao padrão de um token
- **Padrão**: É a descrição da forma que os lexemas de um token podem ter

O Analisador Léxico converte a sequência de caracteres do programa fonte em uma sequência de tokens que o analisador sintático utilizará. Cada token possui:
- Um **tipo** (classe do token)
- Um **lexema** (sequência de caracteres reconhecida)
- **Atributos** (informações adicionais como valor numérico, nome do identificador, etc.)

### Tokens na Linguagem LPD

A linguagem LPD possui os seguintes tipos de tokens:
- **Palavras reservadas**: `programa`, `var`, `inicio`, `fim`, `procedimento`, `funcao`, `enquanto`, `faca`, `se`, `entao`, `senao`, `leia`, `escreva`, `inteiro`, `booleano`, `verdadeiro`, `falso`, `e`, `ou`, `nao`, `div`
- **Operadores**: `:=`, `+`, `-`, `*`, `div`, `=`, `!=`, `<`, `<=`, `>`, `>=`
- **Símbolos estruturais**: `(`, `)`, `:`, `;`, `,`, `.`
- **Identificadores**: Nomes definidos pelo usuário
- **Números**: Literais inteiros
- **Fim de arquivo**: Marcador especial para o final do código

## Estrutura do Código

### Classes e Enumerações

#### `TipoToken` (Enum)

Enumeração que define todos os tipos de tokens possíveis na linguagem LPD. Cada valor representa uma classe de token diferente.

**Valores principais:**
- Tokens estruturais: `PROGRAMA`, `VAR`, `INICIO`, `FIM`, `PROCEDIMENTO`, `FUNCAO`
- Tokens de controle: `ENQUANTO`, `FACA`, `SE`, `ENTAO`, `SENAO`
- Tokens de I/O: `LEIA`, `ESCREVA`
- Tokens de tipo: `INTEIRO`, `BOOLEANO`, `VERDADEIRO`, `FALSO`
- Tokens lógicos: `E`, `OU`, `NAO`
- Tokens de dados: `IDENTIFICADOR`, `NUMERO`
- Operadores: `ATRIBUICAO`, `MAIS`, `MENOS`, `MULTIPLICACAO`, `DIVISAO`, `IGUAL`, `DIFERENTE`, `MENOR`, `MENOR_IGUAL`, `MAIOR`, `MAIOR_IGUAL`
- Símbolos: `ABRE_PARENTESES`, `FECHA_PARENTESES`, `DOIS_PONTOS`, `PONTO_VIRGULA`, `VIRGULA`, `PONTO`
- Especial: `FIM_ARQUIVO`

#### `PALAVRAS_RESERVADAS` (Dict)

Dicionário que mapeia palavras reservadas (em minúsculas) para seus respectivos tipos de token. Permite ao analisador léxico identificar quando um identificador é na verdade uma palavra reservada.

**Exemplo:**
```python
PALAVRAS_RESERVADAS = {
    "programa": TipoToken.PROGRAMA,
    "var": TipoToken.VAR,
    "inicio": TipoToken.INICIO,
    # ... etc
}
```

#### `Token` (dataclass)

Classe que representa um token reconhecido pelo analisador léxico.

**Atributos:**
- `tipo: TipoToken` - Tipo do token (classe)
- `lexema: str` - Sequência de caracteres reconhecida
- `linha: int` - Número da linha onde o token foi encontrado
- `coluna: int` - Número da coluna onde o token foi encontrado
- `valor: Optional[object]` - Valor associado ao token (ex: número inteiro para `NUMERO`, nome para `IDENTIFICADOR`)

**Exemplo de uso:**
```python
# Token de número
Token(TipoToken.NUMERO, "42", linha=5, coluna=10, valor=42)

# Token de identificador
Token(TipoToken.IDENTIFICADOR, "variavel", linha=3, coluna=1, valor="variavel")

# Token de palavra reservada
Token(TipoToken.PROGRAMA, "programa", linha=1, coluna=1)
```

### Classes de Exceção

O módulo define três classes de exceção para tratamento de erros em diferentes fases:

#### `ErroLexico` (Exception)

Exceção lançada quando ocorre um erro durante a análise léxica.

**Atributos:**
- `linha: int` - Linha onde o erro ocorreu
- `coluna: int` - Coluna onde o erro ocorreu

**Uso:**
```python
raise ErroLexico("Caractere inválido: '@'", linha=10, coluna=5)
```

#### `ErroSintatico` (Exception)

Exceção lançada quando ocorre um erro durante a análise sintática.

**Atributos:**
- `linha: int` - Linha onde o erro ocorreu (pode ser 0 se não especificada)
- `coluna: int` - Coluna onde o erro ocorreu (pode ser 0 se não especificada)

**Uso:**
```python
raise ErroSintatico("Esperado ';', encontrado 'fim'", linha=15, coluna=3)
```

#### `ErroSemantico` (Exception)

Exceção lançada quando ocorre um erro durante a análise semântica.

**Atributos:**
- `linha: int` - Linha onde o erro ocorreu (pode ser 0 se não especificada)
- `coluna: int` - Coluna onde o erro ocorreu (pode ser 0 se não especificada)

**Uso:**
```python
raise ErroSemantico("Variável 'x' não foi declarada", linha=8, coluna=2)
```

## Detalhamento das Funções

### Estrutura de Dados

O módulo não possui funções, apenas definições de tipos de dados e estruturas. As principais estruturas são:

1. **Enum `TipoToken`**: Define todos os tipos de tokens usando `auto()` para valores únicos
2. **Dict `PALAVRAS_RESERVADAS`**: Mapeamento estático de palavras reservadas
3. **Dataclass `Token`**: Estrutura imutável para representar tokens
4. **Classes de Exceção**: Hierarquia de erros específicos por fase

## Análise Detalhada do Código

### Enumeração `TipoToken`

```python
class TipoToken(Enum):
    """Enumeração dos tipos de tokens da linguagem LPD."""
    PROGRAMA = auto()
    VAR = auto()
    # ... mais tokens
```

**Explicação do código:**
- `Enum` é uma classe base do Python que permite criar enumerações
- `auto()` gera automaticamente valores únicos sequenciais para cada membro
- Cada token da linguagem LPD tem um valor único na enumeração
- Isso permite comparação eficiente usando `==` ou `in`

**Por que usar Enum:**
- Evita erros de digitação (não pode usar string incorreta)
- Facilita comparações (`token.tipo == TipoToken.PROGRAMA`)
- Melhora legibilidade do código
- Permite iteração sobre todos os tipos

### Dicionário `PALAVRAS_RESERVADAS`

```python
PALAVRAS_RESERVADAS = {
    "programa": TipoToken.PROGRAMA,
    "var": TipoToken.VAR,
    # ... mais mapeamentos
}
```

**Explicação do código:**
- É um dicionário Python (`dict`) que mapeia strings (palavras reservadas em minúsculas) para tipos de token
- As chaves são sempre minúsculas para permitir comparação case-insensitive
- Os valores são membros da enumeração `TipoToken`
- Permite busca O(1) em média para verificar se um identificador é palavra reservada

**Como funciona:**
```python
# Exemplo de uso interno:
lexema_lower = "programa".lower()  # "programa"
if lexema_lower in PALAVRAS_RESERVADAS:
    tipo = PALAVRAS_RESERVADAS[lexema_lower]  # TipoToken.PROGRAMA
```

### Classe `Token` (dataclass)

```python
@dataclass
class Token:
    tipo: TipoToken
    lexema: str
    linha: int
    coluna: int
    valor: Optional[object] = None
```

**Explicação do código:**
- `@dataclass` é um decorador do Python que gera automaticamente:
  - Método `__init__()` com todos os campos
  - Método `__repr__()` para representação em string
  - Método `__eq__()` para comparação de igualdade
- `tipo: TipoToken` - Tipo do token (obrigatório)
- `lexema: str` - Sequência de caracteres reconhecida (obrigatório)
- `linha: int` - Linha onde foi encontrado (obrigatório)
- `coluna: int` - Coluna onde foi encontrado (obrigatório)
- `valor: Optional[object] = None` - Valor opcional (padrão None)

**Criação de instância:**
```python
# Token de número - valor é preenchido
token = Token(TipoToken.NUMERO, "42", linha=1, coluna=10, valor=42)

# Token de palavra reservada - valor é None
token = Token(TipoToken.PROGRAMA, "programa", linha=1, coluna=1)
```

**Vantagens do dataclass:**
- Código mais limpo (não precisa escrever `__init__` manualmente)
- Imutabilidade opcional (pode usar `frozen=True` se necessário)
- Comparação automática de igualdade
- Representação automática para debug

### Classe `ErroLexico`

```python
class ErroLexico(Exception):
    def __init__(self, mensagem: str, linha: int, coluna: int):
        super().__init__(f"[{linha}:{coluna}] {mensagem}")
        self.linha = linha
        self.coluna = coluna
```

**Explicação do código:**
- Herda de `Exception` (classe base de exceções Python)
- `super().__init__()` chama o construtor da classe pai com mensagem formatada
- A mensagem inclui linha e coluna no formato `[linha:coluna] mensagem`
- Armazena `linha` e `coluna` como atributos para acesso posterior

**Como funciona:**
```python
# Quando lançada:
raise ErroLexico("Caractere inválido '@'", linha=5, coluna=10)

# A mensagem será: "[5:10] Caractere inválido '@'"
# E pode acessar: erro.linha  # 5
#                 erro.coluna  # 10
```

**Por que herdar de Exception:**
- Permite usar `try/except` para capturar erros
- Pode ser propagada através de chamadas de função
- Integra com sistema de exceções do Python

### Classe `ErroSintatico`

```python
class ErroSintatico(Exception):
    def __init__(self, mensagem: str, linha: int = 0, coluna: int = 0):
        super().__init__(f"[{linha}:{coluna}] {mensagem}" if linha else mensagem)
        self.linha = linha
        self.coluna = coluna
```

**Explicação do código:**
- Similar a `ErroLexico`, mas linha/coluna são opcionais (padrão 0)
- Usa expressão condicional: `if linha else mensagem`
- Se linha for 0, não inclui `[linha:coluna]` na mensagem
- Útil quando o erro não está associado a uma posição específica

**Diferença de ErroLexico:**
- Erros léxicos sempre têm posição (sempre há um caractere problemático)
- Erros sintáticos podem não ter posição específica (ex: estrutura incorreta)

### Classe `ErroSemantico`

```python
class ErroSemantico(Exception):
    def __init__(self, mensagem: str, linha: int = 0, coluna: int = 0):
        super().__init__(f"[{linha}:{coluna}] {mensagem}" if linha else mensagem)
        self.linha = linha
        self.coluna = coluna
```

**Explicação do código:**
- Idêntica a `ErroSintatico` em estrutura
- Usada para erros semânticos (tipos incompatíveis, variáveis não declaradas, etc.)
- Pode ou não ter posição específica dependendo do contexto

**Hierarquia de erros:**
```
Exception (classe base Python)
├── ErroLexico    (erros de caracteres/tokens)
├── ErroSintatico (erros de estrutura/sintaxe)
└── ErroSemantico (erros de tipos/declarações)
```

Todas herdam de `Exception`, permitindo captura genérica ou específica:
```python
try:
    # código
except ErroLexico as e:
    # trata erro léxico
except (ErroSintatico, ErroSemantico) as e:
    # trata erros sintáticos ou semânticos
```

## Integração

### Uso pelo Analisador Léxico

O módulo `analisador_lexico.py` importa e utiliza:
- `TipoToken` para classificar tokens reconhecidos
- `PALAVRAS_RESERVADAS` para identificar palavras reservadas
- `Token` para criar instâncias de tokens
- `ErroLexico` para reportar erros léxicos

### Uso pelo Analisador Sintático

O módulo `analisador_sintatico.py` importa e utiliza:
- `Token` para trabalhar com tokens
- `TipoToken` para verificar tipos esperados
- `ErroSintatico` para reportar erros sintáticos

### Uso pelo Analisador Semântico

O módulo `analisador_semantico.py` importa e utiliza:
- `ErroSemantico` para reportar erros semânticos

### Fluxo de Dados

```
Código Fonte (string)
    ↓
Analisador Léxico
    ↓
Lista de Tokens (Token[])
    ↓
Analisador Sintático
    ↓
AST (árvore sintática)
    ↓
Analisador Semântico
    ↓
AST Anotada + Tabela de Símbolos
```

## Exemplos Práticos

### Exemplo 1: Token de Número

```python
from tokens import Token, TipoToken

# Criando um token de número
token_numero = Token(
    tipo=TipoToken.NUMERO,
    lexema="42",
    linha=1,
    coluna=10,
    valor=42
)

print(f"Tipo: {token_numero.tipo.name}")
print(f"Lexema: {token_numero.lexema}")
print(f"Valor: {token_numero.valor}")
print(f"Posição: linha {token_numero.linha}, coluna {token_numero.coluna}")
```

### Exemplo 2: Verificação de Palavra Reservada

```python
from tokens import PALAVRAS_RESERVADAS, TipoToken

def verificar_palavra_reservada(lexema: str):
    lexema_lower = lexema.lower()
    if lexema_lower in PALAVRAS_RESERVADAS:
        return PALAVRAS_RESERVADAS[lexema_lower]
    return TipoToken.IDENTIFICADOR

# Teste
print(verificar_palavra_reservada("programa"))  # TipoToken.PROGRAMA
print(verificar_palavra_reservada("minhaVar"))  # TipoToken.IDENTIFICADOR
```

### Exemplo 3: Tratamento de Erros

```python
from tokens import ErroLexico, ErroSintatico, ErroSemantico

# Erro léxico
try:
    raise ErroLexico("Caractere inválido '@'", linha=5, coluna=10)
except ErroLexico as e:
    print(f"Erro léxico: {e}")
    print(f"Linha: {e.linha}, Coluna: {e.coluna}")

# Erro sintático
try:
    raise ErroSintatico("Esperado ';' após declaração", linha=10, coluna=5)
except ErroSintatico as e:
    print(f"Erro sintático: {e}")

# Erro semântico
try:
    raise ErroSemantico("Variável 'x' não declarada", linha=8, coluna=2)
except ErroSemantico as e:
    print(f"Erro semântico: {e}")
```

## Relação com as Notas de Aula

Conforme as notas de aula (seção 3.2 - Tokens, Padrões, Lexemas):

> "Quando se fala sobre a análise Lexical, usamos os termos 'token', 'padrão' e 'lexema'. Existe um conjunto de cadeias de entrada para as quais o mesmo token é produzido como token de entrada. O padrão é dito reconhecer cada cadeia do conjunto. Um lexema é um conjunto de caracteres no programa-fonte que é reconhecido pelo padrão de algum token."

O módulo `tokens.py` implementa exatamente essa definição:
- **Token** = Tipo de símbolo (representado por `TipoToken`)
- **Padrão** = Regras de reconhecimento (implementadas no analisador léxico)
- **Lexema** = Sequência de caracteres reconhecida (atributo `lexema` da classe `Token`)

A estrutura de tokens também segue o padrão descrito nas notas de aula, onde cada token possui atributos que influenciam decisões na análise gramatical e na tradução.

