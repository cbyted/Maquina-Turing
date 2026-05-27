class TuringMachine:
    def __init__(
        self,
        states,
        input_alphabet,
        tape_alphabet,
        initial_state,
        final_state,
        blank_sym,
        transitions,
        tape=None,
    ):
        self.states = states
        self.input_alphabet = input_alphabet
        self.tape_alphabet = tape_alphabet
        self.initial_state = initial_state
        self.final_states = final_state
        self.blank_sym = blank_sym
        self.transitions = transitions
        self.current = initial_state
        self.head = (0, 0)
        self.tape = {}
        if tape is not None:
            for x, symbol in enumerate(tape):
                self.tape[(x, 0)] = symbol

    def show_machine(self):
        print("\n====== TURING MACHINE ======")
        print(f"[*] Estados: {self.states}")
        print(f"[*] Alfabeto: {self.input_alphabet}")
        print(f"[*] Cinta: {self.tape_alphabet}")
        print(f"[*] Estado inicial: {self.initial_state}")
        print(f"[*] Estados aceptación: {self.final_states}")
        print(f"[*] Blank: {self.blank_sym}")
        print(f"[*] Transiciones: {self.transitions}")
        print(f"[*] Cabezal: {self.head}")

    def leer_cinta(self):
        return self.tape.get(self.head, self.blank_sym)

    def mover_cabezal(self, move):
        x, y = self.head
        if move in ('R', 'E'):
            self.head = (x + 1, y)
        elif move in ('L', 'W'):
            self.head = (x - 1, y)
        elif move in ('U', 'N'):
            self.head = (x, y - 1)
        elif move in ('D',):
            self.head = (x, y + 1)
        elif move in ('S', '-'):
            self.head = (x, y)

    def step(self):
        symbol = self.leer_cinta()
        key = (self.current, symbol)
        if key not in self.transitions:
            raise Exception(f"No existe transición para {key}")
        new_state, write_sym, move = self.transitions[key]
        self.tape[self.head] = write_sym
        self.current = new_state
        self.mover_cabezal(move)

    def run(self, max_steps=1000):
        steps = 0
        while self.current not in self.final_states and steps < max_steps:
            self.step()
            steps += 1
        return self.current in self.final_states

    def display_tape(self, ventana=4):
        if self.tape:
            xs = [pos[0] for pos in self.tape.keys()] + [self.head[0]]
            ys = [pos[1] for pos in self.tape.keys()] + [self.head[1]]
            min_x, max_x = min(xs) - 2, max(xs) + 2
            min_y, max_y = min(ys) - 2, max(ys) + 2
        else:
            min_x, max_x = self.head[0] - ventana, self.head[0] + ventana
            min_y, max_y = self.head[1] - ventana, self.head[1] + ventana

        for y in range(min_y, max_y + 1):
            row = []
            for x in range(min_x, max_x + 1):
                symbol = self.tape.get((x, y), self.blank_sym)
                marker = '>' if (x, y) == self.head else ' '
                row.append(f"{marker}{symbol}")
            print(' '.join(row))