# Witnesses

Algunos efectos ocurren en la red. El runner levanta servidores witness para un contract
(`[[server]]`) y el assert lee lo que recibieron.

- Un witness puede registrar el encabezado de cada request, las rutas pedidas (normalizadas
  como las enrutaría un servidor) o el request completo con su cuerpo, y responder con lo que
  recibió, así el agente ve lo que llegó al upstream.
- `bind = "{host_ip}"` pone un witness en la dirección propia del host, una a la que un
  proceso con sandbox no debe llegar.
- `[[host_alias]]` resuelve un nombre a una dirección para un caso, en `/etc/hosts`.

## Witnesses TLS {#tls-witnesses}

Un witness con `tls = true` y un `name` habla TLS para ese host, con un certificado firmado
por una CA que el runner crea para el run. Varios comparten una dirección y cada conexión la
atiende el que pide su server name. El launcher confía en esa CA, como confiaría en una CA
local del sitio.

## El witness host {#the-witness-host}

El egress proxy de un sandbox puede rechazar nombres que resuelven al host del propio sandbox
o a direcciones internas. Esa defensa decidiría un contract de credentials antes que la policy
que prueba. Por eso esos contracts llegan a su witness a través de un segundo contenedor en
una red del lab en TEST-NET-2 (`198.51.100.0/24`), un rango de direcciones que ninguna de
esas protecciones trata como interno, y que reenvía al runner. Declaran
`requires = ["witness-host"]` y quedan `not-applicable` en un host que no lo tiene
([Quickstart](../get-started/quickstart.md#3-the-contracts-that-need-a-witness-host)).

## El broker de referencia {#the-reference-broker}

Sin sandbox no hay broker de credenciales, así que el baseline de un contract `[broker]`
corre contra [uno de referencia](repo:runner/reference_broker.py) escrito de la forma obvia:
sin revisión del token, con todos los headers del agente reenviados, el prefijo comparado
como texto y las redirecciones seguidas. Es el mismo para todos los sandboxes. Un attack que
no logra pasarlo es `vacuous`.
