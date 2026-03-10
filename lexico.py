import re

# === Análisis Léxico ===
# Definir los patrones para los diferentes tipos de tokens
token_patron = {
    "KEYWORD":    r'\b(if|else|while|for|return|int|float|void|println|print)\b',
    "STRING":     r'"[^"]*"',
    "IDENTIFIER": r'\b[a-zA-Z_][a-zA-Z0-9_]*\b',
    "NUMBER":     r'\b\d+(\.\d+)?\b',
    "OPERATOR":   r'[+\-*/=<>!]=?|&&|\|\|',
    "DELIMITER":  r'[();{},]',
    "WHITESPACE": r'\s+',
}

def identificar_tokens(texto):
    # Unimos todos los patrones en un único patrón usando grupos nombrados
    patron_general = '|'.join(
        f'(?P<{token}>{patron})'
        for token, patron in token_patron.items()
    )

    patron_regex = re.compile(patron_general)

    tokens_encontrados = []

    for match in patron_regex.finditer(texto):
        for token, valor in match.groupdict().items():
            if valor is not None and token != "WHITESPACE":  # Ignoramos espacios en blanco
                tokens_encontrados.append((token, valor))

    return tokens_encontrados


# ==========================
# DEFINICIÓN DEL AST
# ==========================

class NodoAST():
    # Clase base para todos los nodos del AST

    def traducirPy(self):
        # Traduccion de C++ a Python
        raise NotImplementedError("Metodo traducirPy() no implementado en este Nodo.")

    def traducirRuby(self):
        # Traduccion de C++ a Ruby
        raise NotImplementedError("Metodo traducirRuby() no implementado en este Nodo.")

    def generarCodigo(self):
        # Traduccion de C++ a ASSEMBLER
        raise NotImplementedError("Metodo generarCodigo() no implementado en este Nodo.")


# ==========================
# NODO PROGRAMA
# ==========================

class NodoPrograma(NodoAST):
    # Nodo que representa a un programa completo
    def __init__(self, funciones, main):
        self.variables = []
        self.funciones = funciones
        self.main = main

    def generarCodigo(self):
        codigo = ["section .text", "global _start"]
        data = ["section .bss"]

        # Recolectar variables de cada funcion
        for funcion in self.funciones:
            codigo.append(funcion.generarCodigo())

            for instruccion in funcion.cuerpo:
                if isinstance(instruccion, NodoAsignacion):
                    self.variables.append((instruccion.tipo[1], instruccion.nombre[1]))

            if len(funcion.parametros) > 0:
                for parametro in funcion.parametros:
                    self.variables.append((parametro.tipo[1], parametro.nombre[1]))

        # Recolectar variables del main
        for instruccion in self.main.cuerpo:
            if isinstance(instruccion, NodoAsignacion):
                self.variables.append((instruccion.tipo[1], instruccion.nombre[1]))

        codigo.append("_start:")
        codigo.append(self.main.generarCodigo())
        codigo.append("   mov eax, 1      ; syscall exit")
        codigo.append("   xor ebx, ebx    ; Codigo de salida 0")
        codigo.append("   int 0x80")

        for variable in self.variables:
            if variable[0] == 'int':
                data.append(f'  {variable[1]}:  resd 1')

        codigo = '\n'.join(codigo)
        return '\n'.join(data) + '\n' + codigo

    def traducirPy(self):
        resultado = []
        for funcion in self.funciones:
            resultado.append(funcion.traducirPy())
        resultado.append(self.main.traducirPy())
        return "\n\n".join(resultado)

    def traducirRuby(self):
        resultado = []
        for funcion in self.funciones:
            resultado.append(funcion.traducirRuby())
        resultado.append(self.main.traducirRuby())
        return "\n\n".join(resultado)


# ==========================
# NODO FUNCION
# ==========================

class NodoFuncion(NodoAST):
    # Nodo que representa la funcion
    def __init__(self, tipo, nombre, parametros, cuerpo):
        self.tipo = tipo
        self.nombre = nombre
        self.parametros = parametros
        self.cuerpo = cuerpo

    def generarCodigo(self):
        codigo = f'{self.nombre[1]}:\n'
        if len(self.parametros) > 0:
            for parametro in self.parametros:
                codigo += '\n   pop   eax'
                codigo += f'\n   mov [{parametro.nombre[1]}],   eax'
        codigo += '\n'.join(c.generarCodigo() for c in self.cuerpo)
        codigo += '\n    ret\n'
        return codigo

    def traducirPy(self):
        params = ", ".join(p.traducirPy() for p in self.parametros)
        lineas = []
        for c in self.cuerpo:
            if hasattr(c, 'traducirPy') and callable(c.traducirPy):
                try:
                    lineas.append(c.traducirPy(indent=1))
                except TypeError:
                    lineas.append(c.traducirPy())
        cuerpo = "\n    ".join(lineas)
        return f"def {self.nombre[1]}({params}):\n    {cuerpo}"

    def traducirRuby(self):
        params = ", ".join(p.traducirRuby() for p in self.parametros)
        lineas = []
        for c in self.cuerpo:
            if hasattr(c, 'traducirRuby') and callable(c.traducirRuby):
                try:
                    lineas.append(c.traducirRuby(indent=1))
                except TypeError:
                    lineas.append(c.traducirRuby())
        cuerpo = "\n    ".join(lineas)
        return f"def {self.nombre[1]}({params})\n    {cuerpo}\nend"


# ==========================
# NODO LLAMADA A FUNCION
# ==========================

class NodoLlamadaFuncion(NodoAST):
    # Nodo que representa una llamada a funcion generica
    def __init__(self, nombref, argumentos):
        self.nombre_funcion = nombref
        self.argumentos = argumentos

    def traducirPy(self):
        args = ", ".join(arg.traducirPy() for arg in self.argumentos)
        if self.nombre_funcion == "print":
            return f"print({args}, end='')"
        elif self.nombre_funcion == "println":
            return f"print({args})"
        else:
            return f"{self.nombre_funcion}({args})"

    def traducirRuby(self):
        args = ", ".join(arg.traducirRuby() for arg in self.argumentos)
        if self.nombre_funcion == "print":
            return f"print {args}"
        elif self.nombre_funcion == "println":
            return f"puts {args}"
        else:
            return f"{self.nombre_funcion}({args})"

    def generarCodigo(self):
        codigo = []
        for argumento in reversed(self.argumentos):
            codigo.append(argumento.generarCodigo())
            codigo.append('   push   eax')
        codigo.append(f'   call   {self.nombre_funcion}')
        return '\n'.join(codigo)


# ==========================
# NODO PRINT
# ==========================

class NodoPrint(NodoAST):
    # Nodo que representa print(expr) — sin salto de linea
    def __init__(self, expresion):
        self.expresion = expresion

    def traducirPy(self):
        return f"print({self.expresion.traducirPy()}, end='')"

    def traducirRuby(self):
        return f"print {self.expresion.traducirRuby()}"

    def generarCodigo(self):
        codigo = self.expresion.generarCodigo()
        codigo += '\n   push   eax'
        codigo += '\n   call   print'
        return codigo


# ==========================
# NODO PRINTLN
# ==========================

class NodoPrintln(NodoAST):
    # Nodo que representa println(expr) — con salto de linea
    def __init__(self, expresion):
        self.expresion = expresion

    def traducirPy(self):
        return f"print({self.expresion.traducirPy()})"

    def traducirRuby(self):
        return f"puts {self.expresion.traducirRuby()}"

    def generarCodigo(self):
        codigo = self.expresion.generarCodigo()
        codigo += '\n   push   eax'
        codigo += '\n   call   println'
        return codigo


# ==========================
# NODO IF / ELSE
# ==========================

class NodoIf(NodoAST):
    # Nodo que representa if (condicion) { cuerpo } [else { cuerpo_else }]
    # cuerpo_else puede ser None si no hay clausula else
    def __init__(self, condicion, cuerpo_if, cuerpo_else=None):
        self.condicion = condicion
        self.cuerpo_if = cuerpo_if
        self.cuerpo_else = cuerpo_else

    def traducirPy(self, indent=0):
        tab = "    " * indent
        condicion = self.condicion.traducirPy()
        cuerpo_if = f"\n{tab}    ".join(c.traducirPy() for c in self.cuerpo_if)
        resultado = f"if {condicion}:\n{tab}    {cuerpo_if}"
        if self.cuerpo_else:
            cuerpo_else = f"\n{tab}    ".join(c.traducirPy() for c in self.cuerpo_else)
            resultado += f"\n{tab}else:\n{tab}    {cuerpo_else}"
        return resultado

    def traducirRuby(self, indent=0):
        tab = "    " * indent
        condicion = self.condicion.traducirRuby()
        cuerpo_if = f"\n{tab}    ".join(c.traducirRuby() for c in self.cuerpo_if)
        resultado = f"if {condicion}\n{tab}    {cuerpo_if}"
        if self.cuerpo_else:
            cuerpo_else = f"\n{tab}    ".join(c.traducirRuby() for c in self.cuerpo_else)
            resultado += f"\n{tab}else\n{tab}    {cuerpo_else}"
        resultado += f"\n{tab}end"
        return resultado

    def generarCodigo(self):
        etiqueta_else = f"else_{id(self)}"
        etiqueta_fin  = f"fin_if_{id(self)}"
        codigo = []
        codigo.append(self.condicion.generarCodigo())
        codigo.append('   cmp   eax, 0')
        if self.cuerpo_else:
            codigo.append(f'   je    {etiqueta_else}')
        else:
            codigo.append(f'   je    {etiqueta_fin}')
        for instruccion in self.cuerpo_if:
            codigo.append(instruccion.generarCodigo())
        if self.cuerpo_else:
            codigo.append(f'   jmp   {etiqueta_fin}')
            codigo.append(f'{etiqueta_else}:')
            for instruccion in self.cuerpo_else:
                codigo.append(instruccion.generarCodigo())
        codigo.append(f'{etiqueta_fin}:')
        return '\n'.join(codigo)


# ==========================
# NODO WHILE
# ==========================

class NodoWhile(NodoAST):
    # Nodo que representa while (condicion) { cuerpo }
    def __init__(self, condicion, cuerpo):
        self.condicion = condicion
        self.cuerpo = cuerpo

    def traducirPy(self, indent=0):
        tab = "    " * indent
        condicion = self.condicion.traducirPy()
        cuerpo = f"\n{tab}    ".join(c.traducirPy() for c in self.cuerpo)
        return f"while {condicion}:\n{tab}    {cuerpo}"

    def traducirRuby(self, indent=0):
        tab = "    " * indent
        condicion = self.condicion.traducirRuby()
        cuerpo = f"\n{tab}    ".join(c.traducirRuby() for c in self.cuerpo)
        return f"while {condicion}\n{tab}    {cuerpo}\n{tab}end"

    def generarCodigo(self):
        etiqueta_inicio = f"inicio_while_{id(self)}"
        etiqueta_fin    = f"fin_while_{id(self)}"
        codigo = []
        codigo.append(f'{etiqueta_inicio}:')
        codigo.append(self.condicion.generarCodigo())
        codigo.append('   cmp   eax, 0')
        codigo.append(f'   je    {etiqueta_fin}')
        for instruccion in self.cuerpo:
            codigo.append(instruccion.generarCodigo())
        codigo.append(f'   jmp   {etiqueta_inicio}')
        codigo.append(f'{etiqueta_fin}:')
        return '\n'.join(codigo)


# ==========================
# NODO FOR
# ==========================

class NodoFor(NodoAST):
    # Nodo que representa for (inicio; condicion; incremento) { cuerpo }
    def __init__(self, inicio, condicion, incremento, cuerpo):
        self.inicio = inicio
        self.condicion = condicion
        self.incremento = incremento
        self.cuerpo = cuerpo

    def traducirPy(self, indent=0):
        tab = "    " * indent
        inicio     = self.inicio.traducirPy()
        condicion  = self.condicion.traducirPy()
        incremento = self.incremento.traducirPy()
        cuerpo     = f"\n{tab}    ".join(c.traducirPy() for c in self.cuerpo)
        return f"{inicio}\n{tab}while {condicion}:\n{tab}    {cuerpo}\n{tab}    {incremento}"

    def traducirRuby(self, indent=0):
        tab = "    " * indent
        inicio     = self.inicio.traducirRuby()
        condicion  = self.condicion.traducirRuby()
        incremento = self.incremento.traducirRuby()
        cuerpo     = f"\n{tab}    ".join(c.traducirRuby() for c in self.cuerpo)
        return f"{inicio}\n{tab}while {condicion}\n{tab}    {cuerpo}\n{tab}    {incremento}\n{tab}end"

    def generarCodigo(self):
        etiqueta_inicio = f"inicio_for_{id(self)}"
        etiqueta_fin    = f"fin_for_{id(self)}"
        codigo = []
        codigo.append(self.inicio.generarCodigo())
        codigo.append(f'{etiqueta_inicio}:')
        codigo.append(self.condicion.generarCodigo())
        codigo.append('   cmp   eax, 0')
        codigo.append(f'   je    {etiqueta_fin}')
        for instruccion in self.cuerpo:
            codigo.append(instruccion.generarCodigo())
        codigo.append(self.incremento.generarCodigo())
        codigo.append(f'   jmp   {etiqueta_inicio}')
        codigo.append(f'{etiqueta_fin}:')
        return '\n'.join(codigo)


# ==========================
# NODOS BÁSICOS
# ==========================

class NodoParametro(NodoAST):
    # Nodo que representa a un parametro de funcion
    def __init__(self, tipo, nombre):
        self.tipo = tipo
        self.nombre = nombre

    def traducirPy(self):
        return self.nombre[1]

    def traducirRuby(self):
        return self.nombre[1]


class NodoAsignacion(NodoAST):
    # Nodo que representa una declaracion + asignacion: int x = expr
    def __init__(self, tipo, nombre, expresion):
        self.tipo = tipo
        self.nombre = nombre
        self.expresion = expresion

    def generarCodigo(self):
        codigo = self.expresion.generarCodigo()
        codigo += f'\n   mov [{self.nombre[1]}], eax'
        return codigo

    def traducirPy(self):
        return f"{self.nombre[1]} = {self.expresion.traducirPy()}"

    def traducirRuby(self):
        return f"{self.nombre[1]} = {self.expresion.traducirRuby()}"


class NodoReasignacion(NodoAST):
    # Nodo que representa una reasignacion: x = expr (sin tipo)
    def __init__(self, nombre, expresion):
        self.nombre = nombre
        self.expresion = expresion

    def generarCodigo(self):
        codigo = self.expresion.generarCodigo()
        codigo += f'\n   mov [{self.nombre[1]}], eax'
        return codigo

    def traducirPy(self):
        return f"{self.nombre[1]} = {self.expresion.traducirPy()}"

    def traducirRuby(self):
        return f"{self.nombre[1]} = {self.expresion.traducirRuby()}"


class NodoOperacion(NodoAST):
    # Nodo que representa una operacion aritmetica o de comparacion
    def __init__(self, izquierda, operador, derecha):
        self.izquierda = izquierda
        self.operador = operador
        self.derecha = derecha

    def generarCodigo(self):
        codigo = []
        codigo.append(self.izquierda.generarCodigo())
        codigo.append('   push    eax')
        codigo.append(self.derecha.generarCodigo())
        codigo.append('   mov   ebx, eax')
        codigo.append('   pop    eax')
        op = self.operador[1]
        if op == '+':
            codigo.append('   add   eax, ebx')
        elif op == '-':
            codigo.append('   sub   eax, ebx')
        elif op == '*':
            codigo.append('   imul  eax, ebx')
        elif op in ('<', '>', '<=', '>=', '==', '!='):
            instruccion_salto = {
                '<': 'jl', '>': 'jg', '<=': 'jle',
                '>=': 'jge', '==': 'je', '!=': 'jne'
            }[op]
            etiqueta_true = f"cmp_true_{id(self)}"
            etiqueta_end  = f"cmp_end_{id(self)}"
            codigo.append('   cmp   eax, ebx')
            codigo.append('   mov   eax, 0')
            codigo.append(f'   {instruccion_salto}  {etiqueta_true}')
            codigo.append(f'   jmp   {etiqueta_end}')
            codigo.append(f'{etiqueta_true}:')
            codigo.append('   mov   eax, 1')
            codigo.append(f'{etiqueta_end}:')
        return '\n'.join(codigo)

    def traducirPy(self):
        return f"{self.izquierda.traducirPy()} {self.operador[1]} {self.derecha.traducirPy()}"

    def traducirRuby(self):
        return f"{self.izquierda.traducirRuby()} {self.operador[1]} {self.derecha.traducirRuby()}"


class NodoRetorno(NodoAST):
    # Nodo que representa un retorno de funcion
    def __init__(self, expresion):
        self.expresion = expresion

    def generarCodigo(self):
        return self.expresion.generarCodigo()

    def traducirPy(self):
        return f"return {self.expresion.traducirPy()}"

    def traducirRuby(self):
        return f"return {self.expresion.traducirRuby()}"


class NodoIdentificador(NodoAST):
    # Nodo que representa un identificador
    def __init__(self, nombre):
        self.nombre = nombre

    def generarCodigo(self):
        return f'\n   mov eax, [{self.nombre[1]}]'

    def traducirPy(self):
        return self.nombre[1]

    def traducirRuby(self):
        return self.nombre[1]


class NodoNumero(NodoAST):
    # Nodo que representa un numero
    def __init__(self, valor):
        self.valor = valor

    def generarCodigo(self):
        return f'\n   mov eax, {self.valor[1]}'

    def traducirPy(self):
        if isinstance(self.valor, tuple):
            return str(self.valor[1])
        return str(self.valor)

    def traducirRuby(self):
        if isinstance(self.valor, tuple):
            return str(self.valor[1])
        return str(self.valor)


class NodoString(NodoAST):
    # Nodo que representa una cadena de texto
    def __init__(self, valor):
        self.valor = valor

    def generarCodigo(self):
        return f'; cadena: {self.valor[1]}'

    def traducirPy(self):
        return self.valor[1]

    def traducirRuby(self):
        return self.valor[1]