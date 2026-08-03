# Architecture

This repository is the control plane for organization-approved container
images. Image definitions are discovered from `images/**/image.yaml`; the
Dockerfile and structure-test configuration beside each definition are the
build and test inputs.

The flow is:

```text
metadata + pinned upstream -> policy validation -> multi-platform build
                                      -> tests -> scan/SBOM/provenance/sign
                                      -> immutable candidate -> promotion
```

Images are built once and promoted by digest. Moving convenience tags are
catalog metadata, not deployment identity. Application deployments should
record `name:tag@sha256:digest`.

Runtime images and builder images are separate. Production variants use an
explicit numeric non-root user and contain no credentials or organization
certificates. CI is responsible for policy checks; the registry is the source
of published artifacts and attestations.
