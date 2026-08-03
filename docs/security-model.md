# Security model

Every pull request validates metadata, Dockerfile policy, non-root execution,
and image tests. Publication additionally requires vulnerability scanning,
SBOM, provenance, and a signature attached to the registry digest.

Only upstreams listed in `policies/allowed-upstreams.yaml` are permitted.
Critical vulnerabilities fail publication; fixable high vulnerabilities also
fail. Exceptions require an owner, justification, compensating control, and
an expiration date. Credentials and certificates must never be copied into
image layers.
