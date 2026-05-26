#==================================#
# AUXILIARES PARA MANEJO DE DJANGO #
#==================================#

def posicion_a_clave(pos):
    return f"{pos[0]}||{pos[1]}"

def clave_a_posicion(clave):
    x, y = clave.split('||')
    return (int(x), int(y))

def posicion_a_clave(pos):
    return f"{pos[0]}||{pos[1]}"

def clave_a_posicion(clave):
    x, y = clave.split('||')
    return (int(x), int(y))

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


#==============================#
# CLASE PRINCIPAL DEL PROGRAMA #
#==============================#

class TuringMachine:
    def __init__(
        self,
        nombre_mt,
        estados,
        alfabeto_entrada,
        alfabeto_cinta,
        estado_inicial,
        estados_finales,
        simbolo_vacio,
        transiciones,
        cinta=None,
    ):
        self.nombre_mt = nombre_mt
        self.estados = estados
        self.alfabeto_entrada = alfabeto_entrada
        self.alfabeto_cinta = alfabeto_cinta
        self.estado_inicial = estado_inicial
        self.estados_finales = estados_finales
        self.simbolo_vacio = simbolo_vacio
        self.transiciones = transiciones
        self.estado_actual = estado_inicial
        self.cabezal = (0, 0)

        self.pasos = 0
        self.max_pasos = 500
        self.historial = []

        self.resultado = '' # Por defecto
        self.terminado = False

        self.cadena = cinta or ''
        self.cinta = {}
        if cinta is not None:
            for x, symbol in enumerate(cinta):
                self.cinta[(x, 0)] = symbol
    
    # Reiniciar la maquina
    def reset(self):
        self.estado_actual = self.estado_inicial
        self.cabezal = (0, 0)
        self.pasos = 0
        self.historial = []
        self.terminado = False
        self.resultado = ''
        self.cinta = {}
        for x, symbol in enumerate(self.cadena):
            self.cinta[(x, 0)] = symbol
        self.cadena = None

    # Cinvertir campso de la maquina a un diccionario
    def to_session(self):
        return {
            'nombre_mt': self.nombre_mt,
            'estados': self.estados,
            'alfabeto_entrada': self.alfabeto_entrada,
            'alfabeto_cinta': self.alfabeto_cinta,
            'estado_inicial': self.estado_inicial,
            'estados_finales': self.estados_finales,
            'simbolo_vacio': self.simbolo_vacio,
            'transiciones': transiciones_to_session(self.transiciones),
            'estado_actual': self.estado_actual,
            'cinta': cinta_to_session(self.cinta),
            'cabezal': list(self.cabezal),
            'pasos': self.pasos,
            'historial': self.historial,
            'terminado': self.terminado,
            'resultado': self.resultado,
            'cadena': self.cadena,
        }

    # La maquina ya existe
    @classmethod
    def get_machine_from_session(cls, data):
        tm = cls(
            nombre_mt=data['nombre_mt'],
            estados=data['estados'],
            alfabeto_entrada=data['alfabeto_entrada'],
            alfabeto_cinta=data['alfabeto_cinta'],
            estado_inicial=data['estado_inicial'],
            estados_finales=data['estados_finales'],
            simbolo_vacio=data['simbolo_vacio'],
            transiciones=session_to_transiciones(data['transiciones']),
            cinta=data['cadena'],
        )

        tm.estado_actual = data['estado_actual']
        tm.cinta = session_to_cinta(data['cinta'])
        tm.cabezal = tuple(data['cabezal'])
        tm.pasos = data['pasos']
        tm.historial = data['historial']
        tm.terminado = data['terminado']
        tm.resultado = data['resultado']
        return tm

    #===================================#
    # FUNCIONAMIENTO BASE DE LA MAQUINA #
    #===================================#

    # Leer un simbolo de la cinta
    def leer_cinta(self):
        return self.cinta.get(self.cabezal, self.simbolo_vacio)

    # Mostrar la cinta
    def display_cinta(self, ventana=4):
        if self.cinta:
            xs = [pos[0] for pos in self.cinta.keys()] + [self.cabezal[0]]
            ys = [pos[1] for pos in self.cinta.keys()] + [self.cabezal[1]]
            min_x, max_x = min(xs) - 2, max(xs) + 2
            min_y, max_y = min(ys) - 2, max(ys) + 2
        else:
            min_x, max_x = self.cabezal[0] - ventana, self.cabezal[0] + ventana
            min_y, max_y = self.cabezal[1] - ventana, self.cabezal[1] + ventana

        grid = []
        for y in range(min_y, max_y + 1):
            row = []
            for x in range(min_x, max_x + 1):
                row.append({
                    'x':          x,
                    'y':          y,
                    'simbolo':    self.cinta.get((x, y), self.simbolo_vacio),
                    'es_cabezal': (x, y) == self.cabezal,
                })
            grid.append(row)
        return grid

    def step(self):
        simbolo = self.leer_cinta()
        clave = (self.estado_actual, simbolo)

        if clave not in self.transiciones:
            self.terminado = True
            self.resultado = 'rechazada'
            return
        
        nuevo_estado, escribe, direccion = self.transiciones[clave]

        x, y = self.cabezal
        if direccion in ('R', 'E'):
            nuevo_cabezal = (x + 1, y)
        elif direccion in ('L', 'W'):
            nuevo_cabezal = (x - 1, y)
        elif direccion in ('U', 'N'):
            nuevo_cabezal = (x, y - 1)
        elif direccion in ('D', 'S'):
            nuevo_cabezal = (x, y + 1)
        else:
            self.terminado = True
            self.resultado = 'rechazada'
            return

        detalle = {
            'numero': self.pasos + 1,
            'estado': self.estado_actual,
            'lee': simbolo,
            'siguiente': nuevo_estado,
            'escribe': escribe,
            'direccion': direccion,
        }

        self.cinta[self.cabezal] = escribe
        self.cabezal = nuevo_cabezal
        self.estado_actual = nuevo_estado
        self.pasos += 1
        self.historial.append(detalle)

        if not self.terminado and nuevo_estado in self.estados_finales:
            self.resultado = 'aceptada'
            self.terminado = True
        elif not self.terminado and self.pasos >= self.max_pasos:
            self.terminado = True
            self.resultado = 'limite'

        
    def run(self):
        while not self.terminado:
            self.step()


    #==========================#  
    # HISTORIAL DE EJECUCIONES #
    #==========================#

    # Devolver datos para guarar en el historial de ejecuciones completadas
    def get_resumen_ejecucion(self):
        if self.terminado:
            resultado_final = {
                'maquina': self.nombre_mt,
                'cadena': self.cadena if self.cadena else 'ε',
                'resultado': self.resultado,
                'pasos': self.pasos
            }
            return resultado_final
        else:
            print("[!] La simulación aún no ha terminado")
            return None 
    
    
    