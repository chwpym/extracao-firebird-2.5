import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import sys
import os
from datetime import datetime

# Adicionar o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import FirebirdDB
import config
from relatorios.preview_window import PreviewWindow

class RelatorioLocalizacaoWindow:
    def __init__(self, parent):
        self.parent = parent
        self.db = None
        
        # Criar janela
        self.window = tk.Toplevel(parent)
        self.window.title("Relatório de Localização de Produtos")
        self.window.geometry("650x600")  # Aumentado para mostrar botões
        
        # Centralizar janela
        self._center_window(650, 600)
        
        # Manter janela sempre visível
        self.window.transient(parent)
        self.window.grab_set()
        self.window.focus_force()
        
        # Conectar ao banco
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
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        lbl_title = ttk.Label(main_frame, text="Relatório de Localização de Produtos", 
                             font=("Helvetica", 12, "bold"))
        lbl_title.pack(pady=(0, 20))
        
        # ===== TIPO DE FILTRO =====
        filtro_frame = ttk.LabelFrame(main_frame, text="Tipo de Filtro", padding="15")
        filtro_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.filtro_tipo = tk.StringVar(value="prateleira")
        
        # Radio: Prateleira
        ttk.Radiobutton(filtro_frame, text="Prateleira (ex: A, B, C)", 
                       variable=self.filtro_tipo, value="prateleira",
                       command=self._on_filtro_change).pack(anchor=tk.W, pady=2)
        
        self.frame_prateleira = ttk.Frame(filtro_frame)
        self.frame_prateleira.pack(fill=tk.X, padx=20, pady=5)
        ttk.Label(self.frame_prateleira, text="Prateleira:").pack(side=tk.LEFT, padx=5)
        self.entry_prateleira = ttk.Entry(self.frame_prateleira, width=10)
        self.entry_prateleira.pack(side=tk.LEFT, padx=5)
        
        # Radio: Faixa
        ttk.Radiobutton(filtro_frame, text="Faixa de Localizações (ex: A-01 até A-06)", 
                       variable=self.filtro_tipo, value="faixa",
                       command=self._on_filtro_change).pack(anchor=tk.W, pady=2)
        
        self.frame_faixa = ttk.Frame(filtro_frame)
        self.frame_faixa.pack(fill=tk.X, padx=20, pady=5)
        ttk.Label(self.frame_faixa, text="De:").pack(side=tk.LEFT, padx=5)
        self.entry_faixa_inicio = ttk.Entry(self.frame_faixa, width=15)
        self.entry_faixa_inicio.pack(side=tk.LEFT, padx=5)
        ttk.Label(self.frame_faixa, text="Até:").pack(side=tk.LEFT, padx=5)
        self.entry_faixa_fim = ttk.Entry(self.frame_faixa, width=15)
        self.entry_faixa_fim.pack(side=tk.LEFT, padx=5)
        
        # Radio: Específica
        ttk.Radiobutton(filtro_frame, text="Localização Específica (ex: A-02)", 
                       variable=self.filtro_tipo, value="especifica",
                       command=self._on_filtro_change).pack(anchor=tk.W, pady=2)
        
        self.frame_especifica = ttk.Frame(filtro_frame)
        self.frame_especifica.pack(fill=tk.X, padx=20, pady=5)
        ttk.Label(self.frame_especifica, text="Localização:").pack(side=tk.LEFT, padx=5)
        self.entry_especifica = ttk.Entry(self.frame_especifica, width=20)
        self.entry_especifica.pack(side=tk.LEFT, padx=5)
        
        # Radio: Todas
        ttk.Radiobutton(filtro_frame, text="Todas as Localizações", 
                       variable=self.filtro_tipo, value="todas",
                       command=self._on_filtro_change).pack(anchor=tk.W, pady=2)
        
        # ===== OPÇÕES =====
        opcoes_frame = ttk.LabelFrame(main_frame, text="Opções", padding="15")
        opcoes_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.check_sem_estoque = tk.BooleanVar(value=False)
        ttk.Checkbutton(opcoes_frame, text="Incluir produtos sem estoque", 
                       variable=self.check_sem_estoque).pack(anchor=tk.W, pady=2)
        
        self.check_agrupar = tk.BooleanVar(value=True)
        ttk.Checkbutton(opcoes_frame, text="Agrupar por prateleira", 
                       variable=self.check_agrupar).pack(anchor=tk.W, pady=2)
        
        self.check_exibir_unitario = tk.BooleanVar(value=True)
        ttk.Checkbutton(opcoes_frame, text="Exibir Valor Unitário", 
                       variable=self.check_exibir_unitario).pack(anchor=tk.W, pady=2)
        
        self.check_exibir_total = tk.BooleanVar(value=True)
        ttk.Checkbutton(opcoes_frame, text="Exibir Valor Total", 
                       variable=self.check_exibir_total).pack(anchor=tk.W, pady=2)
        
        botoes_frame = ttk.Frame(main_frame)
        botoes_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(botoes_frame, text="👁️ Visualizar", 
                  command=self._visualizar).pack(side=tk.LEFT, padx=5)
        ttk.Button(botoes_frame, text="📄 Gerar PDF", 
                  command=self._gerar_pdf).pack(side=tk.LEFT, padx=5)
        ttk.Button(botoes_frame, text="📊 Gerar Excel", 
                  command=self._gerar_excel).pack(side=tk.LEFT, padx=5)
        ttk.Button(botoes_frame, text="Fechar", 
                  command=self._on_close).pack(side=tk.RIGHT, padx=5)
        
        # Inicializar estado dos campos
        self._on_filtro_change()
    
    def _on_filtro_change(self):
        """Habilita/desabilita campos conforme tipo de filtro"""
        tipo = self.filtro_tipo.get()
        
        # Desabilitar todos
        for widget in self.frame_prateleira.winfo_children():
            if isinstance(widget, ttk.Entry):
                widget.config(state='disabled')
        for widget in self.frame_faixa.winfo_children():
            if isinstance(widget, ttk.Entry):
                widget.config(state='disabled')
        for widget in self.frame_especifica.winfo_children():
            if isinstance(widget, ttk.Entry):
                widget.config(state='disabled')
        
        # Habilitar conforme seleção
        if tipo == "prateleira":
            self.entry_prateleira.config(state='normal')
            self.entry_prateleira.focus()
        elif tipo == "faixa":
            self.entry_faixa_inicio.config(state='normal')
            self.entry_faixa_fim.config(state='normal')
            self.entry_faixa_inicio.focus()
        elif tipo == "especifica":
            self.entry_especifica.config(state='normal')
            self.entry_especifica.focus()
    
    def _validar_filtros(self):
        """Valida os filtros antes de gerar relatório"""
        tipo = self.filtro_tipo.get()
        
        if tipo == "prateleira":
            if not self.entry_prateleira.get().strip():
                messagebox.showwarning("Validação", "Digite a prateleira (ex: A, B, C)")
                return False
        elif tipo == "faixa":
            if not self.entry_faixa_inicio.get().strip() or not self.entry_faixa_fim.get().strip():
                messagebox.showwarning("Validação", "Digite o início e fim da faixa")
                return False
        elif tipo == "especifica":
            if not self.entry_especifica.get().strip():
                messagebox.showwarning("Validação", "Digite a localização específica")
                return False
        
        return True
    
    def _construir_query(self):
        """Constrói a query SQL conforme filtros"""
        tipo = self.filtro_tipo.get()
        
        # Filtro de localização
        if tipo == "prateleira":
            prateleira = self.entry_prateleira.get().strip().upper()
            where_loc = f"UPPER(PROD_LOCALIZACAOPECA) LIKE '{prateleira}%'"
        elif tipo == "faixa":
            inicio = self.entry_faixa_inicio.get().strip().upper()
            fim = self.entry_faixa_fim.get().strip().upper()
            where_loc = f"UPPER(PROD_LOCALIZACAOPECA) BETWEEN '{inicio}' AND '{fim}'"
        elif tipo == "especifica":
            loc = self.entry_especifica.get().strip().upper()
            where_loc = f"UPPER(PROD_LOCALIZACAOPECA) = '{loc}'"
        else:  # todas
            where_loc = "1=1"
        
        # Filtro de estoque
        if not self.check_sem_estoque.get():
            where_estoque = "AND PROD_QTDEESTOQUEFISICO > 0"
        else:
            where_estoque = ""
        
        query = f"""
        SELECT 
            PROD_CODIGO,
            PROD_DESCRICAOPRODUTO,
            PROD_MARCA,
            PROD_CODIGOFABRICANTE,
            PROD_LOCALIZACAOPECA,
            PROD_QTDEESTOQUEFISICO,
            PROD_PRECOAVISTA,
            (PROD_QTDEESTOQUEFISICO * PROD_PRECOAVISTA) AS VALOR_TOTAL
        FROM PRODUTO
        WHERE {where_loc} {where_estoque}
        ORDER BY PROD_LOCALIZACAOPECA, PROD_DESCRICAOPRODUTO
        """
        
        return query
    
    def _buscar_dados(self):
        """Busca dados do banco"""
        if not self._validar_filtros():
            return None
        
        try:
            query = self._construir_query()
            
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning)
                df = pd.read_sql(query, self.db.get_connection())
            
            if df.empty:
                messagebox.showinfo("Sem Dados", "Nenhum produto encontrado com os filtros selecionados")
                return None
            
            return df
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar dados:\n{str(e)}")
            return None
    
    def _visualizar(self):
        """Abre janela de visualização dos dados"""
        df = self._buscar_dados()
        if df is None:
            return
        
        # Criar janela de preview
        PreviewWindow(self.window, df, 
                      agrupar=self.check_agrupar.get(),
                      exibir_unitario=self.check_exibir_unitario.get(),
                      exibir_total=self.check_exibir_total.get())
    
    def _gerar_pdf(self):
        """Gera relatório em PDF"""
        df = self._buscar_dados()
        if df is None:
            return
        
        try:
            from relatorios.pdf_generator import gerar_pdf_localizacao
            
            # Escolher onde salvar
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                initialfile=f"relatorio_localizacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )
            
            if filename:
                gerar_pdf_localizacao(df, filename, 
                                     agrupar=self.check_agrupar.get(),
                                     exibir_unitario=self.check_exibir_unitario.get(),
                                     exibir_total=self.check_exibir_total.get())
                messagebox.showinfo("Sucesso", f"PDF gerado com sucesso!\n{filename}")
                
                # Abrir arquivo
                os.startfile(filename)
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar PDF:\n{str(e)}")
    
    def _gerar_excel(self):
        """Gera relatório em Excel"""
        df = self._buscar_dados()
        if df is None:
            return
        
        try:
            from relatorios.excel_generator import gerar_excel_localizacao
            
            # Escolher onde salvar
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=f"relatorio_localizacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )
            
            if filename:
                gerar_excel_localizacao(df, filename, 
                                       agrupar=self.check_agrupar.get(),
                                       exibir_unitario=self.check_exibir_unitario.get(),
                                       exibir_total=self.check_exibir_total.get())
                messagebox.showinfo("Sucesso", f"Excel gerado com sucesso!\n{filename}")
                
                # Abrir arquivo
                os.startfile(filename)
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar Excel:\n{str(e)}")
