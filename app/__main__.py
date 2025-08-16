from argparse import ArgumentParser
from sys import exit

from rich.console import Console
from rich_argparse import (
    ArgumentDefaultsRichHelpFormatter,
    MetavarTypeRichHelpFormatter,
    RawTextRichHelpFormatter,
)

from app.utils import get_or_fetch_project, resolve_dependencies

from .models import Version
from .modrinth import ModrinthApi


class UltimateHelpFormatter(
    MetavarTypeRichHelpFormatter,
    RawTextRichHelpFormatter,
    ArgumentDefaultsRichHelpFormatter,
): ...


def get_parser() -> ArgumentParser:
    parser = ArgumentParser(
        prog="Modrinth downloader",
        description="Download whole collection from modrinth",
        formatter_class=UltimateHelpFormatter,
    )

    parser.add_argument(
        "-c", "--collection", help="Modrinth collection id or URL", required=True, type=str
    )
    parser.add_argument(
        "-o", "--optional", help="Allow to optional dependencies", action="store_true"
    )
    parser.add_argument("-g", "--game-version", help="Minecraft version", required=True, type=str)
    parser.add_argument(
        "-l", "--loader", help="Mod loader", required=True, nargs="+", default=[], type=str
    )
    parser.add_argument("-t", "--token", help="Modrinth personal access token", type=str)

    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    console = Console()

    collection_id: str = args.collection
    if collection_id.startswith("http"):
        _, collection_id = collection_id.rsplit("/", 1)

    api = ModrinthApi(args.game_version, args.loader)

    # Collection

    with console.status("[bold blue]Reading collection...") as status:
        collection = api.read_collection(collection_id)
    if not collection:
        console.print("[red]Collection not found[/red]")
        exit(1)

    console.print(
        f"Collection: [bold green]{collection.title}[/bold green]",
        f"Game version: [bold green]{args.game_version}[/bold green]",
        f"Loaders: [bold green]{'[white], [/white]'.join(args.loader)}[/bold green]",
        sep="\n",
        end="\n\n",
    )

    # Projects

    with console.status("[bold blue]Reading collection projects...") as status:
        projects = api.read_projects(collection.projects)
    if not projects:
        console.print("[yellow]Collection is empty[/yellow]")
        exit(0)

    # Versions

    versions: list[Version] = []
    with console.status("[bold blue]Reading projects versions...") as status:
        for project in projects:
            project_versions = api.read_project_versions(project.id)
            if not project_versions:
                continue
            project_newest_version = project_versions[0]
            versions.append(project_newest_version)

    # Dependencies

    dependencies: dict[str, list[Version]] = dict((project.id, []) for project in projects)
    with console.status("[bold blue]Checking collection dependencies...") as status:
        dependencies = resolve_dependencies(api, versions, args.optional)

    # Summary

    for index, item in enumerate(dependencies.items()):
        project_id, dependency_versions = item
        project = get_or_fetch_project(api, project_id, projects)
        index_number = (str(index + 1).zfill(2) + ". ").rjust(5)

        console.print(
            f"[bold black]{index_number}[/bold black][bold white]{project.title}[/bold white]"
        )

        if len(dependency_versions) == 0:
            console.print(
                f"{' ' * len(index_number)}[yellow]No available versions[/yellow]\n"
            )
            continue

        if len(dependency_versions) > 1:
            for dependency_version in dependency_versions:
                locked_project = get_or_fetch_project(api, dependency_version.locked_by, projects)
                optional_str = " (optional)" if dependency_version.is_optional else ""
                projects.append(locked_project)
                console.print(
                    f"{' ' * len(index_number)}[black]{dependency_version.to_console_print()}[/black]"
                )
            print()
            continue

        dependency_version = dependency_versions[0]
        console.print(
            f"{' ' * len(index_number)}[black]{dependency_version.to_console_print()}[/black]\n"
        )
