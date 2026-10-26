# Run the lab on Linux

The published runs used a disposable Ubuntu 24.04 VM with kernel 6.8 (Landlock ABI 4),
created with Lima on the operator's machine with nothing mounted from it. Docker Desktop
is not enough: its kernel has no Landlock, so Landlock sandboxes cannot be measured there
and one of them would run with no confinement at all.

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

Each case runs in a `--rm` container whose options are recorded in the result's host
stamp, with one CPU, 1 GiB and 512 processes. The AppArmor profile only adds user
namespaces for that container, so the host-wide setting stays as it was. After a reboot
it has to be loaded again.

Add `SC_WITNESS=1` and `runner/lab-witness.sh up` for the contracts that need a
[witness host](../concepts/witnesses.md#the-witness-host). The VM's own notes are in
[repo:runner/lima/README.md](repo:runner/lima/README.md).
