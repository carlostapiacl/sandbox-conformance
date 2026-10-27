# sandbox-conformance

Un lab abierto para medir sandboxes para agentes de programación con IA.

Los sandboxes para agentes de programación dicen qué detienen, como leer tus llaves o
plantar un git hook. Este lab convierte cada una de esas afirmaciones en un **contract** que
cualquiera puede correr, lo corre contra cada sandbox con el mismo procedimiento y publica
el resultado con la evidencia de cada caso.

**Corpus v1.1**: 196 contracts, reexpresados a partir de las suites de tests públicas de
sandbox-runtime, nono, Codex, Deno, bubblewrap y OpenHands, cada uno con el crédito a su
fuente. Medidos hasta ahora: sandbox-runtime, nono, Codex CLI, landrun y TartarOS, en Linux.

## Por dónde empezar {#where-to-start}

- Para ver los números: [Todos los runs](results/index.md), y después la carpeta de un run
  para ver la evidencia.
- Para correrlo tú mismo: [Quickstart](get-started/quickstart.md).
- Para saber qué significa un número antes de confiar en él: [Metodología](methodology.md) y
  [Resultados y readings](concepts/results.md).
- Para agregar una garantía o un sandbox: [Escribir un contract](how-to/write-a-contract.md),
  [Agregar un sandbox](how-to/add-a-sandbox.md).

## Cómo decide un contract {#how-a-contract-decides}

Un contract tiene tres partes. El **attack** es algo que el agente no debe poder hacer. El
**control** es trabajo legítimo que tiene que seguir funcionando, así que un sandbox que
bloquea todo no pasa. El **assert** revisa el efecto real en el disco o en la red. Antes de
que un contract cuente en contra de un sandbox, su attack tiene que funcionar sin sandbox en
el mismo host ([Baseline y control](concepts/baseline.md)).

TartarOS, uno de los sandboxes medidos, partió con este lab, del mismo autor, para
intentar mitigar cada variante que el lab encuentra. La
[metodología](methodology.md#conflict-of-interest) dice cómo se evita que eso influya en
los resultados.
