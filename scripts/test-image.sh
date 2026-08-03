#!/usr/bin/env bash
set -euo pipefail

image=${1:?usage: scripts/test-image.sh image}
uid=${2:-10001}
actual_uid=$(docker image inspect --format '{{.Config.User}}' "$image")
[[ "$actual_uid" == "$uid:$uid" ]] || { echo "Expected non-root user $uid:$uid, found $actual_uid" >&2; exit 1; }
docker run --rm --entrypoint /bin/sh "$image" -c 'id -u; test "$(id -u)" -ne 0'
