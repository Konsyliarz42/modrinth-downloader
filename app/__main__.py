from argparse import ArgumentParser
from sys import exit

from rich.console import Console
from rich_argparse import (
    ArgumentDefaultsRichHelpFormatter,
    MetavarTypeRichHelpFormatter,
    RawTextRichHelpFormatter,
)

from . import get_logger
from .models import Version
from .modrinth import ModrinthApi
from .utils import get_dependency_dict


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
    logger = get_logger("app")
    logger.warning("---- START ----")
    parser = get_parser()
    logger.debug("Start argument parsing")
    args = parser.parse_args()

    collection_id: str = args.collection
    if collection_id.startswith("http"):
        _, collection_id = collection_id.rsplit("/", 1)

    logger.info("Parsed arguments: '%s', %s, '%s'", args.game_version, args.loader, args.collection)

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
    logger.info("Fetching versions")
    with console.status("[bold blue]Fetching projects versions...[/bold blue]"):
        for project_id in collection.projects:
            logger.debug("- Project: '%s'", project_id)
            if download_dict.get(project_id):
                logger.debug("  Project already fetched, skip")
                continue
            versions = api.read_project_versions(project_id)
            logger.debug("  Project versions: %s", len(versions))
            selected_version = versions[0]
            download_dict[project_id] = [selected_version]
            logger.debug("  Project newest version: '%s'", selected_version.id)
            download_dict.update(get_dependency_dict(api, download_dict, selected_version))

    # Projects

    logger.info("Fetching projects")
    with console.status("[bold blue]Fetching projects details...[/bold blue]"):
        projects = api.read_projects(list(download_dict.keys()))

    print()
    for index, project in enumerate(projects):
        console.print(project.to_console_print(index))
        for version in download_dict[project.id]:
            console.print(version.to_console_print(projects))
        print()
