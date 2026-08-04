# Service images

Service images are ready-to-run infrastructure components. They are deployed
as services, rather than used as operating-system foundations, language
runtimes, or application build environments.

Examples include:

- Web servers: Nginx, Apache, Caddy
- Databases: PostgreSQL, MySQL, Redis
- Message brokers: RabbitMQ, Kafka
- Proxies: HAProxy, Traefik
- Observability components: Prometheus and exporters
- CI infrastructure: GitHub Actions self-hosted runners

The image categories are:

```text
base       Debian, Ubuntu, Alpine, BusyBox
runtime    Java, Node.js, Python
framework  React, Vite
service    Nginx, databases, brokers, proxies, Actions runners
```

For a frontend application, the usual flow is:

```text
React/Vite framework builder -> dist/ assets -> Nginx service image
```

The current Nginx service is published through the **Publish base image**
workflow because it is the only service currently in the catalog. When the
service catalog grows, it can move to a dedicated **Publish service image**
workflow without changing the image definitions.

The GitHub Actions runner is also published by the base/service workflow. It
is based on Ubuntu 24.04 and starts the runner through `run.sh`; registration
secrets are supplied only at runtime.
