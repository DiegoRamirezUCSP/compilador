class Escaner:
    def __init__(self, source_code):
        self.source_code = source_code
        self.index = 0
        self.line = 1
        self.column = 1
        self.OPERATORS = ['+', '-', '*', '/', '%', '=', '==', '!=', '<', '>', '<=', '>=', '&&', '||', '&', '++', '--']
        self.DELIMITERS = ['(', ')', '{', '}', ';', ',']
        self.keywords = ['int', 'char', 'bool', 'string', 'void', 'if', 'else', 'while', 'return', 'print']
        self.tokens = []

    def handle_whitespace_and_comments(self):
        while self.index < len(self.source_code) and self.source_code[self.index].isspace():
            if self.source_code[self.index] == '\n':
                self.line += 1
                self.column = 0
            self.index += 1
            self.column += 1
        if self.source_code[self.index:self.index + 2] == "//":
            while self.index < len(self.source_code) and self.source_code[self.index] != '\n':
                self.index += 1
                self.column += 1
        elif self.source_code[self.index:self.index + 2] == "/*":
            self.index += 2
            self.column += 2
            while self.index < len(self.source_code) and self.source_code[self.index:self.index + 2] != "*/":
                if self.source_code[self.index] == '\n':
                    self.line += 1
                    self.column = 0
                self.index += 1
                self.column += 1
            self.index += 2  # Saltar '*/'

    def recognize_identifiers_and_keywords(self):
        start_index = self.index
        while self.index < len(self.source_code) and (self.source_code[self.index].isalnum() or self.source_code[self.index] == '_'):
            self.index += 1
            self.column += 1
        token_value = self.source_code[start_index:self.index]
        if token_value in self.keywords:
            return "KEYWORD", token_value
        else:
            return "IDENTIFIER", token_value

    def recognize_integer(self):
        start_index = self.index
        while self.index < len(self.source_code) and self.source_code[self.index].isdigit():
            self.index += 1
            self.column += 1
        token_value = self.source_code[start_index:self.index]
        return "INTEGER", token_value

    def recognize_characters_and_strings(self):
        start_char = self.source_code[self.index]
        self.index += 1  # Saltar comilla inicial
        self.column += 1
        start_index = self.index
        while self.index < len(self.source_code) and self.source_code[self.index] != start_char:
            if self.source_code[self.index] == '\\':  # Manejo de caracteres de escape
                self.index += 1
                self.column += 1
            self.index += 1
            self.column += 1
        token_value = self.source_code[start_index:self.index]
        self.index += 1  # Saltar comilla final
        self.column += 1
        if start_char == "'":
            if len(token_value) == 1 or (len(token_value) == 2 and token_value[0] == '\\'):
                return "CHAR", token_value
            else:
                return "ERROR", "Carácter inválido"
        else:
            return "STRING", token_value

    def recognize_operators_and_delimiters(self):
        # Verificar operadores de dos caracteres primero
        if self.index + 1 < len(self.source_code) and self.source_code[self.index:self.index + 2] in self.OPERATORS:
            operator = self.source_code[self.index:self.index + 2]
            self.index += 2
            self.column += 2
            return "OPERATOR", operator
        # Verificar operadores de un solo carácter
        elif self.source_code[self.index] in self.OPERATORS:
            operator = self.source_code[self.index]
            self.index += 1
            self.column += 1
            return "OPERATOR", operator
        # Verificar delimitadores
        elif self.source_code[self.index] in self.DELIMITERS:
            delimiter = self.source_code[self.index]
            self.index += 1
            self.column += 1
            return "DELIMITER", delimiter
        else:
            raise ValueError(f"Operador o delimitador no válido en la línea {self.line}, columna {self.column}")

    def handle_errors(self):
        print(f"Error léxico: carácter no reconocido '{self.source_code[self.index]}' en la línea {self.line}, columna {self.column}")
        self.index += 1

    def scan(self):
        while self.index < len(self.source_code):
            self.handle_whitespace_and_comments()

            if self.index >= len(self.source_code):
                break

            char = self.source_code[self.index]

            if char.isalpha() or char == '_':
                token_type, token_value = self.recognize_identifiers_and_keywords()
            elif char.isdigit():
                token_type, token_value = self.recognize_integer()
            elif char in ['"', "'"]:
                token_type, token_value = self.recognize_characters_and_strings()
            elif char in self.OPERATORS or char in self.DELIMITERS:
                try:
                    token_type, token_value = self.recognize_operators_and_delimiters()
                except ValueError as e:
                    print(e)
                    self.handle_errors()
                    continue
            else:
                self.handle_errors()
                continue

            # Agregar la información de línea y columna al token
            self.tokens.append((token_type, token_value, (self.line, self.column)))
            print(f"Token: {token_type}, Valor: {token_value} en la línea {self.line}, columna {self.column}")

        return self.tokens
    
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        self.symbol_table = {}

    def parse(self):
        while self.current < len(self.tokens):
            self.parse_global_decls()

    def parse_global_decls(self):
        while self.current < len(self.tokens):
            if self.tokens[self.current][0] == "KEYWORD":
                if self.tokens[self.current][1] in ["int", "char", "bool", "string"]:
                    self.parse_var_decl()
                elif self.tokens[self.current][1] == "void":
                    self.parse_function()
            else:
                break

    def parse_var_decl(self):
        type_token = self.match("KEYWORD")
        identifier_token = self.match("IDENTIFIER")
        if self.current < len(self.tokens) and self.tokens[self.current][0] == "OPERATOR" and self.tokens[self.current][1] == "=":
            self.match("OPERATOR")  # =
            expr = self.parse_expression()  # Parsear expresión de asignación
            print(f"{type_token[1]} {identifier_token[1]} = {expr};")
        self.match("DELIMITER")  # ;

    def parse_function(self):
        type_token = self.match("KEYWORD")
        identifier_token = self.match("IDENTIFIER")
        self.match("DELIMITER")  # (
        params = self.parse_params()
        self.match("DELIMITER")  # )
        self.match("DELIMITER")  # {
        self.symbol_table[identifier_token[1]] = {"type": type_token[1], "params": params, "scope": "global"}
        self.parse_stmt_list()
        self.match("DELIMITER")  # }

    def parse_params(self):
        params = []
        if self.tokens[self.current][0] == "KEYWORD":
            while True:
                type_token = self.match("KEYWORD")
                identifier_token = self.match("IDENTIFIER")
                params.append((type_token[1], identifier_token[1]))
                if self.tokens[self.current][0] == "DELIMITER" and self.tokens[self.current][1] == ',':
                    self.match("DELIMITER")  # ,
                else:
                    break
        return params

    def parse_stmt_list(self):
        while self.current < len(self.tokens) and self.tokens[self.current][0] != "DELIMITER":
            self.parse_statement()

    def parse_statement(self):
        if self.tokens[self.current][0] == "KEYWORD" and self.tokens[self.current][1] == "if":
            self.parse_if_stmt()
        elif self.tokens[self.current][0] == "KEYWORD" and self.tokens[self.current][1] == "for":
            self.parse_for_stmt()
        elif self.tokens[self.current][0] == "KEYWORD" and self.tokens[self.current][1] == "print":
            self.parse_print_stmt()
        elif self.tokens[self.current][0] == "KEYWORD" and self.tokens[self.current][1] == "return":
            self.parse_return_stmt()
        else:
            self.parse_expr_stmt()

    def parse_if_stmt(self):
        self.match("KEYWORD")  # if
        self.match("DELIMITER")  # (
        condition = self.parse_expression()  # Parsear condición
        self.match("DELIMITER")  # )
        then_stmt = self.parse_statement()  # Parsear declaración "then"
        if self.current < len(self.tokens) and self.tokens[self.current][0] == "KEYWORD" and self.tokens[self.current][1] == "else":
            self.match("KEYWORD")  # else
            else_stmt = self.parse_statement()  # Parsear declaración "else"
            print(f"if ({condition}) {{ {then_stmt} }} else {{ {else_stmt} }}")
        else:
            print(f"if ({condition}) {{ {then_stmt} }}")

    def parse_for_stmt(self):
        self.match("KEYWORD")  # for
        self.match("DELIMITER")  # (
        init_stmt = self.parse_expr_stmt()  # Inicialización
        condition = self.parse_expression()  # Condición
        self.match("DELIMITER")  # ;
        increment_stmt = self.parse_expr_stmt()  # Incremento
        self.match("DELIMITER")  # )
        body_stmt = self.parse_statement()  # Cuerpo del bucle
        print(f"for ({init_stmt}; {condition}; {increment_stmt}) {{ {body_stmt} }}")

    def parse_print_stmt(self):
        self.match("KEYWORD")  # print
        self.match("DELIMITER")  # (
        expr = self.parse_expr_list()  # Parsear lista de expresiones
        self.match("DELIMITER")  # )
        print(f"print({expr});")

    def parse_expr_list(self):
        exprs = []
        while True:
            expr = self.parse_expression()
            exprs.append(expr)
            if self.current < len(self.tokens) and self.tokens[self.current][0] == "DELIMITER" and self.tokens[self.current][1] == ',':
                self.match("DELIMITER")  # ,
            else:
                break
        return ', '.join(exprs)

    def parse_expr_stmt(self):
        expr = self.parse_expression()
        self.match("DELIMITER")  # ;

    def parse_return_stmt(self):
        self.match("KEYWORD")  # return
        expr = self.parse_expression()  # Parsear expresión
        self.match("DELIMITER")  # ;

    def parse_expression(self):
        if self.tokens[self.current][0] == "IDENTIFIER" and self.tokens[self.current + 1][0] == "OPERATOR" and self.tokens[self.current + 1][1] == '=':
            identifier = self.match("IDENTIFIER")
            self.match("OPERATOR")  # =
            expr = self.parse_or_expr()  # Obtener la expresión a la derecha de la asignación
            return f"{identifier[1]} = {expr}"
        elif self.tokens[self.current][0] == "IDENTIFIER" and self.tokens[self.current + 1][0] == "DELIMITER" and self.tokens[self.current + 1][1] == '(':
            function_call = self.parse_function_call()  # Llamada a la función
            return function_call
        else:
            return self.parse_or_expr()

    def parse_function_call(self):
        identifier = self.match("IDENTIFIER")
        self.match("DELIMITER")  # (
        args = self.parse_expr_list()  # Obtener argumentos
        self.match("DELIMITER")  # )
        return f"{identifier[1]}({args})"

    def parse_or_expr(self):
        left = self.parse_and_expr()
        while self.current < len(self.tokens) and self.tokens[self.current][0] == "OPERATOR" and self.tokens[self.current][1] == "||":
            self.match("OPERATOR")  # ||
            right = self.parse_and_expr()
            left = f"({left} || {right})"
        return left

    def parse_and_expr(self):
        left = self.parse_eq_expr()
        while self.current < len(self.tokens) and self.tokens[self.current][0] == "OPERATOR" and self.tokens[self.current][1] == "&&":
            self.match("OPERATOR")  # &&
            right = self.parse_eq_expr()
            left = f"({left} && {right})"
        return left

    def parse_eq_expr(self):
        left = self.parse_rel_expr()
        while self.current < len(self.tokens) and self.tokens[self.current][0] == "OPERATOR" and self.tokens[self.current][1] in ["==", "!="]:
            op = self.match("OPERATOR")[1]
            right = self.parse_rel_expr()
            left = f"({left} {op} {right})"
        return left

    def parse_rel_expr(self):
        left = self.parse_add_expr()
        while self.current < len(self.tokens) and self.tokens[self.current][0] == "OPERATOR" and self.tokens[self.current][1] in ["<", ">", "<=", ">="]:
            op = self.match("OPERATOR")[1]
            right = self.parse_add_expr()
            left = f"({left} {op} {right})"
        return left

    def parse_add_expr(self):
        left = self.parse_mul_expr()
        while self.current < len(self.tokens) and self.tokens[self.current][0] == "OPERATOR" and self.tokens[self.current][1] in ["+", "-"]:
            op = self.match("OPERATOR")[1]
            right = self.parse_mul_expr()
            left = f"({left} {op} {right})"
        return left

    def parse_mul_expr(self):
        left = self.parse_unary()
        while self.current < len(self.tokens) and self.tokens[self.current][0] == "OPERATOR" and self.tokens[self.current][1] in ["*", "/", "%"]:
            op = self.match("OPERATOR")[1]
            right = self.parse_unary()
            left = f"({left} {op} {right})"
        return left

    def parse_unary(self):
        if self.tokens[self.current][0] == "OPERATOR" and self.tokens[self.current][1] in ["!", "-"]:
            op = self.match("OPERATOR")[1]
            operand = self.parse_unary()
            return f"{op}{operand}"
        else:
            return self.parse_factor()

    def parse_factor(self):
        if self.tokens[self.current][0] == "IDENTIFIER":
            return self.match("IDENTIFIER")[1]
        elif self.tokens[self.current][0] == "INTEGER":
            return self.match("INTEGER")[1]
        elif self.tokens[self.current][0] == "DELIMITER" and self.tokens[self.current][1] == "(":
            self.match("DELIMITER")  # (
            expr = self.parse_expression()
            self.match("DELIMITER")  # )
            return f"({expr})"
        else:
            raise SyntaxError(f"Error de sintaxis: se esperaba un factor pero se encontró {self.tokens[self.current]}")

    def match(self, expected_type):
        if self.tokens[self.current][0] == expected_type:
            token = self.tokens[self.current]
            self.current += 1
            return token
        else:
            raise SyntaxError(f"Error de sintaxis: se esperaba {expected_type} pero se encontró {self.tokens[self.current]}")

def leer_codigo_desde_archivo(nombre_archivo):
    with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
        return archivo.read()

nombre_archivo = 'codigo_fuente.txt'
codigo = leer_codigo_desde_archivo(nombre_archivo)
escaner = Escaner(codigo))
tokens = escaner.scan()
parser = Parser(tokens)
parser.parse()
print(parser.symbol_table)  # Mostrar la tabla de símbolos
