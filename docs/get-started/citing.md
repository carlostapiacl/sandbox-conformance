# Citing

If you use the contracts or the results, cite the repository and the corpus version you
used:

```bibtex
@misc{sandbox-conformance,
  author       = {Tapia, Carlos},
  title        = {sandbox-conformance: an open lab for measuring sandboxes for AI coding agents},
  year         = {2026},
  howpublished = {\url{https://github.com/carlostapiacl/sandbox-conformance}},
  note         = {Corpus v1.0}
}
```

GitHub reads [`CITATION.cff`](repo:CITATION.cff) and offers the same as APA or BibTeX.
A result is cited with its run folder (`results/<date>`), the sandbox version and the
corpus version in its row of [All runs](../results/index.md).

The contracts re-express guarantees from other projects' tests. Their sources are in
[`SOURCES.md`](repo:SOURCES.md) and in each contract's `source` field.
