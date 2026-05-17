from re import search
from machine import TuringMachine

valid_machines = {
    "lenguaje-no-regular.mt",
    "palindromo-binario.mt",
    "duplicadora-de-unos.mt",
    "duplicadora-binaria.mt",
    "termina-en-aa.mt",
    "suma-dos-numeros.mt"
}

def strip_parsing(data):
    data = [item.strip() for item in data]
    return data

def parse_transition(line, dictionary):
    current_state = search(r"(.*)\s->", line).group(1).split(",")
    transition = search(r"->\s*(.*)", line).group(1).split(",")
    
    stripped_current_state = strip_parsing(current_state)
    stripped_transition = strip_parsing(transition)

    dictionary[tuple(stripped_current_state)] = tuple(stripped_transition)

def general_parsing(line):
    data = search(r":\s*(.*)", line).group(1).split(",")
    if len(data) > 0:
        stripped_data = strip_parsing(data)
        return stripped_data
    else:
        return None

def parsing_mt_file(selected_file):
    try:
        parsed_file = {}
        transitions = {}

        in_transitions = False

        if selected_file not in valid_machines:
            raise Exception("Maquina no válida")
        else:
            try:
                filename = "files/machines/" + selected_file
                with open(filename, 'r') as mt:
                    print("[+] Exito: El archivo se cargó correctamente")

                    for line in mt:
                        if in_transitions:
                            parse_transition(line, transitions)    
                        
                        if "Estados" in line:
                            states = general_parsing(line)
                            if states is not None:
                                parsed_file["states"] = states
                            else:
                                raise Exception("No se leyó ningún estado")
                        elif "Alfabeto_entrada" in line:
                            input_alphabet = general_parsing(line)
                            if input_alphabet is not None:
                                parsed_file["input_alphabet"] = input_alphabet
                            else:
                                raise Exception("No se leyó ningún alfabeto")
                        elif "Alfabeto_cinta" in line:
                            tape_alphabet = general_parsing(line)
                            if tape_alphabet is not None:
                                parsed_file["tape_alphabet"] = tape_alphabet
                            else:
                                raise Exception("No se leyó ningún alfabeto cinta")
                        elif "Inicial" in line:
                            initial_state = general_parsing(line)
                            if initial_state is not None:
                                parsed_file["initial_state"] = initial_state
                            else:
                                raise Exception("No se leyó ningún estado inicial")    
                        elif "Finales" in line:
                            final_states = general_parsing(line)
                            if final_states is not None:
                                parsed_file["final_states"] = final_states 
                            else:
                                raise Exception("No se encontraron estados finales")
                        elif "Blanco" in line:
                            blank_sym = general_parsing(line)
                            if blank_sym is not None:
                                parsed_file["blank_symbol"] = blank_sym
                            else:
                                raise Exception("No se encontraron estados finales")
                        elif "Transiciones" in line:
                            in_transitions = True 
                    mt.close()    

                    parsed_file["transitions"] = transitions
                    return parsed_file
            except FileNotFoundError:
                print("[!] Error: Archivo no encontrado")
    except Exception as e:
        print(f"[!] Error: {e}")

def show_parsed_file(dictionary):
    print("\n[*] Resultado del diccionario tras el parsing")
    for key in dictionary:
        if key == "transitions":
            print(f"{key}:")
            for transition in dictionary[key]:
                print(f"{transition} : {dictionary[key][transition]}")
        else:
            print(f"{key} : {dictionary[key]}")

def main():
    file_dict = parsing_mt_file("palindromo-binario.mt")

    mt_simulator = TuringMachine(
        file_dict["states"],
        file_dict["input_alphabet"],
        file_dict["tape_alphabet"],
        file_dict["initial_state"][0],
        file_dict["final_states"][0],
        file_dict["blank_symbol"][0],    
        file_dict["transitions"],
        tape="1001"
    )
    try:
        mt_simulator.show_machine()

        print("\n[*] Running the tape:")
        result = mt_simulator.run()
        if result == True:
            print("Accepted")
        else:
            print("Rejected")

        print("\nFinal result:")
        mt_simulator.display_tape()
    except Exception as e:
        print(f"{e}")

if __name__ == "__main__":
    main()