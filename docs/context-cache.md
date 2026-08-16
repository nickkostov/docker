# Context Cache

## Goal
Maintain approved, reproducible, signed base, runtime, and service images.

## Stack
Dockerfiles, YAML metadata, JSON Schema, shell validation, Python 3.10+, Click,
Rich, PyYAML, GitHub Actions, OCI registry artifacts, and
SBOM/provenance/signature tooling.

## Files
`images/` definitions, including Debian 11 bullseye, Debian 12 bookworm, and
Debian 13 trixie plus Ubuntu 20.04, 22.04, 24.04, and 26.04; `catalog/`
inventory; Alpine 3.21-3.24 and BusyBox 1.37.0-1.38.0 base definitions;
service definitions such as Nginx; `policies/` controls;
`schemas/` metadata contract; `scripts/` local automation; `docs/` operating
model; `.github/workflows/` CI; `src/inspectur/` metadata inventory CLI;
`src/image_builder/` collection expander/build CLI;
`images/base/alpine/images.yaml` compact Alpine source; `pyproject.toml`
installs `inspectur` and `builder`; `docs/node-runtime.md`
documents the Node matrix and shared Dockerfile flow.

## Rules
Pin upstreams by verified digest. Use numeric non-root users. Keep only base,
runtime, and service image classes. Never use `latest`, bake secrets into
layers, or rebuild during promotion. Production references record image digests. Keep
`image.yaml` nested mappings and lists in block style; validate them against
`schemas/image.schema.json`. Builder-generated files are derived output and are
not committed.

## Decisions
Use one central catalog, metadata-driven discovery, immutable build tags,
expiring vulnerability exceptions, and build-once/promote-by-digest. Inspectur
reads `images/**/image.yaml` directly and treats unresolved upstream or runtime
base digests as blocked. Builder expands Alpine's `versions` mapping, uses
temporary contexts by default, and enables Buildx push/SBOM/provenance with
`--ci`. Services are approved custom or rebuilt images for
direct use, including thin rebuilds of pinned upstreams such as Nginx.
