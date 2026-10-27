# Publicar un run

Un run publicado es una carpeta `results/<date>[-what]` con:

- `<sandbox>.json` por sandbox: una línea por caso, con su resultado, basis, razón, exit
  statuses, efecto y el hash del contract, más la identidad del sandbox del run, el host
  stamp, el profile, la versión de la spec y la versión del corpus;
- `raw/<sandbox>.full.json`: todo lo que capturó el runner;
- `comparison.md`: la tabla, generada;
- `review.json`: el reading de cada resultado distinto de `contained`, con quién y por qué;
- `README.md`: qué se midió, en qué, y todo lo que un lector necesite para leerlo.

```sh
python3 runner/report.py /tmp/out results/2026-11-02-mysandbox
python3 runner/versions.py > results/versions.md
```

Antes de publicar, revisa cada resultado que no sea `contained` contra su salida cruda y dale un
reading. No declares nada que no se haya corrido. Un resultado publicado nunca se edita: una
corrección es un run nuevo, o un reading nuevo que conserva el anterior.

Para enviar un run medido en otra parte, abre un pull request con la carpeta y el commit del
lab con que se corrió. Un hallazgo sobre un sandbox sigue las
[reglas de divulgación](../methodology.md#disclosure).
