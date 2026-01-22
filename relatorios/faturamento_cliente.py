import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from datetime import datetime
import pandas as pd
from core.database import FirebirdDB
import config
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import os

class FaturamentoClienteWindow:
    def __init__(self, parent):
        self.db = FirebirdDB(config.DB_CONFIG)
        self.db.connect()
        self.df_vendas = pd.DataFrame()
        self.cliente_codigo = None
        self.cliente_nome = None
        
        # Criar janela
        self.window = tk.Toplevel(parent)
        self.window.title("Relatório de Faturamento por Cliente")
        self.window.geometry("1400x800")
        
        # Centralizar
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - 700
        y = (self.window.winfo_screenheight() // 2) - 400
        self.window.geometry(f"+{x}+{y}")
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Cria os widgets da interface"""
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # === ÁREA DE BUSCA ===
        search_frame = ttk.LabelFrame(main_frame, text="Busca", padding="10")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Cliente
        ttk.Label(search_frame, text="Cliente (Código ou Nome):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.txt_cliente = ttk.Entry(search_frame, width=50)
        self.txt_cliente.grid(row=0, column=1, sticky=tk.W, padx=5)
        self.txt_cliente.bind('<KeyRelease>', lambda e: self._auto_format_date(self.txt_data_inicio) if e.widget != self.txt_cliente else None)
        
        # Datas
        ttk.Label(search_frame, text="Data Inicial:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.txt_data_inicio = ttk.Entry(search_frame, width=15)
        self.txt_data_inicio.grid(row=1, column=1, sticky=tk.W, padx=5)
        self.txt_data_inicio.bind('<KeyRelease>', lambda e: self._auto_format_date(e.widget))
        
        # Data inicial padrão (primeiro dia do mês)
        self.txt_data_inicio.insert(0, datetime.now().replace(day=1).strftime("%d/%m/%Y"))
        
        ttk.Label(search_frame, text="Data Final:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.txt_data_fim = ttk.Entry(search_frame, width=15)
        self.txt_data_fim.grid(row=2, column=1, sticky=tk.W, padx=5)
        self.txt_data_fim.bind('<KeyRelease>', lambda e: self._auto_format_date(e.widget))
        
        # Data final padrão (hoje)
        self.txt_data_fim.insert(0, datetime.now().strftime("%d/%m/%Y"))
        
        # Filtro de pagamento
        ttk.Label(search_frame, text="Filtro de Pagamento:").grid(row=3, column=0, sticky=tk.W, pady=5)
        
        filter_frame = ttk.Frame(search_frame)
        filter_frame.grid(row=3, column=1, sticky=tk.W, padx=5)
        
        self.filtro_pagamento = tk.StringVar(value="todos")
        ttk.Radiobutton(filter_frame, text="Todos", variable=self.filtro_pagamento, value="todos").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(filter_frame, text="Pagos", variable=self.filtro_pagamento, value="pagos").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(filter_frame, text="Não Pagos", variable=self.filtro_pagamento, value="nao_pagos").pack(side=tk.LEFT, padx=5)
        
        # Botões de ação
        btn_frame = ttk.Frame(search_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Buscar", command=self._buscar).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Limpar", command=self._limpar).pack(side=tk.LEFT, padx=5)
        
        # === ÁREA DE RESULTADOS ===
        results_frame = ttk.Frame(main_frame)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Label com informações do cliente
        self.lbl_cliente = ttk.Label(results_frame, text="", font=("Arial", 12, "bold"))
        self.lbl_cliente.pack(pady=(0, 10))
        
        # Tabela de vendas
        table_frame = ttk.LabelFrame(results_frame, text="Vendas do Cliente", padding="5")
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        
        # Treeview
        columns = ('cod_prod', 'descricao', 'pedido', 'data_venda', 'qtde', 'vl_unit', 'vl_total')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings',
                                 yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        # Configurar colunas
        self.tree.heading('cod_prod', text='Código Produto')
        self.tree.heading('descricao', text='Descrição Produto')
        self.tree.heading('pedido', text='Pedido')
        self.tree.heading('data_venda', text='Data Venda')
        self.tree.heading('qtde', text='Qtde')
        self.tree.heading('vl_unit', text='Vl. Unitário')
        self.tree.heading('vl_total', text='Vl. Total')
        
        self.tree.column('cod_prod', width=100, anchor='center')
        self.tree.column('descricao', width=400, anchor='w')
        self.tree.column('pedido', width=80, anchor='center')
        self.tree.column('data_venda', width=100, anchor='center')
        self.tree.column('qtde', width=80, anchor='e')
        self.tree.column('vl_unit', width=100, anchor='e')
        self.tree.column('vl_total', width=100, anchor='e')
        
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        scroll_y.grid(row=0, column=1, sticky='ns')
        scroll_x.grid(row=1, column=0, sticky='ew')
        
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        
        # Frame de totais
        totals_frame = ttk.Frame(results_frame)
        totals_frame.pack(fill=tk.X, pady=10)
        
        self.lbl_totais = ttk.Label(totals_frame, text="", font=("Arial", 11, "bold"))
        self.lbl_totais.pack(side=tk.RIGHT, padx=10)
        
        # Botão Gerar PDF
        ttk.Button(totals_frame, text="📄 Gerar PDF", command=self._gerar_pdf).pack(side=tk.LEFT, padx=10)
    
    def _auto_format_date(self, entry_widget):
        """Formata automaticamente a data enquanto o usuário digita"""
        current_value = entry_widget.get()
        cursor_pos = entry_widget.index(tk.INSERT)
        
        if not current_value:
            return
        
        value_only_digits = current_value.replace('/', '')
        
        if len(value_only_digits) > 8:
            value_only_digits = value_only_digits[:8]
        
        value_only_digits = ''.join(filter(str.isdigit, value_only_digits))
        
        if not value_only_digits:
            entry_widget.delete(0, tk.END)
            return
        
        formatted = ''
        for i, char in enumerate(value_only_digits):
            if i == 2 or i == 4:
                formatted += '/'
            formatted += char
        
        if formatted != current_value:
            digits_before = len(current_value[:cursor_pos].replace('/', ''))
            
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, formatted)
            
            new_pos = digits_before
            if digits_before > 2:
                new_pos += 1
            if digits_before > 4:
                new_pos += 1
            
            new_pos = min(new_pos, len(formatted))
            
            try:
                entry_widget.icursor(new_pos)
            except:
                pass
    
    def _buscar(self):
        """Busca vendas do cliente"""
        cliente = self.txt_cliente.get().strip()
        data_ini = self.txt_data_inicio.get().strip()
        data_fim = self.txt_data_fim.get().strip()
        
        if not cliente:
            messagebox.showwarning("Aviso", "Digite o código ou nome do cliente!")
            self.window.focus_force()
            return
        
        if not data_ini or not data_fim:
            messagebox.showwarning("Aviso", "Digite o período (data inicial e final)!")
            self.window.focus_force()
            return
        
        try:
            dt_ini = datetime.strptime(data_ini, "%d/%m/%Y").strftime("%Y-%m-%d")
            dt_fim = datetime.strptime(data_fim, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Erro", "Formato de data inválido! Use DD/MM/AAAA")
            self.window.focus_force()
            return
        
        try:
            # Primeiro, buscar o cliente
            if cliente.isdigit():
                # Busca por código
                query_cliente = "SELECT CLI_CODIGO, CLI_NOME FROM CLIENTE WHERE CLI_CODIGO = ?"
                params_cliente = [int(cliente)]
            else:
                # Busca por nome (múltiplas palavras)
                query_cliente = "SELECT CLI_CODIGO, CLI_NOME FROM CLIENTE WHERE 1=1"
                params_cliente = []
                palavras = cliente.upper().split()
                for palavra in palavras:
                    if palavra:
                        query_cliente += " AND UPPER(CLI_NOME) CONTAINING ?"
                        params_cliente.append(palavra)
            
            cursor = self.db.get_connection().cursor()
            cursor.execute(query_cliente, params_cliente)
            cliente_row = cursor.fetchone()
            
            if not cliente_row:
                messagebox.showwarning("Aviso", "Cliente não encontrado!")
                self.window.focus_force()
                return
            
            self.cliente_codigo = cliente_row[0]
            self.cliente_nome = cliente_row[1]
            
            # Buscar vendas do cliente com filtro de pagamento
            filtro = self.filtro_pagamento.get()
            
            if filtro == "pagos":
                # Apenas pedidos pagos (LEFT JOIN + IS NOT NULL é mais rápido que EXISTS)
                query = """
                    SELECT 
                        P.PED_NUMEROOPERACAO,
                        P.PED_DATAVENDA,
                        I.PROD_CODIGO,
                        PR.PROD_DESCRICAOPRODUTO,
                        I.PIT_QTDEVENDIDA,
                        I.PIT_VALORUNITARIO,
                        (I.PIT_QTDEVENDIDA * I.PIT_VALORUNITARIO) AS VL_TOTAL
                    FROM PEDIDO P
                    INNER JOIN PEDITENS I ON P.PED_NUMEROOPERACAO = I.PED_NUMEROOPERACAO
                    LEFT JOIN PRODUTO PR ON I.PROD_CODIGO = PR.PROD_CODIGO
                    INNER JOIN RECEBER R ON P.PED_NUMEROOPERACAO = R.PED_NUMEROOPERACAO
                    INNER JOIN RECEBTO RT ON R.REC_NUMEROOPERACAO = RT.REC_NUMEROOPERACAO
                    WHERE P.CLI_CODIGO = ?
                      AND CAST(P.PED_DATAVENDA AS DATE) BETWEEN ? AND ?
                    ORDER BY P.PED_DATAVENDA, P.PED_NUMEROOPERACAO
                """
            elif filtro == "nao_pagos":
                # Apenas pedidos não pagos (LEFT JOIN + IS NULL é MUITO mais rápido que NOT EXISTS)
                query = """
                    SELECT 
                        P.PED_NUMEROOPERACAO,
                        P.PED_DATAVENDA,
                        I.PROD_CODIGO,
                        PR.PROD_DESCRICAOPRODUTO,
                        I.PIT_QTDEVENDIDA,
                        I.PIT_VALORUNITARIO,
                        (I.PIT_QTDEVENDIDA * I.PIT_VALORUNITARIO) AS VL_TOTAL
                    FROM PEDIDO P
                    INNER JOIN PEDITENS I ON P.PED_NUMEROOPERACAO = I.PED_NUMEROOPERACAO
                    LEFT JOIN PRODUTO PR ON I.PROD_CODIGO = PR.PROD_CODIGO
                    INNER JOIN RECEBER R ON P.PED_NUMEROOPERACAO = R.PED_NUMEROOPERACAO
                    LEFT JOIN RECEBTO RT ON R.REC_NUMEROOPERACAO = RT.REC_NUMEROOPERACAO
                    WHERE P.CLI_CODIGO = ?
                      AND CAST(P.PED_DATAVENDA AS DATE) BETWEEN ? AND ?
                      AND RT.REC_NUMEROOPERACAO IS NULL
                    ORDER BY P.PED_DATAVENDA, P.PED_NUMEROOPERACAO
                """
            else:
                # Todos os pedidos
                query = """
                    SELECT 
                        P.PED_NUMEROOPERACAO,
                        P.PED_DATAVENDA,
                        I.PROD_CODIGO,
                        PR.PROD_DESCRICAOPRODUTO,
                        I.PIT_QTDEVENDIDA,
                        I.PIT_VALORUNITARIO,
                        (I.PIT_QTDEVENDIDA * I.PIT_VALORUNITARIO) AS VL_TOTAL
                    FROM PEDIDO P
                    INNER JOIN PEDITENS I ON P.PED_NUMEROOPERACAO = I.PED_NUMEROOPERACAO
                    LEFT JOIN PRODUTO PR ON I.PROD_CODIGO = PR.PROD_CODIGO
                    WHERE P.CLI_CODIGO = ?
                      AND CAST(P.PED_DATAVENDA AS DATE) BETWEEN ? AND ?
                    ORDER BY P.PED_DATAVENDA, P.PED_NUMEROOPERACAO
                """
            
            cursor.execute(query, [self.cliente_codigo, dt_ini, dt_fim])
            rows = cursor.fetchall()
            
            columns = ['PED_NUMEROOPERACAO', 'PED_DATAVENDA', 'PROD_CODIGO', 'PROD_DESCRICAOPRODUTO',
                      'PIT_QTDEVENDIDA', 'PIT_VALORUNITARIO', 'VL_TOTAL']
            self.df_vendas = pd.DataFrame(rows, columns=columns)
            
            self._atualizar_tabela()
            self.window.focus_force()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar vendas:\n{str(e)}")
            self.window.focus_force()
    
    def _atualizar_tabela(self):
        """Atualiza a tabela com as vendas"""
        # Limpar tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if self.df_vendas.empty:
            self.lbl_cliente.config(text="")
            self.lbl_totais.config(text="")
            messagebox.showinfo("Aviso", "Nenhuma venda encontrada para este cliente no período informado.")
            self.window.focus_force()
            return
        
        # Atualizar label do cliente
        self.lbl_cliente.config(text=f"Cliente: {self.cliente_codigo} - {self.cliente_nome}")
        
        # Preencher tabela
        total_qtde = 0
        total_valor = 0
        
        for idx, row in self.df_vendas.iterrows():
            data_venda = row['PED_DATAVENDA'].strftime("%d/%m/%Y") if pd.notna(row['PED_DATAVENDA']) else ""
            descricao = row['PROD_DESCRICAOPRODUTO'] if pd.notna(row['PROD_DESCRICAOPRODUTO']) else ""
            
            qtde = row['PIT_QTDEVENDIDA'] if pd.notna(row['PIT_QTDEVENDIDA']) else 0
            vl_unit = row['PIT_VALORUNITARIO'] if pd.notna(row['PIT_VALORUNITARIO']) else 0
            vl_total = row['VL_TOTAL'] if pd.notna(row['VL_TOTAL']) else 0
            
            total_qtde += qtde
            total_valor += vl_total
            
            self.tree.insert('', tk.END, values=(
                row['PROD_CODIGO'],
                descricao,
                row['PED_NUMEROOPERACAO'],
                data_venda,
                f"{qtde:,.2f}",
                f"R$ {vl_unit:,.2f}",
                f"R$ {vl_total:,.2f}"
            ))
        
        # Atualizar totais
        self.lbl_totais.config(text=f"TOTAIS:  Qtde: {total_qtde:,.2f}  |  Valor: R$ {total_valor:,.2f}")
        
        messagebox.showinfo("Sucesso", f"{len(self.df_vendas)} venda(s) encontrada(s).")
        self.window.focus_force()
    
    def _limpar(self):
        """Limpa os campos e resultados"""
        self.txt_cliente.delete(0, tk.END)
        self.txt_data_inicio.delete(0, tk.END)
        self.txt_data_fim.delete(0, tk.END)
        
        # Resetar datas padrão
        self.txt_data_inicio.insert(0, datetime.now().replace(day=1).strftime("%d/%m/%Y"))
        self.txt_data_fim.insert(0, datetime.now().strftime("%d/%m/%Y"))
        
        # Limpar tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Limpar labels
        self.lbl_cliente.config(text="")
        self.lbl_totais.config(text="")
        
        # Limpar DataFrame
        self.df_vendas = pd.DataFrame()
        self.cliente_codigo = None
        self.cliente_nome = None
    
    def _gerar_pdf(self):
        """Gera PDF do relatório"""
        if self.df_vendas.empty:
            messagebox.showwarning("Aviso", "Não há dados para gerar o PDF!")
            self.window.focus_force()
            return
        
        # Solicitar local para salvar
        data_ini = self.txt_data_inicio.get().replace('/', '')
        data_fim = self.txt_data_fim.get().replace('/', '')
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"faturamento_cliente_{self.cliente_codigo}_{data_ini}_{data_fim}.pdf"
        )
        
        if not filename:
            return
        
        try:
            self._criar_pdf(filename)
            messagebox.showinfo("Sucesso", f"PDF gerado com sucesso!\n{filename}")
            self.window.focus_force()
            
            # Perguntar se deseja abrir
            if messagebox.askyesno("Abrir PDF", "Deseja abrir o arquivo PDF?"):
                os.startfile(filename)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar PDF:\n{str(e)}")
            self.window.focus_force()
    
    def _criar_pdf(self, filename):
        """Cria o arquivo PDF"""
        doc = SimpleDocTemplate(filename, pagesize=A4,
                               rightMargin=1*cm, leftMargin=1*cm,
                               topMargin=1*cm, bottomMargin=1*cm)
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Cabeçalho
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=14,
            textColor=colors.HexColor('#000080'),
            spaceAfter=6,
            alignment=TA_CENTER
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            spaceAfter=12
        )
        
        elements.append(Paragraph("ORIGINAL AUTO PEÇAS", title_style))
        elements.append(Paragraph("FATURAMENTO POR CLIENTE", title_style))
        
        periodo = f"Período: {self.txt_data_inicio.get()} a {self.txt_data_fim.get()}"
        data_geracao = f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        elements.append(Paragraph(f"{data_geracao}        {periodo}", subtitle_style))
        
        # Informações do cliente
        cliente_info = f"CLIENTE  {self.cliente_codigo}    {self.cliente_nome}"
        elements.append(Paragraph(cliente_info, subtitle_style))
        elements.append(Spacer(1, 0.5*cm))
        
        # Tabela de dados
        data = [['CÓDIGO', 'DESCRIÇÃO PRODUTO', 'PEDIDO', 'DATA VENDA', 'QTDE', 'VR. UNIT.', 'VR. TOTAL']]
        
        total_qtde = 0
        total_valor = 0
        
        for idx, row in self.df_vendas.iterrows():
            data_venda = row['PED_DATAVENDA'].strftime("%d/%m/%Y") if pd.notna(row['PED_DATAVENDA']) else ""
            descricao = str(row['PROD_DESCRICAOPRODUTO'])[:40] if pd.notna(row['PROD_DESCRICAOPRODUTO']) else ""
            
            qtde = row['PIT_QTDEVENDIDA'] if pd.notna(row['PIT_QTDEVENDIDA']) else 0
            vl_unit = row['PIT_VALORUNITARIO'] if pd.notna(row['PIT_VALORUNITARIO']) else 0
            vl_total = row['VL_TOTAL'] if pd.notna(row['VL_TOTAL']) else 0
            
            total_qtde += qtde
            total_valor += vl_total
            
            data.append([
                str(row['PROD_CODIGO']),
                descricao,
                str(row['PED_NUMEROOPERACAO']),
                data_venda,
                f"{qtde:.2f}",
                f"{vl_unit:.2f}",
                f"{vl_total:.2f}"
            ])
        
        # Linha de total
        data.append([
            '', '', '', 'TOTAL GERAL ===>>>',
            f"{total_qtde:.2f}",
            '',
            f"{total_valor:.2f}"
        ])
        
        # Criar tabela (larguras ajustadas para A4 retrato - total ~19cm)
        col_widths = [1.5*cm, 7*cm, 1.8*cm, 2.2*cm, 1.5*cm, 2*cm, 2*cm]
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),  # Pedido
            ('ALIGN', (3, 0), (3, -1), 'CENTER'),  # Data
            ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),  # Números
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        
        elements.append(table)
        
        # Gerar PDF
        doc.build(elements)
