from app.enums import DependencyType
from app.models import Project, Version
from app.modrinth import ModrinthApi


def read_version_dependencies(
    api: ModrinthApi,
    version: Version,
    allow_optional: bool,
    current_dependencies: dict[str, list[Version]] = {},
) -> dict[str, list[Version]]:
    dependencies = current_dependencies.copy()

    for dependency in version.dependencies:
        # Skip dependency if not necessary
        if (
            (dependency["dependency_type"] == DependencyType.OPTIONAL and not allow_optional)
            or dependency["dependency_type"] == DependencyType.INCOMPATIBLE
            or dependency["dependency_type"] == DependencyType.EMBEDDED
            or not dependency["project_id"]
        ):
            continue

        # Skip dependency if already exist
        if dependency["project_id"] in dependencies.keys():
            all_dependency_versions = [
                version
                for version in dependencies[dependency["project_id"]]
                if version.id == dependency["version_id"]
            ]
            if not dependency["version_id"] or all_dependency_versions:
                if dependency["version_id"] and dependency["dependency_type"] == DependencyType.OPTIONAL:
                    new_version = next(version for version in all_dependency_versions if version.id == dependency["version_id"])
                    index = dependencies[dependency["project_id"]].index(new_version)
                    new_version.is_optional = True
                    dependencies[dependency["project_id"]][index] = new_version
                continue

        # Find version
        dependency_versions = api.read_project_versions(dependency["project_id"])
        if dependency["version_id"]:
            dependency_version = next(
                v for v in dependency_versions if v.id == dependency["version_id"]
            )
            dependency_version.is_locked = True
            dependency_version.locked_by = version.project_id
        else:
            dependency_version = dependency_versions[0]
            dependency_version.is_optional = (
                dependency["dependency_type"] == DependencyType.OPTIONAL
            )

        # Add dependency to others
        if dependency["project_id"] in dependencies.keys():
            dependencies[dependency["project_id"]].append(dependency_version)
        else:
            dependencies[dependency["project_id"]] = [dependency_version]

    return dependencies


def resolve_dependencies(
    api: ModrinthApi, versions: list[Version], allow_optional: bool
) -> dict[str, list[Version]]:
    all_dependencies: dict[str, list[Version]] = {}

    for version in versions:
        if version.project_id in all_dependencies.keys():
            continue
        all_dependencies[version.project_id] = [version]

        dependencies = read_version_dependencies(api, version, allow_optional, all_dependencies)
        for _, dependency_versions in dependencies.copy().items():
            for dependency_version in dependency_versions:
                dependencies.update(
                    read_version_dependencies(
                        api, dependency_version, allow_optional, all_dependencies
                    )
                )

        all_dependencies.update(dependencies)

    for project_id, dependency_versions in all_dependencies.items():
        only_locked_versions = [version for version in dependency_versions if version.is_locked]
        if not only_locked_versions:
            continue
        all_dependencies[project_id] = only_locked_versions

    return all_dependencies


def get_or_fetch_project(api: ModrinthApi, project_id: str, projects: list[Project]) -> Project:
    project_in_list = [project for project in projects if project.id == project_id]
    if project_in_list:
        return project_in_list[0]

    project_in_api = api.read_projects([project_id])
    return project_in_api[0]
