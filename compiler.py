import re

# Definir clase Token
class Token:
    def __init__(self, tipo, valor, linea, columna):
        self.tipo = tipo
        self.valor = valor
        self.linea = linea
        self.columna = columna

    def __repr__(self):
        return f"{self.tipo}({self.valor}) en línea {self.linea}, columna {self.columna}"

# Definir el scanner
class Scanner:
    def __init__(self, codigo):
        self.codigo = codigo
        self.pos = 0
        self.linea = 1
        self.columna = 1
        self.longitud = len(codigo)

    def getchar(self):
        if self.pos < self.longitud:
            char = self.codigo[self.pos]
            self.pos += 1
            self.columna += 1
            if char == '\n':
                self.linea += 1
                self.columna = 1
            return char
        return None

    def peekchar(self):
        if self.pos < self.longitud:
            return self.codigo[self.pos]
        return None

    def skip_whitespace(self):
        while self.peekchar() and self.peekchar() in ' \t\n\r':
            self.getchar()

    def skip_comment(self):
        char = self.getchar()
        if char == '/':  # Comentario tipo C++
            while self.peekchar() and self.peekchar() != '\n':
                self.getchar()
        elif char == '*':  # Comentario tipo C
            while True:
                if self.getchar() == '*' and self.peekchar() == '/':
                    self.getchar()
                    break

    def get_string(self):
        valor = '"'
        while True:
            char = self.getchar()
            if char == '"' or char is None:
                valor += '"'
                break
            valor += char
        return valor

    def gettoken(self):
        self.skip_whitespace()

        char = self.getchar()
        if not char:
            return None  # Fin de entrada

        # Detectar identificadores o palabras clave (soporta caracteres Unicode como tildes)
        if re.match(r'[a-zA-Z_áéíóúÁÉÍÓÚ]', char):
            valor = char
            while self.peekchar() and re.match(r'[a-zA-Z0-9_áéíóúÁÉÍÓÚ]', self.peekchar()):
                valor += self.getchar()

            if valor in {"if", "else", "for", "return", "print", "integer", "boolean", "char", "string", "true", "false"}:
                return Token("PALABRA_CLAVE", valor, self.linea, self.columna)
            else:
                return Token("ID", valor, self.linea, self.columna)

        # Detectar números
        if re.match(r'\d', char):
            valor = char
            while self.peekchar() and re.match(r'\d', self.peekchar()):
                valor += self.getchar()
            return Token("NUMERO", valor, self.linea, self.columna)

        # Detectar cadenas
        if char == '"':
            return Token("STRING", self.get_string(), self.linea, self.columna)

        # Detectar operadores y otros símbolos
        if char == '+':
            return Token("SUMA", char, self.linea, self.columna)
        if char == '-':
            return Token("RESTA", char, self.linea, self.columna)
        if char == '*':
            return Token("MULT", char, self.linea, self.columna)
        if char == '/':
            if self.peekchar() == '*' or self.peekchar() == '/':
                self.skip_comment()
                return self.gettoken()
            return Token("DIV", char, self.linea, self.columna)
        if char == '=':
            if self.peekchar() == '=':
                self.getchar()
                return Token("IGUAL", "==", self.linea, self.columna)
            else:
                return Token("ASIGNACION", char, self.linea, self.columna)

        # Operadores relacionales
        if char == '>':
            if self.peekchar() == '=':
                self.getchar()
                return Token("GEQ", ">=", self.linea, self.columna)
            return Token("GT", char, self.linea, self.columna)
        if char == '<':
            if self.peekchar() == '=':
                self.getchar()
                return Token("LEQ", "<=", self.linea, self.columna)
            return Token("LT", char, self.linea, self.columna)

        # Operador lógico AND y bitwise
        if char == '&':
            if self.peekchar() == '&':
                self.getchar()
                return Token("AND", "&&", self.linea, self.columna)
            return Token("AMPERSAND", "&", self.linea, self.columna)

        # Detectar paréntesis, llaves y punto y coma
        if char == '(':
            return Token("LPAREN", char, self.linea, self.columna)
        if char == ')':
            return Token("RPAREN", char, self.linea, self.columna)
        if char == '{':
            return Token("LBRACE", char, self.linea, self.columna)
        if char == '}':
            return Token("RBRACE", char, self.linea, self.columna)
        if char == ';':
            return Token("SEMICOLON", char, self.linea, self.columna)

        # Error léxico
        return Token("ERROR", char, self.linea, self.columna)

# Ejemplo de uso
codigo = '''
integer á = 10;
if (á > 5) {
    á = á + 1;
    print("Hola mundo");
    /* comentario */
} else {
    á = á - 1;
}
boolean flag = true;
if (flag && á >= 11) {
    print("Condición cumplida");
}
'''

scanner = Scanner(codigo)
token = scanner.gettoken()
while token:
    print(token)
    token = scanner.gettoken()
