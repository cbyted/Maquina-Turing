Estados: q0,q1,qf
Alfabeto_entrada: a,b
Alfabeto_cinta: a,b,B
Inicial: q0
Finales: qf
Blanco: B
Transiciones:
q0,a -> q1,a,R
q0,b -> q0,b,R
q1,a -> q2,a,R
q1,b -> q0,b,R
q2,a -> q2,a,R
q2,b -> q0,b,R
q2,B -> qf,B,R