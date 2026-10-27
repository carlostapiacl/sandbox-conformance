# Runner

Corre los contracts contra un sandbox a través de su adapter, dentro de un container
Linux desechable. Nunca lo corras en una estación de trabajo: los attacks hacen lo que dicen.

| archivo | qué |
|---|---|
| `run.py` | el runner: baseline sin sandbox, después attack + control + `[assert]` con el sandbox; registra lo que observó cada fase |
| `verdict.py` | el procedimiento de decisión de [`spec/verdicts.md`](../spec/verdicts.md): convierte esas observaciones en un resultado por contract |
| `adapters/<sandbox>.py` | mapea la `[policy]` neutral de un contract a la configuración de ese sandbox; `check()` nombra lo que no puede expresar, `wrap()` arma el comando |
| `adapters/common.py` | el vocabulario de `[policy]` que comparten todos los adapters |
| `report.py` | convierte la salida completa del runner en una carpeta de run: `<sandbox>.json`, `raw/`, `comparison.md` |
| `landing.py` | reconstruye el bloque de datos de `index.html` a partir de una carpeta de run, con las mismas marcas y notas de revisión que su `comparison.md` |
| `Dockerfile` | la imagen del lab: imagen base por digest, cada descarga verificada contra un sha256 fijo; el `identity()` de cada adapter registra el sha256 de lo que realmente corrió (`artifact_sha256`) |
| `lab.sh` | corre un sandbox en un container `--rm` con las opciones registradas en el host stamp |
| `sc-lab.apparmor` | profile de AppArmor que solo agrega `userns` (Ubuntu 24.04), cargado para un run y quitado después |
| `reference/` | sandboxes falsos con un comportamiento conocido (allow-all, deny-all, roto, que se niegan a arrancar), usados solo para probar el lab |
| `lima/` | una VM local desechable para el lab (Ubuntu 24.04, kernel 6.8, nada montado), como la que se usó en el run del 2026-10-16 |
| `tests/` | los tests propios del lab: `python3 -m unittest discover -s runner/tests` (Python 3.11+, sin dependencias, sin privilegios) |

En un host Linux desechable con Docker:

```sh
apparmor_parser -r -W runner/sc-lab.apparmor
docker build -t sc-lab:tools runner/
sh runner/lab.sh sandbox-runtime /tmp/out          # or nono, codex; optional contract ids
python3 runner/report.py /tmp/out results/<date>
apparmor_parser -R runner/sc-lab.apparmor
```

Resultados: `contained`, `escaped`, `control-broke`, `unsupported` (una brecha de capacidad,
nunca una vulnerabilidad), `vacuous` (el attack tampoco funciona sin
sandbox), `needs-feature`, `not-applicable`. Mira `results/<date>/README.md` para
el método.
