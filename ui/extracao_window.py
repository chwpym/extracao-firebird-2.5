import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import threading
import os
from datetime import datetime
import sys

# Adicionar o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import FirebirdDB
from core.exporter import DataExporter
import config


class ExtracaoWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Extração de Dados Firebird para Excel")

        # Tamanho da janela
        window_width = 800
        window_height = 800
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Variáveis
        db_path_initial = (
            config.DB_CONFIG["dsn"].split(":")[-1]
            if ":" in config.DB_CONFIG["dsn"]
            else config.DB_CONFIG["dsn"]
        )
        self.db_path = tk.StringVar(value=db_path_initial)
        self.db_user = tk.StringVar(value=config.DB_CONFIG["user"])
        self.db_pass = tk.StringVar(value=config.DB_CONFIG["password"])
        self.dll_path = tk.StringVar(
            value=config.DB_CONFIG.get("fb_library_name", "fbclient.dll")
        )

        # Datas em padrão PT-BR (DD/MM/AAAA)
        self.start_date_str = tk.StringVar(value="01/01/2024")
        self.end_date_str = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        self.tipo_data_var = tk.StringVar(value="VENCIMENTO")

        # Seleção de Entidades
        self.entity_options = {
            "clientes": tk.BooleanVar(value=True),
            "produtos": tk.BooleanVar(value=True),
            "fornecedores": tk.BooleanVar(value=True),
            "entradas_saidas": tk.BooleanVar(value=True),
            "contas_pagar": tk.BooleanVar(value=True),
            "contas_receber": tk.BooleanVar(value=True),
            "contas_receber_aberto": tk.BooleanVar(value=True),
        }

        self.entity_labels = {
            "clientes": "Clientes",
            "produtos": "Produtos",
            "fornecedores": "Fornecedores",
            "entradas_saidas": "Movimentações (Entradas/Saídas)",
            "contas_pagar": "Contas a Pagar",
            "contas_receber": "Contas a Receber (Todos)",
            "contas_receber_aberto": "Contas a Receber (Somente Aberto)",
        }

        self._create_widgets()

    def _auto_format_date(self, entry_widget):
        """Formata automaticamente DD/MM/AAAA mantendo a posição do cursor"""
        current_value = entry_widget.get()
        cursor_pos = entry_widget.index(tk.INSERT)

        if not current_value:
            return

        # Remover tudo que não for dígito
        value_only_digits = "".join(
            filter(str.isdigit, current_value.replace("/", ""))
        )[:8]

        if not value_only_digits:
            entry_widget.delete(0, tk.END)
            return

        formatted = ""
        for i, char in enumerate(value_only_digits):
            if i == 2 or i == 4:
                formatted += "/"
            formatted += char

        if formatted != current_value:
            # Salvar quantidade de dígitos antes do cursor
            digits_before = len(current_value[:cursor_pos].replace("/", ""))

            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, formatted)

            # Recalcular posição do cursor com base nos dígitos e barras adicionadas
            new_pos = digits_before
            if digits_before > 2:
                new_pos += 1
            if digits_before > 4:
                new_pos += 1

            entry_widget.icursor(min(new_pos, len(formatted)))

    def _create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        lbl_title = ttk.Label(
            main_frame,
            text="Extração de Dados Firebird para Excel",
            font=("Helvetica", 14, "bold"),
        )
        lbl_title.pack(pady=(0, 20))

        # Config do Banco
        db_frame = ttk.LabelFrame(
            main_frame, text="Configuração do Banco", padding="15"
        )
        db_frame.pack(fill=tk.X, pady=5)

        ttk.Label(db_frame, text="Arquivo .FDB:").grid(
            row=0, column=0, sticky="w", pady=5
        )
        ttk.Entry(db_frame, textvariable=self.db_path).grid(
            row=0, column=1, sticky="ew", padx=5
        )
        ttk.Button(db_frame, text="Procurar...", command=self._browse_db).grid(
            row=0, column=2, padx=5
        )

        ttk.Label(db_frame, text="Usuário:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(db_frame, textvariable=self.db_user, width=15).grid(
            row=1, column=1, sticky="w", padx=5
        )

        ttk.Label(db_frame, text="Senha:").grid(
            row=1, column=1, sticky="e", padx=(0, 110)
        )
        ttk.Entry(db_frame, textvariable=self.db_pass, show="*", width=15).grid(
            row=1, column=1, sticky="e", padx=5
        )

        ttk.Label(db_frame, text="fbclient.dll:").grid(
            row=2, column=0, sticky="w", pady=5
        )
        ttk.Entry(db_frame, textvariable=self.dll_path).grid(
            row=2, column=1, sticky="ew", padx=5
        )
        ttk.Button(db_frame, text="Procurar...", command=self._browse_dll).grid(
            row=2, column=2, padx=5
        )

        db_frame.columnconfigure(1, weight=1)

        # Filtros
        filter_frame = ttk.LabelFrame(
            main_frame, text="Filtros de Período", padding="15"
        )
        filter_frame.pack(fill=tk.X, pady=5)

        ttk.Label(filter_frame, text="Início (DD/MM/AAAA):").grid(
            row=0, column=0, sticky="w"
        )
        entry_start = ttk.Entry(
            filter_frame, textvariable=self.start_date_str, width=15
        )
        entry_start.grid(row=0, column=1, padx=5, pady=5)
        entry_start.bind("<KeyRelease>", lambda e: self._auto_format_date(entry_start))

        ttk.Label(filter_frame, text="Fim (DD/MM/AAAA):").grid(
            row=0, column=2, sticky="w", padx=(20, 0)
        )
        entry_end = ttk.Entry(filter_frame, textvariable=self.end_date_str, width=15)
        entry_end.grid(row=0, column=3, padx=5, pady=5)
        entry_end.bind("<KeyRelease>", lambda e: self._auto_format_date(entry_end))

        ttk.Label(filter_frame, text="Filtrar por:").grid(
            row=0, column=4, padx=(20, 5), sticky="w"
        )
        ttk.Radiobutton(
            filter_frame,
            text="Vencimento",
            variable=self.tipo_data_var,
            value="VENCIMENTO",
        ).grid(row=0, column=5, padx=5)
        ttk.Radiobutton(
            filter_frame, text="Emissão", variable=self.tipo_data_var, value="EMISSAO"
        ).grid(row=0, column=6, padx=5)

        # Entidades para Extração
        entities_frame = ttk.LabelFrame(
            main_frame, text="Dados para Extrair", padding="15"
        )
        entities_frame.pack(fill=tk.X, pady=5)

        # Grid de Checkboxes (2 colunas)
        row, col = 0, 0
        for entity, var in self.entity_options.items():
            ttk.Checkbutton(
                entities_frame, text=self.entity_labels[entity], variable=var
            ).grid(row=row, column=col, sticky="w", padx=10, pady=2)
            col += 1
            if col > 1:
                col = 0
                row += 1

        # Botão Iniciar
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=15)

        self.btn_start = ttk.Button(
            btn_frame, text="INICIAR EXTRAÇÃO TOTAL", command=self._start_extraction
        )
        self.btn_start.pack(fill=tk.X)

        # Barra de Progresso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame, variable=self.progress_var, maximum=100
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        self.status_var = tk.StringVar(value="Aguardando início...")
        ttk.Label(main_frame, textvariable=self.status_var).pack(pady=(0, 10))

        # Log View
        log_frame = ttk.LabelFrame(main_frame, text="Log de Execução", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_widget = ScrolledText(
            log_frame, height=15, font=("Consolas", 9), state="disabled", bg="#f0f0f0"
        )
        self.log_widget.pack(fill=tk.BOTH, expand=True)

    def _browse_db(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Firebird DB", "*.fdb"), ("All Files", "*.*")]
        )
        if filename:
            self.db_path.set(filename)

    def _browse_dll(self):
        filename = filedialog.askopenfilename(
            filetypes=[("DLL Files", "*.dll"), ("All Files", "*.*")]
        )
        if filename:
            self.dll_path.set(filename)

    def _parse_date(self, date_str):
        """Converte DD/MM/AAAA para AAAA-MM-DD"""
        try:
            return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            return None

    def _log_to_gui(self, message):
        def update():
            self.log_widget.config(state="normal")
            self.log_widget.insert(
                tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n"
            )
            self.log_widget.see(tk.END)
            self.log_widget.config(state="disabled")

        self.window.after(0, update)

    def _start_extraction(self):
        # Validar datas
        start = self._parse_date(self.start_date_str.get())
        end = self._parse_date(self.end_date_str.get())

        if not start or not end:
            messagebox.showerror("Erro", "Formato de data inválido! Use DD/MM/AAAA")
            return

        self.btn_start.config(state="disabled")
        self.progress_var.set(0)
        self.status_var.set("Iniciando...")
        self._log_to_gui(
            f"Extração solicitada para o período: {self.start_date_str.get()} até {self.end_date_str.get()}"
        )

        thread = threading.Thread(target=self._run_extraction_logic, args=(start, end))
        thread.daemon = True
        thread.start()

    def _run_extraction_logic(self, start_dt, end_dt):
        tipo_data = self.tipo_data_var.get()
        try:
            local_config = config.DB_CONFIG.copy()
            db_file = self.db_path.get().replace("\\", "/").strip()

            if ":" in db_file and not any(
                db_file.startswith(p) for p in ["localhost", "127.0.0.1"]
            ):
                dsn = f"127.0.0.1:{db_file}"
            else:
                dsn = db_file

            local_config["dsn"] = dsn
            local_config["user"] = self.db_user.get()
            local_config["password"] = self.db_pass.get()
            local_config["fb_library_name"] = self.dll_path.get()

            self._log_to_gui(f"Conectando a: {dsn}...")

            db = FirebirdDB(local_config)
            if not db.connect():
                self._log_to_gui("ERRO: Falha na conexão.")
                self.window.after(0, lambda: self.btn_start.config(state="normal"))
                return

            exporter = DataExporter(
                db.get_connection(),
                config.OUTPUT_DIR,
                os.path.join(os.path.dirname(__file__), "..", "sql"),
            )

            # Filtrar apenas entidades selecionadas
            all_entities = [
                "clientes",
                "produtos",
                "fornecedores",
                "entradas_saidas",
                "contas_pagar",
                "contas_receber",
                "contas_receber_aberto",
            ]
            entities = [e for e in all_entities if self.entity_options[e].get()]

            if not entities:
                self._log_to_gui("AVISO: Nenhuma entidade selecionada para extração.")
                self.window.after(0, lambda: self.btn_start.config(state="normal"))
                db.close()
                return

            total = len(entities)

            for i, entity in enumerate(entities):
                pct = ((i + 1) / total) * 100
                self.window.after(
                    0,
                    lambda p=pct, e=entity: (
                        self.progress_var.set(p),
                        self.status_var.set(f"Exportando: {e}..."),
                    ),
                )

                self._log_to_gui(f"Processando: {entity}")

                # Definir campo de data conforme o tipo
                campo_sql = None
                if entity == "contas_receber" or entity == "contas_receber_aberto":
                    campo_sql = (
                        "d.RED_DATAVENCIMENTO"
                        if tipo_data == "VENCIMENTO"
                        else "r.REC_DATAEMISSAO"
                    )
                elif entity == "contas_pagar":
                    campo_sql = (
                        "d.PAD_DATAVENCIMENTO"
                        if tipo_data == "VENCIMENTO"
                        else "p.PAG_DATAEMISSAO"
                    )
                else:
                    campo_sql = (
                        None  # Outras entidades podem não usar ou usar campo fixo
                    )

                success = exporter.export_entity(
                    entity, start_dt, end_dt, date_field=campo_sql
                )

                if success:
                    self._log_to_gui(f"Finalizado: {entity}.xlsx")
                else:
                    self._log_to_gui(f"ERRO ao exportar {entity}")

            self.window.after(
                0,
                lambda: (
                    self.progress_var.set(100),
                    self.status_var.set("Finalizado!"),
                ),
            )
            db.close()
            self._log_to_gui("--- PROCESSO FINALIZADO ---")
            messagebox.showinfo("Sucesso", "Extração concluída com sucesso!")

        except Exception as e:
            self._log_to_gui(f"ERRO CRÍTICO: {e}")
            messagebox.showerror("Erro", f"Ocorreu um erro durante a extração:\n{e}")
        finally:
            self.window.after(0, lambda: self.btn_start.config(state="normal"))
