import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import pandas as pd
from datetime import datetime
from core.database import FirebirdDB
import config
import os


class ContasReceberSearchWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Consulta de Contas a Receber")
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

        self.df_resultados = pd.DataFrame()
        self.current_item = None

        self._create_widgets()

        # Fechar conexão ao fechar janela
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # === BUSCA ===
        search_frame = ttk.LabelFrame(main_frame, text="Filtros de Busca", padding="10")
        search_frame.pack(fill=tk.X, pady=(0, 10))

        # Linha 1
        ttk.Label(search_frame, text="IDs Clientes:").grid(
            row=0, column=0, sticky="w", padx=5
        )
        self.txt_clientes = ttk.Entry(search_frame, width=30)
        self.txt_clientes.grid(row=0, column=1, sticky="w", padx=5)
        ttk.Label(
            search_frame,
            text="(Separe por vírgula, ex: 834, 123)",
            font=("Arial", 8, "italic"),
        ).grid(row=0, column=2, sticky="w")

        self.situacao_var = tk.StringVar(value="ABERTO")

        radio_frame = ttk.Frame(search_frame)
        radio_frame.grid(row=0, column=3, padx=20, sticky="w")

        ttk.Radiobutton(
            radio_frame, text="Em Aberto", variable=self.situacao_var, value="ABERTO"
        ).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(
            radio_frame, text="Pagos", variable=self.situacao_var, value="PAGO"
        ).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(
            radio_frame, text="Todos", variable=self.situacao_var, value="TODOS"
        ).pack(side=tk.LEFT, padx=5)

        ttk.Label(search_frame, text="Filtrar por:").grid(
            row=0, column=4, padx=(20, 5), sticky="e"
        )
        self.tipo_data_var = tk.StringVar(value="VENCIMENTO")
        tipo_data_frame = ttk.Frame(search_frame)
        tipo_data_frame.grid(row=0, column=5, sticky="w")
        ttk.Radiobutton(
            tipo_data_frame,
            text="Vencimento",
            variable=self.tipo_data_var,
            value="VENCIMENTO",
        ).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(
            tipo_data_frame,
            text="Emissão",
            variable=self.tipo_data_var,
            value="EMISSAO",
        ).pack(side=tk.LEFT, padx=5)

        # Linha 2: Datas
        date_group_frame = ttk.Frame(search_frame)
        date_group_frame.grid(row=1, column=0, columnspan=4, sticky="w")

        ttk.Label(date_group_frame, text="Venc. Início:").pack(
            side=tk.LEFT, padx=(5, 5)
        )
        self.txt_data_inicio = ttk.Entry(date_group_frame, width=12)
        self.txt_data_inicio.pack(side=tk.LEFT, padx=5)
        self.txt_data_inicio.insert(0, "01/01/2020")
        self.txt_data_inicio.bind(
            "<KeyRelease>", lambda e: self._auto_format_date(self.txt_data_inicio)
        )

        ttk.Label(date_group_frame, text="Venc. Fim:").pack(side=tk.LEFT, padx=(20, 5))
        self.txt_data_fim = ttk.Entry(date_group_frame, width=12)
        self.txt_data_fim.pack(side=tk.LEFT, padx=5)
        self.txt_data_fim.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.txt_data_fim.bind(
            "<KeyRelease>", lambda e: self._auto_format_date(self.txt_data_fim)
        )

        # Botões
        btn_frame = ttk.Frame(search_frame)
        btn_frame.grid(row=1, column=4, sticky="e", padx=5)
        ttk.Button(btn_frame, text="🔍 Buscar", command=self._buscar).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(btn_frame, text="🗑️ Limpar", command=self._limpar).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(
            btn_frame, text="📊 Exportar Excel", command=self._exportar_excel
        ).pack(side=tk.LEFT, padx=5)

        search_frame.columnconfigure(4, weight=1)

        # === TABELA ===
        table_frame = ttk.LabelFrame(main_frame, text="Contas a Receber", padding="5")
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)

        columns = (
            "op",
            "nf",
            "emissao",
            "cod_cli",
            "cliente",
            "parcela",
            "vencimento",
            "valor",
            "recebido",
            "data_rec",
            "tpf",
        )
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
        )

        headers = {
            "op": "Nº Op",
            "nf": "Nº NF",
            "emissao": "Emissão",
            "cod_cli": "Cód Cli",
            "cliente": "Nome Cliente",
            "parcela": "Parc",
            "vencimento": "Vencimento",
            "valor": "R$ Parcela",
            "recebido": "R$ Recebido",
            "data_rec": "Data Rec.",
            "tpf": "TPF-Recebido",
        }

        for col, head in headers.items():
            self.tree.heading(
                col, text=head, command=lambda c=col: self._sort_column(c, False)
            )
            width = 100 if col != "cliente" else 300
            anchor = (
                "center"
                if col not in ["cliente", "valor", "recebido", "tpf"]
                else ("w" if col == "cliente" else ("center" if col == "tpf" else "e"))
            )
            self.tree.column(col, width=width, anchor=anchor)

        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # === DETALHES ===
        details_frame = ttk.LabelFrame(
            main_frame, text="Histórico / Observações", padding="10"
        )
        details_frame.pack(fill=tk.X)

        self.txt_historico = ScrolledText(
            details_frame, height=5, font=("Arial", 9), state=tk.DISABLED
        )
        self.txt_historico.pack(fill=tk.BOTH, expand=True)

    def _auto_format_date(self, entry_widget):
        """Formata automaticamente DD/MM/AAAA mantendo a posição do cursor"""
        current_value = entry_widget.get()
        cursor_pos = entry_widget.index(tk.INSERT)

        if not current_value:
            return

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
            digits_before = len(current_value[:cursor_pos].replace("/", ""))

            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, formatted)

            new_pos = digits_before
            if digits_before > 2:
                new_pos += 1
            if digits_before > 4:
                new_pos += 1

            entry_widget.icursor(min(new_pos, len(formatted)))

    def _buscar(self):
        data_ini_str = self.txt_data_inicio.get().strip()
        data_fim_str = self.txt_data_fim.get().strip()
        clientes_str = self.txt_clientes.get().strip()
        situacao = self.situacao_var.get()
        tipo_data = self.tipo_data_var.get()

        try:
            dt_ini = datetime.strptime(data_ini_str, "%d/%m/%Y").strftime("%Y-%m-%d")
            dt_fim = datetime.strptime(data_fim_str, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Erro", "Datas inválidas! Use DD/MM/AAAA")
            return

        sql_map = {
            "ABERTO": "contas_receber_aberto.sql",
            "PAGO": "contas_receber_pago.sql",
            "TODOS": "contas_receber.sql",
        }
        sql_file = sql_map.get(situacao, "contas_receber.sql")
        sql_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "sql", sql_file
        )

        try:
            with open(sql_path, "r", encoding="utf-8") as f:
                query = f.read()

            query = query.replace(":DATA_INI", f"'{dt_ini}'")
            query = query.replace(":DATA_FIM", f"'{dt_fim}'")

            campo_sql = (
                "d.RED_DATAVENCIMENTO"
                if tipo_data == "VENCIMENTO"
                else "r.REC_DATAEMISSAO"
            )
            query = query.replace(":CAMPO_DATA", campo_sql)

            if clientes_str:
                # Processar IDs de clientes
                ids = [
                    id.strip()
                    for id in clientes_str.replace(",", " ").split()
                    if id.strip().isdigit()
                ]
                if ids:
                    ids_list = ",".join(ids)
                    if "ORDER BY" in query:
                        query = query.replace(
                            "ORDER BY", f"AND r.CLI_CODIGO IN ({ids_list}) ORDER BY"
                        )
                    else:
                        query += f" AND r.CLI_CODIGO IN ({ids_list})"

            cursor = self.db.get_connection().cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

            cols = [desc[0] for desc in cursor.description]
            self.df_resultados = pd.DataFrame(rows, columns=cols)

            self._atualizar_tabela()

        except Exception as e:
            messagebox.showerror("Erro na busca", str(e))

    def _atualizar_tabela(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if self.df_resultados.empty:
            messagebox.showinfo("Aviso", "Nenhum resultado encontrado.")
            return

        for idx, row in self.df_resultados.iterrows():
            d_emissao = (
                row["REC_DATAEMISSAO"].strftime("%d/%m/%Y")
                if pd.notna(row["REC_DATAEMISSAO"])
                else ""
            )
            d_venc = (
                row["RED_DATAVENCIMENTO"].strftime("%d/%m/%Y")
                if pd.notna(row["RED_DATAVENCIMENTO"])
                else ""
            )
            d_rec = (
                row["DATA_REC_REAL"].strftime("%d/%m/%Y")
                if pd.notna(row["DATA_REC_REAL"])
                else ""
            )
            tpf = row["TPF_RECEBIDO"] if pd.notna(row["TPF_RECEBIDO"]) else ""

            v_parc = (
                f"R$ {row['RED_VALORPARCELA']:,.2f}"
                if pd.notna(row["RED_VALORPARCELA"])
                else "R$ 0,00"
            )
            v_rec = (
                f"R$ {row['RED_VALORRECEBIDO']:,.2f}"
                if pd.notna(row["RED_VALORRECEBIDO"])
                else "R$ 0,00"
            )

            self.tree.insert(
                "",
                tk.END,
                values=(
                    row["REC_NUMEROOPERACAO"],
                    row["REC_NUMERONOTAFISCAL"],
                    d_emissao,
                    row["CLI_CODIGO"],
                    row["CLI_NOME"],
                    row["RED_PARCELA"],
                    d_venc,
                    v_parc,
                    v_rec,
                    d_rec,
                    tpf,
                ),
                tags=(str(idx),),
            )

    def _on_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        idx = int(self.tree.item(selection[0])["tags"][0])
        row = self.df_resultados.iloc[idx]

        self.txt_historico.config(state=tk.NORMAL)
        self.txt_historico.delete(1.0, tk.END)
        self.txt_historico.insert(
            tk.END, str(row["REC_HISTORICO"]) if pd.notna(row["REC_HISTORICO"]) else ""
        )
        self.txt_historico.config(state=tk.DISABLED)

    def _limpar(self):
        self.txt_clientes.delete(0, tk.END)
        self.txt_data_inicio.delete(0, tk.END)
        self.txt_data_inicio.insert(0, "01/01/2020")
        self.txt_data_fim.delete(0, tk.END)
        self.txt_data_fim.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.situacao_var.set("ABERTO")
        self.tipo_data_var.set("VENCIMENTO")
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.txt_historico.config(state=tk.NORMAL)
        self.txt_historico.delete(1.0, tk.END)
        self.txt_historico.config(state=tk.DISABLED)

    def _exportar_excel(self):
        if self.df_resultados.empty:
            messagebox.showwarning("Aviso", "Não há dados para exportar.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")]
        )
        if path:
            try:
                self.df_resultados.to_excel(path, index=False)
                messagebox.showinfo("Sucesso", "Exportado com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro ao exportar", str(e))

    def _sort_column(self, col, reverse):
        if self.df_resultados.empty:
            return
        # Mapeamento simplificado para exemplo
        col_map = {
            "op": "REC_NUMEROOPERACAO",
            "cliente": "CLI_NOME",
            "vencimento": "RED_DATAVENCIMENTO",
        }
        df_col = col_map.get(col)
        if df_col:
            self.df_resultados = self.df_resultados.sort_values(
                by=df_col, ascending=not reverse
            )
            self._atualizar_tabela()
            self.tree.heading(col, command=lambda: self._sort_column(col, not reverse))

    def _on_closing(self):
        self.db.close()
        self.window.destroy()
