import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import threading
import os
from datetime import datetime
from core.database import FirebirdDB
from core.exporter import DataExporter
import config
import logging

class ExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Extrator Firebird 2.5 - Original Auto Peças")
        self.root.geometry("800x700")
        
        # Estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        db_path_initial = config.DB_CONFIG['dsn'].split(':')[-1] if ':' in config.DB_CONFIG['dsn'] else config.DB_CONFIG['dsn']
        self.db_path = tk.StringVar(value=db_path_initial)
        self.db_user = tk.StringVar(value=config.DB_CONFIG['user'])
        self.db_pass = tk.StringVar(value=config.DB_CONFIG['password'])
        
        # Datas em padrão PT-BR (DD/MM/AAAA)
        self.start_date_str = tk.StringVar(value="01/01/2024")
        self.end_date_str = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        
        self._create_widgets()
        self._create_menu()
        
    def _create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Temas
        theme_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Temas", menu=theme_menu)
        
        # Adiciona todos os temas disponíveis + 'arc' se não estiver na lista
        available_themes = list(self.style.theme_names())
        if 'arc' not in available_themes:
            available_themes.append('arc')
            
        for t in available_themes:
            theme_menu.add_command(label=t, command=lambda theme=t: self._apply_theme(theme))

        # Menu Ferramentas
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ferramentas", menu=tools_menu)
        
        tools_menu.add_command(label="Verificar Contagem de Tabelas", command=lambda: self._run_tool("check_counts.py"))
        tools_menu.add_command(label="Inspecionar Banco (Tabelas)", command=lambda: self._run_tool("inspect_db.py"))
        tools_menu.add_command(label="Testar Nomes no Pagar", command=lambda: self._run_tool("test_pagar_names.py"))

    def _apply_theme(self, theme_name):
        """Aplica o tema selecionado"""
        try:
            self.style.theme_use(theme_name)
        except tk.TclError:
            messagebox.showwarning("Tema Indisponível", f"O tema '{theme_name}' não está disponível neste sistema.")

    def _run_tool(self, script_name):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        script_path = os.path.join(base_dir, 'tools', script_name)
        
        if not os.path.exists(script_path):
            messagebox.showerror("Erro", f"Script não encontrado: {script_path}")
            return
            
        self._log_to_gui(f"Executando ferramenta: {script_name}...")
        
        def run():
            import subprocess
            try:
                # Importante: rodar no base_dir para que imports funcionem se necessário
                result = subprocess.run(['python', script_path], capture_output=True, text=True, encoding='latin-1', cwd=base_dir)
                self._log_to_gui(f"--- Fim da ferramenta {script_name} ---")
                if result.stdout:
                    self._log_to_gui(result.stdout)
                if result.stderr:
                    self._log_to_gui(f"ERRO:\n{result.stderr}")
            except Exception as e:
                self._log_to_gui(f"Erro ao rodar ferramenta: {e}")
                
        threading.Thread(target=run, daemon=True).start()

    def _auto_format_date(self, var, event=None):
        """Formata automaticamente DD/MM/AAAA enquanto o usuário digita"""
        value = var.get().replace("/", "")  # Remove barras existentes
        
        # Limita a 8 dígitos
        if len(value) > 8:
            value = value[:8]
        
        # Formata com barras
        formatted = ""
        for i, char in enumerate(value):
            if i == 2 or i == 4:
                formatted += "/"
            formatted += char
        
        var.set(formatted)
        
    def _create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        lbl_title = ttk.Label(main_frame, text="Extração de Dados Firebird para Excel", font=("Helvetica", 14, "bold"))
        lbl_title.pack(pady=(0, 20))
        
        # Config do Banco
        db_frame = ttk.LabelFrame(main_frame, text="Configuração do Banco", padding="15")
        db_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(db_frame, text="Arquivo .FDB:").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(db_frame, textvariable=self.db_path).grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(db_frame, text="Procurar...", command=self._browse_db).grid(row=0, column=2, padx=5)
        
        ttk.Label(db_frame, text="Usuário:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(db_frame, textvariable=self.db_user, width=15).grid(row=1, column=1, sticky="w", padx=5)
        
        ttk.Label(db_frame, text="Senha:").grid(row=1, column=1, sticky="e", padx=(0, 110))
        ttk.Entry(db_frame, textvariable=self.db_pass, show="*", width=15).grid(row=1, column=1, sticky="e", padx=5)
        
        db_frame.columnconfigure(1, weight=1)
        
        # Filtros
        filter_frame = ttk.LabelFrame(main_frame, text="Filtros de Período", padding="15")
        filter_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(filter_frame, text="Início (DD/MM/AAAA):").grid(row=0, column=0, sticky="w")
        entry_start = ttk.Entry(filter_frame, textvariable=self.start_date_str, width=15)
        entry_start.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Fim (DD/MM/AAAA):").grid(row=0, column=2, sticky="w", padx=(20, 0))
        entry_end = ttk.Entry(filter_frame, textvariable=self.end_date_str, width=15)
        entry_end.grid(row=0, column=3, padx=5, pady=5)
        
        # Adiciona auto-formatação às datas
        self.start_date_str.trace_add("write", lambda *args: self._auto_format_date(self.start_date_str))
        self.end_date_str.trace_add("write", lambda *args: self._auto_format_date(self.end_date_str))
        
        # Botão Iniciar
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=15)
        
        self.btn_start = ttk.Button(btn_frame, text="INICIAR EXTRAÇÃO TOTAL", command=self._start_extraction)
        self.btn_start.pack(fill=tk.X)
        
        # Barra de Progresso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        self.status_var = tk.StringVar(value="Aguardando início...")
        ttk.Label(main_frame, textvariable=self.status_var).pack(pady=(0, 10))
        
        # Log View
        log_frame = ttk.LabelFrame(main_frame, text="Log de Execução", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_widget = ScrolledText(log_frame, height=15, font=("Consolas", 9), state='disabled', bg="#f0f0f0")
        self.log_widget.pack(fill=tk.BOTH, expand=True)
        
    def _browse_db(self):
        filename = filedialog.askopenfilename(filetypes=[("Firebird DB", "*.fdb"), ("All Files", "*.*")])
        if filename:
            self.db_path.set(filename)

    def _parse_date(self, date_str):
        """Converte DD/MM/AAAA para AAAA-MM-DD"""
        try:
            return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            return None

    def _log_to_gui(self, message):
        def update():
            self.log_widget.config(state='normal')
            self.log_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
            self.log_widget.see(tk.END)
            self.log_widget.config(state='disabled')
        self.root.after(0, update)

    def _start_extraction(self):
        # Validar datas
        start = self._parse_date(self.start_date_str.get())
        end = self._parse_date(self.end_date_str.get())
        
        if not start or not end:
            messagebox.showerror("Erro", "Formato de data inválido! Use DD/MM/AAAA")
            return
            
        self.btn_start.config(state='disabled')
        self.progress_var.set(0)
        self.status_var.set("Iniciando...")
        self._log_to_gui(f"Extração solicitada para o período: {self.start_date_str.get()} até {self.end_date_str.get()}")
        
        thread = threading.Thread(target=self._run_extraction_logic, args=(start, end))
        thread.daemon = True
        thread.start()
        
    def _run_extraction_logic(self, start_dt, end_dt):
        try:
            local_config = config.DB_CONFIG.copy()
            db_file = self.db_path.get().replace('\\', '/').strip()
            
            if ":" in db_file and not any(db_file.startswith(p) for p in ["localhost", "127.0.0.1"]):
                dsn = f"127.0.0.1:{db_file}"
            else:
                dsn = db_file
            
            local_config['dsn'] = dsn
            local_config['user'] = self.db_user.get()
            local_config['password'] = self.db_pass.get()
            
            self._log_to_gui(f"Conectando a: {dsn}...")
            
            db = FirebirdDB(local_config)
            if not db.connect():
                self._log_to_gui("ERRO: Falha na conexão.")
                self.root.after(0, lambda: self.btn_start.config(state='normal'))
                return

            exporter = DataExporter(db.get_connection(), config.OUTPUT_DIR, os.path.join(os.path.dirname(__file__), '..', 'sql'))
            
            entities = ['clientes', 'produtos', 'fornecedores', 'entradas_saidas', 'contas_pagar', 'contas_receber']
            total = len(entities)
            
            for i, entity in enumerate(entities):
                pct = ((i + 1) / total) * 100 # Adjusted to show progress for current entity
                self.root.after(0, lambda p=pct, e=entity: (self.progress_var.set(p), self.status_var.set(f"Exportando: {e}...")))
                
                self._log_to_gui(f"Processando: {entity}")
                success = exporter.export_entity(entity, start_dt, end_dt) # Pass start_dt and end_dt
                
                if success:
                    self._log_to_gui(f"Finalizado: {entity}.xlsx")
                else:
                    self._log_to_gui(f"ERRO ao exportar {entity}")

            self.root.after(0, lambda: (self.progress_var.set(100), self.status_var.set("Finalizado!")))
            db.close()
            self._log_to_gui("--- PROCESSO FINALIZADO ---")
            messagebox.showinfo("Sucesso", "Extração concluída com sucesso!")
            
        except Exception as e:
            self._log_to_gui(f"ERRO CRÍTICO: {e}")
            messagebox.showerror("Erro", f"Ocorreu um erro durante a extração:\n{e}")
        finally:
            self.root.after(0, lambda: self.btn_start.config(state='normal'))
