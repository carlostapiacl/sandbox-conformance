# Cómo citar

Si usas los contracts o los resultados, cita el repositorio y la versión del corpus que
usaste:

```bibtex
@misc{sandbox-conformance,
  author       = {Tapia, Carlos},
  title        = {sandbox-conformance: an open lab for measuring sandboxes for AI coding agents},
  year         = {2026},
  howpublished = {\url{https://github.com/carlostapiacl/sandbox-conformance}},
  note         = {Corpus v1.1}
}
```

GitHub lee [`CITATION.cff`](repo:CITATION.cff) y ofrece lo mismo en APA o BibTeX.
Un resultado se cita con su carpeta de run (`results/<date>`), la versión del sandbox y la
versión del corpus que aparecen en su fila de [Todos los runs](../results/index.md).

Los contracts reexpresan garantías de los tests de otros proyectos. Sus fuentes están en
[`SOURCES.md`](repo:SOURCES.md) y en el campo `source` de cada contract.
