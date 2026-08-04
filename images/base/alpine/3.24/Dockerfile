# syntax=docker/dockerfile:1
ARG UPSTREAM_IMAGE
FROM ${UPSTREAM_IMAGE}
ARG BUILD_DATE
ARG REVISION
ARG VERSION
LABEL org.opencontainers.image.title="Organization Alpine Base" org.opencontainers.image.description="Approved Alpine Linux base image" org.opencontainers.image.version="${VERSION}" org.opencontainers.image.created="${BUILD_DATE}" org.opencontainers.image.revision="${REVISION}" org.opencontainers.image.source="https://github.com/example-org/platform-container-images"
RUN addgroup -S -g 10001 app && adduser -S -D -H -u 10001 -G app -s /sbin/nologin app
WORKDIR /app
USER 10001:10001
