# Resultados y readings

Un resultado responde tres preguntas, que se registran por separado. El **resultado** es lo que se
observó, asignado de forma mecánica. La **basis** dice si un campo de la policy pidió la
garantía. El **reading** es lo que un revisor dice que significa. Un reading nunca cambia un
resultado. Las reglas completas están en los [verdicts](../reference/verdicts.md).

## Resultados {#resultados}

| resultado | significado |
|---|---|
| `contained` | el attack no tuvo efecto y el control funcionó |
| `escaped` | el attack tuvo efecto bajo el sandbox |
| `control-broke` | el attack no tuvo efecto, y el control tampoco |
| `inconclusive` | el caso corrió, pero su evidencia no lo decide |
| `unsupported` | el sandbox no puede expresar un campo de la policy: una brecha de capacidad |
| `vacuous` | el attack no funciona en este host ni siquiera sin sandbox |
| `needs-feature` | al runner o al adapter le falta algo que el contract necesita |
| `not-applicable` | el contract no aplica a este sistema o host |
| `invalid-contract`, `invalid-baseline`, `harness-error` | fallas del lab: no dicen nada sobre el sandbox |

## Basis {#basis}

`configured` significa que un campo de la policy pide la garantía, así que un escape es una
regla configurada que no se cumplió. `default` significa que ninguno la pide, así que el
resultado muestra los defaults propios del sandbox, y un escape es una diferencia de defaults.

## Readings {#readings}

Cada resultado medido distinto de `contained` recibe uno, `pending` hasta que se revisa:

| reading | ¿es un hallazgo? |
|---|---|
| `confirmed`: la garantía, tal como está declarada, no se cumplió | sí |
| `documented`: la documentación del sandbox declara el límite | un límite conocido |
| `design`: una decisión deliberada que difiere del supuesto del contract | un límite conocido |
| `platform-dependent`: depende de una capacidad del host que este host no tiene | no en este host |
| `contract-assumption`: el contract supone algo falso para este sandbox | no |
| `interface`: viene de cómo el lab se comunica con el sandbox | no |

Un conteo de escapes siempre se desglosa por reading. Los readings viven en el `review.json`
de cada run, con quién los escribió y por qué.
