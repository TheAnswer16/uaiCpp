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

    def _expect(self, expected_type, description):
        if not self._match(expected_type):
            self._error(
                f"Esperado {description} (token '{expected_type}'), "
                f"mas encontrado '{self.current.lexeme}'"
            )

    def _error(self, msg):
        self.errors.append(
            f"[Linha {self.current.line}, Coluna {self.current.column}] Erro sintático: {msg}"
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
            self._expect("PONTO_E_VIRGULA", "ponto e vírgula ';' ao final do comando mostra_trem")
        elif self.current.type == "ESCUTA_TREM":
            self._match("ESCUTA_TREM")
            self._expect("IDENT", "identificador após escuta_trem")
            self._expect("PONTO_E_VIRGULA", "ponto e vírgula ';' ao final do comando escuta_trem")
        elif self.current.type == "UAI":
            self._condicional()
        elif self.current.type == "VORTA":
            self._match("VORTA")
            self._expr()
            self._expect("PONTO_E_VIRGULA", "ponto e vírgula ';' após o comando vorta")
        else:
            self._error(f"Comando inesperado: '{self.current.lexeme}'")

    def _decl(self):
        self._match("TREM")
        if self.current.type in ("INT", "REAL", "LOGICO", "TEXTO", "LISTA", "DATA_HORA"):
            self._advance()
        else:
            self._error(
                f"Tipo inválido na declaração. Esperado: int, real, lógico, texto, lista ou data_hora; encontrado: '{self.current.lexeme}'"
            )
        self._expect("IDENT", "identificador da variável")
        if self._match("OP_ATRIB"):
            self._expr()
        self._expect("PONTO_E_VIRGULA", "ponto e vírgula ';' ao final da declaração")

    def _condicional(self):
        self._advance()
        self._expect("ABRE_PAR", "parêntese de abertura '(' após 'uai'")
        self._expr()
        self._expect("FECHA_PAR", "parêntese de fechamento ')' após a condição")
        self._expect("ABRE_BLOCO", "início de bloco 'chegô'")
        while self.current.type not in ("FECHA_BLOCO", "EOF"):
            self._statement()
        self._expect("FECHA_BLOCO", "fim de bloco 'cabo'")

        while self.current.type == "UAI_SO":
            self._advance()
            self._expect("ABRE_PAR", "parêntese de abertura '(' após 'uai'")
            self._expr()
            self._expect("FECHA_PAR", "parêntese de fechamento ')' após a condição")
            self._expect("ABRE_BLOCO", "início de bloco 'chegô'")
            while self.current.type not in ("FECHA_BLOCO", "EOF"):
                self._statement()
            self._expect("FECHA_BLOCO", "fim de bloco 'cabo'")

        if self.current.type == "UAI_NADA":
            self._advance()
            self._expect("ABRE_BLOCO", "início de bloco 'chegô'")
            while self.current.type not in ("FECHA_BLOCO", "EOF"):
                self._statement()
            self._expect("FECHA_BLOCO", "fim de bloco 'cabo'")

    def _expr(self):
        if self.current.type in ("IDENT", "NUMERO", "STRING", "CHAR", "VERDADE", "MINTIRA"):
            self._advance()
            while self.current.type in ("OP_MAT", "OP_REL", "TAMEM", "OU"):
                self._advance()
                self._expr()
        elif self._match("ABRE_PAR"):
            self._expr()
            self._expect("FECHA_PAR", "parêntese de fechamento ')' para encerrar expressão")
        else:
            self._error(
                f"Expressão inválida: '{self.current.lexeme}'. Esperado identificador, número ou valor válido"
            )
