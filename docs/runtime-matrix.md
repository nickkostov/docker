# Runtime image matrix

Runtime images are selected by three dimensions:

```text
runtime + runtime version + organization OS + OS version
```

For Node.js, the supported matrix is maintained in
`images/runtimes/node/versions.yaml`. Only combinations listed there may be
published. This prevents an uncontrolled multiplication of images and keeps
Alpine/musl and Ubuntu/glibc builds explicit.

Example image identities:

```text
ghcr.io/nickkostov/base-images/node:22-alpine3.21
ghcr.io/nickkostov/base-images/node:22-ubuntu24.04
ghcr.io/nickkostov/base-images/node:24-alpine3.23
```

Each variant requires both the organization OS digest and the upstream runtime
digest before it can be built. Java and Python remain on their existing
version definitions until their supported OS/version matrices are selected.
