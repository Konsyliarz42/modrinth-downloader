from . import get_logger
from .enums import DependencyType, VersionType
from .models import Version
from .modrinth import ModrinthApi

logger = get_logger("app-utils")


def find_version(version_id: str, versions: list[Version]) -> Version | None:
    for version in versions:
        if version.id == version_id:
            return version

    return None


def get_newest_versions(versions: list[Version]) -> list[Version]:
    alphas: list[Version] = []
    betas: list[Version] = []
    releases: list[Version] = []

    for version in versions:
        if not alphas and version.version_type == VersionType.ALPHA:
            alphas.append(version)
        if not betas and version.version_type == VersionType.BETA:
            betas.append(version)
        if not releases and version.version_type == VersionType.RELEASE:
            releases.append(version)

        if alphas and betas and releases:
            break

    return alphas + betas + releases


def get_dependency_dict(
    api: ModrinthApi, download_dict: dict[str, list[Version]], version: Version
) -> dict[str, list[Version]]:
    logger.info("Resolving dependencies for: '%s'", version.id)
    new_download_dict = download_dict.copy()

    logger.debug("  Number of dependencies: %s", len(version.dependencies))
    for dependency in version.dependencies:
        if dependency["dependency_type"] != DependencyType.REQUIRED or not dependency["project_id"]:
            logger.warning("  Dependency is not required or have not `project_id`, skip")
            continue

        logger.debug("  - Dependency project: '%s'", dependency["project_id"])

        if dependency["project_id"] in new_download_dict.keys():
            if not dependency["version_id"]:
                logger.warning("    Project is already on the list, skip")
                continue

            version_index = [
                index
                for index, ver in enumerate(new_download_dict[dependency["project_id"]])
                if ver.id == dependency["version_id"]
            ]
            if version_index:
                new_download_dict[dependency["project_id"]][version_index[0]].required_by.append(
                    version.project_id
                )
                logger.warning("    Version is already on the list, skip")
                continue
            logger.debug("    Version required: '%s'", dependency["version_id"])
            logger.debug(
                "    Versions on the list: %s",
                [ver.id for ver in new_download_dict[dependency["project_id"]]],
            )

        versions = api.read_project_versions(dependency["project_id"])
        logger.debug("    Project versions: %s", len(versions))
        selected_version = versions[0]

        if dependency["version_id"]:
            selected_version = next(ver for ver in versions if ver.id == dependency["version_id"])
            selected_version.required_by.append(version.project_id)

        logger.debug("    Selected version: '%s'", selected_version.id)

        if dependency["project_id"] in new_download_dict.keys():
            new_download_dict[dependency["project_id"]].append(selected_version)
        else:
            new_download_dict[dependency["project_id"]] = [selected_version]

        new_download_dict.update(get_dependency_dict(api, new_download_dict, selected_version))

    return new_download_dict
