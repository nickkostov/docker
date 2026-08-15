#!/usr/bin/env bash
set -euo pipefail

# Dispatch every currently supported workflow combination.
# Use --dry-run to print commands without dispatching them.

dry_run=false
if [[ "${1:-}" == "--dry-run" ]]; then
  dry_run=true
elif [[ $# -gt 0 ]]; then
  echo "Usage: $0 [--dry-run]" >&2
  exit 2
fi

command -v gh >/dev/null || {
  echo "gh CLI is required: https://cli.github.com/" >&2
  exit 1
}

dispatch() {
  local workflow=$1
  shift
  local -a args=(gh workflow run "$workflow")
  local input

  for input in "$@"; do
    args+=(--field "$input")
  done

  printf '%s' "${args[*]}"
  printf '\n'
  if [[ "$dry_run" == false ]]; then
    "${args[@]}"
  fi
}

echo "Dispatching base images"
for version in 3.21 3.22 3.23 3.24; do
  dispatch "Publish base image" image_type=base os=alpine version="$version"
done
for version in 1.37.0 1.38.0; do
  dispatch "Publish base image" image_type=base os=busybox version="$version"
done
for version in 11 12 13; do
  dispatch "Publish base image" image_type=base os=debian version="$version"
done
for version in 20.04 22.04 24.04 26.04; do
  dispatch "Publish base image" image_type=base os=ubuntu version="$version"
done

echo "Dispatching Node.js runtime matrix"
for version in 22 24; do
  for base_version in 3.21 3.22 3.23; do
    dispatch "Publish runtime image" runtime=node version="$version" base_os=alpine base_version="$base_version"
  done
  for base_version in 22.04 24.04 26.04; do
    dispatch "Publish runtime image" runtime=node version="$version" base_os=ubuntu base_version="$base_version"
  done
done

echo "Dispatching service images"
for version in 22.04 24.04 26.04; do
  dispatch "Publish service image" service=actions-runner version="$version"
done
dispatch "Publish service image" service=nginx version=current

echo "All workflow dispatches submitted. Use: gh run list"
