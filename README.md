# Organization Container Images

Central source for approved, hardened Docker base and runtime images.

The catalog is metadata-driven. Each image keeps its Dockerfile, lifecycle,
security requirements, owners, and pinned upstream digest together under
`images/`. CI validates metadata and Dockerfile policy before an image can be
published.

## Repository layout

- `images/` - approved image definitions
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

An upstream digest must be replaced with a registry-verified value before an
image is buildable or publishable. Production consumers should pin the
published image by digest.
