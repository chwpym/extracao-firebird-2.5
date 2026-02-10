import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import os
import subprocess
import threading
import sys
import ast


class DiagnosticWindow:
    def __init__(self, parent):
        self.parent = parent
        self.tools_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"
        )

        self.window = tk.Toplevel(parent)
        self.window.title("Central de Diagnóstico e Testes Pro")
        self.window.geometry("1100x700")
        self.window.transient(parent)
        self.window.grab_set()

        self._center_window(1100, 700)
        self._create_widgets()
        self._refresh_scripts()

    def _center_window(self, width, height):
        self.window.update_idletasks()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.window.geometry(f"{width}x{height}+{x}+{y}")

    def _create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Splitter principal
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Lado Esquerdo: Lista de Scripts e Manual
        left_side = ttk.Frame(paned)
        paned.add(left_side, weight=1)

        # Lista
        list_frame = ttk.LabelFrame(left_side, text="🛠️ Ferramentas", padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        self.script_list = tk.Listbox(list_frame, font=("Arial", 10), height=10)
        self.script_list.pack(fill=tk.BOTH, expand=True)
        self.script_list.bind("<<ListboxSelect>>", self._on_script_select)

        # Manual
        manual_frame = ttk.LabelFrame(
            left_side, text="📖 Como Usar / O que faz", padding="5"
        )
        manual_frame.pack(fill=tk.BOTH, expand=True)

        self.manual_text = ScrolledText(
            manual_frame, wrap=tk.WORD, font=("Arial", 9), height=10
        )
        self.manual_text.pack(fill=tk.BOTH, expand=True)
        self.manual_text.config(state="disabled", bg="#f0f0f0")

        # Botões de Ação embaixo da lista
        btn_frame = ttk.Frame(left_side, padding="5")
        btn_frame.pack(fill=tk.X)

        ttk.Button(btn_frame, text="▶️ Executar", command=self._run_script).pack(
            side=tk.LEFT, padx=2, expand=True, fill=tk.X
        )
        ttk.Button(btn_frame, text="📝 Editar Código", command=self._edit_script).pack(
            side=tk.LEFT, padx=2, expand=True, fill=tk.X
        )

        # Lado Direito: Console de Saída
        right_side = ttk.Frame(paned)
        paned.add(right_side, weight=2)

        console_frame = ttk.LabelFrame(
            right_side, text="💻 Console (Saída em tempo real)", padding="5"
        )
        console_frame.pack(fill=tk.BOTH, expand=True)

        self.console = ScrolledText(
            console_frame,
            wrap=tk.WORD,
            bg="#1e1e1e",
            fg="#00ff00",
            font=("Consolas", 10),
        )
        self.console.pack(fill=tk.BOTH, expand=True)

        ttk.Button(
            right_side,
            text="🧹 Limpar Console",
            command=lambda: self.console.delete(1.0, tk.END),
        ).pack(pady=5, fill=tk.X)

    def _get_script_manual(self, path):
        """Lê a docstring ou comentários iniciais do script"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                tree = ast.parse(content)
                doc = ast.get_docstring(tree)
                if doc:
                    return doc.strip()

                # Se não tiver docstring, pega as primeiras linhas de comentário
                lines = content.splitlines()
                comments = []
                for line in lines:
                    if line.startswith("#"):
                        comments.append(line.strip("#").strip())
                    elif line.strip() and not (
                        line.startswith("#")
                        or line.startswith('"""')
                        or line.startswith("'''")
                    ):
                        break
                return (
                    "\n".join(comments) if comments else "Nenhuma descrição disponível."
                )
        except Exception as e:
            return f"Erro ao ler manual: {e}"

    def _on_script_select(self, event):
        selection = self.script_list.curselection()
        if not selection:
            return

        script_name = self.script_list.get(selection[0])
        script_path = os.path.join(self.tools_dir, script_name)

        manual = self._get_script_manual(script_path)

        self.manual_text.config(state="normal")
        self.manual_text.delete(1.0, tk.END)
        self.manual_text.insert(tk.END, manual)
        self.manual_text.config(state="disabled")

    def _refresh_scripts(self):
        self.script_list.delete(0, tk.END)
        if os.path.exists(self.tools_dir):
            scripts = [f for f in os.listdir(self.tools_dir) if f.endswith(".py")]
            for script in sorted(scripts):
                self.script_list.insert(tk.END, script)

    def _run_script(self):
        selection = self.script_list.curselection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um script para executar.")
            return

        script_name = self.script_list.get(selection[0])
        script_path = os.path.join(self.tools_dir, script_name)

        self.console.insert(
            tk.END, f"\n>>> INICIANDO: {script_name}\n" + "-" * 60 + "\n"
        )
        self.console.see(tk.END)

        threading.Thread(
            target=self._execute_command, args=(script_path,), daemon=True
        ).start()

    def _execute_command(self, path):
        try:
            root_dir = os.path.dirname(os.path.dirname(path))
            env = os.environ.copy()
            current_pythonpath = env.get("PYTHONPATH", "")
            env["PYTHONPATH"] = (
                root_dir + os.pathsep + current_pythonpath
                if current_pythonpath
                else root_dir
            )

            process = subprocess.Popen(
                [sys.executable, path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=root_dir,
                env=env,
            )

            for line in process.stdout:
                self.window.after(0, self._append_to_console, line)

            process.wait()
            self.window.after(
                0,
                self._append_to_console,
                f"\n--- FINALIZADO (Código: {process.returncode}) ---\n",
            )
        except Exception as e:
            self.window.after(0, self._append_to_console, f"\nERRO: {str(e)}\n")

    def _append_to_console(self, text):
        self.console.insert(tk.END, text)
        self.console.see(tk.END)

    def _edit_script(self):
        selection = self.script_list.curselection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um script para editar.")
            return

        script_name = self.script_list.get(selection[0])
        script_path = os.path.join(self.tools_dir, script_name)

        EditWindow(self.window, script_name, script_path, self._on_script_select)


class EditWindow:
    def __init__(self, parent, name, path, on_save_callback):
        self.path = path
        self.on_save = on_save_callback

        self.top = tk.Toplevel(parent)
        self.top.title(f"Editando: {name}")
        self.top.geometry("800x600")
        self.top.transient(parent)
        self.top.grab_set()

        # Toolbar
        toolbar = ttk.Frame(self.top, padding="5")
        toolbar.pack(fill=tk.X)

        ttk.Button(toolbar, text="💾 SALVAR", command=self._save).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(toolbar, text="❌ FECHAR", command=self.top.destroy).pack(
            side=tk.LEFT, padx=5
        )

        # Editor
        self.editor = ScrolledText(
            self.top,
            wrap=tk.NONE,
            font=("Consolas", 10),
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="white",
        )
        self.editor.pack(fill=tk.BOTH, expand=True)

        try:
            with open(path, "r", encoding="utf-8") as f:
                self.editor.insert(tk.END, f.read())
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir arquivo: {e}")

    def _save(self):
        try:
            content = self.editor.get(1.0, tk.END)
            with open(self.path, "w", encoding="utf-8") as f:
                f.write(content.strip())
            messagebox.showinfo("Sucesso", "Arquivo salvo com sucesso!")
            self.on_save(None)  # Atualiza o manual
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")
