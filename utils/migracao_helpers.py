import tkinter as tk
from tkinter import messagebox
import pandas as pd

def formatar_texto_migracao(produto_row):
    """
    Combina a aplicação e o código original de forma ultra-robusta.
    Lida com Pandas Series, Dicionários e campos BLOB do Firebird.
    """
    if produto_row is None:
        return None
        
    # Converter para dicionário para facilitar a manipulação
    if hasattr(produto_row, 'to_dict'):
        data = produto_row.to_dict()
    else:
        try:
            data = dict(produto_row)
        except:
            return None
            
    # Criar um mapeamento de chaves em maiúsculo para evitar erros de case
    data_upper = {str(k).upper(): v for k, v in data.items()}
    
    # Criar função auxiliar para extrair valores limpos
    
    def get_clean_val(key):
        val = data_upper.get(key.upper())
        
        # Processar valor
        
        # Se for nulo ou NaN do Pandas
        if pd.isna(val) or val is None:
            return ""
            
        # Tratar campos BLOB
        if isinstance(val, (bytes, bytearray)):
            try:
                decoded = val.decode('latin-1', errors='replace').strip()
                return decoded
            except:
                return str(val).strip()
                
        # Limpar strings "falsas"
        s_val = str(val).strip()
        blacklist = ['NONE', 'NAN', 'NULL', '-', 'NONE', 'NAN']
        if s_val.upper() in blacklist:
            return ""
            
        return s_val

    aplicacao = get_clean_val('PROD_APLICACAO')
    cod_original = get_clean_val('PROD_CODIGOORIGINAL')
    
    # Se a aplicação vier vazia, tenta o campo alternativo
    if not aplicacao:
        aplicacao = get_clean_val('PROD_APLICACAO1')
    
    # Formatar texto final

    # Montagem do texto final
    if aplicacao and cod_original:
        texto = f"{aplicacao} - ORIG: {cod_original}"
    elif aplicacao:
        texto = aplicacao
    elif cod_original:
        texto = cod_original
    else:
        return None
    
    # CRÍTICO: Remover TODAS as quebras de linha para evitar que o Windows Clipboard History
    # divida o texto em múltiplos itens!
    texto = texto.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
    
    # Remover espaços duplos
    while '  ' in texto:
        texto = texto.replace('  ', ' ')
    
    return texto.strip()

def copiar_para_clipboard(window, texto):
    """Auxiliar para copiar texto para a área de transferência do Windows usando API nativa"""
    if not texto:
        return False
    
    # Copiar para clipboard usando API do Windows
    try:
        # Tentar usar win32clipboard (API do Windows)
        try:
            import win32clipboard
            import time
            
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(texto, win32clipboard.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            
            # Pequeno delay para garantir que o clipboard foi atualizado
            time.sleep(0.2)
            
            # VERIFICAR se foi copiado corretamente
            win32clipboard.OpenClipboard()
            clipboard_content = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            
            # Retornar sucesso (clipboard pode ser verificado manualmente)
            return True
            
        except ImportError:
            # Se win32clipboard não estiver disponível, tentar pyperclip
            try:
                import pyperclip
                pyperclip.copy(texto)
                
                # Verificar
                if pyperclip.paste() == texto:
                    print(f"✅ COPIADO usando pyperclip\n")
                    return True
                else:
                    print(f"❌ ERRO: pyperclip não copiou corretamente\n")
                    return False
                    
            except ImportError:
                # Fallback para Tkinter (método original)
                print(f"⚠️ Usando Tkinter clipboard (fallback)\n")
                import time
                
                window.clipboard_clear()
                window.update()
                window.update_idletasks()
                
                window.clipboard_append(texto)
                
                window.update()
                window.update_idletasks()
                time.sleep(0.2)
                window.update()
                
                try:
                    clipboard_content = window.clipboard_get()
                    if clipboard_content == texto:
                        print(f"✅ VERIFICAÇÃO: Clipboard contém o texto correto ({len(clipboard_content)} chars)\n")
                        return True
                    else:
                        print(f"❌ ERRO: Clipboard contém texto diferente!\n")
                        return False
                except:
                    return True
                    
    except Exception as e:
        print(f"❌ ERRO ao copiar: {e}\n")
        return False

def mostrar_popup_migracao(parent_window, produto_row):
    """
    Mostra popup personalizado com o texto de migração e botão para copiar.
    Centraliza TODA a lógica de migração em um único lugar.
    """
    # Formatar o texto usando a função existente
    texto_final = formatar_texto_migracao(produto_row)
    
    if not texto_final:
        messagebox.showinfo("Aviso", "Este produto não possui aplicação nem código original preenchidos.")
        return
    
    # Criar janela popup personalizada
    popup = tk.Toplevel(parent_window)
    popup.title("Texto para Migração")
    popup.geometry("600x300")
    popup.transient(parent_window)
    popup.grab_set()
    
    # Centralizar janela
    popup.update_idletasks()
    x = (popup.winfo_screenwidth() // 2) - (600 // 2)
    y = (popup.winfo_screenheight() // 2) - (300 // 2)
    popup.geometry(f"600x300+{x}+{y}")
    
    # Frame principal
    main_frame = tk.Frame(popup, padx=20, pady=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Label de instrução
    label = tk.Label(main_frame, text="Texto formatado para migração:", 
                     font=("Arial", 10, "bold"))
    label.pack(pady=(0, 10))
    
    # Campo de texto com scroll
    from tkinter.scrolledtext import ScrolledText
    text_widget = ScrolledText(main_frame, wrap=tk.WORD, font=("Arial", 10),
                               height=8, exportselection=False)
    text_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
    text_widget.insert(1.0, texto_final)
    text_widget.config(state=tk.DISABLED)  # Somente leitura
    
    # Frame para botões
    button_frame = tk.Frame(main_frame)
    button_frame.pack(fill=tk.X)
    
    # Variável para controlar se foi copiado
    copiado = [False]  # Usar lista para poder modificar dentro da função
    
    def copiar_e_fechar():
        """Copia o texto e fecha a janela"""
        if copiar_para_clipboard(popup, texto_final):
            copiado[0] = True
            messagebox.showinfo("✅ Copiado!", 
                              f"Texto copiado com sucesso!\n\n{len(texto_final)} caracteres copiados.",
                              parent=popup)
            popup.destroy()
        else:
            messagebox.showerror("Erro", "Erro ao copiar para a área de transferência.", 
                               parent=popup)
    
    # Botão Copiar
    btn_copiar = tk.Button(button_frame, text="📋 Copiar para Área de Transferência",
                          command=copiar_e_fechar, font=("Arial", 10, "bold"),
                          bg="#4CAF50", fg="white", padx=20, pady=10)
    btn_copiar.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
    
    # Botão Fechar
    btn_fechar = tk.Button(button_frame, text="Fechar", command=popup.destroy,
                          font=("Arial", 10), padx=20, pady=10)
    btn_fechar.pack(side=tk.RIGHT, padx=(5, 0))
    
    # Atalho: Enter para copiar, Esc para fechar
    popup.bind('<Return>', lambda e: copiar_e_fechar())
    popup.bind('<Escape>', lambda e: popup.destroy())
    
    # Focar no botão copiar
    btn_copiar.focus_set()
