from __future__ import annotations

import os
import shlex
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import click

from image_builder import __version__
from image_builder.core import (
    BuilderError,
    ExpandedImage,
    expand_collection,
    load_collection,
    render_dockerfile,
    render_image,
    resolve_context_files,
    select_versions,
)


def resolve_definition(path: Path | None) -> Path:
    definition = (path or Path("images.yaml")).expanduser().resolve()
    if not definition.is_file():
        raise BuilderError(f"definition not found: {definition}")
    return definition


def selected_images(path: Path | None, versions: tuple[str, ...]) -> tuple[Path, list[ExpandedImage]]:
    definition = resolve_definition(path)
    images = select_versions(expand_collection(load_collection(definition)), versions)
    return definition, images


def load_template(definition: Path, override: Path | None) -> str:
    collection = load_collection(definition)
    configured = override if override is not None else collection.get("template")
    if not configured:
        raise BuilderError(
            "no Dockerfile template configured; add template to images.yaml or pass --template"
        )
    try:
        template = Path(configured).expanduser()
    except TypeError as error:
        raise BuilderError("Dockerfile template path must be a string") from error
    if override is not None:
        template = template.resolve()
    elif not template.is_absolute():
        template = definition.parent / template
    try:
        return template.read_text(encoding="utf-8")
    except OSError as error:
        raise BuilderError(f"cannot read Dockerfile template {template}: {error}") from error


def revision() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=False
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def utc_values() -> tuple[str, str]:
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%SZ"), now.strftime("%Y%m%d-%H%M%S")


def local_command(image: ExpandedImage, context: Path, build_date: str, git_revision: str) -> list[str]:
    return [
        "docker", "build",
        "--build-arg", f"VERSION={image.version}",
        "--build-arg", f"BUILD_DATE={build_date}",
        "--build-arg", f"REVISION={git_revision}",
        "--tag", f'local/{image.metadata["name"]}:{image.version}',
        str(context),
    ]


def ci_command(
    image: ExpandedImage, context: Path, build_date: str, git_revision: str, timestamp: str
) -> list[str]:
    command = [
        "docker", "buildx", "build", "--push",
        "--platform", ",".join(image.platforms),
        "--sbom=true", "--provenance=mode=max",
        "--build-arg", f"VERSION={image.version}",
        "--build-arg", f"BUILD_DATE={build_date}",
        "--build-arg", f"REVISION={git_revision}",
    ]
    tags = [
        f"{repository}:{tag}"
        for repository in image.repositories
        for tag in (f"{image.version}-{timestamp}", *image.metadata["tags"])
    ]
    for tag in dict.fromkeys(tags):
        command.extend(("--tag", tag))
    command.append(str(context))
    return command


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__)
def cli() -> None:
    """Generate and build images from an images.yaml collection."""


@cli.command()
@click.argument("definition", required=False, type=click.Path(path_type=Path, dir_okay=False))
@click.option("--version", "versions", multiple=True, help="Generate only this version; repeatable.")
@click.option("--output", type=click.Path(path_type=Path, file_okay=False), default="generated", show_default=True)
@click.option("--template", type=click.Path(path_type=Path, dir_okay=False), help="Override Dockerfile.template path.")
def generate(
    definition: Path | None,
    versions: tuple[str, ...],
    output: Path,
    template: Path | None,
) -> None:
    """Write versioned Dockerfiles to disk."""
    try:
        source, images = selected_images(definition, versions)
        template_text = load_template(source, template)
        for image in images:
            directory = render_image(image, output.resolve(), template_text, source.parent)
            click.echo(f"generated {directory}")
        click.echo(f"source: {source}")
    except BuilderError as error:
        raise click.ClickException(str(error)) from error


@cli.command()
@click.argument("definition", required=False, type=click.Path(path_type=Path, dir_okay=False))
@click.option("--version", "versions", multiple=True, help="Build only this version; repeatable.")
@click.option("--ci/--local", default=False, help="Use buildx, push all registry tags, SBOM, and provenance.")
@click.option("--dry-run", is_flag=True, help="Print Docker commands without executing them.")
@click.option("--template", type=click.Path(path_type=Path, dir_okay=False), help="Override Dockerfile.template path.")
def build(
    definition: Path | None,
    versions: tuple[str, ...],
    ci: bool,
    dry_run: bool,
    template: Path | None,
) -> None:
    """Build all listed versions without keeping generated files."""
    try:
        source, images = selected_images(definition, versions)
        template_text = load_template(source, template)
        build_date, timestamp = utc_values()
        git_revision = os.environ.get("GITHUB_SHA") or revision()
        with tempfile.TemporaryDirectory(prefix="builder-") as temporary:
            output = Path(temporary)
            for image in images:
                context = render_image(image, output, template_text, source.parent)
                command = (
                    ci_command(image, context, build_date, git_revision, timestamp)
                    if ci
                    else local_command(image, context, build_date, git_revision)
                )
                click.echo(f"{image.metadata['name']}:{image.version} <- {source}")
                click.echo(shlex.join(command))
                if not dry_run:
                    subprocess.run(command, check=True)
    except BuilderError as error:
        raise click.ClickException(str(error)) from error
    except (OSError, subprocess.CalledProcessError) as error:
        raise click.ClickException(f"build failed: {error}") from error


@cli.command()
@click.argument("definition", required=False, type=click.Path(path_type=Path, dir_okay=False))
def validate(definition: Path | None) -> None:
    """Validate and expand every version without writing files."""
    try:
        source, images = selected_images(definition, ())
        template_text = load_template(source, None)
        for image in images:
            render_dockerfile(image, template_text)
            resolve_context_files(image, source.parent)
        click.echo(f"valid: {source} ({len(images)} versions)")
    except BuilderError as error:
        raise click.ClickException(str(error)) from error
