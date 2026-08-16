# Organization Container Images

Central source for approved base, runtime, and service container images.

The catalog is metadata-driven. Each image keeps its Dockerfile, lifecycle,
security requirements, owners, and pinned upstream digest together under
`images/`. CI validates metadata and Dockerfile policy before an image can be
published.

Alpine also demonstrates the lightweight collection model: one authored
`images.yaml` can generate all versioned build contexts locally or build them
directly from temporary contexts in CI.

## Repository layout

- `images/base/` - approved operating-system foundations
- `images/runtimes/` - approved language runtimes on organization base images
- `images/services/` - approved custom or rebuilt images used as services
- `catalog/` - published image inventory and support matrix
- `policies/` - security, lifecycle, upstream, and license rules
- `schemas/` - metadata schemas
- `scripts/` - discovery and validation tooling
- `.github/workflows/` - pull-request, rebuild, and reusable workflows
- `docs/` - architecture, security, versioning, and consumer guidance

## Local validation

```sh
make validate
```

## Repository inventory CLI

Install the `inspectur` helper in a local virtual environment:

```sh
make inspectur-install
source .venv/bin/activate
inspectur --help
```

Running `inspectur` without a command displays the complete image inventory.
See [the Inspectur guide](docs/inspectur.md) for filters, readiness checks, and
runtime matrix views.

## Builder CLI

Install Builder and preview an Alpine build:

```sh
make builder-install
source .venv/bin/activate
builder build images/base/alpine/images.yaml --version 3.24 --dry-run
```

Use `builder generate` when you want to inspect materialized Dockerfiles, or
`builder build` to build from temporary contexts without adding generated files
to the repository. See [the Builder guide](docs/builder.md).

An upstream digest must be replaced with a registry-verified value before an
image is buildable or publishable. Production consumers should pin the
published image by digest.
