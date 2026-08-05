from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import click
import yaml
from rich import box
from rich.console import Console
from rich.table import Table
from rich.text import Text

from inspectur import __version__


DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
VARIANTS = ("base", "runtime", "builder", "framework", "service", "tool")
STATUSES = ("experimental", "supported", "maintenance", "deprecated", "end-of-life")
STATUS_STYLES = {
    "experimental": "magenta",
    "supported": "green",
    "maintenance": "yellow",
    "deprecated": "bright_red",
    "end-of-life": "red bold",
}


class MetadataError(Exception):
    """Raised when repository metadata cannot be loaded."""


@dataclass(frozen=True)
class ImageDefinition:
    path: Path
    root: Path
    data: dict[str, Any]

    @property
    def name(self) -> str:
        return str(self.data.get("name", "unknown"))

    @property
    def variant(self) -> str:
        return str(self.data.get("variant", "unknown"))

    @property
    def version(self) -> str:
        return str(self.data.get("version", "unknown"))

    @property
    def status(self) -> str:
        return str(self.data.get("lifecycle", {}).get("status", "unknown"))

    @property
    def support_until(self) -> str:
        return str(self.data.get("lifecycle", {}).get("support_until", "unknown"))

    @property
    def upstream(self) -> str:
        upstream = self.data.get("upstream", {})
        image = upstream.get("image", "unknown")
        tag = upstream.get("tag", "unknown")
        return f"{image}:{tag}"

    @property
    def repository(self) -> str:
        return str(self.data.get("registry", {}).get("repository", "unknown"))

    @property
    def platforms(self) -> str:
        return ",".join(str(platform).removeprefix("linux/") for platform in self.data.get("platforms", []))

    @property
    def relative_path(self) -> str:
        return str(self.path.parent.relative_to(self.root))

    @property
    def issues(self) -> list[str]:
        issues: list[str] = []
        upstream_digest = str(self.data.get("upstream", {}).get("digest", ""))
        if not DIGEST_RE.fullmatch(upstream_digest):
            issues.append("upstream digest")

        if self.variant == "runtime":
            base_digest = str(self.data.get("base", {}).get("digest", ""))
            if not DIGEST_RE.fullmatch(base_digest):
                issues.append("base digest")
        return issues

    @property
    def ready(self) -> bool:
        return not self.issues


@dataclass
class AppContext:
    root: Path
    console: Console


def natural_key(value: str) -> list[object]:
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", value)]


def find_repository_root(explicit_root: Path | None) -> Path:
    if explicit_root is not None:
        candidate = explicit_root.expanduser().resolve()
        if not (candidate / "images").is_dir():
            raise MetadataError(f"{candidate} does not contain an images directory")
        return candidate

    for candidate in (Path.cwd(), *Path.cwd().parents):
        if (candidate / "images").is_dir():
            return candidate
    raise MetadataError("repository root not found; run inside the repository or pass --root")


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise MetadataError(f"cannot read {path}: {error}") from error
    if not isinstance(data, dict):
        raise MetadataError(f"{path} must contain a YAML mapping")
    return data


def discover_images(root: Path) -> list[ImageDefinition]:
    images = [ImageDefinition(path, root, load_yaml(path)) for path in (root / "images").glob("**/image.yaml")]
    return sorted(images, key=lambda image: (image.variant, image.name, natural_key(image.version)))


def styled_status(status: str) -> Text:
    return Text(status, style=STATUS_STYLES.get(status, "white"))


def readiness(ready: bool) -> Text:
    return Text("ready" if ready else "blocked", style="green bold" if ready else "yellow bold")


def image_table(
    images: Iterable[ImageDefinition],
    title: str,
    show_references: bool,
    show_paths: bool,
) -> Table:
    table = Table(title=title, box=box.ROUNDED, header_style="bold cyan", expand=False)
    table.add_column("Image", style="bold", no_wrap=True, min_width=5)
    table.add_column("Version", no_wrap=True)
    table.add_column("Status", no_wrap=True)
    table.add_column("Ready", no_wrap=True)
    table.add_column("Platforms", no_wrap=True)
    if show_references:
        table.add_column("Upstream", no_wrap=True, overflow="ellipsis", max_width=36)
        table.add_column("Repository", no_wrap=True, overflow="ellipsis", max_width=40)
    if show_paths:
        table.add_column("Definition", style="dim", no_wrap=True, overflow="ellipsis", max_width=45)

    for image in images:
        row: list[Any] = [
            image.name,
            image.version,
            styled_status(image.status),
            readiness(image.ready),
            image.platforms,
        ]
        if show_references:
            row.extend((image.upstream, image.repository))
        if show_paths:
            row.append(image.relative_path)
        table.add_row(*row)
    return table


def print_inventory(
    app: AppContext,
    variant: str | None,
    status: str | None,
    name: str | None,
    readiness_filter: str,
    group_by: str,
    show_references: bool,
    show_paths: bool,
) -> None:
    images = discover_images(app.root)
    if variant:
        images = [image for image in images if image.variant == variant]
    if status:
        images = [image for image in images if image.status == status]
    if name:
        images = [image for image in images if image.name == name]
    if readiness_filter != "all":
        expected = readiness_filter == "ready"
        images = [image for image in images if image.ready is expected]

    if not images:
        app.console.print("[yellow]No image definitions match the selected filters.[/yellow]")
        return

    if group_by == "none":
        app.console.print(image_table(images, f"Image inventory ({len(images)})", show_references, show_paths))
        return

    key = (lambda image: image.variant) if group_by == "variant" else (lambda image: image.status)
    groups: dict[str, list[ImageDefinition]] = {}
    for image in images:
        groups.setdefault(key(image), []).append(image)
    for index, (group, entries) in enumerate(sorted(groups.items())):
        if index:
            app.console.print()
        app.console.print(image_table(entries, f"{group.title()} images ({len(entries)})", show_references, show_paths))


@click.group(invoke_without_command=True, context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--root",
    type=click.Path(path_type=Path, file_okay=False),
    envvar="INSPECTUR_ROOT",
    help="Repository root. Defaults to the nearest parent containing images/.",
)
@click.option("--no-color", is_flag=True, help="Disable colored output.")
@click.version_option(__version__)
@click.pass_context
def cli(ctx: click.Context, root: Path | None, no_color: bool) -> None:
    """Inspect image.yaml definitions in the container image repository."""
    try:
        repository_root = find_repository_root(root)
    except MetadataError as error:
        raise click.ClickException(str(error)) from error
    ctx.obj = AppContext(repository_root, Console(no_color=no_color))
    if ctx.invoked_subcommand is None:
        ctx.invoke(list_images)


@cli.command("list")
@click.option("--variant", type=click.Choice(VARIANTS), help="Show only one image variant.")
@click.option("--status", type=click.Choice(STATUSES), help="Show only one lifecycle state.")
@click.option("--name", help="Show only an exact image name.")
@click.option(
    "--readiness",
    "readiness_filter",
    type=click.Choice(("all", "ready", "blocked")),
    default="all",
    show_default=True,
)
@click.option("--group-by", type=click.Choice(("variant", "status", "none")), default="variant", show_default=True)
@click.option("--references", is_flag=True, help="Include upstream and target repository columns.")
@click.option("--paths", is_flag=True, help="Include metadata paths in the table.")
@click.pass_obj
def list_images(
    app: AppContext,
    variant: str | None,
    status: str | None,
    name: str | None,
    readiness_filter: str,
    group_by: str,
    references: bool,
    paths: bool,
) -> None:
    """List and filter all discovered images."""
    try:
        print_inventory(app, variant, status, name, readiness_filter, group_by, references, paths)
    except MetadataError as error:
        raise click.ClickException(str(error)) from error


@cli.command()
@click.argument("name")
@click.argument("version", required=False)
@click.pass_obj
def show(app: AppContext, name: str, version: str | None) -> None:
    """Show complete details for IMAGE [VERSION]."""
    try:
        matches = [image for image in discover_images(app.root) if image.name == name]
    except MetadataError as error:
        raise click.ClickException(str(error)) from error
    if version is not None:
        matches = [image for image in matches if image.version == version]
    if not matches:
        raise click.ClickException(f"image not found: {name}{':' + version if version else ''}")
    if len(matches) > 1:
        versions = ", ".join(image.version for image in matches)
        raise click.ClickException(f"multiple versions found for {name}: {versions}; provide VERSION")

    image = matches[0]
    data = image.data
    details = Table(title=f"{image.name}:{image.version}", box=box.ROUNDED, show_header=False)
    details.add_column("Field", style="bold cyan", no_wrap=True)
    details.add_column("Value", overflow="fold")
    details.add_row("Variant", image.variant)
    details.add_row("Description", str(data.get("description", "unknown")))
    details.add_row("Lifecycle", styled_status(image.status))
    details.add_row("Support until", image.support_until)
    details.add_row("Readiness", readiness(image.ready))
    details.add_row("Missing", ", ".join(image.issues) if image.issues else "none")
    details.add_row("Upstream", image.upstream)
    details.add_row("Upstream digest", str(data.get("upstream", {}).get("digest", "unknown")))
    if data.get("base"):
        base = data["base"]
        details.add_row("Approved base", f"{base.get('repository')}:{base.get('tag')}")
        details.add_row("Base digest", str(base.get("digest", "unknown")))
    details.add_row("Published as", image.repository)
    details.add_row("Tags", ", ".join(map(str, data.get("tags", []))))
    details.add_row("Platforms", ", ".join(map(str, data.get("platforms", []))))
    details.add_row("Owners", ", ".join(map(str, data.get("owners", []))))
    user = data.get("user", {})
    details.add_row("User", f"{user.get('uid', 'unknown')}:{user.get('gid', 'unknown')}")
    details.add_row("Definition", image.relative_path)
    app.console.print(details)


@cli.command()
@click.pass_obj
def summary(app: AppContext) -> None:
    """Show inventory totals by variant and lifecycle state."""
    try:
        images = discover_images(app.root)
    except MetadataError as error:
        raise click.ClickException(str(error)) from error
    variants = Counter(image.variant for image in images)
    statuses = Counter(image.status for image in images)

    table = Table(title="Repository summary", box=box.ROUNDED, header_style="bold cyan")
    table.add_column("Measure")
    table.add_column("Count", justify="right", style="bold")
    table.add_row("Total definitions", str(len(images)))
    table.add_row("Ready to build", str(sum(image.ready for image in images)), style="green")
    table.add_row("Blocked by digest", str(sum(not image.ready for image in images)), style="yellow")
    for variant, count in sorted(variants.items()):
        table.add_row(f"Variant: {variant}", str(count))
    for status, count in sorted(statuses.items()):
        table.add_row(f"Lifecycle: {status}", str(count))
    app.console.print(table)


@cli.command()
@click.option("--variant", type=click.Choice(VARIANTS), help="Check only one image variant.")
@click.pass_obj
def check(app: AppContext, variant: str | None) -> None:
    """Report unresolved required digests and exit non-zero when blocked."""
    try:
        images = discover_images(app.root)
    except MetadataError as error:
        raise click.ClickException(str(error)) from error
    if variant:
        images = [image for image in images if image.variant == variant]
    blocked = [image for image in images if not image.ready]
    if not blocked:
        app.console.print("[green bold]All selected image definitions have verified digest values.[/green bold]")
        return

    table = Table(title="Blocked image definitions", box=box.ROUNDED, header_style="bold cyan")
    table.add_column("Image", style="bold")
    table.add_column("Version")
    table.add_column("Variant")
    table.add_column("Missing")
    table.add_column("Definition", style="dim", no_wrap=True, overflow="ellipsis")
    for image in blocked:
        table.add_row(image.name, image.version, image.variant, ", ".join(image.issues), image.relative_path)
    app.console.print(table)
    raise click.exceptions.Exit(1)


@cli.command()
@click.option("--runtime", help="Show only one runtime name, such as node.")
@click.pass_obj
def matrix(app: AppContext, runtime: str | None) -> None:
    """Show entries from runtime versions.yaml matrix files."""
    paths = sorted((app.root / "images" / "runtimes").glob("*/versions.yaml"))
    if runtime:
        paths = [path for path in paths if path.parent.name == runtime]
    if not paths:
        raise click.ClickException("no runtime matrix definitions found")

    for index, path in enumerate(paths):
        data = load_yaml(path)
        runtime_name = str(data.get("name", path.parent.name))
        table = Table(title=f"{runtime_name.title()} runtime matrix", box=box.ROUNDED, header_style="bold cyan")
        table.add_column("Runtime", no_wrap=True)
        table.add_column("Base OS", no_wrap=True)
        table.add_column("Base version", no_wrap=True)
        table.add_column("Base digest", no_wrap=True)
        table.add_column("Upstream tag")
        table.add_column("Upstream digest", no_wrap=True)

        versions = data.get("runtime_versions", {})
        for runtime_version, operating_systems in versions.items():
            for base_os, base_versions in operating_systems.items():
                for base_version, entry in base_versions.items():
                    base_ready = DIGEST_RE.fullmatch(str(entry.get("base_digest", ""))) is not None
                    upstream_ready = DIGEST_RE.fullmatch(str(entry.get("upstream_digest", ""))) is not None
                    table.add_row(
                        str(runtime_version),
                        str(base_os),
                        str(base_version),
                        readiness(base_ready),
                        str(entry.get("upstream_tag", "unknown")),
                        readiness(upstream_ready),
                    )
        if index:
            app.console.print()
        app.console.print(table)


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
