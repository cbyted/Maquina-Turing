Estados: q0,q1,q2,q3,q4,q5,q6,q7,qf
Alfabeto_entrada: 0,1
Alfabeto_cinta: 0,1,#,B,X,Y
Inicial: q0
Finales: qf
Blanco: B
Transiciones:
q0,0 -> q0,0,R
q0,1 -> q0,1,R
q0,B -> q1,#,L
q1,0 -> q1,0,L
q1,1 -> q1,1,L
q1,# -> q1,#,L
q1,B -> q2,B,R
q2,0 -> q3,X,R
q2,1 -> q4,Y,R
q2,# -> qf,#,S  
q3,0 -> q3,0,R
q3,1 -> q3,1,R
q3,# -> q3,#,R
q3,B -> q5,0,L
q4,0 -> q4,0,R
q4,1 -> q4,1,R
q4,# -> q4,#,R
q4,B -> q5,1,L
q5,0 -> q5,0,L
q5,1 -> q5,1,L
q5,# -> q5,#,L
q5,X -> q2,0,R  
q5,Y -> q2,1,R  