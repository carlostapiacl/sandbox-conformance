#!/bin/sh
# The lab's witness host, for contracts that `require = ["witness-host"]`.
#   runner/lab-witness.sh up | down
# A Docker network on TEST-NET-2 (198.51.100.0/24: no SSRF guard treats it as
# internal) and a second container on it that forwards 80 and 443 to the runner's
# container, where the witness servers listen. A sandbox whose egress guard refuses
# its own host's addresses reaches the witness here, as it would a remote host.
# Run the measurement with:
#   --network sc-lab-testnet --ip 198.51.100.10 -e SC_WITNESS_IP=198.51.100.200
set -eu
NET=sc-lab-testnet RUNNER_IP=198.51.100.10 WITNESS_IP=198.51.100.200
IMAGE=${SC_IMAGE:-sc-lab:tools}
case "${1:-}" in
up)
  docker network inspect "$NET" >/dev/null 2>&1 || docker network create --subnet 198.51.100.0/24 "$NET" >/dev/null
  docker rm -f sc-witness >/dev/null 2>&1 || true
  docker run -d --rm --name sc-witness --network "$NET" --ip "$WITNESS_IP" "$IMAGE" sh -c \
    "socat TCP-LISTEN:443,fork,reuseaddr TCP:$RUNNER_IP:443 & socat TCP-LISTEN:80,fork,reuseaddr TCP:$RUNNER_IP:80 & wait" >/dev/null
  echo "witness host $WITNESS_IP -> $RUNNER_IP" ;;
down)
  docker rm -f sc-witness >/dev/null 2>&1 || true
  docker network rm "$NET" >/dev/null 2>&1 || true ;;
*) echo "usage: $0 up|down" >&2; exit 2 ;;
esac
