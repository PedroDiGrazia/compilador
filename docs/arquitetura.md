# Arquitetura do Compilador LPD - Documentação Geral

## Visão Geral

Este documento descreve a arquitetura geral do compilador LPD, explicando como todos os módulos se integram e funcionam em conjunto para transformar código fonte em código executável.

## Estrutura do Compilador

O compilador LPD é composto de **10 módulos principais** (excluindo `criar_executaveis.py`):

1. **`tokens.py`** - Definições de tokens e exceções
2. **`analisador_lexico.py`** - Scanner (análise léxica)
3. **`arvore_sintatica.py`** - Estruturas da AST
4. **`analisador_sintatico.py`** - Parser (análise sintática)
5. **`tabela_simbolos.py`** - Gerenciamento de símbolos e escopos
6. **`analisador_semantico.py`** - Verificação semântica
7. **`gerador_codigo.py`** - Geração de código assembly
8. **`maquina_virtual.py`** - Executor da MVD
9. **`compilador.py`** - Orquestrador principal
10. **`interface.py`** - Interface gráfica

## Fluxo de Compilação Completo

### Diagrama de Fluxo

```
┌─────────────────┐
│  Código Fonte   │
│   (.txt)        │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│  Analisador Léxico  │ ← tokens.py
│  (Scanner)          │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Lista de Tokens    │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ Analisador Sintático│ ← arvore_sintatica.py
│  (Parser)           │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   AST (Programa)    │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ Analisador Semântico│ ← tabela_simbolos.py
│                     │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ AST Anotada +       │
│ Tabela de Símbolos  │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Gerador de Código  │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Código Assembly    │
│     (.obj)          │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Máquina Virtual    │
│      (MVD)          │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│     Saída           │
└─────────────────────┘
```

### Fase 1: Análise Léxica

**Módulo:** `analisador_lexico.py`  
**Dependências:** `tokens.py`

**Entrada:** Código fonte (string)  
**Saída:** Lista de tokens (`List[Token]`)

**Processo:**
1. Lê código fonte caractere por caractere
2. Remove espaços e comentários
3. Reconhece padrões (identificadores, números, operadores, etc.)
4. Classifica tokens usando `TipoToken`
5. Cria objetos `Token` com lexema, linha, coluna e valor

**Exemplo:**
```
Código: "programa teste; var x: inteiro;"
Tokens: [PROGRAMA, IDENTIFICADOR("teste"), PONTO_VIRGULA, VAR, IDENTIFICADOR("x"), DOIS_PONTOS, INTEIRO, PONTO_VIRGULA]
```

### Fase 2: Análise Sintática

**Módulo:** `analisador_sintatico.py`  
**Dependências:** `tokens.py`, `arvore_sintatica.py`

**Entrada:** Lista de tokens  
**Saída:** AST (`Programa`)

**Processo:**
1. Lê tokens sequencialmente
2. Verifica ordem conforme gramática LPD
3. Constrói nós da AST recursivamente
4. Retorna nó raiz `Programa`

**Estrutura da AST:**
```
Programa
├── nome: str
├── declaracoes_variaveis: DeclaracoesVariaveis
├── procedimentos: List[Procedimento]
├── funcoes: List[Funcao]
└── comando_composto: ComandoComposto
```

### Fase 3: Análise Semântica

**Módulo:** `analisador_semantico.py`  
**Dependências:** `arvore_sintatica.py`, `tabela_simbolos.py`, `tokens.py`

**Entrada:** AST  
**Saída:** AST anotada + Tabela de Símbolos

**Processo:**
1. Percorre AST recursivamente
2. Gerencia escopos (entra/sai conforme blocos)
3. Declara símbolos na tabela
4. Verifica uso de identificadores
5. Verifica compatibilidade de tipos
6. Anota AST com tipos (`tipo_expressao`)

**Tabela de Símbolos:**
- Gerencia escopos hierárquicos
- Armazena tipo, categoria, endereço de memória
- Suporta shadowing (símbolos com mesmo nome em escopos diferentes)

### Fase 4: Geração de Código

**Módulo:** `gerador_codigo.py`  
**Dependências:** `arvore_sintatica.py`, `tabela_simbolos.py`

**Entrada:** AST anotada + Tabela de Símbolos  
**Saída:** Lista de instruções assembly

**Processo:**
1. Reconstitui tabela de símbolos (para manter escopos corretos)
2. Percorre AST recursivamente
3. Gera código para cada construção:
   - Expressões → Instruções de pilha (LDC, LDV, ADD, etc.)
   - Comandos → Instruções de controle (JMP, JMPF, CALL, etc.)
   - Escopos → ALLOC/DALLOC
4. Gera rótulos para desvios e subrotinas
5. Retorna lista de strings com código assembly

**Estrutura do código gerado:**
```
START
ALLOC ... (variáveis globais)
JMP L_principal (se houver subrotinas)
[subrotinas]
L_principal NULL
[corpo principal]
DALLOC ...
HLT
```

### Fase 5: Execução

**Módulo:** `maquina_virtual.py`

**Entrada:** Arquivo `.obj` com código assembly  
**Saída:** Valores impressos

**Processo:**
1. Carrega programa assembly
2. Processa rótulos
3. Executa instruções sequencialmente
4. Gerencia pilha de dados
5. Trata I/O (RD, PRN)
6. Executa até HLT

## Estrutura de Dados Compartilhada

### Token

```python
@dataclass
class Token:
    tipo: TipoToken      # Tipo do token
    lexema: str          # Sequência de caracteres
    linha: int           # Linha no código fonte
    coluna: int          # Coluna no código fonte
    valor: Optional[object]  # Valor (para números, identificadores)
```

**Uso:** Passado do analisador léxico para o sintático.

### AST (Árvore Sintática Abstrata)

**Estrutura hierárquica:**
- `Programa` (raiz)
  - `DeclaracoesVariaveis`
  - `List[Procedimento]`
  - `List[Funcao]`
  - `ComandoComposto`
    - `List[Comando]`
      - `Atribuicao`, `ComandoSe`, `ComandoEnquanto`, etc.
      - `Expressao`
        - `OperacaoBinaria`, `Identificador`, `Numero`, etc.

**Uso:** Passada do analisador sintático para o semântico e gerador.

### Tabela de Símbolos

**Estrutura:**
- Lista de escopos (`List[InfoEscopo]`)
- Cada escopo contém dicionário de símbolos
- Cada símbolo tem: nome, tipo, categoria, nível, endereço

**Uso:** 
- Populada pelo analisador semântico
- Utilizada pelo gerador de código para obter endereços

## Integração entre Módulos

### Dependências Diretas

```
tokens.py
  ↑
  ├── analisador_lexico.py
  ├── analisador_sintatico.py
  └── analisador_semantico.py

arvore_sintatica.py
  ↑
  ├── analisador_sintatico.py
  ├── analisador_semantico.py
  └── gerador_codigo.py

tabela_simbolos.py
  ↑
  ├── analisador_semantico.py
  └── gerador_codigo.py

maquina_virtual.py
  ↑
  └── interface.py

compilador.py
  ↑
  ├── analisador_lexico.py
  ├── analisador_sintatico.py
  ├── analisador_semantico.py
  └── gerador_codigo.py

interface.py
  ↑
  └── maquina_virtual.py
```

### Fluxo de Dados Detalhado

#### Compilação Completa

```python
# 1. Análise Léxica
codigo_fonte = ler_arquivo("programa.txt")
tokens = AnalisadorLexico(codigo_fonte).obter_tokens()
# tokens: List[Token]

# 2. Análise Sintática
ast = AnalisadorSintatico(tokens).analisar()
# ast: Programa

# 3. Análise Semântica
analisador_semantico = AnalisadorSemantico()
tabela_simbolos = analisador_semantico.analisar(ast)
# ast: Programa (anotado com tipos)
# tabela_simbolos: TabelaSimbolos (populada)

# 4. Geração de Código
gerador = GeradorCodigo()
instrucoes = gerador.gerar(ast, tabela_simbolos)
# instrucoes: List[str]

# 5. Execução
mv = MaquinaVirtual()
mv.carregar_programa("programa.obj")
saida = mv.executar()
# saida: List[int]
```

## Gerenciamento de Escopos

### Modelo de Escopos

A tabela de símbolos utiliza **modelo de pilha** para escopos:

1. **Escopo Global** (nível 0):
   - Variáveis globais
   - Funções e procedimentos globais

2. **Escopos Locais** (nível 1+):
   - Variáveis locais de funções/procedimentos
   - Subrotinas aninhadas

### Endereçamento de Memória

**Estratégia:**
- Cada escopo tem um **endereço base**
- Variáveis são alocadas sequencialmente a partir do endereço base
- Endereço base do escopo filho = último endereço usado pelo escopo pai + 1

**Exemplo:**
```
Escopo Global (base=0):
  - retorno_funcao1: endereço 0
  - x: endereço 1
  - y: endereço 2

Escopo Função1 (base=3):
  - a: endereço 3
  - b: endereço 4
```

### ALLOC/DALLOC

**Geração:**
- `ALLOC m,n`: Ao entrar em escopo (aloca n variáveis a partir de m)
- `DALLOC m,n`: Ao sair de escopo (desaloca na ordem inversa)

**Ordem:** LIFO (Last In, First Out) - último escopo alocado é o primeiro desalocado.

## Tratamento de Erros

### Hierarquia de Erros

```
Exception
├── ErroLexico      (fase 1: análise léxica)
├── ErroSintatico   (fase 2: análise sintática)
└── ErroSemantico   (fase 3: análise semântica)
```

### Propagação de Erros

1. **Erro Léxico**: Detectado no `AnalisadorLexico`, interrompe compilação
2. **Erro Sintático**: Detectado no `AnalisadorSintatico`, interrompe compilação
3. **Erro Semântico**: Detectado no `AnalisadorSemantico`, interrompe compilação
4. **Erro de Execução**: Detectado na `MaquinaVirtual`, interrompe execução

### Mensagens de Erro

Todas as exceções incluem:
- **Mensagem descritiva**: Explica o erro
- **Localização**: Linha e coluna (quando disponível)

## Exemplo Completo

### Programa Fonte

```lpd
programa exemplo;
var x: inteiro;
inicio
    x := 5;
    escreva(x);
fim.
```

### Fase 1: Tokens

```python
[
    Token(PROGRAMA, "programa", 1, 1),
    Token(IDENTIFICADOR, "exemplo", 1, 10),
    Token(PONTO_VIRGULA, ";", 1, 17),
    Token(VAR, "var", 2, 1),
    Token(IDENTIFICADOR, "x", 2, 5),
    Token(DOIS_PONTOS, ":", 2, 6),
    Token(INTEIRO, "inteiro", 2, 8),
    Token(PONTO_VIRGULA, ";", 2, 15),
    Token(INICIO, "inicio", 3, 1),
    Token(IDENTIFICADOR, "x", 4, 5),
    Token(ATRIBUICAO, ":=", 4, 7),
    Token(NUMERO, "5", 4, 10, valor=5),
    Token(PONTO_VIRGULA, ";", 4, 11),
    Token(ESCREVA, "escreva", 5, 5),
    Token(ABRE_PARENTESES, "(", 5, 12),
    Token(IDENTIFICADOR, "x", 5, 13),
    Token(FECHA_PARENTESES, ")", 5, 14),
    Token(PONTO_VIRGULA, ";", 5, 15),
    Token(FIM, "fim", 6, 1),
    Token(PONTO, ".", 6, 4),
    Token(FIM_ARQUIVO, "", 6, 5)
]
```

### Fase 2: AST

```python
Programa(
    nome="exemplo",
    declaracoes_variaveis=DeclaracoesVariaveis([
        DeclaracaoVariavel(["x"], "inteiro")
    ]),
    procedimentos=[],
    funcoes=[],
    comando_composto=ComandoComposto([
        Atribuicao("x", Numero(5)),
        ComandoEscrita(Identificador("x"))
    ])
)
```

### Fase 3: Tabela de Símbolos

```
Escopo 0 (base=0, vars=1):
  x: inteiro (variavel) @ 0
```

### Fase 4: Código Assembly

```
START
ALLOC 0 1
LDC 5
STR 0
LDV 0
PRN
DALLOC 0 1
HLT
```

### Fase 5: Execução

```
Saída: 5
```

## Relação com as Notas de Aula

### Estrutura Geral dos Compiladores

Conforme as notas de aula (seção 1), o compilador LPD implementa todas as fases descritas:

1. ✅ **Analisador Léxico**: Fragmenta código em tokens
2. ✅ **Analisador Sintático**: Verifica sintaxe e constrói AST
3. ✅ **Analisador Semântico**: Verifica semântica e tipos
4. ✅ **Gerenciador da Tabela de Símbolos**: Gerencia declarações e escopos
5. ✅ **Gerador de Código**: Produz código assembly

### Linguagem LPD

A implementação segue a especificação BNF da linguagem LPD descrita nas notas de aula (seção 2.1):
- Estrutura de programa
- Declarações de variáveis
- Procedimentos e funções
- Comandos e expressões

### Máquina Virtual Didática

A implementação da MVD segue a especificação das notas de aula (seção 7):
- Arquitetura a pilha
- Instruções descritas
- ALLOC/DALLOC para escopos
- CALL/RETURN para subrotinas

## Conclusão

O compilador LPD é uma implementação completa e didática que demonstra todos os conceitos fundamentais de compiladores:
- Análise léxica, sintática e semântica
- Gerenciamento de escopos e tabela de símbolos
- Geração de código para máquina virtual
- Execução de código gerado

Cada módulo tem responsabilidades bem definidas e se integra harmoniosamente com os demais, formando um sistema completo e funcional.

