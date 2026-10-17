# A local lab host with Lima

How the [2026-10-16 run](../../results/2026-10-16/README.md) was measured: a
disposable Ubuntu 24.04 VM on the operator's own machine, with nothing mounted
from it. Lima's default template mounts your home directory; `sc-lab.yaml` sets
`mounts: []` and turns off port forwarding.

Docker Desktop is not enough: its kernel is built without Landlock
(`CONFIG_SECURITY_LANDLOCK is not set`), so nono and landrun cannot be measured
there, and landrun's `--best-effort` would run with no confinement at all.

```sh
limactl create --name sc-lab --tty=false runner/lima/sc-lab.yaml
limactl start sc-lab
# the kernel of the published runs, and Docker
limactl shell sc-lab -- sudo sh -c 'apt-get update && apt-get install -y \
  linux-image-6.8.0-146-generic linux-modules-6.8.0-146-generic docker.io'
limactl stop sc-lab && limactl start sc-lab      # boots 6.8.0-146
# copy a commit in, build the image, load the AppArmor profile, measure
git archive --prefix=sc/ HEAD -o /tmp/sc.tar && limactl copy /tmp/sc.tar sc-lab:/tmp/
limactl shell sc-lab -- sh -c 'cd && tar xf /tmp/sc.tar && cd sc \
  && sudo docker build -t sc-lab:tools runner/ \
  && sudo apparmor_parser -r -W runner/sc-lab.apparmor \
  && for s in sandbox-runtime nono codex landrun; do \
       sudo SC_COMMIT=<commit> sh runner/lab.sh $s $HOME/out; done'
# bring $HOME/out back, then
limactl delete sc-lab
```

This is level B of a lab (a disposable VM with a known kernel), adequate for
these contracts: each attack tries to leave the sandbox inside the guest. Tests
that try to escape a kernel or a hypervisor need a dedicated machine.
