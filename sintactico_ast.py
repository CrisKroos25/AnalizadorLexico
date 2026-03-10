import lexico

# Analizador sintactico 
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def obtener_token_actual(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def coincidir(self, tipo_esperado):
        token_actual = self.obtener_token_actual()
        if token_actual and token_actual[0] == tipo_esperado:
            self.pos += 1
            return token_actual
        else:
            raise SyntaxError(f"Error sintactico: Se esperaba {tipo_esperado}, pero se encontro: {token_actual}")

    # ----------------------------------------
    # PUNTO DE ENTRADA
    # ----------------------------------------

    def parsear(self):
        # Parsea múltiples funciones y retorna un NodoPrograma
        funciones = []
        main = None

        while self.obtener_token_actual() is not None:
            nodo_funcion = self.funcion()
            if nodo_funcion.nombre[1] == 'main':
                main = nodo_funcion
            else:
                funciones.append(nodo_funcion)

        return lexico.NodoPrograma(funciones, main)

    # ----------------------------------------
    # FUNCION
    # ----------------------------------------

    def funcion(self):
        # Gramatica: tipo IDENTIFIER ( [parametros] ) { cuerpo }
        tipo_retorno    = self.coincidir('KEYWORD')         # Tipo de retorno (ej. int)
        nombre_funcion  = self.coincidir('IDENTIFIER')      # Nombre de la funcion
        self.coincidir('DELIMITER')                         # Se espera (

        if nombre_funcion[1] == 'main':
            parametros = []
        else:
            if self.obtener_token_actual() and self.obtener_token_actual()[1] == ')':
                parametros = []
            else:
                parametros = self.parametros()

        self.coincidir('DELIMITER')                         # Se espera )
        self.coincidir('DELIMITER')                         # Se espera {
        cuerpo = self.cuerpo()                              # Cuerpo de la funcion
        self.coincidir('DELIMITER')                         # Se espera }

        # Consumir el ; opcional despues del } (ej. };)
        if self.obtener_token_actual() and self.obtener_token_actual()[1] == ';':
            self.coincidir('DELIMITER')

        return lexico.NodoFuncion(tipo_retorno, nombre_funcion, parametros, cuerpo)

    # ----------------------------------------
    # PARAMETROS
    # ----------------------------------------

    def parametros(self):
        lista_parametros = []

        # Regla: tipo IDENTIFIER (, tipo IDENTIFIER)*
        tipo   = self.coincidir('KEYWORD')
        nombre = self.coincidir('IDENTIFIER')
        lista_parametros.append(lexico.NodoParametro(tipo, nombre))

        while self.obtener_token_actual() and self.obtener_token_actual()[1] == ',':
            self.coincidir('DELIMITER')
            tipo   = self.coincidir('KEYWORD')
            nombre = self.coincidir('IDENTIFIER')
            lista_parametros.append(lexico.NodoParametro(tipo, nombre))

        return lista_parametros

    # ----------------------------------------
    # CUERPO
    # ----------------------------------------

    def cuerpo(self):
        instrucciones = []

        while self.obtener_token_actual() and self.obtener_token_actual()[1] != '}':
            token = self.obtener_token_actual()

            if token[1] == 'return':
                instrucciones.append(self.retorno())

            elif token[1] == 'if':
                instrucciones.append(self.instruccion_if())
                # Consumir ; opcional despues del bloque (ej. };)
                if self.obtener_token_actual() and self.obtener_token_actual()[1] == ';':
                    self.coincidir('DELIMITER')

            elif token[1] == 'while':
                instrucciones.append(self.instruccion_while())
                if self.obtener_token_actual() and self.obtener_token_actual()[1] == ';':
                    self.coincidir('DELIMITER')

            elif token[1] == 'for':
                instrucciones.append(self.instruccion_for())
                if self.obtener_token_actual() and self.obtener_token_actual()[1] == ';':
                    self.coincidir('DELIMITER')

            elif token[1] == 'print':
                instrucciones.append(self.instruccion_print())

            elif token[1] == 'println':
                instrucciones.append(self.instruccion_println())

            elif token[0] == 'KEYWORD':
                # Cualquier otro keyword es una declaracion+asignacion: tipo IDENTIFIER = expr;
                instrucciones.append(self.asignacion())

            elif token[0] == 'IDENTIFIER':
                # Puede ser reasignacion (x = ...) o llamada a funcion (f(...))
                instrucciones.append(self.instruccion_identificador())

            else:
                raise SyntaxError(f"Instruccion no valida: {token}")

        return instrucciones

    # ----------------------------------------
    # INSTRUCCIONES ESPECÍFICAS
    # ----------------------------------------

    def asignacion(self):
        # Gramatica: tipo IDENTIFIER = expresion ;
        tipo    = self.coincidir('KEYWORD')
        nombre  = self.coincidir('IDENTIFIER')
        self.coincidir('OPERATOR')                          # Se espera =
        expresion = self.expresion()
        self.coincidir('DELIMITER')                         # Se espera ;
        return lexico.NodoAsignacion(tipo, nombre, expresion)

    def instruccion_identificador(self):
        # Decide si es reasignacion (x = ...) o llamada a funcion (f(...))
        identificador = self.coincidir('IDENTIFIER')
        token_sig = self.obtener_token_actual()

        if token_sig and token_sig[1] == '(':
            # Llamada como instruccion: f(args);
            self.coincidir('DELIMITER')                     # Se espera (
            argumentos = self.llamadaFuncion()
            self.coincidir('DELIMITER')                     # Se espera )
            self.coincidir('DELIMITER')                     # Se espera ;
            return lexico.NodoLlamadaFuncion(identificador[1], argumentos)

        elif token_sig and token_sig[0] == 'OPERATOR' and token_sig[1] == '=':
            # Reasignacion: x = expresion;
            self.coincidir('OPERATOR')                      # Se espera =
            expresion = self.expresion()
            self.coincidir('DELIMITER')                     # Se espera ;
            return lexico.NodoReasignacion(identificador, expresion)

        else:
            raise SyntaxError(f"Se esperaba '(' o '=' despues de identificador, pero se encontro: {token_sig}")

    def retorno(self):
        self.coincidir('KEYWORD')                           # Se espera return
        expresion = self.expresion()
        self.coincidir('DELIMITER')                         # Se espera ;
        return lexico.NodoRetorno(expresion)

    # ----------------------------------------
    # INSTRUCCION PRINT
    # ----------------------------------------

    def instruccion_print(self):
        # Gramatica: print ( expresion ) ;
        self.coincidir('KEYWORD')                           # Se espera print
        self.coincidir('DELIMITER')                         # Se espera (
        expresion = self.expresion()
        self.coincidir('DELIMITER')                         # Se espera )
        self.coincidir('DELIMITER')                         # Se espera ;
        return lexico.NodoPrint(expresion)

    # ----------------------------------------
    # INSTRUCCION PRINTLN
    # ----------------------------------------

    def instruccion_println(self):
        # Gramatica: println ( expresion ) ;
        self.coincidir('KEYWORD')                           # Se espera println
        self.coincidir('DELIMITER')                         # Se espera (
        expresion = self.expresion()
        self.coincidir('DELIMITER')                         # Se espera )
        self.coincidir('DELIMITER')                         # Se espera ;
        return lexico.NodoPrintln(expresion)

    # ----------------------------------------
    # INSTRUCCION IF / ELSE
    # ----------------------------------------

    def instruccion_if(self):
        # Gramatica: if ( condicion ) { cuerpo } [else { cuerpo }]
        self.coincidir('KEYWORD')                           # Se espera if
        self.coincidir('DELIMITER')                         # Se espera (
        condicion = self.expresion()
        self.coincidir('DELIMITER')                         # Se espera )
        self.coincidir('DELIMITER')                         # Se espera {
        cuerpo_if = self.cuerpo()
        self.coincidir('DELIMITER')                         # Se espera }

        # Verificar si hay clausula else
        cuerpo_else = None
        if self.obtener_token_actual() and self.obtener_token_actual()[1] == 'else':
            self.coincidir('KEYWORD')                       # Se espera else
            self.coincidir('DELIMITER')                     # Se espera {
            cuerpo_else = self.cuerpo()
            self.coincidir('DELIMITER')                     # Se espera }

        return lexico.NodoIf(condicion, cuerpo_if, cuerpo_else)

    # ----------------------------------------
    # INSTRUCCION WHILE
    # ----------------------------------------

    def instruccion_while(self):
        # Gramatica: while ( condicion ) { cuerpo }
        self.coincidir('KEYWORD')                           # Se espera while
        self.coincidir('DELIMITER')                         # Se espera (
        condicion = self.expresion()
        self.coincidir('DELIMITER')                         # Se espera )
        self.coincidir('DELIMITER')                         # Se espera {
        cuerpo = self.cuerpo()
        self.coincidir('DELIMITER')                         # Se espera }
        return lexico.NodoWhile(condicion, cuerpo)

    # ----------------------------------------
    # INSTRUCCION FOR
    # ----------------------------------------

    def instruccion_for(self):
        # Gramatica: for ( inicio ; condicion ; incremento ) { cuerpo }
        self.coincidir('KEYWORD')                           # Se espera for
        self.coincidir('DELIMITER')                         # Se espera (

        # inicio: puede ser declaracion (int i = 0) o reasignacion (i = 0)
        token = self.obtener_token_actual()
        if token[0] == 'KEYWORD':
            inicio = self.asignacion()                      # tipo IDENTIFIER = expr ;
        elif token[0] == 'IDENTIFIER':
            identificador = self.coincidir('IDENTIFIER')
            self.coincidir('OPERATOR')                      # Se espera =
            expresion = self.expresion()
            self.coincidir('DELIMITER')                     # Se espera ;
            inicio = lexico.NodoReasignacion(identificador, expresion)
        else:
            raise SyntaxError(f"Se esperaba inicio de for, pero se encontro: {token}")

        condicion = self.expresion()
        self.coincidir('DELIMITER')                         # Se espera ;

        # incremento: reasignacion sin ; final (ej: i = i + 1)
        identificador = self.coincidir('IDENTIFIER')
        self.coincidir('OPERATOR')                          # Se espera =
        expresion_inc = self.expresion()
        incremento = lexico.NodoReasignacion(identificador, expresion_inc)

        self.coincidir('DELIMITER')                         # Se espera )
        self.coincidir('DELIMITER')                         # Se espera {
        cuerpo = self.cuerpo()
        self.coincidir('DELIMITER')                         # Se espera }

        return lexico.NodoFor(inicio, condicion, incremento, cuerpo)

    # ----------------------------------------
    # EXPRESIONES Y TERMINOS
    # ----------------------------------------

    def expresion(self):
        izquierda = self.termino()
        while self.obtener_token_actual() and self.obtener_token_actual()[0] == 'OPERATOR':
            # Detenerse si el operador es = (es asignacion, no expresion)
            if self.obtener_token_actual()[1] == '=':
                break
            operador = self.coincidir('OPERATOR')
            derecha = self.termino()
            izquierda = lexico.NodoOperacion(izquierda, operador, derecha)
        return izquierda

    def termino(self):
        token = self.obtener_token_actual()

        if token[0] == 'NUMBER':
            return lexico.NodoNumero(self.coincidir('NUMBER'))

        elif token[0] == 'STRING':
            return lexico.NodoString(self.coincidir('STRING'))

        elif token[0] == 'IDENTIFIER':
            identificador = self.coincidir('IDENTIFIER')
            # Verificar si es llamada a funcion dentro de expresion
            if self.obtener_token_actual() and self.obtener_token_actual()[1] == '(':
                self.coincidir('DELIMITER')                 # Se espera (
                argumentos = self.llamadaFuncion()
                self.coincidir('DELIMITER')                 # Se espera )
                return lexico.NodoLlamadaFuncion(identificador[1], argumentos)
            else:
                return lexico.NodoIdentificador(identificador)

        elif token[0] == 'KEYWORD' and token[1] in ('print', 'println'):
            # print/println usados como expresion (valor de retorno)
            if token[1] == 'print':
                self.coincidir('KEYWORD')
                self.coincidir('DELIMITER')
                expresion = self.expresion()
                self.coincidir('DELIMITER')
                return lexico.NodoPrint(expresion)
            else:
                self.coincidir('KEYWORD')
                self.coincidir('DELIMITER')
                expresion = self.expresion()
                self.coincidir('DELIMITER')
                return lexico.NodoPrintln(expresion)

        else:
            raise SyntaxError(f'Expresion no valida: {token}')

    def llamadaFuncion(self):
        argumentos = []

        # Si no hay argumentos
        if self.obtener_token_actual() and self.obtener_token_actual()[1] == ')':
            return argumentos

        # Regla: expr (, expr)*
        sigue = True
        while sigue:
            sigue = False
            argumentos.append(self.expresion())
            if self.obtener_token_actual() and self.obtener_token_actual()[1] == ',':
                self.coincidir('DELIMITER')                 # Se espera ,
                sigue = True

        return argumentos

    def llamadaComoInstruccion(self):
        identificador = self.coincidir('IDENTIFIER')
        self.coincidir('DELIMITER')                         # Se espera (
        argumentos = self.llamadaFuncion()
        self.coincidir('DELIMITER')                         # Se espera )
        self.coincidir('DELIMITER')                         # Se espera ;
        return lexico.NodoLlamadaFuncion(identificador[1], argumentos)