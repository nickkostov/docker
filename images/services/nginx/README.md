# Nginx service

Organization-approved rebuild of the pinned official Nginx image. It is
published under the organization registry with controlled tags, OCI metadata,
SBOM, and provenance.

The Dockerfile applies the repository's numeric non-root-user policy. Validate
the Nginx listen port, PID path, cache, and temporary directories before using
the image with a production configuration.
