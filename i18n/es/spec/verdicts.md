# Verdicts

**Versión:** 1.0.0-draft · **Estado:** borrador, abierto a revisión · **Reemplaza a:** v0 (implícita; los
runs del 2026-10-15)

Este documento define qué significa un resultado de sandbox-conformance: los valores que puede
tomar un resultado, el procedimiento que los asigna, el registro que los contiene y las reglas para
compararlos y publicarlos. [`format.md`](format.md) define cómo se escribe un contract;
este documento define cómo se juzga. [`runner/verdict.py`](../runner/verdict.py)
implementa el procedimiento de decisión (§4), y [`runner/tests/`](../runner/tests/) lo verifica,
regla por regla y contra sandboxes de referencia cuyo comportamiento se conoce.

Está escrito para que dos labs independientes, que corren el mismo contract contra el mismo
sandbox en hosts equivalentes, asignen el mismo resultado, y para que cualquiera que lea un resultado
pueda saber qué se observó, qué se pidió y qué significa, sin confiar en el
lab que lo produjo.

Las palabras clave DEBE, NO DEBE, DEBERÍA, NO DEBERÍA y PUEDE (MUST, MUST NOT, SHOULD,
SHOULD NOT y MAY) se interpretan como se describe en [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) y
[RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) cuando, y solo cuando, aparecen en
mayúsculas.

## 1. Términos {#1-terms}

- **Contract**: un archivo TOML que enuncia una garantía ([`format.md`](format.md)).
- **Sandbox bajo prueba**: un sandbox, en una versión exacta.
- **Adapter**: el código que traduce la `[policy]` neutral de un contract a la configuración y
  la línea de comandos de ese sandbox.
- **Profile**: cómo el adapter completa lo que la policy del contract deja abierto (§7).
- **Host**: la máquina donde corre el caso, descrita por sus capacidades detectadas, no
  solo por su versión de kernel.
- **Caso**: un contract × una versión de sandbox × un profile × un host.
- **Fase**: una pasada de un caso desde un estado limpio. Todo caso tiene una fase *baseline*
  (sin sandbox) y una fase *con sandbox*.
- **Lab**: el runner, los adapters y la configuración del host, a diferencia del sandbox bajo
  prueba.

## 2. Tres ejes {#2-three-axes}

Un resultado responde tres preguntas distintas. Se DEBEN registrar como campos separados
y NO se DEBEN fundir en un solo valor ni expresar solo con marcas tipográficas.

| eje | pregunta | valores | quién lo asigna |
|---|---|---|---|
| **resultado** | ¿Qué se observó? | §3 | el procedimiento de decisión (§4), mecánicamente |
| **basis** | ¿Se pidió la garantía? | `configured`, `default` (§5) | el contract y el adapter, antes del run |
| **reading** | ¿Qué significa? | §6 | un revisor, después del run |

Un reading NO DEBE cambiar un resultado. Un resultado es lo que el lab midió; un reading es una
explicación adjunta a él.

## 3. Resultados {#3-results}

Los resultados se dividen en tres grupos. Solo el primero dice algo sobre el sandbox.

### 3.1 Medidos: el caso corrió y dice algo sobre el sandbox {#31-measured-the-case-ran-and-says-something-about-the-sandbox}

| resultado | significado |
|---|---|
| `contained` | El attack no tuvo efecto bajo el sandbox, y el control tuvo éxito. |
| `escaped` | El attack tuvo efecto bajo el sandbox. |
| `control-broke` | El attack no tuvo efecto, pero el control también falló: el sandbox detuvo trabajo legítimo. |
| `inconclusive` | El caso corrió, pero la evidencia no decide entre los resultados de arriba (§4.6). |

### 3.2 No medidos: el caso no corrió, por una razón del sandbox o del host {#32-not-measured-the-case-did-not-run-for-a-reason-about-the-sandbox-or-the-host}

| resultado | significado |
|---|---|
| `unsupported` | El sandbox no puede expresar un campo de la policy del contract. Una brecha de capacidad, nunca una vulnerabilidad. |
| `not-applicable` | El contract no aplica a este host: sistema operativo equivocado, o falta una capacidad del host requerida. |
| `vacuous` | El attack no tiene efecto en este host ni siquiera sin sandbox, así que bloquearlo no prueba nada. |

### 3.3 Fallas del lab: el caso no dice nada sobre el sandbox {#33-lab-faults-the-case-says-nothing-about-the-sandbox}

| resultado | significado |
|---|---|
| `invalid-contract` | El contract no pasa la validación: un campo desconocido, una parte que falta, una condición que ninguna fase puede observar. |
| `invalid-baseline` | Sin sandbox el control falla, y el contract no declara por qué (§4.4). |
| `needs-feature` | Al runner o al adapter le falta una función que el contract necesita (un placeholder, un broker, una ubicación de logs). |
| `harness-error` | Falló el lab mismo: una excepción en el runner o el adapter, fixtures que no se pudieron crear, un sandbox que no arranca bajo ninguna policy en este host. |

Una falla del lab NO DEBE reportarse como un resultado medido. En particular, que el sandbox no
arranque NO DEBE reportarse como `contained` (§4.5).

## 4. Procedimiento de decisión {#4-decision-procedure}

Los pasos de abajo se aplican en orden; el primero que asigna un resultado termina el caso.
Cada fase parte de un estado limpio: un `{root}` nuevo, fixtures recreados, ningún proceso
que quede de una fase anterior.

### 4.1 Validar el contract {#41-validate-the-contract}

Campos desconocidos, que falte `[attack]` o `[control]`, o un `[assert]` que no nombra nada
observable → `invalid-contract`.

### 4.2 Aplicabilidad {#42-applicability}

El sistema operativo del host no está en `os`, o una capacidad de `requires` no se detecta en el host
→ `not-applicable`, con la capacidad faltante nombrada.

Lo mismo vale para lo que necesita el sandbox mismo. Algunos sandboxes se degradan en silencio: en un
host sin el mecanismo del que dependen, arrancan y no confinan nada (landrun con
`--best-effort` y sin Landlock), y la prueba de arranque (§4.5) no lo puede detectar. El adapter
DEBE declarar las capacidades del host que su sandbox necesita para confinar algo
(`HOST_REQUIRES`); sin ellas todo caso es `not-applicable`, con la capacidad y
el sandbox nombrados. Cuando un sandbox descarta solo parte de una policy en este host (las reglas TCP
de landrun por debajo de Landlock ABI 4), el adapter DEBE reportar los campos afectados como `unsupported`
(§4.3) en vez de dejar que el caso se mida como si aplicaran.

### 4.3 Capacidad {#43-capability}

El adapter reporta un campo de `[policy]` que no puede expresar → `unsupported`, con el campo
y la razón. El adapter reporta una función del runner o del adapter que le falta →
`needs-feature`. Ambos se deciden antes de que corra nada.

### 4.4 Baseline (sin sandbox) {#44-baseline-no-sandbox}

1. Cualquier excepción del lab → `harness-error`.
2. El attack DEBE tener efecto (§4.6). Si no lo tiene → `vacuous`.
3. El control DEBE tener éxito. Si falla, el caso es `invalid-baseline`, salvo que el
   contract declare `control_requires_sandbox = "<reason>"`: un control que verifica
   algo que solo el sandbox provee (una variable de proxy que fija, por ejemplo). La
   declaración DEBE estar en el contract antes del run; NO DEBE agregarse para explicar
   un resultado a posteriori.
   El control corre después del attack, en la misma fase, así que también muestra que el sandbox
   sigue usable después del intento. Por eso NO DEBE depender de nada que el
   attack tenga permitido cambiar cuando tiene éxito (el contenido de una raíz con escritura, por
   ejemplo): si no, un attack de baseline exitoso rompe el control, y la culpa es del
   contract, no del sandbox.

### 4.5 Con sandbox {#45-sandboxed}

1. Cualquier excepción del lab → `harness-error`.
2. **Prueba de arranque.** Antes que nada, el lab corre `true` bajo el sandbox con una
   policy mínima (una raíz con escritura, el directorio limpio propio de la fase). Si no
   tiene éxito → `harness-error`: el sandbox no corre en este host en absoluto, y nada
   de lo que haga después dice algo sobre el confinamiento.
3. **Contracts con `expect_refusal = true`** (el resultado correcto es que el sandbox
   rechace esta policy). El lab corre `true` bajo la policy del contract, la *prueba
   de rechazo*. Que falle es `contained` solo si la falla coincide con la firma
   de rechazo que el adapter declara para ese sandbox (un exit status y, cuando el
   sandbox imprime uno, un mensaje). Una falla que no coincide → `inconclusive`. Una
   prueba de rechazo que tiene éxito → el caso sigue con el attack, y el efecto
   decide.
4. Correr el attack, después el control.
5. El attack tuvo efecto (§4.6) → `escaped`. El resultado del attack no es claro (§4.6) →
   `inconclusive`.
6. El attack no tuvo efecto y el control falló → `control-broke`.
7. En cualquier otro caso → `contained`.

### 4.6 Cuándo el attack "tiene efecto" {#46-when-the-attack-takes-effect}

- Si el contract tiene un `[assert]` y la baseline mostró su efecto (un archivo cambiado,
  un marcador presente, un proceso muerto), el efecto decide, en ambas fases. El
  exit status del attack se registra pero no decide.
- Si no, decide el exit status del attack. `expect_exit` (por defecto 0) significa *tuvo
  efecto*. Un status NO DEBE representar dos resultados, así que:
  - si el contract declara `blocked_exit`, solo esos status significan *bloqueado*; cualquier
    otro status no es claro;
  - si no lo declara, todo otro status significa *bloqueado*, salvo los que indican que el
    attack nunca llegó a una decisión: un timeout, 126 y 127 (no ejecutable, no
    encontrado), y la muerte por una señal (128 + n). Esos no son claros. SIGSYS es la excepción:
    es como un filtro de syscalls (la acción kill de seccomp) detiene un proceso, así que significa
    *bloqueado*;
  - un attack que puede salir con su status de *bloqueado* por una razón distinta a ser
    bloqueado (un script cuyo intérprete sale con 1 ante un error no capturado, por ejemplo)
    DEBE declarar `blocked_exit` con un status que su intérprete no use.

  Un resultado que no es claro hace que el caso sea `inconclusive`.
- Un contract cuyo attack declara `expect_exit` y no tiene `[assert]` es un contract de
  *fidelidad*: la garantía es que el sandbox reporta el exit status propio del comando
  (143 para un comando terminado por SIGTERM, por ejemplo). Sin sandbox el attack DEBE
  reportar `expect_exit`, o el caso es `vacuous`; bajo el sandbox cualquier otro status es
  `escaped`, y un timeout es `inconclusive`.
- Un timeout del control es un control fallido. Un timeout de un attack decidido por exit status es
  `inconclusive`.

### 4.7 Repeticiones {#47-repetitions}

Un contract que depende del timing (una race, un fixture tardío) DEBERÍA declarar
`repeat = <n>`. Cada repetición es una fase con sandbox completa desde un estado limpio.

- Cualquier repetición `escaped` → `escaped`, registrado como *k de n*.
- Todas las repeticiones `contained` → `contained`.
- Cualquier otra mezcla (algunas `control-broke`, algunas `inconclusive`, algunas fallas del lab) →
  `inconclusive`, con cada repetición registrada.

Un solo run `contained` de un attack que depende del timing NO DEBE reportarse como una
garantía que se cumple, salvo que el contract lo declare determinista.

## 5. Basis {#5-basis}

| basis | significado |
|---|---|
| `configured` | Un campo de `[policy]` pide esta garantía. Un `escaped` aquí es una regla configurada que no se cumplió. |
| `default` | Ningún campo de `[policy]` la pide. El resultado muestra lo que el sandbox hace por su cuenta; un `escaped` aquí es una diferencia de defaults, no una regla rota. |

La basis se fija antes del run, a partir del contract y el adapter, y DEBE
registrarse con cada resultado medido.

## 6. Reading {#6-reading}

Todo resultado medido distinto de `contained` DEBERÍA recibir un reading. Mientras no lo reciba,
su reading es `pending`. Un reading lleva un tipo, una nota, quién lo escribió y cuándo.

| reading | significado | ¿cuenta como hallazgo? |
|---|---|---|
| `pending` | Todavía sin revisar. | todavía no |
| `confirmed` | La garantía, tal como está enunciada, no se cumplió. | **sí** |
| `documented` | La documentación propia del sandbox declara esta limitación. | limitación conocida |
| `design` | Una decisión de diseño deliberada que difiere del supuesto del contract. | limitación conocida |
| `platform-dependent` | El resultado depende de una capacidad del host que a este host le falta (un Landlock ABI más nuevo, por ejemplo). | no, en este host |
| `contract-assumption` | El contract supone algo que no se cumple para la arquitectura de este sandbox; dado cómo está construido, el resultado no es una vulneración. | no |
| `interface` | El resultado viene de cómo el contract o el adapter le habla al sandbox (a través de su proxy, por ejemplo), no de la garantía. | no |

Un reading PUEDE enmendarse después. El reading anterior DEBE conservarse, para que un reading
publicado nunca se reemplace en silencio.

## 7. Profiles {#7-profiles}

La `[policy]` de un contract dice lo que pide. Un sandbox suele tener opciones que la policy
no menciona. El profile dice cómo las fija el adapter.

| profile | el adapter fija cada opción que la policy deja abierta en |
|---|---|
| `strict` | el valor más restrictivo que la documentación del sandbox soporta y que todavía deja correr el control |
| `default` | el default propio del sandbox |
| `custom` | valores nombrados en el registro del caso |

Todo resultado DEBE nombrar su profile. Los runs de v0 usaron `strict`.

## 8. Comparar y publicar {#8-comparing-and-publishing}

1. Los resultados NO se DEBEN sumar, promediar ni rankear entre versiones de sandbox, profiles o
   hosts con distintas capacidades detectadas. Una tabla que compara sandboxes DEBE
   indicar la versión, el profile y el host de cada columna.
2. NO se DEBE publicar un puntaje o ranking único entre sandboxes. Los conteos por resultado
   PUEDEN publicarse por grupo de casos.
3. Un conteo de `escaped` DEBE desglosarse por reading, para que un lector pueda distinguir
   hallazgos confirmados de supuestos del contract y limitaciones conocidas.
4. Las fallas del lab (§3.3) DEBEN publicarse como tales, y NO DEBEN contarse como resultados
   medidos.
5. Un resultado publicado NO DEBE cambiarse. Una corrección es un run nuevo, o un reading nuevo
   que conserva el anterior.

## 9. Divulgación {#9-disclosure}

Si un resultado se puede mostrar es una cuestión separada de cuál es el resultado.

- Mientras haya una divulgación coordinada abierta, un lab NO DEBE publicar el resultado, su reading,
  su evidencia ni ningún texto que lo describa, y NO DEBE publicar que ese resultado
  existe: una marca "withheld" nombra el sandbox y el contract, y los contracts se pueden
  correr, así que la marca por sí sola le permite a cualquiera reproducir el hallazgo.
- Los contracts involucrados quedan fuera del corpus publicado y fuera de todo
  run publicado, para todo sandbox, para que ni una celda faltante ni una fila faltante
  apunten a ellos.
- Se publican, con sus resultados, solo cuando el proceso de divulgación con los
  mantenedores del sandbox lo permite ([`SECURITY.md`](../SECURITY.md)).

## 10. El registro del caso {#10-the-case-record}

Todo caso DEBE producir un registro. Los campos marcados *después* son OBLIGATORIOS una vez que el lab los puede
proveer (ver el roadmap) y DEBERÍAN completarse antes de eso.

| campo | contenido |
|---|---|
| `spec_version` | versión de este documento bajo la que se juzgó el caso |
| `contract` | id, ruta y SHA-256 del archivo del contract |
| `corpus_commit`, `runner_commit` | commits de los contracts y del runner |
| `adapter` | nombre, y SHA-256 del módulo del adapter |
| `sandbox` | nombre, versión, origen (paquete o release); SHA-256 del binario (*después*) |
| `profile` | §7, y para `custom`, los valores |
| `config` | la configuración que produjo el adapter, y (*después*) la configuración que el sandbox reporta haber aplicado |
| `host` | kernel, sistema operativo, arquitectura, capacidades detectadas (Landlock ABI, user namespaces, cgroups…), opciones del contenedor |
| `result`, `basis`, `reading`, `disclosure` | §3, §5, §6, §9 |
| `phases` | para cada fase y repetición: comando, exit status, si hubo timeout, duración, output capturado (acotado), evidencia del efecto |
| `reason` | para todo resultado distinto de `contained` y `escaped`, el porqué |

## 11. Exportación SARIF {#11-sarif-export}

Un run PUEDE exportarse como [SARIF 2.1.0](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html),
para que las herramientas que leen resultados de análisis estático y de seguridad lo puedan ingerir sin cambios. Un
`run` SARIF por versión de sandbox y profile; cada contract es una `rule`; cada caso
medido es un `result`.

| resultado | `kind` SARIF | `level` SARIF |
|---|---|---|
| `contained` | `pass` | `none` |
| `escaped` | `fail` | `error` (severity critical o high), `warning` (medium) |
| `control-broke` | `fail` | `warning` |
| `inconclusive` | `open` | `none` |
| `unsupported`, `not-applicable`, `vacuous` | `notApplicable` | `none` |
| fallas del lab (§3.3) | no es un `result`: una `toolExecutionNotification` de la `invocation` del run | `error` |

- Un reading `contract-assumption` o `interface` se exporta como una `suppression` con
  `status: accepted` y la nota como su `justification`. El resultado sigue siendo un `fail`.
- `basis`, `reading`, `profile` y las capacidades del host van en `properties`.

## 12. Versionado {#12-versioning}

Este documento usa versionado semántico. Un cambio que puede cambiar el resultado de un
caso existente es una versión mayor. Un run registra la versión bajo la que se juzgó, y
nunca se reescribe con otro juicio: volver a juzgarlo es un run nuevo.

### Desde v0 (los runs del 2026-10-15) {#from-v0-the-2026-10-15-runs}

Los runs del 2026-10-15 se juzgaron antes de que existiera este documento. Quedan como se publicaron.
Así se leen sus valores en términos de v1:

| v0 | v1 |
|---|---|
| `contained` con razón "sandbox refused to start" | `contained` solo si el rechazo coincide con la firma del adapter; si no, `inconclusive` (volver a medir) |
| `contained` / `control-broke` con `control_fails_unsandboxed` | `invalid-baseline`, salvo que el contract ahora declare `control_requires_sandbox` |
| `needs-feature` con razón "runner error…" | `harness-error` |
| `needs-feature` (otras razones) | `needs-feature` |
| `withheld` (resultado) | no se publica en absoluto mientras la divulgación esté abierta (§9) |
| `basis: policy` / `built-in` | `configured` / `default` |
| marcas `*` / `‡` / `§` | `basis: default` / reading `contract-assumption` o `interface` / reading `platform-dependent` |
| reading `kernel-dependent` | `platform-dependent` |
| reading `vacuous` | eliminado: el resultado ya lo dice |
| attacks decididos por exit status sin `blocked_exit` | v0 leía cualquier status distinto de éxito como bloqueado; v1 lee los timeouts, 126, 127 y las señales distintas de SIGSYS como `inconclusive` |
| `contained` / `control-broke` de un sandbox que nunca arrancó | `harness-error` (la prueba de arranque, §4.5) |

## 13. Preguntas abiertas {#13-open-questions}

- **Firmas de rechazo**: cada adapter tiene que declarar una. Algunos sandboxes no imprimen
  un mensaje distinto cuando rechazan una policy; para esos, ¿basta con un exit status?
- **Cantidad de repeticiones**: ¿qué `n` hace confiable un `contained` en una race, y debería
  fijarse por contract o por familia?
- **Observación independiente**: §4.6 todavía confía en el snapshot que el runner mismo toma del
  efecto. Una versión posterior debería exigir efectos observados desde fuera del alcance del
  proceso con sandbox, al menos para las garantías de red y de procesos.
- **Severidad del hallazgo**: `severity` pertenece al contract; no está resuelto si un hallazgo confirmado
  necesita su propia calificación de impacto (condiciones necesarias, alcance).
