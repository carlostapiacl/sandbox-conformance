# Formato de los contracts

Un contract es un archivo TOML que describe una sola garantía que un sandbox debería cumplir.
Está escrito para que cualquiera lo lea sin conocer el funcionamiento interno de ningún sandbox,
y para que un runner lo ejecute contra cualquier sandbox a través de un adapter.
Cómo se juzga un run de un contract, y qué significa cada resultado, está en
[`verdicts.md`](verdicts.md).

## Forma {#shape}

```toml
id       = "secrets-read-deny-single-file"   # unique, kebab-case
category = "secrets"                         # folder it lives in
severity = "critical"                        # critical | high | medium
os       = ["linux", "macos"]                # where it applies
source   = "project test/path (License)"     # where the guarantee comes from
requires = ["userns"]                        # host capabilities needed (optional)

[policy]            # the confinement the agent runs under (sandbox-neutral fields)
read_denies    = ["{root}/home/.netrc"]
writable_roots = ["{root}/work"]

[[fixture]]         # files/dirs created before the run
path    = "{root}/home/.netrc"
content = "machine x login y password hunter2"

[attack]            # must NOT succeed
cmd = "grep -q hunter2 {root}/home/.netrc"

[control]           # legitimate work that MUST keep working
cmd = "echo ok > {root}/work/f.txt"

[assert]            # the real effect checked afterwards
unchanged = "{root}/home/.netrc"
```

## Las tres partes que le dan sentido a un resultado {#the-three-parts-that-make-a-result-mean-something}

- **attack**: la operación prohibida. Un contract cuenta en contra de un sandbox solo
  si este attack *funciona sin ningún sandbox* en el mismo host; si no, el run lo
  reporta VACUOUS, porque "bloqueado" no probaría nada.
- **control**: trabajo normal que tiene que seguir funcionando. Un sandbox que bloquea
  el attack rompiendo el control falla el contract.
- **assert**: lo que se revisa en disco o en la red: un archivo protegido está
  `unchanged`, un marcador plantado está `absent`.

`{root}` es un directorio temporal nuevo por cada run. `expect_refusal = true` marca una
policy cuyo resultado correcto es que el sandbox se niegue a arrancar.

## Campos que hacen un resultado inequívoco {#fields-that-make-a-result-unambiguous}

Cómo se juzga cada uno está en [`verdicts.md`](verdicts.md) §4.

| campo | dónde | significado |
|---|---|---|
| `expect_exit` | `[attack]` | el status que significa que el attack tuvo efecto (por defecto 0). Sin `[assert]`, el contract es un contract de *fidelidad*: el sandbox tiene que reportar exactamente este status |
| `blocked_exit` | `[attack]` | los status que significan *bloqueado*. Obligatorio cuando el attack puede salir con su status de bloqueo por otra razón: un script de Python que sale con 1 cuando lo bloquean no puede distinguir eso de una excepción no capturada, así que sale con 3 y declara `blocked_exit = [3]` |
| `control_requires_sandbox` | nivel superior | por qué se espera que el control falle sin sandbox (revisa una variable que pone el proxy del sandbox, o habla con su broker). Sin este campo, un control que falla sin sandbox deja el caso en `invalid-baseline` |
| `repeat` | nivel superior | corre la fase con sandbox esta cantidad de veces, para attacks que dependen del timing; cualquier escape es un escape, y se reporta como *k de n* |
| `bind` | `[[server]]` | la dirección en la que escucha un witness server (por defecto `127.0.0.1`). `{host_ip}` es la dirección propia de este host que no es loopback, para un witness al que un proceso con sandbox no debe llegar; un contract que la usa declara `requires = ["host-ip"]` |

El control corre después del attack, en la misma fase. No puede depender de nada que el
attack pueda cambiar legítimamente cuando tiene éxito (el contenido de un writable root,
por ejemplo), porque si no, un attack que funciona lo rompe en el baseline.

Witnesses y asserts que provee el runner:

| campo | dónde | significado |
|---|---|---|
| `log` | `[[server]]` | agrega a este archivo cada request head crudo que recibe el server |
| `log_paths` | `[[server]]` | agrega, uno por línea, el path que pide cada request line (también una en pipeline), normalizado como lo haría un server común antes de rutearlo: sin authority, con los percent-escapes deshechos y los dot segments resueltos |
| `echo_headers` | `[[server]]` | responde con el request head recibido, para que el agente vea lo que llegó al upstream |
| `respond` | `[[server]]` | la respuesta cruda que se envía (por defecto un `200 ok`) |
| `absent_line` | `[assert]` | `{ file, pattern }`: el efecto es una línea de `file` que calza con la expresión regular `pattern` |
| `[[host_alias]]` | nivel superior | `name`, `ip`: un nombre de host que se resuelve a `ip` solo para este caso (en `/etc/hosts`, restaurado después). Un contract que lo usa declara `requires = ["hosts-file"]`: donde `/etc/hosts` no se puede escribir, el caso no aplica |
| `tls`, `name` | `[[server]]` | el witness habla TLS para el host `name`, con un certificado hoja firmado por una CA que el runner crea en cada run. Varios en una misma dirección comparten un listener y cada conexión la atiende el que pide su TLS server name. El launcher confía en esa CA (`NODE_EXTRA_CA_CERTS`, `CURL_CA_BUNDLE`, `SSL_CERT_FILE`) |
| `read_body`, `echo_request` | `[[server]]` | lee también el body del request (`Content-Length` o chunked, 64 KiB como máximo) hacia `log`; responde con el request completo recibido, body incluido |

## Credenciales enmascaradas: `[[masked_env]]` {#masked-credentials-masked_env}

Una credencial enmascarada es una variable que el agente usa sin tener su valor: la
copia del agente es un reemplazo, y el sandbox pone el valor real en el egress, solo
hacia los hosts propios de la credencial.

```toml
[[masked_env]]
name = "SC_TOKEN"
value = "sc-real-7f3a91"           # in the launcher's environment
inject_hosts = ["api.masked.test"]  # where the real value may go
```

El valor real está en el entorno del launcher, tal como lo lee un sandbox. Sin
sandbox, el agente lo tiene, y eso es lo que muestra el baseline. Cada adapter mapea la
tabla al enmascaramiento de su sandbox, o reporta `unsupported`. Un witness al que el agente
tiene que llegar por nombre a través del egress proxy del sandbox escucha en `{host_ip}`, y su
nombre se resuelve a `{witness_ip}`: otro host de la red del lab que le reenvía el tráfico
(`runner/lab-witness.sh`). El contract declara `requires = ["witness-host"]`.
Las direcciones de esa red son de las que ningún guard contra SSRF trata como internas (TEST-NET-2,
`198.51.100.0/24`), y el witness no está en el host del propio sandbox, que un guard
también podría rechazar; así, el caso lo decide la policy y no el guard.

## La tabla `[broker]` {#the-broker-table}

Un broker de credenciales le permite al agente usar un secreto que nunca tiene: el agente le pide
al broker, y el broker hace el request real con el secreto agregado. Un contract sobre un
broker lo declara en términos neutrales; cada adapter lo mapea al broker de su sandbox.

```toml
[broker]
port  = 19550                       # loopback port the agent reaches it on
token = "run-token-only-the-agent-has"  # the agent sends it in X-Broker-Auth
allowed_hosts  = [".allowed.test"]  # forwarding allow-list (optional)
allow_internal = false              # may an allowed name resolve inward (optional)

[[broker.capability]]               # /up/rest -> upstream_base/rest
prefix        = "/up"
upstream_base = "http://127.0.0.1:19650"
inject_header = "Authorization"     # added by the broker
inject_value  = "Bearer the-agent-never-sees-this"
```

**El baseline corre contra un broker de referencia.** Sin sandbox no hay
broker, así que "el attack funciona sin sandbox" necesita un reemplazo. En el baseline
el runner levanta [`runner/reference_broker.py`](../runner/reference_broker.py) en
el puerto del contract: un broker escrito de la forma obvia, sin ninguna de las defensas
que prueban los contracts (no revisa el token, reenvía todos los headers del agente, compara el prefijo
como string y agrega el path tal como viene escrito, sigue redirects, reenvía a cualquier host
por nombre). Un attack que no pasa por él deja el caso en `vacuous`; uno
que pasa se corre después contra el broker propio del sandbox. El broker de referencia es
el mismo para todos los sandboxes.

## Adapters {#adapters}

Cada sandbox mapea la `[policy]` neutral a su propia configuración. Un campo que un
sandbox no puede expresar es una brecha de capacidad y se registra como tal, nunca se cuenta como
vulnerabilidad. Mira `sandboxes/`.

## Alcance de lectura: el modelo neutral vs. el modelo granted {#read-scope-the-neutral-model-vs-the-granted-model}

Por defecto un contract usa el **read model neutral**: todo se puede leer
excepto los paths nombrados en `read_denies`. Esto refleja cómo se suelen configurar
sandbox-runtime y Codex (leer en todas partes y después denegar), y es el modelo
detrás de todos los contracts que tienen un campo `read_denies`.

Un sandbox de capacidades como nono funciona al revés. Landlock es
allow-only: concedes el workspace y nada más, y un secreto queda
protegido porque nadie lo concedió. Un `read_denies` dentro de un área concedida no
tiene sentido ahí, así que los contracts neutrales reportan `unsupported` contra nono,
no porque nono sea más débil, sino porque el test está escrito en un modelo que nono no
habla.

`read_scope = "granted"` declara la policy en ese segundo modelo, para que el mismo
attack se pueda medir de forma justa contra los tres sandboxes:

```toml
[policy]
read_scope    = "granted"
writable_roots = ["{root}/work"]
read_allows    = ["{root}/home/notes.txt"]   # a non-secret file the control reads
```

Con `read_scope = "granted"` los únicos paths que se pueden leer son `writable_roots`,
`read_allows` y los paths del sistema que el runner ya provee (para que `sh`,
`python3` y `curl` sigan corriendo). **No** hay `read_denies`: el path protegido
no se puede leer porque no está en ninguna concesión. Un contract que necesita un
`read_deny` *dentro* de un área concedida y escribible (un archivo protegido en medio
del workspace) no se puede expresar así; esa es una brecha de capacidad real,
registrada como tal, no traducida.

Un adapter que no puede expresar el modelo granted para su sandbox reporta
`unsupported`, exactamente como lo hace con cualquier otro campo que no puede mapear.
