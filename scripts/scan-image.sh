#!/usr/bin/env bash
set -euo pipefail

image=${1:?usage: scripts/scan-image.sh image}
command -v trivy >/dev/null || { echo "trivy is required for image scanning" >&2; exit 1; }
trivy image --severity CRITICAL,HIGH --ignore-unfixed --exit-code 1 "$image"
