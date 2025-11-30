# Compilador Principal - Documentação

## Introdução e Teoria

### Base Teórica

O arquivo `compilador.py` é o **orquestrador principal** do compilador LPD. Ele coordena todas as fases de compilação: análise léxica, sintática, semântica e geração de código.

Conforme as notas de aula (seção 1), um compilador é composto de várias fases que trabalham em conjunto:
1. **Análise Léxica**: Converte código fonte em tokens
2. **Análise Sintática**: Constrói a AST
3. **Análise Semântica**: Verifica tipos e declarações
4. **Geração de Código**: Produz código assembly

O `compilador.py` implementa o fluxo completo de compilação e oferece opções para executar fases individuais.

## Estrutura do Código

### Funções Principais

#### `main()`

Função principal que processa argumentos da linha de comando e executa a compilação.

**Processo:**
1. Verifica argumentos
2. Lê arquivo fonte
3. Determina modo de operação
4. Executa fase(s) solicitada(s)
5. Trata erros e exibe mensagens

**Modos de operação:**
- `--lexico`: Apenas análise léxica
- `--sintatico`: Análise léxica + sintática
- `--semantico`: Análise léxica + sintática + semântica
- (padrão): Compilação completa

#### `imprimir_uso()`

Imprime instruções de uso do compilador.

**Uso:** Exibido quando não há argumentos ou com `--ajuda`.

### Funções de Análise Individual

#### `executar_lexico(codigo_fonte: str)`

Executa apenas a análise léxica.

**Processo:**
1. Cria `AnalisadorLexico`
2. Obtém lista de tokens
3. Imprime tokens formatados (linha, coluna, tipo, lexema, valor)

**Saída:**
```
=== ANÁLISE LÉXICA ===

  1:1  PROGRAMA      'programa'
  1:10 IDENTIFICADOR 'exemplo'
  ...
```

#### `executar_sintatico(codigo_fonte: str)`

Executa análise léxica e sintática.

**Processo:**
1. Executa análise léxica
2. Cria `AnalisadorSintatico` e analisa tokens
3. Imprime AST formatada

**Saída:**
```
=== ANÁLISE LÉXICA ===
[OK] Análise léxica concluída: 15 tokens

=== ANÁLISE SINTÁTICA ===
[OK] Análise sintática concluída

=== ÁRVORE SINTÁTICA ABSTRATA (AST) ===
Programa(exemplo)
  ...
```

#### `executar_semantico(codigo_fonte: str)`

Executa análise léxica, sintática e semântica.

**Processo:**
1. Executa análise léxica
2. Executa análise sintática
3. Cria `AnalisadorSemantico` e analisa AST
4. Imprime tabela de símbolos

**Saída:**
```
=== ANÁLISE LÉXICA ===
[OK] Análise léxica concluída: 15 tokens

=== ANÁLISE SINTÁTICA ===
[OK] Análise sintática concluída

=== ANÁLISE SEMÂNTICA ===
[OK] Análise semântica concluída

=== TABELA DE SÍMBOLOS ===
=== Tabela de Símbolos ===
Escopo 0 (base=0, vars=1):
  x: inteiro (variavel) @ 0
  ...
```

### Função de Compilação Completa

#### `compilar_programa(codigo_fonte: str, arquivo_saida: str = "saida.obj")`

Executa compilação completa (todas as fases).

**Parâmetros:**
- `codigo_fonte`: Código fonte como string
- `arquivo_saida`: Nome do arquivo de saída (padrão: "saida.obj")

**Processo:**
1. **Análise Léxica**: Cria `AnalisadorLexico` e obtém tokens
2. **Análise Sintática**: Cria `AnalisadorSintatico` e constrói AST
3. **Análise Semântica**: Cria `AnalisadorSemantico` e verifica semântica
4. **Geração de Código**: Cria `GeradorCodigo` e gera código assembly
5. Salva código em arquivo
6. Imprime código gerado

**Saída:**
```
=== COMPILADOR LPD ===

[1/4] Análise Léxica... OK (15 tokens)
[2/4] Análise Sintática... OK
[3/4] Análise Semântica... OK (3 variáveis)
[4/4] Geração de Código... OK (25 instruções)

[OK] Compilação concluída com sucesso!
      Código gerado em: programa.obj

=== CÓDIGO GERADO ===
START
ALLOC 0 1
...
HLT
```

## Tratamento de Erros

### Códigos de Saída

O compilador utiliza códigos de saída diferentes para cada tipo de erro:
- **0**: Sucesso
- **1**: Erro de argumentos/uso
- **2**: Erro léxico (`ErroLexico`)
- **3**: Erro sintático (`ErroSintatico`)
- **4**: Erro semântico (`ErroSemantico`)
- **5**: Erro interno (exceção não tratada)

### Tratamento de Exceções

```python
try:
    # Compilação
except ErroLexico as e:
    print(f"\n[ERRO] ERRO LÉXICO: {e}")
    sys.exit(2)
except ErroSintatico as e:
    print(f"\n[ERRO] ERRO SINTÁTICO: {e}")
    sys.exit(3)
except ErroSemantico as e:
    print(f"\n[ERRO] ERRO SEMÂNTICO: {e}")
    sys.exit(4)
except Exception as e:
    print(f"\n[ERRO] ERRO INTERNO: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(5)
```

## Integração

### Fluxo Completo de Compilação

```
Código Fonte (.txt)
    ↓
compilador.py main()
    ↓
Lê arquivo
    ↓
AnalisadorLexico.obter_tokens()
    ↓
Lista de Tokens
    ↓
AnalisadorSintatico.analisar()
    ↓
AST (Programa)
    ↓
AnalisadorSemantico.analisar()
    ↓
AST Anotada + TabelaSimbolos
    ↓
GeradorCodigo.gerar()
    ↓
Código Assembly
    ↓
Arquivo .obj
```

### Dependências

- **`analisador_lexico`**: `AnalisadorLexico`
- **`tokens`**: `TipoToken`, `ErroLexico`, `ErroSintatico`, `ErroSemantico`
- **`analisador_sintatico`**: `AnalisadorSintatico`
- **`analisador_semantico`**: `AnalisadorSemantico`
- **`gerador_codigo`**: `GeradorCodigo`
- **`arvore_sintatica`**: `arvore_para_string`

## Exemplos Práticos

### Exemplo 1: Compilação Completa

```bash
python3 compilador.py programa.txt
```

**Saída:**
```
=== COMPILADOR LPD ===

[1/4] Análise Léxica... OK (25 tokens)
[2/4] Análise Sintática... OK
[3/4] Análise Semântica... OK (5 variáveis)
[4/4] Geração de Código... OK (42 instruções)

[OK] Compilação concluída com sucesso!
      Código gerado em: programa.obj
```

### Exemplo 2: Apenas Análise Léxica

```bash
python3 compilador.py programa.txt --lexico
```

**Saída:**
```
=== ANÁLISE LÉXICA ===

  1:1  PROGRAMA      'programa'
  1:10 IDENTIFICADOR 'exemplo'
  ...
```

### Exemplo 3: Análise até Semântica

```bash
python3 compilador.py programa.txt --semantico
```

**Saída:**
```
=== ANÁLISE LÉXICA ===
[OK] Análise léxica concluída: 25 tokens

=== ANÁLISE SINTÁTICA ===
[OK] Análise sintática concluída

=== ANÁLISE SEMÂNTICA ===
[OK] Análise semântica concluída

=== TABELA DE SÍMBOLOS ===
...
```

### Exemplo 4: Tratamento de Erro

```bash
python3 compilador.py programa_errado.txt
```

**Saída:**
```
=== COMPILADOR LPD ===

[1/4] Análise Léxica... OK (20 tokens)
[2/4] Análise Sintática... OK
[3/4] Análise Semântica... 

[ERRO] ERRO SEMÂNTICO: Variável 'x' não foi declarada
```

## Análise Detalhada do Código

### Função `compilar_programa` - Análise Detalhada

```python
def compilar_programa(codigo_fonte: str, arquivo_saida: str = "saida.obj"):
    """Executa compilação completa."""
    print("=== COMPILADOR LPD ===\n")
    
    # Análise Léxica
    print("[1/4] Análise Léxica...", end=" ")
    tokens = AnalisadorLexico(codigo_fonte).obter_tokens()
    print(f"OK ({len([t for t in tokens if t.tipo != TipoToken.FIM_ARQUIVO])} tokens)")
    
    # Análise Sintática
    print("[2/4] Análise Sintática...", end=" ")
    ast = AnalisadorSintatico(tokens).analisar()
    print("OK")
    
    # Análise Semântica
    print("[3/4] Análise Semântica...", end=" ")
    analisador = AnalisadorSemantico()
    tabela_simbolos = analisador.analisar(ast)
    print(f"OK ({tabela_simbolos.obter_tamanho_memoria()} variáveis)")
    
    # Geração de Código
    print("[4/4] Geração de Código...", end=" ")
    gerador = GeradorCodigo()
    instrucoes = gerador.gerar(ast, tabela_simbolos)
    print(f"OK ({len(instrucoes)} instruções)")
    
    # Salva código gerado
    gerador.salvar_em_arquivo(arquivo_saida)
    print(f"\n[OK] Compilação concluída com sucesso!")
    print(f"      Código gerado em: {arquivo_saida}")
    
    # Mostra código gerado
    print(f"\n=== CÓDIGO GERADO ===")
    print(gerador.obter_codigo())
```

**Explicação linha por linha:**

**1. Análise Léxica:**
- `tokens = AnalisadorLexico(codigo_fonte).obter_tokens()`: 
  - Cria instância do analisador léxico com código fonte
  - Chama `obter_tokens()` que retorna lista completa de tokens
  - `AnalisadorLexico` é criado e usado imediatamente (não precisa manter referência)
- `len([t for t in tokens if t.tipo != TipoToken.FIM_ARQUIVO])`: 
  - Filtra tokens (remove FIM_ARQUIVO da contagem)
  - Lista por compreensão cria lista apenas com tokens válidos
  - `len()` conta quantidade

**2. Análise Sintática:**
- `ast = AnalisadorSintatico(tokens).analisar()`: 
  - Cria analisador sintático com lista de tokens
  - Chama `analisar()` que retorna nó `Programa` (raiz da AST)
  - Se houver erro sintático, exceção é lançada e função termina

**3. Análise Semântica:**
- `analisador = AnalisadorSemantico()`: Cria instância do analisador semântico
  - Instância é mantida (pode ser útil para debug)
- `tabela_simbolos = analisador.analisar(ast)`: 
  - Analisa AST semanticamente
  - Retorna tabela de símbolos populada
  - AST é anotada com tipos durante análise
- `tabela_simbolos.obter_tamanho_memoria()`: 
  - Retorna tamanho total de memória necessária
  - Usado para exibir informação ao usuário

**4. Geração de Código:**
- `gerador = GeradorCodigo()`: Cria instância do gerador
- `instrucoes = gerador.gerar(ast, tabela_simbolos)`: 
  - Gera código assembly a partir da AST
  - Retorna lista de strings (instruções)
- `gerador.salvar_em_arquivo(arquivo_saida)`: 
  - Salva código em arquivo `.obj`
  - Método interno do gerador escreve arquivo
- `gerador.obter_codigo()`: 
  - Retorna código como string única (junta instruções com `\n`)
  - Exibido para o usuário ver código gerado

**Fluxo de exceções:**
- Se qualquer fase lançar exceção, `main()` captura e exibe erro
- Códigos de saída diferentes para cada tipo de erro
- Compilação para na primeira fase com erro

### Função `main` - Análise Detalhada

```python
def main():
    # Se não tem argumentos, mostra ajuda
    if len(sys.argv) < 2:
        imprimir_uso()
        sys.exit(1)
    
    # Se pede ajuda
    if "--ajuda" in sys.argv or "-a" in sys.argv:
        imprimir_uso()
        sys.exit(0)
    
    # Arquivo de entrada
    arquivo_entrada = sys.argv[1]
    
    # Lê arquivo fonte
    try:
        with open(arquivo_entrada, "r", encoding="utf-8") as f:
            codigo_fonte = f.read()
    except FileNotFoundError:
        print(f"Erro: Arquivo '{arquivo_entrada}' não encontrado")
        sys.exit(1)
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        sys.exit(1)
    
    # Determina modo de operação
    modo = "compilar"  # padrão
    
    if "--lexico" in sys.argv:
        modo = "lexico"
    elif "--sintatico" in sys.argv:
        modo = "sintatico"
    elif "--semantico" in sys.argv:
        modo = "semantico"
    
    # Define arquivo de saída na mesma pasta do compilador
    nome_base = os.path.basename(arquivo_entrada).replace('.txt', '.obj')
    arquivo_saida = nome_base
    
    # Executa compilação
    try:
        if modo == "lexico":
            executar_lexico(codigo_fonte)
        elif modo == "sintatico":
            executar_sintatico(codigo_fonte)
        elif modo == "semantico":
            executar_semantico(codigo_fonte)
        else:  # compilar
            compilar_programa(codigo_fonte, arquivo_saida)
    
    except ErroLexico as e:
        print(f"\n[ERRO] ERRO LÉXICO: {e}")
        sys.exit(2)
    except ErroSintatico as e:
        print(f"\n[ERRO] ERRO SINTÁTICO: {e}")
        sys.exit(3)
    except ErroSemantico as e:
        print(f"\n[ERRO] ERRO SEMÂNTICO: {e}")
        sys.exit(4)
    except Exception as e:
        print(f"\n[ERRO] ERRO INTERNO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(5)
```

**Explicação linha por linha:**

**1. Verificação de argumentos:**
- `if len(sys.argv) < 2`: Verifica se há pelo menos 1 argumento (além nome do script)
  - `sys.argv[0]` = nome do script
  - `sys.argv[1]` = primeiro argumento (arquivo)
- `imprimir_uso()`: Exibe instruções de uso
- `sys.exit(1)`: Termina com código de erro

**2. Verificação de ajuda:**
- `if "--ajuda" in sys.argv or "-a" in sys.argv`: Verifica flags de ajuda
- `sys.exit(0)`: Termina com sucesso (ajuda não é erro)

**3. Leitura do arquivo:**
- `arquivo_entrada = sys.argv[1]`: Obtém nome do arquivo do primeiro argumento
- `with open(arquivo_entrada, "r", encoding="utf-8") as f:`: 
  - Abre arquivo em modo leitura
  - `encoding="utf-8"` garante suporte a caracteres especiais
  - `with` garante fechamento automático do arquivo
- `codigo_fonte = f.read()`: Lê todo o conteúdo do arquivo como string
- `except FileNotFoundError`: Captura erro se arquivo não existe
- `except Exception`: Captura outros erros de leitura

**4. Determinação do modo:**
- `modo = "compilar"`: Modo padrão (compilação completa)
- Verifica flags na ordem: `--lexico`, `--sintatico`, `--semantico`
- Apenas uma flag é processada (primeira encontrada)

**5. Definição de arquivo de saída:**
- `os.path.basename(arquivo_entrada)`: Obtém apenas nome do arquivo (sem caminho)
- `.replace('.txt', '.obj')`: Substitui extensão `.txt` por `.obj`
- Arquivo é salvo no diretório atual (não no diretório do arquivo fonte)

**6. Execução:**
- `try/except`: Captura exceções de cada fase
- Cada modo chama função específica
- Exceções específicas (`ErroLexico`, etc.) são capturadas separadamente
- `Exception` genérica captura erros inesperados (com traceback)

**7. Tratamento de erros:**
- Cada tipo de erro tem código de saída diferente:
  - `sys.exit(2)`: Erro léxico
  - `sys.exit(3)`: Erro sintático
  - `sys.exit(4)`: Erro semântico
  - `sys.exit(5)`: Erro interno
- `traceback.print_exc()`: Imprime stack trace para erros internos (debug)

## Relação com as Notas de Aula

### Estrutura do Compilador

Conforme as notas de aula (seção 1), um compilador possui várias fases que trabalham em conjunto. O `compilador.py` implementa exatamente essa estrutura:

1. **Analisador Léxico**: Fragmenta código em tokens
2. **Analisador Sintático**: Verifica sintaxe e constrói AST
3. **Analisador Semântico**: Verifica semântica e tipos
4. **Gerador de Código**: Produz código assembly

### Fluxo de Compilação

O fluxo implementado segue o modelo descrito nas notas de aula:
- Cada fase consome saída da fase anterior
- Erros são detectados e reportados em cada fase
- A compilação pode ser interrompida a qualquer momento por erro

### Tratamento de Erros

Conforme as notas de aula (seção 5.4), o compilador deve:
- Reportar erros claramente
- Indicar localização do erro (linha, coluna)
- Fornecer mensagens informativas

A implementação faz isso através das exceções específicas (`ErroLexico`, `ErroSintatico`, `ErroSemantico`) que incluem linha e coluna.

