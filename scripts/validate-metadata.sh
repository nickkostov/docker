#!/usr/bin/env bash
set -euo pipefail

errors=0
while IFS= read -r metadata; do
  image_dir=${metadata%/image.yaml}
  for required in name variant version upstream registry user lifecycle security tags; do
    if ! rg -q "^${required}:" "$metadata"; then
      echo "ERROR: $metadata is missing top-level key: $required" >&2
      errors=$((errors + 1))
    fi
  done
  if ! rg -q '^  digest: sha256:[0-9a-f]{64}$' "$metadata"; then
    echo "ERROR: $metadata must contain a verified sha256 digest" >&2
    errors=$((errors + 1))
  fi
  if rg -q '(^|:) latest($|[[:space:]])' "$metadata"; then
    echo "ERROR: $metadata uses forbidden latest tag" >&2
    errors=$((errors + 1))
  fi
  for sibling in Dockerfile README.md; do
    test -f "$image_dir/$sibling" || { echo "ERROR: missing $image_dir/$sibling" >&2; errors=$((errors + 1)); }
  done
done < <(scripts/discover-images.sh)

if (( errors > 0 )); then
  exit 1
fi
echo "Metadata structure is valid."
