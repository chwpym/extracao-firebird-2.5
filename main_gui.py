from ui.app import ExtractorApp
import tkinter as tk
from utils.logger import setup_logger

if __name__ == "__main__":
    # Inicializa o logger para terminal e arquivo
    setup_logger()
    
    root = tk.Tk()
    app = ExtractorApp(root)
    root.mainloop()
