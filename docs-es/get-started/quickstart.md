# Quickstart

Los attacks hacen lo que dicen: intentan leer secretos, escribir fuera del workspace y
llegar a la red. Córrelos solo en un host desechable, nunca en tu estación de trabajo.

## 1. Los tests propios del lab (cualquier máquina, sin privilegios) {#1-the-labs-own-tests-any-machine-no-privileges}

```sh
git clone https://github.com/carlostapiacl/sandbox-conformance
cd sandbox-conformance
python3 -m unittest discover -s runner/tests     # Python 3.11+, no dependencies
python3 runner/corpus.py check                   # contracts/ is exactly the latest corpus version
```

Los tests corren el procedimiento de decisión contra [sandboxes de referencia](repo:runner/reference)
cuyo comportamiento se conoce: uno que permite todo (cada attack escapa), uno que deniega
todo (cada control se rompe) y otros que se niegan a correr. Si pasan, el lab juzga un caso
como dicen los [verdicts](../reference/verdicts.md).

## 2. Un sandbox, en un host Linux desechable {#2-one-sandbox-on-a-disposable-linux-host}

Necesitas Docker y un kernel con Landlock (el kernel de Docker Desktop no lo tiene). Los
runs publicados usaron Ubuntu 24.04 con kernel 6.8 en una [VM de Lima](../how-to/run-on-linux.md).

```sh
sudo apparmor_parser -r -W runner/sc-lab.apparmor      # adds userns for the container only
sudo docker build -t sc-lab:tools runner/              # every download checked by hash
sudo sh runner/lab.sh sandbox-runtime /tmp/out          # or nono, codex, landrun, tartaros
python3 runner/report.py /tmp/out results/$(date +%F)-mine
```

`lab.sh` recibe ids de contracts después de la carpeta de salida para correr solo esos.
`/tmp/out/<sandbox>.json` guarda cada caso: qué corrió cada fase, su exit status, su salida
y el efecto observado. `report.py` lo convierte en una carpeta de run como las publicadas.

## 3. Los contracts que necesitan un witness host {#3-the-contracts-that-need-a-witness-host}

Los contracts de credenciales enmascaradas llegan a un witness por nombre a través del proxy
del sandbox, en un segundo host de la red del lab ([Witnesses](../concepts/witnesses.md)):

```sh
sudo sh runner/lab-witness.sh up
sudo SC_WITNESS=1 sh runner/lab.sh tartaros /tmp/out
sudo sh runner/lab-witness.sh down
```

Sin él, esos contracts quedan `not-applicable`.
