# main.py
import sys, argparse, lexer

ap = argparse.ArgumentParser(description="Analisador léxico UaiC++")
ap.add_argument("arquivo", help="caminho do código-fonte UaiC++")
args = ap.parse_args()

with open(args.arquivo, encoding="utf-8") as f:
    src = f.read()

lex = lexer.Lexer(src)
tokens, errors = lex.scan()

for t in tokens:
    print(f"Linha: {t.line:>3} – Coluna: {t.column:<3} – Token:<{t.type},{t.lexeme}>")
if errors:
    print("\n⟹ Erros:")
    for e in errors:
        print(e)
