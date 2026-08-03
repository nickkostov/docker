#!/usr/bin/env bash
set -euo pipefail

image=${1:?usage: scripts/generate-sbom.sh image output}
out=${2:?usage: scripts/generate-sbom.sh image output}
command -v syft >/dev/null || { echo "syft is required for SBOM generation" >&2; exit 1; }
syft "$image" -o "spdx-json=$out"
