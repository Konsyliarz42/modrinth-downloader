import json
from argparse import ArgumentParser, MetavarTypeHelpFormatter
from logging import getLogger
from pathlib import Path

from rich.console import Console

from .models import Entry
from .modrinth import ModrinthApi
from .utils import download_entry, get_entries

logger = getLogger("App")


def get_arguments() -> tuple[str, str, str, str, Path]:
    parser = ArgumentParser(prog="Modrinth downloader", formatter_class=MetavarTypeHelpFormatter)
    parser.add_argument("-t", "--token", help="personal access token", required=True, type=str)
    parser.add_argument("-g", "--game", help="game version", required=True, type=str)
    parser.add_argument("-l", "--loader", help="mod loader", required=True, type=str)
    parser.add_argument("-c", "--collection", help="collection URL or ID", required=True, type=str)
    parser.add_argument("--game-path", help="path to game directory", type=str)

    args = parser.parse_args()
    logger.debug(
        "Parsed arguments: %s",
        json.dumps(
            {
                "token": args.token,
                "game": args.game,
                "loader": args.loader,
                "collection": args.collection,
                "game_path": args.game_path,
            },
            indent=4,
        ),
    )

    collection_id: str = args.collection
    if collection_id.startswith("http"):
        collection_id = collection_id[collection_id.rfind("/") + 1 :]

    return (args.token, args.game, args.loader, collection_id, Path(args.game_path or "download"))


def main(console: Console) -> None:
    logger.info("Start initialization")
    token, game_version, loader, collection_id, game_path = get_arguments()
    modrinth = ModrinthApi(token, game_version, loader)
    logger.info("Initialization end")
    console.print(f"{"-"*64}\nModrinth Downloader\n{"-"*64}")

    console.print(
        f"Game version: [bold yellow]{game_version}[/bold yellow]\nLoader: [bold yellow]{loader}[/bold yellow]\n"
    )

    with console.status("Fetching information about collection..."):
        logger.info("Fetching collection: '%s' ", collection_id)
        collection = modrinth.get_collection(collection_id)
        console.print(f"Collection: [bold cyan]{collection.name}[/bold cyan]")

    with console.status("Fetching information about projects..."):
        entries = get_entries(modrinth, collection)

    print("\nDownload files:")
    for entry in entries:
        download_entry(game_path, entry)


if __name__ == "__main__":
    console = Console()

    main(console)
    # try:
    #     main(console)
    # except Exception as error:
    #     logger.error(error)
