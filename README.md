# Compilador LPD

Compilador para a Linguagem de Programação Didática (LPD).

## Como Usar

### Compilar um programa

```bash
python3 compilador.py programas/programa.txt
```

O arquivo compilado é gerado em: `programas/compilado/programa.obj`

### Executar na Máquina Virtual

```bash
python3 maquina_virtual.py programas/compilado/programa.obj
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
programas/compilado/ # Arquivos compilados (.obj)
```
