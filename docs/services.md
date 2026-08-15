# Service images

Service images are organization-approved custom or rebuilt images intended for
direct use. A service may be a thin rebuild of a pinned upstream image, such as
Nginx, or a more customized image, such as the GitHub Actions Runner.

The purpose of rebuilding an upstream service is to publish it under the
organization registry with a verified upstream digest, organization metadata,
security policy, SBOM, provenance, and controlled tags. A service Dockerfile
does not need to make extensive changes: an approved rebuild of an otherwise
unchanged upstream image is a valid service.

Examples include:

- Web servers: Nginx, Apache, Caddy
- Databases: PostgreSQL, MySQL, Redis
- Message brokers: RabbitMQ, Kafka
- Proxies: HAProxy, Traefik
- Observability components: Prometheus and exporters
- CI infrastructure: GitHub Actions self-hosted runners

The complete image taxonomy is:

```text
base       Debian, Ubuntu, Alpine, BusyBox
runtime    Java, Node.js, Python
service    Nginx, databases, brokers, proxies, Actions runners
```

The current Nginx service is published through the dedicated **Publish service
image** workflow. Additional web servers, databases, brokers, proxies, and
observability services can be added there without cluttering the base-image
workflow.

The GitHub Actions runner is also published by the dedicated service workflow. It
is available on Ubuntu 22.04, 24.04, and 26.04 and starts the runner through
`run.sh`; registration secrets are supplied only at runtime.
