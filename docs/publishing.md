# Publishing with GitHub Actions

Images are published to GitHub Container Registry (GHCR) by manually triggered
GitHub Actions workflows. Each workflow requires a
verified upstream digest, builds both `linux/amd64` and `linux/arm64`, pushes
an immutable tag, and emits SBOM and provenance attestations.

The separate **Publish Builder base images** workflow handles the collection
model. Select `alpine` or `busybox` from its dropdown and optionally enter one
version. Leaving the version blank validates and publishes every version listed
in the selected `images.yaml`. The workflow resolves only fixed repository
paths, installs Builder, validates the collection, and runs `builder build
--ci` after Buildx and GHCR authentication are configured.

From the GitHub Actions tab:

1. Select one of the three workflows: **Publish base image**, **Publish runtime image**, or **Publish service image**.
2. Choose **Run workflow**.
3. Select the image-specific options and version.
4. Start the workflow. It resolves the matching `image.yaml` and generates an immutable UTC tag automatically using
   the image version and run timestamp, for example `11-20260804-224517`.
   The same build also updates the moving major/version tag, such as `11`.
5. Review the published digest before promoting it.

The workflow uses the repository `GITHUB_TOKEN`; it needs `packages: write`,
`attestations: write`, and `id-token: write` permissions. Pull requests only
validate and never publish.

Alpine publishing is resolved dynamically from
`images/base/alpine/images.yaml`. The workflow installs the Python `builder`
command and runs `builder build ... --ci`; therefore adding an Alpine version
does not require another committed Dockerfile or a hard-coded workflow case.
Builder creates temporary contexts, pushes the declared tags, and asks Buildx
for SBOM and provenance attestations.

Each publication creates two tags from the same digest. The selected image
type is routed to its dedicated workflow:

Runtime images are handled by the separate **Publish runtime image** workflow.
The current workflow supports the Node.js Alpine and Ubuntu matrix. It verifies
that the selected organization OS digest exists in GHCR before starting the
runtime build and fails when either the OS or upstream runtime digest is not
recorded.

Services are handled by **Publish service image**. It currently supports Nginx
and the Ubuntu 22.04, 24.04, and 26.04 Actions Runner variants.

```text
ghcr.io/nickkostov/base-images/ubuntu:20.04-20260804-224517
ghcr.io/nickkostov/base-images/ubuntu:20.04
```

The timestamped tag is the immutable organization build reference. The
version-only tag is intentionally mutable and points to the newest approved
build for that version. Production deployments should use the digest from the
timestamped build rather than relying only on the moving tag.
