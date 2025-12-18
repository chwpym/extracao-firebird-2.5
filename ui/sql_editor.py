import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
import os
import glob

class SQLEditorWindow:
    def __init__(self, parent, sql_dir):
        self.parent = parent
        self.sql_dir = sql_dir
        self.editors = {}  # Dicionário para armazenar os widgets de texto de cada aba
        
        # Criar janela
        self.window = tk.Toplevel(parent)
        self.window.title("Editor de Consultas SQL")
        self.window.geometry("900x600")
        
        # Criar notebook (abas)
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Carregar arquivos SQL
        self._load_sql_files()
        
        # Frame de botões
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="🧪 Testar Query Atual", command=self._test_current_query).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="💾 Salvar Tudo", command=self._save_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="💾 Salvar Atual", command=self._save_current).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔄 Recarregar", command=self._reload_current).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Fechar", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)
        
    def _load_sql_files(self):
        """Carrega todos os arquivos .sql da pasta sql/"""
        sql_files = glob.glob(os.path.join(self.sql_dir, "*.sql"))
        
        if not sql_files:
            messagebox.showwarning("Aviso", "Nenhum arquivo SQL encontrado na pasta sql/")
            return
        
        for sql_file in sorted(sql_files):
            filename = os.path.basename(sql_file)
            tab_name = filename.replace('.sql', '').replace('_', ' ').title()
            
            # Criar frame para a aba
            tab_frame = ttk.Frame(self.notebook)
            self.notebook.add(tab_frame, text=tab_name)
            
            # Adicionar label de ajuda
            help_text = self._get_help_text(filename)
            if help_text:
                help_label = ttk.Label(tab_frame, text=help_text, foreground="gray", wraplength=850)
                help_label.pack(pady=5, padx=10, anchor="w")
            
            # Criar editor de texto com scroll
            editor = ScrolledText(tab_frame, wrap=tk.WORD, font=("Consolas", 10))
            editor.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            # Carregar conteúdo do arquivo
            try:
                with open(sql_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    editor.insert('1.0', content)
            except Exception as e:
                editor.insert('1.0', f"Erro ao carregar arquivo: {e}")
            
            # Armazenar referência
            self.editors[sql_file] = editor
            
    def _get_help_text(self, filename):
        """Retorna texto de ajuda para cada tipo de arquivo SQL"""
        help_texts = {
            'clientes.sql': '📋 Extração de clientes. Use :DATA_INI e :DATA_FIM para filtros de data.',
            'produtos.sql': '📦 Extração de produtos. Use :DATA_INI e :DATA_FIM para filtros de data.',
            'fornecedores.sql': '🏭 Extração de fornecedores. Use :DATA_INI e :DATA_FIM para filtros de data.',
            'entradas_saidas.sql': '📊 Movimentações (Kardex). Placeholders: :DATA_INI e :DATA_FIM são obrigatórios.',
            'contas_pagar.sql': '💰 Contas a pagar. Placeholders: :DATA_INI e :DATA_FIM são obrigatórios.',
            'contas_receber.sql': '💵 Contas a receber. Placeholders: :DATA_INI e :DATA_FIM são obrigatórios.'
        }
        return help_texts.get(filename, '')
    
    def _save_current(self):
        """Salva apenas o arquivo da aba atual"""
        current_tab = self.notebook.select()
        if not current_tab:
            return
            
        tab_index = self.notebook.index(current_tab)
        sql_file = list(self.editors.keys())[tab_index]
        editor = self.editors[sql_file]
        
        try:
            content = editor.get('1.0', tk.END)
            with open(sql_file, 'w', encoding='utf-8') as f:
                f.write(content.rstrip())  # Remove espaços em branco no final
            
            tab_name = os.path.basename(sql_file)
            messagebox.showinfo("Sucesso", f"Arquivo {tab_name} salvo com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar arquivo: {e}")
    
    def _save_all(self):
        """Salva todos os arquivos SQL abertos"""
        saved_count = 0
        errors = []
        
        for sql_file, editor in self.editors.items():
            try:
                content = editor.get('1.0', tk.END)
                with open(sql_file, 'w', encoding='utf-8') as f:
                    f.write(content.rstrip())
                saved_count += 1
            except Exception as e:
                errors.append(f"{os.path.basename(sql_file)}: {e}")
        
        if errors:
            messagebox.showwarning("Aviso", 
                f"Salvos: {saved_count}\nErros:\n" + "\n".join(errors))
        else:
            messagebox.showinfo("Sucesso", f"{saved_count} arquivo(s) salvo(s) com sucesso!")
    
    def _reload_current(self):
        """Recarrega o arquivo da aba atual do disco"""
        current_tab = self.notebook.select()
        if not current_tab:
            return
            
        tab_index = self.notebook.index(current_tab)
        sql_file = list(self.editors.keys())[tab_index]
        editor = self.editors[sql_file]
        
        if messagebox.askyesno("Confirmar", "Descartar alterações e recarregar do disco?"):
            try:
                with open(sql_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                editor.delete('1.0', tk.END)
                editor.insert('1.0', content)
                messagebox.showinfo("Sucesso", "Arquivo recarregado!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao recarregar: {e}")
    
    def _test_current_query(self):
        """Testa a query da aba atual conectando ao banco"""
        current_tab = self.notebook.select()
        if not current_tab:
            return
            
        tab_index = self.notebook.index(current_tab)
        sql_file = list(self.editors.keys())[tab_index]
        editor = self.editors[sql_file]
        
        # Pegar a query do editor
        query = editor.get('1.0', tk.END).strip()
        
        if not query:
            messagebox.showwarning("Aviso", "Query vazia!")
            return
        
        # Substituir placeholders por valores de teste
        test_query = query.replace(':DATA_INI', "'2024-01-01'")
        test_query = test_query.replace(':DATA_FIM', "'2024-12-31'")
        
        # Tentar conectar e testar
        try:
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            import config
            from core.database import FirebirdDB
            
            db = FirebirdDB(config.DB_CONFIG)
            if not db.connect():
                messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados.\nVerifique as configurações em config.py")
                return
            
            # Executar query
            import pandas as pd
            df = pd.read_sql(test_query, db.get_connection())
            
            row_count = len(df)
            col_count = len(df.columns) if row_count > 0 else 0
            
            db.close()
            
            # Mostrar resultado
            result_msg = f"✅ Query válida!\n\n"
            result_msg += f"📊 Registros retornados: {row_count}\n"
            result_msg += f"📋 Colunas: {col_count}\n\n"
            
            if row_count > 0:
                result_msg += f"Colunas: {', '.join(df.columns.tolist())}"
            
            messagebox.showinfo("Teste de Query", result_msg)
            
        except Exception as e:
            error_msg = f"❌ Erro na query:\n\n{str(e)}\n\n"
            error_msg += "💡 Dica: Verifique a sintaxe SQL e os nomes das tabelas/colunas."
            messagebox.showerror("Erro no Teste", error_msg)
