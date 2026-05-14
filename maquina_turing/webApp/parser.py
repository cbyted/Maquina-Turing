from re import search, findall

# Archivos .mt válidos
valid_machines = {
    "lenguaje-no-regular.mt",
    "palindromo-binario.mt",
    "duplicadora-de-unos.mt",
    "duplicadora-binaria.mt",
    "termina-en-aa.mt",
    "suma-dos-numeros.mt"
}

# Convertir las transiciones a tuplas
def parse_transition(line, dictionary):
    current_state = tuple(search(r"(.*)\s->", line).group(1).split(","))
    transition = tuple(search(r"->\s*(.*)", line).group(1).split(","))
    dictionary[current_state] = transition

# Parsing de los demas datos
def general_parsing(line):
    data = search(r":\s*(.*)", line).group(1).split(",")
    if len(data) > 0:
        return data
    else:
        return None
        
# Crear un diccionario con los datos obtenidos
def parsing_mt_file(selected_file):
    try:
        parsed_file = {}
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
                            parse_transition(line, parsed_file)
                            
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
                    return parsed_file
            except FileNotFoundError:
                print("[!] Error: Archivo no encontrado")
    except Exception as e:
        print(f"[!] Error: {e}")

def show_parsed_file(dictionary):
    print("\n[*] Resultado del diccionario tras el parsing")
    for key in dictionary:
        print(f"{key} : {dictionary[key]}")

def main():
    file_dict = parsing_mt_file("termina-en-aa.mt")
    show_parsed_file(file_dict)

if __name__ == "__main__":
    main()