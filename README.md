# EXTRATOR FIREBIRD 2.5 PARA EXCEL (Modular)

Versão aprimorada e modularizada do extrator de dados Firebird 2.5 para Excel, agora com suporte a Interface Gráfica (GUI), Logs e Barras de Progresso.

## 📂 Estrutura do Projeto

```
migracao_firebird/
├── core/               # Lógica principal (Banco e Exportador)
├── ui/                 # Telas e Interface Tkinter
├── utils/              # Loggers e formatadores
├── tools/              # Scripts de diagnóstico e inspeção (Checkers)
├── sql/                # Consultas SQL por entidade
├── output/             # Arquivos Excel gerados (.xlsx)
├── logs/               # Histórico detalhado de execuções (.log)
├── main_gui.py         # App com Interface Gráfica (RECOMENDADO)
├── exportar.py         # App via Linha de Comando (CLI)
├── config.py           # Configurações do Banco
└── requirements.txt    # Dependências (incluindo tqdm)
```

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
    'dsn': 'localhost:D:/Caminho/Seu/Banco/NomeBanco.FDB',
    'user': 'Nome User',
    'password': 'Senha',
    'charset': 'WIN1252',
    'fb_library_name': 'fbclient.dll'
}
```

## 🚀 Como Usar (Interface Gráfica)

O modo recomendado é utilizar a Interface Gráfica:

```bash
python main_gui.py
```
Nesta tela, você poderá selecionar o arquivo `.FDB`, definir o período de extração e acompanhar os logs em tempo real.

## 💻 Como Usar (Linha de Comando)

Para rodar via terminal com barra de progresso:

```bash
python exportar.py
```

## ⚙️ Configuração Local

O arquivo `config.py` vem configurado para buscar o banco em `D:/DELPHI/bd/SGCADM.FDB`. O arquivo `.gitignore` protege suas configurações locais para que não sejam enviadas por engano para o GitHub.

## 💡 Melhorias Implementadas

- **Arquitetura Modular:** Separação completa de interface, lógica e utilitários.
- **Multithreading:** A interface gráfica não trava durante a extração pesada.
- **Logs em Arquivo:** Todo erro ou aviso é salvo automaticamente na pasta `logs/`.
- **Organização:** Scripts de teste e inspeção foram movidos para a pasta `tools/`.

---
Projeto desenvolvido para migração de dados legados Firebird para o formato Excel.
