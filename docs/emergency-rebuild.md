# Emergency rebuild

For a critical, exploitable vulnerability:

1. Identify affected supported digests and open an emergency change.
2. Update the upstream digest or package input and record the vulnerability.
3. Run policy validation, image tests, scan, SBOM, provenance, and signing.
4. Publish a new immutable build tag and promote that digest through each
   environment.
5. Notify consumers and retain the superseded digest for rollback and audit.

Do not overwrite an existing immutable tag or rebuild separately per
environment.
