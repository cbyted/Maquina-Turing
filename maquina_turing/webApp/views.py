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

def construir_cinta_visible(cinta, cabezal, simbolo_blanco, ventana=6):
    if cinta:
        min_pos = min(min(cinta.keys()), cabezal) - 2
        max_pos = max(max(cinta.keys()), cabezal) + 2
    else:
        min_pos = cabezal - ventana
        max_pos = cabezal + ventana
 
    min_pos = min(min_pos, cabezal - ventana)
    max_pos = max(max_pos, cabezal + ventana)
 
    celdas = []
    for pos in range(min_pos, max_pos + 1):
        celdas.append({
            'posicion':   pos,
            'simbolo':    cinta.get(pos, simbolo_blanco),
            'es_cabezal': pos == cabezal,
        })
    return celdas

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
 
        # Guardar en sesión
        request.session['maquina_nombre']   = maquina
        request.session['mt_states']        = parsed['states']
        request.session['mt_input_alpha']   = parsed['input_alphabet']
        request.session['mt_tape_alpha']    = parsed['tape_alphabet']
        request.session['mt_initial']       = parsed['initial_state']
        request.session['mt_finals']        = parsed['final_states']
        request.session['mt_blank']         = parsed['blank_symbol']
        request.session['mt_transiciones']  = transiciones_to_session(
            {k: v for k, v in parsed.items() if isinstance(k, tuple)}
        )
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
 
        transiciones = {k: v for k, v in parsed.items() if isinstance(k, tuple)}
        context['mt_data'] = {
            'states':        parsed['states'],
            'input_alphabet': parsed['input_alphabet'],
            'tape_alphabet': parsed['tape_alphabet'],
            'initial_state': parsed['initial_state'],
            'final_states':  parsed['final_states'],
            'blank_symbol':  parsed['blank_symbol'],
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
 
            cinta = inicializar_cinta(cadena, blank)
 
            request.session['sim_cadena']    = cadena
            request.session['sim_estado']    = estado_inicial
            request.session['sim_cinta']     = {str(k): v for k, v in cinta.items()}
            request.session['sim_cabezal']   = 0
            request.session['sim_paso']      = 0
            request.session['sim_historial'] = []
            request.session['sim_terminado'] = False
            request.session['sim_resultado'] = None
 
            if not request.session.get('sim_terminado', True):
                estado   = request.session['sim_estado']
                cinta    = {int(k): v for k, v in request.session['sim_cinta'].items()}
                cabezal  = request.session['sim_cabezal']
                paso     = request.session['sim_paso']
                historial = request.session['sim_historial']
 
                nuevo_estado, cinta, nuevo_cabezal, detalle, terminado, resultado = \
                    ejecutar_paso(estado, cinta, cabezal, transiciones, blank)
 
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
 
                request.session['sim_estado']    = nuevo_estado
                request.session['sim_cinta']     = {str(k): v for k, v in cinta.items()}
                request.session['sim_cabezal']   = nuevo_cabezal
                request.session['sim_paso']      = paso
                request.session['sim_historial'] = historial
                request.session['sim_terminado'] = terminado
                request.session['sim_resultado'] = resultado
 
                # Guardar en historial global de la sesión si terminó
                if terminado:
                    _guardar_en_historial(request, maquina_nombre,
                                          request.session['sim_cadena'], resultado, paso)
 
        elif accion == 'completo':
            if not request.session.get('sim_terminado', True):
                estado   = request.session['sim_estado']
                cinta    = {int(k): v for k, v in request.session['sim_cinta'].items()}
                cabezal  = request.session['sim_cabezal']
                paso     = request.session['sim_paso']
                historial = request.session['sim_historial']
                terminado = False
                resultado = None
 
                while not terminado:
                    nuevo_estado, cinta, cabezal, detalle, terminado, resultado = \
                        ejecutar_paso(estado, cinta, cabezal, transiciones, blank)
 
                    paso += 1
                    if detalle:
                        detalle['numero'] = paso
                        historial.append(detalle)
 
                    estado = nuevo_estado
 
                    if not terminado and estado in finals:
                        terminado = True
                        resultado = 'aceptada'
 
                    if not terminado and paso >= MAX_PASOS:
                        terminado = True
                        resultado = 'limite'
 
                request.session['sim_estado']    = estado
                request.session['sim_cinta']     = {str(k): v for k, v in cinta.items()}
                request.session['sim_cabezal']   = cabezal
                request.session['sim_paso']      = paso
                request.session['sim_historial'] = historial
                request.session['sim_terminado'] = terminado
                request.session['sim_resultado'] = resultado
 
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
        cinta    = {int(k): v for k, v in request.session.get('sim_cinta', {}).items()}
        cabezal  = request.session.get('sim_cabezal', 0)
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