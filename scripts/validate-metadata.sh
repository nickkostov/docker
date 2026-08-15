#!/usr/bin/env bash
set -euo pipefail

errors=0
while IFS= read -r metadata; do
  image_dir=${metadata%/image.yaml}
  for required in name variant version upstream registry user lifecycle security tags; do
    if ! grep -Eq "^${required}:" "$metadata"; then
      echo "ERROR: $metadata is missing top-level key: $required" >&2
      errors=$((errors + 1))
    fi
  done
  if grep -Eq '^variant:[[:space:]]*runtime' "$metadata" && ! grep -Eq '^base:' "$metadata"; then
    echo "ERROR: $metadata runtime images must declare an approved base image" >&2
    errors=$((errors + 1))
  fi
  digest_count=0
  while IFS= read -r digest; do
    digest_count=$((digest_count + 1))
    if ! [[ "$digest" =~ ^sha256:[0-9a-f]{64}$ ]]; then
      echo "ERROR: $metadata contains an unverified digest: $digest" >&2
      errors=$((errors + 1))
    fi
  done < <(awk '$1 == "digest:" {print $2}' "$metadata")
  if (( digest_count == 0 )); then
    echo "ERROR: $metadata must contain at least one verified sha256 digest" >&2
    errors=$((errors + 1))
  fi
  if grep -Eq '(^|:) latest($|[[:space:]])' "$metadata"; then
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
