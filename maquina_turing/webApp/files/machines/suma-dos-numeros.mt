Estados: q0,q1,q2,qf
Alfabeto_entrada: 1,#
Alfabeto_cinta: 1,#,B
Inicial: q0
Finales: qf
Blanco: B
Transiciones:
q0,1 -> q0,1,R
q0,# -> q1,#,R
q1,1 -> q1,1,R
q1,B -> q2,1,L
q2,1 -> q2,1,L
q2,# -> qf,B,R