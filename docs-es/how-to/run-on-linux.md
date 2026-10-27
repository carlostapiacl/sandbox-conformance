# Correr el lab en Linux

Los runs publicados usaron una VM desechable con Ubuntu 24.04 y kernel 6.8 (Landlock ABI 4),
creada con Lima en la máquina del operador, sin nada montado desde ella. Docker Desktop no
basta: su kernel no tiene Landlock, así que ahí no se pueden medir los sandboxes basados en
Landlock y uno de ellos correría sin ningún confinamiento.

```sh
limactl create --name sc-lab --tty=false runner/lima/sc-lab.yaml
limactl start sc-lab
limactl shell sc-lab -- sudo sh -c 'apt-get update && apt-get install -y \
  linux-image-6.8.0-146-generic linux-modules-6.8.0-146-generic docker.io'
limactl stop sc-lab && limactl start sc-lab      # boots 6.8.0-146
git archive --prefix=sc/ HEAD -o /tmp/sc.tar && limactl copy /tmp/sc.tar sc-lab:/tmp/
limactl shell sc-lab -- sh -c 'cd && tar xf /tmp/sc.tar && cd sc \
  && sudo docker build -t sc-lab:tools runner/ \
  && sudo apparmor_parser -r -W runner/sc-lab.apparmor \
  && sudo SC_COMMIT=<commit> sh runner/lab.sh sandbox-runtime $HOME/out'
```

Cada caso corre en un contenedor `--rm` cuyas opciones quedan registradas en el host stamp
del resultado, con una CPU, 1 GiB y 512 procesos. El profile de AppArmor solo agrega user
namespaces para ese contenedor, así que la configuración de todo el host queda como estaba.
Después de reiniciar hay que cargarlo de nuevo.

Agrega `SC_WITNESS=1` y `runner/lab-witness.sh up` para los contracts que necesitan un
[witness host](../concepts/witnesses.md#the-witness-host). Las notas de la VM están en
[`runner/lima/README.md`](repo:runner/lima/README.md).
