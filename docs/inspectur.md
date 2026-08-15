# Inspectur repository CLI

`inspectur` discovers `images/**/image.yaml` definitions directly, so the CLI
inventory follows repository metadata without a separate manually maintained
data source. It uses Click for commands and Rich for terminal tables.

## Installation

From the repository root:

```sh
make inspectur-install
source .venv/bin/activate
inspectur --help
```

The command searches the current directory and its parents for `images/`. Use
`--root PATH` or `INSPECTUR_ROOT` when running it elsewhere.

## Commands

Display the complete inventory, grouped by image type:

```sh
inspectur
inspectur list
```

Filter the inventory:

```sh
inspectur list --variant base
inspectur list --status supported --readiness ready
inspectur list --name ubuntu --paths
inspectur list --variant service --references
inspectur list --readiness blocked
```

Inspect one definition:

```sh
inspectur show ubuntu 24.04
inspectur show actions-runner 2.336.0-ubuntu24.04
```

Display counts, verify required digests, or inspect runtime combinations:

```sh
inspectur summary
inspectur check
inspectur check --variant service
inspectur matrix
inspectur matrix --runtime node
```

`inspectur check` exits with status `1` when a selected definition still has a
placeholder or invalid required digest. A runtime is ready only when both its
approved base digest and upstream runtime digest are valid SHA-256 values.
