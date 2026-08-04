#!/usr/bin/env bash
set -euo pipefail

errors=0
while IFS= read -r dockerfile; do
  if ! grep -Eq '^# syntax=docker/dockerfile:1' "$dockerfile"; then
    echo "ERROR: $dockerfile must declare Dockerfile syntax" >&2
    errors=$((errors + 1))
  fi
  for label in title description version created revision source; do
    grep -Eq "org.opencontainers.image.${label}" "$dockerfile" || {
      echo "ERROR: $dockerfile is missing OCI label ${label}" >&2
      errors=$((errors + 1))
    }
  done
  grep -Eq '^USER [1-9][0-9]*:[1-9][0-9]*$' "$dockerfile" || {
    echo "ERROR: $dockerfile must finish with a numeric non-root USER" >&2
    errors=$((errors + 1))
  }
done < <(find images -type f -name Dockerfile -print | sort)

if (( errors > 0 )); then exit 1; fi
echo "Dockerfile policy is valid."
