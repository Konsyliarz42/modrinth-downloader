import os
from pathlib import Path

from dotenv import load_dotenv

from modrinth import ModrinthAPI

from .utils import download_mods, read_mods

load_dotenv()

download_folder = Path(os.environ["DOWNLOAD_PATH"])

if not download_folder.exists():
    raise ValueError(f"{download_folder} not exists")
elif not download_folder.is_dir():
    raise ValueError(f"{download_folder} is not a directory")

csv_file = Path(input("csv path: "))

if not csv_file.exists():
    raise ValueError(f"{download_folder} not exists")
elif not csv_file.is_file():
    raise ValueError(f"{download_folder} is not a file")

api = ModrinthAPI(os.environ["PERSONAL_ACCESS_TOKEN"])
mods = read_mods(csv_file)

download_mods(api, mods, download_folder)
