from logging import getLogger
from pathlib import Path
from typing import Optional

import httpx
from rich.progress import Progress

from .enums import DependencyType, ProjectType
from .models import Collection, Entry, Project, Version
from .modrinth import ModrinthApi, ModrinthException

logger = getLogger("App")


def find_in_entries(entries: list[Entry], project_id: str) -> Optional[Entry]:
    return next((entry for entry in entries if entry.project.id == project_id), None)


def get_version(api: ModrinthApi, project: Project, version_id: Optional[str] = None) -> Version:
    logger.info("Fetching versions")
    versions = api.get_project_versions(project)

    if len(versions) == 0:
        raise ModrinthException(
            f"There is no matching versions for project: '{project.id}' ({project.name})"
        )

    if version := next((version for version in versions if version.id == version_id), None):
        return version

    return versions[-1]


def create_entries_for_project(
    api: ModrinthApi,
    project: Project,
    already_created_entries: list[Entry] = [],
) -> list[Entry]:
    version = get_version(api, project)
    print(f"- {project.name.ljust(64)} {version.number}", flush=True)
    logger.info("Adding the project to entry list with newest version: '%s'", version.id)
    entries: list[Entry] = [Entry(project=project, version=version)]

    if len(version.dependencies) == 0:
        return entries

    logger.info("Looking for project dependencies")
    logger.debug("- dependencies: %i", len(version.dependencies))
    for number, dependency in enumerate(version.dependencies):
        logger.debug("Dependency %i. - Project: '%s'", number, dependency.project_id)
        if dependency.type == DependencyType.OPTIONAL:
            logger.warning("Dependency is optional, skip")
            continue

        if find_in_entries([*already_created_entries, *entries], dependency.project_id):
            logger.warning("Dependency project already exist in entry list, skip")
            continue

        logger.info("Fetching dependency: '%s'", dependency.project_id)
        dependency_project = api.get_project(dependency.project_id)
        dependency_version = get_version(api, dependency_project, dependency.version_id)
        print(f"  - {dependency_project.name.ljust(62)} {dependency_version.number}", flush=True)
        logger.info("Adding dependency project to entry list")
        entries.append(Entry(project=dependency_project, version=dependency_version))

    return entries


def get_entries(api: ModrinthApi, collection: Collection) -> list[Entry]:
    entries: list[Entry] = []

    for project_id in collection.project_ids:
        logger.info("Fetching collection project: '%s'", project_id)

        if find_in_entries(entries, project_id):
            logger.warning("Project already exist in entry list, skip")
            continue

        project = api.get_project(project_id)
        entries.extend(create_entries_for_project(api, project, entries))

    return entries


def download_entry(game_path: Path, entry: Entry) -> None:
    logger.debug("Preparing directory to downloading the project: '%s'", entry.project.id)
    file_dir: Path
    match entry.project.type:
        case ProjectType.MOD:
            file_dir = game_path.joinpath("mods")
        case ProjectType.MODPACK:
            file_dir = game_path.joinpath("modpacks")
        case ProjectType.RESOURCEPACK:
            file_dir = game_path.joinpath("resourcepacks")
        case ProjectType.SHADER:
            file_dir = game_path.joinpath("shaderpacks")
    file_dir.mkdir(exist_ok=True)

    with Progress() as progress:
        for file in entry.version.files:
            # Download only primary files
            if not file.primary:
                continue

            file_path = file_dir.joinpath(file.name)

            if file_path.exists():
                logger.warning("Project was already downloaded, skip")
                continue

            logger.info("Downloading file '%s'", file.name)
            file_path.touch()
            with httpx.stream("GET", file.url) as response:
                total = int(response.headers["Content-Length"])
                download_task = progress.add_task(f"- {file.name.ljust(64)}", total=total)

                with open(file_path, "wb") as file_output:
                    for chunk in response.iter_bytes():
                        file_output.write(chunk)
                        progress.update(download_task, completed=response.num_bytes_downloaded)
            logger.info("File downloaded")
