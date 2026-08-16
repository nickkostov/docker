# Builder CLI

`builder` turns one compact `images.yaml` collection into build contexts. It is
separate from `inspectur`: Inspectur reports inventory; Builder generates and
builds images.

Alpine is the first and intentionally smallest implementation. Its authored
source is `images/base/alpine/images.yaml`. Common fields live once at the top,
while `versions` contains the pinned upstream, lifecycle, platforms, target
registries, and tags that differ per version.

Dockerfile content is not embedded in Python. A collection selects its default
Jinja template relative to `images.yaml`:

```yaml
template: Dockerfile.template
```

Templates can use any expanded metadata field:

```dockerfile
FROM {{ upstream.image }}:{{ upstream.tag }}@{{ upstream.digest }}
RUN addgroup -S -g {{ user.gid }} {{ user.name }}
USER {{ user.uid }}:{{ user.gid }}
```

Jinja conditionals, loops, and filters are available. Builder passes standard
metadata plus custom top-level and per-version YAML fields to the template;
version fields override global fields. Missing template values fail validation
instead of silently producing an incomplete Dockerfile. The renderer is not
tied to Alpine or to a predefined Dockerfile layout.

## Install

From the repository root:

```sh
make builder-install
source .venv/bin/activate
builder --help
```

When the current directory contains `images.yaml`, the path can be omitted.

## Generate files locally

Generate every listed Alpine version under `generated/alpine/<version>`:

```sh
cd images/base/alpine
builder generate
```

Generate only one version elsewhere:

```sh
builder generate images/base/alpine/images.yaml \
  --version 3.24 \
  --output /tmp/container-contexts
```

Override the collection's template when needed:

```sh
builder generate images/base/alpine/images.yaml \
  --template path/to/Dockerfile.template
```

Each version directory contains only its generated `Dockerfile`. `images.yaml`
remains the single metadata source; Builder does not duplicate metadata or
generate READMEs inside version directories. Generated Dockerfiles are derived
output and do not need to be committed.

The generated `FROM` instruction is concrete and digest-pinned, for example:

```dockerfile
FROM docker.io/library/alpine:3.24@sha256:28bd5fe8b56d1bd048e5babf5b10710ebe0bae67db86916198a6eec434943f8b
```

The Dockerfile can therefore be built directly without supplying an
`UPSTREAM_IMAGE` build argument.

## User configuration

The complete global non-root user configuration is required once for the whole
image family:

```yaml
user:
  name: app
  uid: 10001
  gid: 10001
  workdir: /app
  shell: /sbin/nologin
```

A version may override one or more values by adding the same `user` mapping
inside that version. Builder accepts a safe Linux user name, positive numeric
UID/GID, and absolute work-directory and shell paths. It generates the Alpine
`addgroup`/`adduser`, `WORKDIR`, and numeric `USER` instructions from these
values. There are no fallback user values in the Python implementation.

## Build locally without generated repository files

Preview one build:

```sh
builder build images/base/alpine/images.yaml --version 3.24 --dry-run
```

Build it as `local/alpine:3.24`:

```sh
builder build images/base/alpine/images.yaml --version 3.24
```

Omit `--version` to build every version in the collection. Builder creates a
temporary context for each image and removes it after Docker exits.

## CI mode

CI uses the same command with `--ci`:

```sh
builder build images/base/alpine/images.yaml --version 3.24 --ci
```

CI mode runs `docker buildx build --push` for the declared platforms. It adds
the timestamped immutable tag plus every `additional_tags` entry, and requests
SBOM and provenance attestations. Registry authentication and Buildx setup must
already exist; the base-image GitHub Action performs those steps.

The repository's opinionated owner and security defaults are applied during
expansion. User configuration is not hidden in Python and must be declared in
`images.yaml`.
