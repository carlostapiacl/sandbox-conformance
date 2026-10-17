#!/bin/sh
# Run one sandbox's measurement in a throwaway container on a Linux lab host.
#   runner/lab.sh <sandbox> <outdir> [contract ids...]
# Needs: the sc-lab:tools image (runner/Dockerfile) and the `sc-lab` AppArmor
# profile loaded (runner/sc-lab.apparmor): it only adds `userns`, so the
# sandboxes can create user namespaces on Ubuntu 24.04 without touching the
# host-wide kernel.apparmor_restrict_unprivileged_userns sysctl.
set -eu
SANDBOX=$1; OUT=$2; shift 2
HERE=$(cd "$(dirname "$0")/.." && pwd)
mkdir -p "$OUT"
OPTS="--init --cpus 1 --memory 1g --pids-limit 512 --security-opt seccomp=unconfined --security-opt apparmor=sc-lab --security-opt systempaths=unconfined"
# The commit being measured: from git when the tree is a checkout, else from SC_COMMIT.
COMMIT=${SC_COMMIT:-$(git -C "$HERE" rev-parse HEAD 2>/dev/null || true)}
docker run --rm --name "sc-$SANDBOX" $OPTS \
  -e SC_COMMIT="$COMMIT" \
  -e SC_CONTAINER_STAMP="docker $(docker version --format '{{.Server.Version}}'); $OPTS; image sc-lab:tools $(docker image inspect -f '{{.Id}}' sc-lab:tools)" \
  -v "$HERE/runner:/lab/runner:ro" -v "$HERE/contracts:/lab/contracts:ro" -v "$OUT:/out" \
  sc-lab:tools python3 /lab/runner/run.py --sandbox "$SANDBOX" --contracts /lab/contracts \
  --out "/out/$SANDBOX.json" ${1:+--only "$@"}
