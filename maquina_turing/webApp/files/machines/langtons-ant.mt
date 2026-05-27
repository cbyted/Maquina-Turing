Estados: qN,qE,qS,qW,qf
Alfabeto_entrada: B
Alfabeto_cinta: B,1
Inicial: qN
Finales: qf
Blanco: B
Transiciones:
qN,B -> qE,1,R
qN,1 -> qW,B,L
qE,B -> qS,1,D
qE,1 -> qN,B,U
qS,B -> qW,1,L
qS,1 -> qE,B,R
qW,B -> qN,1,U
qW,1 -> qS,B,D