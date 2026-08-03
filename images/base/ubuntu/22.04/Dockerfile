# syntax=docker/dockerfile:1
ARG UPSTREAM_IMAGE
FROM ${UPSTREAM_IMAGE}
ARG BUILD_DATE
ARG REVISION
ARG VERSION
LABEL org.opencontainers.image.title="Organization Ubuntu Base" org.opencontainers.image.description="Approved Ubuntu base image" org.opencontainers.image.version="${VERSION}" org.opencontainers.image.created="${BUILD_DATE}" org.opencontainers.image.revision="${REVISION}" org.opencontainers.image.source="https://github.com/example-org/platform-container-images"
RUN groupadd --gid 10001 app && useradd --uid 10001 --gid 10001 --no-create-home --home-dir /nonexistent --shell /usr/sbin/nologin app
WORKDIR /app
USER 10001:10001
