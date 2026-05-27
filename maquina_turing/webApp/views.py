import re
from django.shortcuts import render, redirect
from django.contrib import messages
from .parser import parsing_mt_file
 
MAX_PASOS = 500

def posicion_a_clave(pos):
    return f"{pos[0]}||{pos[1]}"
 
def clave_a_posicion(clave):
    x, y = clave.split('||')
    return (int(x), int(y))
 
def parse_cadena_entrada(cadena):
    cadena = str(cadena or '').strip()
    if not cadena:
        return ''
    if ',' in cadena or '\n' in cadena or '\r' in cadena:
        filas = [fila.replace(' ', '') for fila in re.split(r'[\r\n,]+', cadena) if fila.strip()]
        return filas
    return cadena

def normalizar_simbolo_entrada(simbolo, blank_symbol, tape_alphabet):
    if simbolo == '0' and blank_symbol != '0' and '0' not in tape_alphabet:
        return blank_symbol
    return simbolo
 
def inicializar_cinta(cadena, simbolo_blanco, tape_alphabet):
    cinta = {}
    cabezal = (0, 0)

    if isinstance(cadena, list):
        for y, fila in enumerate(cadena):
            for x, simbolo in enumerate(fila):
                cinta[(x, y)] = normalizar_simbolo_entrada(simbolo, simbolo_blanco, tape_alphabet)
        if cadena:
            cabezal = (len(cadena[0]) // 2, len(cadena) // 2)
    else:
        for x, simbolo in enumerate(cadena):
            cinta[(x, 0)] = normalizar_simbolo_entrada(simbolo, simbolo_blanco, tape_alphabet)
        cabezal = (0, 0)

    return cinta, cabezal
 
def leer_cinta(cinta, pos, simbolo_blanco):
    return cinta.get(pos, simbolo_blanco)
 
def ejecutar_paso(estado, cinta, cabezal, transiciones, simbolo_blanco):
    simbolo = leer_cinta(cinta, cabezal, simbolo_blanco)
    clave = (estado, simbolo)
    if clave not in transiciones:
        return estado, cinta, cabezal, None, True, 'rechazada'
    nuevo_estado, escribe, direccion = transiciones[clave]
    cinta[cabezal] = escribe
    x, y = cabezal
    if direccion in ('R', 'E'):
        nuevo_cabezal = (x + 1, y)
    elif direccion in ('L', 'W'):
        nuevo_cabezal = (x - 1, y)
    elif direccion in ('U', 'N'):
        nuevo_cabezal = (x, y - 1)
    elif direccion in ('D',):
        nuevo_cabezal = (x, y + 1)
    elif direccion in ('S', '-'):  # Stay
        nuevo_cabezal = (x, y)
    else:
        nuevo_cabezal = (x, y)
    detalle = {
        'estado':    estado,
        'lee':       simbolo,
        'siguiente': nuevo_estado,
        'escribe':   escribe,
        'direccion': direccion,
    }
    return nuevo_estado, cinta, nuevo_cabezal, detalle, False, None

def construir_cinta_visible(cinta, cabezal, simbolo_blanco, ventana=4):
    if cinta:
        xs = [pos[0] for pos in cinta.keys()] + [cabezal[0]]
        ys = [pos[1] for pos in cinta.keys()] + [cabezal[1]]
        min_x = min(xs) - 2
        max_x = max(xs) + 2
        min_y = min(ys) - 2
        max_y = max(ys) + 2
    else:
        min_x = cabezal[0] - ventana
        max_x = cabezal[0] + ventana
        min_y = cabezal[1] - ventana
        max_y = cabezal[1] + ventana
 
    grid = []
    for y in range(min_y, max_y + 1):
        row = []
        for x in range(min_x, max_x + 1):
            row.append({
                'x':          x,
                'y':          y,
                'simbolo':    cinta.get((x, y), simbolo_blanco),
                'es_cabezal': (x, y) == cabezal,
            })
        grid.append(row)
    return grid

def cinta_to_session(cinta):
    resultado = {}
    for posicion, valor in cinta.items():
        resultado[posicion_a_clave(posicion)] = valor
    return resultado

def session_to_cinta(session_cinta):
    resultado = {}
    for clave_str, valor in session_cinta.items():
        resultado[clave_a_posicion(clave_str)] = valor
    return resultado

def session_to_transiciones(session_trans):
    resultado = {}
    for clave_str, valor in session_trans.items():
        estado, simbolo = clave_str.split('||')
        resultado[(estado, simbolo)] = tuple(valor)
    return resultado

def transiciones_to_session(transiciones):
    resultado = {}
    for (estado, simbolo), valor in transiciones.items():
        clave_str = f"{estado}||{simbolo}"
        resultado[clave_str] = list(valor)
    return resultado


def transiciones_to_list(transiciones):
    lista = []
    for (from_state, read_sym), (to_state, write_sym, direction) in transiciones.items():
        lista.append({
            'from_state': from_state,
            'read':       read_sym,
            'to_state':   to_state,
            'write':      write_sym,
            'direction':  direction,
        })
    return sorted(lista, key=lambda x: (x['from_state'], x['read']))

def ejecutar_un_paso(estado, cinta, cabezal, transiciones, blank, paso, historial, finals):
    if estado in finals:
        return estado, cinta, cabezal, paso, historial, True, 'aceptada'

    nuevo_estado, cinta, nuevo_cabezal, detalle, terminado, resultado = ejecutar_paso(
        estado, cinta, cabezal, transiciones, blank
    )
    paso += 1
    if detalle:
        detalle['numero'] = paso
        historial.append(detalle)
    if not terminado and nuevo_estado in finals:
        terminado = True
        resultado = 'aceptada'
    if not terminado and paso >= MAX_PASOS:
        terminado = True
        resultado = 'limite'
    return nuevo_estado, cinta, nuevo_cabezal, paso, historial, terminado, resultado

def cargar(request):
    context = {
        'maquina_cargada': request.session.get('maquina_nombre'),
        'mt_data': None,
    }
 
    if request.method == 'POST':
        maquina = request.POST.get('maquina')
        if not maquina:
            messages.error(request, 'Debes seleccionar una máquina.')
            return render(request, 'cargar.html', context)
 
        parsed = parsing_mt_file(maquina)
        if parsed is None:
            messages.error(request, f'No se pudo cargar "{maquina}". Verifica el archivo .mt.')
            return render(request, 'cargar.html', context)
 
        request.session['maquina_nombre']   = maquina
        request.session['mt_states']        = parsed['states']
        request.session['mt_input_alpha']   = parsed['input_alphabet']
        request.session['mt_tape_alpha']    = parsed['tape_alphabet']
        request.session['mt_initial']       = parsed['initial_state'][0] if isinstance(parsed['initial_state'], list) else parsed['initial_state']
        request.session['mt_finals']        = parsed['final_states']
        request.session['mt_blank']         = parsed['blank_symbol'][0] if isinstance(parsed['blank_symbol'], list) else parsed['blank_symbol']
        request.session['mt_transiciones']  = transiciones_to_session(parsed['transitions'])
        request.session.pop('sim_estado',   None)
        request.session.pop('sim_cinta',    None)
        request.session.pop('sim_cabezal',  None)
        request.session.pop('sim_paso',     None)
        request.session.pop('sim_historial',None)
        request.session.pop('sim_terminado',None)
        request.session.pop('sim_resultado',None)
        request.session.pop('sim_cadena',   None)
 
        messages.success(request, f'Máquina "{maquina}" cargada correctamente.')
        context['maquina_cargada'] = maquina
 
        transiciones = parsed['transitions']
        context['mt_data'] = {
            'states':        parsed['states'],
            'input_alphabet': parsed['input_alphabet'],
            'tape_alphabet': parsed['tape_alphabet'],
            'initial_state': parsed['initial_state'][0] if isinstance(parsed['initial_state'], list) else parsed['initial_state'],
            'final_states':  parsed['final_states'],
            'blank_symbol':  parsed['blank_symbol'][0] if isinstance(parsed['blank_symbol'], list) else parsed['blank_symbol'],
            'transitions':   transiciones_to_list(transiciones),
        }
 
    elif request.session.get('maquina_nombre'):
        # GET con máquina ya cargada: mostrar la 7-tupla
        trans_raw = request.session.get('mt_transiciones', {})
        transiciones = session_to_transiciones(trans_raw)
        context['mt_data'] = {
            'states':        request.session.get('mt_states', []),
            'input_alphabet': request.session.get('mt_input_alpha', []),
            'tape_alphabet': request.session.get('mt_tape_alpha', []),
            'initial_state': request.session.get('mt_initial', ''),
            'final_states':  request.session.get('mt_finals', []),
            'blank_symbol':  request.session.get('mt_blank', 'B'),
            'transitions':   transiciones_to_list(transiciones),
        }
 
    return render(request, 'cargar.html', context)

def simular(request):
    maquina_nombre = request.session.get('maquina_nombre')

    context = {
        'maquina_nombre':  maquina_nombre,
        'simulacion_activa': False,
        'terminado':       False,
        'resultado':       None,
        'cinta_visible':   [],
        'historial':       [],
        'estado_actual':   None,
        'cabezal':         0,
        'paso_actual':     0,
        'cadena_actual':   '',
        'max_pasos':       MAX_PASOS,
    }
 
    if not maquina_nombre:
        return render(request, 'simular.html', context)
 
    blank          = request.session.get('mt_blank', 'B')
    finals         = request.session.get('mt_finals', [])
    trans_raw      = request.session.get('mt_transiciones', {})
    transiciones   = session_to_transiciones(trans_raw)
 
    if request.method == 'POST':
        accion = request.POST.get('accion')
 
        if accion == 'iniciar':
            cadena = request.POST.get('cadena', '').strip()
            estado_inicial = request.session.get('mt_initial', 'q0')
            cadena_parsed = parse_cadena_entrada(cadena)
            cinta, cabezal = inicializar_cinta(cadena_parsed, blank, request.session.get('mt_tape_alpha', []))
 
            request.session['sim_cadena']    = cadena
            request.session['sim_estado']    = estado_inicial
            request.session['sim_cinta']     = cinta_to_session(cinta)
            request.session['sim_cabezal']   = [cabezal[0], cabezal[1]]
            request.session['sim_paso']      = 0
            request.session['sim_historial'] = []
            request.session['sim_terminado'] = False
            request.session['sim_resultado'] = None
 
            estado   = request.session['sim_estado']
            cinta    = session_to_cinta(request.session['sim_cinta'])
            cabezal  = tuple(request.session['sim_cabezal'])
            paso     = request.session['sim_paso']
            historial = request.session['sim_historial']
 
            estado, cinta, cabezal, paso, historial, terminado, resultado = ejecutar_un_paso(
                estado, cinta, cabezal, transiciones, blank, paso, historial, finals
            )
 
            request.session['sim_estado']    = estado
            request.session['sim_cinta']     = cinta_to_session(cinta)
            request.session['sim_cabezal']   = [cabezal[0], cabezal[1]]
            request.session['sim_paso']      = paso
            request.session['sim_historial'] = historial
            request.session['sim_terminado'] = terminado
            request.session['sim_resultado'] = resultado
 
            if terminado:
                _guardar_en_historial(request, maquina_nombre,
                                      request.session['sim_cadena'], resultado, paso)
 
        elif accion == 'completo':
            if not request.session.get('sim_terminado', True):
                estado   = request.session['sim_estado']
                cinta    = session_to_cinta(request.session.get('sim_cinta', {}))
                cabezal  = tuple(request.session.get('sim_cabezal', [0, 0]))
                paso     = request.session['sim_paso']
                historial = request.session['sim_historial']
                terminado = False
                resultado = None
 
                while not terminado:
                    estado, cinta, cabezal, paso, historial, terminado, resultado = ejecutar_un_paso(
                        estado, cinta, cabezal, transiciones, blank, paso, historial, finals
                    )
 
                request.session['sim_estado']    = estado
                request.session['sim_cinta']     = cinta_to_session(cinta)
                request.session['sim_cabezal']   = [cabezal[0], cabezal[1]]
                request.session['sim_paso']      = paso
                request.session['sim_historial'] = historial
                request.session['sim_terminado'] = terminado
                request.session['sim_resultado'] = resultado
 
                _guardar_en_historial(request, maquina_nombre,
                                      request.session['sim_cadena'], resultado, paso)
        elif accion == 'paso':
            if request.session.get('sim_estado') is not None and not request.session.get('sim_terminado', True):
                estado   = request.session['sim_estado']
                cinta    = session_to_cinta(request.session.get('sim_cinta', {}))
                cabezal  = tuple(request.session.get('sim_cabezal', [0, 0]))
                paso     = request.session['sim_paso']
                historial = request.session['sim_historial']
 
                estado, cinta, cabezal, paso, historial, terminado, resultado = ejecutar_un_paso(
                    estado, cinta, cabezal, transiciones, blank, paso, historial, finals
                )
 
                request.session['sim_estado']    = estado
                request.session['sim_cinta']     = cinta_to_session(cinta)
                request.session['sim_cabezal']   = [cabezal[0], cabezal[1]]
                request.session['sim_paso']      = paso
                request.session['sim_historial'] = historial
                request.session['sim_terminado'] = terminado
                request.session['sim_resultado'] = resultado
 
                if terminado:
                    _guardar_en_historial(request, maquina_nombre,
                                          request.session['sim_cadena'], resultado, paso)
 
        elif accion == 'reiniciar':
            for key in ['sim_estado', 'sim_cinta', 'sim_cabezal',
                        'sim_paso', 'sim_historial', 'sim_terminado',
                        'sim_resultado', 'sim_cadena']:
                request.session.pop(key, None)
 
        return redirect('simular')

    sim_activa = 'sim_estado' in request.session
 
    if sim_activa:
        cinta    = session_to_cinta(request.session.get('sim_cinta', {}))
        cabezal  = tuple(request.session.get('sim_cabezal', [0, 0]))
        historial = request.session.get('sim_historial', [])
 
        context.update({
            'simulacion_activa': True,
            'terminado':         request.session.get('sim_terminado', False),
            'resultado':         request.session.get('sim_resultado'),
            'estado_actual':     request.session.get('sim_estado'),
            'cabezal':           cabezal,
            'paso_actual':       request.session.get('sim_paso', 0),
            'cadena_actual':     request.session.get('sim_cadena', ''),
            'cinta_visible':     construir_cinta_visible(cinta, cabezal, blank),
            'historial':         list(reversed(historial)),
        })
 
    return render(request, 'simular.html', context)

def historial(request):
    ejecuciones = request.session.get('historial_ejecuciones', [])
    return render(request, 'historial.html', {'ejecuciones': ejecuciones})

def _guardar_en_historial(request, maquina, cadena, resultado, pasos):

    historial = request.session.get('historial_ejecuciones', [])
    historial.append({
        'maquina':   maquina,
        'cadena':    cadena if cadena else 'ε',
        'resultado': resultado,
        'pasos':     pasos,
    })
    request.session['historial_ejecuciones'] = historial