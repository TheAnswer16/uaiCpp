import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
from lexer import Lexer
from parser import Parser

def open_file():
    path = filedialog.askopenfilename(
        title="Abrir arquivo .uai",
        filetypes=[("UaiC++ source", "*.uai"), ("Todos", "*.*")]
    )
    if path:
        with open(path, encoding="utf-8") as f:
            code_box.delete("1.0", tk.END)
            code_box.insert(tk.END, f.read())

def run_lexer_and_parser():
    src = code_box.get("1.0", tk.END)
    lexer = Lexer(src)
    tokens, lex_errors = lexer.scan()

    tok_box.config(state="normal")
    tok_box.delete("1.0", tk.END)
    for t in tokens:
        tok_box.insert(tk.END, f"Linha: {t.line:>3} – Coluna: {t.column:<3} – Token:<{t.type},{t.lexeme}>\n")
    tok_box.config(state="disabled")

    lexerr_box.config(state="normal")
    lexerr_box.delete("1.0", tk.END)
    if lex_errors:
        lexerr_box.insert(tk.END, "\n".join(lex_errors))
    else:
        lexerr_box.insert(tk.END, "‹nenhum›")
    lexerr_box.config(state="disabled")

    parser = Parser(tokens)
    parse_errors = parser.parse()

    parserr_box.config(state="normal")
    parserr_box.delete("1.0", tk.END)
    if parse_errors:
        parserr_box.insert(tk.END, "\n".join(parse_errors))
    else:
        parserr_box.insert(tk.END, "‹nenhum›")
    parserr_box.config(state="disabled")

def clear_all():
    for box in (code_box, tok_box, lexerr_box, parserr_box):
        box.config(state="normal")
        box.delete("1.0", tk.END)
        if box is not code_box:
            box.config(state="disabled")

root = tk.Tk()
root.title("UaiC++ – Analisador Léxico e Sintático")
root.geometry("1000x700")
root.columnconfigure(0, weight=1)
root.rowconfigure(1, weight=1)

btn_frame = ttk.Frame(root, padding=4)
btn_frame.grid(row=0, column=0, sticky="ew")
for i in range(5):
    btn_frame.columnconfigure(i, weight=1)

ttk.Button(btn_frame, text="Abrir", command=open_file).grid(row=0, column=0, sticky="ew")
ttk.Button(btn_frame, text="Analisar", command=run_lexer_and_parser).grid(row=0, column=1, sticky="ew")
ttk.Button(btn_frame, text="Limpar", command=clear_all).grid(row=0, column=2, sticky="ew")
ttk.Button(btn_frame, text="Sair", command=root.destroy).grid(row=0, column=3, sticky="ew")

code_box = scrolledtext.ScrolledText(root, width=90, height=20, font=("Consolas", 11))
code_box.grid(row=1, column=0, sticky="nsew", padx=4, pady=(0,4))

lower = ttk.Frame(root)
lower.grid(row=2, column=0, sticky="nsew")
lower.columnconfigure(0, weight=2)
lower.columnconfigure(1, weight=1)

tok_box = scrolledtext.ScrolledText(lower, width=60, height=12, font=("Consolas", 10), state="disabled")
tok_box.grid(row=0, column=0, sticky="nsew", padx=(0,4))
lexerr_box = scrolledtext.ScrolledText(lower, width=40, height=12, font=("Consolas", 10), foreground="red", state="disabled")
lexerr_box.grid(row=0, column=1, sticky="nsew")

parserr_box = scrolledtext.ScrolledText(root, height=6, font=("Consolas", 10), foreground="purple", state="disabled")
parserr_box.grid(row=3, column=0, sticky="nsew", padx=4, pady=(4,4))

root.mainloop()
