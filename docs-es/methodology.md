# Metodología

## Qué se mide {#what-is-measured}

Si un sandbox mantiene una garantía cuando el agente que está adentro intenta romperla. Se
asume que el agente está comprometido: cada attack se ejecuta tal como está escrito, desde
un proceso confinado por el sandbox, y el lab observa si su efecto ocurrió en el host. Qué
tan seguido se compromete un agente real, por ejemplo con un prompt injection, es otra
pregunta, y la miden benchmarks como [AgentDojo](https://agentdojo.spylab.ai/).

Fuera del alcance: escapes del kernel o de un hipervisor, canales laterales y denegación de
servicio más allá de los límites de recursos que declara un contract. Los hosts del lab son
VMs desechables con un kernel conocido, adecuadas para attacks que intentan salir del
sandbox dentro del guest.

## Cómo se decide un caso {#how-a-case-is-decided}

Cada caso corre un baseline sin sandbox y una fase con sandbox, cada una desde un estado
limpio. El [procedimiento de decisión](reference/verdicts.md#4-decision-procedure) convierte
lo que observaron en un resultado de forma mecánica, y [los tests del lab](repo:runner/tests)
lo revisan regla por regla contra sandboxes de referencia. Después, un revisor agrega un
reading, y este nunca cambia el resultado.

## Comparar runs {#comparing-runs}

Una fila de [Todos los runs](results/index.md) es una versión de un sandbox, un host, un
profile, una versión del corpus y una versión de los verdicts. Los resultados no se suman, no
se promedian ni se ordenan en ranking entre filas que difieren en cualquiera de estos, y no
se publica un puntaje único entre sandboxes. Los conteos son por resultado, y los escapes se
desglosan por reading, así que un hallazgo confirmado se lee aparte de un supuesto del
contract o de un límite conocido.

## Configurar cada sandbox {#configuring-each-sandbox}

Cada sandbox corre a través de un adapter configurado como lo recomienda su propia
documentación para un confinamiento estricto. Un campo que no puede expresar se reporta como
`unsupported` y queda aparte de los resultados medidos. Una diferencia de defaults lleva
`basis: default`.

## Evidencia {#evidence}

Cada caso registra los comandos que se corrieron, sus exit statuses, la salida acotada, el
efecto observado, el hash del contract, el hash del adapter, el hash del binario del sandbox,
y las capacidades detectadas del host y las opciones del contenedor. El registro crudo de
cada run se publica con él.

## Conflicto de interés {#conflict-of-interest}

TartarOS, uno de los sandboxes medidos, partió junto con este lab, del mismo autor. Es donde
se prueban las variantes que encuentra el lab, una por una, para ver si cada una se puede
mitigar; el lab es el que dice si se logró. Para evitar que eso influya en los resultados:

- los contracts vienen de las suites de tests de otros proyectos, cada uno con su crédito;
- el corpus se congeló antes de la primera medición de TartarOS, y cada cambio posterior a
  un contract queda registrado con su razón en el [changelog](changelog/contracts.md) y mueve
  la [versión del corpus](concepts/corpus-versions.md), así que un contract cambiado después
  de un resultado queda a la vista;
- los resultados y la página de TartarOS declaran el conflicto, y sus archivos de resultados llevan
  `conflict_of_interest`.

## Divulgación {#disclosure}

Una debilidad encontrada en un sandbox va primero a ese proyecto. Mientras una divulgación
está abierta, no se publica nada sobre ella, ni siquiera el hecho de que se retiene un
resultado. Un contract se puede correr, así que esa sola marca le permitiría a cualquiera
reproducirlo. Los contracts involucrados quedan fuera del corpus publicado y de cada run
hasta que se cierra la divulgación ([verdicts §9](reference/verdicts.md#9-disclosure)).
