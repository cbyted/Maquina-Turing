Estados: q0,q1,q2,q3,qf
Alfabeto_entrada: 0,1
Alfabeto_cinta: 0,1,B,X
Inicial: q0
Finales: qf
Blanco: B
Transiciones:
q0,0 -> q1,X,R
q1,0 -> q1,0,R
q1,1 -> q2,1,R
q2,1 -> q2,1,R
q2,B -> q3,B,L
q3,1 -> q3,1,L
q3,0 -> q0,0,R
q0,X -> q0,X,R
q0,B -> qf,B,S