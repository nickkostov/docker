# syntax=docker/dockerfile:1
# check=skip=InvalidDefaultArgInFrom
ARG UPSTREAM_IMAGE
FROM ${UPSTREAM_IMAGE}

ARG RUNNER_VERSION=2.329.0
ARG TARGETARCH
ARG BUILD_DATE
ARG REVISION
ARG VERSION

LABEL org.opencontainers.image.title="Organization GitHub Actions Runner" \
      org.opencontainers.image.description="GitHub Actions self-hosted runner on Ubuntu 24.04" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.revision="${REVISION}" \
      org.opencontainers.image.source="https://github.com/nickkostov/docker"

ENV DEBIAN_FRONTEND=noninteractive

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
    jq \
    sudo \
    tar \
    gzip \
    unzip \
  && rm -rf /var/lib/apt/lists/*

RUN getent group 1000 >/dev/null || groupadd --gid 1000 runner \
  && useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash runner \
  && usermod -aG sudo runner

WORKDIR /home/runner

RUN case "${TARGETARCH}" in \
      amd64) runner_arch="x64" ;; \
      arm64) runner_arch="arm64" ;; \
      *) echo "Unsupported architecture: ${TARGETARCH}"; exit 1 ;; \
    esac \
  && curl -fsSL \
     "https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-${runner_arch}-${RUNNER_VERSION}.tar.gz" \
     -o runner.tar.gz \
  && tar -xzf runner.tar.gz \
  && rm runner.tar.gz \
  && mv run.sh runner-entrypoint.sh \
  && ./bin/installdependencies.sh \
  && chown -R 1000:1000 /home/runner

COPY --chown=1000:1000 run.sh /home/runner/run.sh
RUN chmod +x /home/runner/run.sh

USER 1000:1000
