# Glosario de la traducción al español

Las páginas en español traducen la prosa. Lo que se nombra queda en inglés, con el mismo
spelling que en las páginas en inglés y en los contratos, para que un término se busque igual
en los dos sitios.

## Queda en inglés

contract, corpus, baseline, control, attack, assert, witness, verdict, reading, basis, run,
runner, sandbox, adapter, profile, policy, read model, fixture, host, broker, egress, proxy,
trust-handoff, read-deny, write-deny, allowlist, deny-all, allow-all, kernel, lab, seccomp,
Landlock, Seatbelt, namespace.

Los valores literales: `contained`, `escaped`, `control-broke`, `unsupported`, `vacuous`,
`needs-feature`, `not-applicable`, `invalid-baseline` y los demás results y verdicts; los
campos de los contratos (`source`, `severity`, `os`, `control_requires_sandbox`…), comandos,
rutas, nombres de archivos y de sandboxes.

En plural siguen la regla del inglés: los contracts, los runs, los sandboxes.

## Se traduce

Todo lo que se lee: oraciones, títulos de sección, textos de enlaces, títulos de admonitions.
"result" → resultado (`result` en código o como nombre de campo); "case" → caso; "evidence" → evidencia; "claim" → afirmación; "guarantee" → garantía;
"measure/measured" → medir/medido; "escape" (verbo) → escapar.

## Reglas

- Español de Chile con tuteo: tienes, puedes, mira. Nunca voseo ni usted.
- Cada encabezado traducido conserva el ancla del inglés: `## Comparar runs {#comparing-runs}`,
  con el slug que MkDocs genera del título en inglés (minúsculas, espacios a guiones, sin
  puntuación). Así los enlaces `página.md#ancla` funcionan sin cambios.
- Bloques de código, TOML, comandos y destinos de enlaces no se tocan (`repo:` incluido); se
  traduce el texto del enlace.
- Nada que no esté en el original: ni frases de cierre, ni aclaraciones, ni avisos.
- Sin rayas (—) de inciso o remate: coma, punto o paréntesis. Sin "no es X, es Y" ni muletillas
  ("cabe destacar", "la clave", "vale la pena").
- Tildes actuales: "solo", "este", sin tilde.
