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

class ClienteSearchWindow:
    def __init__(self, parent):
        self.parent = parent
        self.db = None
        self.current_cliente_codigo = None
        
        # Criar janela
        self.window = tk.Toplevel(parent)
        self.window.title("Consulta de Clientes")
        
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
        search_frame = ttk.LabelFrame(main_frame, text="Buscar Cliente", padding="10")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Campo de busca
        ttk.Label(search_frame, text="Nome, CPF/CNPJ ou Telefone:").pack(side=tk.LEFT, padx=5)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=60)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind('<Return>', lambda e: self._buscar_cliente())
        search_entry.focus()
        
        # Checkbox busca por código interno
        self.busca_codigo_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(search_frame, text="🔢 Busca por Código", 
                       variable=self.busca_codigo_var).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(search_frame, text="🔍 Buscar", command=self._buscar_cliente).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="📄 Buscar Todos", command=self._buscar_todos).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="🔄 Limpar", command=self._limpar_busca).pack(side=tk.LEFT, padx=5)
        
        # ===== LISTA DE CLIENTES =====
        clientes_frame = ttk.LabelFrame(main_frame, text="Clientes Encontrados", padding="10")
        clientes_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 10))
        
        # Filtro rápido
        filter_frame = ttk.Frame(clientes_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(filter_frame, text="Filtro rápido:").pack(side=tk.LEFT, padx=5)
        self.filter_var = tk.StringVar()
        self.filter_var.trace('w', self._aplicar_filtro_rapido)
        ttk.Entry(filter_frame, textvariable=self.filter_var, width=40).pack(side=tk.LEFT, padx=5)
        
        # Treeview para lista de clientes
        tree_frame = ttk.Frame(clientes_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        # Colunas da lista
        columns = ("codigo", "nome", "fantasia", "documento", "telefone", "cidade")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings',
                                 yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Configurar colunas
        self.tree.heading("codigo", text="Código")
        self.tree.heading("nome", text="Nome/Razão Social")
        self.tree.heading("fantasia", text="Fantasia")
        self.tree.heading("documento", text="CPF/CNPJ")
        self.tree.heading("telefone", text="Telefone")
        self.tree.heading("cidade", text="Cidade")
        
        self.tree.column("codigo", width=80, anchor=tk.W)
        self.tree.column("nome", width=300, anchor=tk.W)
        self.tree.column("fantasia", width=200, anchor=tk.W)
        self.tree.column("documento", width=150, anchor=tk.W)
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
        self.tree.bind('<Double-1>', self._on_cliente_double_click)
        
        # ===== DETALHES DO CLIENTE =====
        details_frame = ttk.LabelFrame(main_frame, text="Detalhes do Cliente", padding="10")
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
        
        # Grid para todos os dados (fonte maior e copíavel)
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
        
        ttk.Label(scrollable_frame, text="Data Nascimento:", font=font_label).grid(row=row, column=col3_label, sticky=tk.W, padx=5, pady=3)
        self.lbl_data_nasc = tk.Entry(scrollable_frame, font=font_value, relief=tk.FLAT, state='readonly', width=12)
        self.lbl_data_nasc.grid(row=row, column=col3_value, sticky=tk.W, padx=5, pady=3)
        
        # LINHA 2 - Nome completo span 6 colunas
        row += 1
        ttk.Label(scrollable_frame, text="Nome/Razão Social:", font=font_label).grid(row=row, column=col1_label, sticky=tk.W, padx=5, pady=3)
        self.lbl_nome = tk.Entry(scrollable_frame, font=font_value, relief=tk.FLAT, state='readonly', width=70)
        self.lbl_nome.grid(row=row, column=col1_value, sticky=tk.W, padx=5, pady=3, columnspan=5)
        
        # LINHA 3 - Fantasia span 6 colunas
        row += 1
        ttk.Label(scrollable_frame, text="Nome Fantasia:", font=font_label).grid(row=row, column=col1_label, sticky=tk.W, padx=5, pady=3)
        self.lbl_fantasia = tk.Entry(scrollable_frame, font=font_value, relief=tk.FLAT, state='readonly', width=70)
        self.lbl_fantasia.grid(row=row, column=col1_value, sticky=tk.W, padx=5, pady=3, columnspan=5)
        
        # LINHA 4 - Documentos (3 campos)
        row += 1
        ttk.Label(scrollable_frame, text="CPF:", font=font_label).grid(row=row, column=col1_label, sticky=tk.W, padx=5, pady=3)
        self.lbl_cpf = tk.Entry(scrollable_frame, font=font_value, relief=tk.FLAT, state='readonly', width=15)
        self.lbl_cpf.grid(row=row, column=col1_value, sticky=tk.W, padx=5, pady=3)
        
        ttk.Label(scrollable_frame, text="RG:", font=font_label).grid(row=row, column=col2_label, sticky=tk.W, padx=5, pady=3)
        self.lbl_rg = tk.Entry(scrollable_frame, font=font_value, relief=tk.FLAT, state='readonly', width=15)
        self.lbl_rg.grid(row=row, column=col2_value, sticky=tk.W, padx=5, pady=3)
        
        ttk.Label(scrollable_frame, text="CNPJ:", font=font_label).grid(row=row, column=col3_label, sticky=tk.W, padx=5, pady=3)
        self.lbl_cnpj = tk.Entry(scrollable_frame, font=font_value, relief=tk.FLAT, state='readonly', width=20)
        self.lbl_cnpj.grid(row=row, column=col3_value, sticky=tk.W, padx=5, pady=3)
        
        # LINHA 5 - Insc. Estadual (2 campos)
        row += 1
        ttk.Label(scrollable_frame, text="Insc. Estadual:", font=font_label).grid(row=row, column=col1_label, sticky=tk.W, padx=5, pady=3)
        self.lbl_ie = tk.Entry(scrollable_frame, font=font_value, relief=tk.FLAT, state='readonly', width=20)
        self.lbl_ie.grid(row=row, column=col1_value, sticky=tk.W, padx=5, pady=3, columnspan=5)
        
        # LINHA 6 - Contatos (3 campos)
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
        
        # LINHA 7 - Email span 6 colunas
        row += 1
        ttk.Label(scrollable_frame, text="Email:", font=font_label).grid(row=row, column=col1_label, sticky=tk.W, padx=5, pady=3)
        self.lbl_email = tk.Entry(scrollable_frame, font=font_value, relief=tk.FLAT, state='readonly', width=70)
        self.lbl_email.grid(row=row, column=col1_value, sticky=tk.W, padx=5, pady=3, columnspan=5)
        
        # LINHA 8 - Endereço completo span 6 colunas
        row += 1
        ttk.Label(scrollable_frame, text="Logradouro:", font=font_label).grid(row=row, column=col1_label, sticky=tk.W, padx=5, pady=3)
        self.lbl_logradouro = tk.Entry(scrollable_frame, font=font_value, relief=tk.FLAT, state='readonly', width=70)
        self.lbl_logradouro.grid(row=row, column=col1_value, sticky=tk.W, padx=5, pady=3, columnspan=5)
        
        # LINHA 9 - Número, Complemento, Bairro (3 campos)
        row += 1
        ttk.Label(scrollable_frame, text="Número:", font=font_label).grid(row=row, column=col1_label, sticky=tk.W, padx=5, pady=3)
        self.lbl_numero = tk.Entry(scrollable_frame, font=font_value, relief=tk.FLAT, state='readonly', width=10)
        self.lbl_numero.grid(row=row, column=col1_value, sticky=tk.W, padx=5, pady=3)
        
        ttk.Label(scrollable_frame, text="Complemento:", font=font_label).grid(row=row, column=col2_label, sticky=tk.W, padx=5, pady=3)
        self.lbl_complemento = tk.Entry(scrollable_frame, font=font_value, relief=tk.FLAT, state='readonly', width=20)
        self.lbl_complemento.grid(row=row, column=col2_value, sticky=tk.W, padx=5, pady=3)
        
        ttk.Label(scrollable_frame, text="Bairro:", font=font_label).grid(row=row, column=col3_label, sticky=tk.W, padx=5, pady=3)
        self.lbl_bairro = tk.Entry(scrollable_frame, font=font_value, relief=tk.FLAT, state='readonly', width=25)
        self.lbl_bairro.grid(row=row, column=col3_value, sticky=tk.W, padx=5, pady=3)
        
        # LINHA 10 - CEP, Cidade, UF (3 campos)
        row += 1
        ttk.Label(scrollable_frame, text="CEP:", font=font_label).grid(row=row, column=col1_label, sticky=tk.W, padx=5, pady=3)
        self.lbl_cep = tk.Entry(scrollable_frame, font=font_value, relief=tk.FLAT, state='readonly', width=12)
        self.lbl_cep.grid(row=row, column=col1_value, sticky=tk.W, padx=5, pady=3)
        
        ttk.Label(scrollable_frame, text="Cidade:", font=font_label).grid(row=row, column=col2_label, sticky=tk.W, padx=5, pady=3)
        self.lbl_cidade = tk.Entry(scrollable_frame, font=font_value, relief=tk.FLAT, state='readonly', width=25)
        self.lbl_cidade.grid(row=row, column=col2_value, sticky=tk.W, padx=5, pady=3)
        
        ttk.Label(scrollable_frame, text="UF:", font=font_label).grid(row=row, column=col3_label, sticky=tk.W, padx=5, pady=3)
        self.lbl_uf = tk.Entry(scrollable_frame, font=font_value, relief=tk.FLAT, state='readonly', width=5)
        self.lbl_uf.grid(row=row, column=col3_value, sticky=tk.W, padx=5, pady=3)
        
        # LINHA 11 - Datas (3 campos)
        row += 1
        ttk.Label(scrollable_frame, text="Data Cadastro:", font=font_label).grid(row=row, column=col1_label, sticky=tk.W, padx=5, pady=3)
        self.lbl_data_cadastro = tk.Entry(scrollable_frame, font=font_value, relief=tk.FLAT, state='readonly', width=12)
        self.lbl_data_cadastro.grid(row=row, column=col1_value, sticky=tk.W, padx=5, pady=3)
        
        ttk.Label(scrollable_frame, text="Última Compra:", font=font_label).grid(row=row, column=col2_label, sticky=tk.W, padx=5, pady=3)
        self.lbl_ultima_compra = tk.Entry(scrollable_frame, font=font_value, relief=tk.FLAT, state='readonly', width=12)
        self.lbl_ultima_compra.grid(row=row, column=col2_value, sticky=tk.W, padx=5, pady=3)
        
        # LINHA 12 - Observações span 6 colunas
        row += 1
        ttk.Label(scrollable_frame, text="Observações:", font=font_label).grid(row=row, column=col1_label, sticky=tk.NW, padx=5, pady=3)
        self.txt_observacoes = tk.Text(scrollable_frame, font=font_value, height=3, width=90, wrap=tk.WORD)
        self.txt_observacoes.grid(row=row, column=col1_value, sticky=tk.W, padx=5, pady=3, columnspan=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Status bar
        self.status_var = tk.StringVar(value="Pronto")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def _buscar_cliente(self):
        """Busca clientes no banco de dados"""
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
                        CLI_CODIGO, CLI_NOME, CLI_FANTASIA,
                        CLI_CPF, CLI_CNPJ, CLI_TELEFONE, CLI_CELULAR,
                        CLI_CIDADE, CLI_UF, CLI_BAIRRO, CLI_CEP,
                        CLI_LOGRADOUROENDERECO, CLI_LOGRADOURONUMERO, CLI_COMPLEMENTO,
                        CLI_EMAIL, CLI_FAX, CLI_RG, CLI_INSCRICAOESTADUAL,
                        CLI_PESSOAFISICAJURIDICA, CLI_DATANASCIMENTO,
                        CLI_DATACADASTRO, CLI_DATAULTIMACOMPRA
                    FROM CLIENTE
                    WHERE CLI_CODIGO = {termo}
                """
            else:
                # Busca por nome, documento ou telefone
                termo_upper = termo.upper()
                query = f"""
                    SELECT 
                        CLI_CODIGO, CLI_NOME, CLI_FANTASIA,
                        CLI_CPF, CLI_CNPJ, CLI_TELEFONE, CLI_CELULAR,
                        CLI_CIDADE, CLI_UF, CLI_BAIRRO, CLI_CEP,
                        CLI_LOGRADOUROENDERECO, CLI_LOGRADOURONUMERO, CLI_COMPLEMENTO,
                        CLI_EMAIL, CLI_FAX, CLI_RG, CLI_INSCRICAOESTADUAL,
                        CLI_PESSOAFISICAJURIDICA, CLI_DATANASCIMENTO,
                        CLI_DATACADASTRO, CLI_DATAULTIMACOMPRA
                    FROM CLIENTE
                    WHERE UPPER(CLI_NOME) LIKE '%{termo_upper}%'
                       OR UPPER(CLI_FANTASIA) LIKE '%{termo_upper}%'
                       OR CLI_CPF LIKE '%{termo}%'
                       OR CLI_CNPJ LIKE '%{termo}%'
                       OR CLI_TELEFONE LIKE '%{termo}%'
                       OR CLI_CELULAR LIKE '%{termo}%'
                    ORDER BY CLI_NOME
                """
            
            df = pd.read_sql(query, self.db.get_connection())
            
            if df is None or df.empty:
                self.status_var.set("Nenhum cliente encontrado")
                messagebox.showinfo("Informação", "Nenhum cliente encontrado")
                return
            
            # Armazenar dataframe
            self.df_clientes = df
            
            # Limpar treeview
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Preencher treeview
            for idx, row in df.iterrows():
                codigo = row['CLI_CODIGO']
                nome = row['CLI_NOME'] or '-'
                fantasia = row['CLI_FANTASIA'] or '-'
                
                # Documento (CPF ou CNPJ)
                if row['CLI_PESSOAFISICAJURIDICA'] == 'F':
                    documento = self._formatar_cpf(row['CLI_CPF']) if row['CLI_CPF'] else '-'
                else:
                    documento = self._formatar_cnpj(row['CLI_CNPJ']) if row['CLI_CNPJ'] else '-'
                
                telefone = row['CLI_TELEFONE'] or row['CLI_CELULAR'] or '-'
                cidade = row['CLI_CIDADE'] or '-'
                
                self.tree.insert('', 'end', values=(codigo, nome, fantasia, documento, telefone, cidade))
            
            self.status_var.set(f"{len(df)} cliente(s) encontrado(s)")
            
        except Exception as e:
            self.status_var.set("Erro na busca")
            messagebox.showerror("Erro", f"Erro ao buscar clientes:\n{str(e)}")
    
    def _buscar_todos(self):
        """Busca todos os clientes do banco de dados"""
        try:
            self.status_var.set("Buscando todos os clientes...")
            self.window.update()
            
            query = """
                SELECT 
                    CLI_CODIGO, CLI_NOME, CLI_FANTASIA,
                    CLI_CPF, CLI_CNPJ, CLI_TELEFONE, CLI_CELULAR,
                    CLI_CIDADE, CLI_UF, CLI_BAIRRO, CLI_CEP,
                    CLI_LOGRADOUROENDERECO, CLI_LOGRADOURONUMERO, CLI_COMPLEMENTO,
                    CLI_EMAIL, CLI_FAX, CLI_RG, CLI_INSCRICAOESTADUAL,
                    CLI_PESSOAFISICAJURIDICA, CLI_DATANASCIMENTO,
                    CLI_DATACADASTRO, CLI_DATAULTIMACOMPRA
                FROM CLIENTE
                ORDER BY CLI_NOME
            """
            
            df = pd.read_sql(query, self.db.get_connection())
            
            if df is None or df.empty:
                self.status_var.set("Nenhum cliente encontrado")
                messagebox.showinfo("Informação", "Nenhum cliente encontrado")
                return
            
            # Armazenar dataframe
            self.df_clientes = df
            
            # Limpar treeview
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Preencher treeview
            for idx, row in df.iterrows():
                codigo = row['CLI_CODIGO']
                nome = row['CLI_NOME'] or '-'
                fantasia = row['CLI_FANTASIA'] or '-'
                
                # Documento (CPF ou CNPJ)
                if row['CLI_PESSOAFISICAJURIDICA'] == 'F':
                    documento = self._formatar_cpf(row['CLI_CPF']) if row['CLI_CPF'] else '-'
                else:
                    documento = self._formatar_cnpj(row['CLI_CNPJ']) if row['CLI_CNPJ'] else '-'
                
                telefone = row['CLI_TELEFONE'] or row['CLI_CELULAR'] or '-'
                cidade = row['CLI_CIDADE'] or '-'
                
                self.tree.insert('', 'end', values=(codigo, nome, fantasia, documento, telefone, cidade))
            
            self.status_var.set(f"{len(df)} cliente(s) encontrado(s)")
            
        except Exception as e:
            self.status_var.set("Erro na busca")
            messagebox.showerror("Erro", f"Erro ao buscar todos os clientes:\n{str(e)}")
    
    def _ordenar_por_coluna(self, col):
        """Ordena a lista ao clicar no cabeçalho da coluna"""
        if not hasattr(self, 'df_clientes') or self.df_clientes is None:
            return
        
        # Mapear colunas da treeview para colunas do dataframe
        col_map = {
            'codigo': 'CLI_CODIGO',
            'nome': 'CLI_NOME',
            'fantasia': 'CLI_FANTASIA',
            'documento': 'CLI_CPF',  # Usar CPF como referência
            'telefone': 'CLI_TELEFONE',
            'cidade': 'CLI_CIDADE'
        }
        
        if col not in col_map:
            return
        
        df_col = col_map[col]
        
        # Alternar ordem ascendente/descendente
        if not hasattr(self, '_sort_reverse'):
            self._sort_reverse = {}
        
        self._sort_reverse[col] = not self._sort_reverse.get(col, False)
        
        # Ordenar dataframe
        self.df_clientes = self.df_clientes.sort_values(
            by=df_col, 
            ascending=not self._sort_reverse[col],
            na_position='last'
        )
        
        # Limpar e repreencher treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for idx, row in self.df_clientes.iterrows():
            codigo = row['CLI_CODIGO']
            nome = row['CLI_NOME'] or '-'
            fantasia = row['CLI_FANTASIA'] or '-'
            
            if row['CLI_PESSOAFISICAJURIDICA'] == 'F':
                documento = self._formatar_cpf(row['CLI_CPF']) if row['CLI_CPF'] else '-'
            else:
                documento = self._formatar_cnpj(row['CLI_CNPJ']) if row['CLI_CNPJ'] else '-'
            
            telefone = row['CLI_TELEFONE'] or row['CLI_CELULAR'] or '-'
            cidade = row['CLI_CIDADE'] or '-'
            
            self.tree.insert('', 'end', values=(codigo, nome, fantasia, documento, telefone, cidade))
    
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
        if not hasattr(self, 'df_clientes') or self.df_clientes is None:
            return
        
        filtro = self.filter_var.get().upper()
        
        # Limpar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Filtrar e preencher
        for idx, row in self.df_clientes.iterrows():
            nome = str(row['CLI_NOME'] or '').upper()
            fantasia = str(row['CLI_FANTASIA'] or '').upper()
            cidade = str(row['CLI_CIDADE'] or '').upper()
            
            if filtro in nome or filtro in fantasia or filtro in cidade:
                codigo = row['CLI_CODIGO']
                nome_display = row['CLI_NOME'] or '-'
                fantasia_display = row['CLI_FANTASIA'] or '-'
                
                if row['CLI_PESSOAFISICAJURIDICA'] == 'F':
                    documento = self._formatar_cpf(row['CLI_CPF']) if row['CLI_CPF'] else '-'
                else:
                    documento = self._formatar_cnpj(row['CLI_CNPJ']) if row['CLI_CNPJ'] else '-'
                
                telefone = row['CLI_TELEFONE'] or row['CLI_CELULAR'] or '-'
                cidade_display = row['CLI_CIDADE'] or '-'
                
                self.tree.insert('', 'end', values=(codigo, nome_display, fantasia_display, documento, telefone, cidade_display))
    
    def _on_cliente_double_click(self, event):
        """Exibe detalhes do cliente ao clicar"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        codigo = item['values'][0]
        
        # Buscar dados completos
        cliente = self.df_clientes[self.df_clientes['CLI_CODIGO'] == codigo].iloc[0]
        
        # Preencher detalhes - usar delete + insert para Entry readonly
        def set_entry(entry, value):
            entry.config(state='normal')
            entry.delete(0, tk.END)
            entry.insert(0, str(value) if value else '-')
            entry.config(state='readonly')
        
        set_entry(self.lbl_codigo, codigo)
        set_entry(self.lbl_nome, cliente['CLI_NOME'] or '-')
        set_entry(self.lbl_fantasia, cliente['CLI_FANTASIA'] or '-')
        
        tipo = "Pessoa Física" if cliente['CLI_PESSOAFISICAJURIDICA'] == 'F' else "Pessoa Jurídica"
        set_entry(self.lbl_tipo, tipo)
        
        # Data de nascimento
        data_nasc = cliente.get('CLI_DATANASCIMENTO')
        if pd.notna(data_nasc):
            set_entry(self.lbl_data_nasc, data_nasc.strftime('%d/%m/%Y') if hasattr(data_nasc, 'strftime') else str(data_nasc))
        else:
            set_entry(self.lbl_data_nasc, '-')
        
        set_entry(self.lbl_cpf, self._formatar_cpf(cliente['CLI_CPF']) if cliente['CLI_CPF'] else '-')
        set_entry(self.lbl_rg, cliente['CLI_RG'] or '-')
        set_entry(self.lbl_cnpj, self._formatar_cnpj(cliente['CLI_CNPJ']) if cliente['CLI_CNPJ'] else '-')
        set_entry(self.lbl_ie, cliente['CLI_INSCRICAOESTADUAL'] or '-')
        
        set_entry(self.lbl_telefone, cliente['CLI_TELEFONE'] or '-')
        set_entry(self.lbl_celular, cliente['CLI_CELULAR'] or '-')
        set_entry(self.lbl_fax, cliente['CLI_FAX'] or '-')
        set_entry(self.lbl_email, cliente['CLI_EMAIL'] or '-')
        
        set_entry(self.lbl_logradouro, cliente['CLI_LOGRADOUROENDERECO'] or '-')
        set_entry(self.lbl_numero, cliente.get('CLI_LOGRADOURONUMERO', '-') or '-')
        set_entry(self.lbl_complemento, cliente.get('CLI_COMPLEMENTO', '-') or '-')
        set_entry(self.lbl_bairro, cliente['CLI_BAIRRO'] or '-')
        set_entry(self.lbl_cep, self._formatar_cep(cliente['CLI_CEP']) if cliente['CLI_CEP'] else '-')
        set_entry(self.lbl_cidade, cliente['CLI_CIDADE'] or '-')
        set_entry(self.lbl_uf, cliente['CLI_UF'] or '-')
        
        # Datas
        data_cad = cliente.get('CLI_DATACADASTRO')
        if pd.notna(data_cad):
            set_entry(self.lbl_data_cadastro, data_cad.strftime('%d/%m/%Y') if hasattr(data_cad, 'strftime') else str(data_cad))
        else:
            set_entry(self.lbl_data_cadastro, '-')
        
        data_ult = cliente.get('CLI_DATAULTIMACOMPRA')
        if pd.notna(data_ult):
            set_entry(self.lbl_ultima_compra, data_ult.strftime('%d/%m/%Y') if hasattr(data_ult, 'strftime') else str(data_ult))
        else:
            set_entry(self.lbl_ultima_compra, '-')
        
        # Observações (Text widget)
        self.txt_observacoes.delete('1.0', tk.END)
        # Nota: campo CLI_HISTORICO é BLOB, não vamos exibir por enquanto
        self.txt_observacoes.insert('1.0', '(Campo de observações disponível para edição futura)')
        
        self.current_cliente_codigo = codigo
    
    def _limpar_detalhes(self):
        """Limpa os detalhes do cliente"""
        def clear_entry(entry):
            entry.config(state='normal')
            entry.delete(0, tk.END)
            entry.insert(0, '-')
            entry.config(state='readonly')
        
        clear_entry(self.lbl_codigo)
        clear_entry(self.lbl_nome)
        clear_entry(self.lbl_fantasia)
        clear_entry(self.lbl_tipo)
        clear_entry(self.lbl_data_nasc)
        clear_entry(self.lbl_cpf)
        clear_entry(self.lbl_rg)
        clear_entry(self.lbl_cnpj)
        clear_entry(self.lbl_ie)
        clear_entry(self.lbl_telefone)
        clear_entry(self.lbl_celular)
        clear_entry(self.lbl_fax)
        clear_entry(self.lbl_email)
        clear_entry(self.lbl_logradouro)
        clear_entry(self.lbl_numero)
        clear_entry(self.lbl_complemento)
        clear_entry(self.lbl_bairro)
        clear_entry(self.lbl_cep)
        clear_entry(self.lbl_cidade)
        clear_entry(self.lbl_uf)
        clear_entry(self.lbl_data_cadastro)
        clear_entry(self.lbl_ultima_compra)
        self.txt_observacoes.delete('1.0', tk.END)
        self.current_cliente_codigo = None
    
    def _formatar_cpf(self, cpf):
        """Formata CPF: 000.000.000-00"""
        if not cpf:
            return '-'
        cpf = str(cpf).strip().replace('.', '').replace('-', '')
        if len(cpf) == 11:
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        return cpf
    
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
