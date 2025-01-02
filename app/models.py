from dataclasses import dataclass
from typing import Optional

from .constants import BASE_MODRINTH_URL
from .enums import DependencyType, ProjectType


@dataclass
class File:
    name: str
    url: str
    size: int
    primary: bool

    @classmethod
    def from_dict(cls, data: dict[str, any]) -> "File":
        return cls(
            name=data["filename"],
            url=data["url"],
            size=data["size"],
            primary=data["primary"]
        )


@dataclass
class Dependency:
    project_id: str
    type: DependencyType

    version_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict[str, any]) -> "Dependency":
        return cls(
            project_id=data["project_id"],
            type=data["dependency_type"],
            version_id=data["version_id"],
        )


@dataclass
class Version:
    id: str
    name: str
    number: str
    project_id: str
    game_versions: tuple[str]
    loaders: tuple[str]
    files: tuple[File, ...]
    dependencies: tuple[Dependency, ...]

    changelog: Optional[str] = None

    def __eq__(self, other: "Version") -> bool:
        return self.id == other.id

    def __repr__(self) -> str:
        return f"<Version: {self.id}({self.name})>"

    @property
    def modrinth_url(self) -> str:
        return f"{BASE_MODRINTH_URL}/mod/{self.project_id}/version/{self.id}"

    @classmethod
    def from_dict(cls, data: dict[str, any]) -> "Version":
        files = [File.from_dict(file_data) for file_data in data["files"]]
        dependencies = [
            Dependency.from_dict(dependency_data) for dependency_data in data["dependencies"]
        ]

        return cls(
            id=data["id"],
            name=data["name"],
            number=data["version_number"],
            project_id=data["project_id"],
            game_versions=data["game_versions"],
            loaders=data["loaders"],
            files=files,
            dependencies=dependencies,
            changelog=data["changelog"],
        )


@dataclass
class Project:
    id: str
    name: str
    game_versions: tuple[str]
    loaders: tuple[str]
    type: ProjectType
    version_ids: tuple[str, ...]

    description: Optional[str] = None

    def __eq__(self, other: "Project") -> bool:
        return self.id == other.id

    def __repr__(self) -> str:
        return f"<Project: {self.id}({self.name})>"

    @property
    def modrinth_url(self) -> str:
        return f"{BASE_MODRINTH_URL}/mod/{self.id}"

    @classmethod
    def from_dict(cls, data: dict[str, any]) -> "Project":
        return cls(
            id=data["id"],
            name=data["title"],
            game_versions=data["game_versions"],
            loaders=data["loaders"],
            type=data["project_type"],
            version_ids=data["versions"],
            description=data["description"],
        )


@dataclass
class Collection:
    id: str
    name: str
    project_ids: tuple[str, ...]

    description: Optional[str] = None

    @property
    def modrinth_url(self) -> str:
        return f"{BASE_MODRINTH_URL}/collection/{self.id}"

    def __repr__(self) -> str:
        return f"<Collection: {self.id}|{self.name}>"

    @classmethod
    def from_dict(cls, data: dict[str, any]) -> "Collection":
        return cls(
            id=data["id"],
            name=data["name"],
            project_ids=data["projects"],
            description=data["description"],
        )


@dataclass
class Entry:
    project: Project
    version: Version
