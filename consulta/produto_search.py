import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import pandas as pd
import sys
import os

# Adicionar o diretório pai ao path para importar módulos do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import FirebirdDB
from consulta.queries import BUSCAR_PRODUTO, HISTORICO_COMPRAS, PRECO_MEDIO_COMPRAS
import config

class ProdutoSearchWindow:
    def __init__(self, parent):
        self.parent = parent
        self.current_produto_codigo = None
        
        # Criar janela
        self.window = tk.Toplevel(parent)
        self.window.title("Consulta de Produtos")
        self.window.geometry("900x700")
        
        # Centralizar janela
        self._center_window(900, 700)
        
        # Manter janela sempre visível
        self.window.transient(parent)
        self.window.grab_set()
        self.window.focus_force()
        
        self._create_widgets()
    
    def _center_window(self, width, height):
        """Centraliza a janela na tela"""
        self.window.update_idletasks()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = ((screen_height - height) // 2) - 30
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def _create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ===== ÁREA DE BUSCA =====
        search_frame = ttk.LabelFrame(main_frame, text="Buscar Produto", padding="10")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Código, Descrição ou Referência:").pack(side=tk.LEFT, padx=5)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=50)
        search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        search_entry.bind('<Return>', lambda e: self._buscar_produto())
        
        ttk.Button(search_frame, text="🔍 Buscar", command=self._buscar_produto).pack(side=tk.LEFT, padx=5)
        
        # ===== DADOS DO PRODUTO =====
        produto_frame = ttk.LabelFrame(main_frame, text="Dados do Produto", padding="10")
        produto_frame.pack(fill=tk.BOTH, pady=(0, 10))
        
        # Frame interno com 2 colunas
        inner_frame = ttk.Frame(produto_frame)
        inner_frame.pack(fill=tk.BOTH, expand=True)
        
        # Coluna 1: Imagem (placeholder)
        img_frame = ttk.Frame(inner_frame, relief=tk.SUNKEN, borderwidth=2)
        img_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        self.img_label = ttk.Label(img_frame, text="[Imagem\ndo\nProduto]", 
                                   width=15, anchor=tk.CENTER, background="lightgray")
        self.img_label.pack(padx=20, pady=20)
        
        # Coluna 2: Dados
        dados_frame = ttk.Frame(inner_frame)
        dados_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Labels de dados
        self.lbl_codigo = ttk.Label(dados_frame, text="Código: -", font=("Arial", 10))
        self.lbl_codigo.pack(anchor=tk.W, pady=2)
        
        self.lbl_descricao = ttk.Label(dados_frame, text="Descrição: -", font=("Arial", 10))
        self.lbl_descricao.pack(anchor=tk.W, pady=2)
        
        self.lbl_aplicacao = ttk.Label(dados_frame, text="Aplicação: -", font=("Arial", 10))
        self.lbl_aplicacao.pack(anchor=tk.W, pady=2)
        
        self.lbl_referencia = ttk.Label(dados_frame, text="Referência: -", font=("Arial", 10))
        self.lbl_referencia.pack(anchor=tk.W, pady=2)
        
        self.lbl_estoque = ttk.Label(dados_frame, text="Estoque: -", font=("Arial", 10, "bold"), foreground="blue")
        self.lbl_estoque.pack(anchor=tk.W, pady=2)
        
        self.lbl_preco = ttk.Label(dados_frame, text="Preço de Venda: -", font=("Arial", 10, "bold"), foreground="green")
        self.lbl_preco.pack(anchor=tk.W, pady=2)
        
        self.lbl_localizacao = ttk.Label(dados_frame, text="Localização: -", font=("Arial", 10))
        self.lbl_localizacao.pack(anchor=tk.W, pady=2)
        
        # ===== HISTÓRICO DE COMPRAS =====
        historico_frame = ttk.LabelFrame(main_frame, text="Histórico de Compras", padding="10")
        historico_frame.pack(fill=tk.BOTH, expand=True)
        
        # Controles do histórico
        controles_frame = ttk.Frame(historico_frame)
        controles_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(controles_frame, text="Mostrar:").pack(side=tk.LEFT, padx=5)
        
        self.qtd_compras_var = tk.StringVar(value="5")
        qtd_combo = ttk.Combobox(controles_frame, textvariable=self.qtd_compras_var, 
                                 values=["5", "10", "20", "Todas"], width=10, state='readonly')
        qtd_combo.pack(side=tk.LEFT, padx=5)
        qtd_combo.bind('<<ComboboxSelected>>', lambda e: self._atualizar_historico())
        
        ttk.Label(controles_frame, text="compras").pack(side=tk.LEFT, padx=5)
        
        # Label de preço médio
        self.lbl_preco_medio = ttk.Label(controles_frame, text="Preço Médio: R$ 0,00", 
                                         font=("Arial", 10, "bold"), foreground="darkgreen")
        self.lbl_preco_medio.pack(side=tk.RIGHT, padx=10)
        
        # Tabela de histórico
        table_frame = ttk.Frame(historico_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        hsb = ttk.Scrollbar(table_frame, orient="horizontal")
        
        # Treeview
        self.tree = ttk.Treeview(table_frame, 
                                 columns=("data", "fornecedor", "qtd", "preco", "nf"),
                                 show="headings",
                                 yscrollcommand=vsb.set,
                                 xscrollcommand=hsb.set)
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Colunas
        self.tree.heading("data", text="Data")
        self.tree.heading("fornecedor", text="Fornecedor")
        self.tree.heading("qtd", text="Qtd")
        self.tree.heading("preco", text="Preço Unit.")
        self.tree.heading("nf", text="Nota Fiscal")
        
        self.tree.column("data", width=100, anchor=tk.CENTER)
        self.tree.column("fornecedor", width=200, anchor=tk.W)
        self.tree.column("qtd", width=80, anchor=tk.CENTER)
        self.tree.column("preco", width=100, anchor=tk.E)
        self.tree.column("nf", width=150, anchor=tk.W)
        
        # Grid
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Botão fechar
        ttk.Button(main_frame, text="Fechar", command=self.window.destroy).pack(pady=10)
    
    def _buscar_produto(self):
        """Busca o produto no banco de dados"""
        termo_busca = self.search_var.get().strip()
        
        if not termo_busca:
            messagebox.showwarning("Aviso", "Digite um código, descrição ou referência para buscar")
            return
        
        try:
            # Conectar ao banco
            db = FirebirdDB(config.DB_CONFIG)
            if not db.connect():
                messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados")
                return
            
            # Preparar query otimizada com apenas os campos necessários
            query = f"""
            SELECT 
                PROD_CODIGO,
                PROD_DESCRICAOPRODUTO,
                PROD_UNIDADE,
                PROD_CODIGOBARRA,
                PROD_APLICACAO,
                PROD_QTDEESTOQUEFISICO,
                PROD_MINIMO,
                PROD_PRECOAVISTA,
                PROD_PRECOCUSTO,
                PROD_LOCALIZACAOPECA,
                PROD_MARCA,
                PROD_REFERENCIA
            FROM PRODUTO
            WHERE 
                CAST(PROD_CODIGO AS VARCHAR(50)) = '{termo_busca}' OR
                UPPER(PROD_DESCRICAOPRODUTO) LIKE '%{termo_busca.upper()}%' OR
                CAST(PROD_CODIGOBARRA AS VARCHAR(50)) = '{termo_busca}'
            """
            
            # Executar query
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning)
                df = pd.read_sql(query, db.get_connection())
            
            db.close()
            
            if df.empty:
                messagebox.showinfo("Não encontrado", "Nenhum produto encontrado com esse critério")
                self._limpar_dados()
                return
            
            # Pegar primeiro resultado
            produto = df.iloc[0]
            self.current_produto_codigo = produto['PROD_CODIGO']
            
            # Exibir dados
            self._exibir_produto(produto)
            
            # Carregar histórico
            self._atualizar_historico()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar produto:\n{str(e)}")
    
    def _exibir_produto(self, produto):
        """Exibe os dados do produto na interface"""
        self.lbl_codigo.config(text=f"Código: {produto['PROD_CODIGO']}")
        self.lbl_descricao.config(text=f"Descrição: {produto['PROD_DESCRICAOPRODUTO']}")
        self.lbl_aplicacao.config(text=f"Unidade: {produto.get('PROD_UNIDADE', '-') or '-'} | Marca: {produto.get('PROD_MARCA', '-') or '-'}")
        self.lbl_referencia.config(text=f"Referência: {produto.get('PROD_REFERENCIA', '-') or '-'} | Cód. Barras: {produto.get('PROD_CODIGOBARRA', '-') or '-'}")
        
        estoque = produto.get('PROD_QTDEESTOQUEFISICO', 0) or 0
        minimo = produto.get('PROD_MINIMO', 0) or 0
        self.lbl_estoque.config(text=f"Estoque: {estoque} unidades | Mínimo: {minimo}")
        
        preco_venda = produto.get('PROD_PRECOAVISTA', 0) or 0
        preco_custo = produto.get('PROD_PRECOCUSTO', 0) or 0
        self.lbl_preco.config(text=f"Preço Venda: R$ {preco_venda:,.2f} | Custo: R$ {preco_custo:,.2f}")
        
        localizacao = produto.get('PROD_LOCALIZACAOPECA', '-') or '-'
        aplicacao = produto.get('PROD_APLICACAO', '-') or '-'
        self.lbl_localizacao.config(text=f"Localização: {localizacao} | Aplicação: {aplicacao[:50]}...")
    
    def _carregar_imagem(self, foto_blob):
        """Tenta carregar e exibir a imagem do produto (BLOB)"""
        if not foto_blob or pd.isna(foto_blob):
            self.img_label.config(text="[Sem\nImagem]")
            return
        
        try:
            from PIL import Image, ImageTk
            from io import BytesIO
            import fdb
            
            # Se for BlobReader do fdb (Firebird)
            if hasattr(foto_blob, 'read'):
                # Ler o conteúdo do BLOB
                blob_data = foto_blob.read()
                if blob_data:
                    img = Image.open(BytesIO(blob_data))
                    img.thumbnail((150, 150))
                    photo = ImageTk.PhotoImage(img)
                    self.img_label.config(image=photo, text="")
                    self.img_label.image = photo
                else:
                    self.img_label.config(text="[BLOB\nVazio]")
            # Se for bytes diretos
            elif isinstance(foto_blob, (bytes, bytearray)):
                img = Image.open(BytesIO(foto_blob))
                img.thumbnail((150, 150))  # Redimensionar
                photo = ImageTk.PhotoImage(img)
                self.img_label.config(image=photo, text="")
                self.img_label.image = photo  # Manter referência
            # Se for caminho de arquivo (fallback)
            elif isinstance(foto_blob, str):
                import os
                if os.path.exists(foto_blob):
                    img = Image.open(foto_blob)
                    img.thumbnail((150, 150))
                    photo = ImageTk.PhotoImage(img)
                    self.img_label.config(image=photo, text="")
                    self.img_label.image = photo
                else:
                    self.img_label.config(text="[Imagem\nNão\nEncontrada]")
            else:
                self.img_label.config(text="[Formato\nInválido]")
        except Exception as e:
            print(f"Erro ao carregar imagem: {e}")  # Debug
            self.img_label.config(text="[Erro ao\nCarregar\nImagem]")
    
    def _atualizar_historico(self):
        """Atualiza o histórico de compras"""
        if not self.current_produto_codigo:
            return
        
        # Limpar tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            # Conectar ao banco
            db = FirebirdDB(config.DB_CONFIG)
            if not db.connect():
                return
            
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
                df_historico = pd.read_sql(query_historico, db.get_connection())
                df_preco_medio = pd.read_sql(query_preco, db.get_connection())
            
            db.close()
            
            # Exibir histórico
            for _, row in df_historico.iterrows():
                data = row['ENT_DATAENTRADA'].strftime('%d/%m/%Y') if pd.notna(row['ENT_DATAENTRADA']) else '-'
                fornecedor = row['FOR_NOME'] or '-'
                qtd = int(row['ENI_QTDEENTRADA']) if pd.notna(row['ENI_QTDEENTRADA']) else 0
                preco = row['ENI_VALORUNITARIO'] or 0
                nf = row['ENT_NUMERONOTAFISCAL'] or '-'
                
                self.tree.insert('', 'end', values=(
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
        """Limpa todos os dados exibidos"""
        self.current_produto_codigo = None
        self.lbl_codigo.config(text="Código: -")
        self.lbl_descricao.config(text="Descrição: -")
        self.lbl_aplicacao.config(text="Aplicação: -")
        self.lbl_referencia.config(text="Referência: -")
        self.lbl_estoque.config(text="Estoque: -")
        self.lbl_preco.config(text="Preço de Venda: -")
        self.lbl_localizacao.config(text="Localização: -")
        self.lbl_preco_medio.config(text="Preço Médio: R$ 0,00")
        
        for item in self.tree.get_children():
            self.tree.delete(item)
