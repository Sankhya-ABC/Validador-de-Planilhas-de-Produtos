# Validador-de-Planilhas-de-Produtos
Este é um aplicativo desktop desenvolvido em Python para validar planilhas de produtos de acordo com regras específicas. O sistema verifica cada linha do arquivo de entrada (Excel ou CSV), aplica regras de validação e gera dois arquivos de saída: um com os produtos válidos e outro com os produtos inválidos (incluindo mensagens de erro detalhadas).

## Funcionalidades Principais
- Validação de planilhas de produtos (Excel ou CSV)
- Interface gráfica amigável com logo animado
- Barra de progresso em tempo real
- Botão de cancelamento durante a execução
- Geração de relatórios de validação
- Forçamento automático do campo USO_PROD para "R"
- Validação de hierarquia de grupos
- Verificação de campos obrigatórios e formatos específicos

## Requisitos do Sistema
- Python 3.8 ou superior
- Bibliotecas Python:
```python
pip install pandas, tkinter, pillow, openpyxl
```

## Como Usar
### Execução do Programa
1. Clone o repositório ou faça download dos arquivos
2. Execute o arquivo principal:
```python
python validador_com_interface.py
```
### Interface Gráfica
1. Seleção de Arquivo:
    - Clique em "Procurar" para selecionar um arquivo Excel ou CSV
    - O caminho do arquivo aparecerá no campo de texto
2. Validação:
    - Clique em "Executar Validação" para iniciar o processo
    - A barra de progresso mostrará o andamento
    - O contador exibirá linhas processadas e inválidas
3. Cancelamento:
    - Clique em "Parar" para interromper a validação a qualquer momento
4. Resultados:
    - Após a conclusão, uma mensagem mostrará estatísticas
    - Os arquivos de saída serão salvos na pasta `saida/`:
        - `produtos_validos.xlsx`: Produtos sem erros
        - `produtos_invalidos.xlsx`: Produtos com erros e mensagens de validação
### Preparação da Planilha
A planilha de entrada deve conter as seguintes colunas (pelo menos as obrigatórias):
| Coluna | Obrigatório | Tipo | Tamanho | Opções Permitidas |
|-----------------------|-------------|-------------|:---------:|---------------------------------|
| GRUPO_PAI             | SIM         | Alfanumérico| 30      | -                               |
| GRUPO_FILHO           | NÃO         | Alfanumérico| 30      | -                               |
| GRUPO_NETO            | NÃO         | Alfanumérico| 30      | -                               |
| GRUPO_BISNETO         | NÃO         | Alfanumérico| 30      | -                               |
| COD_SIST_ANTERIOR     | NÃO         | Alfanumérico| -       | -                               |
| DESCR_PROD            | SIM         | Alfanumérico| 100     | -                               |
| COMPLEMENTO           | NÃO         | Alfanumérico| 100     | -                               |
| USO_PROD              | SIM         | Alfanumérico| 1       | 1,2,4,B,C,D,E,F,I,M,O,P,R,T,V   |
| UNIDADE               | SIM         | Alfanumérico| 2       | CX,DZ,GR,HR,KG,KW,LT,ML,MT,PC,PT,TN,UN |
| COD_BARRAS            | NÃO         | Alfanumérico| 15      | -                               |
| NCM                   | SIM         | Numérico    | 8       | -                               |
| MARCA                 | NÃO         | Alfanumérico| 20      | -                               |
| REF_FORN              | NÃO         | Alfanumérico| 30      | -                               |
| IDENTIF_IMOBILIZADO   | NÃO         | Numérico    | 2       | 1,2,3,4,5,6,99                  |
| UTILIZ_IMOBILIZADO    | NÃO         | Numérico    | 1       | 1,2,3,9                         |

## Descrição dos Arquivos
### validador_com_interface.py
Arquivo principal que contém a interface gráfica e a lógica de controle

**Principais componentes**:
- `ValidadorApp`: Classe principal da aplicação
    - `__init__`: Inicializa a interface
    - `_build_widgets`: Constrói os elementos da interface
    - `_load_gif_logo`: Carrega e anima o logo
    - `_run_validation`: Lógica principal de validação
    - `_start_validation`: Inicia a validação em thread separada

**Fluxo de validação**:
1. Seleção do arquivo de entrada
2. Leitura do arquivo (Excel/CSV)
3. Padronização de nomes de colunas
4. Preenchimento de colunas faltantes
5. Forçamento de USO_PROD para "R"
6. Validação linha por linha
7. Geração de arquivos de saída
8. Exibição de estatísticas

### regra_validacao_produtos.py
Contém as regras de validação e funções auxiliares.

**Componentes principais**:
- `OPCOES_USO_PROD`: Valores permitidos para USO_PROD
- `OPCOES_UNIDADE`: Valores permitidos para UNIDADE
- `REGRAS_PRODUTO`: Dicionário com todas as regras de validação
- `limpar_valor`: Função para limpeza de valores
- `is_vazio`: Verifica se um valor está vazio
- `validar_campo_basico`: Valida um campo individual
- `validar_linha_produto`: Valida uma linha completa

**Regras especiais**:
1. Hierarquia de grupos:
    - Se GRUPO_NETO preenchido → GRUPO_FILHO obrigatório
    - Se GRUPO_BISNETO preenchido → GRUPO_NETO obrigatório
2. Campos condicionais:
    - Se USO_PROD = 'I':
        - IDENTIF_IMOBILIZADO obrigatório
        - UTILIZ_IMOBILIZADO obrigatório
    - Caso contrário:
        - IDENTIF_IMOBILIZADO deve ser vazio
        - UTILIZ-IMOBILIZADO deve ser vazio

### utils.py
Funções utilitárias para tratamento de texto.

**Funções**:
- `limpar_para_contagem`:
    - Normaliza texto para NFC
    - Remove caracteres de controle
    - Reduz espaços múltiplos
    - Remove espaços no início/fim

## Regras de Validação Detalhadas
### Campos Alfanuméricos
1. Remoção de espaços extras
2. Verificação de tamanho máximo (após limpeza)
3. Para campos obrigatórios: não pode ser vazio
### Campos Numéricos
1. Remoção de pontuação (., -) e espaços
2. Verificação se contém apenas dígitos
3. Verificação de tamanho máximo
4. Para campos obrigatórios: não pode ser vazio
### Campos com Opções
1. Verificação se valor está na lista permitida
2. Valores são comparados após limpeza
### Validação Especial do NCM
1. Deve ter exatamente 8 dígitos
2. Não pode conter caracteres não numéricos

## Fluxo de Trabalho Recomendado
1. Prepare sua planilha com as colunas necessárias
2. Execute o validador
3. Analise o arquivo `produtos_invalidos.xlsx`
4. Corrija os erros indicados na coluna "OBS_Validação"
5. Repita o processo até não haver mais erros
6. Use o arquivo `produtos_validos.xlsx` em seus sistemas

## Notas Importantes
1. O campo USO_PROD é sempre forçado para "R" independente do valor original
2. Colunas faltantes são automaticamente criadas com valores vazio
3. Nomes de colunas são convertidos para maiúsculas e sem espaços extras
4. O logo animado requer o arquivo `futuro_animado.gif` no mesmo diretório
5. Arquivos de saída são sobrescritos a cda execução

## Limitações Conhecidas
1. Arquivos muitos grandes (>100.000 linhas) podem ter desempenho reduzido
2. Não suporta arquivos Excel com múltiplas planilhas
3. Validação de CEP não está implementada neste módulo

## Exemplo de Saída
produtos_invalidos.xlsx:
| GRUPO_PAI | DESCR_PROD | ... | OBS_Validação |
| --------- | ---------- | :---: | ------------- |
| Eletrônicos | Monitor 4K | ... | NCM: deve conter apenas dígitos; UNIDADE: 'CX2' não está entre opções permitidas |
| Móveis    | Cadeira Gamer | ... | DESCR_PROD: Tamanho excede máximo de 100 (encontrado 120) |

