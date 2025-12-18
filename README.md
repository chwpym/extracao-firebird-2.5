# 🔥 EXTRATOR FIREBIRD 2.5 PARA EXCEL - Sistema Universal

Sistema completo e modular para extração de dados de **qualquer banco Firebird 2.5** para arquivos Excel (.xlsx), com interface gráfica moderna e recursos avançados.

## ✨ Principais Recursos

- 🖥️ **Interface Gráfica Completa** - Tkinter com design moderno
- 🌍 **Universal** - Funciona com qualquer banco Firebird 2.5
- 📅 **Datas em PT-BR** - Digite datas no formato brasileiro (DD/MM/AAAA) com auto-formatação
- 📊 **Barra de Progresso** - Acompanhe a extração em tempo real
- 🎨 **Temas Personalizáveis** - Escolha o visual que preferir (incluindo Arc)
- 🔍 **Filtros Dinâmicos** - Extraia apenas o período desejado
- 📝 **Logs Automáticos** - Histórico completo de todas as operações
- ⚡ **Multithreading** - Interface não trava durante extrações pesadas

## 📂 Estrutura do Projeto

```
migracao_firebird/
├── core/               # Lógica principal (Banco e Exportador)
│   ├── database.py     # Gerenciamento de conexões
│   └── exporter.py     # Processamento e exportação
├── ui/                 # Interface Gráfica Tkinter
│   └── app.py          # Janela principal
├── utils/              # Utilitários
│   └── logger.py       # Sistema de logs
├── tools/              # Scripts auxiliares de diagnóstico
├── sql/                # Consultas SQL customizáveis
├── output/             # Arquivos Excel gerados
├── logs/               # Histórico de execuções
├── main_gui.py         # 🎯 INICIAR AQUI (Interface Gráfica)
├── exportar.py         # Modo linha de comando (CLI)
├── config.py           # Configurações padrão
└── requirements.txt    # Dependências Python
```

## 🚀 Início Rápido

### 1. Instalação

```bash
# Clone o repositório
git clone git@github.com:chwpym/extracao-firebird-2.5.git
cd extracao-firebird-2.5

# Instale as dependências
pip install -r requirements.txt
```

### 2. Execute a Interface Gráfica

```bash
python main_gui.py
```

### 3. Configure na Interface

Na janela que abrir, você precisa informar:

- **Arquivo .FDB**: Caminho do seu banco Firebird
- **Usuário**: Geralmente `SYSDBA`
- **Senha**: Senha do banco (geralmente `masterkey`)
- **fbclient.dll**: Caminho da biblioteca Firebird (ex: `C:/Program Files/Firebird/fbclient.dll`)
- **Período**: Datas de início e fim no formato DD/MM/AAAA

### 4. Inicie a Extração

Clique em **"INICIAR EXTRAÇÃO TOTAL"** e acompanhe o progresso!

## 🛠️ Requisitos do Sistema

- **Python 3.7+** (64-bit recomendado)
- **Firebird Client** (`fbclient.dll` versão compatível com seu banco)
- **Bibliotecas Python**:
  - `fdb` - Conexão com Firebird
  - `pandas` - Processamento de dados
  - `xlsxwriter` - Geração de Excel
  - `tqdm` - Barras de progresso

## 📖 Modos de Uso

### Interface Gráfica (Recomendado) 🖥️

```bash
python main_gui.py
```

**Recursos da GUI:**
- Seleção visual de arquivos
- Datas com auto-formatação (DD/MM/AAAA)
- Barra de progresso em tempo real
- Log de execução na própria janela
- Temas personalizáveis
- Validação de dados antes da extração

### Linha de Comando (CLI) 💻

```bash
python exportar.py
```

**Quando usar:**
- Automação via scripts
- Agendamento de tarefas
- Servidores sem interface gráfica

## ⚙️ Configuração Avançada

### Arquivo `config.py`

Valores padrão que aparecem na interface:

```python
DB_CONFIG = {
    'dsn': 'localhost:D:/Caminho/Banco.FDB',
    'user': 'SYSDBA',
    'password': 'masterkey',
    'charset': 'WIN1252',
    'fb_library_name': 'fbclient.dll'
}
```

### Customização de Consultas SQL

As consultas SQL estão na pasta `sql/` e podem ser editadas:

- `clientes.sql` - Extração de clientes
- `produtos.sql` - Extração de produtos
- `fornecedores.sql` - Extração de fornecedores
- `entradas_saidas.sql` - Movimentações (Kardex)
- `contas_pagar.sql` - Contas a pagar
- `contas_receber.sql` - Contas a receber

**Placeholders disponíveis:**
- `:DATA_INI` - Data inicial (substituída automaticamente)
- `:DATA_FIM` - Data final (substituída automaticamente)

## 🎨 Temas Disponíveis

Acesse **Menu → Temas** para escolher:
- `clam` (padrão)
- `alt`
- `default`
- `classic`
- `vista` (Windows)
- `xpnative` (Windows XP)
- `arc` (moderno)

## 📊 Dados Extraídos

O sistema extrai as seguintes entidades (se existirem no banco):

1. **Clientes** - Cadastro completo
2. **Produtos** - Catálogo de produtos
3. **Fornecedores** - Cadastro de fornecedores
4. **Entradas/Saídas** - Movimentação de estoque (Kardex)
5. **Contas a Pagar** - Parcelas e histórico
6. **Contas a Receber** - Recebimentos e histórico

## 🔒 Segurança

- ✅ Senhas não são exibidas na interface (campo com `*`)
- ✅ `.gitignore` configurado para não versionar dados sensíveis
- ✅ Logs não contêm senhas
- ✅ Arquivos de saída ficam apenas localmente

## 🐛 Solução de Problemas

### Erro: "No module named 'fdb'"
```bash
pip install fdb
```

### Erro: "fbclient.dll not found"
- Baixe o Firebird Client compatível com seu banco
- Indique o caminho completo na interface

### Erro de conexão
- Verifique se o banco está acessível
- Confirme usuário e senha
- Teste o DSN: `localhost:D:/caminho/banco.fdb`

## 📝 Logs

Todos os logs são salvos em `logs/extracao_AAAAMMDD.log` com:
- Timestamp de cada operação
- Quantidade de registros processados
- Erros detalhados (se houver)

## 🤝 Contribuindo

Este projeto está em desenvolvimento ativo. Sugestões e melhorias são bem-vindas!

## 📄 Licença

Projeto desenvolvido para migração de dados legados Firebird 2.5 para Excel.

---

**Desenvolvido com ❤️ para facilitar migrações de dados Firebird**
