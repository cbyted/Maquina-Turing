from django.shortcuts import render, redirect
from django.contrib import messages
from .parser import parsing_mt_file
 
 
MAX_PASOS = 500

def inicializar_cinta(cadena, simbolo_blanco):
    cinta = {}
    for i, simbolo in enumerate(cadena):
        cinta[i] = simbolo
    return cinta
 
def leer_cinta(cinta, pos, simbolo_blanco):
    return cinta.get(pos, simbolo_blanco)
 
 
def ejecutar_paso(estado, cinta, cabezal, transiciones, simbolo_blanco):
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