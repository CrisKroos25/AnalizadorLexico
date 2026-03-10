import json
import lexico
import sintactico_ast


codigo_fuente = """
int suma(int a, int b) {
    int c = a + b;
    return c;
};

int main() {
    int resultado = suma(3, 4);
    println(resultado);

    int x = 10;
    if (x > 5) {
        println(x);
    } else {
        print(x);
    };

    int i = 0;
    while (i < 3) {
        println(i);
        i = i + 1;
    };

    int j = 0;
    for (int k = 0; k < 4; k = k + 1) {
        println(k);
    };

    print(resultado);
    println(resultado);

    return 0;
};
"""


# ==========================
# ANÁLISIS LÉXICO
# ==========================

tokens = lexico.identificar_tokens(codigo_fuente)

print("=== TOKENS ENCONTRADOS ===")
for tipo, valor in tokens:
    print(f"  {tipo:12}: {valor}")


# ==========================
# ANÁLISIS SINTÁCTICO
# ==========================

try:
    print("\n=== ANÁLISIS SINTÁCTICO ===")
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
            'programa': 'Noname',
            'funciones': [imprimir_ast(f) for f in nodo.funciones],
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
    elif isinstance(nodo, lexico.NodoReasignacion):
        return {
            "tipo": 'reasignacion',
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
        return nodo.nombre[1]
    elif isinstance(nodo, lexico.NodoNumero):
        return {"Numero": nodo.valor}
    elif isinstance(nodo, lexico.NodoString):
        return {"String": nodo.valor[1]}
    elif isinstance(nodo, lexico.NodoLlamadaFuncion):
        return {
            "LlamadaFuncion": nodo.nombre_funcion,
            "Argumentos": [imprimir_ast(a) for a in nodo.argumentos]
        }
    elif isinstance(nodo, lexico.NodoPrint):
        return {
            "tipo": "print",
            "expresion": imprimir_ast(nodo.expresion)
        }
    elif isinstance(nodo, lexico.NodoPrintln):
        return {
            "tipo": "println",
            "expresion": imprimir_ast(nodo.expresion)
        }
    elif isinstance(nodo, lexico.NodoIf):
        nodo_json = {
            "tipo": "if",
            "condicion": imprimir_ast(nodo.condicion),
            "cuerpo_if": [imprimir_ast(c) for c in nodo.cuerpo_if]
        }
        if nodo.cuerpo_else:
            nodo_json["cuerpo_else"] = [imprimir_ast(c) for c in nodo.cuerpo_else]
        return nodo_json
    elif isinstance(nodo, lexico.NodoWhile):
        return {
            "tipo": "while",
            "condicion": imprimir_ast(nodo.condicion),
            "cuerpo": [imprimir_ast(c) for c in nodo.cuerpo]
        }
    elif isinstance(nodo, lexico.NodoFor):
        return {
            "tipo": "for",
            "inicio": imprimir_ast(nodo.inicio),
            "condicion": imprimir_ast(nodo.condicion),
            "incremento": imprimir_ast(nodo.incremento),
            "cuerpo": [imprimir_ast(c) for c in nodo.cuerpo]
        }
    else:
        return {}


# ==========================
# MOSTRAR AST EN FORMATO JSON
# ==========================

if arbol_ast:
    print("\n=== AST GENERADO ===")
    print(json.dumps(imprimir_ast(arbol_ast), indent=4))

    print("\n=== TRADUCCIÓN A PYTHON ===")
    print(arbol_ast.traducirPy())

    print("\n=== TRADUCCIÓN A RUBY ===")
    print(arbol_ast.traducirRuby())