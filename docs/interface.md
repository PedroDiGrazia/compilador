# Interface Gráfica - Documentação

## Introdução e Teoria

### Base Teórica

A **Interface Gráfica** (`interface.py`) fornece uma interface visual para o compilador LPD usando **Tkinter**. Ela permite compilar programas e executá-los na Máquina Virtual de forma interativa, sem necessidade de linha de comando.

A interface gráfica facilita:
- **Compilação visual**: Ver resultados de cada fase
- **Execução interativa**: Executar programas com entrada do usuário
- **Debugging**: Visualizar saída do compilador e da máquina virtual

## Estrutura do Código

### Classe Principal: `InterfaceCompilador`

A classe `InterfaceCompilador` gerencia toda a interface gráfica.

#### Atributos da Classe

```python
def __init__(self, janela):
    self.janela = janela                          # Janela principal Tkinter
    self.arquivo_fonte = tk.StringVar()          # Caminho do arquivo fonte
    self.arquivo_objeto = tk.StringVar()         # Nome do arquivo objeto
    self.entrada_usuario = tk.StringVar()        # Entrada do usuário
    self.mv = None                                # Instância da Máquina Virtual
    self.thread_mv = None                         # Thread para execução da MV
    self.aguardando_entrada = False              # Flag de espera de entrada
    self.evento_entrada = threading.Event()      # Evento para sincronização
    self.valor_entrada = None                     # Valor digitado pelo usuário
```

**Estrutura:**
- Variáveis Tkinter para armazenar valores da interface
- Instância da Máquina Virtual para execução
- Threading para execução não-bloqueante
- Sincronização para entrada interativa

### Métodos de Interface

#### `criar_interface()`

Cria todos os componentes da interface gráfica.

**Componentes criados:**
1. **Seção 1 - Seleção de Arquivo**:
   - Campo de texto para caminho do arquivo
   - Botão "Procurar..." para selecionar arquivo

2. **Seção 2 - Compilar**:
   - Botões para análises individuais: "Léxico", "Sintático", "Semântico"
   - Botões principais: "COMPILAR", "EXECUTAR VM"

3. **Seção 3 - Saída**:
   - Área de texto com scroll para exibir saída
   - Campo de entrada para valores (quando MV aguarda entrada)
   - Botão "Enviar" para enviar entrada

4. **Barra de Status**: Exibe status atual

#### `selecionar_arquivo()`

Abre diálogo para selecionar arquivo `.txt`.

**Processo:**
1. Abre `filedialog.askopenfilename()`
2. Define `arquivo_fonte` com caminho selecionado
3. Define `arquivo_objeto` como `.obj` correspondente
4. Atualiza status e adiciona mensagem à saída

#### `adicionar_saida(texto, tag=None)`

Adiciona texto à área de saída.

**Parâmetros:**
- `texto`: Texto a adicionar
- `tag`: Tag de formatação (opcional: "info", "sucesso", "erro", "prompt", "input", "output")

**Processo:**
1. Insere texto na área de saída
2. Rola para o final automaticamente
3. Atualiza interface

#### `limpar_saida()`

Limpa a área de saída.

### Métodos de Execução

#### `executar_comando(comando, titulo)`

Executa um comando do sistema e mostra resultado.

**Parâmetros:**
- `comando`: Comando shell a executar
- `titulo`: Título da operação

**Processo:**
1. Executa comando via `subprocess.run()`
2. Captura stdout e stderr
3. Adiciona saída à interface
4. Atualiza status conforme resultado

**Uso:** Executar análises individuais via linha de comando.

#### `executar_lexico()`

Executa apenas análise léxica.

**Comando:** `python3 compilador.py {arquivo} --lexico`

#### `executar_sintatico()`

Executa análise sintática.

**Comando:** `python3 compilador.py {arquivo} --sintatico`

#### `executar_semantico()`

Executa análise semântica.

**Comando:** `python3 compilador.py {arquivo} --semantico`

#### `compilar()`

Compila o programa completo.

**Comando:** `python3 compilador.py {arquivo}`

**Processo:**
1. Verifica se arquivo foi selecionado
2. Executa compilação
3. Exibe resultado na interface

### Execução da Máquina Virtual

#### `executar_mv()`

Inicia execução da Máquina Virtual em thread separada.

**Processo:**
1. Verifica se programa foi compilado
2. Cria thread para execução (`_executar_mv_thread`)
3. Inicia thread (não bloqueia interface)

#### `_executar_mv_thread()`

Executa a MV em thread separada.

**Processo:**
1. Cria instância de `MaquinaVirtual`
2. Carrega programa compilado
3. Chama `_executar_mv_interativo()` para execução passo a passo
4. Trata erros e atualiza interface

#### `_executar_mv_interativo()`

Executa a MV instrução por instrução com suporte a entrada interativa.

**Processo:**
1. Loop principal:
   - Lê instrução atual
   - Se `RD`: Habilita entrada e aguarda valor do usuário
   - Se `PRN`: Exibe valor na interface
   - Caso contrário: Executa instrução normalmente
2. Continua até `HLT` ou erro

**Tratamento especial:**
- **RD**: Aguarda entrada do usuário através de evento
- **PRN**: Exibe valor formatado na interface

#### `_habilitar_entrada()` / `_desabilitar_entrada()`

Gerencia estado do campo de entrada.

**Processo:**
- Habilita campo e botão quando MV aguarda entrada
- Desabilita quando entrada foi processada

#### `enviar_entrada(evento=None)`

Envia valor digitado para a MV.

**Processo:**
1. Obtém valor do campo de entrada
2. Define `valor_entrada`
3. Sinaliza evento (`evento_entrada.set()`)
4. Limpa campo

## Integração

### Uso pelo Usuário

A interface é iniciada assim:

```bash
python3 interface.py
```

Ou:

```python
from interface import main
main()
```

### Fluxo de Uso

```
1. Usuário seleciona arquivo .txt
   ↓
2. Usuário clica "COMPILAR"
   ↓
3. Interface executa compilador.py
   ↓
4. Código .obj é gerado
   ↓
5. Usuário clica "EXECUTAR VM"
   ↓
6. Interface carrega e executa código na MV
   ↓
7. Se programa pede entrada, interface aguarda
   ↓
8. Usuário digita valor e clica "Enviar"
   ↓
9. MV continua execução
   ↓
10. Saída é exibida na interface
```

### Dependências

- **`tkinter`**: Interface gráfica
- **`subprocess`**: Execução de comandos
- **`threading`**: Execução não-bloqueante
- **`maquina_virtual`**: `MaquinaVirtual`, `ErroMVD`

## Exemplos Práticos

### Exemplo 1: Compilação via Interface

1. Abrir interface: `python3 interface.py`
2. Clicar "Procurar..." e selecionar `programa.txt`
3. Clicar "COMPILAR"
4. Ver resultado na área de saída

### Exemplo 2: Execução Interativa

1. Após compilar, clicar "EXECUTAR VM"
2. Se programa tem `leia()`, campo de entrada aparece
3. Digitar valor e clicar "Enviar"
4. Ver saída na área de texto

### Exemplo 3: Análise Individual

1. Selecionar arquivo
2. Clicar "Léxico" para ver apenas tokens
3. Clicar "Sintático" para ver AST
4. Clicar "Semântico" para ver tabela de símbolos

## Análise Detalhada do Código

### Método `_executar_mv_interativo` - Análise Detalhada

```python
def _executar_mv_interativo(self):
    """Executa a MV instrução por instrução com suporte a entrada interativa."""
    self.mv.executando = True
    self.mv.i = 0
    self.mv.s = -1
    self.mv.saida = []
    
    while self.mv.executando and self.mv.i < len(self.mv.P):
        instrucao, operandos = self.mv.P[self.mv.i]
        
        # Tratamento especial para RD (leitura)
        if instrucao == 'RD':
            self._habilitar_entrada()
            self.adicionar_saida("Digite um valor inteiro: ", "prompt")
            
            # Aguarda entrada do usuário
            self.evento_entrada.clear()
            self.evento_entrada.wait()
            
            # Processa o valor
            try:
                valor = int(self.valor_entrada)
                self.mv.s += 1
                self.mv.M[self.mv.s] = valor
                self.adicionar_saida(f"{valor}\n", "input")
                self.mv.i += 1
            except (ValueError, TypeError):
                raise ErroMVD("Entrada inválida: esperado inteiro")
                
            self._desabilitar_entrada()
            
        # Tratamento especial para PRN (impressão)
        elif instrucao == 'PRN':
            if self.mv.s < 0:
                raise ErroMVD("Stack underflow em PRN")
            valor = self.mv.M[self.mv.s]
            self.adicionar_saida(f"{valor}\n", "output")
            self.mv.saida.append(valor)
            self.mv.s -= 1
            self.mv.i += 1
            
        # Outras instruções
        else:
            self.mv._executar_instrucao(instrucao, operandos)
```

**Explicação linha por linha:**

**1. Inicialização:**
- `self.mv.executando = True`: Flag de controle (True = continua execução)
- `self.mv.i = 0`: Inicializa program counter (primeira instrução)
- `self.mv.s = -1`: Inicializa stack pointer (pilha vazia)
- `self.mv.saida = []`: Lista para acumular valores impressos

**2. Loop principal:**
- `while self.mv.executando and self.mv.i < len(self.mv.P)`: 
  - Continua enquanto `executando=True` E há instruções
  - `self.mv.executando` vira `False` quando encontra `HLT`
- `instrucao, operandos = self.mv.P[self.mv.i]`: 
  - Lê instrução atual da memória de programa
  - `P` é lista de tuplas `(instrucao, operandos)`

**3. Tratamento especial de RD:**
- `if instrucao == 'RD'`: Detecta instrução de leitura
- `self._habilitar_entrada()`: Habilita campo de entrada na interface
  - Atualiza interface para permitir digitação
- `self.adicionar_saida("Digite um valor inteiro: ", "prompt")`: 
  - Exibe prompt na área de saída
  - Tag "prompt" permite formatação especial
- `self.evento_entrada.clear()`: Limpa evento (prepara para nova espera)
- `self.evento_entrada.wait()`: **Bloqueia até evento ser sinalizado**
  - Thread fica aguardando usuário digitar e clicar "Enviar"
  - `evento_entrada.set()` é chamado quando usuário envia valor
- `valor = int(self.valor_entrada)`: Converte entrada para inteiro
  - `self.valor_entrada` foi definido por `enviar_entrada()`
- `self.mv.s += 1`: Incrementa topo da pilha
- `self.mv.M[self.mv.s] = valor`: Armazena valor lido na pilha
- `self.adicionar_saida(f"{valor}\n", "input")`: Exibe valor digitado
- `self.mv.i += 1`: Avança para próxima instrução
- `self._desabilitar_entrada()`: Desabilita campo de entrada

**Por que usar evento:**
- Thread de execução precisa aguardar entrada do usuário
- `Event.wait()` bloqueia thread até `Event.set()` ser chamado
- Interface gráfica (thread principal) não trava durante espera
- Permite execução não-bloqueante

**4. Tratamento especial de PRN:**
- `elif instrucao == 'PRN'`: Detecta instrução de impressão
- `if self.mv.s < 0`: Verifica se pilha não está vazia
- `valor = self.mv.M[self.mv.s]`: Obtém valor do topo da pilha
- `self.adicionar_saida(f"{valor}\n", "output")`: 
  - Exibe valor na interface (tag "output" para formatação)
  - `\n` para quebra de linha
- `self.mv.saida.append(valor)`: Adiciona à lista de saída
- `self.mv.s -= 1`: Remove valor da pilha
- `self.mv.i += 1`: Avança

**5. Outras instruções:**
- `else`: Todas as outras instruções
- `self.mv._executar_instrucao(instrucao, operandos)`: 
  - Delega execução para método da máquina virtual
  - Método interno executa instrução e atualiza estado

**Por que tratamento especial de RD/PRN:**
- Interface gráfica precisa interagir com usuário
- RD: Aguarda entrada do usuário (não pode usar `input()` que trava GUI)
- PRN: Exibe na interface (não apenas `print()` no terminal)
- Outras instruções: Executam normalmente (sem interação)

### Método `enviar_entrada` - Análise Detalhada

```python
def enviar_entrada(self, evento=None):
    """Envia o valor digitado para a MV."""
    if self.aguardando_entrada:
        self.valor_entrada = self.entrada_usuario.get().strip()
        self.entrada_usuario.set("")
        self.evento_entrada.set()
```

**Explicação linha por linha:**
- `if self.aguardando_entrada`: Verifica se MV está aguardando entrada
  - Flag controlada por `_habilitar_entrada()` / `_desabilitar_entrada()`
- `self.valor_entrada = self.entrada_usuario.get().strip()`: 
  - `self.entrada_usuario` é `StringVar` do Tkinter
  - `.get()` obtém texto do campo de entrada
  - `.strip()` remove espaços em branco no início/fim
- `self.entrada_usuario.set("")`: Limpa campo de entrada
- `self.evento_entrada.set()`: **Sinaliza evento**
  - Libera thread que estava aguardando em `evento_entrada.wait()`
  - Thread de execução continua processando valor

**Fluxo de sincronização:**
```
Thread MV:                    Thread GUI:
  ...                           ...
  RD detectado                  Usuário digita valor
  habilita entrada              Usuário clica "Enviar"
  evento.clear()                enviar_entrada() chamado
  evento.wait()  ────────────→  valor_entrada = texto
  (BLOQUEADO)                   evento.set()
  (AGUARDANDO)  ←────────────   
  valor recebido
  continua execução
```

**Por que usar threading:**
- Interface gráfica roda na thread principal
- Execução da MV em thread separada evita travar interface
- Evento permite comunicação entre threads de forma segura

### Método `executar_comando` - Análise Detalhada

```python
def executar_comando(self, comando, titulo):
    """Executa um comando e mostra o resultado."""
    if not self.arquivo_fonte.get():
        messagebox.showwarning("Aviso", "Selecione um arquivo .txt primeiro!")
        return
        
    self.adicionar_saida(f"\n{'='*50}\n", "info")
    self.adicionar_saida(f"{titulo}\n", "info")
    self.adicionar_saida(f"{'='*50}\n", "info")
    self.status.set(f"Executando: {titulo}...")
    self.janela.update()
    
    try:
        resultado = subprocess.run(
            comando,
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        if resultado.stdout:
            self.adicionar_saida(resultado.stdout)
            
        if resultado.stderr:
            self.adicionar_saida(resultado.stderr, "erro")
            
        if resultado.returncode == 0:
            self.adicionar_saida(f"\n[OK] {titulo} concluído\n", "sucesso")
            self.status.set(f"{titulo} - OK")
        else:
            self.adicionar_saida(f"\n[ERRO] {titulo} falhou\n", "erro")
            self.status.set(f"{titulo} - Erro")
            
    except Exception as e:
        self.adicionar_saida(f"\n[ERRO] {str(e)}\n", "erro")
        self.status.set("Erro")
```

**Explicação linha por linha:**

**1. Validação:**
- `if not self.arquivo_fonte.get()`: Verifica se arquivo foi selecionado
  - `arquivo_fonte` é `StringVar` do Tkinter
  - `.get()` retorna string (vazia se não selecionado)
- `messagebox.showwarning(...)`: Exibe diálogo de aviso
- `return`: Para execução se não há arquivo

**2. Preparação da interface:**
- `self.adicionar_saida(...)`: Adiciona cabeçalho formatado
- `self.status.set(...)`: Atualiza barra de status
- `self.janela.update()`: Força atualização da interface
  - Garante que mensagens apareçam antes de executar comando

**3. Execução do comando:**
- `subprocess.run(...)`: Executa comando do sistema
  - `comando`: String com comando shell (ex: `"python3 compilador.py arquivo.txt --lexico"`)
  - `shell=True`: Executa através do shell (permite comandos complexos)
  - `capture_output=True`: Captura stdout e stderr
  - `text=True`: Retorna strings (não bytes)
  - `cwd=...`: Define diretório de trabalho (onde está o compilador)

**4. Processamento do resultado:**
- `resultado.stdout`: Saída padrão do comando
- `resultado.stderr`: Saída de erro do comando
- `resultado.returncode`: Código de retorno (0 = sucesso, !=0 = erro)
- `if resultado.returncode == 0`: Verifica sucesso
  - Adiciona mensagem de sucesso
  - Atualiza status
- `else`: Se houve erro
  - Adiciona mensagem de erro
  - Atualiza status

**5. Tratamento de exceções:**
- `except Exception as e`: Captura erros de execução
  - Ex: comando não encontrado, permissão negada, etc.

**Por que usar subprocess:**
- Executa compilador como processo separado
- Captura saída sem interferir na interface
- Permite executar qualquer comando shell
- Isola erros (não quebra interface se compilador falhar)

## Relação com as Notas de Aula

### Ambiente Interativo

Conforme as notas de aula (seção 5.5), compiladores modernos são interativos:
> "Com a tendência de uso de computadores pessoais interligados em rede, em substituição ao antigos computadores de grande porte, tem-se que a compilação passou a ser uma tarefa de característica interativa."

A interface gráfica implementa exatamente isso:
- Compilação rápida e visual
- Execução interativa com entrada do usuário
- Feedback imediato de erros e resultados

### Execução da Máquina Virtual

A interface permite executar programas compilados na MVD de forma interativa, facilitando:
- Teste de programas
- Debugging visual
- Entrada interativa durante execução

Isso torna o compilador mais acessível e educativo, permitindo que estudantes vejam o resultado de cada fase de compilação e execução.

