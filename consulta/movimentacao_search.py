import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import sys
import os
import warnings
from datetime import datetime, timedelta

# Suprimir warnings do pandas sobre SQLAlchemy
warnings.filterwarnings('ignore', message='.*SQLAlchemy.*', category=UserWarning)

# Adicionar o diretório pai ao path para importar módulos do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import FirebirdDB
import config

class MovimentacaoSearchWindow:
    def __init__(self, parent):
        self.parent = parent
        self.db = None
        self.df_movimentacoes = None
        
        # Criar janela
        self.window = tk.Toplevel(parent)
        self.window.title("Consulta de Movimentações (Kardex)")
        
        # Tamanho inicial (85% da tela)
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        window_width = int(screen_width * 0.85)
        window_height = int(screen_height * 0.85)
        
        # Centralizar
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Permitir redimensionamento
        self.window.minsize(1200, 700)
        
        # NÃO bloquear janela principal
        self.window.focus_force()
        
        # Conectar ao banco
        self._connect_db()
        
        # Criar interface
        self._create_widgets()
        
        # Ao fechar, desconectar
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _connect_db(self):
        """Conecta ao banco de dados"""
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
        
        # ===== ÁREA DE FILTROS =====
        filter_frame = ttk.LabelFrame(main_frame, text="Filtros", padding="10")
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Linha 1: Período
        row1 = ttk.Frame(filter_frame)
        row1.pack(fill=tk.X, pady=5)
        
        ttk.Label(row1, text="Período:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5)
        
        # Data inicial (padrão: primeiro dia do mês atual)
        hoje = datetime.now()
        primeiro_dia = hoje.replace(day=1)
        
        ttk.Label(row1, text="De:").pack(side=tk.LEFT, padx=(20, 5))
        self.data_ini_var = tk.StringVar(value=primeiro_dia.strftime("%d/%m/%Y"))
        data_ini_entry = ttk.Entry(row1, textvariable=self.data_ini_var, width=12)
        data_ini_entry.pack(side=tk.LEFT, padx=5)
        data_ini_entry.bind('<KeyRelease>', self._formatar_data)
        
        ttk.Label(row1, text="Até:").pack(side=tk.LEFT, padx=(20, 5))
        self.data_fim_var = tk.StringVar(value=hoje.strftime("%d/%m/%Y"))
        data_fim_entry = ttk.Entry(row1, textvariable=self.data_fim_var, width=12)
        data_fim_entry.pack(side=tk.LEFT, padx=5)
        data_fim_entry.bind('<KeyRelease>', self._formatar_data)
        
        # Tipo de movimentação
        ttk.Label(row1, text="Tipo:").pack(side=tk.LEFT, padx=(20, 5))
        self.tipo_var = tk.StringVar(value="TODAS")
        tipo_combo = ttk.Combobox(row1, textvariable=self.tipo_var, width=15, state='readonly')
        tipo_combo['values'] = ('TODAS', 'ENTRADA', 'SAIDA')
        tipo_combo.pack(side=tk.LEFT, padx=5)
        
        # Linha 2: Produto (APENAS CÓDIGO)
        row2 = ttk.Frame(filter_frame)
        row2.pack(fill=tk.X, pady=5)
        
        ttk.Label(row2, text="Produto:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5)
        
        # Campo código
        self.produto_codigo_var = tk.StringVar()
        self.produto_codigo_var.trace('w', self._on_codigo_change)
        produto_entry = ttk.Entry(row2, textvariable=self.produto_codigo_var, width=15)
        produto_entry.pack(side=tk.LEFT, padx=5)
        produto_entry.bind('<Return>', lambda e: self._buscar_movimentacoes())
        
        # Busca por código direto (sem popup)
        
        # Descrição (readonly)
        self.produto_descricao_var = tk.StringVar()
        descricao_entry = ttk.Entry(row2, textvariable=self.produto_descricao_var, width=60, state='readonly')
        descricao_entry.pack(side=tk.LEFT, padx=5)
        
        # Botões
        ttk.Button(row2, text="🔍 Buscar", command=self._buscar_movimentacoes).pack(side=tk.LEFT, padx=5)
        ttk.Button(row2, text="🔄 Limpar", command=self._limpar).pack(side=tk.LEFT, padx=5)
        ttk.Button(row2, text="📊 Gerar PDF", command=self._gerar_pdf).pack(side=tk.LEFT, padx=5)
        ttk.Button(row2, text="📗 Gerar Excel", command=self._gerar_excel).pack(side=tk.LEFT, padx=5)
        
        # ===== LISTA DE MOVIMENTAÇÕES =====
        list_frame = ttk.LabelFrame(main_frame, text="Movimentações", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Treeview
        tree_frame = ttk.Frame(list_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        # Colunas: Data, Código Cliente/Fornecedor, Nome Cliente/Fornecedor, Tipo, Documento, Num Nota, Pedido, Qtde, Valor Unit, Valor Total, Vendedor
        columns = ("data", "cod_entidade", "nome_entidade", "tipo", "documento", 
                   "num_nota", "pedido", "qtde", "valor_unit", "valor_total", "vendedor")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings',
                                 yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Configurar colunas
        self.tree.heading("data", text="Data")
        self.tree.heading("cod_entidade", text="Código")
        self.tree.heading("nome_entidade", text="Descrição")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("documento", text="Tipo Docto")
        self.tree.heading("num_nota", text="Num Nota")
        self.tree.heading("pedido", text="Pedido")
        self.tree.heading("qtde", text="Qtde")
        self.tree.heading("valor_unit", text="Vr Unitário")
        self.tree.heading("valor_total", text="Vr Total")
        self.tree.heading("vendedor", text="Vend")
        
        self.tree.column("data", width=100, anchor=tk.CENTER)
        self.tree.column("cod_entidade", width=80, anchor=tk.W)
        self.tree.column("nome_entidade", width=300, anchor=tk.W)
        self.tree.column("tipo", width=100, anchor=tk.W)
        self.tree.column("documento", width=80, anchor=tk.W)
        self.tree.column("num_nota", width=80, anchor=tk.W)
        self.tree.column("pedido", width=80, anchor=tk.W)
        self.tree.column("qtde", width=70, anchor=tk.E)
        self.tree.column("valor_unit", width=90, anchor=tk.E)
        self.tree.column("valor_total", width=90, anchor=tk.E)
        self.tree.column("vendedor", width=60, anchor=tk.W)
        
        # Bind para ordenação
        for col in columns:
            self.tree.heading(col, command=lambda c=col: self._ordenar_por_coluna(c))
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # ===== TOTALIZADORES =====
        totais_frame = ttk.LabelFrame(main_frame, text="Totalizadores", padding="10")
        totais_frame.pack(fill=tk.X, pady=(0, 10))
        
        totais_grid = ttk.Frame(totais_frame)
        totais_grid.pack()
        
        # Estoque Anterior
        ttk.Label(totais_grid, text="ESTOQUE ANTERIOR==>", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=10)
        self.lbl_estoque_anterior = ttk.Label(totais_grid, text="0,00", font=('Arial', 10))
        self.lbl_estoque_anterior.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Entradas
        ttk.Label(totais_grid, text="ENTRADA=>", font=('Arial', 10, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=10)
        self.lbl_qtde_entradas = ttk.Label(totais_grid, text="0", font=('Arial', 10), foreground='green')
        self.lbl_qtde_entradas.grid(row=0, column=3, sticky=tk.W, padx=5)
        
        # Saídas
        ttk.Label(totais_grid, text="SAIDA=>", font=('Arial', 10, 'bold')).grid(row=0, column=4, sticky=tk.W, padx=10)
        self.lbl_qtde_saidas = ttk.Label(totais_grid, text="0", font=('Arial', 10), foreground='red')
        self.lbl_qtde_saidas.grid(row=0, column=5, sticky=tk.W, padx=5)
        
        # Devoluções
        ttk.Label(totais_grid, text="DEVOLUCAO=>", font=('Arial', 10, 'bold')).grid(row=0, column=6, sticky=tk.W, padx=10)
        self.lbl_qtde_devolucoes = ttk.Label(totais_grid, text="0", font=('Arial', 10))
        self.lbl_qtde_devolucoes.grid(row=0, column=7, sticky=tk.W, padx=5)
        
        # Saldo
        ttk.Label(totais_grid, text="SALDO DO ESTOQUE==>", font=('Arial', 10, 'bold')).grid(row=0, column=8, sticky=tk.W, padx=10)
        self.lbl_saldo = ttk.Label(totais_grid, text="0", font=('Arial', 10, 'bold'), foreground='blue')
        self.lbl_saldo.grid(row=0, column=9, sticky=tk.W, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Pronto - Digite o código do produto e clique em Buscar")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def _on_codigo_change(self, *args):
        """Quando o código muda, busca a descrição do produto"""
        codigo = self.produto_codigo_var.get().strip()
        if not codigo:
            self.produto_descricao_var.set("")
            return
        
        try:
            # Escapar aspas simples
            codigo_escaped = codigo.replace("'", "''")
            query = f"SELECT PROD_DESCRICAOPRODUTO FROM PRODUTO WHERE PROD_CODIGO = '{codigo_escaped}'"
            df = pd.read_sql(query, self.db.get_connection())
            
            if not df.empty:
                self.produto_descricao_var.set(df.iloc[0]['PROD_DESCRICAOPRODUTO'])
            else:
                self.produto_descricao_var.set("(Produto não encontrado)")
        except Exception as e:
            # Silenciosamente ignorar erros durante digitação
            self.produto_descricao_var.set("")
    
    def _formatar_data(self, event):
        """Formata automaticamente a data ao digitar 8 números"""
        widget = event.widget
        texto = widget.get().replace('/', '')
        
        # Se digitou exatamente 8 números, formata
        if len(texto) == 8 and texto.isdigit():
            data_formatada = f"{texto[:2]}/{texto[2:4]}/{texto[4:]}"
            widget.delete(0, tk.END)
            widget.insert(0, data_formatada)
    
    def _abrir_busca_produto(self):
        """Abre popup de busca de produtos - DESABILITADO"""
        # Método desabilitado - usuário prefere digitar código direto
        messagebox.showinfo("Informação", "Digite o código do produto diretamente no campo acima")
        return
        # Criar janela popup
        popup = tk.Toplevel(self.window)
        popup.title("Buscar Produto")
        
        # Tamanho menor
        popup_width = 700
        popup_height = 400
        
        # Centralizar
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        x = (screen_width - popup_width) // 2
        y = (screen_height - popup_height) // 2
        popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")
        
        popup.transient(self.window)
        popup.grab_set()
        
        # Frame de busca
        search_frame = ttk.Frame(popup, padding="10")
        search_frame.pack(fill=tk.X)
        
        ttk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT, padx=5)
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var, width=40)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.focus()
        
        def buscar_produtos():
            termo = search_var.get().strip()
            if not termo:
                messagebox.showwarning("Atenção", "Digite algo para buscar")
                return
            
            try:
                # Escapar caracteres especiais para SQL
                termo_escaped = termo.replace("'", "''")
                
                # Query usando LIKE com escape correto
                query = f"""
                    SELECT PROD_CODIGO, PROD_DESCRICAOPRODUTO
                    FROM PRODUTO
                    WHERE UPPER(PROD_DESCRICAOPRODUTO) LIKE UPPER('%{termo_escaped}%')
                       OR PROD_CODIGO LIKE '%{termo_escaped}%'
                    ORDER BY PROD_DESCRICAOPRODUTO
                    FETCH FIRST 100 ROWS ONLY
                """
                
                # Executar query
                conn = self.db.get_connection()
                df = pd.read_sql(query, conn)
                
                # Limpar tree
                for item in tree.get_children():
                    tree.delete(item)
                
                if df.empty:
                    messagebox.showinfo("Informação", "Nenhum produto encontrado")
                    return
                
                # Preencher
                for idx, row in df.iterrows():
                    tree.insert('', 'end', values=(row['PROD_CODIGO'], row['PROD_DESCRICAOPRODUTO']))
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao buscar produtos:\n{str(e)}")
        
        def selecionar_produto(event=None):
            selection = tree.selection()
            if selection:
                item = tree.item(selection[0])
                codigo = item['values'][0]
                self.produto_codigo_var.set(codigo)
                popup.destroy()
        
        ttk.Button(search_frame, text="🔍 Buscar", command=buscar_produtos).pack(side=tk.LEFT, padx=5)
        search_entry.bind('<Return>', lambda e: buscar_produtos())
        
        # Treeview
        tree_frame = ttk.Frame(popup, padding="10")
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        tree = ttk.Treeview(tree_frame, columns=("codigo", "descricao"), show='headings', yscrollcommand=vsb.set)
        vsb.config(command=tree.yview)
        
        tree.heading("codigo", text="Código")
        tree.heading("descricao", text="Descrição")
        tree.column("codigo", width=100)
        tree.column("descricao", width=550)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree.bind('<Double-1>', selecionar_produto)
        
        # Botões
        btn_frame = ttk.Frame(popup, padding="10")
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="Selecionar", command=selecionar_produto).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=popup.destroy).pack(side=tk.RIGHT, padx=5)
    
    def _validar_datas(self):
        """Valida as datas informadas"""
        try:
            data_ini = datetime.strptime(self.data_ini_var.get(), "%d/%m/%Y")
            data_fim = datetime.strptime(self.data_fim_var.get(), "%d/%m/%Y")
            
            if data_ini > data_fim:
                messagebox.showerror("Erro", "Data inicial não pode ser maior que data final")
                return None, None
            
            return data_ini, data_fim
        except ValueError:
            messagebox.showerror("Erro", "Formato de data inválido. Use DD/MM/AAAA")
            return None, None
    
    def _buscar_movimentacoes(self):
        """Busca movimentações do produto"""
        data_ini, data_fim = self._validar_datas()
        if not data_ini:
            return
        
        codigo = self.produto_codigo_var.get().strip()
        if not codigo:
            messagebox.showwarning("Atenção", "Digite o código do produto")
            return
        
        try:
            self.status_var.set("Buscando movimentações...")
            self.window.update()
            
            # Construir query
            query = self._construir_query(data_ini, data_fim, codigo)
            
            df = pd.read_sql(query, self.db.get_connection())
            
            if df is None or df.empty:
                self.status_var.set("Nenhuma movimentação encontrada")
                messagebox.showinfo("Informação", "Nenhuma movimentação encontrada para este produto no período")
                return
            
            self._exibir_resultados(df)
            
        except Exception as e:
            self.status_var.set("Erro na busca")
            messagebox.showerror("Erro", f"Erro ao buscar movimentações:\n{str(e)}")
    
    def _calcular_estoque_anterior(self, data_ini, codigo):
        """Calcula o estoque anterior ao período consultado"""
        try:
            data_ini_str = data_ini.strftime("%Y-%m-%d")
            codigo_escaped = codigo.replace("'", "''")
            
            # Query para calcular movimentações ANTES da data inicial
            query = f"""
            SELECT 
                COALESCE(SUM(CASE WHEN mov.TIPO LIKE '%ENTRADA%' THEN mov.QTDE ELSE 0 END), 0) AS ENTRADAS,
                COALESCE(SUM(CASE WHEN mov.TIPO LIKE '%SAIDA%' THEN mov.QTDE ELSE 0 END), 0) AS SAIDAS
            FROM (
                -- SAÍDAS (VENDAS)
                SELECT 
                    'SAIDA (VI)' as TIPO,
                    i.PIT_QTDEVENDIDA as QTDE
                FROM PEDITENS i
                INNER JOIN PEDIDO p ON i.PED_NUMEROOPERACAO = p.PED_NUMEROOPERACAO
                WHERE i.PROD_CODIGO = '{codigo_escaped}'
                  AND p.PED_DATAVENDA < '{data_ini_str}'
                
                UNION ALL
                
                -- ENTRADAS (COMPRAS)
                SELECT 
                    'ENTRADA (EE)' as TIPO,
                    i.ENI_QTDEENTRADA as QTDE
                FROM ENTITENS i
                INNER JOIN ENTRADA e ON i.ENT_NUMEROOPERACAO = e.ENT_NUMEROOPERACAO
                WHERE i.PROD_CODIGO = '{codigo_escaped}'
                  AND e.ENT_DATAENTRADA < '{data_ini_str}'
            ) mov
            """
            
            df = pd.read_sql(query, self.db.get_connection())
            
            if df is not None and not df.empty:
                entradas = float(df.iloc[0]['ENTRADAS']) if pd.notna(df.iloc[0]['ENTRADAS']) else 0
                saidas = float(df.iloc[0]['SAIDAS']) if pd.notna(df.iloc[0]['SAIDAS']) else 0
                estoque_anterior = entradas - saidas
                return int(estoque_anterior)
            
            return 0
            
        except Exception as e:
            print(f"Erro ao calcular estoque anterior: {e}")
            return 0
    
    def _construir_query(self, data_ini, data_fim, codigo):
        """Constrói a query SQL usando a query fornecida pelo usuário"""
        data_ini_str = data_ini.strftime("%Y-%m-%d")
        data_fim_str = data_fim.strftime("%Y-%m-%d")
        
        # Escapar código
        codigo_escaped = codigo.replace("'", "''")
        
        # Filtro de tipo
        tipo = self.tipo_var.get()
        filtro_tipo = ""
        if tipo == "ENTRADA":
            filtro_tipo = "AND mov.TIPO LIKE '%ENTRADA%'"
        elif tipo == "SAIDA":
            filtro_tipo = "AND mov.TIPO LIKE '%SAIDA%'"
        
        query = f"""
        SELECT 
            mov.DATA_MOV AS DATA,
            mov.ENTIDADE_COD AS COD_ENTIDADE,
            mov.ENTIDADE_NOME AS NOME_ENTIDADE,
            mov.TIPO,
            mov.TIPO_DOCTO AS DOCUMENTO,
            mov.NUM_NOTA,
            mov.PEDIDO,
            mov.QTDE,
            mov.VALOR_UNIT,
            mov.TOTAL,
            mov.VENDEDOR
        FROM (
            -- SAÍDAS (VENDAS)
            SELECT 
                i.PROD_CODIGO,
                p.PED_DATAVENDA as DATA_MOV,
                'SAIDA (VI)' as TIPO,
                'VI' as TIPO_DOCTO,
                '' as NUM_NOTA,
                CAST(p.PED_NUMEROPEDIDO AS VARCHAR(20)) as PEDIDO,
                p.CLI_CODIGO as ENTIDADE_COD,
                c.CLI_NOME as ENTIDADE_NOME,
                i.PIT_QTDEVENDIDA as QTDE,
                i.PIT_VALORUNITARIO as VALOR_UNIT,
                (i.PIT_QTDEVENDIDA * i.PIT_VALORUNITARIO) as TOTAL,
                '' as VENDEDOR
            FROM PEDITENS i
            JOIN PEDIDO p ON i.PED_NUMEROOPERACAO = p.PED_NUMEROOPERACAO
            LEFT JOIN CLIENTE c ON p.CLI_CODIGO = c.CLI_CODIGO
            WHERE p.PED_DATAVENDA BETWEEN '{data_ini_str}' AND '{data_fim_str}'
              AND i.PROD_CODIGO = '{codigo_escaped}'

            UNION ALL

            -- ENTRADAS (COMPRAS)
            SELECT 
                i.PROD_CODIGO,
                e.ENT_DATAENTRADA as DATA_MOV,
                'ENTRADA (EE)' as TIPO,
                'EE' as TIPO_DOCTO,
                CAST(e.ENT_NUMERONOTAFISCAL AS VARCHAR(20)) as NUM_NOTA,
                CAST(e.ENT_NUMEROOPERACAO AS VARCHAR(20)) as PEDIDO,
                e.FOR_CODIGO as ENTIDADE_COD,
                f.FOR_NOME as ENTIDADE_NOME,
                i.ENI_QTDEENTRADA as QTDE,
                i.ENI_VALORUNITARIO as VALOR_UNIT,
                (i.ENI_QTDEENTRADA * i.ENI_VALORUNITARIO) as TOTAL,
                '' as VENDEDOR
            FROM ENTITENS i
            JOIN ENTRADA e ON i.ENT_NUMEROOPERACAO = e.ENT_NUMEROOPERACAO
            LEFT JOIN FORNECEDOR f ON e.FOR_CODIGO = f.FOR_CODIGO
            WHERE e.ENT_DATAENTRADA BETWEEN '{data_ini_str}' AND '{data_fim_str}'
              AND i.PROD_CODIGO = '{codigo_escaped}'
        ) mov
        WHERE 1=1
        {filtro_tipo}
        ORDER BY mov.DATA_MOV, mov.TIPO
        """
        
        return query
    
    def _exibir_resultados(self, df):
        """Exibe os resultados na treeview e calcula totalizadores"""
        self.df_movimentacoes = df
        
        # Limpar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Preencher treeview
        qtde_entradas = 0
        qtde_saidas = 0
        qtde_devolucoes = 0
        
        for idx, row in df.iterrows():
            data = row['DATA'].strftime('%d/%m/%Y') if pd.notna(row['DATA']) else '-'
            cod_entidade = row['COD_ENTIDADE'] or '-'
            nome_entidade = row['NOME_ENTIDADE'] or '-'
            tipo = row['TIPO']
            documento = row['DOCUMENTO'] or '-'
            num_nota = row['NUM_NOTA'] or '-'
            pedido = row['PEDIDO'] or '-'
            qtde = int(row['QTDE']) if pd.notna(row['QTDE']) else 0
            valor_unit = f"{row['VALOR_UNIT']:.2f}".replace('.', ',') if pd.notna(row['VALOR_UNIT']) else '0,00'
            valor_total = f"{row['TOTAL']:.2f}".replace('.', ',') if pd.notna(row['TOTAL']) else '0,00'
            vendedor = row['VENDEDOR'] or ''
            
            self.tree.insert('', 'end', values=(data, cod_entidade, nome_entidade, tipo, documento,
                                                num_nota, pedido, qtde, valor_unit, valor_total, vendedor))
            
            # Calcular totais
            if 'ENTRADA' in tipo:
                qtde_entradas += qtde
            elif 'SAIDA' in tipo:
                qtde_saidas += qtde
            elif 'DEVOLUCAO' in tipo:
                qtde_devolucoes += qtde
        
        # Calcular estoque anterior
        data_ini, _ = self._validar_datas()
        codigo = self.produto_codigo_var.get().strip()
        estoque_anterior = self._calcular_estoque_anterior(data_ini, codigo)
        
        # Atualizar totalizadores
        saldo = estoque_anterior + qtde_entradas - qtde_saidas
        self.lbl_estoque_anterior.config(text=str(int(estoque_anterior)))
        self.lbl_qtde_entradas.config(text=str(int(qtde_entradas)))
        self.lbl_qtde_saidas.config(text=str(int(qtde_saidas)))
        self.lbl_qtde_devolucoes.config(text=str(int(qtde_devolucoes)))
        self.lbl_saldo.config(text=str(int(saldo)))
        
        self.status_var.set(f"{len(df)} movimentação(ões) encontrada(s)")
    
    def _ordenar_por_coluna(self, col):
        """Ordena a lista ao clicar no cabeçalho da coluna"""
        if not hasattr(self, 'df_movimentacoes') or self.df_movimentacoes is None:
            return
        
        # Mapear colunas
        col_map = {
            'data': 'DATA',
            'cod_entidade': 'COD_ENTIDADE',
            'nome_entidade': 'NOME_ENTIDADE',
            'tipo': 'TIPO',
            'documento': 'DOCUMENTO',
            'num_nota': 'NUM_NOTA',
            'pedido': 'PEDIDO',
            'qtde': 'QTDE',
            'valor_unit': 'VALOR_UNIT',
            'valor_total': 'TOTAL',
            'vendedor': 'VENDEDOR'
        }
        
        if col not in col_map:
            return
        
        df_col = col_map[col]
        
        # Alternar ordem
        if not hasattr(self, '_sort_reverse'):
            self._sort_reverse = {}
        
        self._sort_reverse[col] = not self._sort_reverse.get(col, False)
        
        # Ordenar
        self.df_movimentacoes = self.df_movimentacoes.sort_values(
            by=df_col,
            ascending=not self._sort_reverse[col],
            na_position='last'
        )
        
        # Reexibir
        self._exibir_resultados(self.df_movimentacoes)
    
    def _limpar(self):
        """Limpa filtros e resultados"""
        self.produto_codigo_var.set("")
        self.produto_descricao_var.set("")
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.lbl_estoque_anterior.config(text="0,00")
        self.lbl_qtde_entradas.config(text="0")
        self.lbl_qtde_saidas.config(text="0")
        self.lbl_qtde_devolucoes.config(text="0")
        self.lbl_saldo.config(text="0")
        self.status_var.set("Pronto - Digite o código do produto e clique em Buscar")
    
    def _gerar_pdf(self):
        """Gera relatório PDF"""
        if not hasattr(self, 'df_movimentacoes') or self.df_movimentacoes is None or self.df_movimentacoes.empty:
            messagebox.showwarning("Atenção", "Nenhuma movimentação para gerar relatório")
            return
        
        try:
            # Solicitar local para salvar
            codigo = self.produto_codigo_var.get().strip()
            descricao = self.produto_descricao_var.get().strip()
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=f"kardex_{codigo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )
            
            if not filename:
                return
            
            self.status_var.set("Gerando PDF...")
            self.window.update()
            
            # Importar gerador de PDF
            from relatorios.kardex_pdf import KardexPDFGenerator
            
            # Preparar totalizadores
            totalizadores = {
                'estoque_anterior': int(self.lbl_estoque_anterior.cget('text')),
                'entradas': int(self.lbl_qtde_entradas.cget('text')),
                'saidas': int(self.lbl_qtde_saidas.cget('text')),
                'devolucoes': int(self.lbl_qtde_devolucoes.cget('text')),
                'saldo': int(self.lbl_saldo.cget('text'))
            }
            
            # Obter datas
            data_ini = datetime.strptime(self.data_ini_var.get(), "%d/%m/%Y")
            data_fim = datetime.strptime(self.data_fim_var.get(), "%d/%m/%Y")
            
            # Gerar PDF
            generator = KardexPDFGenerator()
            generator.gerar_pdf(
                filename=filename,
                dados=self.df_movimentacoes,
                produto_codigo=codigo,
                produto_descricao=descricao,
                data_ini=data_ini,
                data_fim=data_fim,
                totalizadores=totalizadores
            )
            
            self.status_var.set(f"PDF gerado: {filename}")
            messagebox.showinfo("Sucesso", f"Relatório PDF gerado com sucesso!\n\n{filename}")
            
        except Exception as e:
            self.status_var.set("Erro ao gerar PDF")
            messagebox.showerror("Erro", f"Erro ao gerar PDF:\n{str(e)}")
    
    def _gerar_excel(self):
        """Gera relatório Excel"""
        if not hasattr(self, 'df_movimentacoes') or self.df_movimentacoes is None or self.df_movimentacoes.empty:
            messagebox.showwarning("Atenção", "Nenhuma movimentação para gerar relatório")
            return
        
        try:
            # Solicitar local para salvar
            codigo = self.produto_codigo_var.get().strip()
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=f"kardex_{codigo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )
            
            if not filename:
                return
            
            self.status_var.set("Gerando Excel...")
            self.window.update()
            
            # Criar Excel
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Preparar dados
                df_export = self.df_movimentacoes.copy()
                df_export['DATA'] = df_export['DATA'].dt.strftime('%d/%m/%Y')
                
                # Renomear colunas
                df_export.columns = ['DATA', 'CODIGO', 'DESCRICAO', 'TIPO', 'TIPO DOCTO',
                                     'NUM NOTA', 'PEDIDO', 'QTDE', 'VR UNITARIO', 'VR TOTAL', 'VEND']
                
                # Escrever dados
                df_export.to_excel(writer, sheet_name='Kardex', index=False)
                
                # Formatar
                worksheet = writer.sheets['Kardex']
                
                # Ajustar largura das colunas
                worksheet.column_dimensions['A'].width = 12
                worksheet.column_dimensions['B'].width = 10
                worksheet.column_dimensions['C'].width = 40
                worksheet.column_dimensions['D'].width = 15
                worksheet.column_dimensions['E'].width = 12
                worksheet.column_dimensions['F'].width = 12
                worksheet.column_dimensions['G'].width = 12
                worksheet.column_dimensions['H'].width = 10
                worksheet.column_dimensions['I'].width = 12
                worksheet.column_dimensions['J'].width = 12
                worksheet.column_dimensions['K'].width = 6
            
            self.status_var.set(f"Excel gerado: {filename}")
            messagebox.showinfo("Sucesso", f"Relatório Excel gerado com sucesso!\n\n{filename}")
            
        except Exception as e:
            self.status_var.set("Erro ao gerar Excel")
            messagebox.showerror("Erro", f"Erro ao gerar Excel:\n{str(e)}")
