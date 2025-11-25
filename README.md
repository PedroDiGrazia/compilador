# Compilador LPD

Compilador para a Linguagem de Programação Didática (LPD).

## Como Usar

### Compilar um programa

```bash
python3 compilador.py programa.txt -s programa.obj
```

### Executar na Máquina Virtual

```bash
python3 maquina_virtual.py programa.obj
```

### Interface Gráfica

```bash
python3 interface.py
```

## Opções do Compilador

| Opção          | Descrição                              |
| -------------- | -------------------------------------- |
| `--lexico`     | Apenas análise léxica                  |
| `--sintatico`  | Análise léxica + sintática             |
| `--semantico`  | Análise léxica + sintática + semântica |
| `-s <arquivo>` | Especifica arquivo de saída            |
| `--ajuda`      | Mostra ajuda                           |

## Estrutura de Pastas

```
programas/           # Arquivos fonte (.txt)
programas/compilado/ # Arquivos compilados (.obj)
```
