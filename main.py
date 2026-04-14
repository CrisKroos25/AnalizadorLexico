import json
import lexico
import sintactico_ast
import subprocess

codigo_fuente = """
int suma(int a, int b) {
    int c = a + b;
    return c;
};

int main() {
    int resultado = suma(1,2);
    return 0};
"""
    

# ==========================
# ANÁLISIS LÉXICO
# ==========================

tokens = lexico.identificar_tokens(codigo_fuente)

print("Tokens encontrados:")
for tipo, valor in tokens:
    print(f"{tipo}: {valor}")

# ==========================
# ANÁLISIS SINTÁCTICO
# ==========================

try:
    print("\nIniciando análisis sintáctico...")
    parser = sintactico_ast.Parser(tokens)
    arbol_ast = parser.parsear()
    print("Análisis sintáctico completo sin errores.")
except SyntaxError as e:
    print(e)
    arbol_ast = None


# ==========================
# FUNCIÓN PARA IMPRIMIR AST
# ==========================

def imprimir_ast(nodo):

    if isinstance(nodo, lexico.NodoPrograma):
        return {
            'programa' : 'Noname',
            'funciones' : [imprimir_ast(f) for f in nodo.funciones],
            'main': imprimir_ast(nodo.main)
        }
    elif isinstance(nodo, lexico.NodoFuncion):
        return {
            "nombre": nodo.nombre[1],
            "parametros": [imprimir_ast(p) for p in nodo.parametros],
            "cuerpo": [imprimir_ast(c) for c in nodo.cuerpo]
        }

    elif isinstance(nodo, lexico.NodoParametro):
        return {
            "id": nodo.nombre[1],
            "tipo": nodo.tipo[1]
        }

    elif isinstance(nodo, lexico.NodoAsignacion):
        return {
            "tipo": 'asignacion',
            "variable": nodo.nombre[1],
            "expresion": imprimir_ast(nodo.expresion)
        }

    elif isinstance(nodo, lexico.NodoOperacion):
        return {
            "op": nodo.operador[1],
            "izq": imprimir_ast(nodo.izquierda),
            "der": imprimir_ast(nodo.derecha)
        }

    elif isinstance(nodo, lexico.NodoRetorno):
        return {
            "tipo": "return",
            "valor": imprimir_ast(nodo.expresion)
        }

    elif isinstance(nodo, lexico.NodoIdentificador):
        return nodo.nombre[1]   #Devolver solo el nombre como string

    elif isinstance(nodo, lexico.NodoNumero):
        return {
            "Numero": nodo.valor
        }
    
    elif isinstance(nodo, lexico.NodoLlamadaFuncion):
        return {
            "LlamadaFuncion": nodo.nombre_funcion,
            "Argumentos": [imprimir_ast(a) for a in nodo.argumentos]
        }

    else:
        return {}


# ==========================
# MOSTRAR AST EN FORMATO JSON
# ==========================

if arbol_ast:
    print("\nAST generado:")
    print(json.dumps(imprimir_ast(arbol_ast), indent=4))


nodoExp = lexico.NodoOperacion(lexico.NodoNumero(5), '+' , lexico.NodoNumero(8))
print(json.dumps(imprimir_ast(nodoExp), indent=1))

print(arbol_ast.traducirPy())
print(arbol_ast.traducirRuby())



def compilar(programa):
    #Generar el codigo en ensamblador
    codigo_asm = programa.generar_codigo()
    print(codigo_asm)
    text_file = open("ejasmcompiladores.asm", "w")
    text_file.write(codigo_asm)
    text_file.close()

    subprocess.run(["nasm", "-f", "elf", "ejasmcompiladores.asm"])
    subprocess.run(["ld" "-m" "elf_i386" "ejasmcompiladores.o" "-o" "ejasmcompiladores"])