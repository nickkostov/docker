from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, StrictUndefined, TemplateError


DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
IMAGE_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
PLATFORM_RE = re.compile(r"^linux/(amd64|arm64)$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
LIFECYCLE_STATUSES = {"experimental", "supported", "maintenance", "deprecated", "end-of-life"}
DEFAULT_OWNERS = ["platform-engineering"]
REQUIRED_USER_KEYS = {"name", "uid", "gid", "workdir", "shell"}
USER_NAME_RE = re.compile(r"^[a-z_][a-z0-9_-]*$")
ABSOLUTE_PATH_RE = re.compile(r"^/[A-Za-z0-9._/-]+$")
DEFAULT_SECURITY = {
    "maximum_severity": "high",
    "fail_on_fixable": True,
    "require_signature": True,
    "require_sbom": True,
    "require_provenance": True,
}


class BuilderError(Exception):
    """Raised when an image collection cannot be expanded safely."""


@dataclass(frozen=True)
class ExpandedImage:
    version: str
    metadata: dict[str, Any]
    repositories: tuple[str, ...]
    build_user: dict[str, Any]

    @property
    def upstream(self) -> str:
        upstream = self.metadata["upstream"]
        return f'{upstream["image"]}@{upstream["digest"]}'

    @property
    def repository(self) -> str:
        return str(self.metadata["registry"]["repository"])

    @property
    def platforms(self) -> list[str]:
        return [str(platform) for platform in self.metadata["platforms"]]


def load_collection(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise BuilderError(f"cannot read {path}: {error}") from error
    if not isinstance(data, dict):
        raise BuilderError(f"{path} must contain a YAML mapping")
    return data


def expand_collection(data: dict[str, Any]) -> list[ExpandedImage]:
    for key in ("name", "variant", "description", "versions"):
        if key not in data:
            raise BuilderError(f"images.yaml is missing top-level key: {key}")
    if IMAGE_NAME_RE.fullmatch(str(data["name"])) is None:
        raise BuilderError("image name must contain lowercase letters, numbers, and hyphens")
    if data["variant"] not in {"base", "runtime", "service"}:
        raise BuilderError("variant must be base, runtime, or service")
    versions = data["versions"]
    if not isinstance(versions, dict) or not versions:
        raise BuilderError("versions must be a non-empty mapping")

    expanded: list[ExpandedImage] = []
    for raw_version, entry in versions.items():
        version = str(raw_version)
        if not isinstance(entry, dict):
            raise BuilderError(f"version {version} must be a mapping")
        for key in ("upstream", "lifecycle", "platforms", "push_registries", "additional_tags"):
            if key not in entry:
                raise BuilderError(f"version {version} is missing key: {key}")

        upstream = entry["upstream"]
        if not isinstance(upstream, dict) or not all(key in upstream for key in ("image", "tag", "digest")):
            raise BuilderError(f"version {version} must define upstream image, tag, and digest")
        if not str(upstream["image"]) or not str(upstream["tag"]) or str(upstream["tag"]) == "latest":
            raise BuilderError(f"version {version} has an invalid upstream image or tag")
        if not DIGEST_RE.fullmatch(str(upstream["digest"])):
            raise BuilderError(f"version {version} does not contain a verified sha256 digest")

        registries = entry["push_registries"]
        if not isinstance(registries, dict) or not registries:
            raise BuilderError(f"version {version} must define at least one push registry")
        primary = registries.get("ghcr") or next(iter(registries.values()))
        if not isinstance(primary, dict) or not primary.get("repository"):
            raise BuilderError(f"version {version} has no push repository")
        repositories = tuple(
            str(registry["repository"])
            for registry in registries.values()
            if isinstance(registry, dict) and registry.get("repository")
        )
        if len(repositories) != len(registries):
            raise BuilderError(f"version {version} has an invalid push registry")

        platforms = entry["platforms"]
        tags = entry["additional_tags"]
        if not isinstance(platforms, list) or not platforms:
            raise BuilderError(f"version {version} must define at least one platform")
        if any(PLATFORM_RE.fullmatch(str(platform)) is None for platform in platforms):
            raise BuilderError(f"version {version} contains an unsupported platform")
        if not isinstance(tags, list) or not tags:
            raise BuilderError(f"version {version} must define at least one additional tag")
        if any(str(tag) == "latest" for tag in tags):
            raise BuilderError(f"version {version} uses the forbidden latest tag")
        lifecycle = entry["lifecycle"]
        if (
            not isinstance(lifecycle, dict)
            or lifecycle.get("status") not in LIFECYCLE_STATUSES
            or DATE_RE.fullmatch(str(lifecycle.get("support_until", ""))) is None
        ):
            raise BuilderError(f"version {version} has an invalid lifecycle")

        common_user = data.get("user")
        version_user = entry.get("user", {})
        if not isinstance(common_user, dict):
            raise BuilderError("images.yaml must define a global user mapping")
        missing_user_keys = REQUIRED_USER_KEYS - common_user.keys()
        if missing_user_keys:
            raise BuilderError(
                "global user configuration is missing: " + ", ".join(sorted(missing_user_keys))
            )
        if not isinstance(version_user, dict):
            raise BuilderError(f"version {version} user override must be a mapping")
        user = {**common_user, **version_user}
        if (
            USER_NAME_RE.fullmatch(str(user.get("name", ""))) is None
            or not isinstance(user.get("uid"), int)
            or user["uid"] < 1
            or not isinstance(user.get("gid"), int)
            or user["gid"] < 1
            or ABSOLUTE_PATH_RE.fullmatch(str(user.get("workdir", ""))) is None
            or ABSOLUTE_PATH_RE.fullmatch(str(user.get("shell", ""))) is None
        ):
            raise BuilderError(f"version {version} has an invalid user configuration")

        metadata = {
            **{key: value for key, value in data.items() if key != "versions"},
            **entry,
            "name": data["name"],
            "variant": data["variant"],
            "version": version,
            "description": data["description"],
            "owners": data.get("owners", DEFAULT_OWNERS),
            "upstream": upstream,
            "platforms": platforms,
            "registry": {"repository": primary["repository"]},
            "user": {"uid": user["uid"], "gid": user["gid"]},
            "lifecycle": lifecycle,
            "security": data.get("security", DEFAULT_SECURITY),
            "tags": list(dict.fromkeys((version, *(str(tag) for tag in tags)))),
        }
        expanded.append(ExpandedImage(version, metadata, repositories, user))
    return expanded


def select_versions(images: list[ExpandedImage], versions: tuple[str, ...]) -> list[ExpandedImage]:
    if not versions:
        return images
    by_version = {image.version: image for image in images}
    missing = [version for version in versions if version not in by_version]
    if missing:
        raise BuilderError(f"unknown version(s): {', '.join(missing)}")
    return [by_version[version] for version in versions]


def render_dockerfile(image: ExpandedImage, template_text: str) -> str:
    context = {
        **image.metadata,
        "user": image.build_user,
        "repositories": image.repositories,
    }
    try:
        environment = Environment(
            autoescape=False,
            keep_trailing_newline=True,
            undefined=StrictUndefined,
        )
        return environment.from_string(template_text).render(**context)
    except TemplateError as error:
        raise BuilderError(f"cannot render Dockerfile for {image.version}: {error}") from error


def render_image(image: ExpandedImage, output_root: Path, template_text: str) -> Path:
    directory = output_root / str(image.metadata["name"]) / image.version
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "Dockerfile").write_text(
        render_dockerfile(image, template_text), encoding="utf-8"
    )
    return directory
