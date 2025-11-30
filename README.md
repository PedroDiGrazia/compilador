# Compilador LPD

Compilador para a Linguagem de Programação Didática (LPD).

## Como Usar

### Compilar um programa

```bash
python3 compilador.py programas/programa.txt
```

O arquivo compilado `.obj` é gerado na mesma pasta do compilador.

### Executar na Máquina Virtual

```bash
python3 maquina_virtual.py programa.obj
```

### Interface Gráfica

```bash
python3 interface.py
```

## Opções do Compilador

| Opção         | Descrição                              |
| ------------- | -------------------------------------- |
| `--lexico`    | Apenas análise léxica                  |
| `--sintatico` | Análise léxica + sintática             |
| `--semantico` | Análise léxica + sintática + semântica |
| `--ajuda`     | Mostra ajuda                           |

## Estrutura de Pastas

```
programas/           # Arquivos fonte (.txt)
```

## Executáveis (Windows)

### Gerar executáveis

```bash
python criar_executaveis.py
```

Os executáveis são gerados na pasta `dist/`.

### Usar os executáveis

**Interface Gráfica** (recomendado):

- Duplo clique em `interface.exe`

**Linha de comando**:

```cmd
compilador.exe programa.txt
maquina_virtual.exe programa.obj
```

### Estrutura para distribuição

```
minha_pasta/
├── compilador.exe
├── maquina_virtual.exe
├── interface.exe
├── programa.txt      # arquivo fonte
└── programa.obj      # gerado após compilar
```
