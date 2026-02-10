import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
import sys
from utils.preferences import UserPreferences
import logging


class ExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestão e Extração Firebird")

        # Maximizar janela
        self.root.state("zoomed")

        # Preferências do usuário
        self.prefs = UserPreferences()

        # Estilo
        self.style = ttk.Style()
        saved_theme = self.prefs.get_theme()
        try:
            self.style.theme_use(saved_theme)
        except:
            self.style.theme_use("clam")

        self._create_menu()
        self._create_widgets()

    def _create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Menu Configurar
        config_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Configurar", menu=config_menu)
        config_menu.add_command(
            label="📝 Editar Consultas SQL", command=self._open_sql_editor
        )

        # Menu Ferramentas
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ferramentas", menu=tools_menu)
        tools_menu.add_command(
            label="🚀 Extração de Dados Firebird", command=self._open_extracao
        )
        tools_menu.add_command(
            label="⚡ Otimizar Performance do Kardex", command=self._otimizar_kardex
        )
        tools_menu.add_command(
            label="🛠️ Central de Diagnóstico e Testes", command=self._open_diagnostic
        )

        # Menu Consultas
        consultas_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Consultas", menu=consultas_menu)
        consultas_menu.add_command(
            label="👥 Consultar Clientes", command=self._open_cliente_search
        )
        consultas_menu.add_command(
            label="🏭 Consultar Fornecedores", command=self._open_fornecedor_search
        )
        consultas_menu.add_separator()
        consultas_menu.add_command(
            label="🔍 Consultar Produto (Detalhada)", command=self._open_produto_search
        )
        consultas_menu.add_command(
            label="⚡ Consultar Produto (Rápida)", command=self._open_produto_listagem
        )
        consultas_menu.add_separator()
        consultas_menu.add_command(
            label="📊 Consultar Movimentações (Kardex)",
            command=self._open_movimentacao_search,
        )
        consultas_menu.add_command(
            label="💰 Consultar Vendas (Pedidos)", command=self._open_pedido_search
        )
        consultas_menu.add_command(
            label="📦 Consultar Entrada de NF", command=self._open_entrada_nf_search
        )
        consultas_menu.add_command(
            label="💰 Consultar Contas a Receber",
            command=self._open_contas_receber_search,
        )

        # Menu Relatórios
        relatorios_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Relatórios", menu=relatorios_menu)
        relatorios_menu.add_command(
            label="📍 Relatório de Localização",
            command=self._open_relatorio_localizacao,
        )
        relatorios_menu.add_command(
            label="💰 Faturamento por Cliente", command=self._open_faturamento_cliente
        )

        # Menu Temas
        theme_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Temas", menu=theme_menu)
        for t in self.style.theme_names():
            theme_menu.add_command(
                label=t, command=lambda theme=t: self._apply_theme(theme)
            )

        # Menu Ajuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        help_menu.add_command(label="📖 Manual de Uso", command=self._show_manual)
        help_menu.add_command(
            label="💻 Comandos SQL Firebird", command=self._show_sql_commands
        )
        help_menu.add_separator()
        help_menu.add_command(
            label="🌐 Documentação Online", command=self._open_documentation
        )

    def _create_widgets(self):
        """Cria o Dashboard principal"""
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Frame centralizado
        center_frame = ttk.Frame(self.main_container)
        center_frame.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

        lbl_welcome = ttk.Label(
            center_frame, text="BEM-VINDO AO SISTEMA", font=("Helvetica", 20, "bold")
        )
        lbl_welcome.pack(pady=20)

        lbl_subtitle = ttk.Label(
            center_frame,
            text="Selecione uma ferramenta no menu acima ou use os atalhos abaixo:",
            font=("Helvetica", 11),
        )
        lbl_subtitle.pack(pady=(0, 40))

        # Grade de botões de atalho
        btn_grid = ttk.Frame(center_frame)
        btn_grid.pack()

        # Configuração dos botões (Texto, Ícone/Símbolo, Comando, Cor de fundo simulada por estilo)
        shortcuts = [
            ("📊 Kardex\nMovimentações", self._open_movimentacao_search),
            ("🚀 Extração\nde Dados", self._open_extracao),
            ("👥 Consultar\nClientes", self._open_cliente_search),
            ("🏭 Consultar\nFornecedores", self._open_fornecedor_search),
            ("🔍 Consultar\nProduto", self._open_produto_search),
            ("💰 Consultar\nVendas", self._open_pedido_search),
            ("📦 Consultar\nEntrada de NF", self._open_entrada_nf_search),
            ("💰 Contas\na Receber", self._open_contas_receber_search),
            ("📍 Relatório\nLocalização", self._open_relatorio_localizacao),
            ("🛠️ Diagnóstico\ne Testes", self._open_diagnostic),
        ]

        row, col = 0, 0
        for text, cmd in shortcuts:
            btn = ttk.Button(btn_grid, text=text, width=20, command=cmd)
            btn.grid(row=row, column=col, padx=10, pady=10, ipady=10)
            col += 1
            if col > 2:
                col = 0
                row += 1

    def _open_extracao(self):
        from ui.extracao_window import ExtracaoWindow

        ExtracaoWindow(self.root)

    def _open_sql_editor(self):
        from ui.sql_editor import SQLEditorWindow

        sql_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sql"
        )
        SQLEditorWindow(self.root, sql_dir)

    def _open_diagnostic(self):
        from ui.diagnostic_window import DiagnosticWindow

        DiagnosticWindow(self.root)

    def _otimizar_kardex(self):
        import subprocess
        import threading
        from tkinter import messagebox

        resposta = messagebox.askyesno(
            "Otimizar Performance do Kardex",
            "Esta operação irá criar índices no banco de dados para melhorar a performance do Kardex.\n\nDeseja continuar?",
        )
        if not resposta:
            return

        progress_window = tk.Toplevel(self.root)
        progress_window.title("Otimizando...")
        progress_window.geometry("400x150")
        progress_window.transient(self.root)
        progress_window.grab_set()

        # Centralizar
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 200
        y = (self.root.winfo_screenheight() // 2) - 75
        progress_window.geometry(f"+{x}+{y}")

        tk.Label(
            progress_window,
            text="Criando índices no banco de dados...",
            font=("Arial", 10),
        ).pack(pady=30)

        def executar():
            try:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                script_path = os.path.join(base_dir, "scripts", "otimizar_kardex.py")
                result = subprocess.run(
                    ["python", script_path],
                    capture_output=True,
                    text=True,
                    cwd=base_dir,
                )
                progress_window.destroy()
                if result.returncode == 0:
                    messagebox.showinfo("Sucesso", "Índices criados com sucesso!")
                else:
                    messagebox.showerror(
                        "Erro", f"Erro: {result.stderr or result.stdout}"
                    )
            except Exception as e:
                if progress_window.winfo_exists():
                    progress_window.destroy()
                messagebox.showerror("Erro", str(e))

        threading.Thread(target=executar, daemon=True).start()

    def _otimizar_faturamento(self):
        import subprocess
        import threading
        from tkinter import messagebox

        resposta = messagebox.askyesno(
            "Otimizar Performance do Faturamento",
            "Esta operação irá criar índices no banco de dados para melhorar a performance do Relatório de Faturamento.\\n\\nDeseja continuar?",
        )
        if not resposta:
            return

        progress_window = tk.Toplevel(self.root)
        progress_window.title("Otimizando...")
        progress_window.geometry("400x150")
        progress_window.transient(self.root)
        progress_window.grab_set()

        # Centralizar
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 200
        y = (self.root.winfo_screenheight() // 2) - 75
        progress_window.geometry(f"+{x}+{y}")

        tk.Label(
            progress_window,
            text="Criando índices no banco de dados...",
            font=("Arial", 10),
        ).pack(pady=30)

        def executar():
            try:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                script_path = os.path.join(
                    base_dir, "scripts", "otimizar_faturamento.py"
                )
                result = subprocess.run(
                    ["python", script_path],
                    capture_output=True,
                    text=True,
                    cwd=base_dir,
                )
                progress_window.destroy()
                if result.returncode == 0:
                    messagebox.showinfo(
                        "Sucesso",
                        "Índices criados com sucesso!\\nA performance do Relatório de Faturamento deve melhorar significativamente.",
                    )
                else:
                    messagebox.showerror(
                        "Erro", f"Erro: {result.stderr or result.stdout}"
                    )
            except Exception as e:
                if progress_window.winfo_exists():
                    progress_window.destroy()
                messagebox.showerror("Erro", str(e))

        threading.Thread(target=executar, daemon=True).start()

    def _open_produto_search(self):
        from consulta.produto_search import ProdutoSearchWindow

        ProdutoSearchWindow(self.root)

    def _open_cliente_search(self):
        from consulta.cliente_search import ClienteSearchWindow

        ClienteSearchWindow(self.root)

    def _open_fornecedor_search(self):
        from consulta.fornecedor_search import FornecedorSearchWindow

        FornecedorSearchWindow(self.root)

    def _open_movimentacao_search(self):
        from consulta.movimentacao_search import MovimentacaoSearchWindow

        MovimentacaoSearchWindow(self.root)

    def _open_pedido_search(self):
        from consulta.pedido_search import PedidoSearchWindow

        PedidoSearchWindow(self.root)

    def _open_entrada_nf_search(self):
        from consulta.entrada_nf_search import EntradaNFSearchWindow

        EntradaNFSearchWindow(self.root)

    def _open_contas_receber_search(self):
        from consulta.contas_receber_search import ContasReceberSearchWindow

        ContasReceberSearchWindow(self.root)

    def _open_produto_listagem(self):
        from consulta.produto_listagem import ProdutoListagemWindow

        ProdutoListagemWindow(self.root)

    def _open_relatorio_localizacao(self):
        from relatorios.localizacao import RelatorioLocalizacaoWindow

        RelatorioLocalizacaoWindow(self.root)

    def _open_faturamento_cliente(self):
        from relatorios.faturamento_cliente import FaturamentoClienteWindow

        FaturamentoClienteWindow(self.root)

    def _show_manual(self):
        from ui.help_window import HelpWindow

        HelpWindow(self.root, "manual")

    def _show_sql_commands(self):
        from ui.help_window import HelpWindow

        HelpWindow(self.root, "sql_commands")

    def _open_documentation(self):
        from ui.help_window import open_documentation

        open_documentation()

    def _apply_theme(self, theme_name):
        try:
            self.style.theme_use(theme_name)
            self.prefs.set_theme(theme_name)
        except tk.TclError:
            messagebox.showwarning("Aviso", f"Tema '{theme_name}' não disponível.")
