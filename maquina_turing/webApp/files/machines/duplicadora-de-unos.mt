Estados: q0,q1,q2,q3,q4,qf
Alfabeto_entrada: 1
Alfabeto_cinta: 1,B,X,Y
Inicial: q0
Finales: qf
Blanco: B
Transiciones:
q0,1 -> q1,X,R
q0,Y -> q3,Y,S
q0,B -> qf,B,S
q1,1 -> q1,1,R
q1,Y -> q1,Y,R
q1,B -> q2,Y,L
q2,1 -> q2,1,L
q2,Y -> q2,Y,L
q2,X -> q0,X,R
q3,Y -> q3,1,R
q3,B -> q4,B,L
q4,1 -> q4,1,L
q4,X -> q4,1,L
q4,B -> qf,B,R