# parser.py – analisador sintático para a linguagem UaiC++
# Autor: Alex Martins e João Lucio (continuação do projeto)

from lexer import Token

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0
        self.errors: list[str] = []
        self.current = self._peek()

    def _peek(self, la=0):
        if self.pos + la >= len(self.tokens):
            return Token("EOF", "<EOF>", -1, -1)
        return self.tokens[self.pos + la]

    def _advance(self):
        self.pos += 1
        self.current = self._peek()

    def _match(self, expected_type):
        if self.current.type == expected_type:
            self._advance()
            return True
        return False

    def _expect(self, expected_type, message):
        if not self._match(expected_type):
            self._error(f"Esperado '{expected_type}', mas encontrado '{self.current.lexeme}'")

    def _error(self, msg):
        self.errors.append(
            f"Erro sintático na linha {self.current.line}, coluna {self.current.column}: {msg}"
        )
        self._advance()  # Tenta seguir adiante

    def parse(self):
        while self.current.type != "EOF":
            self._statement()
        return self.errors

    def _statement(self):
        if self.current.type == "TREM":
            self._decl()
        elif self.current.type == "MOSTRA_TREM":
            self._match("MOSTRA_TREM")
            self._expr()
            self._expect("PONTO_E_VIRGULA", "';' ao final do comando mostra_trem")
        elif self.current.type == "ESCUTA_TREM":
            self._match("ESCUTA_TREM")
            self._expect("IDENT", "identificador após escuta_trem")
            self._expect("PONTO_E_VIRGULA", "';' ao final de escuta_trem")
        elif self.current.type == "COND_SE":
            self._condicional()
        elif self.current.type == "VORTA":
            self._match("VORTA")
            self._expr()
            self._expect("PONTO_E_VIRGULA", "';' após vorta")
        else:
            self._error(f"Comando inesperado: {self.current.lexeme}")

    def _decl(self):
        self._match("TREM")
        if self.current.type in ("INT", "REAL", "LOGICO", "TEXTO", "LISTA", "DATA_HORA"):
            self._advance()
        else:
            self._error("Tipo de dado inválido na declaração")
        self._expect("IDENT", "identificador da variável")
        if self._match("OP_ATRIB"):
            self._expr()
        self._expect("PONTO_E_VIRGULA", "';' ao final da declaração")

    def _condicional(self):
        self._advance()  # uai
        self._expect("ABRE_PAR", "'(' após uai")
        self._expr()
        self._expect("FECHA_PAR", "')' após condição")
        self._expect("ABRE_BLOCO", "chego para abrir bloco")
        while self.current.type not in ("FECHA_BLOCO", "EOF"):
            self._statement()
        self._expect("FECHA_BLOCO", "cabo para fechar bloco")

    def _expr(self):
        # Expressão simples: IDENT ou NUMERO (ou agrupamento com parênteses)
        if self.current.type in ("IDENT", "NUMERO", "STRING", "CHAR", "VERDADE", "MINTIRA"):
            self._advance()
            if self.current.type in ("OP_MAT", "OP_REL", "OP_LOGICO"):
                self._advance()
                self._expr()
        elif self._match("ABRE_PAR"):
            self._expr()
            self._expect("FECHA_PAR", "')' após expressão")
        else:
            self._error(f"Expressão inválida: {self.current.lexeme}")
