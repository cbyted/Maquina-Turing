Estados: q0,q1,q2,qf
Alfabeto_entrada: 0,1
Alfabeto_cinta: 0,1,B
Inicial: q0
Finales: qf
Blanco: B
Transiciones:
q0,0 -> q1,B,R
q0,1 -> q2,B,R
q0,B -> qf,B,S
q1,0 -> q1,0,R
q1,1 -> q1,1,R
q1,B -> q0,B,L
q2,0 -> q2,0,R
q2,1 -> q2,1,R
q2,B -> q0,B,L