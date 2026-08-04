# Node.js runtime matrix

Node.js runtime images are selected by runtime version and organization OS
variant. The matrix intentionally contains only tested combinations:

```text
node/<version>/<os>/<os-version>
```

Examples:

```text
node/22/alpine/3.21
node/22/ubuntu/24.04
node/24/alpine/3.23
```

The build uses the approved organization OS digest as the final image base and
copies the matching musl or glibc runtime payload from the pinned upstream
Node.js image. It publishes a timestamped variant tag and a moving variant
tag, for example `node:22-alpine3.21`.
