# Adapters y profiles

Un adapter es un módulo en [`runner/adapters`](repo:runner/adapters) que traduce la policy
neutral de un contract a la configuración y la línea de comandos de un sandbox. Nunca lee el
attack. Hace tres cosas:

- `identity()` registra el nombre, la versión, el commit, la licencia del sandbox y el hash
  del binario que corrió.
- `check(contract)` nombra los campos de la policy que el sandbox no puede expresar
  (`unsupported`) o que el lab no puede proveer (`needs-feature`).
- `wrap(...)` arma el comando que corre una fase bajo el sandbox.

El motor, los contracts y el formato no cambian cuando se agrega un sandbox. Cada sandbox
tiene una página que dice cómo su adapter mapea cada campo: [Sandboxes](../sandboxes/index.md).

## Profiles {#profiles}

La policy dice qué pide un contract. Un sandbox suele tener opciones que la policy no
menciona, y el profile dice cómo las configura el adapter. `strict` pone cada una en el valor
más restrictivo que soporta la documentación del propio sandbox y que todavía deja correr el
control. `default` deja los defaults del sandbox. Todos los runs publicados hasta ahora son
`strict`, y cada fila de [Todos los runs](../results/index.md) nombra su profile.
