"""
gui_tk.py – interface Tkinter para o analisador léxico UaiC++
Autor: Alex Martins e João Lucio
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from lexer import Lexer

# ---------- callbacks ---------- #
def open_file():
    path = filedialog.askopenfilename(
        title="Abrir arquivo .uai",
        filetypes=[("UaiC++ source", "*.uai"), ("Todos", "*.*")]
    )
    if path:
        with open(path, encoding="utf-8") as f:
            code_box.delete("1.0", tk.END)
            code_box.insert(tk.END, f.read())

def run_lexer():
    src = code_box.get("1.0", tk.END)
    lexer = Lexer(src)
    tokens, errors = lexer.scan()

    tok_box.config(state="normal")
    tok_box.delete("1.0", tk.END)
    for t in tokens:
        tok_box.insert(tk.END,
            f"Linha: {t.line:>3} – Coluna: {t.column:<3} – Token:<{t.type},{t.lexeme}>\n")
    tok_box.config(state="disabled")

    err_box.config(state="normal")
    err_box.delete("1.0", tk.END)
    if errors:
        err_box.insert(tk.END, "\n".join(errors))
    else:
        err_box.insert(tk.END, "‹nenhum›")
    err_box.config(state="disabled")

def clear_all():
    for box in (code_box, tok_box, err_box):
        box.config(state="normal")
        box.delete("1.0", tk.END)
        if box is not code_box:
            box.config(state="disabled")

# ---------- janela ---------- #
root = tk.Tk()
root.title("UaiC++ – Analisador Léxico")

root.columnconfigure(0, weight=1)
root.rowconfigure(1, weight=1)

# barra de botões
btn_frame = ttk.Frame(root, padding=4)
btn_frame.grid(row=0, column=0, sticky="ew")
for i in range(4):
    btn_frame.columnconfigure(i, weight=1)

ttk.Button(btn_frame, text="Abrir arquivo", command=open_file).grid(row=0, column=0, sticky="ew")
ttk.Button(btn_frame, text="Analisar",      command=run_lexer).grid(row=0, column=1, sticky="ew")
ttk.Button(btn_frame, text="Limpar",        command=clear_all).grid(row=0, column=2, sticky="ew")
ttk.Button(btn_frame, text="Sair",          command=root.destroy).grid(row=0, column=3, sticky="ew")

# caixas de texto
code_box = scrolledtext.ScrolledText(root, width=90, height=20, font=("Consolas", 11))
code_box.grid(row=1, column=0, sticky="nsew", padx=4, pady=(0,4))

lower = ttk.Frame(root)
lower.grid(row=2, column=0, sticky="nsew")
lower.columnconfigure(0, weight=3)
lower.columnconfigure(1, weight=2)

tok_box = scrolledtext.ScrolledText(lower, width=70, height=12, font=("Consolas", 10), state="disabled")
tok_box.grid(row=0, column=0, sticky="nsew", padx=(0,4))
err_box = scrolledtext.ScrolledText(lower, width=40, height=12, font=("Consolas", 10), foreground="red", state="disabled")
err_box.grid(row=0, column=1, sticky="nsew")

root.mainloop()
