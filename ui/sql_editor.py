import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText
import os
import json

class SQLEditorWindow:
    def __init__(self, parent, sql_dir):
        self.parent = parent
        self.sql_dir = sql_dir
        self.queries_file = os.path.join(sql_dir, 'query_library.json')
        self.current_query_name = None
        
        # Carregar biblioteca de queries
        self.query_library = self._load_query_library()
        
        # Criar janela
        self.window = tk.Toplevel(parent)
        self.window.title("Editor SQL - Biblioteca de Queries")
        self.window.geometry("1000x700")
        
        # Manter janela sempre visível e em foco
        self.window.transient(parent)
        self.window.grab_set()
        self.window.focus_force()
        
        self._create_widgets()
        
    def _load_query_library(self):
        """Carrega ou cria a biblioteca de queries"""
        if os.path.exists(self.queries_file):
            try:
                with open(self.queries_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        # Biblioteca padrão com queries úteis
        return {
            "📋 Listar Todas as Tabelas": {
                "description": "Lista todas as tabelas do banco de dados",
                "sql": "SELECT RDB$RELATION_NAME AS TABELA\nFROM RDB$RELATIONS\nWHERE RDB$SYSTEM_FLAG = 0\nORDER BY RDB$RELATION_NAME"
            },
            "🔍 Ver Estrutura de Tabela": {
                "description": "Mostra colunas de uma tabela específica (substitua NOME_TABELA)",
                "sql": "SELECT\n    RF.RDB$FIELD_NAME AS COLUNA,\n    CASE F.RDB$FIELD_TYPE\n        WHEN 7 THEN 'SMALLINT'\n        WHEN 8 THEN 'INTEGER'\n        WHEN 10 THEN 'FLOAT'\n        WHEN 12 THEN 'DATE'\n        WHEN 13 THEN 'TIME'\n        WHEN 14 THEN 'CHAR'\n        WHEN 16 THEN 'BIGINT'\n        WHEN 27 THEN 'DOUBLE'\n        WHEN 35 THEN 'TIMESTAMP'\n        WHEN 37 THEN 'VARCHAR'\n        WHEN 261 THEN 'BLOB'\n        ELSE 'UNKNOWN'\n    END AS TIPO,\n    F.RDB$FIELD_LENGTH AS TAMANHO,\n    RF.RDB$NULL_FLAG AS OBRIGATORIO\nFROM RDB$RELATION_FIELDS RF\nJOIN RDB$FIELDS F ON RF.RDB$FIELD_SOURCE = F.RDB$FIELD_NAME\nWHERE RF.RDB$RELATION_NAME = 'NOME_TABELA'\nORDER BY RF.RDB$FIELD_POSITION"
            },
            "📊 Contar Registros de Todas as Tabelas": {
                "description": "Conta quantos registros existem em cada tabela",
                "sql": "-- Esta query precisa ser executada manualmente para cada tabela\n-- Exemplo:\nSELECT 'CLIENTE' AS TABELA, COUNT(*) AS REGISTROS FROM CLIENTE\nUNION ALL\nSELECT 'PRODUTO', COUNT(*) FROM PRODUTO\nUNION ALL\nSELECT 'FORNECEDOR', COUNT(*) FROM FORNECEDOR"
            },
            "👥 Extração: Clientes": {
                "description": "Extrai todos os clientes cadastrados",
                "sql": "SELECT\n    CLI_CODIGO,\n    CLI_NOME,\n    CLI_ENDERECO,\n    CLI_BAIRRO,\n    CLI_CIDADE,\n    CLI_UF,\n    CLI_CEP,\n    CLI_TELEFONE,\n    CLI_CELULAR,\n    CLI_EMAIL,\n    CLI_CPF_CNPJ,\n    CLI_RG_IE,\n    CLI_DATACADASTRO\nFROM CLIENTE\nORDER BY CLI_NOME"
            },
            "📦 Extração: Produtos": {
                "description": "Extrai todos os produtos cadastrados",
                "sql": "SELECT\n    PROD_CODIGO,\n    PROD_DESCRICAOPRODUTO,\n    PROD_UNIDADE,\n    PROD_PRECOCUSTO,\n    PROD_PRECOVENDA,\n    PROD_ESTOQUEATUAL,\n    PROD_ESTOQUEMINIMO,\n    PROD_CODIGOBARRA,\n    PROD_ATIVO\nFROM PRODUTO\nORDER BY PROD_DESCRICAOPRODUTO"
            },
            "🏭 Extração: Fornecedores": {
                "description": "Extrai todos os fornecedores cadastrados",
                "sql": "SELECT\n    FOR_CODIGO,\n    FOR_NOME,\n    FOR_ENDERECO,\n    FOR_BAIRRO,\n    FOR_CIDADE,\n    FOR_UF,\n    FOR_CEP,\n    FOR_TELEFONE,\n    FOR_EMAIL,\n    FOR_CNPJ,\n    FOR_IE\nFROM FORNECEDOR\nORDER BY FOR_NOME"
            },
            "📊 Movimentações: Kardex Completo": {
                "description": "Relatório unificado de entradas e saídas (use :DATA_INI e :DATA_FIM)",
                "sql": "SELECT\n    mov.PROD_CODIGO AS \"COD_PRODUTO\",\n    prod.PROD_DESCRICAOPRODUTO AS \"DESCRICAO\",\n    mov.DATA_MOV AS \"DATA\",\n    mov.TIPO,\n    mov.DOCUMENTO,\n    mov.ENTIDADE_COD AS \"COD_ENTIDADE\",\n    mov.ENTIDADE_NOME AS \"NOME_ENTIDADE\",\n    mov.QTDE,\n    mov.VALOR_UNIT,\n    mov.TOTAL\nFROM (\n    SELECT\n        i.PROD_CODIGO,\n        p.PED_DATAVENDA as DATA_MOV,\n        'SAIDA (VI)' as TIPO,\n        CAST(p.PED_NUMEROPEDIDO AS VARCHAR(20)) as DOCUMENTO,\n        p.CLI_CODIGO as ENTIDADE_COD,\n        c.CLI_NOME as ENTIDADE_NOME,\n        i.PIT_QTDEVENDIDA as QTDE,\n        i.PIT_VALORUNITARIO as VALOR_UNIT,\n        (i.PIT_QTDEVENDIDA * i.PIT_VALORUNITARIO) as TOTAL\n    FROM PEDITENS i\n    JOIN PEDIDO p ON i.PED_NUMEROOPERACAO = p.PED_NUMEROOPERACAO\n    LEFT JOIN CLIENTE c ON p.CLI_CODIGO = c.CLI_CODIGO\n    WHERE p.PED_DATAVENDA BETWEEN :DATA_INI AND :DATA_FIM\n    \n    UNION ALL\n    \n    SELECT\n        i.PROD_CODIGO,\n        e.ENT_DATAENTRADA as DATA_MOV,\n        'ENTRADA (EE)' as TIPO,\n        CAST(e.ENT_NUMERONOTAFISCAL AS VARCHAR(20)) as DOCUMENTO,\n        e.FOR_CODIGO as ENTIDADE_COD,\n        f.FOR_NOME as ENTIDADE_NOME,\n        i.ENI_QTDEENTRADA as QTDE,\n        i.ENI_VALORUNITARIO as VALOR_UNIT,\n        (i.ENI_QTDEENTRADA * i.ENI_VALORUNITARIO) as TOTAL\n    FROM ENTITENS i\n    JOIN ENTRADA e ON i.ENT_NUMEROOPERACAO = e.ENT_NUMEROOPERACAO\n    LEFT JOIN FORNECEDOR f ON e.FOR_CODIGO = f.FOR_CODIGO\n    WHERE e.ENT_DATAENTRADA BETWEEN :DATA_INI AND :DATA_FIM\n) mov\nJOIN PRODUTO prod ON mov.PROD_CODIGO = prod.PROD_CODIGO\nORDER BY mov.PROD_CODIGO, mov.DATA_MOV"
            },
            "💰 Financeiro: Contas a Pagar": {
                "description": "Extrai contas a pagar com detalhes (use :DATA_INI e :DATA_FIM)",
                "sql": "SELECT\n    p.PAG_NUMEROOPERACAO,\n    p.PAG_DOCTO,\n    p.PAG_DATAEMISSAO,\n    p.FOR_CODIGO,\n    (SELECT f.FOR_NOME FROM FORNECEDOR f WHERE f.FOR_CODIGO = p.FOR_CODIGO) AS FOR_NOME,\n    d.PAD_PARCELA,\n    d.PAD_DATAVENCIMENTO,\n    d.PAD_VALORPARCELA,\n    d.PAD_VRTOTALPAGO,\n    p.PAG_HISTORICO\nFROM PAGDET d\nJOIN PAGAR p ON d.PAG_NUMEROOPERACAO = p.PAG_NUMEROOPERACAO\nWHERE d.PAD_DATAVENCIMENTO BETWEEN :DATA_INI AND :DATA_FIM\nORDER BY d.PAD_DATAVENCIMENTO"
            },
            "💵 Financeiro: Contas a Receber": {
                "description": "Extrai contas a receber com detalhes (use :DATA_INI e :DATA_FIM)",
                "sql": "SELECT\n    r.REC_NUMEROOPERACAO,\n    r.REC_NUMERONOTAFISCAL,\n    r.REC_DATAEMISSAO,\n    r.CLI_CODIGO,\n    (SELECT c.CLI_NOME FROM CLIENTE c WHERE c.CLI_CODIGO = r.CLI_CODIGO) AS CLI_NOME,\n    d.RED_PARCELA,\n    d.RED_DATAVENCIMENTO,\n    d.RED_VALORPARCELA,\n    d.RED_VALORRECEBIDO,\n    d.RED_DATARECEBIMENTO,\n    r.REC_HISTORICO\nFROM RECDET d\nJOIN RECEBER r ON d.REC_NUMEROOPERACAO = r.REC_NUMEROOPERACAO\nWHERE d.RED_DATAVENCIMENTO BETWEEN :DATA_INI AND :DATA_FIM\nORDER BY d.RED_DATAVENCIMENTO"
            },
            "🔎 Explorar: Primeiros 100 Registros": {
                "description": "Visualiza os primeiros 100 registros de qualquer tabela (substitua NOME_TABELA)",
                "sql": "SELECT FIRST 100 * FROM NOME_TABELA"
            },
            "📈 Análise: Produtos Mais Vendidos": {
                "description": "Top produtos por quantidade vendida (use :DATA_INI e :DATA_FIM)",
                "sql": "SELECT\n    p.PROD_CODIGO,\n    p.PROD_DESCRICAOPRODUTO,\n    SUM(i.PIT_QTDEVENDIDA) AS QTDE_TOTAL,\n    SUM(i.PIT_QTDEVENDIDA * i.PIT_VALORUNITARIO) AS VALOR_TOTAL\nFROM PEDITENS i\nJOIN PRODUTO p ON i.PROD_CODIGO = p.PROD_CODIGO\nJOIN PEDIDO ped ON i.PED_NUMEROOPERACAO = ped.PED_NUMEROOPERACAO\nWHERE ped.PED_DATAVENDA BETWEEN :DATA_INI AND :DATA_FIM\nGROUP BY p.PROD_CODIGO, p.PROD_DESCRICAOPRODUTO\nORDER BY QTDE_TOTAL DESC"
            },
            "👤 Análise: Melhores Clientes": {
                "description": "Clientes com maior volume de compras (use :DATA_INI e :DATA_FIM)",
                "sql": "SELECT\n    c.CLI_CODIGO,\n    c.CLI_NOME,\n    COUNT(DISTINCT p.PED_NUMEROOPERACAO) AS NUM_PEDIDOS,\n    SUM(i.PIT_QTDEVENDIDA * i.PIT_VALORUNITARIO) AS VALOR_TOTAL\nFROM PEDIDO p\nJOIN CLIENTE c ON p.CLI_CODIGO = c.CLI_CODIGO\nJOIN PEDITENS i ON p.PED_NUMEROOPERACAO = i.PED_NUMEROOPERACAO\nWHERE p.PED_DATAVENDA BETWEEN :DATA_INI AND :DATA_FIM\nGROUP BY c.CLI_CODIGO, c.CLI_NOME\nORDER BY VALOR_TOTAL DESC"
            }
        }
    
    def _save_query_library(self):
        """Salva a biblioteca de queries"""
        try:
            with open(self.queries_file, 'w', encoding='utf-8') as f:
                json.dump(self.query_library, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar biblioteca: {e}")
    
    def _create_widgets(self):
        # Frame superior - Seleção de query
        top_frame = ttk.Frame(self.window, padding="10")
        top_frame.pack(fill=tk.X)
        
        ttk.Label(top_frame, text="Query Salva:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        self.query_combo = ttk.Combobox(top_frame, values=list(self.query_library.keys()), width=50, state='readonly')
        self.query_combo.pack(side=tk.LEFT, padx=5)
        self.query_combo.bind('<<ComboboxSelected>>', self._load_selected_query)
        
        ttk.Button(top_frame, text="➕ Nova", command=self._new_query).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="💾 Salvar Como", command=self._save_as_query).pack(side=tk.LEFT, padx=5)
        
        # Frame de descrição
        desc_frame = ttk.LabelFrame(self.window, text="📖 Descrição da Query", padding="10")
        desc_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.desc_label = ttk.Label(desc_frame, text="Selecione uma query ou escreva uma nova", foreground="gray", wraplength=950)
        self.desc_label.pack(fill=tk.X)
        
        # Frame do editor SQL
        editor_frame = ttk.LabelFrame(self.window, text="✏️ Editor SQL", padding="10")
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Nota de ajuda
        help_note = ttk.Label(editor_frame, 
            text="💡 Dica: Use as queries da biblioteca como referência. Firebird usa sintaxe diferente de MySQL (ex: SELECT FIRST 100 * FROM tabela ao invés de LIMIT 100)",
            foreground="blue", wraplength=950, font=("Arial", 8))
        help_note.pack(pady=5)
        
        self.sql_editor = ScrolledText(editor_frame, wrap=tk.WORD, font=("Consolas", 10), height=20)
        self.sql_editor.pack(fill=tk.BOTH, expand=True)
        
        # Frame de botões
        btn_frame = ttk.Frame(self.window, padding="10")
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="🧪 Testar Query", command=self._test_query, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="💾 Salvar Alterações", command=self._save_current_query).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ Excluir Query", command=self._delete_query).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔄 Limpar Editor", command=self._clear_editor).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Fechar", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def _load_selected_query(self, event=None):
        """Carrega a query selecionada no editor"""
        selected = self.query_combo.get()
        if selected and selected in self.query_library:
            self.current_query_name = selected
            query_data = self.query_library[selected]
            
            # Atualizar descrição
            self.desc_label.config(text=query_data.get('description', 'Sem descrição'))
            
            # Carregar SQL no editor
            self.sql_editor.delete('1.0', tk.END)
            self.sql_editor.insert('1.0', query_data.get('sql', ''))
    
    def _new_query(self):
        """Limpa o editor para criar nova query"""
        self.current_query_name = None
        self.query_combo.set('')
        self.desc_label.config(text="Nova query - escreva seu SQL abaixo")
        self.sql_editor.delete('1.0', tk.END)
    
    def _clear_editor(self):
        """Limpa o editor"""
        if messagebox.askyesno("Confirmar", "Limpar o editor?"):
            self.sql_editor.delete('1.0', tk.END)
    
    def _save_as_query(self):
        """Salva a query atual com um novo nome"""
        sql = self.sql_editor.get('1.0', tk.END).strip()
        if not sql:
            messagebox.showwarning("Aviso", "Editor vazio!")
            return
        
        name = simpledialog.askstring("Nome da Query", "Digite um nome para esta query:")
        if not name:
            return
        
        desc = simpledialog.askstring("Descrição", "Digite uma descrição (opcional):") or "Query personalizada"
        
        self.query_library[name] = {
            "description": desc,
            "sql": sql
        }
        
        self._save_query_library()
        self.query_combo['values'] = list(self.query_library.keys())
        self.query_combo.set(name)
        self.current_query_name = name
        
        messagebox.showinfo("Sucesso", f"Query '{name}' salva com sucesso!")
    
    def _save_current_query(self):
        """Salva alterações na query atual"""
        if not self.current_query_name:
            messagebox.showinfo("Info", "Use 'Salvar Como' para salvar uma nova query")
            return
        
        sql = self.sql_editor.get('1.0', tk.END).strip()
        if not sql:
            messagebox.showwarning("Aviso", "Editor vazio!")
            return
        
        self.query_library[self.current_query_name]['sql'] = sql
        self._save_query_library()
        messagebox.showinfo("Sucesso", f"Query '{self.current_query_name}' atualizada!")
    
    def _delete_query(self):
        """Exclui a query selecionada"""
        if not self.current_query_name:
            messagebox.showwarning("Aviso", "Selecione uma query para excluir")
            return
        
        if messagebox.askyesno("Confirmar", f"Excluir a query '{self.current_query_name}'?"):
            del self.query_library[self.current_query_name]
            self._save_query_library()
            self.query_combo['values'] = list(self.query_library.keys())
            self._new_query()
            messagebox.showinfo("Sucesso", "Query excluída!")
    
    def _test_query(self):
        """Testa a query atual"""
        query = self.sql_editor.get('1.0', tk.END).strip()
        
        if not query:
            messagebox.showwarning("Aviso", "Editor vazio!")
            return
        
        # Substituir placeholders por valores de teste
        test_query = query.replace(':DATA_INI', "'2024-01-01'")
        test_query = test_query.replace(':DATA_FIM', "'2024-12-31'")
        test_query = test_query.replace('NOME_TABELA', 'CLIENTE')  # Placeholder padrão
        
        try:
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            import config
            from core.database import FirebirdDB
            
            db = FirebirdDB(config.DB_CONFIG)
            if not db.connect():
                messagebox.showerror("Erro", "Não foi possível conectar ao banco.\nVerifique config.py")
                return
            
            import pandas as pd
            import warnings
            
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning)
                df = pd.read_sql(test_query, db.get_connection())
            
            row_count = len(df)
            col_count = len(df.columns) if row_count > 0 else 0
            
            db.close()
            
            # Criar janela de resultado mais detalhada
            result_window = tk.Toplevel(self.window)
            result_window.title("Resultado do Teste")
            result_window.geometry("700x500")
            result_window.transient(self.window)
            
            # Frame de resumo
            summary_frame = ttk.Frame(result_window, padding="10")
            summary_frame.pack(fill=tk.X)
            
            summary_text = f"✅ Query executada com sucesso!\n📊 Registros: {row_count} | 📋 Colunas: {col_count}"
            ttk.Label(summary_frame, text=summary_text, font=("Arial", 10, "bold")).pack()
            
            if row_count > 0:
                # Mostrar colunas
                cols_frame = ttk.LabelFrame(result_window, text="Colunas Retornadas", padding="10")
                cols_frame.pack(fill=tk.X, padx=10, pady=5)
                
                cols_text = ", ".join(df.columns.tolist())
                ttk.Label(cols_frame, text=cols_text, wraplength=650).pack()
                
                # Mostrar preview dos dados
                preview_frame = ttk.LabelFrame(result_window, text="Preview dos Dados (primeiras 10 linhas)", padding="10")
                preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
                
                preview_text = ScrolledText(preview_frame, wrap=tk.NONE, font=("Consolas", 9), height=15)
                preview_text.pack(fill=tk.BOTH, expand=True)
                
                # Formatar dados para exibição
                preview_data = df.head(10).to_string(index=False)
                preview_text.insert('1.0', preview_data)
                preview_text.config(state='disabled')
            else:
                ttk.Label(result_window, text="⚠️ Nenhum registro retornado", 
                         font=("Arial", 10), foreground="orange").pack(pady=20)
            
            # Botão fechar
            ttk.Button(result_window, text="OK", command=result_window.destroy).pack(pady=10)
            
        except Exception as e:
            error_msg = f"❌ Erro ao executar query:\n\n{str(e)}\n\n"
            error_msg += "💡 Verifique a sintaxe SQL e os nomes das tabelas/colunas."
            messagebox.showerror("Erro", error_msg)
