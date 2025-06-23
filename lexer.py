# -*- coding: utf-8 -*-
"""
lexer.py – analisador léxico para a linguagem UaiC++
Autor: (seu nome)
"""

import re
from collections import namedtuple

# -------- CONFIGURAÇÕES GERAIS -------- #
MAX_LEN = 32          # tamanho máx. de identificador ou número
Token = namedtuple("Token", "type lexeme line column")

# Palavras-reservadas segundo a proposta
KEYWORDS = {
    "trem", "int", "real", "lógico", "texto", "lista", "data_hora",
    "tamem", "ou", "não", "uai", "uai_nada", "uai_so",
    "vorta", "verdade", "mintira",
    "trem_funcionando", "chegô", "acabô",
    "escuta_trem", "mostra_trem"
}

# Operadores e símbolos de vários tamanhos (procure os mais longos primeiro)
OPERATORS = {
    "<=": "OP_REL", ">=": "OP_REL", "==": "OP_REL", "!=": "OP_REL",
    "<": "OP_REL",  ">": "OP_REL",
    "+": "OP_MAT", "-": "OP_MAT", "*": "OP_MAT", "/": "OP_MAT",
    "=": "OP_ATRIB"
}
SYMBOLS = {
    "(": "ABRE_PAR", ")": "FECHA_PAR",
    "{": "ABRE_CHAVE", "}": "FECHA_CHAVE",
    ",": "VIRGULA", ";": "PONTO_E_VIRGULA"
}

# Regex auxiliares
RE_ID = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
RE_INT = re.compile(r"\d+")
RE_FLOAT = re.compile(r"\d+\.\d+")

class Lexer:
    """Scanner de uma passada para UaiC++."""
    def __init__(self, source: str) -> None:
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1
        self.length = len(source)
        self.tokens = []
        self.errors = []

    # ---------- API PÚBLICA ---------- #
    def scan(self):
        while not self._eof():
            ch = self._peek()
            if ch in " \t\r":
                self._consume_whitespace()
            elif ch == "\n":
                self._advance()           # conta linha
                self.line += 1
                self.col = 1
            elif ch == "/" and self._peek(1) == "/":
                self._consume_comment()
            elif ch in SYMBOLS:
                self._add_token(SYMBOLS[ch], ch)
                self._advance()
            elif self._match_operator():
                pass
            elif ch in "\"'":
                self._consume_string_or_char(ch)
            elif ch.isdigit():
                self._consume_number()
            elif ch.isalpha() or ch == "_":
                self._consume_identifier()
            else:
                self._error("Símbolo desconhecido")
                self._advance()
        return self.tokens, self.errors

    # ---------- MÉTODOS PRIVADOS ---------- #
    def _eof(self, lookahead=0):
        return self.pos + lookahead >= self.length

    def _peek(self, lookahead=0):
        return '' if self._eof(lookahead) else self.source[self.pos + lookahead]

    def _advance(self, n=1):
        for _ in range(n):
            self.pos += 1
            self.col += 1

    def _add_token(self, tok_type, lexeme):
        self.tokens.append(Token(tok_type, lexeme, self.line, self.col))

    def _error(self, message):
        self.errors.append(f"Linha: {self.line} – Coluna: {self.col} – Erro: {message}")

    def _consume_whitespace(self):
        while self._peek() in " \t\r":
            self._advance()

    def _consume_comment(self):
        # ignora tudo até a quebra de linha ou EOF
        while not self._eof() and self._peek() != "\n":
            self._advance()

    def _match_operator(self):
        for op in sorted(OPERATORS.keys(), key=len, reverse=True):
            if self.source.startswith(op, self.pos):
                self._add_token(OPERATORS[op], op)
                self._advance(len(op))
                return True
        return False

    def _consume_string_or_char(self, quote):
        start_line, start_col = self.line, self.col
        lexeme = quote
        self._advance()
        while not self._eof() and self._peek() != quote and self._peek() != "\n":
            lexeme += self._peek()
            self._advance()
        # fim da string?
        if self._eof() or self._peek() == "\n":
            self._error("String/char não fechado")
        else:
            lexeme += quote
            self._advance()
            tok_type = "STRING" if quote == "\"" else "CHAR"
            self._add_token(tok_type, lexeme)

    def _consume_number(self):
        start = self.pos
        match = RE_FLOAT.match(self.source[self.pos:])
        if match:
            lexeme = match.group(0)
            self._advance(len(lexeme))
        else:
            match = RE_INT.match(self.source[self.pos:])
            lexeme = match.group(0)
            self._advance(len(lexeme))
        if len(lexeme) > MAX_LEN:
            self._error("Número muito longo")
        # número mal formado? ex.: 2.a3
        if not re.fullmatch(r"\d+(\.\d+)?", lexeme):
            self._error("Número mal formado")
        self._add_token("NUMERO", lexeme)

    def _consume_identifier(self):
        match = RE_ID.match(self.source[self.pos:])
        lexeme = match.group(0)
        self._advance(len(lexeme))
        if len(lexeme) > MAX_LEN:
            self._error("Identificador muito longo")
        tok_type = "IDENT"              # default
        if lexeme in KEYWORDS:
            tok_type = lexeme.upper()   # palavra-reservada vira seu próprio tipo
        self._add_token(tok_type, lexeme)
