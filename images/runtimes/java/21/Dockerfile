# syntax=docker/dockerfile:1
# check=skip=InvalidDefaultArgInFrom
ARG BASE_IMAGE
ARG UPSTREAM_IMAGE
FROM ${BASE_IMAGE} AS approved-os
FROM ${UPSTREAM_IMAGE} AS upstream-runtime
FROM approved-os
ARG BUILD_DATE
ARG REVISION
ARG VERSION
LABEL org.opencontainers.image.title="Organization Java Runtime" org.opencontainers.image.description="Approved Java runtime" org.opencontainers.image.version="${VERSION}" org.opencontainers.image.created="${BUILD_DATE}" org.opencontainers.image.revision="${REVISION}" org.opencontainers.image.source="https://github.com/nickkostov/docker"
USER root
COPY --from=upstream-runtime /opt/java/openjdk /opt/java/openjdk
ENV JAVA_HOME=/opt/java/openjdk PATH=/opt/java/openjdk/bin:$PATH
RUN groupadd --gid 10001 app && useradd --uid 10001 --gid 10001 --no-create-home --home-dir /nonexistent --shell /usr/sbin/nologin app
WORKDIR /app
USER 10001:10001
