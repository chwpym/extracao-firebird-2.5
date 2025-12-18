# EXTRATOR FIREBIRD 2.5 PARA EXCEL

Este projeto foi desenvolvido para automatizar a extração de dados históricos de um banco de dados Firebird 2.5 (utilizado originalmente em sistemas Delphi 7) e exportá-los para arquivos Excel (.xlsx) organizados por categorias.

## 🚀 Funcionalidades

- **Extração Unificada (Kardex):** Relatório consolidado de Entradas (ENTITENS) e Saídas (PEDITENS), incluindo descrições de produtos, nomes de clientes/fornecedores e datas reais de entrada.
- **Financeiro Detalhado:** Extração de todas as parcelas de Contas a Pagar (PAGDET) e Contas a Receber (RECDET) com vínculo aos nomes das entidades.
- **Cadastros Básicos:** Exportação completa de Clientes, Produtos e Fornecedores.
- **Performance Otimizada:** Consultas SQL utilizando JOINS para lidar com grandes volumes de dados (testado com +300 mil registros).
- **Gestão de Dependências:** Configuração automática para bibliotecas legadas (`fbclient.dll`).

## 🛠️ Requisitos

- Python 3.x (64-bit recomendado)
- Firebird Client (`fbclient.dll` versão 64-bit deve estar na pasta raiz)
- Bibliotecas Python: `fdb`, `pandas`, `xlsxwriter`

## 📦 Instalação

1. Clone o repositório:
   ```bash
   git clone git@github.com:chwpym/extracao-firebird-2.5.git
   cd extracao-firebird-2.5
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuração

Edite o arquivo `config.py` para apontar para o seu arquivo de banco de dados (.FDB):

```python
DB_CONFIG = {
    'dsn': 'localhost:D:/Caminho/Seu/Banco/SGCADM.FDB',
    'user': 'SYSDBA',
    'password': 'masterkey',
    'charset': 'WIN1252',
    'fb_library_name': 'fbclient.dll'
}
```

## 📖 Como Usar

Para iniciar a extração completa:

```bash
python exportar.py
```

Os arquivos serão gerados na subpasta `output/`.

## 💡 Próximas Melhorias (Sugestões)

- **Interface Gráfica (Tkinter):** Criar uma janela para seleção do arquivo .FDB e botão de "Iniciar Extração".
- **Barras de Progresso:** Implementar `tqdm` para acompanhar a evolução de cada tabela no terminal.
- **Logs Automatizados:** Gravar erros e estatísticas em um arquivo `.log`.
- **Filtros Dinâmicos:** Adicionar uma interface para escolher o período (datas) antes da extração.

---
Desenvolvido como ferramenta de migração de dados legados.
