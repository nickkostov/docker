# Context Cache

## Goal
Maintain compact YAML-driven definitions that generate reproducible base,
runtime, and service Docker images locally and in GitHub Actions.

## Stack
Python 3.10+, Click, PyYAML, Jinja2, Docker/Buildx, YAML metadata, GitHub
Actions, GHCR, SBOM, and provenance attestations.

## Files
`src/image_builder/` implements collection expansion, strict Jinja rendering,
safe context-file copying, local builds, and CI publishing. Image families use
`images.yaml` plus `Dockerfile.template`. `images/services/action-runners/`
also declares `run.sh` through `context_files`. Base publishing is in
`.github/workflows/publish-builder-images.yml`; service publishing is in
`.github/workflows/publish-builder-services.yml`. `docs/builder.md` and
`docs/publishing.md` document usage.

## Rules
Pin every `FROM` image by verified digest. Keep configuration visible in YAML;
global user and `params` values may be overridden per version. Generated
Dockerfiles and temporary contexts are derived output. Context files must be
relative, remain inside the collection directory, and cannot replace the
generated Dockerfile. Never bake runner registration tokens or other secrets
into images. Production deployments use published digests.

## Decisions
Builder is independent of inventory tooling. Jinja templates receive flattened
metadata and the `image` namespace. `builder generate` writes inspectable
contexts; `builder build` uses temporary contexts; `--ci` performs
multi-platform Buildx pushes with timestamped and moving tags, SBOM, and
provenance. Actions Runner is a service built from approved Ubuntu images;
`runner_version` is YAML-configured and `run.sh` is copied into its generated
context. Base and service images use separate manually triggered workflows.
