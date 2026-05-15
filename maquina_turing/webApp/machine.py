
class Tape:
    blank = ""

class TuringMachine:
    def __init__(self, states, input_alphabet, tape_alphabet, initial_state, final_states, blank_sym, transitions): 
        self.states = states
        self.input_alphabet = input_alphabet
        self.tape_alphabet = tape_alphabet
        self.initial_state = initial_state
        self.final_states = final_states
        self.blank_sym = blank_sym
        self.transitions = transitions
        self.head = 0
        self.current = initial_state
    
    # debugging
    def show_machine(self):
        print("\n====== TURING MACHINE ======")
        print(f"[*] Estados: {self.states}")
        print(f"[*] Alfabeto: {self.input_alphabet}")
        print(f"[*] Cinta: {self.tape_alphabet}")
        print(f"[*] Estado inicial: {self.initial_state}")
        print(f"[*] Estados finales: {self.final_states}")
        print(f"[*] Simbolos vacios: {self.blank_sym}")
        print(f"[*] Transiciones: {self.transitions}")

    def step(self):
        if self.head < len(self.tape_alphabet):
            symbol = self.tape_alphabet[self.head] 
        else:
            symbol = ''

        if (self.current, symbol) in self.transitions:
            new_state, write_sym, move = self.transitions[(self.current, symbol)]
            print(f"{new_state} {write_sym} {move}")
            if (self.head < len(self.tape_alphabet)):
                self.tape_alphabet[self.head] = write_sym

    def run(self):
        return