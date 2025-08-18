from . import Logger
from .enums import DependencyType, VersionType
from .models import Project, Version
from .modrinth import ModrinthApi
from rich.console import Console

logger = Logger("app-utils")


def find_version(version_id: str, versions: list[Version]) -> Version | None:
    for version in versions:
        if version.id == version_id:
            return version

    return None


def find_version_index(version_id: str, versions: list[Version]) -> int | None:
    for index, version in enumerate(versions):
        if version.id == version_id:
            return index

    return None


def get_newest_version(versions: list[Version], prefer_releases: bool) -> Version | None:
    if len(versions) == 0:
        return None

    if prefer_releases:
        for version in versions:
            if version.version_type == VersionType.RELEASE:
                return version

    return versions[0]


def get_final_versions(versions: list[Version]) -> list[Version]:
    required_versions = [version for version in versions if version.required_by]

    if not required_versions:
        return [versions[0]]

    return required_versions


def get_dependency_dict(
    api: ModrinthApi,
    download_dict: dict[str, list[Version]],
    version: Version,
    prefer_releases: bool,
) -> dict[str, list[Version]]:
    logger.info("Resolving dependencies for: '%s'", version.id, indent_level=1)
    new_download_dict = download_dict.copy()

    logger.debug("Number of dependencies: %s", len(version.dependencies), indent_level=2)
    for dependency in version.dependencies:
        project_id = dependency["project_id"]
        version_id = dependency["version_id"]

        logger.info("- Dependency project: '%s'", project_id, indent_level=1)

        if dependency["dependency_type"] != DependencyType.REQUIRED or not project_id:
            logger.warning(
                "Dependency is not required or have not `project_id`, skip", indent_level=2
            )
            continue

        if project_id in new_download_dict.keys():
            if not version_id:
                logger.warning("Project is already on the list, skip", indent_level=2)
                continue

            logger.debug("Required version: '%s'", version_id, indent_level=2)
            version_index = find_version_index(version_id, new_download_dict[project_id])
            if version_index is not None:
                new_download_dict[project_id][version_index].required_by.append(version.project_id)
                logger.warning("Version is already on the list, skip", indent_level=2)
                continue
        elif version_id:
            logger.debug("Required version: '%s'", version_id, indent_level=2)

        versions = api.read_project_versions(project_id)
        logger.debug("Fetched versions: %s", len(versions), indent_level=2)
        selected_version = get_newest_version(versions, prefer_releases)

        if not selected_version:
            logger.warning(
                "No available versions for dependency project: '%s', skip",
                project_id,
                indent_level=2,
            )
            continue

        if version_id:
            selected_version = find_version(version_id, versions)
            if not selected_version:
                continue

            selected_version.required_by.append(version.project_id)

        logger.debug("Selected version: '%s'", selected_version.id, indent_level=2)

        if project_id in new_download_dict.keys():
            new_download_dict[project_id].append(selected_version)
        else:
            new_download_dict[project_id] = [selected_version]

        new_download_dict.update(
            get_dependency_dict(api, new_download_dict, selected_version, prefer_releases)
        )

    return new_download_dict


def print_project_list(
    console: Console,
    download_dict: dict[str, list[Version]],
    projects: list[Project],
) -> None:
    print()

    for index, project in enumerate(projects):
        console.print(project.to_console_print(index))
        versions = download_dict[project.id]

        for version in versions:
            console.print(version.to_console_print(projects))

        print()
