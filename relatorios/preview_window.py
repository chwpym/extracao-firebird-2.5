import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import os
from datetime import datetime


class PreviewWindow:
    """Janela de visualização dos dados antes de gerar PDF/Excel"""
    def __init__(self, parent, df, agrupar=True, exibir_unitario=True, exibir_total=True):
        self.parent = parent
        self.df = df
        self.agrupar = agrupar
        self.exibir_unitario = exibir_unitario
        self.exibir_total = exibir_total
        
        # Criar janela
        self.window = tk.Toplevel(parent)
        self.window.title("Visualização do Relatório")
        self.window.state('zoomed')  # Maximizar
        
        # Criar interface
        self._create_widgets()
    
    def _create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(title_frame, text="OFICINA AUTO PEÇAS", 
                 font=("Helvetica", 14, "bold")).pack()
        ttk.Label(title_frame, text="POSIÇÃO DE ESTOQUE", 
                 font=("Helvetica", 12, "bold")).pack()
        ttk.Label(title_frame, text=f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 
                 font=("Helvetica", 10)).pack()
        
        # Frame da tabela
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        hsb = ttk.Scrollbar(table_frame, orient="horizontal")
        
        # Treeview
        columns = ["codigo", "descricao", "marca", "ref", "local", "estoque"]
        if self.exibir_unitario: columns.append("vl_unit")
        if self.exibir_total: columns.append("vl_total")
        
        self.tree = ttk.Treeview(table_frame,
                                 columns=tuple(columns),
                                 show="tree headings",
                                 yscrollcommand=vsb.set,
                                 xscrollcommand=hsb.set)
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Colunas
        self.tree.heading("#0", text="")
        self.tree.heading("codigo", text="Código")
        self.tree.heading("descricao", text="Descrição")
        self.tree.heading("marca", text="Marca")
        self.tree.heading("ref", text="Cód.Fab.")
        self.tree.heading("local", text="Local.")
        self.tree.heading("estoque", text="Estoque")
        
        self.tree.column("#0", width=0, stretch=False)
        self.tree.column("codigo", width=70, anchor=tk.W)
        self.tree.column("descricao", width=400, anchor=tk.W)
        self.tree.column("marca", width=180, anchor=tk.W)
        self.tree.column("ref", width=120, anchor=tk.W)
        self.tree.column("local", width=180, anchor=tk.W)
        self.tree.column("estoque", width=120, anchor=tk.E)

        if self.exibir_unitario:
            self.tree.heading("vl_unit", text="Vl.Unit.")
            self.tree.column("vl_unit", width=100, anchor=tk.E)
            
        if self.exibir_total:
            self.tree.heading("vl_total", text="Vl.Total")
            self.tree.column("vl_total", width=100, anchor=tk.E)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Preencher dados
        self._preencher_dados()
        
        # Frame de totais
        total_frame = ttk.Frame(main_frame)
        total_frame.pack(fill=tk.X, pady=(0, 10))
        
        total_geral = self.df['VALOR_TOTAL'].sum()
        ttk.Label(total_frame, text=f"VALOR TOTAL: R$ {total_geral:,.2f}", 
                 font=("Helvetica", 12, "bold"),
                 foreground="darkblue").pack(side=tk.RIGHT, padx=20)
        
        # Botões
        botoes_frame = ttk.Frame(main_frame)
        botoes_frame.pack(fill=tk.X)
        
        ttk.Button(botoes_frame, text="📄 Gerar PDF", 
                  command=self._gerar_pdf).pack(side=tk.LEFT, padx=5)
        ttk.Button(botoes_frame, text="📊 Gerar Excel", 
                  command=self._gerar_excel).pack(side=tk.LEFT, padx=5)
        ttk.Button(botoes_frame, text="Fechar", 
                  command=self.window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def _format_estoque(self, valor):
        """Formata o estoque: retira .0 se for inteiro, usa vírgula se quebrado"""
        try:
            v = float(valor)
            if v == int(v):
                return str(int(v))
            return str(v).replace('.', ',')
        except:
            return str(valor)

    def _preencher_dados(self):
        """Preenche a tabela com os dados"""
        if self.agrupar:
            # Agrupar por prateleira
            self.df['GRUPO'] = self.df['PROD_LOCALIZACAOPECA'].apply(
                lambda x: str(x).split('-')[0] if pd.notna(x) else 'SEM LOC'
            )
            
            for grupo in sorted(self.df['GRUPO'].unique()):
                df_grupo = self.df[self.df['GRUPO'] == grupo]
                
                # Inserir grupo (com a mesma quantidade de colunas que a tabela)
                num_cols = 6 + (1 if self.exibir_unitario else 0) + (1 if self.exibir_total else 0)
                grupo_id = self.tree.insert('', 'end', text=f"GRUPO: {grupo}", 
                                           values=('',) * num_cols,
                                           tags=('grupo',))
                
                subtotal = 0
                for idx, row in df_grupo.iterrows():
                    estoque = row.get('PROD_QTDEESTOQUEFISICO', 0) or 0
                    vl_unit = row.get('PROD_PRECOAVISTA', 0) or 0
                    vl_total = row.get('VALOR_TOTAL', 0) or 0
                    
                    values = [
                        row['PROD_CODIGO'],
                        row['PROD_DESCRICAOPRODUTO'],
                        row.get('PROD_MARCA', '-') or '-',
                        row.get('PROD_CODIGOFABRICANTE', '-') or '-',
                        row.get('PROD_LOCALIZACAOPECA', '-') or '-',
                        self._format_estoque(estoque)
                    ]
                    if self.exibir_unitario: values.append(f"{vl_unit:.2f}")
                    if self.exibir_total: values.append(f"{vl_total:.2f}")
                    
                    self.tree.insert(grupo_id, 'end', values=tuple(values))
                    subtotal += vl_total
                
                # Inserir subtotal dinâmico
                if self.exibir_total:
                    # Montar linha de subtotal com o número correto de colunas
                    subtotal_cols = ['', '', '', '', '', ''] # Código, Desc, Marca, Ref, Local, Estoque
                    if self.exibir_unitario:
                        subtotal_cols.append('Subtotal:')
                        subtotal_cols.append(f"{subtotal:.2f}")
                    else:
                        subtotal_cols[-1] = 'Subtotal:' # Substitui estoque por Subtotal:
                        subtotal_cols.append(f"{subtotal:.2f}")
                    
                    self.tree.insert(grupo_id, 'end',
                                    values=tuple(subtotal_cols),
                                    tags=('subtotal',))
                
                # Expandir grupo automaticamente
                self.tree.item(grupo_id, open=True)
        else:
            # Sem agrupamento
            for idx, row in self.df.iterrows():
                estoque = row.get('PROD_QTDEESTOQUEFISICO', 0) or 0
                vl_unit = row.get('PROD_PRECOAVISTA', 0) or 0
                vl_total = row.get('VALOR_TOTAL', 0) or 0
                
                values = [
                    row['PROD_CODIGO'],
                    row['PROD_DESCRICAOPRODUTO'],
                    row.get('PROD_MARCA', '-') or '-',
                    row.get('PROD_CODIGOFABRICANTE', '-') or '-',
                    row.get('PROD_LOCALIZACAOPECA', '-') or '-',
                    self._format_estoque(estoque)
                ]
                if self.exibir_unitario: values.append(f"{vl_unit:.2f}")
                if self.exibir_total: values.append(f"{vl_total:.2f}")
                
                self.tree.insert('', 'end', values=tuple(values))
        
        # Estilos
        self.tree.tag_configure('grupo', background='#D9E1F2', font=('Helvetica', 10, 'bold'))
        self.tree.tag_configure('subtotal', background='#E2EFDA', font=('Helvetica', 9, 'bold'))
    
    def _gerar_pdf(self):
        """Gera PDF a partir dos dados visualizados"""
        try:
            from relatorios.pdf_generator import gerar_pdf_localizacao
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                initialfile=f"relatorio_localizacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )
            
            if filename:
                gerar_pdf_localizacao(self.df, filename, 
                                     agrupar=self.agrupar,
                                     exibir_unitario=self.exibir_unitario,
                                     exibir_total=self.exibir_total)
                messagebox.showinfo("Sucesso", f"PDF gerado com sucesso!\n{filename}")
                os.startfile(filename)
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar PDF:\n{str(e)}")
    
    def _gerar_excel(self):
        """Gera Excel a partir dos dados visualizados"""
        try:
            from relatorios.excel_generator import gerar_excel_localizacao
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=f"relatorio_localizacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )
            
            if filename:
                gerar_excel_localizacao(self.df, filename, 
                                       agrupar=self.agrupar,
                                       exibir_unitario=self.exibir_unitario,
                                       exibir_total=self.exibir_total)
                messagebox.showinfo("Sucesso", f"Excel gerado com sucesso!\n{filename}")
                os.startfile(filename)
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar Excel:\n{str(e)}")
