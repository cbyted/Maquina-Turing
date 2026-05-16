Estados: q0,q1,q2,q3,q4,qf
Alfabeto_entrada: 0,1
Alfabeto_cinta: 0,1,#,B,X,Y
Inicial: q0
Finales: qf
Blanco: B
Transiciones:
q0,0 -> q1,X,R
q0,1 -> q2,Y,R
q0,B -> q3,B,L
q1,0 -> q1,0,R
q1,1 -> q1,1,R
q1,# -> q1,#,R
q1,B -> q3,0,L
q2,0 -> q2,0,R
q2,1 -> q2,1,R
q2,# -> q2,#,R
q2,B -> q3,1,L
q3,0 -> q3,0,L
q3,1 -> q3,1,L
q3,X -> q0,X,R
q3,Y -> q0,Y,R
q3,# -> q4,#,R
q4,0 -> q4,0,R
q4,1 -> q4,1,R
q4,B -> qf,B,S