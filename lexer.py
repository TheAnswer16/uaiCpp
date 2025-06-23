# -*- coding: utf-8 -*-
"""
lexer.py – analisador léxico para a linguagem UaiC++
Autor: Alex Martins e João Luxio
"""

import re
from collections import namedtuple

# ============================================================
# CONFIGURAÇÕES GERAIS
# ============================================================
MAX_LEN = 32
Token   = namedtuple("Token", "type lexeme line column")

# ============================================================
# PALAVRAS-RESERVADAS  →  tipo de token
# (duas grafias quando houver acento)
# ============================================================
KEYWORDS: dict[str, str] = {
    # tipos
    "trem": "TREM",
    "int":  "INT",
    "real": "REAL",
    "logico": "LOGICO", "lógico": "LOGICO",
    "texto": "TEXTO",
    "lista": "LISTA",
    "data_hora": "DATA_HORA",

    # operadores lógicos / condicionais
    "tamem": "TAMEM",
    "ou":    "OU",
    "nao":   "NAO", "não": "NAO",

    # estruturas de decisão
    "uai":      "UAI",
    "uai_so":   "UAI_SO",
    "uai_nada": "UAI_NADA",

    # booleanos
    "verdade": "VERDADE",
    "mintira": "MINTIRA", "mentira": "MINTIRA",

    # bloco com palavras-chave
    "chego": "ABRE_BLOCO",  "chegô": "ABRE_BLOCO",
    "cabo":  "FECHA_BLOCO", "acabo": "FECHA_BLOCO", "acabô": "FECHA_BLOCO",

    # outros
    "vorta": "VORTA",
    "escuta_trem": "ESCUTA_TREM",
    "mostra_trem": "MOSTRA_TREM",
    "trem_funcionando": "TREM_FUNCIONANDO",
}

# ============================================================
# OPERADORES E SÍMBOLOS
# ============================================================
OPERATORS = {
    # relacionais
    "<=": "OP_REL", ">=": "OP_REL", "==": "OP_REL", "!=": "OP_REL",
    "<":  "OP_REL", ">":  "OP_REL",
    # matemáticos
    "+": "OP_MAT", "-": "OP_MAT", "*": "OP_MAT", "/": "OP_MAT",
    # atribuição
    "=": "OP_ATRIB",
}

# >>> As chaves “{” e “}” foram removidas:
SYMBOLS = {
    "(": "ABRE_PAR",
    ")": "FECHA_PAR",
    ",": "VIRGULA",
    ";": "PONTO_E_VIRGULA",
}

# ============================================================
# REGEX AUXILIARES
# ============================================================
RE_ID = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ_][A-Za-zÀ-ÖØ-öø-ÿ0-9_]*")

# ============================================================
# CLASSE LEXER
# ============================================================
class Lexer:
    """Scanner de uma passada para a linguagem UaiC++."""

    def __init__(self, source: str) -> None:
        self.source = source
        self.pos    = 0
        self.line   = 1
        self.col    = 1
        self.length = len(source)
        self.tokens: list[Token] = []
        self.errors: list[str]   = []

    # --------------------------------------------------------
    # API PÚBLICA
    # --------------------------------------------------------
    def scan(self):
        while not self._eof():
            ch = self._peek()

            if ch in " \t\r":                         # espaço / tab
                self._consume_whitespace()
            elif ch == "\n":                         # quebra de linha
                self._advance(); self.line += 1; self.col = 1
            elif ch == "/" and self._peek(1) == "/": # comentário //
                self._consume_comment()
            elif ch in SYMBOLS:                      # símbolo isolado
                self._add_token(SYMBOLS[ch], ch); self._advance()
            elif self._match_operator():             # operadores
                pass
            elif ch in "\"'":                        # string/char
                self._consume_string_or_char(ch)
            elif ch.isdigit():                       # número ou id mal formado
                if self._peek(1).isalpha() or self._peek(1) == "_":
                    self._consume_bad_identifier()
                else:
                    self._consume_number()
            elif ch.isalpha() or ch == "_":          # identificador / palavra-reservada
                self._consume_identifier()
            else:                                    # qualquer outro
                self._error("Símbolo desconhecido"); self._advance()

        return self.tokens, self.errors

    # --------------------------------------------------------
    # UTILITÁRIOS
    # --------------------------------------------------------
    def _eof(self, la=0): return self.pos + la >= self.length
    def _peek(self, la=0): return "" if self._eof(la) else self.source[self.pos+la]
    def _advance(self, n=1): 
        for _ in range(n): self.pos += 1; self.col += 1
    def _add_token(self, t, lx): self.tokens.append(Token(t, lx, self.line, self.col))
    def _error(self, msg): self.errors.append(f"Linha: {self.line} – Coluna: {self.col} – Erro: {msg}")

    # --------------------------------------------------------
    # CONSUMOS
    # --------------------------------------------------------
    def _consume_whitespace(self):
        while self._peek() in " \t\r": self._advance()

    def _consume_comment(self):
        while not self._eof() and self._peek() != "\n": self._advance()

    def _match_operator(self):
        for op in sorted(OPERATORS, key=len, reverse=True):
            if self.source.startswith(op, self.pos):
                self._add_token(OPERATORS[op], op); self._advance(len(op)); return True
        return False

    def _consume_string_or_char(self, quote):
        lexeme = quote; self._advance()
        while not self._eof() and self._peek() not in (quote, "\n"):
            lexeme += self._peek(); self._advance()
        if self._eof() or self._peek() == "\n":
            self._error("String/char não fechado")
        else:
            lexeme += quote; self._advance()
            self._add_token("STRING" if quote == "\"" else "CHAR", lexeme)

    def _consume_number(self):
        lexeme = ""
        while self._peek().isdigit(): lexeme += self._peek(); self._advance()
        if self._peek() == ".":                          # parte decimal
            if not self._peek(1).isdigit():              # mal-formado 2.a3
                lexeme += "."; self._advance()
                while self._peek().isalnum() or self._peek() == ".": 
                    lexeme += self._peek(); self._advance()
                self._error("Número mal formado"); self._add_token("NUMERO", lexeme); return
            lexeme += "."; self._advance()
            while self._peek().isdigit(): lexeme += self._peek(); self._advance()
        if len(lexeme) > MAX_LEN: self._error("Número muito longo")
        self._add_token("NUMERO", lexeme)

    def _consume_bad_identifier(self):
        lexeme = ""
        while self._peek().isalnum() or self._peek() == "_": lexeme += self._peek(); self._advance()
        self._error("Identificador mal formado"); self._add_token("IDENT", lexeme)

    def _consume_identifier(self):
        match = RE_ID.match(self.source[self.pos:])
        if not match:
            self._error("Identificador mal formado"); self._advance(); return
        lexeme = match.group(0); self._advance(len(lexeme))
        if len(lexeme) > MAX_LEN: self._error("Identificador muito longo")
        self._add_token(KEYWORDS.get(lexeme, "IDENT"), lexeme)
