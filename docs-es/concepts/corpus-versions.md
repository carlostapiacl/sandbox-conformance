# Versiones del corpus

Una versión del corpus es un conjunto fijo de archivos de contracts, por hash. Cada run
registra el hash de cada contract que corrió, así que cualquiera puede revisar qué versión
midió un run:

```sh
python3 runner/corpus.py of results/2026-10-26-tartaros-alpha16/tartaros.json
# {"version": "1.0", "ran": 194, "of": 194, "whole": true}
```

Un run que corrió sin cambios todos los contracts de una versión midió esa versión. Uno que
corrió algunos midió un subconjunto, que se muestra como *v1.0 (6 of 194)*. Los runs
anteriores a la primera versión corrieron contracts que cambiaron después y son *pre-1.0*.

La versión se mueve con cada cambio en `contracts/`: una versión menor por un contract
agregado o cambiado, una mayor por una eliminación o por un cambio del formato o de los
verdicts que pueda cambiar el resultado de un contract sin cambios. Los tests del lab fallan si
un contract cambia sin la versión siguiente. Las reglas y la lista de versiones están en la
[referencia del corpus](../reference/corpus.md); por qué cambió cada contract está en el
[changelog](../changelog/contracts.md).

[Qué cambió por versión](../results/versions.md) compara versiones de un mismo sandbox en los
contracts que sus runs comparten sin cambios.
