# Image metadata

Every image definition is stored in `images/**/image.yaml` and validated against
`schemas/image.schema.json`. Repository metadata uses block-style YAML for
nested mappings and lists so definitions remain readable and produce useful
line-level diffs.

Repeated image families may instead use one family-level `images.yaml` with a
`versions` mapping. Builder validates and expands that source into the same
per-version metadata shape. Alpine is the first collection-based family; see
[Builder CLI](builder.md).

Each definition records:

- image identity, variant, version, description, and owners;
- upstream image, tag, and verified digest;
- supported platforms and destination registry repository;
- numeric runtime UID and GID;
- lifecycle status and support end date;
- vulnerability, signature, SBOM, and provenance requirements;
- supported publishing tags.

Runtime definitions additionally require an approved organization base image
and its published digest. Service definitions describe custom or rebuilt images
that are approved for direct organizational use.

Values such as `sha256:REPLACE_WITH_VERIFIED_DIGEST` are explicit incomplete
metadata, not valid release digests. They intentionally fail metadata and schema
validation until replaced with a registry-verified SHA-256 digest.
