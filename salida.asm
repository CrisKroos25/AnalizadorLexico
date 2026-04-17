section .data
    newline  db  0x0A          ; salto de linea
    digbuf   times 12 db 0     ; buffer conversion entero->string
    str_0  db  'Inicio del programa', 0
    str_0_len  equ  $ - str_0 - 1
    str_1  db  'Resultado de suma(3,4): ', 0
    str_1_len  equ  $ - str_1 - 1
    str_2  db  'x es mayor que 5', 0
    str_2_len  equ  $ - str_2 - 1
    str_3  db  'x es menor o igual a 5', 0
    str_3_len  equ  $ - str_3 - 1
    str_4  db  'Conteo while:', 0
    str_4_len  equ  $ - str_4 - 1
    str_5  db  'Conteo for:', 0
    str_5_len  equ  $ - str_5 - 1
    str_6  db  'Fin del programa', 0
    str_6_len  equ  $ - str_6 - 1
    str_7  db  'Hola %d', 0x0A, '', 0
    str_7_len  equ  $ - str_7 - 1

section .bss
    c:  resd 1
    a:  resd 1
    b:  resd 1
    resultado:  resd 1
    x:  resd 1
    i:  resd 1
    k:  resd 1

section .text
global _start
extern printf


; -------------------------------------------------------
; __int_to_str: convierte EAX a decimal ASCII en digbuf
;   Entrada : EAX = entero a convertir
;   Salida  : ESI = puntero al primer digito en digbuf
;             ECX = longitud de la cadena
; -------------------------------------------------------
__int_to_str:
    push ebx
    push edx
    push edi
    mov  edi, digbuf        ; apuntar al buffer
    add  edi, 11            ; empezar por el final
    mov  byte [edi], 0      ; terminador nulo
    mov  ebx, 10            ; divisor decimal
    test eax, eax
    jnz  .convertir
    ; caso especial: eax == 0
    dec  edi
    mov  byte [edi], '0'
    jmp  .fin
.convertir:
    test eax, eax
    jz   .fin
    xor  edx, edx
    div  ebx                ; eax = cociente, edx = resto
    add  dl, '0'
    dec  edi
    mov  [edi], dl
    jmp  .convertir
.fin:
    mov  esi, edi           ; ESI = inicio del string
    mov  ecx, digbuf
    add  ecx, 11
    sub  ecx, esi           ; ECX = longitud
    pop  edi
    pop  edx
    pop  ebx
    ret

; -------------------------------------------------------
; __print_int: imprime EAX como entero decimal (sin newline)
;   Entrada : EAX = entero
; -------------------------------------------------------
__print_int:
    call __int_to_str       ; ESI = ptr, ECX = len
    mov  eax, 4             ; sys_write
    mov  ebx, 1             ; stdout
    ; ecx = ptr (usar esi)
    push ecx
    mov  ecx, esi
    pop  edx                ; edx = longitud
    int  0x80
    ret

; -------------------------------------------------------
; __println_int: imprime EAX como entero decimal + newline
;   Entrada : EAX = entero
; -------------------------------------------------------
__println_int:
    call __int_to_str       ; ESI = ptr, ECX = len
    mov  eax, 4
    mov  ebx, 1
    push ecx
    mov  ecx, esi
    pop  edx
    int  0x80
    ; imprimir newline
    mov  eax, 4
    mov  ebx, 1
    mov  ecx, newline
    mov  edx, 1
    int  0x80
    ret


suma:
    pop   eax
    mov  [a], eax
    pop   eax
    mov  [b], eax
    mov  eax, [a]
    push  eax
    mov  eax, [b]
    mov   ebx, eax
    pop   eax
    add   eax, ebx
    mov  [c], eax
    mov  eax, [c]
    ret

_start:
main:
    ; println string 'Inicio del programa'
    mov  eax, 4         ; sys_write
    mov  ebx, 1         ; stdout
    mov  ecx, str_0
    mov  edx, 19
    int  0x80
    ; newline
    mov  eax, 4
    mov  ebx, 1
    mov  ecx, newline
    mov  edx, 1
    int  0x80
    mov  eax, 4
    push  eax
    mov  eax, 3
    push  eax
    call  suma
    mov  [resultado], eax
    ; print string 'Resultado de suma(3,4): '
    mov  eax, 4         ; sys_write
    mov  ebx, 1         ; stdout
    mov  ecx, str_1
    mov  edx, 24
    int  0x80
    mov  eax, [resultado]
    ; println entero (con newline)
    call __println_int
    mov  eax, 10
    mov  [x], eax
    mov  eax, [x]
    push  eax
    mov  eax, 5
    mov   ebx, eax
    pop   eax
    cmp   eax, ebx
    mov   eax, 0
    jg   cmp_t_2651742593552
    jmp   cmp_e_2651742593552
cmp_t_2651742593552:
    mov   eax, 1
cmp_e_2651742593552:
    cmp  eax, 0
    je   else_2651742901584
    ; println string 'x es mayor que 5'
    mov  eax, 4         ; sys_write
    mov  ebx, 1         ; stdout
    mov  ecx, str_2
    mov  edx, 16
    int  0x80
    ; newline
    mov  eax, 4
    mov  ebx, 1
    mov  ecx, newline
    mov  edx, 1
    int  0x80
    jmp  fin_if_2651742901584
else_2651742901584:
    ; println string 'x es menor o igual a 5'
    mov  eax, 4         ; sys_write
    mov  ebx, 1         ; stdout
    mov  ecx, str_3
    mov  edx, 22
    int  0x80
    ; newline
    mov  eax, 4
    mov  ebx, 1
    mov  ecx, newline
    mov  edx, 1
    int  0x80
fin_if_2651742901584:
    mov  eax, 0
    mov  [i], eax
    ; println string 'Conteo while:'
    mov  eax, 4         ; sys_write
    mov  ebx, 1         ; stdout
    mov  ecx, str_4
    mov  edx, 13
    int  0x80
    ; newline
    mov  eax, 4
    mov  ebx, 1
    mov  ecx, newline
    mov  edx, 1
    int  0x80
ini_while_2651742902256:
    mov  eax, [i]
    push  eax
    mov  eax, 3
    mov   ebx, eax
    pop   eax
    cmp   eax, ebx
    mov   eax, 0
    jl   cmp_t_2651742594512
    jmp   cmp_e_2651742594512
cmp_t_2651742594512:
    mov   eax, 1
cmp_e_2651742594512:
    cmp  eax, 0
    je   fin_while_2651742902256
    mov  eax, [i]
    ; println entero (con newline)
    call __println_int
    mov  eax, [i]
    push  eax
    mov  eax, 1
    mov   ebx, eax
    pop   eax
    add   eax, ebx
    mov  [i], eax
    jmp  ini_while_2651742902256
fin_while_2651742902256:
    ; println string 'Conteo for:'
    mov  eax, 4         ; sys_write
    mov  ebx, 1         ; stdout
    mov  ecx, str_5
    mov  edx, 11
    int  0x80
    ; newline
    mov  eax, 4
    mov  ebx, 1
    mov  ecx, newline
    mov  edx, 1
    int  0x80
    mov  eax, 0
    mov  [k], eax
ini_for_2651742902592:
    mov  eax, [k]
    push  eax
    mov  eax, 4
    mov   ebx, eax
    pop   eax
    cmp   eax, ebx
    mov   eax, 0
    jl   cmp_t_2651742968736
    jmp   cmp_e_2651742968736
cmp_t_2651742968736:
    mov   eax, 1
cmp_e_2651742968736:
    cmp  eax, 0
    je   fin_for_2651742902592
    mov  eax, [k]
    ; println entero (con newline)
    call __println_int
    mov  eax, [k]
    push  eax
    mov  eax, 1
    mov   ebx, eax
    pop   eax
    add   eax, ebx
    mov  [k], eax
    jmp  ini_for_2651742902592
fin_for_2651742902592:
    ; println string 'Fin del programa'
    mov  eax, 4         ; sys_write
    mov  ebx, 1         ; stdout
    mov  ecx, str_6
    mov  edx, 16
    int  0x80
    ; newline
    mov  eax, 4
    mov  ebx, 1
    mov  ecx, newline
    mov  edx, 1
    int  0x80
    mov  eax, 42
    push  eax
    ; referencia string str_7
    push  eax
    call  printf
    add   esp, 8
    mov  eax, 0
    ret
    ; salida del programa
    mov  eax, 1
    xor  ebx, ebx
    int  0x80