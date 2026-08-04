# Publishing with GitHub Actions

Images are published to GitHub Container Registry (GHCR) by the manually
triggered `Publish container image` workflow. The workflow requires a
verified upstream digest, builds both `linux/amd64` and `linux/arm64`, pushes
an immutable tag, and emits SBOM and provenance attestations.

From the GitHub Actions tab:

1. Select **Publish container image**.
2. Choose **Run workflow**.
3. Select the image from the `metadata` dropdown.
4. Start the workflow. It generates an immutable UTC tag automatically using
   the image version and run timestamp, for example `11-20260804-224517`.
5. Review the published digest before promoting it.

The workflow uses the repository `GITHUB_TOKEN`; it needs `packages: write`,
`attestations: write`, and `id-token: write` permissions. Pull requests only
validate and never publish.
