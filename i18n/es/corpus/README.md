# Versiones del corpus

Una versión del corpus es un conjunto fijo de contracts, byte por byte: `v<version>.json` lista
el id, el path y el SHA-256 de cada contract. Un run registra el hash de cada contract que
corrió, así que cualquiera puede revisar qué versión midió
(`python3 runner/corpus.py of <result.json>`).

Dos resultados se pueden comparar contract por contract solo cuando el contract es el mismo
archivo en ambos. Los resultados entre sandboxes, o entre versiones de un mismo sandbox, se comparan en
la misma versión del corpus, o en los contracts que los dos runs comparten sin cambios
([`results/versions.md`](../results/versions.md) hace lo segundo).

## Cuándo cambia la versión {#when-the-version-moves}

La versión es `MAJOR.MINOR`. Todo cambio en `contracts/` viene con la versión siguiente
en el mismo pull request; si no, los tests del lab fallan
(`runner/corpus.py check`).

| cambio | versión | por qué |
|---|---|---|
| se agrega un contract | minor | los resultados anteriores siguen válidos; el nuevo todavía no tiene ninguno |
| cambia el archivo de un contract (attack, control, assert, policy, fixtures, `os`, `requires`, incluso un comentario) | minor | su hash cambia, así que sus resultados anteriores ya no son de este contract; los demás siguen siendo comparables |
| se quita un contract, o hay un cambio en el formato de los contracts o en [`spec/verdicts.md`](../spec/verdicts.md) que puede cambiar el resultado de un contract que no cambió | major | los resultados de antes y de después no se pueden comparar sin volver a correr |

Cada manifiesto después del primero lista lo que cambió (`since`: added, removed,
changed). [`contracts/CHANGES.md`](../contracts/CHANGES.md) dice por qué.

Un run publicado nunca se re-etiqueta: midió la versión cuyos hashes
registró. Volver a medir en una versión más nueva es un run nuevo.

## Versiones {#versions}

| versión | fecha | contracts | qué |
|---|---|---|---|
| [1.0](v1.0.json) | 2026-10-26 | 194 | la primera versión: los contracts de todos los runs hasta el 2026-10-26, con los seis contracts de credenciales enmascaradas. Los runs anteriores corrieron contracts que cambiaron desde entonces y aparecen como *pre-1.0* |
| [1.1](v1.1.json) | 2026-10-26 | 196 | dos contracts de los tests de permisos de Deno: un read-deny al que se llega por `/proc/self/root`, y un directorio con write-deny que tiene que sobrevivir a un `rm -rf` de su directorio padre |
