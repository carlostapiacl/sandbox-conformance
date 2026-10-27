# Policy y read models

`[policy]` declara el confinamiento en campos neutrales: `writable_roots`, `read_denies`,
`read_allows`, `allow_domains`, `[broker]`, `[[masked_env]]` y el resto que está en la
[referencia del formato](../reference/format.md). Cada adapter los mapea a su sandbox, y un
campo que un sandbox no puede expresar deja el caso como `unsupported`.

Los sandboxes leen el sistema de archivos de una de dos formas, y un contract dice en cuál
está escrito.

El **modelo neutral** es el default: todo se puede leer salvo `read_denies`. Así se suelen
configurar sandbox-runtime y Codex.

El **modelo granted** (`read_scope = "granted"`) es como funcionan los sandboxes de
capacidades como nono y landrun: solo se pueden leer `writable_roots`, `read_allows` y las
rutas del sistema que provee el runner, así que un secreto se protege no otorgándolo. Un
deny dentro de un área otorgada no tiene sentido ahí.

El mismo attack se puede escribir en los dos modelos, y el corpus tiene variantes
*by-omission* de los contracts read-deny en el modelo granted, así que un sandbox de
capacidades se mide en la garantía dentro de su propio modelo. Una garantía que solo un
modelo puede declarar, como un archivo secreto en medio de un workspace escribible, es una
brecha de capacidad, y se registra como tal.
