# Architecture

This repository is the control plane for organization-approved container
images. It intentionally supports only three image classes:

- `base` — operating-system foundations such as Debian, Ubuntu, and Alpine;
- `runtime` — language runtimes such as Node.js, Java, and Python;
- `service` — custom or rebuilt images approved for direct organizational use.

Image definitions are discovered from `images/**/image.yaml`; the Dockerfile
and structure-test configuration beside each definition are the build and test
inputs.

The flow is:

```text
metadata + pinned upstream -> policy validation -> multi-platform build
                                      -> tests -> scan/SBOM/provenance/sign
                                      -> immutable candidate -> promotion
```

Images are built once and promoted by digest. Moving convenience tags are
catalog metadata, not deployment identity. Application deployments should
record `name:tag@sha256:digest`.

Framework-specific builders, generic tool images, and separate builder-image
categories are outside this repository architecture. Production variants use
an explicit numeric non-root user and contain no credentials or organization
certificates. CI is responsible for policy checks; the registry is the source
of published artifacts and attestations.
