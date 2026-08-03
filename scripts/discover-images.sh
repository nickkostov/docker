#!/usr/bin/env bash
set -euo pipefail

find images -type f -name image.yaml -print | sort
