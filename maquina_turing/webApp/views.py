import re
from django.shortcuts import render, redirect
from django.contrib import messages

from .parser import parsing_mt_file
from .machine import TuringMachine
from .machine import cinta_to_session
from .machine import session_to_cinta
from .machine import session_to_transiciones
from .machine import transiciones_to_session
from .machine import transiciones_to_list

MAX_PASOS = 13000

def _guardar_en_historial(request, maquina, cadena, resultado, pasos):
    historial = request.session.get('historial_ejecuciones', [])
    historial.append({
        'maquina':   maquina,
        'cadena':    cadena if cadena else 'ε',
        'resultado': resultado,
        'pasos':     pasos,
    })
    request.session['historial_ejecuciones'] = historial

def historial(request):
    ejecuciones = request.session.get('historial_ejecuciones', [])
    return render(request, 'historial.html', {'ejecuciones': ejecuciones})

def normalizar_valor(valor):
    if isinstance(valor, list):
        return valor[0]
    return valor

def cargar(request):      # GET con máquina ya cargada: mostrar la 7-tupla
    context = {
        'maquina_cargada': request.session.get('maquina_nombre'),
        'mt_data': None,
    }
 
    if request.method == 'POST':
        maquina = request.POST.get('maquina')
        if not maquina:
            messages.error(request, 'Debes seleccionar una máquina.')
            return render(request, 'cargar.html', context)

        # Bandera para detectar el .mt de langston y aplicar los estilos correspondientes
        is_langtons_ant = False

        if maquina == "langtons-ant.mt":
            is_langtons_ant = True

        parsed = parsing_mt_file(maquina)
        if parsed is None:
            messages.error(request, f'No se pudo cargar "{maquina}". Verifica el archivo .mt.')
            return render(request, 'cargar.html', context)
 
        request.session['is_langtons_ant']  = is_langtons_ant 
        request.session['maquina_nombre']   = maquina
        request.session['mt_states']        = parsed['states']
        request.session['mt_input_alpha']   = parsed['input_alphabet']
        request.session['mt_tape_alpha']    = parsed['tape_alphabet']
        request.session['mt_initial']       = normalizar_valor(parsed['initial_state'])
        request.session['mt_finals']        = parsed['final_states']
        request.session['mt_blank']         = normalizar_valor(parsed['blank_symbol'])
        request.session['mt_transiciones']  = transiciones_to_session(parsed['transitions'])
        
        request.session.pop('tm', None)

        messages.success(request, f'Máquina "{maquina}" cargada correctamente.')
        context['maquina_cargada'] = maquina
 
        transiciones = parsed['transitions']
        context['mt_data'] = {
            'states':         parsed['states'],
            'input_alphabet': parsed['input_alphabet'],
            'tape_alphabet':  parsed['tape_alphabet'],
            'initial_state':  parsed['initial_state'][0] if isinstance(parsed['initial_state'], list) else parsed['initial_state'],
            'final_states':   parsed['final_states'],
            'blank_symbol':   parsed['blank_symbol'][0] if isinstance(parsed['blank_symbol'], list) else parsed['blank_symbol'],
            'transitions':    transiciones_to_list(transiciones),
        }
 
    elif request.session.get('maquina_nombre'):
  
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

def init_context(maquina_nombre):
    context = {
        'is_langtons_ant': False,
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
    return context

def new_machine_from_session(request, maquina, cadena, transiciones):    
    tm = TuringMachine(
        nombre_mt=maquina,
        estados=request.session.get('mt_states', []),
        alfabeto_entrada=request.session.get('mt_input_alpha', []),
        alfabeto_cinta=request.session.get('mt_tape_alpha', []),
        estado_inicial=request.session.get('mt_initial', 'q0'),
        estados_finales=request.session.get('mt_finals', []),
        simbolo_vacio=request.session.get('mt_blank', 'B'),
        transiciones=transiciones,
        cinta=cadena,  
    )
    return tm

def simular(request):
    maquina_nombre = request.session.get('maquina_nombre')
    context = init_context(maquina_nombre)
    
    # Para detectar cuando se usa langston ant
    context['is_langtons_ant'] = request.session.get('is_langtons_ant', False)

    if not maquina_nombre:
        return render(request, 'simular.html', context)
 
    trans_raw      = request.session.get('mt_transiciones', {})
    transiciones   = session_to_transiciones(trans_raw)
    terminado = False

    if request.method == 'POST':
        accion = request.POST.get('accion')
 
        if accion == 'iniciar':
            cadena = request.POST.get('cadena', '').strip()

            tm = new_machine_from_session(request, maquina_nombre, cadena, transiciones)
            tm.step()

            request.session['tm'] = tm.to_session()
            terminado = tm.terminado

            if terminado:
                _guardar_en_historial(
                    request, 
                    tm.nombre_mt,
                    tm.cadena,
                    tm.resultado, 
                    tm.pasos
                )
 
        elif accion == 'completo':
            if not terminado:
 
                tm = TuringMachine.get_machine_from_session(request.session['tm'])
                tm.run()

                request.session['tm'] = tm.to_session()
                terminado = tm.terminado 

                _guardar_en_historial(
                    request, 
                    tm.nombre_mt,
                    tm.cadena,
                    tm.resultado,
                    tm.pasos
                )

        elif accion == 'paso':
            tm = TuringMachine.get_machine_from_session(request.session['tm'])

            if tm.estado_actual is not None and not tm.terminado:

                tm.step()
                request.session['tm'] = tm.to_session()
                terminado = tm.terminado

                if terminado:
                    _guardar_en_historial(
                        request,
                        tm.nombre_mt,
                        tm.cadena, 
                        tm.resultado, 
                        tm.pasos
                    )
 
        elif accion == 'reiniciar':
            request.session.pop('tm', None)

        return redirect('simular')

    sim_activa = 'tm' in request.session
    if sim_activa:

        tm = TuringMachine.get_machine_from_session(request.session['tm'])

        context.update({
            'simulacion_activa': True,
            'terminado': tm.terminado,
            'resultado': tm.resultado,
            'estado_actual': tm.estado_actual,
            'cabezal': tm.cabezal,
            'paso_actual': tm.pasos,
            'cadena_actual': tm.cadena,
            'cinta_visible': tm.display_cinta(),
            'historial': list(reversed(tm.historial)),
        })
 
    return render(request, 'simular.html', context)