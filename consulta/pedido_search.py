import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import pandas as pd
from datetime import datetime
from core.database import FirebirdDB
import config

class PedidoSearchWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Consulta de Vendas (Pedidos)")
        self.window.geometry("1400x800")
        
        # Centralizar
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - 700
        y = (self.window.winfo_screenheight() // 2) - 400
        self.window.geometry(f"1400x800+{x}+{y}")
        
        # Manter foco
        self.window.focus_force()
        
        self.db = FirebirdDB(config.DB_CONFIG)
        if not self.db.connect():
            messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados.")
            self.window.destroy()
            return
        
        self.df_pedidos = pd.DataFrame()
        self.current_pedido = None
        
        self._create_widgets()
        
        # Fechar conexão ao fechar janela
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # === BUSCA (COMPACTA) ===
        search_frame = ttk.LabelFrame(main_frame, text="Buscar Pedido", padding="10")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Tudo em uma linha
        ttk.Label(search_frame, text="Nº Operação:").grid(row=0, column=0, sticky="w", padx=5)
        self.txt_num_operacao = ttk.Entry(search_frame, width=15)
        self.txt_num_operacao.grid(row=0, column=1, sticky="w", padx=5)
        self.txt_num_operacao.bind('<Return>', lambda e: self._buscar())
        
        ttk.Label(search_frame, text="Data Início:").grid(row=0, column=2, sticky="w", padx=(15, 5))
        self.txt_data_inicio = ttk.Entry(search_frame, width=12)
        self.txt_data_inicio.grid(row=0, column=3, sticky="w", padx=5)
        self.txt_data_inicio.insert(0, datetime.now().replace(day=1).strftime("%d/%m/%Y"))
        self.txt_data_inicio.bind('<KeyRelease>', lambda e: self._auto_format_date(self.txt_data_inicio))
        
        ttk.Label(search_frame, text="Data Fim:").grid(row=0, column=4, sticky="w", padx=5)
        self.txt_data_fim = ttk.Entry(search_frame, width=12)
        self.txt_data_fim.grid(row=0, column=5, sticky="w", padx=5)
        self.txt_data_fim.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.txt_data_fim.bind('<KeyRelease>', lambda e: self._auto_format_date(self.txt_data_fim))
        
        ttk.Label(search_frame, text="Cliente:").grid(row=0, column=6, sticky="w", padx=(15, 5))
        self.txt_cliente = ttk.Entry(search_frame, width=30)
        self.txt_cliente.grid(row=0, column=7, sticky="ew", padx=5)
        self.txt_cliente.bind('<Return>', lambda e: self._buscar())
        
        # Botões
        ttk.Button(search_frame, text="🔍 Buscar", command=self._buscar).grid(row=0, column=8, padx=5)
        ttk.Button(search_frame, text="🗑️ Limpar", command=self._limpar).grid(row=0, column=9, padx=5)
        
        search_frame.columnconfigure(7, weight=1)
        
        # === TABELA DE PEDIDOS ===
        table_frame = ttk.LabelFrame(main_frame, text="Pedidos Encontrados", padding="5")
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Scrollbars
        scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        
        # Treeview
        columns = ('num_op', 'num_ped', 'data', 'cliente', 'vendedor', 'placa', 'veiculo', 'vr_total', 'desconto', 'vr_liquido')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', 
                                 yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        # Configurar colunas
        self.tree.heading('num_op', text='Nº Operação')
        self.tree.heading('num_ped', text='Nº Pedido')
        self.tree.heading('data', text='Data Venda')
        self.tree.heading('cliente', text='Cliente')
        self.tree.heading('vendedor', text='Vendedor')
        self.tree.heading('placa', text='Placa')
        self.tree.heading('veiculo', text='Veículo')
        self.tree.heading('vr_total', text='Vr. Total')
        self.tree.heading('desconto', text='Desconto')
        self.tree.heading('vr_liquido', text='Vr. Líquido')
        
        self.tree.column('num_op', width=100, anchor='center')
        self.tree.column('num_ped', width=100, anchor='center')
        self.tree.column('data', width=100, anchor='center')
        self.tree.column('cliente', width=250, anchor='w')
        self.tree.column('vendedor', width=200, anchor='w')
        self.tree.column('placa', width=100, anchor='center')
        self.tree.column('veiculo', width=150, anchor='w')
        self.tree.column('vr_total', width=100, anchor='e')
        self.tree.column('desconto', width=100, anchor='e')
        self.tree.column('vr_liquido', width=100, anchor='e')
        
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        scroll_y.grid(row=0, column=1, sticky='ns')
        scroll_x.grid(row=1, column=0, sticky='ew')
        
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        
        # Bind de seleção e ordenação
        self.tree.bind('<<TreeviewSelect>>', self._on_pedido_select)
        
        # Adicionar ordenação por coluna
        for col in columns:
            self.tree.heading(col, command=lambda c=col: self._sort_column(c, False))
        
        # === DETALHES E ITENS ===
        details_frame = ttk.Frame(main_frame)
        details_frame.pack(fill=tk.BOTH, expand=True)
        
        # Detalhes do Pedido
        info_frame = ttk.LabelFrame(details_frame, text="Detalhes do Pedido", padding="10")
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.txt_detalhes = ScrolledText(info_frame, height=8, font=("Arial", 9), state=tk.DISABLED)
        self.txt_detalhes.pack(fill=tk.BOTH, expand=True)
        
        # Itens do Pedido
        itens_frame = ttk.LabelFrame(details_frame, text="Itens do Pedido", padding="5")
        itens_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        scroll_itens_y = ttk.Scrollbar(itens_frame, orient=tk.VERTICAL)
        
        columns_itens = ('codigo', 'descricao', 'qtde', 'vr_unit', 'vr_total')
        self.tree_itens = ttk.Treeview(itens_frame, columns=columns_itens, show='headings',
                                       yscrollcommand=scroll_itens_y.set, height=8)
        
        self.tree_itens.heading('codigo', text='Código')
        self.tree_itens.heading('descricao', text='Descrição')
        self.tree_itens.heading('qtde', text='Qtde')
        self.tree_itens.heading('vr_unit', text='Vr. Unit.')
        self.tree_itens.heading('vr_total', text='Vr. Total')
        
        self.tree_itens.column('codigo', width=80, anchor='center')
        self.tree_itens.column('descricao', width=300, anchor='w')
        self.tree_itens.column('qtde', width=80, anchor='center')
        self.tree_itens.column('vr_unit', width=100, anchor='e')
        self.tree_itens.column('vr_total', width=100, anchor='e')
        
        scroll_itens_y.config(command=self.tree_itens.yview)
        
        self.tree_itens.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_itens_y.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _buscar(self):
        """Busca pedidos conforme critérios"""
        num_op = self.txt_num_operacao.get().strip()
        data_ini = self.txt_data_inicio.get().strip()
        data_fim = self.txt_data_fim.get().strip()
        cliente = self.txt_cliente.get().strip()
        
        # Construir query
        query = """
            SELECT 
                P.PED_NUMEROOPERACAO,
                P.PED_NUMEROPEDIDO,
                P.PED_DATAVENDA,
                C.CLI_NOME,
                V.VEND_NOME,
                P.PED_PLACA,
                P.VEICULO,
                P.PED_ANOVEICULO,
                P.PED_VRTOTAL,
                P.PED_VRDESCONTO,
                P.PED_VRLIQUIDO,
                P.PED_OBSERVACAO,
                P.PED_KILOMETRAGEM,
                P.PED_COMISSAOVENDEDOR,
                P.CLI_CODIGO,
                P.VEND_CODIGO
            FROM PEDIDO P
            LEFT JOIN CLIENTE C ON P.CLI_CODIGO = C.CLI_CODIGO
            LEFT JOIN VENDEDOR V ON P.VEND_CODIGO = V.VEND_CODIGO
            WHERE 1=1
        """
        
        params = []
        
        # Filtro por número de operação
        if num_op:
            query += " AND P.PED_NUMEROOPERACAO = ?"
            params.append(int(num_op))
        else:
            # Filtro por datas
            if data_ini and data_fim:
                try:
                    dt_ini = datetime.strptime(data_ini, "%d/%m/%Y").strftime("%Y-%m-%d")
                    dt_fim = datetime.strptime(data_fim, "%d/%m/%Y").strftime("%Y-%m-%d")
                    query += " AND CAST(P.PED_DATAVENDA AS DATE) BETWEEN ? AND ?"
                    params.extend([dt_ini, dt_fim])
                except ValueError:
                    messagebox.showerror("Erro", "Formato de data inválido! Use DD/MM/AAAA")
                    self.window.focus_force()
                    return
            
            # Filtro por cliente
            if cliente:
                query += " AND UPPER(C.CLI_NOME) CONTAINING UPPER(?)"
                params.append(cliente)
        
        query += " ORDER BY P.PED_DATAVENDA DESC"
        
        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Converter para DataFrame
            columns = ['PED_NUMEROOPERACAO', 'PED_NUMEROPEDIDO', 'PED_DATAVENDA', 'CLI_NOME', 'VEND_NOME',
                      'PED_PLACA', 'VEICULO', 'PED_ANOVEICULO', 'PED_VRTOTAL', 'PED_VRDESCONTO', 
                      'PED_VRLIQUIDO', 'PED_OBSERVACAO', 'PED_KILOMETRAGEM', 'PED_COMISSAOVENDEDOR',
                      'CLI_CODIGO', 'VEND_CODIGO']
            self.df_pedidos = pd.DataFrame(rows, columns=columns)
            
            self._atualizar_tabela()
            self.window.focus_force()  # Manter foco
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar pedidos:\n{str(e)}")
            self.window.focus_force()
    
    def _limpar(self):
        """Limpa os campos de busca e resultados"""
        # Limpar campos
        self.txt_num_operacao.delete(0, tk.END)
        self.txt_data_inicio.delete(0, tk.END)
        self.txt_data_fim.delete(0, tk.END)
        self.txt_cliente.delete(0, tk.END)
        
        # Resetar datas padrão
        self.txt_data_inicio.insert(0, datetime.now().replace(day=1).strftime("%d/%m/%Y"))
        self.txt_data_fim.insert(0, datetime.now().strftime("%d/%m/%Y"))
        
        # Limpar tabela de pedidos
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
        self.df_pedidos = pd.DataFrame()
        self.current_pedido = None
        
        # Focar no campo de número de operação
        self.txt_num_operacao.focus()
    
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
    
    def _sort_column(self, col, reverse):
        """Ordena a tabela por coluna"""
        if self.df_pedidos.empty:
            return
        
        # Mapear coluna visual para coluna do DataFrame
        col_map = {
            'num_op': 'PED_NUMEROOPERACAO',
            'num_ped': 'PED_NUMEROPEDIDO',
            'data': 'PED_DATAVENDA',
            'cliente': 'CLI_NOME',
            'vendedor': 'VEND_NOME',
            'placa': 'PED_PLACA',
            'veiculo': 'VEICULO',
            'vr_total': 'PED_VRTOTAL',
            'desconto': 'PED_VRDESCONTO',
            'vr_liquido': 'PED_VRLIQUIDO'
        }
        
        df_col = col_map.get(col)
        if not df_col:
            return
        
        # Ordenar DataFrame
        self.df_pedidos = self.df_pedidos.sort_values(by=df_col, ascending=not reverse)
        
        # Atualizar tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for idx, row in self.df_pedidos.iterrows():
            data_venda = row['PED_DATAVENDA'].strftime("%d/%m/%Y") if pd.notna(row['PED_DATAVENDA']) else ""
            cliente = row['CLI_NOME'] if pd.notna(row['CLI_NOME']) else ""
            vendedor = row['VEND_NOME'] if pd.notna(row['VEND_NOME']) else ""
            placa = row['PED_PLACA'] if pd.notna(row['PED_PLACA']) else ""
            veiculo = row['VEICULO'] if pd.notna(row['VEICULO']) else ""
            vr_total = f"R$ {row['PED_VRTOTAL']:,.2f}" if pd.notna(row['PED_VRTOTAL']) else "R$ 0,00"
            desconto = f"R$ {row['PED_VRDESCONTO']:,.2f}" if pd.notna(row['PED_VRDESCONTO']) else "R$ 0,00"
            vr_liquido = f"R$ {row['PED_VRLIQUIDO']:,.2f}" if pd.notna(row['PED_VRLIQUIDO']) else "R$ 0,00"
            
            self.tree.insert('', tk.END, values=(
                row['PED_NUMEROOPERACAO'],
                row['PED_NUMEROPEDIDO'],
                data_venda,
                cliente,
                vendedor,
                placa,
                veiculo,
                vr_total,
                desconto,
                vr_liquido
            ), tags=(str(idx),))
        
        # Inverter ordem na próxima vez
        self.tree.heading(col, command=lambda: self._sort_column(col, not reverse))
    
    def _atualizar_tabela(self):
        """Atualiza a tabela com os pedidos"""
        # Limpar tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if self.df_pedidos.empty:
            messagebox.showinfo("Aviso", "Nenhum pedido encontrado.")
            self.window.focus_force()
            return
        
        # Preencher tabela
        for idx, row in self.df_pedidos.iterrows():
            data_venda = row['PED_DATAVENDA'].strftime("%d/%m/%Y") if pd.notna(row['PED_DATAVENDA']) else ""
            cliente = row['CLI_NOME'] if pd.notna(row['CLI_NOME']) else ""
            vendedor = row['VEND_NOME'] if pd.notna(row['VEND_NOME']) else ""
            placa = row['PED_PLACA'] if pd.notna(row['PED_PLACA']) else ""
            veiculo = row['VEICULO'] if pd.notna(row['VEICULO']) else ""
            vr_total = f"R$ {row['PED_VRTOTAL']:,.2f}" if pd.notna(row['PED_VRTOTAL']) else "R$ 0,00"
            desconto = f"R$ {row['PED_VRDESCONTO']:,.2f}" if pd.notna(row['PED_VRDESCONTO']) else "R$ 0,00"
            vr_liquido = f"R$ {row['PED_VRLIQUIDO']:,.2f}" if pd.notna(row['PED_VRLIQUIDO']) else "R$ 0,00"
            
            self.tree.insert('', tk.END, values=(
                row['PED_NUMEROOPERACAO'],
                row['PED_NUMEROPEDIDO'],
                data_venda,
                cliente,
                vendedor,
                placa,
                veiculo,
                vr_total,
                desconto,
                vr_liquido
            ), tags=(str(idx),))
        
        # Só mostrar mensagem se não for busca por número de operação
        if not self.txt_num_operacao.get().strip():
            messagebox.showinfo("Sucesso", f"{len(self.df_pedidos)} pedido(s) encontrado(s).")
            self.window.focus_force()
    
    def _on_pedido_select(self, event):
        """Quando seleciona um pedido"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        idx = int(item['tags'][0])
        pedido = self.df_pedidos.iloc[idx]
        
        self.current_pedido = pedido
        
        # Atualizar detalhes
        self._exibir_detalhes(pedido)
        
        # Carregar itens
        self._carregar_itens(pedido['PED_NUMEROOPERACAO'])
    
    def _exibir_detalhes(self, pedido):
        """Exibe detalhes do pedido"""
        self.txt_detalhes.config(state=tk.NORMAL)
        self.txt_detalhes.delete(1.0, tk.END)
        
        # Formatar valores ANTES da f-string
        vr_total = f"R$ {pedido['PED_VRTOTAL']:,.2f}" if pd.notna(pedido['PED_VRTOTAL']) else "R$ 0,00"
        vr_desconto = f"R$ {pedido['PED_VRDESCONTO']:,.2f}" if pd.notna(pedido['PED_VRDESCONTO']) else "R$ 0,00"
        vr_liquido = f"R$ {pedido['PED_VRLIQUIDO']:,.2f}" if pd.notna(pedido['PED_VRLIQUIDO']) else "R$ 0,00"
        comissao = pedido['PED_COMISSAOVENDEDOR'] if pd.notna(pedido['PED_COMISSAOVENDEDOR']) else 0
        ano = int(pedido['PED_ANOVEICULO']) if pd.notna(pedido['PED_ANOVEICULO']) else ''
        
        detalhes = f"""Nº Operação: {pedido['PED_NUMEROOPERACAO']}
Nº Pedido: {pedido['PED_NUMEROPEDIDO']}
Data Venda: {pedido['PED_DATAVENDA'].strftime('%d/%m/%Y %H:%M') if pd.notna(pedido['PED_DATAVENDA']) else ''}

Cliente: {pedido['CLI_NOME'] if pd.notna(pedido['CLI_NOME']) else 'Não informado'}
Vendedor: {pedido['VEND_NOME'] if pd.notna(pedido['VEND_NOME']) else 'Não informado'}
Comissão Vendedor: {comissao}%

Veículo: {pedido['VEICULO'] if pd.notna(pedido['VEICULO']) else ''}
Placa: {pedido['PED_PLACA'] if pd.notna(pedido['PED_PLACA']) else ''}
Ano: {ano}
Kilometragem: {pedido['PED_KILOMETRAGEM'] if pd.notna(pedido['PED_KILOMETRAGEM']) else ''}

Valor Total: {vr_total}
Desconto: {vr_desconto}
Valor Líquido: {vr_liquido}

Observação: {pedido['PED_OBSERVACAO'] if pd.notna(pedido['PED_OBSERVACAO']) else ''}
"""
        
        self.txt_detalhes.insert(1.0, detalhes)
        self.txt_detalhes.config(state=tk.DISABLED)
    
    def _carregar_itens(self, num_operacao):
        """Carrega itens do pedido"""
        # Limpar tabela de itens
        for item in self.tree_itens.get_children():
            self.tree_itens.delete(item)
        
        try:
            query = """
                SELECT 
                    I.PROD_CODIGO,
                    P.PROD_DESCRICAOPRODUTO,
                    I.PIT_QTDEVENDIDA,
                    I.PIT_VALORUNITARIO,
                    (I.PIT_QTDEVENDIDA * I.PIT_VALORUNITARIO) AS TOTAL
                FROM PEDITENS I
                LEFT JOIN PRODUTO P ON I.PROD_CODIGO = P.PROD_CODIGO
                WHERE I.PED_NUMEROOPERACAO = ?
                ORDER BY I.PROD_CODIGO
            """
            
            cursor = self.db.get_connection().cursor()
            cursor.execute(query, [num_operacao])
            rows = cursor.fetchall()
            
            if rows:
                for row in rows:
                    codigo = row[0] if row[0] else ""
                    descricao = row[1] if row[1] else "Produto não encontrado"
                    qtde = f"{row[2]:,.2f}" if row[2] else "0"
                    vr_unit = f"R$ {row[3]:,.2f}" if row[3] else "R$ 0,00"
                    vr_total = f"R$ {row[4]:,.2f}" if row[4] else "R$ 0,00"
                    
                    self.tree_itens.insert('', tk.END, values=(codigo, descricao, qtde, vr_unit, vr_total))
            
        except Exception as e:
            print(f"Erro ao carregar itens: {e}")  # Log silencioso
    
    def _on_closing(self):
        """Fecha conexão e janela"""
        self.db.close()
        self.window.destroy()
