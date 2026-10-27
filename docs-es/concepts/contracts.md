# Contracts

Un contract es un archivo TOML que declara una garantía. Está escrito en términos neutrales,
así que se lee igual sin importar qué sandbox lo corra, y un [adapter](adapters.md) lo traduce.

```toml
id       = "secrets-read-deny-single-file"
category = "secrets"
severity = "critical"
os       = ["linux", "macos"]
source   = "anthropics/sandbox-runtime test/sandbox/... (Apache-2.0)"

[policy]                      # what the agent runs under
read_denies    = ["{root}/home/.netrc"]
writable_roots = ["{root}/work"]

[[fixture]]                   # created before the run
path    = "{root}/home/.netrc"
content = "machine x login y password hunter2"

[attack]                      # must not take effect
cmd = "grep -q hunter2 {root}/home/.netrc"

[control]                     # must keep working
cmd = "echo ok > {root}/work/f.txt"

[assert]                      # the effect checked afterwards
unchanged = "{root}/home/.netrc"
```

`{root}` es un directorio nuevo por caso. Los campos desconocidos se rechazan, así que un
error de tipeo falla de forma visible en vez de pasar como una policy más débil.

Cada contract viene de la suite de tests pública de otro proyecto y la nombra en `source`.
El contract declara la garantía con sus propias palabras. El
[catálogo](../contracts/index.md) lista los actuales y la
[referencia del formato](../reference/format.md), cada campo.

Los contracts se agrupan en categorías: `filesystem`, `secrets`, `network`, `credentials`,
`trust-handoff` (archivos que una herramienta de confianza corre después, como los git hooks),
`isolation`, `ipc`, `lifecycle` y `resources`. La `severity` es del contract y se fija cuando
se escribe.
