# syntax=docker/dockerfile:1
# check=skip=InvalidDefaultArgInFrom
ARG UPSTREAM_IMAGE
FROM ${UPSTREAM_IMAGE}
ARG BUILD_DATE
ARG REVISION
ARG VERSION
LABEL org.opencontainers.image.title="Organization Python Runtime" org.opencontainers.image.description="Approved Python runtime" org.opencontainers.image.version="${VERSION}" org.opencontainers.image.created="${BUILD_DATE}" org.opencontainers.image.revision="${REVISION}" org.opencontainers.image.source="https://github.com/nickkostov/docker"
USER root
RUN groupadd --gid 10001 app && useradd --uid 10001 --gid 10001 --no-create-home --home-dir /nonexistent --shell /usr/sbin/nologin app
WORKDIR /app
USER 10001:10001
