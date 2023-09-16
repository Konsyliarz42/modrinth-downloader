import csv
import math
from pathlib import Path

import httpx
from progress.bar import Bar

from modrinth import ModrinthAPI, ModrinthError, Version

from .models import Mod


def _download(version: Version, destination: Path) -> None:
    file_destination = destination.joinpath(version.file_name)
    chunk_size_bytes = 1000

    if (
        file_destination.exists()
        and file_destination.stat().st_size == version.file_size
    ):
        print(f"{file_destination.name.ljust(64)} | skipped (Already downloaded)")
        return

    with open(file_destination, "w+b") as file:
        with httpx.stream("GET", version.file_url, follow_redirects=True) as response:
            response.raise_for_status()

            with Bar(
                file_destination.name.ljust(64),
                max=math.ceil(version.file_size / chunk_size_bytes),
                fill="=",
            ) as bar:
                for chunk in response.iter_bytes(chunk_size_bytes):
                    file.write(chunk)
                    bar.next()


def download_version(api: ModrinthAPI, version: Version, destination: Path) -> None:
    for dependency in version.required_versions:
        dependency_version = api.get_version(dependency)
        download_version(api, dependency_version, destination)

    for dependency in version.required_projects:
        dependency_versions = api.get_all_versions(dependency)
        download_version(api, dependency_versions[0], destination)

    _download(version, destination)


def read_mods(csv_path: Path) -> list[Mod]:
    with open(csv_path, newline="") as file:
        mods = [Mod.from_json(data) for data in csv.DictReader(file)]

    return mods


def download_mods(api: ModrinthAPI, mods: list[Mod], destination: Path) -> None:
    print("File".ljust(64), "| Status")
    print("-" * 96)

    for mod in mods:
        try:
            if mod.version_id:
                version = api.get_version(mod.version_id)
            else:
                version = api.get_all_versions(mod.id_or_slug)[0]
        except ModrinthError as error:
            print(f"{mod.id_or_slug.ljust(64)} | skipped ({error})")
            continue

        download_version(api, version, destination)
