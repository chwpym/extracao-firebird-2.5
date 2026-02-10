import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import webbrowser


class HelpWindow:
    def __init__(self, parent, help_type="manual"):
        self.parent = parent
        self.help_type = help_type

        # Criar janela
        self.window = tk.Toplevel(parent)
        self.window.transient(parent)

        if help_type == "manual":
            self.window.title("📖 Manual de Uso")
            self._show_manual()
        elif help_type == "sql_commands":
            self.window.title("💻 Comandos SQL Firebird")
            self._show_sql_commands()

        # Centralizar
        self._center_window(900, 600)

    def _center_window(self, width, height):
        """Centraliza a janela"""
        self.window.update_idletasks()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.window.geometry(f"{width}x{height}+{x}+{y}")

    def _show_manual(self):
        """Mostra o manual de uso"""
        content = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    MANUAL DE USO - EXTRATOR FIREBIRD 2.5                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

📋 ÍNDICE:
  1. Visão Geral
  2. Configuração Inicial
  3. Extração de Dados
  4. Editor SQL
  5. Central de Diagnóstico
  6. Dicas e Truques


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣ VISÃO GERAL

Este sistema permite extrair dados de qualquer banco Firebird 2.5 para arquivos Excel.

Principais recursos:
  ✅ Interface gráfica intuitiva
  ✅ Filtros por período (datas em PT-BR)
  ✅ Editor SQL integrado com biblioteca de queries
  ✅ Teste de queries antes de extrair
  ✅ Barra de progresso em tempo real
  ✅ Logs automáticos de todas as operações

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2️⃣ CONFIGURAÇÃO INICIAL

Antes de extrair dados, configure:

📁 Arquivo .FDB:
   - Clique em "Procurar..." e selecione seu banco de dados
   - Exemplo: D:/DELPHI/bd/SGCADM.FDB

👤 Usuário e Senha:
   - Padrão Firebird: SYSDBA / masterkey
   - Altere se seu banco usar credenciais diferentes

🔧 fbclient.dll:
   - Indique o caminho da biblioteca Firebird
   - Geralmente: C:/Program Files/Firebird/fbclient.dll

📅 Filtros de Período:
   - Digite datas no formato DD/MM/AAAA
   - Auto-formatação: digite 01012024 → vira 01/01/2024
   - Essas datas são usadas nas queries que têm :DATA_INI e :DATA_FIM

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3️⃣ EXTRAÇÃO DE DADOS

Passo a passo:

1. Configure o banco (seção acima)
2. Defina o período desejado
3. Clique em "INICIAR EXTRAÇÃO TOTAL"
4. Acompanhe o progresso na barra e no log
5. Ao finalizar, os arquivos Excel estarão em: output/

Entidades extraídas:
  📋 clientes.xlsx
  📦 produtos.xlsx
  🏭 fornecedores.xlsx
  📊 entradas_saidas.xlsx (Kardex)
  💰 contas_pagar.xlsx
  💵 contas_receber.xlsx (Agora com Número de Pedido e NF)


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4️⃣ EDITOR SQL

Menu: Configurar → Editar Consultas SQL

📚 Biblioteca de Queries:
   - Selecione uma query salva no dropdown
   - Veja a descrição e o SQL
   - Modifique se necessário
   - Teste antes de salvar

🧪 Testar Queries:
   1. Escreva ou selecione uma query
   2. Marque "Mostrar TODOS" se quiser ver todos os registros
   3. Clique em "🧪 Testar Query"
   4. Veja o resultado em uma janela separada

💾 Salvar Queries:
   - "Salvar Como" → Cria nova query com nome personalizado
   - "Salvar Alterações" → Atualiza a query atual
   - "Excluir Query" → Remove da biblioteca

🔍 Placeholders Disponíveis:
   :DATA_INI → Substituído pela data inicial
   :DATA_FIM → Substituído pela data final
   NOME_TABELA → Substitua pelo nome real da tabela

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5️⃣ CENTRAL DE DIAGNÓSTICO

Menu: Ferramentas → Central de Diagnóstico e Testes

Esta central permite rodar ferramentas de validação sem sair do sistema:
  ✅ Investigar Cliente: Detalha documentos de um cliente específico.
  ✅ Teste Rápido: Gera amostras de Excel instantâneas.
  ✅ Scripts de Performance: Testa o tempo de resposta do banco.

Os logs da execução aparecem em tempo real no console preto da janela.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6️⃣ DICAS E TRUQUES


💡 Dica 1: Use a query "Listar Todas as Tabelas" para explorar o banco

💡 Dica 2: Teste queries complexas antes de usar na extração

💡 Dica 3: Marque "Mostrar TODOS" só quando necessário (pode demorar)

💡 Dica 4: Os logs ficam salvos em: logs/extraction_AAAAMMDD.log

💡 Dica 5: Firebird usa sintaxe diferente de MySQL:
   ❌ LIMIT 100        → ✅ SELECT FIRST 100
   ❌ SHOW TABLES      → ✅ SELECT RDB$RELATION_NAME FROM RDB$RELATIONS
   ❌ AUTO_INCREMENT   → ✅ GENERATOR

💡 Dica 6: Temas podem ser alterados em: Menu → Temas
   (Sua escolha é salva automaticamente)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📞 SUPORTE

Para mais informações sobre Firebird SQL:
  Menu → Ajuda → Documentação Online

Desenvolvido para facilitar migrações de dados Firebird 2.5 para Excel.
"""

        text_widget = ScrolledText(self.window, wrap=tk.WORD, font=("Consolas", 9))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert("1.0", content)
        text_widget.config(state="disabled")

        ttk.Button(self.window, text="Fechar", command=self.window.destroy).pack(
            pady=10
        )

    def _show_sql_commands(self):
        """Mostra referência de comandos SQL Firebird"""
        content = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    COMANDOS SQL FIREBIRD - REFERÊNCIA RÁPIDA                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

📋 CONSULTAS BÁSICAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Selecionar todos os registros:
  SELECT * FROM nome_tabela

Selecionar colunas específicas:
  SELECT coluna1, coluna2, coluna3 FROM nome_tabela

Limitar resultados (primeiros N registros):
  SELECT FIRST 100 * FROM nome_tabela

Pular registros e limitar:
  SELECT FIRST 100 SKIP 50 * FROM nome_tabela

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 FILTROS E CONDIÇÕES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Filtro simples:
  SELECT * FROM clientes WHERE cidade = 'São Paulo'

Múltiplas condições (AND):
  SELECT * FROM produtos WHERE preco > 100 AND estoque > 0

Múltiplas condições (OR):
  SELECT * FROM clientes WHERE cidade = 'SP' OR cidade = 'RJ'

Filtro por intervalo de datas:
  SELECT * FROM pedidos 
  WHERE data_pedido BETWEEN '2024-01-01' AND '2024-12-31'

Busca parcial (LIKE):
  SELECT * FROM produtos WHERE descricao LIKE '%motor%'

Valores nulos:
  SELECT * FROM clientes WHERE email IS NULL
  SELECT * FROM clientes WHERE email IS NOT NULL

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔗 JOINS (RELACIONAMENTOS)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INNER JOIN (apenas registros que combinam):
  SELECT p.*, c.nome AS cliente_nome
  FROM pedidos p
  JOIN clientes c ON p.cliente_id = c.id

LEFT JOIN (todos da esquerda + combinações):
  SELECT p.*, c.nome AS cliente_nome
  FROM pedidos p
  LEFT JOIN clientes c ON p.cliente_id = c.id

Múltiplos JOINs:
  SELECT p.*, c.nome, prod.descricao
  FROM pedidos p
  JOIN clientes c ON p.cliente_id = c.id
  JOIN produtos prod ON p.produto_id = prod.id

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 AGREGAÇÕES E AGRUPAMENTOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Contar registros:
  SELECT COUNT(*) FROM clientes

Somar valores:
  SELECT SUM(valor_total) FROM pedidos

Média:
  SELECT AVG(preco) FROM produtos

Máximo e Mínimo:
  SELECT MAX(preco), MIN(preco) FROM produtos

Agrupar por categoria:
  SELECT categoria, COUNT(*) AS total
  FROM produtos
  GROUP BY categoria

Agrupar com filtro (HAVING):
  SELECT cidade, COUNT(*) AS total_clientes
  FROM clientes
  GROUP BY cidade
  HAVING COUNT(*) > 10

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔤 ORDENAÇÃO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Ordem crescente:
  SELECT * FROM produtos ORDER BY preco ASC

Ordem decrescente:
  SELECT * FROM produtos ORDER BY preco DESC

Múltiplas colunas:
  SELECT * FROM clientes ORDER BY cidade ASC, nome ASC

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🛠️ FUNÇÕES ÚTEIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Concatenar strings:
  SELECT nome || ' ' || sobrenome AS nome_completo FROM clientes

Converter para maiúsculas/minúsculas:
  SELECT UPPER(nome), LOWER(email) FROM clientes

Extrair parte de data:
  SELECT EXTRACT(YEAR FROM data_pedido) AS ano FROM pedidos
  SELECT EXTRACT(MONTH FROM data_pedido) AS mes FROM pedidos

Substituir NULL por valor:
  SELECT COALESCE(telefone, 'Não informado') FROM clientes

Converter tipos:
  SELECT CAST(preco AS VARCHAR(20)) FROM produtos

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 METADADOS DO BANCO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Listar todas as tabelas:
  SELECT RDB$RELATION_NAME AS TABELA
  FROM RDB$RELATIONS
  WHERE RDB$SYSTEM_FLAG = 0
  ORDER BY RDB$RELATION_NAME

Ver colunas de uma tabela:
  SELECT RDB$FIELD_NAME AS COLUNA
  FROM RDB$RELATION_FIELDS
  WHERE RDB$RELATION_NAME = 'NOME_TABELA'
  ORDER BY RDB$FIELD_POSITION

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ DIFERENÇAS IMPORTANTES: FIREBIRD vs MySQL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MySQL                    →  Firebird
─────────────────────────────────────────────────────────
LIMIT 100                →  SELECT FIRST 100
SHOW TABLES              →  SELECT ... FROM RDB$RELATIONS
AUTO_INCREMENT           →  GENERATOR / SEQUENCE
NOW()                    →  CURRENT_TIMESTAMP
CONCAT(a, b)             →  a || b
IFNULL(x, y)             →  COALESCE(x, y)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Use o Editor SQL para testar suas queries antes de executar!
"""

        text_widget = ScrolledText(self.window, wrap=tk.WORD, font=("Consolas", 9))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert("1.0", content)
        text_widget.config(state="disabled")

        ttk.Button(self.window, text="Fechar", command=self.window.destroy).pack(
            pady=10
        )


def open_documentation():
    """Abre links de documentação no navegador"""
    links = [
        ("Firebird RDBMS (PT-BR)", "https://www.firebirdsql.org/pt/firebird-rdbms"),
        ("Firebird Development (PT-BR)", "https://www.firebirdsql.org/pt/development"),
        ("Python FDB Documentation", "https://fdb.readthedocs.io/"),
    ]

    msg = "Escolha qual documentação abrir:\n\n"
    for i, (name, url) in enumerate(links, 1):
        msg += f"{i}. {name}\n"

    # Criar janela de seleção
    root = tk.Tk()
    root.withdraw()

    choice_window = tk.Toplevel()
    choice_window.title("📚 Documentação Online")
    choice_window.geometry("400x250")

    ttk.Label(
        choice_window,
        text="Escolha qual documentação abrir:",
        font=("Arial", 10, "bold"),
    ).pack(pady=10)

    for name, url in links:
        ttk.Button(
            choice_window,
            text=f"🌐 {name}",
            command=lambda u=url: [webbrowser.open(u), choice_window.destroy()],
        ).pack(pady=5, padx=20, fill=tk.X)

    ttk.Button(choice_window, text="Cancelar", command=choice_window.destroy).pack(
        pady=10
    )

    # Centralizar
    choice_window.update_idletasks()
    width = 400
    height = 250
    screen_width = choice_window.winfo_screenwidth()
    screen_height = choice_window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    choice_window.geometry(f"{width}x{height}+{x}+{y}")
