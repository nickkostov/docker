# Versioning

Published images use three tag classes:

- `runtime.patch-builddate` - immutable organization build
- `runtime.patch` - latest rebuild for an upstream patch
- `runtime` and `runtime-stable` - approved moving aliases

Do not publish `latest`. Production deployments must use a digest. Promotion
must move the same digest between environments; it must not rebuild the image.
