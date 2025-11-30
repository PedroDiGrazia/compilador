# Árvore Sintática Abstrata (AST) - Documentação

## Introdução e Teoria

### Base Teórica

A **Árvore Sintática Abstrata (AST - Abstract Syntax Tree)** é uma representação hierárquica da estrutura sintática de um programa. Conforme as notas de aula (seção 1.3), o analisador sintático constrói a árvore sintática a partir da sequência de tokens fornecida pelo analisador léxico.

#### Função da AST

A AST serve como:
1. **Representação intermediária**: Estrutura de dados que representa o programa fonte de forma estruturada
2. **Base para análise semântica**: O analisador semântico percorre a AST para verificar tipos e regras semânticas
3. **Base para geração de código**: O gerador de código percorre a AST para produzir código assembly

#### Diferença entre Árvore Sintática e Árvore de Derivação

- **Árvore de Derivação**: Contém todos os detalhes da gramática, incluindo símbolos não-terminais intermediários
- **Árvore Sintática Abstrata**: Contém apenas informações essenciais, abstraindo detalhes sintáticos desnecessários

A AST é mais compacta e adequada para as fases posteriores da compilação.

### Estrutura Hierárquica

A AST segue uma estrutura hierárquica onde:
- **Raiz**: Nó `Programa` representando o programa completo
- **Nós intermediários**: Representam estruturas (blocos, comandos, expressões)
- **Folhas**: Representam elementos atômicos (identificadores, números, booleanos)

## Estrutura do Código

### Classe Base: `No`

Todas as classes da AST herdam de `No`, que é uma classe vazia usada apenas para marcação de tipo (type hint).

```python
class No:
    """Classe base para todos os nós da AST."""
    pass
```

### Estruturas do Programa

#### `Programa`

Nó raiz que representa o programa completo.

**Atributos:**
- `nome: str` - Nome do programa (identificador após `programa`)
- `declaracoes_variaveis: Optional[DeclaracoesVariaveis]` - Declarações de variáveis globais (pode ser `None`)
- `procedimentos: List[Procedimento]` - Lista de procedimentos globais
- `funcoes: List[Funcao]` - Lista de funções globais
- `comando_composto: ComandoComposto` - Corpo principal do programa (entre `inicio` e `fim`)

**Estrutura BNF correspondente:**
```
<programa> ::= programa <identificador> ; <bloco> .
```

### Estruturas de Declaração

#### `DeclaracoesVariaveis`

Representa uma seção `var` com múltiplas declarações.

**Atributos:**
- `declaracoes: List[DeclaracaoVariavel]` - Lista de declarações individuais

#### `DeclaracaoVariavel`

Representa uma declaração de uma ou mais variáveis do mesmo tipo.

**Atributos:**
- `identificadores: List[str]` - Lista de nomes de variáveis
- `tipo: str` - Tipo das variáveis (`'inteiro'` ou `'booleano'`)

**Exemplo:** `x, y, z: inteiro` → `DeclaracaoVariavel(['x', 'y', 'z'], 'inteiro')`

#### `Procedimento`

Representa a declaração de um procedimento.

**Atributos:**
- `nome: str` - Nome do procedimento
- `parametros: List[Parametro]` - Lista de parâmetros (pode ser vazia)
- `bloco: Bloco` - Corpo do procedimento

#### `Funcao`

Representa a declaração de uma função.

**Atributos:**
- `nome: str` - Nome da função
- `parametros: List[Parametro]` - Lista de parâmetros (pode ser vazia)
- `tipo_retorno: str` - Tipo de retorno (`'inteiro'` ou `'booleano'`)
- `bloco: Bloco` - Corpo da função

#### `Parametro`

Representa um parâmetro de procedimento ou função.

**Atributos:**
- `identificadores: List[str]` - Lista de nomes de parâmetros do mesmo tipo
- `tipo: str` - Tipo dos parâmetros

**Exemplo:** `a, b: inteiro` → `Parametro(['a', 'b'], 'inteiro')`

#### `Bloco`

Representa um bloco de código (usado em procedimentos, funções e programa principal).

**Atributos:**
- `declaracoes_variaveis: Optional[DeclaracoesVariaveis]` - Declarações locais
- `procedimentos: List[Procedimento]` - Procedimentos aninhados
- `funcoes: List[Funcao]` - Funções aninhadas
- `comando_composto: ComandoComposto` - Comandos executáveis

### Estruturas de Comandos

#### `Comando`

Classe base abstrata para todos os comandos. Não é instanciada diretamente.

#### `ComandoComposto`

Sequência de comandos entre `inicio` e `fim`.

**Atributos:**
- `comandos: List[Comando]` - Lista de comandos na ordem de execução

#### `Atribuicao`

Comando de atribuição: `identificador := expressao`

**Atributos:**
- `identificador: str` - Nome da variável ou função (para retorno)
- `expressao: Expressao` - Expressão a ser avaliada e atribuída

#### `ChamadaProcedimento`

Chamada de procedimento: `nome_procedimento` ou `nome_procedimento(argumentos)`

**Atributos:**
- `nome: str` - Nome do procedimento
- `argumentos: List[Expressao]` - Lista de argumentos (pode ser vazia)

#### `ComandoLeitura`

Comando de leitura: `leia(identificador)`

**Atributos:**
- `identificador: str` - Nome da variável a ser lida

#### `ComandoEscrita`

Comando de escrita: `escreva(expressao)`

**Atributos:**
- `expressao: Expressao` - Expressão a ser impressa

#### `ComandoSe`

Comando condicional: `se expressao entao comando [senao comando]`

**Atributos:**
- `condicao: Expressao` - Condição booleana
- `comando_entao: Comando` - Comando a executar se verdadeiro
- `comando_senao: Optional[Comando]` - Comando a executar se falso (pode ser `None`)

#### `ComandoEnquanto`

Comando de repetição: `enquanto expressao faca comando`

**Atributos:**
- `condicao: Expressao` - Condição booleana
- `corpo: Comando` - Comando a repetir enquanto condição for verdadeira

#### `ComandoVazio`

Comando vazio (nenhuma operação). Usado quando não há comandos em um bloco.

### Estruturas de Expressões

#### `Expressao`

Classe base para todas as expressões.

**Atributos:**
- `tipo_expressao: Optional[str]` - Tipo da expressão (`'inteiro'` ou `'booleano'`), preenchido na análise semântica

#### `OperacaoBinaria`

Operação binária: `esquerda operador direita`

**Atributos:**
- `esquerda: Expressao` - Operando esquerdo
- `operador: str` - Operador (`'+'`, `'-'`, `'*'`, `'div'`, `'e'`, `'ou'`, `'='`, `'!='`, `'<'`, `'<='`, `'>'`, `'>='`)
- `direita: Expressao` - Operando direito
- `tipo_expressao: Optional[str]` - Tipo resultante (preenchido na análise semântica)

#### `OperacaoUnaria`

Operação unária: `operador operando`

**Atributos:**
- `operador: str` - Operador (`'nao'` ou `'-'`)
- `operando: Expressao` - Operando
- `tipo_expressao: Optional[str]` - Tipo resultante

#### `Identificador`

Referência a uma variável ou função.

**Atributos:**
- `nome: str` - Nome do identificador
- `tipo_expressao: Optional[str]` - Tipo (determinado pela tabela de símbolos)

#### `Numero`

Literal numérico inteiro.

**Atributos:**
- `valor: int` - Valor numérico
- `tipo_expressao: str` - Sempre `'inteiro'`

#### `Booleano`

Literal booleano.

**Atributos:**
- `valor: bool` - Valor booleano (`True` ou `False`)
- `tipo_expressao: str` - Sempre `'booleano'`

#### `ChamadaFuncao`

Chamada de função como expressão: `nome_funcao(argumentos)`

**Atributos:**
- `nome: str` - Nome da função
- `argumentos: List[Expressao]` - Lista de argumentos
- `tipo_expressao: Optional[str]` - Tipo de retorno da função

## Função Utilitária

### `arvore_para_string(no: No, recuo: int = 0) -> str`

Converte um nó da AST para representação em string formatada (útil para debug e visualização).

**Parâmetros:**
- `no: No` - Nó raiz da árvore (ou subárvore) a converter
- `recuo: int` - Nível de indentação (usado recursivamente)

**Retorno:** String formatada representando a árvore

**Uso:**
```python
ast = analisador_sintatico.analisar()
print(arvore_para_string(ast))
```

## Detalhamento das Estruturas

### Hierarquia de Herança

```
No (classe base)
├── Programa
├── DeclaracoesVariaveis
├── DeclaracaoVariavel
├── Procedimento
├── Funcao
├── Parametro
├── Bloco
├── ComandoComposto
├── Comando (classe base)
│   ├── Atribuicao
│   ├── ChamadaProcedimento
│   ├── ComandoLeitura
│   ├── ComandoEscrita
│   ├── ComandoSe
│   ├── ComandoEnquanto
│   └── ComandoVazio
└── Expressao (classe base)
    ├── OperacaoBinaria
    ├── OperacaoUnaria
    ├── Identificador
    ├── Numero
    ├── Booleano
    └── ChamadaFuncao
```

### Uso de Dataclasses

Todas as estruturas são definidas como `@dataclass`, o que fornece:
- Construtores automáticos
- Comparação de igualdade
- Representação em string
- Facilita imutabilidade (quando desejado)

## Integração

### Uso pelo Analisador Sintático

O `AnalisadorSintatico` constrói a AST durante o processo de parsing:

```python
# O analisador sintático cria nós da AST
ast = AnalisadorSintatico(tokens).analisar()
# Retorna um nó Programa
```

### Uso pelo Analisador Semântico

O `AnalisadorSemantico` percorre a AST para:
- Verificar declarações de variáveis
- Verificar tipos de expressões
- Popular a tabela de símbolos
- Anotar a AST com tipos (`tipo_expressao`)

```python
analisador_semantico = AnalisadorSemantico()
tabela_simbolos = analisador_semantico.analisar(ast)
# AST agora tem tipos preenchidos
```

### Uso pelo Gerador de Código

O `GeradorCodigo` percorre a AST para gerar código assembly:

```python
gerador = GeradorCodigo()
instrucoes = gerador.gerar(ast, tabela_simbolos)
```

## Exemplos Práticos

### Exemplo 1: AST de um Programa Simples

```python
from arvore_sintatica import Programa, DeclaracoesVariaveis, DeclaracaoVariavel
from arvore_sintatica import ComandoComposto, Atribuicao, Identificador, Numero

# Programa: programa teste; var x: inteiro; inicio x := 5; fim.

ast = Programa(
    nome="teste",
    declaracoes_variaveis=DeclaracoesVariaveis(
        declaracoes=[
            DeclaracaoVariavel(
                identificadores=["x"],
                tipo="inteiro"
            )
        ]
    ),
    procedimentos=[],
    funcoes=[],
    comando_composto=ComandoComposto(
        comandos=[
            Atribuicao(
                identificador="x",
                expressao=Numero(valor=5, tipo_expressao="inteiro")
            )
        ]
    )
)

print(arvore_para_string(ast))
```

### Exemplo 2: AST de Expressão Aritmética

```python
from arvore_sintatica import OperacaoBinaria, Identificador, Numero

# Expressão: x + 5 * 2

expressao = OperacaoBinaria(
    esquerda=Identificador(nome="x", tipo_expressao=None),
    operador="+",
    direita=OperacaoBinaria(
        esquerda=Numero(valor=5, tipo_expressao="inteiro"),
        operador="*",
        direita=Numero(valor=2, tipo_expressao="inteiro"),
        tipo_expressao=None
    ),
    tipo_expressao=None
)
```

### Exemplo 3: AST de Comando Condicional

```python
from arvore_sintatica import ComandoSe, OperacaoBinaria, Identificador, Numero
from arvore_sintatica import Atribuicao, Booleano

# Comando: se x > 0 entao x := 1 senao x := 0

comando = ComandoSe(
    condicao=OperacaoBinaria(
        esquerda=Identificador(nome="x"),
        operador=">",
        direita=Numero(valor=0),
        tipo_expressao="booleano"
    ),
    comando_entao=Atribuicao(
        identificador="x",
        expressao=Numero(valor=1)
    ),
    comando_senao=Atribuicao(
        identificador="x",
        expressao=Numero(valor=0)
    )
)
```

## Análise Detalhada do Código

### Estrutura de Dataclasses

Todas as estruturas da AST são definidas como `@dataclass`. Vamos analisar exemplos:

#### Exemplo: `Programa`

```python
@dataclass
class Programa(No):
    """Nó raiz que representa o programa completo."""
    nome: str
    declaracoes_variaveis: Optional['DeclaracoesVariaveis']
    procedimentos: List['Procedimento']
    funcoes: List['Funcao']
    comando_composto: 'ComandoComposto'
```

**Explicação:**
- `@dataclass`: Decorador que gera automaticamente `__init__()`, `__repr__()`, `__eq__()`
- `nome: str`: Nome do programa (obrigatório, não pode ser None)
- `declaracoes_variaveis: Optional[...]`: Pode ser None (se não há declarações)
- `procedimentos: List[...]`: Lista pode estar vazia (se não há procedimentos)
- `funcoes: List[...]`: Lista pode estar vazia (se não há funções)
- `comando_composto: 'ComandoComposto'`: Sempre presente (obrigatório)

**Uso de aspas nas anotações de tipo:**
- `'DeclaracoesVariaveis'` usa aspas (forward reference)
- Necessário porque classe ainda não foi definida quando `Programa` é definida
- Python resolve referências depois

**Criação de instância:**
```python
programa = Programa(
    nome="exemplo",
    declaracoes_variaveis=DeclaracoesVariaveis([...]),
    procedimentos=[],
    funcoes=[],
    comando_composto=ComandoComposto([...])
)
```

#### Exemplo: `OperacaoBinaria`

```python
@dataclass
class OperacaoBinaria(Expressao):
    """Operação binária: esquerda operador direita"""
    esquerda: Expressao
    operador: str
    direita: Expressao
    tipo_expressao: Optional[str] = None
```

**Explicação:**
- Herda de `Expressao` (classe base)
- `esquerda: Expressao`: Operando esquerdo (pode ser qualquer expressão)
- `operador: str`: String com operador (`'+'`, `'e'`, `'='`, etc.)
- `direita: Expressao`: Operando direito
- `tipo_expressao: Optional[str] = None`: Tipo inferido na análise semântica
  - `= None` significa valor padrão (não precisa fornecer)
  - Preenchido durante análise semântica

**Árvore construída (exemplo: `a + b * c`):**
```
OperacaoBinaria('+',
    Identificador('a'),
    OperacaoBinaria('*',
        Identificador('b'),
        Identificador('c')
    )
)
```

**Por que armazenar operador como string:**
- Mais flexível que enumeração
- Facilita geração de código (mapeamento direto para instruções MVD)
- Independente de implementação de tokens

### Função `arvore_para_string` - Análise Detalhada

```python
def arvore_para_string(no: No, recuo: int = 0) -> str:
    """Converte um nó da AST para representação em string (para debug)."""
    prefixo = "  " * recuo
    
    if isinstance(no, Programa):
        resultado = f"{prefixo}Programa({no.nome})\n"
        if no.declaracoes_variaveis:
            resultado += arvore_para_string(no.declaracoes_variaveis, recuo + 1)
        for proc in no.procedimentos:
            resultado += arvore_para_string(proc, recuo + 1)
        for func in no.funcoes:
            resultado += arvore_para_string(func, recuo + 1)
        resultado += arvore_para_string(no.comando_composto, recuo + 1)
        return resultado
    # ... mais casos
```

**Explicação linha por linha:**

**1. Parâmetros:**
- `no: No`: Nó a converter (pode ser qualquer nó da AST)
- `recuo: int = 0`: Nível de indentação (usado recursivamente)

**2. Cálculo de prefixo:**
- `prefixo = "  " * recuo`: Cria string com espaços para indentação
  - `recuo=0`: "" (sem indentação)
  - `recuo=1`: "  " (2 espaços)
  - `recuo=2`: "    " (4 espaços)

**3. Processamento recursivo:**
- `if isinstance(no, Programa)`: Verifica tipo do nó
  - `isinstance()` verifica se objeto é instância da classe
- `resultado = f"{prefixo}Programa({no.nome})\n"`: 
  - Cria linha com nome do programa
  - `\n` para quebra de linha
- `if no.declaracoes_variaveis:`: Verifica se há declarações
  - `resultado += arvore_para_string(..., recuo + 1)`: 
    - **Recursão!** Converte subárvore com maior indentação
    - `recuo + 1` aumenta indentação para filhos
- `for proc in no.procedimentos:`: Itera sobre procedimentos
  - Converte cada procedimento recursivamente
- Similar para funções e comandos

**4. Retorno:**
- `return resultado`: Retorna string completa da subárvore

**Exemplo de saída:**
```
Programa(exemplo)
  DeclaracoesVariaveis
    DeclaracaoVar(x: inteiro)
  ComandoComposto
    Atribuicao(x :=)
      Numero(5)
```

**Por que recursão:**
- AST é estrutura recursiva (árvore)
- Cada nó pode ter filhos que também são nós
- Recursão naturalmente percorre toda a árvore
- Indentação reflete hierarquia visualmente

## Relação com as Notas de Aula

### Construção da Árvore Sintática

Conforme as notas de aula (seção 1.3), o analisador sintático:
- Verifica a ordem de apresentação dos tokens
- Monta a árvore sintática com base na gramática
- A árvore representa a estrutura das sentenças

A AST implementada segue essa descrição, sendo construída pelo analisador sintático durante o processo de parsing.

### Representação Intermediária

As notas de aula mencionam que a análise semântica cria uma "linguagem intermediária" a partir do texto fonte. A AST serve exatamente como essa representação intermediária:
- É independente da sintaxe concreta do código fonte
- Contém apenas informações essenciais
- É adequada para análise semântica e geração de código

### Gramática com Atributos

Conforme as notas de aula (seção 6.1), gramáticas com atributos permitem propagar valores pela árvore. A AST implementa isso através do atributo `tipo_expressao`, que é preenchido durante a análise semântica e usado na geração de código.

