# Analisador Léxico - Documentação

## Introdução e Teoria

### Base Teórica

O **Analisador Léxico** (também chamado de **Scanner**) é a primeira fase do processo de compilação. Conforme as notas de aula (seção 1.2 e 3.1), sua principal função é fragmentar o programa fonte em componentes básicos e completos chamados **tokens**.

#### Funções do Analisador Léxico

Segundo as notas de aula, o Analisador Léxico cumpre as seguintes tarefas:

1. **Extração e classificação de átomos**: Identifica e classifica os elementos básicos do código fonte
2. **Eliminação de delimitadores e comentários**: Remove espaços em branco e comentários que não são relevantes para a análise sintática
3. **Identificação de palavras reservadas**: Distingue palavras reservadas de identificadores comuns
4. **Recuperação de erros**: Detecta e reporta erros léxicos

#### Interação com Outros Módulos

O Analisador Léxico atua como uma interface entre o texto fonte e o analisador sintático:
- **Entrada**: Sequência de caracteres do programa fonte
- **Saída**: Sequência de tokens (átomos) que são símbolos terminais da gramática

O analisador sintático solicita tokens ao analisador léxico através do comando "obter o próximo token", e o analisador léxico lê caracteres até identificar o próximo token completo.

### Tokens, Padrões e Lexemas

Conforme as notas de aula (seção 3.2):
- **Token**: Classe de símbolos terminais da gramática
- **Padrão**: Descrição da forma que os lexemas de um token podem ter
- **Lexema**: Sequência de caracteres no programa-fonte reconhecida pelo padrão

## Estrutura do Código

### Classe Principal: `AnalisadorLexico`

A classe `AnalisadorLexico` implementa o scanner completo da linguagem LPD.

#### Atributos da Classe

```python
def __init__(self, codigo_fonte: str):
    self.fonte = codigo_fonte          # Código fonte completo
    self.posicao = 0                   # Posição atual no código fonte
    self.linha = 1                     # Linha atual (começa em 1)
    self.coluna = 1                    # Coluna atual (começa em 1)
    self.tamanho = len(codigo_fonte)   # Tamanho total do código fonte
```

#### Constantes

- `CARACTERES_LETRA`: String contendo todas as letras maiúsculas, minúsculas e underscore (`_`)
- `CARACTERES_DIGITO`: String contendo dígitos de 0 a 9
- `TAMANHO_MAX_IDENTIFICADOR`: Limite de 30 caracteres para identificadores (conforme especificação LPD)

## Detalhamento das Funções

### Métodos Auxiliares de Navegação

#### `_espiar(deslocamento: int = 0) -> str`

Retorna o caractere na posição atual + deslocamento **sem avançar** a posição. Permite "olhar adiante" sem consumir caracteres.

**Parâmetros:**
- `deslocamento`: Quantos caracteres à frente olhar (padrão: 0 = caractere atual)

**Retorno:** Caractere na posição especificada ou string vazia se estiver além do fim do arquivo

**Uso:** Essencial para reconhecer operadores de dois caracteres (ex: `:=`, `<=`, `>=`, `!=`)

#### `_avancar() -> str`

Avança para o próximo caractere e retorna o caractere atual. Atualiza a posição, linha e coluna.

**Retorno:** Caractere que estava na posição atual antes de avançar

**Comportamento:**
- Se encontrar `\n`, incrementa `linha` e reseta `coluna` para 1
- Caso contrário, incrementa `coluna`
- Sempre incrementa `posicao`

#### `_corresponde(esperado: str) -> bool`

Verifica se o caractere atual corresponde ao esperado e, se sim, avança automaticamente.

**Parâmetros:**
- `esperado`: Caractere esperado

**Retorno:** `True` se correspondeu e avançou, `False` caso contrário

**Uso:** Simplifica a verificação de caracteres esperados

### Métodos de Processamento

#### `_pular_espacos_e_comentarios()`

Remove espaços em branco e comentários do código fonte. Comentários em LPD são delimitados por `{` e `}`.

**Comportamento:**
1. Remove espaços em branco consecutivos
2. Se encontrar `{`, entra em modo de comentário:
   - Lê caracteres até encontrar `}`
   - Se chegar ao fim do arquivo sem encontrar `}`, lança `ErroLexico`
   - Continua removendo espaços e comentários até não haver mais

**Erros:**
- `ErroLexico`: Se um comentário não for fechado (não encontrar `}`)

#### `_ler_identificador_ou_palavra_reservada() -> Token`

Lê um identificador ou palavra reservada.

**Regras:**
- Deve começar com letra (não pode começar com `_`)
- Pode conter letras, dígitos e `_` após o primeiro caractere
- Máximo de 30 caracteres
- Após ler, verifica se é palavra reservada (case-insensitive)

**Processo:**
1. Verifica se primeiro caractere é letra (não `_`)
2. Lê caracteres válidos (letras, dígitos, `_`)
3. Verifica tamanho máximo
4. Converte para minúsculas e verifica em `PALAVRAS_RESERVADAS`
5. Retorna token apropriado

**Retorno:** `Token` do tipo `IDENTIFICADOR` ou tipo da palavra reservada

**Erros:**
- `ErroLexico`: Se não começar com letra ou exceder 30 caracteres

#### `_ler_numero() -> Token`

Lê um número inteiro.

**Regras:**
- Deve começar com dígito
- Lê dígitos consecutivos
- Converte para inteiro e armazena no atributo `valor`

**Retorno:** `Token` do tipo `NUMERO` com `valor` contendo o inteiro

**Erros:**
- `ErroLexico`: Se não começar com dígito

### Método Principal

#### `obter_tokens() -> List[Token]`

Método principal que analisa todo o código fonte e retorna a lista completa de tokens.

**Processo:**
1. Inicializa lista vazia de tokens
2. Loop principal:
   - Remove espaços e comentários
   - Verifica fim de arquivo
   - Reconhece tokens na seguinte ordem de prioridade:
     a. Operadores de dois caracteres (`:=`, `<=`, `>=`, `!=`)
     b. Operadores e símbolos de um caractere (`=`, `<`, `>`, `+`, `-`, `*`, `(`, `)`, `:`, `;`, `,`, `.`)
     c. Identificadores/palavras reservadas
     d. Números
   - Se nenhum padrão corresponder, lança erro
3. Adiciona token `FIM_ARQUIVO` ao final
4. Retorna lista completa

**Retorno:** Lista de `Token` representando todo o código fonte

**Erros:**
- `ErroLexico`: Para caracteres inválidos ou erros de formatação

**Estratégia de Reconhecimento:**

A ordem de verificação é importante:
1. **Operadores de dois caracteres primeiro**: Evita reconhecer `:` e `=` separadamente quando na verdade é `:=`
2. **Operadores de um caractere**: Depois dos de dois caracteres
3. **Identificadores**: Antes de números (pois números podem começar com dígito, mas identificadores não)
4. **Números**: Por último

## Integração

### Uso pelo Analisador Sintático

O `AnalisadorSintatico` recebe a lista de tokens gerada por `obter_tokens()` e a utiliza para construir a árvore sintática.

**Fluxo:**
```
Código Fonte (string)
    ↓
AnalisadorLexico.obter_tokens()
    ↓
Lista de Tokens (Token[])
    ↓
AnalisadorSintatico(tokens).analisar()
    ↓
AST (Programa)
```

### Dependências

- **`tokens`**: Importa `Token`, `TipoToken`, `PALAVRAS_RESERVADAS`, `ErroLexico`

### Interação com Tabela de Símbolos

Embora o analisador léxico não interaja diretamente com a tabela de símbolos, ele prepara os tokens que serão utilizados pelo analisador sintático para popular a tabela.

## Exemplos Práticos

### Exemplo 1: Análise de Código Simples

```python
from analisador_lexico import AnalisadorLexico

codigo = """
programa exemplo;
var x: inteiro;
inicio
    x := 42;
fim.
"""

analisador = AnalisadorLexico(codigo)
tokens = analisador.obter_tokens()

for token in tokens:
    if token.tipo != TipoToken.FIM_ARQUIVO:
        print(f"{token.linha}:{token.coluna} {token.tipo.name:15s} '{token.lexema}'")
```

**Saída esperada:**
```
1:1 PROGRAMA       'programa'
1:10 IDENTIFICADOR 'exemplo'
1:16 PONTO_VIRGULA ';'
2:1 VAR            'var'
2:5 IDENTIFICADOR   'x'
2:6 DOIS_PONTOS     ':'
2:8 INTEIRO         'inteiro'
2:15 PONTO_VIRGULA  ';'
3:1 INICIO          'inicio'
4:5 IDENTIFICADOR   'x'
4:7 ATRIBUICAO      ':='
4:10 NUMERO         '42'
4:12 PONTO_VIRGULA  ';'
5:1 FIM             'fim'
5:4 PONTO           '.'
```

### Exemplo 2: Tratamento de Comentários

```python
codigo = """
programa teste;
{ Este é um comentário }
var x: inteiro;
{ Comentário
   multilinha }
inicio
    x := 10;
fim.
"""

analisador = AnalisadorLexico(codigo)
tokens = analisador.obter_tokens()

# Comentários não aparecem nos tokens
for token in tokens:
    if token.tipo != TipoToken.FIM_ARQUIVO:
        print(token.lexema, end=" ")
```

**Saída:** `programa teste ; var x : inteiro ; inicio x := 10 ; fim .`

### Exemplo 3: Tratamento de Erros

```python
codigo = "programa teste; var x@: inteiro;"

try:
    analisador = AnalisadorLexico(codigo)
    tokens = analisador.obter_tokens()
except ErroLexico as e:
    print(f"Erro léxico: {e}")
    print(f"Linha {e.linha}, Coluna {e.coluna}")
```

**Saída:** `Erro léxico: [2:10] Caractere inválido: '@'`

### Exemplo 4: Palavras Reservadas vs Identificadores

```python
codigo = "programa programa; var inicio: inteiro;"

analisador = AnalisadorLexico(codigo)
tokens = analisador.obter_tokens()

for token in tokens:
    if token.tipo != TipoToken.FIM_ARQUIVO:
        print(f"{token.lexema:15s} -> {token.tipo.name}")
```

**Saída:**
```
programa        -> PROGRAMA
programa        -> IDENTIFICADOR
;               -> PONTO_VIRGULA
var             -> VAR
inicio          -> IDENTIFICADOR
:               -> DOIS_PONTOS
inteiro         -> INTEIRO
;               -> PONTO_VIRGULA
```

Note que `programa` aparece duas vezes: primeiro como palavra reservada (no cabeçalho) e depois como identificador (nome do programa). O analisador léxico diferencia pelo contexto, mas na verdade ambos são reconhecidos como tokens diferentes pelo analisador sintático.

## Análise Detalhada do Código

### Método `__init__`

```python
def __init__(self, codigo_fonte: str):
    self.fonte = codigo_fonte          # Código fonte completo
    self.posicao = 0                   # Posição atual no código fonte
    self.linha = 1                     # Linha atual (começa em 1)
    self.coluna = 1                    # Coluna atual (começa em 1)
    self.tamanho = len(codigo_fonte)   # Tamanho total do código fonte
```

**Explicação linha por linha:**
- `self.fonte = codigo_fonte`: Armazena o código fonte completo como string. Isso permite acesso direto por índice.
- `self.posicao = 0`: Inicializa posição no início do código (índice 0). Usado para rastrear onde estamos no código.
- `self.linha = 1`: Inicializa contador de linha em 1 (convenção: primeira linha é 1, não 0). Usado para reportar erros.
- `self.coluna = 1`: Inicializa contador de coluna em 1. Resetado para 1 a cada nova linha.
- `self.tamanho = len(codigo_fonte)`: Calcula tamanho uma vez para evitar recalcular. Usado para verificar fim do arquivo.

**Por que armazenar tudo:**
- `fonte`: Permite acesso aleatório por índice (`fonte[posicao]`)
- `posicao`: Rastreia progresso através do código
- `linha/coluna`: Essenciais para mensagens de erro precisas
- `tamanho`: Evita IndexError ao verificar fim do arquivo

### Método `_espiar`

```python
def _espiar(self, deslocamento: int = 0) -> str:
    """Retorna o caractere na posição atual + deslocamento, sem avançar."""
    indice = self.posicao + deslocamento
    return self.fonte[indice] if indice < self.tamanho else ""
```

**Explicação linha por linha:**
- `indice = self.posicao + deslocamento`: Calcula índice absoluto. Se `deslocamento=0`, retorna caractere atual; se `deslocamento=1`, retorna próximo caractere.
- `return self.fonte[indice] if indice < self.tamanho else ""`: 
  - Se índice válido: retorna caractere naquela posição
  - Se índice inválido (fim do arquivo): retorna string vazia (evita IndexError)

**Exemplo de uso:**
```python
# Código: "x := 5"
# posicao = 0, caractere atual = 'x'
caractere_atual = self._espiar(0)      # 'x'
proximo_caractere = self._espiar(1)    # ' '
# posicao ainda é 0 (não avançou)
```

**Por que "espiar" e não avançar:**
- Permite verificar próximo caractere antes de consumir o atual
- Essencial para reconhecer operadores de dois caracteres (`:=`, `<=`, etc.)
- Evita "voltar atrás" se reconhecimento falhar

### Método `_avancar`

```python
def _avancar(self) -> str:
    """Avança para o próximo caractere e retorna o atual."""
    caractere = self._espiar()
    if caractere == "\n":
        self.linha += 1
        self.coluna = 1
    else:
        self.coluna += 1
    self.posicao += 1
    return caractere
```

**Explicação linha por linha:**
- `caractere = self._espiar()`: Obtém caractere atual sem avançar ainda
- `if caractere == "\n"`: Verifica se é quebra de linha
  - `self.linha += 1`: Incrementa contador de linha
  - `self.coluna = 1`: Reseta coluna para 1 (nova linha começa na coluna 1)
- `else: self.coluna += 1`: Se não é quebra de linha, apenas incrementa coluna
- `self.posicao += 1`: Sempre incrementa posição (avança no código)
- `return caractere`: Retorna caractere que estava na posição antes de avançar

**Exemplo de execução:**
```python
# Código: "x\ny"
# posicao=0, linha=1, coluna=1, caractere='x'
caractere = self._avancar()  # Retorna 'x'
# Agora: posicao=1, linha=1, coluna=2

# posicao=1, caractere='\n'
caractere = self._avancar()  # Retorna '\n'
# Agora: posicao=2, linha=2, coluna=1 (resetado!)
```

**Por que gerenciar linha/coluna:**
- Mensagens de erro precisam localização exata
- Facilita debug e correção de erros pelo programador
- Padrão em compiladores profissionais

### Método `_corresponde`

```python
def _corresponde(self, esperado: str) -> bool:
    """Verifica se o caractere atual corresponde ao esperado e avança."""
    if self._espiar() == esperado:
        self._avancar()
        return True
    return False
```

**Explicação linha por linha:**
- `if self._espiar() == esperado`: Verifica se caractere atual é o esperado (sem avançar)
- `self._avancar()`: Se correspondeu, consome o caractere (avança)
- `return True`: Indica que correspondeu e foi consumido
- `return False`: Indica que não correspondeu (não consumiu)

**Exemplo de uso:**
```python
# Código: "x := 5"
# posicao=2, caractere=':'
if self._corresponde(":"):  # True, avança para '='
    # Agora posicao=3, caractere='='
    pass
```

**Vantagem:**
- Simplifica código: `if self._corresponde(":"):` é mais legível que verificar e avançar separadamente
- Evita erros de esquecer de avançar após verificar

### Método `_pular_espacos_e_comentarios`

```python
def _pular_espacos_e_comentarios(self):
    """Pula espaços em branco e comentários."""
    while True:
        caractere = self._espiar()
        # Espaços em branco
        while caractere and caractere.isspace():
            self._avancar()
            caractere = self._espiar()
        # Comentários { ... }
        if caractere == "{":
            linha_inicio, coluna_inicio = self.linha, self.coluna
            self._avancar()
            while True:
                if self._espiar() == "":
                    raise ErroLexico("Comentário não encerrado '}'", linha_inicio, coluna_inicio)
                if self._espiar() == "}":
                    self._avancar()
                    break
                self._avancar()
            continue
        break
```

**Explicação linha por linha:**

**Loop externo (`while True:`):**
- Continua até não haver mais espaços ou comentários

**Remoção de espaços:**
- `caractere = self._espiar()`: Obtém caractere atual
- `while caractere and caractere.isspace()`: Enquanto houver caractere e for espaço em branco
  - `self._avancar()`: Consome o espaço
  - `caractere = self._espiar()`: Obtém próximo caractere
- `caractere.isspace()` retorna True para espaços, tabs, newlines, etc.

**Processamento de comentários:**
- `if caractere == "{"`: Detecta início de comentário
- `linha_inicio, coluna_inicio = self.linha, self.coluna`: Salva posição do `{` para erro
- `self._avancar()`: Consome o `{`
- `while True:`: Loop interno para ler até `}`
  - `if self._espiar() == ""`: Verifica fim do arquivo (erro!)
  - `raise ErroLexico(...)`: Lança erro se comentário não fechado
  - `if self._espiar() == "}"`: Encontrou fechamento
  - `self._avancar()`: Consome o `}`
  - `break`: Sai do loop interno
  - `self._avancar()`: Consome caractere dentro do comentário
- `continue`: Volta ao início do loop externo (pode haver mais comentários)
- `break`: Sai do loop externo (não há mais espaços/comentários)

**Exemplo de execução:**
```python
# Código: "  {comentário}  x"
# posicao=0: ' ' (espaço)
# Pula espaços: posicao=2: '{'
# Entra em comentário: posicao=3 até encontrar '}'
# Pula espaços novamente: posicao=posição_após_}
# Agora: caractere='x' (pronto para processar)
```

### Método `_ler_identificador_ou_palavra_reservada`

```python
def _ler_identificador_ou_palavra_reservada(self) -> Token:
    """Lê um identificador ou palavra reservada."""
    linha_inicio, coluna_inicio = self.linha, self.coluna
    lexema = ""
    # Primeira letra (não pode começar com _)
    if self._espiar() not in CARACTERES_LETRA.replace("_", ""):
        raise ErroLexico("Identificador deve iniciar com letra", linha_inicio, coluna_inicio)
    while True:
        caractere = self._espiar()
        if caractere and (caractere in CARACTERES_LETRA or caractere in CARACTERES_DIGITO):
            lexema += self._avancar()
            if len(lexema) > TAMANHO_MAX_IDENTIFICADOR:
                raise ErroLexico(
                    f"Identificador excede {TAMANHO_MAX_IDENTIFICADOR} caracteres",
                    linha_inicio, coluna_inicio
                )
        else:
            break
    minusculo = lexema.lower()
    if minusculo in PALAVRAS_RESERVADAS:
        return Token(PALAVRAS_RESERVADAS[minusculo], lexema, linha_inicio, coluna_inicio)
    return Token(TipoToken.IDENTIFICADOR, lexema, linha_inicio, coluna_inicio, valor=lexema)
```

**Explicação linha por linha:**

**Inicialização:**
- `linha_inicio, coluna_inicio = self.linha, self.coluna`: Salva posição inicial para token
- `lexema = ""`: String vazia para construir lexema

**Validação do primeiro caractere:**
- `CARACTERES_LETRA.replace("_", "")`: Remove underscore da string (não pode começar com `_`)
- `if self._espiar() not in ...`: Verifica se primeiro caractere é letra (não dígito, não `_`)
- `raise ErroLexico(...)`: Erro se não começar com letra

**Construção do lexema:**
- `while True:`: Loop para ler caracteres válidos
- `caractere = self._espiar()`: Obtém caractere atual
- `if caractere and (caractere in CARACTERES_LETRA or caractere in CARACTERES_DIGITO)`:
  - Verifica se há caractere E se é letra ou dígito
  - `_` é permitido após primeiro caractere (está em `CARACTERES_LETRA`)
- `lexema += self._avancar()`: Adiciona caractere ao lexema e avança
- `if len(lexema) > TAMANHO_MAX_IDENTIFICADOR`: Verifica limite de 30 caracteres
  - `raise ErroLexico(...)`: Erro se exceder limite
- `else: break`: Se caractere inválido, para de ler

**Classificação:**
- `minusculo = lexema.lower()`: Converte para minúsculas (comparação case-insensitive)
- `if minusculo in PALAVRAS_RESERVADAS`: Verifica se é palavra reservada
  - `return Token(PALAVRAS_RESERVADAS[minusculo], ...)`: Retorna token da palavra reservada
- `return Token(TipoToken.IDENTIFICADOR, ..., valor=lexema)`: Retorna token de identificador

**Exemplo de execução:**
```python
# Código: "programa"
# posicao=0, caractere='p'
# lexema = ""
# Verifica 'p' é letra: OK
# lexema = "p", avança
# lexema = "pr", avança
# ... até "programa"
# "programa".lower() = "programa"
# "programa" in PALAVRAS_RESERVADAS: True
# Retorna Token(TipoToken.PROGRAMA, "programa", ...)
```

### Método `_ler_numero`

```python
def _ler_numero(self) -> Token:
    """Lê um número inteiro."""
    linha_inicio, coluna_inicio = self.linha, self.coluna
    lexema = ""
    if self._espiar() not in CARACTERES_DIGITO:
        raise ErroLexico("Número inválido", linha_inicio, coluna_inicio)
    while self._espiar() in CARACTERES_DIGITO:
        lexema += self._avancar()
    # LPD aceita apenas inteiros
    return Token(TipoToken.NUMERO, lexema, linha_inicio, coluna_inicio, valor=int(lexema))
```

**Explicação linha por linha:**
- `linha_inicio, coluna_inicio = self.linha, self.coluna`: Salva posição inicial
- `lexema = ""`: String para construir número
- `if self._espiar() not in CARACTERES_DIGITO`: Valida que primeiro caractere é dígito
- `while self._espiar() in CARACTERES_DIGITO`: Lê dígitos consecutivos
  - `lexema += self._avancar()`: Adiciona dígito e avança
- `return Token(..., valor=int(lexema))`: Cria token com valor convertido para inteiro

**Por que converter para int:**
- `valor` armazena o número como inteiro Python (não string)
- Facilita uso posterior (operações, comparações)
- Evita conversões repetidas

### Método `obter_tokens` - Análise Detalhada

```python
def obter_tokens(self) -> List[Token]:
    tokens: List[Token] = []
    while True:
        self._pular_espacos_e_comentarios()
        caractere = self._espiar()
        if not caractere:
            tokens.append(Token(TipoToken.FIM_ARQUIVO, "", self.linha, self.coluna))
            return tokens
        
        # Operadores de dois caracteres (verificar primeiro)
        if caractere == ":" and self._espiar(1) == "=":
            # ... código para :=
            continue
        # ... mais operadores de dois caracteres
        
        # Operadores de um caractere
        if caractere == "=":
            tokens.append(Token(TipoToken.IGUAL, self._avancar(), self.linha, self.coluna - 1))
            continue
        # ... mais operadores
        
        # Identificadores
        if caractere in CARACTERES_LETRA.replace("_", ""):
            tokens.append(self._ler_identificador_ou_palavra_reservada())
            continue
        
        # Números
        if caractere in CARACTERES_DIGITO:
            tokens.append(self._ler_numero())
            continue
        
        raise ErroLexico(f"Caractere inválido: '{caractere}'", self.linha, self.coluna)
```

**Explicação da estrutura:**

**Inicialização:**
- `tokens: List[Token] = []`: Lista vazia para acumular tokens

**Loop principal (`while True:`):**
- Continua até fim do arquivo

**Processamento de cada iteração:**
1. `self._pular_espacos_e_comentarios()`: Remove espaços e comentários
2. `caractere = self._espiar()`: Obtém caractere atual
3. `if not caractere:`: Verifica fim do arquivo
   - Adiciona token `FIM_ARQUIVO` e retorna

**Reconhecimento de tokens (ordem importante!):**

**1. Operadores de dois caracteres (primeiro!):**
```python
if caractere == ":" and self._espiar(1) == "=":
    # É ":=", não ":" seguido de "="
    linha, coluna = self.linha, self.coluna  # Salva posição
    self._avancar()  # Consome ":"
    self._avancar()  # Consome "="
    tokens.append(Token(TipoToken.ATRIBUICAO, ":=", linha, coluna))
    continue  # Volta ao início do loop
```
- **Por que primeiro:** Se verificar `:` primeiro, consumiria `:` e depois encontraria `=` separadamente
- **Lookahead:** `self._espiar(1)` olha um caractere à frente sem consumir

**2. Operadores de um caractere:**
```python
if caractere == "=":
    tokens.append(Token(TipoToken.IGUAL, self._avancar(), self.linha, self.coluna - 1))
    continue
```
- `self._avancar()`: Consome caractere e retorna ele mesmo
- `self.coluna - 1`: Corrige coluna (já avançou, mas token começa na posição anterior)

**3. Identificadores:**
- Verifica se começa com letra (não `_`)
- Chama método especializado que lê até caractere inválido

**4. Números:**
- Verifica se começa com dígito
- Chama método especializado que lê dígitos consecutivos

**5. Erro:**
- Se nenhum padrão correspondeu, caractere é inválido
- Lança `ErroLexico` com mensagem descritiva

**Por que ordem importa:**
1. Operadores de dois caracteres antes de um caractere (evita reconhecer `:` e `=` separadamente)
2. Identificadores antes de números (evita confusão, mas na verdade números não começam com letra)
3. Essa ordem garante reconhecimento correto e sem ambiguidade

## Relação com as Notas de Aula

### Algoritmo Pega Token

As notas de aula (seção 3.5) descrevem um algoritmo "Pega Token" que o analisador léxico deve implementar. O método `obter_tokens()` implementa esse algoritmo de forma completa:

1. **Pular espaços e comentários**: Implementado em `_pular_espacos_e_comentarios()`
2. **Reconhecer padrões**: Implementado através de verificações condicionais no loop principal
3. **Classificar tokens**: Utiliza `TipoToken` e `PALAVRAS_RESERVADAS`
4. **Coletar atributos**: Armazena lexema, linha, coluna e valor quando aplicável

### Estrutura de Tokens

Conforme as notas de aula, cada token possui:
- **Símbolo**: Tipo do token (implementado como `TipoToken`)
- **Lexema**: Sequência de caracteres (atributo `lexema`)
- **Atributos**: Informações adicionais (atributo `valor`)

A implementação segue essa estrutura exatamente através da classe `Token`.

### Tratamento de Erros

As notas de aula mencionam que o analisador léxico deve realizar recuperação de erros. A implementação atual lança `ErroLexico` quando encontra problemas, permitindo que o compilador principal decida como proceder (parar compilação ou tentar recuperação).

