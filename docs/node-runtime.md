# Node.js runtime images

Node.js uses a matrix-based image definition. A published variant is selected
by Node.js version, organization operating system, and operating-system
version:

```text
node/<node-version>/<base-os>/<base-version>
```

Examples:

```text
node/22/alpine/3.21
node/22/ubuntu/24.04
node/24/alpine/3.23
node/24/ubuntu/26.04
```

These are logical combinations rather than physical directories. The active
implementation consists of:

- `images/runtimes/node/versions.yaml` — supported combinations and digests;
- `images/runtimes/node/Dockerfile` — shared runtime Dockerfile;
- `.github/workflows/publish-runtime.yml` — selection and publishing workflow.

## Selection

The **Publish Runtime Image** workflow accepts four inputs:

```text
runtime + Node.js version + base OS + base OS version
```

For example:

```text
runtime: node
version: 22
base_os: ubuntu
base_version: 24.04
```

The workflow reads the corresponding entry from `versions.yaml`. Each entry
must provide:

- the approved organization OS repository and published digest;
- the official Node.js upstream image and tag;
- the verified upstream Node.js manifest digest.

The workflow rejects a selection when either digest is missing, malformed, or
still contains a placeholder. It also authenticates to GHCR and verifies that
the selected organization OS image exists before starting the build.

## Build flow

The shared Dockerfile uses three stages:

```dockerfile
FROM ${BASE_IMAGE} AS approved-os
FROM ${UPSTREAM_IMAGE} AS upstream-runtime
FROM approved-os

COPY --from=upstream-runtime /usr/local /usr/local
```

`BASE_IMAGE` is the digest-pinned organization Alpine or Ubuntu image.
`UPSTREAM_IMAGE` is the digest-pinned official Node.js image. The final image
starts from the approved organization OS and copies the Node.js runtime payload
from `/usr/local` in the official image.

The final stage creates the numeric non-root user `10001:10001`, sets
`/app` as the working directory, and contains no application source code.

Alpine variants use matching Alpine Node.js upstream images so the runtime is
compatible with musl. Ubuntu variants currently copy from the
`bookworm-slim` Node.js image and therefore use the glibc runtime payload.

## Published tags

A Node.js 22 build on Ubuntu 24.04 publishes two tags pointing to the same
image digest:

```text
ghcr.io/nickkostov/base-images/node:22-ubuntu24.04-<UTC timestamp>
ghcr.io/nickkostov/base-images/node:22-ubuntu24.04
```

The timestamped tag identifies an immutable organization build. The shorter
variant tag moves to the newest approved build for that exact combination.
Production deployments should still pin the published digest.

## Current limitations

The matrix cannot publish entries that still contain
`REPLACE_WITH_VERIFIED_DIGEST` or `REPLACE_WITH_PUBLISHED_BASE_DIGEST`.
Ubuntu organization-base digests are recorded, while Node.js upstream matrix
digests and Alpine organization-base digests must still be completed.
