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