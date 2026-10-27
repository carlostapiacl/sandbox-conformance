# Baseline y control

Un caso corre dos veces desde un estado limpio. El **baseline** corre el attack y el control
sin sandbox. La fase **con sandbox** los corre bajo el sandbox.

Si el attack no funciona en este host sin sandbox, bloquearlo no prueba nada, y el caso es
`vacuous`. Si
el control falla sin sandbox, la culpa es del contract y el caso es
`invalid-baseline`, salvo que el contract declare por qué el control necesita el sandbox
(`control_requires_sandbox`, para un control que habla con el proxy del sandbox).

Un sandbox que detiene el attack rompiendo el control recibe `control-broke`, así que uno que
bloquea todo no pasa. El control corre
después del attack en la misma fase, así que no debe depender de nada que un attack exitoso
pueda cambiar.

Cuando la garantía necesita una contraparte que solo existe dentro de un sandbox, como un
broker de credenciales, el baseline corre contra uno de referencia escrito sin ninguna de las
defensas que se están probando. Un attack que no logra pasar el de referencia también es
`vacuous` ([Witnesses](witnesses.md#the-reference-broker)).

El lab revisa sus propios baselines contra [sandboxes de referencia](repo:runner/reference):
uno allow-all, bajo el cual cada attack tiene que escapar, y uno deny-all, bajo el cual cada
control tiene que romperse.
