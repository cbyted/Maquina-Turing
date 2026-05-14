Estados: q0,q1,qf
Alfabeto_entrada: a,b
Alfabeto_cinta: a,b,B
Inicial: q0
Finales: qf
Blanco: B
Transiciones:
q0,a -> q1,a,R
q0,b -> q0,b,R
q1,a -> qf,a,R
q1,b -> q0,b,R
qf,a -> qf,a,R
qf,b -> qf,b,R