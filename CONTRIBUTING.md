# Contributing

Image changes require metadata, Dockerfile, documentation, and policy review.
Run `make validate` before opening a pull request. Upstream digests must be
verified from the registry and recorded with the source tag. Do not add
credentials, certificates, or mutable `latest` references.
