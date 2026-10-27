# Escribir un contract

1. **Encuentra la garantía en una suite de tests pública.** El lab mide afirmaciones que los
   sandboxes hacen sobre sí mismos, así que un contract parte del test de otro proyecto y lo
   nombra en `source`. Las suites candidatas están en [`corpus-roadmap.md`](repo:corpus-roadmap.md).
2. **Escríbelo en términos neutrales** en `contracts/<category>/<id>.toml`: la policy, los
   fixtures, un attack que no debe tener efecto, un control que tiene que seguir funcionando
   y el efecto para el assert ([Contracts](../concepts/contracts.md),
   [formato](../reference/format.md)).
3. **Haz que el attack sea real.** Córrelo sin sandbox: tiene que funcionar, o el caso es
   `vacuous`. Nunca debilites un attack para que un sandbox pase.
4. **Mantén el control independiente del attack.** Corre después del attack, así que no debe
   necesitar nada que un attack exitoso cambie.
5. **Di qué lo decide.** Cuando un exit status es la evidencia, declara `expect_exit` y, si el
   attack puede salir con su status de bloqueo por otra razón, `blocked_exit`. Declara
   `requires` para las capacidades del host y `os` para los sistemas a los que aplica.
6. **Escribe la siguiente versión del corpus** en el mismo pull request:

    ```sh
    python3 runner/corpus.py build 1.1
    ```

    y agrega una línea a [`contracts/CHANGES.md`](repo:contracts/CHANGES.md) que diga por qué.
    Los tests del lab corren `corpus.py check` y fallan si no
    ([Versiones del corpus](../concepts/corpus-versions.md)).
7. **Corre los tests del lab** (`python3 -m unittest discover -s runner/tests`): los sandboxes
   de referencia revisan que un sandbox allow-all escape de tu attack y que uno deny-all rompa
   tu control.

Si una garantía solo tiene sentido en el modelo de un sandbox, dilo en el contract. Un
sandbox que no puede expresar un campo recibe [`unsupported`](../concepts/results.md).
