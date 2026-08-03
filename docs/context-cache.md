# Context Cache

## Goal
Maintain approved, reproducible, signed Docker base and runtime images.

## Stack
Dockerfiles, YAML metadata, JSON Schema, shell validation, GitHub Actions,
OCI registry artifacts, SBOM/provenance/signature tooling.

## Files
`images/` definitions, including Debian 11 bullseye, Debian 12 bookworm, and
Debian 13 trixie plus Ubuntu 20.04, 22.04, 24.04, and 26.04; `catalog/`
inventory; `policies/` controls;
`schemas/` metadata contract; `scripts/` local automation; `docs/` operating
model; `.github/workflows/` CI.

## Rules
Pin upstreams by verified digest. Use numeric non-root users. Keep builders
separate from runtimes. Never use `latest`, bake secrets into layers, or
rebuild during promotion. Production references record image digests.

## Decisions
Use one central catalog, metadata-driven discovery, immutable build tags,
expiring vulnerability exceptions, and build-once/promote-by-digest.
