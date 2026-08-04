# Publishing with GitHub Actions

Images are published to GitHub Container Registry (GHCR) by the manually
triggered `Publish container image` workflow. The workflow requires a
verified upstream digest, builds both `linux/amd64` and `linux/arm64`, pushes
an immutable tag, and emits SBOM and provenance attestations.

From the GitHub Actions tab:

1. Select one of the three workflows: **Publish base image**, **Publish runtime image**, or **Publish framework image**.
2. Choose **Run workflow**.
3. Select the image-specific options and version.
4. Start the workflow. It resolves the matching `image.yaml` and generates an immutable UTC tag automatically using
   the image version and run timestamp, for example `11-20260804-224517`.
   The same build also updates the moving major/version tag, such as `11`.
5. Review the published digest before promoting it.

The workflow uses the repository `GITHUB_TOKEN`; it needs `packages: write`,
`attestations: write`, and `id-token: write` permissions. Pull requests only
validate and never publish.

Each publication creates two tags from the same digest. The selected image
type is routed to its dedicated workflow:

Runtime images are handled by the separate **Publish runtime image** workflow.
It verifies that the selected organization OS digest exists in GHCR before
starting the runtime build. The current supported dependency is Debian 13;
the runtime workflow fails if that OS image has not been published and its
digest has not been recorded in the runtime `image.yaml`.

```text
ghcr.io/nickkostov/base-images/ubuntu:20.04-20260804-224517
ghcr.io/nickkostov/base-images/ubuntu:20.04
```

The timestamped tag is the immutable organization build reference. The
version-only tag is intentionally mutable and points to the newest approved
build for that version. Production deployments should use the digest from the
timestamped build rather than relying only on the moving tag.
