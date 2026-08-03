#!/usr/bin/env bash
set -euo pipefail

metadata=${1:?usage: scripts/build-image.sh path/to/image.yaml [tag]}
tag=${2:-local}
dir=${metadata%/image.yaml}
upstream_image=$(yq -r '.upstream.image + "@" + .upstream.digest' "$metadata")
if [[ "$upstream_image" == *REPLACE_WITH_VERIFIED_DIGEST* ]]; then
  echo "Refusing to build: replace the unverified upstream digest in $metadata" >&2
  exit 1
fi
docker build --pull=false --build-arg "UPSTREAM_IMAGE=$upstream_image" --build-arg "VERSION=$(yq -r .version "$metadata")" --build-arg "BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ)" --build-arg "REVISION=$(git rev-parse HEAD)" -t "$tag" "$dir"
