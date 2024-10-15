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
class Escaner:
    def __init__(self, codigo):
        self.codigo = codigo
        self.pos = 0
        self.linea = 1
        self.columna = 1
        self.longitud = len(codigo)
        self.errores = []
        self.contador_errores = 0

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

    def saltar_espacios(self):
        while self.peekchar() and self.peekchar() in ' \t\n\r':
            self.getchar()

    def saltar_comentario(self):
        char = self.getchar()
        if char == '/':
            while self.peekchar() and self.peekchar() != '\n':
                self.getchar()
        elif char == '*':
            while True:
                if self.getchar() == '*' and self.peekchar() == '/':
                    self.getchar()
                    break

    def obtener_string(self):
        valor = '"'
        while True:
            char = self.getchar()
            if char == '"' or char is None:
                valor += '"'
                break
            if char == '\\':
                valor += char + self.getchar()
            else:
                valor += char
        return valor

    def reportar_error(self, mensaje):
        error_message = f"ERROR en línea {self.linea}, columna {self.columna}: {mensaje}"
        print(error_message)
        self.errores.append(error_message)
        self.contador_errores += 1

    def obtener_token(self):
        self.saltar_espacios()

        char = self.getchar()
        if not char:
            return None

        if re.match(r'[a-zA-Z_áéíóúÁÉÍÓÚ]', char):
            valor = char
            while self.peekchar() and re.match(r'[a-zA-Z0-9_áéíóúÁÉÍÓÚ]', self.peekchar()):
                valor += self.getchar()

            if valor in {"if", "else", "for", "return", "print", "integer", "boolean", "char", "string", "true", "false"}:
                return Token("PALABRA_CLAVE", valor, self.linea, self.columna)
            else:
                return Token("ID", valor, self.linea, self.columna)

        if re.match(r'\d', char):
            valor = char
            while self.peekchar() and re.match(r'\d', self.peekchar()):
                valor += self.getchar()
            return Token("NUMERO", valor, self.linea, self.columna)

        if char == '"':
            return Token("STRING", self.obtener_string(), self.linea, self.columna)

        if char == '+':
            if self.peekchar() == '+':
                self.getchar()
                return Token("INCREMENTO", "++", self.linea, self.columna)
            return Token("SUMA", char, self.linea, self.columna)

        if char == '-':
            if self.peekchar() == '-':
                self.getchar()
                return Token("DECREMENTO", "--", self.linea, self.columna)
            return Token("RESTA", char, self.linea, self.columna)

        if char == '*':
            return Token("MULT", char, self.linea, self.columna)

        if char == '/':
            if self.peekchar() == '*' or self.peekchar() == '/':
                self.saltar_comentario()
                return self.obtener_token()
            return Token("DIV", char, self.linea, self.columna)

        if char == '=':
            if self.peekchar() == '=':
                self.getchar()
                return Token("IGUAL", "==", self.linea, self.columna)
            else:
                return Token("ASIGNACION", char, self.linea, self.columna)

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

        if char == '&':
            if self.peekchar() == '&':
                self.getchar()
                return Token("AND", "&&", self.linea, self.columna)
            return Token("AMPERSAND", "&", self.linea, self.columna)

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
        if char == ',':
            return Token("COMA", char, self.linea, self.columna)

        self.reportar_error(f"Carácter inesperado '{char}'")
        return Token("ERROR", char, self.linea, self.columna)

    def mostrar_errores(self):
        if self.contador_errores > 0:
            print(f"\nSe encontraron {self.contador_errores} errores:")
            for error in self.errores:
                print(error)
        else:
            print("\nNo se encontraron errores.")

# Función para leer código desde un archivo
def leer_codigo_desde_archivo(nombre_archivo):
    with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
        return archivo.read()

nombre_archivo = 'codigo_fuente.txt'
codigo = leer_codigo_desde_archivo(nombre_archivo)
escaner = Escaner(codigo)

class Parser:
    def __init__(self, escaner):
        self.escaner = escaner
        self.token_actual = self.escaner.obtener_token()

    def consumir(self, tipo_token):
        if self.token_actual.tipo == tipo_token:
            print(f"Token procesado: {self.token_actual}")
            self.token_actual = self.escaner.obtener_token()
        else:
            print(f"Error de parsing: Se esperaba {tipo_token} pero se encontró {self.token_actual.tipo}")
            self.token_actual = self.escaner.obtener_token()

    def parsear_declaracion(self):
        if self.token_actual.tipo == "PALABRA_CLAVE" and self.token_actual.valor == "integer":
            print(f"Parsing declaración: {self.token_actual.valor}")
            self.consumir("PALABRA_CLAVE")
            self.consumir("ID")
            # Permitir declaración sin asignación
            if self.token_actual.tipo == "ASIGNACION":
                self.consumir("ASIGNACION")
                self.consumir("NUMERO")
            self.consumir("SEMICOLON")
        else:
            print(f"Error en parsear declaración: {self.token_actual}")

    def parsear_instruccion(self):
        print("Parsing instrucción:")
        if self.token_actual.tipo == "ID":
            self.consumir("ID")
            self.consumir("ASIGNACION")
            self.consumir("ID")
            self.consumir("SUMA")
            self.consumir("NUMERO")
            self.consumir("SEMICOLON")
        elif self.token_actual.tipo == "PALABRA_CLAVE" and self.token_actual.valor == "print":
            self.consumir("PALABRA_CLAVE")
            self.consumir("LPAREN")
            self.consumir("ID")
            self.consumir("RPAREN")
            self.consumir("SEMICOLON")
        else:
            print(f"Error en parsear instrucción: {self.token_actual}")

    def parsear(self):
        print("Inicio del análisis sintáctico:")
        while self.token_actual:
            if self.token_actual.tipo == "PALABRA_CLAVE" and self.token_actual.valor == "integer":
                self.parsear_declaracion()
            elif self.token_actual.tipo == "ID":
                self.parsear_instruccion()
            else:
                print(f"Error de parsing: Se esperaba una declaración. Token actual: {self.token_actual}")
                self.token_actual = self.escaner.obtener_token()
        print("Análisis sintáctico finalizado.")

# Ejecución del parser
parser = Parser(escaner)
parser.parsear()
escaner.mostrar_errores()


