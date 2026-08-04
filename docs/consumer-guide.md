# Consumer guide

```dockerfile
FROM ghcr.io/nickkostov/base-images/java:21@sha256:<approved-digest>

COPY --chown=10001:10001 target/application.jar /app/application.jar
ENTRYPOINT ["java", "-jar", "/app/application.jar"]
```

Consumers own application dependencies and testing. The platform team owns
base-image patching, rebuilds, signing, and lifecycle notices.
