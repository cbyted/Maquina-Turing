
class TuringMachine:
    def __init__(self, states, input_alphabet, tape_alphabet, initial_state, final_state, blank_sym, transitions, tape=""): 
        self.states = states
        self.input_alphabet = input_alphabet
        self.tape_alphabet = tape_alphabet
        self.initial_state = initial_state
        self.final_state = final_state
        self.blank_sym = blank_sym
        self.transitions = transitions
        self.head = 0
        self.current = initial_state
        self.tape = list(tape) + [blank_sym]
    
    # debugging
    def show_machine(self):
        print("\n====== TURING MACHINE ======")
        print(f"[*] Estados: {self.states}")
        print(f"[*] Alfabeto: {self.input_alphabet}")
        print(f"[*] Cinta: {self.tape_alphabet}")
        print(f"[*] Estado inicial: {self.initial_state}")
        print(f"[*] Estados aceptación: {self.final_state}")
        print(f"[*] Blank: {self.blank_sym}")
        print(f"[*] Transiciones: {self.transitions}")
        print(f"[*] Head: {self.head}")
        print(f"[*] Current state: {self.current}")

    def step(self):
        if self.head < len(self.tape_alphabet):
            symbol = self.tape[self.head] 
        else:
            symbol = ' '

        if (self.current, symbol) in self.transitions:
            new_state, write_sym, move = self.transitions[(self.current, symbol)]

            print(f"Current transition: {(self.current, symbol)} : {(new_state, write_sym, move)}\n")

            if (self.head < len(self.tape_alphabet)):
                self.tape[self.head] = write_sym   
            else:
                self.tape.append(write_sym)

            if move == 'R':
                self.head +=1
            elif move == 'L':
                self.head -= 1
                if self.head < 0:
                    self.tape.insert(0, ' ')

            self.current = new_state
        else:
            self.current = "REJECT"

    def display_tape(self):
        tape_view = ''.join(self.tape).rstrip()
        print(f"\nTape: {tape_view}")
        print(f"Head: {' ' * self.head + '^'}")
        print(f"State: {self.current}")

    def run(self):
        while self.current != self.final_state and self.current != "REJECT":
            self.display_tape()
            self.step()
        return self.current == self.final_state
