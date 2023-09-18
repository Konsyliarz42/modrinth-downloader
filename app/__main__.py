import os
import tomllib
from pathlib import Path

from dotenv import load_dotenv

from modrinth import ModrinthAPI

from .utils import download_mods, read_mods
from .validators import csv_file_validator, download_folder_validator

if __name__ == "__main__":
    print("Modrinth Downloader")

    pyproject = tomllib.loads(Path("./pyproject.toml").read_text("utf-8"))
    version = pyproject["tool"]["poetry"]["version"]
    print(f"Version: {version}\n")

    load_dotenv()

    download_folder = Path(os.environ["DOWNLOAD_PATH"])
    download_folder_validator(download_folder)

    csv_file = Path(input("csv path: "))
    csv_file_validator(csv_file)
    mods = read_mods(csv_file)

    api = ModrinthAPI(os.environ["PERSONAL_ACCESS_TOKEN"], version)
    download_mods(api, mods, download_folder)
