import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import pandas as pd
import sys
import os

# Adicionar o diretório pai ao path para importar módulos do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import FirebirdDB
import config

class ProdutoListagemWindow:
    def __init__(self, parent):
        self.parent = parent
        self.db = None
        self.current_produto_codigo = None
        
        # Criar janela
        self.window = tk.Toplevel(parent)
        self.window.title("Consulta de Produtos (Rápida)")
        
        # Tela cheia
        self.window.state('zoomed')  # Maximizado no Windows
        
        # Manter janela sempre visível
        self.window.transient(parent)
        self.window.grab_set()
        self.window.focus_force()
        
        # Conectar ao banco (conexão persistente)
        self._connect_db()
        
        # Criar interface
        self._create_widgets()
        
        # Ao fechar, desconectar
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _center_window(self, width, height):
        """Centraliza a janela na tela"""
        self.window.update_idletasks()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = ((screen_height - height) // 2) - 30
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
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
        search_frame = ttk.LabelFrame(main_frame, text="Buscar Produto", padding="10")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        # Campo de busca
        ttk.Label(search_frame, text="Descrição ou Aplicação:").pack(side=tk.LEFT, padx=5)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=80)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind('<Return>', lambda e: self._buscar_produto())
        search_entry.focus()
        
        # Checkbox busca por código interno
        self.busca_codigo_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(search_frame, text="🔢 Busca por Código Interno", 
                       variable=self.busca_codigo_var).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(search_frame, text="🔍 Buscar", command=self._buscar_produto).pack(side=tk.LEFT, padx=5)
        
        # ===== LISTA DE PRODUTOS =====
        produtos_frame = ttk.LabelFrame(main_frame, text="Produtos Encontrados", padding="10")
        produtos_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Filtro rápido
        filter_frame = ttk.Frame(produtos_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Linha 1: Filtro de texto e estoque
        filter_line1 = ttk.Frame(filter_frame)
        filter_line1.pack(fill=tk.X, pady=2)
        
        ttk.Label(filter_line1, text="Filtrar lista:").pack(side=tk.LEFT, padx=5)
        self.filter_var = tk.StringVar()
        self.filter_var.trace('w', lambda *args: self._aplicar_filtro())
        filter_entry = ttk.Entry(filter_line1, textvariable=self.filter_var, width=40)
        filter_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_line1, text="Limpar", command=lambda: self.filter_var.set("")).pack(side=tk.LEFT, padx=5)
        
        # Separador
        ttk.Separator(filter_line1, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Filtros de estoque
        ttk.Label(filter_line1, text="Estoque:").pack(side=tk.LEFT, padx=5)
        
        self.check_estoque_positivo = tk.BooleanVar(value=True)
        ttk.Checkbutton(filter_line1, text="Positivo (≥1)", variable=self.check_estoque_positivo,
                       command=self._aplicar_filtro).pack(side=tk.LEFT, padx=2)
        
        self.check_estoque_zerado = tk.BooleanVar(value=True)
        ttk.Checkbutton(filter_line1, text="Zerado (=0)", variable=self.check_estoque_zerado,
                       command=self._aplicar_filtro).pack(side=tk.LEFT, padx=2)
        
        self.check_estoque_negativo = tk.BooleanVar(value=True)
        ttk.Checkbutton(filter_line1, text="Negativo (<0)", variable=self.check_estoque_negativo,
                       command=self._aplicar_filtro).pack(side=tk.LEFT, padx=2)
        
        # Linha 2: Filtros adicionais
        filter_line2 = ttk.Frame(filter_frame)
        filter_line2.pack(fill=tk.X, pady=2)
        
        ttk.Label(filter_line2, text="Outros filtros:").pack(side=tk.LEFT, padx=5)
        
        self.check_apenas_ativos = tk.BooleanVar(value=False)
        ttk.Checkbutton(filter_line2, text="Apenas Ativos", variable=self.check_apenas_ativos,
                       command=self._aplicar_filtro).pack(side=tk.LEFT, padx=2)
        
        self.check_abaixo_minimo = tk.BooleanVar(value=False)
        ttk.Checkbutton(filter_line2, text="Abaixo do Mínimo", variable=self.check_abaixo_minimo,
                       command=self._aplicar_filtro).pack(side=tk.LEFT, padx=2)
        
        self.check_sem_preco = tk.BooleanVar(value=False)
        ttk.Checkbutton(filter_line2, text="Sem Preço", variable=self.check_sem_preco,
                       command=self._aplicar_filtro).pack(side=tk.LEFT, padx=2)
        
        self.check_sem_aplicacao = tk.BooleanVar(value=False)
        ttk.Checkbutton(filter_line2, text="Sem Aplicação", variable=self.check_sem_aplicacao,
                       command=self._aplicar_filtro).pack(side=tk.LEFT, padx=2)
        
        # Separador
        ttk.Separator(filter_line2, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Botão "Mostrar Todos"
        ttk.Button(filter_line2, text="🔄 Mostrar Todos", 
                  command=self._resetar_filtros).pack(side=tk.LEFT, padx=5)
        
        # Tabela de produtos
        table_frame = ttk.Frame(produtos_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        hsb = ttk.Scrollbar(table_frame, orient="horizontal")
        
        self.tree = ttk.Treeview(table_frame,
                                 columns=("codigo", "cod_fab", "descricao", "estoque", "vl_venda", 
                                         "localiz", "ult_compra", "cod_orig", "cod_barras", "marca"),
                                 show="headings",
                                 yscrollcommand=vsb.set,
                                 xscrollcommand=hsb.set,
                                 height=8)
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Colunas com ordenação
        self.tree.heading("codigo", text="Cód. Prod. ▲", command=lambda: self._ordenar_coluna("codigo"))
        self.tree.heading("cod_fab", text="Cód. Fab.", command=lambda: self._ordenar_coluna("cod_fab"))
        self.tree.heading("descricao", text="Descrição do Produto", command=lambda: self._ordenar_coluna("descricao"))
        self.tree.heading("estoque", text="Estoque", command=lambda: self._ordenar_coluna("estoque"))
        self.tree.heading("vl_venda", text="Vl. Venda", command=lambda: self._ordenar_coluna("vl_venda"))
        self.tree.heading("localiz", text="Localiz.", command=lambda: self._ordenar_coluna("localiz"))
        self.tree.heading("ult_compra", text="Últ. Compra", command=lambda: self._ordenar_coluna("ult_compra"))
        self.tree.heading("cod_orig", text="Cód. Orig.", command=lambda: self._ordenar_coluna("cod_orig"))
        self.tree.heading("cod_barras", text="Cód. Barras", command=lambda: self._ordenar_coluna("cod_barras"))
        self.tree.heading("marca", text="Marca", command=lambda: self._ordenar_coluna("marca"))
        
        self.tree.column("codigo", width=70, anchor=tk.CENTER)
        self.tree.column("cod_fab", width=80, anchor=tk.W)
        self.tree.column("descricao", width=300, anchor=tk.W)
        self.tree.column("estoque", width=60, anchor=tk.CENTER)
        self.tree.column("vl_venda", width=80, anchor=tk.E)
        self.tree.column("localiz", width=70, anchor=tk.W)
        self.tree.column("ult_compra", width=90, anchor=tk.CENTER)
        self.tree.column("cod_orig", width=90, anchor=tk.W)
        self.tree.column("cod_barras", width=110, anchor=tk.W)
        self.tree.column("marca", width=100, anchor=tk.W)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Evento de seleção
        self.tree.bind('<<TreeviewSelect>>', self._on_produto_select)
        
        # Variáveis para ordenação
        self.sort_column = "codigo"
        self.sort_reverse = False
        
        # ===== DETALHES DO PRODUTO (IMAGEM + APLICAÇÃO) =====
        detalhes_frame = ttk.Frame(main_frame)
        detalhes_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Imagem do produto
        img_frame = ttk.LabelFrame(detalhes_frame, text="Imagem", padding="10")
        img_frame.pack(side=tk.LEFT, padx=(0, 10), fill=tk.Y)
        
        # Forçar tamanho fixo do frame (não propagar tamanho dos filhos)
        img_frame.pack_propagate(False)
        img_frame.config(width=180, height=200)
        
        # Label com tamanho fixo para imagem
        self.img_label = tk.Label(img_frame, text="[Sem\nImagem]", 
                                  width=150, height=150,  # Tamanho fixo em pixels
                                  bg="lightgray", cursor="hand2",
                                  relief=tk.SUNKEN, bd=2)
        self.img_label.pack(padx=5, pady=5, expand=True)
        self.img_label.bind('<Button-1>', self._abrir_imagem_grande)
        
        # Armazenar imagem original para zoom
        self.imagem_original = None
        
        # Aplicação
        aplicacao_frame = ttk.LabelFrame(detalhes_frame, text="Aplicação", padding="10")
        aplicacao_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.txt_aplicacao = ScrolledText(aplicacao_frame, height=8, wrap=tk.WORD, font=("Arial", 9))
        self.txt_aplicacao.pack(fill=tk.BOTH, expand=True)
        self.txt_aplicacao.config(state=tk.DISABLED)
        
        # Similares
        similares_frame = ttk.LabelFrame(detalhes_frame, text="Produtos Similares", padding="10")
        similares_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Tabela de similares
        sim_table_frame = ttk.Frame(similares_frame)
        sim_table_frame.pack(fill=tk.BOTH, expand=True)
        
        vsb_sim = ttk.Scrollbar(sim_table_frame, orient="vertical")
        hsb_sim = ttk.Scrollbar(sim_table_frame, orient="horizontal")
        
        self.tree_similares = ttk.Treeview(sim_table_frame,
                                          columns=("codigo", "cod_fab", "descricao", "estoque", "preco", "marca"),
                                          show="headings",
                                          yscrollcommand=vsb_sim.set,
                                          xscrollcommand=hsb_sim.set,
                                          height=4)
        
        vsb_sim.config(command=self.tree_similares.yview)
        hsb_sim.config(command=self.tree_similares.xview)
        
        # Colunas
        self.tree_similares.heading("codigo", text="Código")
        self.tree_similares.heading("cod_fab", text="Cód. Fab.")
        self.tree_similares.heading("descricao", text="Descrição")
        self.tree_similares.heading("estoque", text="Estoque")
        self.tree_similares.heading("preco", text="Preço")
        self.tree_similares.heading("marca", text="Marca")
        
        self.tree_similares.column("codigo", width=60, anchor=tk.CENTER)
        self.tree_similares.column("cod_fab", width=80, anchor=tk.W)
        self.tree_similares.column("descricao", width=250, anchor=tk.W)
        self.tree_similares.column("estoque", width=60, anchor=tk.CENTER)
        self.tree_similares.column("preco", width=80, anchor=tk.E)
        self.tree_similares.column("marca", width=80, anchor=tk.W)
        
        self.tree_similares.grid(row=0, column=0, sticky="nsew")
        vsb_sim.grid(row=0, column=1, sticky="ns")
        hsb_sim.grid(row=1, column=0, sticky="ew")
        
        sim_table_frame.grid_rowconfigure(0, weight=1)
        sim_table_frame.grid_columnconfigure(0, weight=1)
        
        # Duplo clique para carregar similar
        self.tree_similares.bind('<Double-1>', self._carregar_similar)
        
        
        # Botão fechar
        ttk.Button(main_frame, text="Fechar", command=self._on_close).pack(pady=10)
    
    def _buscar_produto(self):
        """Busca produtos no banco de dados"""
        termo_busca = self.search_var.get().strip()
        
        # Permitir busca vazia para listar tudo (sem histórico = rápido!)
        
        # Limpar tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            # Verificar se é busca por código interno
            if self.busca_codigo_var.get() and termo_busca:
                # Busca APENAS por código (muito mais rápida!)
                where_clause = f"CAST(PROD_CODIGO AS VARCHAR(50)) = '{termo_busca}'"
            elif termo_busca:
                # Busca normal (código, descrição e aplicação)
                termos = termo_busca.upper().split()
                
                # Construir condições WHERE para cada termo
                condicoes = []
                for termo in termos:
                    condicoes.append(f"""(
                    UPPER(PROD_DESCRICAOPRODUTO) LIKE '%{termo}%' OR
                    UPPER(PROD_APLICACAO) LIKE '%{termo}%'
                )""")
                
                # Juntar com AND para que todos os termos sejam encontrados
                where_clause = " AND ".join(condicoes)
                
                # Adicionar busca por código exato
                if termo_busca.isdigit():
                    where_clause = f"(CAST(PROD_CODIGO AS VARCHAR(50)) = '{termo_busca}') OR ({where_clause})"
            else:
                # Busca vazia = buscar tudo
                where_clause = "1=1"
            
            # Query SIMPLIFICADA - SEM histórico de compras (muito mais rápida!)
            # Sem LIMIT - lista TODOS os produtos
            query = f"""
            SELECT 
                PROD_CODIGO,
                PROD_CODIGOFABRICANTE,
                PROD_DESCRICAOPRODUTO,
                PROD_QTDEESTOQUEFISICO,
                PROD_PRECOAVISTA,
                PROD_LOCALIZACAOPECA,
                PROD_CODIGOBARRA,
                PROD_MARCA,
                PROD_CODIGOORIGINAL,
                PROD_REFERENCIA,
                PROD_MINIMO,
                PROD_APLICACAO
            FROM PRODUTO
            WHERE {where_clause}
            ORDER BY PROD_DESCRICAOPRODUTO
            """
            
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning)
                df = pd.read_sql(query, self.db.get_connection())
            
            if df.empty:
                messagebox.showinfo("Não encontrado", "Nenhum produto encontrado")
                self._limpar_dados()
                return
            
            # Preencher tabela (SEM última compra)
            for idx, row in df.iterrows():
                self.tree.insert('', 'end', values=(
                    row['PROD_CODIGO'],
                    row.get('PROD_CODIGOFABRICANTE', '-') or '-',
                    row['PROD_DESCRICAOPRODUTO'],
                    row.get('PROD_QTDEESTOQUEFISICO', 0) or 0,
                    f"R$ {row.get('PROD_PRECOAVISTA', 0) or 0:,.2f}",
                    row.get('PROD_LOCALIZACAOPECA', '-') or '-',
                    '-',  # Sem última compra (listagem rápida)
                    row.get('PROD_CODIGOORIGINAL', '-') or '-',
                    row.get('PROD_CODIGOBARRA', '-') or '-',
                    row.get('PROD_MARCA', '-') or '-'
                ), tags=(str(row['PROD_CODIGO']),))  # Usar código como tag
            
            # Armazenar DataFrame para uso posterior
            self.df_produtos = df
            

            
            # Selecionar primeiro item automaticamente
            if len(self.tree.get_children()) > 0:
                first_item = self.tree.get_children()[0]
                self.tree.selection_set(first_item)
                self.tree.focus(first_item)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar:\n{str(e)}")
    
    def _on_produto_select(self, event):
        """Quando seleciona um produto na lista"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        prod_codigo = int(item['tags'][0])  # Pegar código da tag
        
        # Buscar produto no DataFrame pelo código
        produto = self.df_produtos[self.df_produtos['PROD_CODIGO'] == prod_codigo].iloc[0]
        
        self.current_produto_codigo = produto['PROD_CODIGO']
        
        # Atualizar aplicação
        self._exibir_aplicacao(produto.get('PROD_APLICACAO', ''))
        
        # Carregar imagem
        self._carregar_imagem(produto['PROD_CODIGO'])
        
        # Atualizar similares
        self._atualizar_similares(produto.get('PROD_REFERENCIA', ''))
    
    def _atualizar_similares(self, referencia):
        """Carrega produtos similares com a mesma referência"""
        # Limpar tabela
        for item in self.tree_similares.get_children():
            self.tree_similares.delete(item)
        
        if not referencia or pd.isna(referencia) or str(referencia).strip() == '':
            return
        
        try:
            # Buscar produtos com mesma referência (exceto o atual)
            query = f"""
            SELECT 
                PROD_CODIGO,
                PROD_CODIGOFABRICANTE,
                PROD_DESCRICAOPRODUTO,
                PROD_QTDEESTOQUEFISICO,
                PROD_PRECOAVISTA,
                PROD_MARCA
            FROM PRODUTO
            WHERE PROD_REFERENCIA = '{referencia}'
            AND PROD_CODIGO != {self.current_produto_codigo}
            ORDER BY PROD_MARCA, PROD_DESCRICAOPRODUTO
            """
            
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning)
                df = pd.read_sql(query, self.db.get_connection())
            
            # Preencher tabela
            for idx, row in df.iterrows():
                self.tree_similares.insert('', 'end', values=(
                    row['PROD_CODIGO'],
                    row.get('PROD_CODIGOFABRICANTE', '-') or '-',
                    row['PROD_DESCRICAOPRODUTO'],
                    row.get('PROD_QTDEESTOQUEFISICO', 0) or 0,
                    f"R$ {row.get('PROD_PRECOAVISTA', 0) or 0:,.2f}",
                    row.get('PROD_MARCA', '-') or '-'
                ))
                
        except Exception as e:
            print(f"Erro ao carregar similares: {e}")
    
    def _carregar_similar(self, event):
        """Carrega o produto similar selecionado na tela principal"""
        selection = self.tree_similares.selection()
        if not selection:
            return
        
        item = self.tree_similares.item(selection[0])
        codigo_similar = item['values'][0]
        
        # Buscar o produto similar no DataFrame principal
        if hasattr(self, 'df_produtos'):
            produto_similar = self.df_produtos[self.df_produtos['PROD_CODIGO'] == codigo_similar]
            
            if not produto_similar.empty:
                # Encontrar e selecionar na árvore principal
                for tree_item in self.tree.get_children():
                    tree_values = self.tree.item(tree_item)['values']
                    if tree_values[0] == codigo_similar:
                        self.tree.selection_set(tree_item)
                        self.tree.focus(tree_item)
                        self.tree.see(tree_item)
                        return
                
                # Se não estiver na lista atual, buscar no banco
                self.search_var.set(str(codigo_similar))
                self._buscar_produto()
    
    def _aplicar_filtro(self):
        """Filtra a lista de produtos"""
        filtro = self.filter_var.get().upper()
        
        if not hasattr(self, 'df_produtos'):
            return
        
        # Limpar tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Preencher com produtos filtrados
        for idx, row in self.df_produtos.iterrows():
            codigo = str(row['PROD_CODIGO'])
            descricao = str(row['PROD_DESCRICAOPRODUTO']).upper()
            marca = str(row.get('PROD_MARCA', '')).upper()
            estoque = row.get('PROD_QTDEESTOQUEFISICO', 0) or 0
            minimo = row.get('PROD_MINIMO', 0) or 0
            preco = row.get('PROD_PRECOAVISTA', 0) or 0
            aplicacao = str(row.get('PROD_APLICACAO', '')).strip()
            
            # Filtro de texto
            if filtro and not (filtro in codigo or filtro in descricao or filtro in marca):
                continue
            
            # Filtro de estoque
            if estoque >= 1 and not self.check_estoque_positivo.get():
                continue
            if estoque == 0 and not self.check_estoque_zerado.get():
                continue
            if estoque < 0 and not self.check_estoque_negativo.get():
                continue
            
            # Filtro: Apenas Ativos (assumindo que produtos sem PROD_ATIVO são ativos)
            if self.check_apenas_ativos.get():
                # Se o campo existir, verificar; senão, considerar ativo
                if 'PROD_ATIVO' in row and row['PROD_ATIVO'] != 'T':
                    continue
            
            # Filtro: Abaixo do Mínimo
            if self.check_abaixo_minimo.get():
                if estoque >= minimo:
                    continue
            
            # Filtro: Sem Preço
            if self.check_sem_preco.get():
                if preco > 0:
                    continue
            
            # Filtro: Sem Aplicação
            if self.check_sem_aplicacao.get():
                if aplicacao:
                    continue
            
            # Adicionar à tabela (SEM última compra)
            self.tree.insert('', 'end', values=(
                row['PROD_CODIGO'],
                row.get('PROD_CODIGOFABRICANTE', '-') or '-',
                row['PROD_DESCRICAOPRODUTO'],
                estoque,
                f"R$ {preco:,.2f}",
                row.get('PROD_LOCALIZACAOPECA', '-') or '-',
                '-',  # Sem última compra (listagem rápida)
                row.get('PROD_CODIGOORIGINAL', '-') or '-',
                row.get('PROD_CODIGOBARRA', '-') or '-',
                row.get('PROD_MARCA', '-') or '-'
            ), tags=(str(row['PROD_CODIGO']),))  # Usar código como tag
    
    def _resetar_filtros(self):
        """Reseta todos os filtros para o padrão"""
        # Limpar filtro de texto
        self.filter_var.set("")
        
        # Resetar checkboxes de estoque (todos marcados)
        self.check_estoque_positivo.set(True)
        self.check_estoque_zerado.set(True)
        self.check_estoque_negativo.set(True)
        
        # Resetar outros filtros (todos desmarcados)
        self.check_apenas_ativos.set(False)
        self.check_abaixo_minimo.set(False)
        self.check_sem_preco.set(False)
        self.check_sem_aplicacao.set(False)
        
        # Reaplicar filtros
        self._aplicar_filtro()
    
    def _ordenar_coluna(self, col):
        """Ordena a tabela pela coluna clicada"""
        if not hasattr(self, 'df_produtos'):
            return
        
        # Alternar direção se clicar na mesma coluna
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False
        
        # Mapear colunas para campos do DataFrame
        col_map = {
            "codigo": "PROD_CODIGO",
            "cod_fab": "PROD_CODIGOFABRICANTE",
            "descricao": "PROD_DESCRICAOPRODUTO",
            "estoque": "PROD_QTDEESTOQUEFISICO",
            "vl_venda": "PROD_PRECOAVISTA",
            "localiz": "PROD_LOCALIZACAOPECA",
            "ult_compra": "ULT_COMPRA",
            "cod_orig": "PROD_REFERENCIA",
            "cod_barras": "PROD_CODIGOBARRA",
            "marca": "PROD_MARCA"
        }
        
        # Ordenar DataFrame
        df_field = col_map[col]
        self.df_produtos = self.df_produtos.sort_values(by=df_field, ascending=not self.sort_reverse)
        
        # Atualizar indicador visual
        for c in ["codigo", "cod_fab", "descricao", "estoque", "vl_venda", "localiz", "ult_compra", "cod_orig", "cod_barras", "marca"]:
            text = {
                "codigo": "Cód. Prod.",
                "cod_fab": "Cód. Fab.",
                "descricao": "Descrição do Produto",
                "estoque": "Estoque",
                "vl_venda": "Vl. Venda",
                "localiz": "Localiz.",
                "ult_compra": "Últ. Compra",
                "cod_orig": "Cód. Orig.",
                "cod_barras": "Cód. Barras",
                "marca": "Marca"
            }[c]
            
            if c == col:
                text += " ▼" if self.sort_reverse else " ▲"
            
            self.tree.heading(c, text=text)
        
        # Recarregar tabela
        self._aplicar_filtro()
    
    def _carregar_imagem(self, codigo_produto):
        """Carrega a imagem do produto do banco"""
        try:
            from PIL import Image, ImageTk
            from io import BytesIO
            
            # Buscar imagem do banco
            query = f"SELECT PROD_FOTO FROM PRODUTO WHERE PROD_CODIGO = {codigo_produto}"
            
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning)
                df = pd.read_sql(query, self.db.get_connection())
            
            if df.empty or pd.isna(df.iloc[0]['PROD_FOTO']):
                self.img_label.config(text="[Sem\nImagem]", image='', compound=tk.CENTER)
                self.imagem_original = None
                return
            
            foto_blob = df.iloc[0]['PROD_FOTO']
            
            # Se for BlobReader do fdb (Firebird)
            if hasattr(foto_blob, 'read'):
                blob_data = foto_blob.read()
                if blob_data:
                    # Armazenar imagem original para zoom
                    self.imagem_original = Image.open(BytesIO(blob_data))
                    
                    # Criar thumbnail para exibição (150x150 max)
                    img_thumb = self.imagem_original.copy()
                    img_thumb.thumbnail((150, 150))
                    photo = ImageTk.PhotoImage(img_thumb)
                    self.img_label.config(image=photo, text="", compound=tk.CENTER)
                    self.img_label.image = photo
                else:
                    self.img_label.config(text="[BLOB\nVazio]", image='', compound=tk.CENTER)
                    self.imagem_original = None
            else:
                self.img_label.config(text="[Formato\nInválido]", image='', compound=tk.CENTER)
                self.imagem_original = None
                
        except Exception as e:
            print(f"Erro ao carregar imagem: {e}")
            self.img_label.config(text="[Erro ao\nCarregar]", image='', compound=tk.CENTER)
            self.imagem_original = None
    
    def _abrir_imagem_grande(self, event):
        """Abre a imagem em tamanho maior em uma nova janela"""
        if not self.imagem_original:
            return
        
        try:
            from PIL import ImageTk
            
            # Criar janela popup
            img_window = tk.Toplevel(self.window)
            img_window.title("Imagem do Produto")
            
            # Redimensionar imagem mantendo proporção (max 800x600)
            img_display = self.imagem_original.copy()
            img_display.thumbnail((800, 600))
            
            # Ajustar tamanho da janela
            width, height = img_display.size
            img_window.geometry(f"{width+20}x{height+20}")
            
            # Centralizar
            img_window.update_idletasks()
            screen_width = img_window.winfo_screenwidth()
            screen_height = img_window.winfo_screenheight()
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            img_window.geometry(f"{width+20}x{height+20}+{x}+{y}")
            
            img_window.transient(self.window)
            
            # Exibir imagem
            photo = ImageTk.PhotoImage(img_display)
            label = ttk.Label(img_window, image=photo)
            label.image = photo  # Manter referência
            label.pack(padx=10, pady=10)
            
            # Fechar ao clicar
            label.bind('<Button-1>', lambda e: img_window.destroy())
            img_window.bind('<Escape>', lambda e: img_window.destroy())
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir imagem:\n{str(e)}")
    
    def _exibir_aplicacao(self, aplicacao):
        """Exibe a aplicação do produto"""
        self.txt_aplicacao.config(state=tk.NORMAL)
        self.txt_aplicacao.delete(1.0, tk.END)
        self.txt_aplicacao.insert(1.0, aplicacao or "Sem aplicação cadastrada")
        self.txt_aplicacao.config(state=tk.DISABLED)
    
    def _atualizar_historico(self):
        """Atualiza o histórico de compras"""
        if not self.current_produto_codigo:
            return
        
        # Limpar tabela
        for item in self.tree_historico.get_children():
            self.tree_historico.delete(item)
        
        try:
            # Determinar limite
            qtd = self.qtd_compras_var.get()
            if qtd == "Todas":
                limit_clause = ""
            else:
                limit_clause = f"FIRST {qtd}"
            
            # Buscar histórico
            query_historico = f"""
            SELECT {limit_clause}
                e.ENT_DATAENTRADA,
                f.FOR_NOME,
                ei.ENI_QTDEENTRADA,
                ei.ENI_VALORUNITARIO,
                e.ENT_NUMERONOTAFISCAL
            FROM ENTITENS ei
            JOIN ENTRADA e ON ei.ENT_NUMEROOPERACAO = e.ENT_NUMEROOPERACAO
            LEFT JOIN FORNECEDOR f ON e.FOR_CODIGO = f.FOR_CODIGO
            WHERE ei.PROD_CODIGO = {self.current_produto_codigo}
            ORDER BY e.ENT_DATAENTRADA DESC
            """
            
            # Buscar preço médio
            query_preco = f"""
            SELECT AVG(ei.ENI_VALORUNITARIO) as PRECO_MEDIO
            FROM (
                SELECT {limit_clause} ei.ENI_VALORUNITARIO
                FROM ENTITENS ei
                JOIN ENTRADA e ON ei.ENT_NUMEROOPERACAO = e.ENT_NUMEROOPERACAO
                WHERE ei.PROD_CODIGO = {self.current_produto_codigo}
                AND ei.ENI_VALORUNITARIO > 0
                ORDER BY e.ENT_DATAENTRADA DESC
            ) ei
            """
            
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning)
                df_historico = pd.read_sql(query_historico, self.db.get_connection())
                df_preco_medio = pd.read_sql(query_preco, self.db.get_connection())
            
            # Exibir histórico
            for _, row in df_historico.iterrows():
                data = row['ENT_DATAENTRADA'].strftime('%d/%m/%Y') if pd.notna(row['ENT_DATAENTRADA']) else '-'
                fornecedor = row['FOR_NOME'] or '-'
                qtd = int(row['ENI_QTDEENTRADA']) if pd.notna(row['ENI_QTDEENTRADA']) else 0
                preco = row['ENI_VALORUNITARIO'] or 0
                nf = row['ENT_NUMERONOTAFISCAL'] or '-'
                
                self.tree_historico.insert('', 'end', values=(
                    data,
                    fornecedor,
                    qtd,
                    f"R$ {preco:,.2f}",
                    nf
                ))
            
            # Exibir preço médio
            if not df_preco_medio.empty and pd.notna(df_preco_medio.iloc[0]['PRECO_MEDIO']):
                preco_medio = df_preco_medio.iloc[0]['PRECO_MEDIO']
                self.lbl_preco_medio.config(text=f"Preço Médio: R$ {preco_medio:,.2f}")
            else:
                self.lbl_preco_medio.config(text="Preço Médio: R$ 0,00")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar histórico:\n{str(e)}")
    
    def _limpar_dados(self):
        """Limpa os dados exibidos"""
        self.current_produto_codigo = None
        # Limpar aplicação
        self.txt_aplicacao.config(state=tk.NORMAL)
        self.txt_aplicacao.delete(1.0, tk.END)
        self.txt_aplicacao.config(state=tk.DISABLED)
        
        # Limpar preço médio
        self.lbl_preco_medio.config(text="Preço Médio: R$ 0,00")
        
        # Limpar histórico
        for item in self.tree_historico.get_children():
            self.tree_historico.delete(item)
        
        # Limpar similares
        for item in self.tree_similares.get_children():
            self.tree_similares.delete(item)
        
        # Limpar imagem
        self.img_label.config(text="[Sem\nImagem]", image='', compound=tk.CENTER)
        self.imagem_original = None
