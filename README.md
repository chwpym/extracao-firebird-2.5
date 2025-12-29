# 🔥 EXTRATOR FIREBIRD 2.5 PARA EXCEL - Sistema Universal

Sistema completo e modular para extração de dados de **qualquer banco Firebird 2.5** para arquivos Excel (.xlsx), com interface gráfica moderna e recursos avançados.

## ✨ Principais Recursos

- 🖥️ **Interface Gráfica Completa** - Tkinter com design moderno e centralizado
- 🌍 **Universal** - Funciona com qualquer banco Firebird 2.5
- 📅 **Datas em PT-BR** - Digite datas no formato brasileiro (DD/MM/AAAA) com auto-formatação
- 📊 **Barra de Progresso** - Acompanhe a extração em tempo real
- 🎨 **Temas Personalizáveis** - Escolha o visual que preferir (salvos automaticamente)
- 🔍 **Filtros Dinâmicos** - Extraia apenas o período desejado
- 📝 **Editor SQL Integrado** - Biblioteca com 12+ queries úteis + editor livre
- 🧪 **Teste de Queries** - Valide SQL antes de extrair
- 📖 **Sistema de Ajuda** - Manual completo + referência SQL Firebird
- 📝 **Logs Automáticos** - Histórico completo de todas as operações
- ⚡ **Multithreading** - Interface não trava durante extrações pesadas

## 📂 Estrutura do Projeto

```
migracao_firebird/
├── core/               # Lógica principal (Banco e Exportador)
│   ├── database.py     # Gerenciamento de conexões
│   └── exporter.py     # Processamento e exportação
├── ui/                 # Interface Gráfica Tkinter
│   ├── app.py          # Janela principal
│   ├── sql_editor.py   # Editor SQL com biblioteca de queries
│   └── help_window.py  # Sistema de ajuda
├── utils/              # Utilitários
│   ├── logger.py       # Sistema de logs
│   └── preferences.py  # Gerenciamento de preferências (temas)
├── tools/              # Scripts auxiliares de diagnóstico
├── sql/                # Consultas SQL customizáveis
│   └── query_library.json  # Biblioteca de queries salvas
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


## 📖 Recursos Avançados

### 🔍 Consulta de Produtos (Novo!)

**Menu: Consultar → Produtos**

Interface completa para consulta e análise de produtos com recursos avançados:

#### 🎯 Funcionalidades Principais

**Busca Inteligente:**
- ✅ Busca multi-palavra com lógica AND (ex: "COXIM CORSA" busca produtos que contenham AMBOS os termos)
- ✅ Busca por código, descrição ou aplicação
- ✅ Busca vazia com confirmação para listar todos os produtos
- ✅ Seleção automática do primeiro resultado

**Filtros Avançados:**
- 📊 **Filtros de Estoque:**
  - Positivo (≥1)
  - Zerado (=0)
  - Negativo (<0)
- 🎯 **Filtros Especiais:**
  - Apenas Ativos
  - Abaixo do Mínimo (produtos que precisam reposição)
  - Sem Preço (produtos sem preço cadastrado)
  - Sem Aplicação (produtos sem aplicação cadastrada)
- 🔤 **Filtro de Texto:** Busca rápida na lista por código, descrição ou marca
- 🔄 **Botão "Mostrar Todos":** Reseta todos os filtros para o padrão

**Tabela de Produtos:**
- 📋 **10 Colunas Informativas:**
  - Código do Produto
  - Código Fabricante
  - Descrição
  - Estoque
  - Valor de Venda
  - Localização
  - Última Compra
  - Código Original
  - Código de Barras
  - Marca
- ⬆️⬇️ **Ordenação por Coluna:** Clique no cabeçalho para ordenar (indicador visual ▲▼)
- 📏 **Scroll Horizontal:** Visualize todas as colunas confortavelmente

**Detalhes do Produto:**
- 🖼️ **Imagem do Produto:**
  - Miniatura fixa (150x150px) que não quebra o layout
  - Clique para ampliar em janela popup (até 800x600px)
  - Fecha com clique ou tecla ESC
- 📝 **Aplicação:** Campo de texto com aplicações do produto
- 🔗 **Produtos Similares:**
  - Lista automática de produtos com mesma referência
  - Exibe: Código, Cód. Fab., Descrição, Estoque, Preço, Marca
  - Duplo clique para carregar similar na tela principal

**Histórico de Compras:**
- 📊 Últimas compras do produto selecionado
- 💰 Preço médio calculado automaticamente
- 📅 Data, Fornecedor, Quantidade, Preço Unitário e Nota Fiscal
- 🔢 Seletor de quantidade (5, 10, 20 ou Todas)

#### 🖥️ Interface

- 🖼️ **Tela Cheia:** Janela maximizada para melhor aproveitamento do espaço
- 📐 **Layout Horizontal:** Imagem | Aplicação | Similares (lado a lado)
- 🎨 **Visual Moderno:** Cores e indicadores visuais para facilitar a leitura
- ⚡ **Conexão Persistente:** Mantém conexão com banco durante toda a sessão

#### 💡 Dicas de Uso

1. **Busca Rápida:** Digite parte do código ou descrição e pressione Enter
2. **Filtros Combinados:** Use múltiplos filtros simultaneamente para refinar resultados
3. **Produtos para Comprar:** Marque "Abaixo do Mínimo" para ver o que precisa repor
4. **Completar Cadastro:** Use "Sem Preço" ou "Sem Aplicação" para encontrar produtos incompletos
5. **Similares:** Veja rapidamente produtos equivalentes de outras marcas
6. **Ordenação:** Ordene por estoque para ver produtos zerados ou por preço para análise

### 📝 Editor SQL Integrado

**Menu: Configurar → Editar Consultas SQL**

O editor SQL possui:

- **Biblioteca com 12+ queries úteis**:
  - 📋 Listar Todas as Tabelas
  - 🔍 Ver Estrutura de Tabela
  - 📊 Contar Registros
  - 👥 Extração: Clientes
  - 📦 Extração: Produtos
  - 🏭 Extração: Fornecedores
  - 📊 Movimentações: Kardex Completo
  - 💰 Financeiro: Contas a Pagar
  - 💵 Financeiro: Contas a Receber
  - 🔎 Explorar: Primeiros 100 Registros
  - 📈 Análise: Produtos Mais Vendidos
  - 👤 Análise: Melhores Clientes

- **Recursos do Editor**:
  - ✅ Dropdown para selecionar queries salvas
  - ✅ Descrição detalhada de cada query
  - ✅ Editor de texto livre para SQL customizado
  - ✅ Teste de queries com preview dos resultados
  - ✅ Checkbox "Mostrar TODOS" para ver todos os registros
  - ✅ Salvar queries personalizadas
  - ✅ Excluir queries que não precisa

### 🧪 Teste de Queries

Antes de executar uma extração:

1. Escreva ou selecione uma query
2. Marque "📊 Mostrar TODOS" se quiser ver todos os registros (opcional)
3. Clique em "🧪 Testar Query"
4. Veja o resultado em uma janela com:
   - Número de registros retornados
   - Lista de colunas
   - Preview dos dados (primeiras 10 linhas ou todos)

### 📚 Sistema de Ajuda

**Menu: Ajuda**

- **📖 Manual de Uso**: Guia completo do sistema
- **💻 Comandos SQL Firebird**: Referência rápida de sintaxe
- **🌐 Documentação Online**: Links para docs oficiais em PT-BR

### 🎨 Temas Personalizáveis

**Menu: Temas**

Escolha entre os temas disponíveis:
- `winnative` - Visual nativo do Windows (recomendado)
- `clam` - Estilo moderno e limpo
- `alt` - Alternativo
- `default` - Padrão do Tkinter
- `classic` - Estilo clássico

**Sua escolha é salva automaticamente!**

## 📊 Dados Extraídos

O sistema extrai as seguintes entidades (se existirem no banco):

1. **Clientes** - Cadastro completo
2. **Produtos** - Catálogo de produtos
3. **Fornecedores** - Cadastro de fornecedores
4. **Entradas/Saídas** - Movimentação de estoque (Kardex)
5. **Contas a Pagar** - Parcelas e histórico
6. **Contas a Receber** - Recebimentos e histórico

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

As consultas SQL estão na pasta `sql/` e podem ser editadas pelo **Editor SQL** ou manualmente:

- `clientes.sql` - Extração de clientes
- `produtos.sql` - Extração de produtos
- `fornecedores.sql` - Extração de fornecedores
- `entradas_saidas.sql` - Movimentações (Kardex)
- `contas_pagar.sql` - Contas a pagar
- `contas_receber.sql` - Contas a receber

**Placeholders disponíveis:**
- `:DATA_INI` - Data inicial (substituída automaticamente)
- `:DATA_FIM` - Data final (substituída automaticamente)

## 💡 Dicas de Uso

1. **Explore o banco primeiro**: Use a query "Listar Todas as Tabelas" para ver o que existe
2. **Teste antes de extrair**: Sempre teste queries complexas no editor SQL
3. **Use o checkbox "Mostrar TODOS" com cuidado**: Pode demorar em tabelas grandes
4. **Consulte o manual**: Menu → Ajuda → Manual de Uso
5. **Aprenda SQL Firebird**: Menu → Ajuda → Comandos SQL Firebird

### 🔍 Diferenças Firebird vs MySQL

| MySQL | Firebird |
|-------|----------|
| `LIMIT 100` | `SELECT FIRST 100` |
| `SHOW TABLES` | `SELECT ... FROM RDB$RELATIONS` |
| `AUTO_INCREMENT` | `GENERATOR / SEQUENCE` |
| `NOW()` | `CURRENT_TIMESTAMP` |
| `CONCAT(a, b)` | `a \|\| b` |

## 🔒 Segurança

- ✅ Senhas não são exibidas na interface (campo com `*`)
- ✅ `.gitignore` configurado para não versionar dados sensíveis
- ✅ Logs não contêm senhas
- ✅ Arquivos de saída ficam apenas localmente
- ✅ Preferências do usuário (temas) não são versionadas

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

### Janelas não aparecem centralizadas
- Isso pode acontecer em monitores com DPI alto
- As janelas ainda funcionam normalmente

## 📝 Logs

Todos os logs são salvos em `logs/extracao_AAAAMMDD.log` com:
- Timestamp de cada operação
- Quantidade de registros processados
- Erros detalhados (se houver)

## 🤝 Contribuindo

Este projeto está em desenvolvimento ativo. Sugestões e melhorias são bem-vindas!

## 📄 Licença

Projeto desenvolvido para facilitar migrações de dados legados Firebird 2.5 para Excel.

---

**Desenvolvido com ❤️ para facilitar migrações de dados Firebird**
