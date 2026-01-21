import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import sys
import os
import warnings

# Suprimir warnings do pandas sobre SQLAlchemy
warnings.filterwarnings('ignore', message='.*SQLAlchemy.*', category=UserWarning)

# Adicionar o diretório pai ao path para importar módulos do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import FirebirdDB
import config

class FornecedorSearchWindow:
    def __init__(self, parent):
        self.parent = parent
        self.db = None
        self.current_fornecedor_codigo = None
        
        # Criar janela
        self.window = tk.Toplevel(parent)
        self.window.title("Consulta de Fornecedores")
        
        # Tamanho inicial (80% da tela)
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        
        # Centralizar
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Permitir redimensionamento
        self.window.minsize(1000, 600)
        
        # NÃO bloquear janela principal
        # self.window.transient(parent)  # REMOVIDO
        # self.window.grab_set()  # REMOVIDO
        self.window.focus_force()
        
        # Conectar ao banco (conexão persistente)
        self._connect_db()
        
        # Criar interface
        self._create_widgets()
        
        # Ao fechar, desconectar
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _connect_db(self):
        """Conecta ao banco de dados (conexão persistente)"""
        try:
            self.db = FirebirdDB(config.DB_CONFIG)
            if not self.db.connect():
                messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao conectar:\n{str(e)}")
    
    def _on_close(self):
        """Fecha a conexão e a janela"""
        if self.db:
            self.db.close()
        self.window.destroy()
    
    def _create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ===== ÁREA DE BUSCA =====
        search_frame = ttk.LabelFrame(main_frame, text="Buscar Fornecedor", padding="10")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Campo de busca
        ttk.Label(search_frame, text="Nome, CNPJ ou Telefone:").pack(side=tk.LEFT, padx=5)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=60)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind('<Return>', lambda e: self._buscar_fornecedor())
        search_entry.focus()
        
        # Checkbox busca por código interno
        self.busca_codigo_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(search_frame, text="🔢 Busca por Código", 
                       variable=self.busca_codigo_var).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(search_frame, text="🔍 Buscar", command=self._buscar_fornecedor).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="📄 Buscar Todos", command=self._buscar_todos).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="🔄 Limpar", command=self._limpar_busca).pack(side=tk.LEFT, padx=5)
        
        # ===== LISTA DE FORNECEDORES =====
        fornecedores_frame = ttk.LabelFrame(main_frame, text="Fornecedores Encontrados", padding="10")
        fornecedores_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 10))
        
        # Filtro rápido
        filter_frame = ttk.Frame(fornecedores_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(filter_frame, text="Filtro rápido:").pack(side=tk.LEFT, padx=5)
        self.filter_var = tk.StringVar()
        self.filter_var.trace('w', self._aplicar_filtro_rapido)
        ttk.Entry(filter_frame, textvariable=self.filter_var, width=40).pack(side=tk.LEFT, padx=5)
        
        # Treeview para lista de fornecedores
        tree_frame = ttk.Frame(fornecedores_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        # Colunas da lista
        columns = ("codigo", "nome", "fantasia", "cnpj", "telefone", "cidade")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings',
                                 yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Configurar colunas
        self.tree.heading("codigo", text="Código")
        self.tree.heading("nome", text="Razão Social")
        self.tree.heading("fantasia", text="Nome Fantasia")
        self.tree.heading("cnpj", text="CNPJ")
        self.tree.heading("telefone", text="Telefone")
        self.tree.heading("cidade", text="Cidade")
        
        self.tree.column("codigo", width=80, anchor=tk.W)
        self.tree.column("nome", width=300, anchor=tk.W)
        self.tree.column("fantasia", width=200, anchor=tk.W)
        self.tree.column("cnpj", width=150, anchor=tk.W)
        self.tree.column("telefone", width=120, anchor=tk.W)
        self.tree.column("cidade", width=150, anchor=tk.W)
        
        # Bind para ordenação ao clicar no cabeçalho
        for col in columns:
            self.tree.heading(col, command=lambda c=col: self._ordenar_por_coluna(c))
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind duplo clique
        self.tree.bind('<Double-1>', self._on_fornecedor_double_click)
        
        # ===== DETALHES DO FORNECEDOR =====
        details_frame = ttk.LabelFrame(main_frame, text="Detalhes do Fornecedor", padding="10")
        details_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Frame com scroll para os detalhes
        canvas = tk.Canvas(details_frame)
        scrollbar = ttk.Scrollbar(details_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Grid para todos os dados (fonte maior e copiável)
        font_label = ('Arial', 9, 'bold')
        font_value = ('Arial', 10)
        
        row = 0
        # Usar 6 colunas para melhor aproveitamento do espaço
        col1_label = 0
        col1_value = 1
        col2_label = 2
        col2_value = 3
        col3_label = 4
        col3_value = 5
        
        # LINHA 1 - 3 campos por linha
        ttk.Label(scrollable_frame, text="Código:", font=font_label).grid(row=row, column=col1_label, sticky=tk.W, padx=5, pady=3)
        self.lbl_codigo = tk.Entry(scrollable_frame, font=font_value, relief=tk.FLAT, state='readonly', width=12)
        self.lbl_codigo.grid(row=row, column=col1_value, sticky=tk.W, padx=5, pady=3)
        
        ttk.Label(scrollable_frame, text="Tipo Pessoa:", font=font_label).grid(row=row, column=col2_label, sticky=tk.W, padx=5, pady=3)
        self.lbl_tipo = tk.Entry(scrollable_frame, font=font_value, relief=tk.FLAT, state='readonly', width=15)
        self.lbl_tipo.grid(row=row, column=col2_value, sticky=tk.W, padx=5, pady=3)
        
        ttk.Label(scrollable_frame, text="Insc. Estadual:", font=font_label).grid(row=row, column=col3_label, sticky=tk.W, padx=5, pady=3)
        self.lbl_ie = tk.Entry(scrollable_frame, font=font_value, relief=tk.FLAT, state='readonly', width=20)
        self.lbl_ie.grid(row=row, column=col3_value, sticky=tk.W, padx=5, pady=3)
        
        # LINHA 2 - Razão Social span 6 colunas
        row += 1
        ttk.Label(scrollable_frame, text="Razão Social:", font=font_label).grid(row=row, column=col1_label, sticky=tk.W, padx=5, pady=3)
        self.lbl_nome = tk.Entry(scrollable_frame, font=font_value, relief=tk.FLAT, state='readonly', width=70)
        self.lbl_nome.grid(row=row, column=col1_value, sticky=tk.W, padx=5, pady=3, columnspan=5)
        
        # LINHA 3 - Fantasia span 6 colunas
        row += 1
        ttk.Label(scrollable_frame, text="Nome Fantasia:", font=font_label).grid(row=row, column=col1_label, sticky=tk.W, padx=5, pady=3)
        self.lbl_fantasia = tk.Entry(scrollable_frame, font=font_value, relief=tk.FLAT, state='readonly', width=70)
        self.lbl_fantasia.grid(row=row, column=col1_value, sticky=tk.W, padx=5, pady=3, columnspan=5)
        
        # LINHA 4 - CNPJ span 6 colunas
        row += 1
        ttk.Label(scrollable_frame, text="CNPJ:", font=font_label).grid(row=row, column=col1_label, sticky=tk.W, padx=5, pady=3)
        self.lbl_cnpj = tk.Entry(scrollable_frame, font=font_value, relief=tk.FLAT, state='readonly', width=20)
        self.lbl_cnpj.grid(row=row, column=col1_value, sticky=tk.W, padx=5, pady=3, columnspan=5)
        
        # LINHA 5 - Contatos (3 campos)
        row += 1
        ttk.Label(scrollable_frame, text="Telefone:", font=font_label).grid(row=row, column=col1_label, sticky=tk.W, padx=5, pady=3)
        self.lbl_telefone = tk.Entry(scrollable_frame, font=font_value, relief=tk.FLAT, state='readonly', width=15)
        self.lbl_telefone.grid(row=row, column=col1_value, sticky=tk.W, padx=5, pady=3)
        
        ttk.Label(scrollable_frame, text="Celular:", font=font_label).grid(row=row, column=col2_label, sticky=tk.W, padx=5, pady=3)
        self.lbl_celular = tk.Entry(scrollable_frame, font=font_value, relief=tk.FLAT, state='readonly', width=15)
        self.lbl_celular.grid(row=row, column=col2_value, sticky=tk.W, padx=5, pady=3)
        
        ttk.Label(scrollable_frame, text="Fax:", font=font_label).grid(row=row, column=col3_label, sticky=tk.W, padx=5, pady=3)
        self.lbl_fax = tk.Entry(scrollable_frame, font=font_value, relief=tk.FLAT, state='readonly', width=15)
        self.lbl_fax.grid(row=row, column=col3_value, sticky=tk.W, padx=5, pady=3)
        
        # LINHA 6 - Email span 6 colunas
        row += 1
        ttk.Label(scrollable_frame, text="Email:", font=font_label).grid(row=row, column=col1_label, sticky=tk.W, padx=5, pady=3)
        self.lbl_email = tk.Entry(scrollable_frame, font=font_value, relief=tk.FLAT, state='readonly', width=70)
        self.lbl_email.grid(row=row, column=col1_value, sticky=tk.W, padx=5, pady=3, columnspan=5)
        
        # LINHA 7 - Endereço completo span 6 colunas
        row += 1
        ttk.Label(scrollable_frame, text="Logradouro:", font=font_label).grid(row=row, column=col1_label, sticky=tk.W, padx=5, pady=3)
        self.lbl_logradouro = tk.Entry(scrollable_frame, font=font_value, relief=tk.FLAT, state='readonly', width=70)
        self.lbl_logradouro.grid(row=row, column=col1_value, sticky=tk.W, padx=5, pady=3, columnspan=5)
        
        # LINHA 8 - Bairro, CEP, Cidade (3 campos)
        row += 1
        ttk.Label(scrollable_frame, text="Bairro:", font=font_label).grid(row=row, column=col1_label, sticky=tk.W, padx=5, pady=3)
        self.lbl_bairro = tk.Entry(scrollable_frame, font=font_value, relief=tk.FLAT, state='readonly', width=25)
        self.lbl_bairro.grid(row=row, column=col1_value, sticky=tk.W, padx=5, pady=3)
        
        ttk.Label(scrollable_frame, text="CEP:", font=font_label).grid(row=row, column=col2_label, sticky=tk.W, padx=5, pady=3)
        self.lbl_cep = tk.Entry(scrollable_frame, font=font_value, relief=tk.FLAT, state='readonly', width=12)
        self.lbl_cep.grid(row=row, column=col2_value, sticky=tk.W, padx=5, pady=3)
        
        ttk.Label(scrollable_frame, text="Cidade:", font=font_label).grid(row=row, column=col3_label, sticky=tk.W, padx=5, pady=3)
        self.lbl_cidade = tk.Entry(scrollable_frame, font=font_value, relief=tk.FLAT, state='readonly', width=25)
        self.lbl_cidade.grid(row=row, column=col3_value, sticky=tk.W, padx=5, pady=3)
        
        # LINHA 9 - UF
        row += 1
        ttk.Label(scrollable_frame, text="UF:", font=font_label).grid(row=row, column=col1_label, sticky=tk.W, padx=5, pady=3)
        self.lbl_uf = tk.Entry(scrollable_frame, font=font_value, relief=tk.FLAT, state='readonly', width=5)
        self.lbl_uf.grid(row=row, column=col1_value, sticky=tk.W, padx=5, pady=3)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Status bar
        self.status_var = tk.StringVar(value="Pronto")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def _buscar_fornecedor(self):
        """Busca fornecedores no banco de dados"""
        termo = self.search_var.get().strip()
        
        if not termo:
            messagebox.showwarning("Atenção", "Digite um termo para buscar")
            return
        
        try:
            self.status_var.set("Buscando...")
            self.window.update()
            
            if self.busca_codigo_var.get():
                # Busca por código
                query = f"""
                    SELECT 
                        FOR_CODIGO, FOR_NOME, FOR_FANTASIA,
                        FOR_CNPJ, FOR_TELEFONE, FOR_CELULAR,
                        FOR_CIDADE, FOR_UF, FOR_BAIRRO, FOR_CEP,
                        FOR_LOGRADOUROENDERECO, FOR_EMAIL, FOR_FAX,
                        FOR_INSCRICAOESTADUAL, FOR_PESSOAFISICAJURIDICA
                    FROM FORNECEDOR
                    WHERE FOR_CODIGO = {termo}
                """
            else:
                # Busca por nome, CNPJ ou telefone
                termo_upper = termo.upper()
                query = f"""
                    SELECT 
                        FOR_CODIGO, FOR_NOME, FOR_FANTASIA,
                        FOR_CNPJ, FOR_TELEFONE, FOR_CELULAR,
                        FOR_CIDADE, FOR_UF, FOR_BAIRRO, FOR_CEP,
                        FOR_LOGRADOUROENDERECO, FOR_EMAIL, FOR_FAX,
                        FOR_INSCRICAOESTADUAL, FOR_PESSOAFISICAJURIDICA
                    FROM FORNECEDOR
                    WHERE UPPER(FOR_NOME) LIKE '%{termo_upper}%'
                       OR UPPER(FOR_FANTASIA) LIKE '%{termo_upper}%'
                       OR FOR_CNPJ LIKE '%{termo}%'
                       OR FOR_TELEFONE LIKE '%{termo}%'
                       OR FOR_CELULAR LIKE '%{termo}%'
                    ORDER BY FOR_NOME
                """
            
            df = pd.read_sql(query, self.db.get_connection())
            
            if df is None or df.empty:
                self.status_var.set("Nenhum fornecedor encontrado")
                messagebox.showinfo("Informação", "Nenhum fornecedor encontrado")
                return
            
            # Armazenar dataframe
            self.df_fornecedores = df
            
            # Limpar treeview
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Preencher treeview
            for idx, row in df.iterrows():
                codigo = row['FOR_CODIGO']
                nome = row['FOR_NOME'] or '-'
                fantasia = row['FOR_FANTASIA'] or '-'
                cnpj = self._formatar_cnpj(row['FOR_CNPJ']) if row['FOR_CNPJ'] else '-'
                telefone = row['FOR_TELEFONE'] or row['FOR_CELULAR'] or '-'
                cidade = row['FOR_CIDADE'] or '-'
                
                self.tree.insert('', 'end', values=(codigo, nome, fantasia, cnpj, telefone, cidade))
            
            self.status_var.set(f"{len(df)} fornecedor(es) encontrado(s)")
            
        except Exception as e:
            self.status_var.set("Erro na busca")
            messagebox.showerror("Erro", f"Erro ao buscar fornecedores:\n{str(e)}")
    
    def _buscar_todos(self):
        """Busca todos os fornecedores do banco de dados"""
        try:
            self.status_var.set("Buscando todos os fornecedores...")
            self.window.update()
            
            query = """
                SELECT 
                    FOR_CODIGO, FOR_NOME, FOR_FANTASIA,
                    FOR_CNPJ, FOR_TELEFONE, FOR_CELULAR,
                    FOR_CIDADE, FOR_UF, FOR_BAIRRO, FOR_CEP,
                    FOR_LOGRADOUROENDERECO, FOR_EMAIL, FOR_FAX,
                    FOR_INSCRICAOESTADUAL, FOR_PESSOAFISICAJURIDICA
                FROM FORNECEDOR
                ORDER BY FOR_NOME
            """
            
            df = pd.read_sql(query, self.db.get_connection())
            
            if df is None or df.empty:
                self.status_var.set("Nenhum fornecedor encontrado")
                messagebox.showinfo("Informação", "Nenhum fornecedor encontrado")
                return
            
            # Armazenar dataframe
            self.df_fornecedores = df
            
            # Limpar treeview
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Preencher treeview
            for idx, row in df.iterrows():
                codigo = row['FOR_CODIGO']
                nome = row['FOR_NOME'] or '-'
                fantasia = row['FOR_FANTASIA'] or '-'
                cnpj = self._formatar_cnpj(row['FOR_CNPJ']) if row['FOR_CNPJ'] else '-'
                telefone = row['FOR_TELEFONE'] or row['FOR_CELULAR'] or '-'
                cidade = row['FOR_CIDADE'] or '-'
                
                self.tree.insert('', 'end', values=(codigo, nome, fantasia, cnpj, telefone, cidade))
            
            self.status_var.set(f"{len(df)} fornecedor(es) encontrado(s)")
            
        except Exception as e:
            self.status_var.set("Erro na busca")
            messagebox.showerror("Erro", f"Erro ao buscar todos os fornecedores:\n{str(e)}")
    
    def _ordenar_por_coluna(self, col):
        """Ordena a lista ao clicar no cabeçalho da coluna"""
        if not hasattr(self, 'df_fornecedores') or self.df_fornecedores is None:
            return
        
        # Mapear colunas da treeview para colunas do dataframe
        col_map = {
            'codigo': 'FOR_CODIGO',
            'nome': 'FOR_NOME',
            'fantasia': 'FOR_FANTASIA',
            'cnpj': 'FOR_CNPJ',
            'telefone': 'FOR_TELEFONE',
            'cidade': 'FOR_CIDADE'
        }
        
        if col not in col_map:
            return
        
        df_col = col_map[col]
        
        # Alternar ordem ascendente/descendente
        if not hasattr(self, '_sort_reverse'):
            self._sort_reverse = {}
        
        self._sort_reverse[col] = not self._sort_reverse.get(col, False)
        
        # Ordenar dataframe
        self.df_fornecedores = self.df_fornecedores.sort_values(
            by=df_col, 
            ascending=not self._sort_reverse[col],
            na_position='last'
        )
        
        # Limpar e repreencher treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for idx, row in self.df_fornecedores.iterrows():
            codigo = row['FOR_CODIGO']
            nome = row['FOR_NOME'] or '-'
            fantasia = row['FOR_FANTASIA'] or '-'
            cnpj = self._formatar_cnpj(row['FOR_CNPJ']) if row['FOR_CNPJ'] else '-'
            telefone = row['FOR_TELEFONE'] or row['FOR_CELULAR'] or '-'
            cidade = row['FOR_CIDADE'] or '-'
            
            self.tree.insert('', 'end', values=(codigo, nome, fantasia, cnpj, telefone, cidade))
    
    def _limpar_busca(self):
        """Limpa os campos de busca e resultados"""
        self.search_var.set("")
        self.filter_var.set("")
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._limpar_detalhes()
        self.status_var.set("Pronto")
    
    def _aplicar_filtro_rapido(self, *args):
        """Aplica filtro rápido na lista"""
        if not hasattr(self, 'df_fornecedores') or self.df_fornecedores is None:
            return
        
        filtro = self.filter_var.get().upper()
        
        # Limpar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Filtrar e preencher
        for idx, row in self.df_fornecedores.iterrows():
            nome = str(row['FOR_NOME'] or '').upper()
            fantasia = str(row['FOR_FANTASIA'] or '').upper()
            cidade = str(row['FOR_CIDADE'] or '').upper()
            
            if filtro in nome or filtro in fantasia or filtro in cidade:
                codigo = row['FOR_CODIGO']
                nome_display = row['FOR_NOME'] or '-'
                fantasia_display = row['FOR_FANTASIA'] or '-'
                cnpj = self._formatar_cnpj(row['FOR_CNPJ']) if row['FOR_CNPJ'] else '-'
                telefone = row['FOR_TELEFONE'] or row['FOR_CELULAR'] or '-'
                cidade_display = row['FOR_CIDADE'] or '-'
                
                self.tree.insert('', 'end', values=(codigo, nome_display, fantasia_display, cnpj, telefone, cidade_display))
    
    def _on_fornecedor_double_click(self, event):
        """Exibe detalhes do fornecedor ao clicar"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        codigo = item['values'][0]
        
        # Buscar dados completos
        fornecedor = self.df_fornecedores[self.df_fornecedores['FOR_CODIGO'] == codigo].iloc[0]
        
        # Preencher detalhes - usar delete + insert para Entry readonly
        def set_entry(entry, value):
            entry.config(state='normal')
            entry.delete(0, tk.END)
            entry.insert(0, str(value) if value else '-')
            entry.config(state='readonly')
        
        set_entry(self.lbl_codigo, codigo)
        set_entry(self.lbl_nome, fornecedor['FOR_NOME'] or '-')
        set_entry(self.lbl_fantasia, fornecedor['FOR_FANTASIA'] or '-')
        
        tipo = "Pessoa Física" if fornecedor['FOR_PESSOAFISICAJURIDICA'] == 'F' else "Pessoa Jurídica"
        set_entry(self.lbl_tipo, tipo)
        
        set_entry(self.lbl_cnpj, self._formatar_cnpj(fornecedor['FOR_CNPJ']) if fornecedor['FOR_CNPJ'] else '-')
        set_entry(self.lbl_ie, fornecedor['FOR_INSCRICAOESTADUAL'] or '-')
        
        set_entry(self.lbl_telefone, fornecedor['FOR_TELEFONE'] or '-')
        set_entry(self.lbl_celular, fornecedor['FOR_CELULAR'] or '-')
        set_entry(self.lbl_fax, fornecedor['FOR_FAX'] or '-')
        set_entry(self.lbl_email, fornecedor['FOR_EMAIL'] or '-')
        
        set_entry(self.lbl_logradouro, fornecedor['FOR_LOGRADOUROENDERECO'] or '-')
        set_entry(self.lbl_bairro, fornecedor['FOR_BAIRRO'] or '-')
        set_entry(self.lbl_cep, self._formatar_cep(fornecedor['FOR_CEP']) if fornecedor['FOR_CEP'] else '-')
        set_entry(self.lbl_cidade, fornecedor['FOR_CIDADE'] or '-')
        set_entry(self.lbl_uf, fornecedor['FOR_UF'] or '-')
        
        self.current_fornecedor_codigo = codigo
    
    def _limpar_detalhes(self):
        """Limpa os detalhes do fornecedor"""
        def clear_entry(entry):
            entry.config(state='normal')
            entry.delete(0, tk.END)
            entry.insert(0, '-')
            entry.config(state='readonly')
        
        clear_entry(self.lbl_codigo)
        clear_entry(self.lbl_nome)
        clear_entry(self.lbl_fantasia)
        clear_entry(self.lbl_tipo)
        clear_entry(self.lbl_cnpj)
        clear_entry(self.lbl_ie)
        clear_entry(self.lbl_telefone)
        clear_entry(self.lbl_celular)
        clear_entry(self.lbl_fax)
        clear_entry(self.lbl_email)
        clear_entry(self.lbl_logradouro)
        clear_entry(self.lbl_bairro)
        clear_entry(self.lbl_cep)
        clear_entry(self.lbl_cidade)
        clear_entry(self.lbl_uf)
        self.current_fornecedor_codigo = None
    
    def _formatar_cnpj(self, cnpj):
        """Formata CNPJ: 00.000.000/0000-00"""
        if not cnpj:
            return '-'
        cnpj = str(cnpj).strip().replace('.', '').replace('/', '').replace('-', '')
        if len(cnpj) == 14:
            return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
        return cnpj
    
    def _formatar_cep(self, cep):
        """Formata CEP: 00000-000"""
        if not cep:
            return '-'
        cep = str(cep).strip().replace('-', '')
        if len(cep) == 8:
            return f"{cep[:5]}-{cep[5:]}"
        return cep
