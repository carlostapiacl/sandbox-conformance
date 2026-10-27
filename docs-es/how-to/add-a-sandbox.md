# Agregar un sandbox

Un sandbox es un módulo, `runner/adapters/<name>.py`. Nada más cambia en el motor.

```python
NAME = "mysandbox"

def identity():        # name, version, commit, license, artifact_sha256
    ...

def check(contract):   # the policy fields it cannot express: {"unsupported": [...]}
    ...                # or what the lab cannot provide: {"needs_feature": [...]}

def wrap(policy, m, contract, env):   # the argv that runs a phase under the sandbox
    ...
```

El vocabulario compartido de la policy está en [`runner/adapters/common.py`](repo:runner/adapters/common.py),
y los adapters existentes son los mejores ejemplos: [`runner/adapters/sandbox_runtime.py`](repo:runner/adapters/sandbox_runtime.py)
mapea a un archivo de configuración y [`runner/adapters/landrun.py`](repo:runner/adapters/landrun.py), a flags.

Configura el sandbox como lo recomienda su propia documentación para un confinamiento
estricto. Un adapter que no puede expresar un campo lo reporta en `check()`. Una policy
aplicada a medias sería un test más débil que se lee como aprobado.

Después instala el sandbox en [`runner/Dockerfile`](repo:runner/Dockerfile), fijado por
versión y verificado por hash, córrelo ([Quickstart](../get-started/quickstart.md)) y escribe
su página en `sandboxes/<name>.md`: qué se midió, cómo se mapea cada campo de la policy y qué
no puede expresar. Una negativa a arrancar necesita una firma que el adapter declare, para que
el lab pueda distinguir una policy rechazada de un attack contenido.
