from django.shortcuts import render, redirect
from django.contrib import messages
from .parser import parsing_mt_file
 
 
MAX_PASOS = 500

def inicializar_cinta(cadena, simbolo_blanco):
    """
    Crea la cinta como diccionario {posición_int: símbolo}.
    La cadena de entrada se coloca desde la posición 0.
    """
    cinta = {}
    for i, simbolo in enumerate(cadena):
        cinta[i] = simbolo
    return cinta
 
 
def leer_cinta(cinta, pos, simbolo_blanco):
    """Lee el símbolo en la posición dada; devuelve blanco si no existe."""
    return cinta.get(pos, simbolo_blanco)
 
 
def ejecutar_paso(estado, cinta, cabezal, transiciones, simbolo_blanco):
    """
    Ejecuta un único paso de la MT.
    Devuelve (nuevo_estado, cinta, nuevo_cabezal, detalle_paso, terminado, resultado)
    donde resultado puede ser 'aceptada', 'rechazada' o None.
    """
    simbolo = leer_cinta(cinta, cabezal, simbolo_blanco)
    clave = (estado, simbolo)
 
    if clave not in transiciones:
        return estado, cinta, cabezal, None, True, 'rechazada'
 
    nuevo_estado, escribe, direccion = transiciones[clave]
 
    cinta[cabezal] = escribe
 
    if direccion == 'R':
        nuevo_cabezal = cabezal + 1
    elif direccion == 'L':
        nuevo_cabezal = cabezal - 1
    else:
        nuevo_cabezal = cabezal
 
    detalle = {
        'estado':    estado,
        'lee':       simbolo,
        'siguiente': nuevo_estado,
        'escribe':   escribe,
        'direccion': direccion,
    }
 
    return nuevo_estado, cinta, nuevo_cabezal, detalle, False, None