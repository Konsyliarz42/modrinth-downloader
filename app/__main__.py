from argparse import ArgumentParser
from sys import exit
from enum import Enum

import questionary
from rich.console import Console
from rich_argparse import (
    ArgumentDefaultsRichHelpFormatter,
    MetavarTypeRichHelpFormatter,
    RawTextRichHelpFormatter,
)

from app.enums import VersionType

from . import Logger
from .models import Project, Version
from .modrinth import ModrinthApi
from .utils import get_dependency_dict, get_final_versions, get_newest_version, print_project_list


class Option(Enum):
    DOWNLOAD = 0
    DOWNLOAD_CLIENT = 1
    DOWNLOAD_SERVER = 2
    SHOW_LIST = 3
    EXIT = 4


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
        "-c",
        "--collection",
        help="Modrinth collection id or URL",
        required=True,
        type=str,
    )
    parser.add_argument(
        "-g",
        "--game-version",
        help="Minecraft version",
        required=True,
        type=str,
    )
    parser.add_argument(
        "-l",
        "--loader",
        help="Mod loader",
        required=True,
        nargs="+",
        default=[],
        type=str,
    )
    parser.add_argument(
        "-r",
        "--releases",
        help="Prefer stable versions",
        action="store_true",
    )
    parser.add_argument(
        "-t",
        "--token",
        help="Modrinth personal access token",
        type=str,
    )

    return parser


if __name__ == "__main__":
    logger = Logger("app")
    logger.warning("---- START ----")
    parser = get_parser()
    logger.debug("Start argument parsing")
    args = parser.parse_args()

    prefer_releases: bool = args.releases
    collection_id: str = args.collection
    if collection_id.startswith("http"):
        _, collection_id = collection_id.rsplit("/", 1)

    logger.info(
        "Parsed arguments: '%s', %s, '%s', '%s'",
        args.game_version,
        args.loader,
        args.collection,
        args.releases,
    )

    api = ModrinthApi(args.game_version, args.loader)
    console = Console()

    # Validations

    logger.debug("Validate game versions: %s", api.game_versions)
    with console.status("[bold blue]Checking game version...[/bold blue]"):
        if not api.validate_game_version():
            console.print("\n[bold red]Game version is invalid[/bold red]")
            logger.critical("Game versions invalid")
            exit(1)

    console.print(
        f"[black]Game version: [/black][bold green]{', '.join(api.game_versions)}[/bold green]"
    )

    logger.debug("Validate loaders: %s", api.game_loaders)
    with console.status("[bold blue]Checking loaders...[/bold blue]"):
        if not api.validate_loaders():
            console.print("\n[bold red]Loaders are invalid[/bold red]")
            logger.critical("Loaders invalid")
            exit(1)

    console.print(f"[black]Loader: [/black][bold green]{', '.join(api.game_loaders)}[/bold green]")

    logger.info("Fetching collection: '%s'", collection_id)
    with console.status("[bold blue]Fetching collection...[/bold blue]"):
        collection = api.read_collection(collection_id)
        if not collection:
            console.print("\n[bold red]Collection not found[/bold red]")
            logger.critical("Collection not found")
            exit(1)

    console.print(f"[black]Collection: [/black][bold green]{collection.title}[/bold green]")

    # Versions

    download_dict: dict[str, list[Version]] = {}
    logger.info("Fetching projects versions")
    with console.status("[bold blue]Fetching projects versions...[/bold blue]"):
        for project_id in collection.projects:
            logger.info("- Project: '%s'", project_id)
            if download_dict.get(project_id):
                logger.debug("Project already fetched, skip", indent_level=1)
                continue

            versions = api.read_project_versions(project_id)
            logger.debug("Project versions: %s", len(versions), indent_level=1)
            newest_version = get_newest_version(versions, prefer_releases)
            if not newest_version:
                logger.warning("No available versions, skip", indent_level=1)
                continue

            download_dict[project_id] = [newest_version]
            logger.debug("Project newest version: '%s'", newest_version.id, indent_level=1)
            download_dict.update(
                get_dependency_dict(api, download_dict, newest_version, prefer_releases)
            )

    # Projects

    logger.info("Fetching projects details")
    with console.status("[bold blue]Fetching projects details...[/bold blue]"):
        projects = api.read_projects(list(download_dict.keys()))

    print()
    collisions: list[tuple[Project, list[Version]]] = []
    for index, project in enumerate(projects):
        final_versions = get_final_versions(download_dict[project.id])
        download_dict[project.id] = final_versions
        if len(final_versions) > 1:
            collisions.append((project, final_versions))

        console.print(project.to_console_print(index))
        for version in final_versions:
            console.print(version.to_console_print(projects))
        print()

    # Collisions

    if collisions:
        console.print(
            "[bold red]\nCollisions detected![/bold red]",
            "[black]Some projects require different versions.",
            "Please select versions manually:[/black]",
            sep="\n",
            end="\n\n",
        )
        logger.info("Resolving collisions")
        for index, collision in enumerate(collisions):
            project, versions = collision
            selected_version = questionary.select(
                message=project.title.ljust(32),
                choices=[
                    questionary.Choice(title=version.to_questionary(), value=version)
                    for version in versions
                ],
                qmark=str(index + 1).zfill(2).rjust(3),
            ).unsafe_ask()
            download_dict[project.id] = [selected_version]
        print()

    # Summary

    console.print("[bold green]Your collection is ready!\n[/bold green]")
    option = Option.SHOW_LIST

    while option == Option.SHOW_LIST:
        option = questionary.select(
            "What should we do now",
            choices=[
                questionary.Choice(title="Download all projects", value=Option.DOWNLOAD),
                questionary.Choice(
                    title="Download only client projects", value=Option.DOWNLOAD_CLIENT
                ),
                questionary.Choice(
                    title="Download only server projects", value=Option.DOWNLOAD_CLIENT
                ),
                questionary.Choice(title="Show project list", value=Option.SHOW_LIST),
                questionary.Choice(title="Exit", value=Option.EXIT),
            ],
        ).unsafe_ask()

        if option == Option.SHOW_LIST:
            print_project_list(console, download_dict, projects)
        if option == Option.EXIT:
            exit(0)
        if option == Option.DOWNLOAD_CLIENT:
            download_dict = dict(
                (project.id, download_dict[project.id]) for project in projects if project.is_client
            )
        if option == Option.DOWNLOAD_SERVER:
            download_dict = dict(
                (project.id, download_dict[project.id]) for project in projects if project.is_server
            )

    print(download_dict)
