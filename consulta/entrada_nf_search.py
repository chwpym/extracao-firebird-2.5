import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import pandas as pd
from datetime import datetime
from core.database import FirebirdDB
import config

class EntradaNFSearchWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Consulta de Entrada de NF")
        self.window.geometry("1500x800")
        
        # Centralizar
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - 750
        y = (self.window.winfo_screenheight() // 2) - 400
        self.window.geometry(f"1500x800+{x}+{y}")
        
        # Manter foco
        self.window.focus_force()
        
        self.db = FirebirdDB(config.DB_CONFIG)
        if not self.db.connect():
            messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados.")
            self.window.destroy()
            return
        
        self.df_entradas = pd.DataFrame()
        self.current_entrada = None
        
        # Variável para tipo de busca
        self.tipo_busca = tk.StringVar(value="data")
        
        self._create_widgets()
        
        # Fechar conexão ao fechar janela
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # === BUSCA ===
        search_frame = ttk.LabelFrame(main_frame, text="Buscar Entrada de NF", padding="10")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Radio buttons para tipo de busca
        radio_frame = ttk.Frame(search_frame)
        radio_frame.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))
        
        ttk.Radiobutton(radio_frame, text="Por Data", variable=self.tipo_busca, 
                       value="data", command=self._toggle_search_fields).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(radio_frame, text="Por Pedido", variable=self.tipo_busca, 
                       value="pedido", command=self._toggle_search_fields).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(radio_frame, text="Por Nota Fiscal", variable=self.tipo_busca, 
                       value="nf", command=self._toggle_search_fields).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(radio_frame, text="Por Fornecedor", variable=self.tipo_busca, 
                       value="fornecedor", command=self._toggle_search_fields).pack(side=tk.LEFT, padx=5)
        
        # Campos de busca
        fields_frame = ttk.Frame(search_frame)
        fields_frame.grid(row=1, column=0, columnspan=4, sticky="ew", pady=5)
        
        # Data
        self.lbl_data_inicio = ttk.Label(fields_frame, text="Data Início:")
        self.txt_data_inicio = ttk.Entry(fields_frame, width=12)
        self.txt_data_inicio.insert(0, datetime.now().replace(day=1).strftime("%d/%m/%Y"))
        self.txt_data_inicio.bind('<KeyRelease>', lambda e: self._auto_format_date(self.txt_data_inicio))
        
        self.lbl_data_fim = ttk.Label(fields_frame, text="Data Fim:")
        self.txt_data_fim = ttk.Entry(fields_frame, width=12)
        self.txt_data_fim.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.txt_data_fim.bind('<KeyRelease>', lambda e: self._auto_format_date(self.txt_data_fim))
        
        # Pedido
        self.lbl_pedido = ttk.Label(fields_frame, text="Nº Pedido:")
        self.txt_pedido = ttk.Entry(fields_frame, width=15)
        self.txt_pedido.bind('<Return>', lambda e: self._buscar())
        
        # Nota Fiscal
        self.lbl_nf = ttk.Label(fields_frame, text="Nº Nota Fiscal:")
        self.txt_nf = ttk.Entry(fields_frame, width=15)
        self.txt_nf.bind('<Return>', lambda e: self._buscar())
        
        # Fornecedor
        self.lbl_fornecedor = ttk.Label(fields_frame, text="Fornecedor:")
        self.txt_fornecedor = ttk.Entry(fields_frame, width=30)
        self.txt_fornecedor.bind('<Return>', lambda e: self._buscar())
        
        # Data para fornecedor
        self.lbl_forn_data_inicio = ttk.Label(fields_frame, text="Data Início:")
        self.txt_forn_data_inicio = ttk.Entry(fields_frame, width=12)
        self.txt_forn_data_inicio.insert(0, datetime.now().replace(day=1).strftime("%d/%m/%Y"))
        self.txt_forn_data_inicio.bind('<KeyRelease>', lambda e: self._auto_format_date(self.txt_forn_data_inicio))
        
        self.lbl_forn_data_fim = ttk.Label(fields_frame, text="Data Fim:")
        self.txt_forn_data_fim = ttk.Entry(fields_frame, width=12)
        self.txt_forn_data_fim.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.txt_forn_data_fim.bind('<KeyRelease>', lambda e: self._auto_format_date(self.txt_forn_data_fim))
        
        # Botões ao lado
        self.btn_buscar = ttk.Button(fields_frame, text="🔍 Buscar", command=self._buscar)
        self.btn_limpar = ttk.Button(fields_frame, text="🗑️ Limpar", command=self._limpar)
        
        # Mostrar campos iniciais
        self._toggle_search_fields()
        
        # === TABELA DE ENTRADAS ===
        table_frame = ttk.LabelFrame(main_frame, text="Entradas Encontradas", padding="5")
        table_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 10))  # expand=False para altura fixa
        
        # Scrollbars
        scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        
        # Treeview com altura reduzida
        columns = ('num_op', 'nf', 'cod_forn', 'fornecedor', 'data_entrada', 'tipo', 'frete', 'ipi', 'icms', 'status', 'pedido', 'desconto', 'total')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings',
                                 yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set, height=8)  # height=8 para reduzir
        
        # Configurar colunas
        self.tree.heading('num_op', text='Operação')
        self.tree.heading('nf', text='Nota Fiscal')
        self.tree.heading('cod_forn', text='Código')
        self.tree.heading('fornecedor', text='Fornecedor')
        self.tree.heading('data_entrada', text='Data Entrada')
        self.tree.heading('tipo', text='Tipo')
        self.tree.heading('frete', text='Vr Frete')
        self.tree.heading('ipi', text='Vr IPI')
        self.tree.heading('icms', text='Vr ICMS')
        self.tree.heading('status', text='Status')
        self.tree.heading('pedido', text='Pedido')
        self.tree.heading('desconto', text='Desconto')
        self.tree.heading('total', text='Vr Total')
        
        self.tree.column('num_op', width=80, anchor='center')
        self.tree.column('nf', width=100, anchor='center')
        self.tree.column('cod_forn', width=60, anchor='center')
        self.tree.column('fornecedor', width=220, anchor='w')
        self.tree.column('data_entrada', width=100, anchor='center')
        self.tree.column('tipo', width=50, anchor='center')
        self.tree.column('frete', width=80, anchor='e')
        self.tree.column('ipi', width=80, anchor='e')
        self.tree.column('icms', width=80, anchor='e')
        self.tree.column('status', width=60, anchor='center')
        self.tree.column('pedido', width=80, anchor='center')
        self.tree.column('desconto', width=80, anchor='e')
        self.tree.column('total', width=100, anchor='e')
        
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        scroll_y.grid(row=0, column=1, sticky='ns')
        scroll_x.grid(row=1, column=0, sticky='ew')
        
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        
        # Bind de seleção e ordenação
        self.tree.bind('<<TreeviewSelect>>', self._on_entrada_select)
        
        # Adicionar ordenação por coluna
        for col in columns:
            self.tree.heading(col, command=lambda c=col: self._sort_column(c, False))
        
        # === DETALHES E ITENS ===
        details_frame = ttk.Frame(main_frame)
        details_frame.pack(fill=tk.BOTH, expand=True)
        
        # Detalhes da Entrada (450px de largura)
        info_frame = ttk.LabelFrame(details_frame, text="Detalhes da Entrada", padding="10")
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 5))
        info_frame.config(width=450)  # Largura aumentada para 450px para evitar quebra de linha
        
        self.txt_detalhes = ScrolledText(info_frame, height=10, width=50, font=("Arial", 9), state=tk.DISABLED)  # width=50
        self.txt_detalhes.pack(fill=tk.BOTH, expand=True)
        
        # Itens da Entrada (espaço restante)
        itens_frame = ttk.LabelFrame(details_frame, text="Itens da Entrada", padding="5")
        itens_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        scroll_itens_y = ttk.Scrollbar(itens_frame, orient=tk.VERTICAL)
        scroll_itens_x = ttk.Scrollbar(itens_frame, orient=tk.HORIZONTAL)
        
        columns_itens = ('codigo', 'descricao', 'qtde', 'vl_unit', 'ipi', 'reajuste', 'vl_venda', 'ncm', 'vl_total')
        self.tree_itens = ttk.Treeview(itens_frame, columns=columns_itens, show='headings',
                                       yscrollcommand=scroll_itens_y.set, 
                                       xscrollcommand=scroll_itens_x.set, height=8)
        
        self.tree_itens.heading('codigo', text='Código')
        self.tree_itens.heading('descricao', text='Descrição')
        self.tree_itens.heading('qtde', text='Qtde')
        self.tree_itens.heading('vl_unit', text='Vl. Unit.')
        self.tree_itens.heading('ipi', text='% IPI')
        self.tree_itens.heading('reajuste', text='Reajuste')
        self.tree_itens.heading('vl_venda', text='Vl Venda')
        self.tree_itens.heading('ncm', text='NCM')
        self.tree_itens.heading('vl_total', text='Vl. Total')
        
        self.tree_itens.column('codigo', width=80, anchor='center')
        self.tree_itens.column('descricao', width=300, anchor='w')
        self.tree_itens.column('qtde', width=70, anchor='center')
        self.tree_itens.column('vl_unit', width=90, anchor='e')
        self.tree_itens.column('ipi', width=70, anchor='center')
        self.tree_itens.column('reajuste', width=90, anchor='e')
        self.tree_itens.column('vl_venda', width=90, anchor='e')
        self.tree_itens.column('ncm', width=90, anchor='center')
        self.tree_itens.column('vl_total', width=100, anchor='e')
        
        scroll_itens_y.config(command=self.tree_itens.yview)
        scroll_itens_x.config(command=self.tree_itens.xview)
        
        self.tree_itens.grid(row=0, column=0, sticky='nsew')
        scroll_itens_y.grid(row=0, column=1, sticky='ns')
        scroll_itens_x.grid(row=1, column=0, sticky='ew')
        
        itens_frame.rowconfigure(0, weight=1)
        itens_frame.columnconfigure(0, weight=1)
    
    def _toggle_search_fields(self):
        """Mostra/esconde campos conforme tipo de busca selecionado"""
        # Esconder todos
        self.lbl_data_inicio.grid_forget()
        self.txt_data_inicio.grid_forget()
        self.lbl_data_fim.grid_forget()
        self.txt_data_fim.grid_forget()
        self.lbl_pedido.grid_forget()
        self.txt_pedido.grid_forget()
        self.lbl_nf.grid_forget()
        self.txt_nf.grid_forget()
        self.lbl_fornecedor.grid_forget()
        self.txt_fornecedor.grid_forget()
        self.lbl_forn_data_inicio.grid_forget()
        self.txt_forn_data_inicio.grid_forget()
        self.lbl_forn_data_fim.grid_forget()
        self.txt_forn_data_fim.grid_forget()
        self.btn_buscar.grid_forget()
        self.btn_limpar.grid_forget()
        
        # Mostrar conforme seleção
        tipo = self.tipo_busca.get()
        
        if tipo == "data":
            self.lbl_data_inicio.grid(row=0, column=0, sticky="w", padx=5)
            self.txt_data_inicio.grid(row=0, column=1, sticky="w", padx=5)
            self.lbl_data_fim.grid(row=0, column=2, sticky="w", padx=5)
            self.txt_data_fim.grid(row=0, column=3, sticky="w", padx=5)
            self.btn_buscar.grid(row=0, column=4, padx=5)
            self.btn_limpar.grid(row=0, column=5, padx=5)
        elif tipo == "pedido":
            self.lbl_pedido.grid(row=0, column=0, sticky="w", padx=5)
            self.txt_pedido.grid(row=0, column=1, sticky="w", padx=5)
            self.btn_buscar.grid(row=0, column=2, padx=5)
            self.btn_limpar.grid(row=0, column=3, padx=5)
        elif tipo == "nf":
            self.lbl_nf.grid(row=0, column=0, sticky="w", padx=5)
            self.txt_nf.grid(row=0, column=1, sticky="w", padx=5)
            self.btn_buscar.grid(row=0, column=2, padx=5)
            self.btn_limpar.grid(row=0, column=3, padx=5)
        elif tipo == "fornecedor":
            self.lbl_fornecedor.grid(row=0, column=0, sticky="w", padx=5)
            self.txt_fornecedor.grid(row=0, column=1, sticky="w", padx=5)
            self.lbl_forn_data_inicio.grid(row=0, column=2, sticky="w", padx=5)
            self.txt_forn_data_inicio.grid(row=0, column=3, sticky="w", padx=5)
            self.lbl_forn_data_fim.grid(row=0, column=4, sticky="w", padx=5)
            self.txt_forn_data_fim.grid(row=0, column=5, sticky="w", padx=5)
            self.btn_buscar.grid(row=0, column=6, padx=5)
            self.btn_limpar.grid(row=0, column=7, padx=5)
    
    def _auto_format_date(self, entry_widget):
        """Formata automaticamente a data enquanto o usuário digita"""
        # Pegar valor atual e posição do cursor
        current_value = entry_widget.get()
        cursor_pos = entry_widget.index(tk.INSERT)
        
        # Se está vazio, não fazer nada
        if not current_value:
            return
        
        # Remover barras para processar
        value_only_digits = current_value.replace('/', '')
        
        # Limitar a 8 dígitos
        if len(value_only_digits) > 8:
            value_only_digits = value_only_digits[:8]
        
        # Remover caracteres não numéricos
        value_only_digits = ''.join(filter(str.isdigit, value_only_digits))
        
        # Se não tem dígitos, limpar
        if not value_only_digits:
            entry_widget.delete(0, tk.END)
            return
        
        # Formatar com barras
        formatted = ''
        for i, char in enumerate(value_only_digits):
            if i == 2 or i == 4:
                formatted += '/'
            formatted += char
        
        # Só atualizar se mudou
        if formatted != current_value:
            # Contar dígitos antes do cursor (ignorando barras)
            digits_before = len(current_value[:cursor_pos].replace('/', ''))
            
            # Atualizar campo
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, formatted)
            
            # Calcular nova posição do cursor
            # Posição = número de dígitos + número de barras antes dessa posição
            new_pos = digits_before
            if digits_before > 2:
                new_pos += 1  # Barra após DD
            if digits_before > 4:
                new_pos += 1  # Barra após MM
            
            # Garantir limites
            new_pos = min(new_pos, len(formatted))
            
            # Restaurar cursor
            try:
                entry_widget.icursor(new_pos)
            except:
                pass
    
    def _buscar(self):
        """Busca entradas conforme critérios"""
        tipo = self.tipo_busca.get()
        
        # Construir query base
        query = """
            SELECT 
                E.ENT_NUMEROOPERACAO,
                E.ENT_NUMERONOTAFISCAL,
                F.FOR_CODIGO,
                F.FOR_NOME,
                E.ENT_DATAENTRADA,
                E.ENT_TIPODEENTRADA,
                E.ENT_VALORFRETE,
                E.ENT_VALORIPI,
                E.ENT_VALORICMS,
                E.ENT_STATUSNOTA,
                E.ENT_NUMEROPEDIDO,
                E.ENT_VALORDESCONTO,
                E.ENT_VALORTOTALNOTA,
                E.ENT_DATAEMISSAO,
                E.ENT_OBSERVACAO,
                E.FOR_CODIGO AS ENT_FOR_CODIGO
            FROM ENTRADA E
            LEFT JOIN FORNECEDOR F ON E.FOR_CODIGO = F.FOR_CODIGO
            WHERE 1=1
        """
        
        params = []
        
        # Adicionar filtros conforme tipo de busca
        if tipo == "data":
            data_ini = self.txt_data_inicio.get().strip()
            data_fim = self.txt_data_fim.get().strip()
            
            if data_ini and data_fim:
                try:
                    dt_ini = datetime.strptime(data_ini, "%d/%m/%Y").strftime("%Y-%m-%d")
                    dt_fim = datetime.strptime(data_fim, "%d/%m/%Y").strftime("%Y-%m-%d")
                    query += " AND CAST(E.ENT_DATAENTRADA AS DATE) BETWEEN ? AND ?"
                    params.extend([dt_ini, dt_fim])
                except ValueError:
                    messagebox.showerror("Erro", "Formato de data inválido! Use DD/MM/AAAA")
                    self.window.focus_force()
                    return
        
        elif tipo == "pedido":
            pedido = self.txt_pedido.get().strip()
            if pedido:
                query += " AND E.ENT_NUMEROPEDIDO = ?"
                params.append(int(pedido))
        
        elif tipo == "nf":
            nf = self.txt_nf.get().strip()
            if nf:
                query += " AND E.ENT_NUMERONOTAFISCAL = ?"
                params.append(int(nf))
        
        elif tipo == "fornecedor":
            fornecedor = self.txt_fornecedor.get().strip()
            data_ini = self.txt_forn_data_inicio.get().strip()
            data_fim = self.txt_forn_data_fim.get().strip()
            
            if fornecedor:
                # Verificar se é numérico (busca por código) ou texto (busca por nome)
                if fornecedor.isdigit():
                    # Busca por código
                    query += " AND F.FOR_CODIGO = ?"
                    params.append(int(fornecedor))
                else:
                    # Dividir o texto em palavras e buscar cada uma separadamente no nome
                    palavras = fornecedor.upper().split()
                    for palavra in palavras:
                        if palavra:  # Ignorar strings vazias
                            query += " AND UPPER(F.FOR_NOME) CONTAINING ?"
                            params.append(palavra)
            
            if data_ini and data_fim:
                try:
                    dt_ini = datetime.strptime(data_ini, "%d/%m/%Y").strftime("%Y-%m-%d")
                    dt_fim = datetime.strptime(data_fim, "%d/%m/%Y").strftime("%Y-%m-%d")
                    query += " AND CAST(E.ENT_DATAENTRADA AS DATE) BETWEEN ? AND ?"
                    params.extend([dt_ini, dt_fim])
                except ValueError:
                    messagebox.showerror("Erro", "Formato de data inválido! Use DD/MM/AAAA")
                    self.window.focus_force()
                    return
        
        query += " ORDER BY E.ENT_DATAENTRADA DESC"
        
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Converter para DataFrame
            columns = ['ENT_NUMEROOPERACAO', 'ENT_NUMERONOTAFISCAL', 'FOR_CODIGO', 'FOR_NOME', 'ENT_DATAENTRADA',
                      'ENT_TIPODEENTRADA', 'ENT_VALORFRETE', 'ENT_VALORIPI', 'ENT_VALORICMS',
                      'ENT_STATUSNOTA', 'ENT_NUMEROPEDIDO', 'ENT_VALORDESCONTO', 'ENT_VALORTOTALNOTA',
                      'ENT_DATAEMISSAO', 'ENT_OBSERVACAO', 'ENT_FOR_CODIGO']
            self.df_entradas = pd.DataFrame(rows, columns=columns)
            
            self._atualizar_tabela()
            self.window.focus_force()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar entradas:\n{str(e)}")
            self.window.focus_force()
    
    def _limpar(self):
        """Limpa os campos de busca e resultados"""
        # Limpar campos
        self.txt_data_inicio.delete(0, tk.END)
        self.txt_data_fim.delete(0, tk.END)
        self.txt_pedido.delete(0, tk.END)
        self.txt_nf.delete(0, tk.END)
        self.txt_fornecedor.delete(0, tk.END)
        self.txt_forn_data_inicio.delete(0, tk.END)
        self.txt_forn_data_fim.delete(0, tk.END)
        
        # Resetar datas padrão
        self.txt_data_inicio.insert(0, datetime.now().replace(day=1).strftime("%d/%m/%Y"))
        self.txt_data_fim.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.txt_forn_data_inicio.insert(0, datetime.now().replace(day=1).strftime("%d/%m/%Y"))
        self.txt_forn_data_fim.insert(0, datetime.now().strftime("%d/%m/%Y"))
        
        # Limpar tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Limpar detalhes
        self.txt_detalhes.config(state=tk.NORMAL)
        self.txt_detalhes.delete(1.0, tk.END)
        self.txt_detalhes.config(state=tk.DISABLED)
        
        # Limpar itens
        for item in self.tree_itens.get_children():
            self.tree_itens.delete(item)
        
        # Limpar DataFrame
        self.df_entradas = pd.DataFrame()
        self.current_entrada = None
    
    def _sort_column(self, col, reverse):
        """Ordena a tabela por coluna"""
        if self.df_entradas.empty:
            return
        
        col_map = {
            'num_op': 'ENT_NUMEROOPERACAO',
            'nf': 'ENT_NUMERONOTAFISCAL',
            'cod_forn': 'FOR_CODIGO',
            'fornecedor': 'FOR_NOME',
            'data_entrada': 'ENT_DATAENTRADA',
            'tipo': 'ENT_TIPODEENTRADA',
            'frete': 'ENT_VALORFRETE',
            'ipi': 'ENT_VALORIPI',
            'icms': 'ENT_VALORICMS',
            'status': 'ENT_STATUSNOTA',
            'pedido': 'ENT_NUMEROPEDIDO',
            'desconto': 'ENT_VALORDESCONTO',
            'total': 'ENT_VALORTOTALNOTA'
        }
        
        df_col = col_map.get(col)
        if not df_col:
            return
        
        self.df_entradas = self.df_entradas.sort_values(by=df_col, ascending=not reverse)
        
        # Atualizar tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for idx, row in self.df_entradas.iterrows():
            data_entrada = row['ENT_DATAENTRADA'].strftime("%d/%m/%Y") if pd.notna(row['ENT_DATAENTRADA']) else ""
            fornecedor = row['FOR_NOME'] if pd.notna(row['FOR_NOME']) else ""
            tipo = row['ENT_TIPODEENTRADA'] if pd.notna(row['ENT_TIPODEENTRADA']) else ""
            status = row['ENT_STATUSNOTA'] if pd.notna(row['ENT_STATUSNOTA']) else ""
            
            frete = f"R$ {row['ENT_VALORFRETE']:,.2f}" if pd.notna(row['ENT_VALORFRETE']) else "R$ 0,00"
            ipi = f"R$ {row['ENT_VALORIPI']:,.2f}" if pd.notna(row['ENT_VALORIPI']) else "R$ 0,00"
            icms = f"R$ {row['ENT_VALORICMS']:,.2f}" if pd.notna(row['ENT_VALORICMS']) else "R$ 0,00"
            desconto = f"R$ {row['ENT_VALORDESCONTO']:,.2f}" if pd.notna(row['ENT_VALORDESCONTO']) else "R$ 0,00"
            total = f"R$ {row['ENT_VALORTOTALNOTA']:,.2f}" if pd.notna(row['ENT_VALORTOTALNOTA']) else "R$ 0,00"
            
            self.tree.insert('', tk.END, values=(
                row['ENT_NUMEROOPERACAO'],
                row['ENT_NUMERONOTAFISCAL'],
                row['FOR_CODIGO'] if pd.notna(row['FOR_CODIGO']) else "",
                fornecedor,
                data_entrada,
                tipo,
                frete,
                ipi,
                icms,
                status,
                row['ENT_NUMEROPEDIDO'],
                desconto,
                total
            ), tags=(str(idx),))
        
        self.tree.heading(col, command=lambda: self._sort_column(col, not reverse))
    
    def _atualizar_tabela(self):
        """Atualiza a tabela com as entradas"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if self.df_entradas.empty:
            messagebox.showinfo("Aviso", "Nenhuma entrada encontrada.")
            self.window.focus_force()
            return
        
        for idx, row in self.df_entradas.iterrows():
            data_entrada = row['ENT_DATAENTRADA'].strftime("%d/%m/%Y") if pd.notna(row['ENT_DATAENTRADA']) else ""
            fornecedor = row['FOR_NOME'] if pd.notna(row['FOR_NOME']) else ""
            tipo = row['ENT_TIPODEENTRADA'] if pd.notna(row['ENT_TIPODEENTRADA']) else ""
            status = row['ENT_STATUSNOTA'] if pd.notna(row['ENT_STATUSNOTA']) else ""
            
            frete = f"R$ {row['ENT_VALORFRETE']:,.2f}" if pd.notna(row['ENT_VALORFRETE']) else "R$ 0,00"
            ipi = f"R$ {row['ENT_VALORIPI']:,.2f}" if pd.notna(row['ENT_VALORIPI']) else "R$ 0,00"
            icms = f"R$ {row['ENT_VALORICMS']:,.2f}" if pd.notna(row['ENT_VALORICMS']) else "R$ 0,00"
            desconto = f"R$ {row['ENT_VALORDESCONTO']:,.2f}" if pd.notna(row['ENT_VALORDESCONTO']) else "R$ 0,00"
            total = f"R$ {row['ENT_VALORTOTALNOTA']:,.2f}" if pd.notna(row['ENT_VALORTOTALNOTA']) else "R$ 0,00"
            
            self.tree.insert('', tk.END, values=(
                row['ENT_NUMEROOPERACAO'],
                row['ENT_NUMERONOTAFISCAL'],
                row['FOR_CODIGO'] if pd.notna(row['FOR_CODIGO']) else "",
                fornecedor,
                data_entrada,
                tipo,
                frete,
                ipi,
                icms,
                status,
                row['ENT_NUMEROPEDIDO'],
                desconto,
                total
            ), tags=(str(idx),))
        
        # Só mostrar mensagem se não for busca específica
        if self.tipo_busca.get() == "data":
            messagebox.showinfo("Sucesso", f"{len(self.df_entradas)} entrada(s) encontrada(s).")
            self.window.focus_force()
    
    def _on_entrada_select(self, event):
        """Quando seleciona uma entrada"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        idx = int(item['tags'][0])
        entrada = self.df_entradas.iloc[idx]
        
        self.current_entrada = entrada
        
        # Atualizar detalhes
        self._exibir_detalhes(entrada)
        
        # Carregar itens
        self._carregar_itens(entrada['ENT_NUMEROOPERACAO'])
    
    def _exibir_detalhes(self, entrada):
        """Exibe detalhes da entrada"""
        self.txt_detalhes.config(state=tk.NORMAL)
        self.txt_detalhes.delete(1.0, tk.END)
        
        # Formatar valores
        vr_frete = f"R$ {entrada['ENT_VALORFRETE']:,.2f}" if pd.notna(entrada['ENT_VALORFRETE']) else "R$ 0,00"
        vr_ipi = f"R$ {entrada['ENT_VALORIPI']:,.2f}" if pd.notna(entrada['ENT_VALORIPI']) else "R$ 0,00"
        vr_icms = f"R$ {entrada['ENT_VALORICMS']:,.2f}" if pd.notna(entrada['ENT_VALORICMS']) else "R$ 0,00"
        vr_desconto = f"R$ {entrada['ENT_VALORDESCONTO']:,.2f}" if pd.notna(entrada['ENT_VALORDESCONTO']) else "R$ 0,00"
        vr_total = f"R$ {entrada['ENT_VALORTOTALNOTA']:,.2f}" if pd.notna(entrada['ENT_VALORTOTALNOTA']) else "R$ 0,00"
        
        detalhes = f"""Nº Operação: {entrada['ENT_NUMEROOPERACAO']}
Nº Nota Fiscal: {entrada['ENT_NUMERONOTAFISCAL']}
Nº Pedido: {entrada['ENT_NUMEROPEDIDO'] if pd.notna(entrada['ENT_NUMEROPEDIDO']) else 'N/A'}

Fornecedor: {entrada['FOR_NOME'] if pd.notna(entrada['FOR_NOME']) else 'Não informado'}

Data Emissão: {entrada['ENT_DATAEMISSAO'].strftime('%d/%m/%Y') if pd.notna(entrada['ENT_DATAEMISSAO']) else ''}
Data Entrada: {entrada['ENT_DATAENTRADA'].strftime('%d/%m/%Y') if pd.notna(entrada['ENT_DATAENTRADA']) else ''}

Tipo: {entrada['ENT_TIPODEENTRADA'] if pd.notna(entrada['ENT_TIPODEENTRADA']) else ''}
Status: {entrada['ENT_STATUSNOTA'] if pd.notna(entrada['ENT_STATUSNOTA']) else ''}

Valor Frete: {vr_frete}
Valor IPI: {vr_ipi}
Valor ICMS: {vr_icms}
Valor Desconto: {vr_desconto}
Valor Total: {vr_total}

Observação: {entrada['ENT_OBSERVACAO'] if pd.notna(entrada['ENT_OBSERVACAO']) else ''}
"""
        
        self.txt_detalhes.insert(1.0, detalhes)
        self.txt_detalhes.config(state=tk.DISABLED)
    
    def _carregar_itens(self, num_operacao):
        """Carrega itens da entrada"""
        for item in self.tree_itens.get_children():
            self.tree_itens.delete(item)
        
        try:
            query = """
                SELECT 
                    I.PROD_CODIGO,
                    P.PROD_DESCRICAOPRODUTO,
                    I.ENI_QTDEENTRADA,
                    I.ENI_VALORUNITARIO,
                    I.ENI_PERCENTUALIPI,
                    I.ENI_PERCACR,
                    I.ENI_VALORVENDA,
                    I.ENI_NCMPRODUTO,
                    (I.ENI_QTDEENTRADA * I.ENI_VALORUNITARIO) AS TOTAL
                FROM ENTITENS I
                LEFT JOIN PRODUTO P ON I.PROD_CODIGO = P.PROD_CODIGO
                WHERE I.ENT_NUMEROOPERACAO = ?
            """
            
            cursor = self.db.get_connection().cursor()
            cursor.execute(query, [num_operacao])
            rows = cursor.fetchall()
            
            if rows:
                for row in rows:
                    codigo = row[0] if row[0] else ""
                    descricao = row[1] if row[1] else "Produto não encontrado"
                    qtde = f"{row[2]:,.2f}" if row[2] else "0"
                    vl_unit = f"R$ {row[3]:,.2f}" if row[3] else "R$ 0,00"
                    ipi = f"{row[4]:.2f}%" if row[4] else "0%"
                    reajuste = f"{row[5]:.2f}%" if row[5] else "0%"
                    vl_venda = f"R$ {row[6]:,.2f}" if row[6] else "R$ 0,00"
                    ncm = row[7] if row[7] else ""
                    vl_total = f"R$ {row[8]:,.2f}" if row[8] else "R$ 0,00"
                    
                    self.tree_itens.insert('', tk.END, values=(codigo, descricao, qtde, vl_unit, ipi, reajuste, vl_venda, ncm, vl_total))
            
        except Exception as e:
            print(f"Erro ao carregar itens: {e}")
    
    def _on_closing(self):
        """Fecha conexão e janela"""
        self.db.close()
        self.window.destroy()
