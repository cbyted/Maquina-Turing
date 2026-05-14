
"""
Maquina de turing

Uso:
- Guardar la información sobre la maquina turing especificada en los archivos .mt
"""
class TurinMachine:
    def __init__(self, states, input_alphabet, tape_alphabet, initial_state, final_states, blank_sym, transitions): 
        self.states = states
        self.input_alphabet = input_alphabet
        self.tape_alphabet = tape_alphabet
        self.initial_state = initial_state
        self.final_states = final_states
        self.blank_sym = blank_sym
        self.transitions = transitions
    
    def detect_steps(self):
        return

    def simulate(self):
        return