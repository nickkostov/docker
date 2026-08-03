# Onboarding

1. Select an image from `catalog/images.yaml` and confirm its lifecycle state.
2. Use the approved repository and a digest-pinned tag in the application
   Dockerfile.
3. Run the reusable `use-approved-base-image.yml` workflow in the application
   repository.
4. Test the application against the candidate digest before promotion.
5. Record the digest in deployment configuration and subscribe to image
   upgrade notifications.

Requests for a new runtime must include its owner, support window, upstream
license, non-root behavior, platforms, and rollback plan.
