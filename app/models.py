from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, TypedDict

from .enums import (
    ClientSideType,
    DependencyType,
    FileType,
    MonetizationStatus,
    ProjectRequestedStatus,
    ProjectStatus,
    ProjectType,
    ServerSideType,
    VersionRequestedStatus,
    VersionStatus,
    VersionType,
)


class DonationUrl(TypedDict):
    id: str
    platform: str
    url: str


class ModeratorMessage(TypedDict):
    message: str
    body: str | None


class License(TypedDict):
    id: str
    name: str
    url: str | None


class GalleryImage(TypedDict):
    created: datetime
    description: str | None
    featured: bool
    ordering: int
    title: str | None
    url: str


class Dependency(TypedDict):
    dependency_type: DependencyType
    file_name: str | None
    project_id: str | None
    version_id: str | None


class FileHash(TypedDict):
    sha512: str
    sha1: str


class File(TypedDict):
    file_type: FileType | None
    filename: str
    hashes: list[FileHash]
    primary: bool
    size: int
    url: str


@dataclass
class Project:
    additional_categories: list[str]
    approved: datetime | None
    body: str
    body_url: str | None
    categories: list[str]
    client_side: ClientSideType
    color: int
    description: str
    discord_url: str | None
    donation_urls: list[DonationUrl]
    downloads: int
    followers: int
    gallery: list[GalleryImage]
    game_versions: list[str]
    icon_url: str | None
    id: str
    issues_url: str | None
    license: License
    loaders: list[str]
    moderator_message: ModeratorMessage
    monetization_status: MonetizationStatus
    project_type: ProjectType
    published: datetime
    queued: datetime | None
    requested_status: ProjectRequestedStatus | None
    server_side: ServerSideType
    slug: str
    source_url: str | None
    status: ProjectStatus
    team: str
    thread_id: str
    title: str
    updated: datetime
    versions: list[str]
    wiki_url: str | None

    organization: Any  # Not described in docs

    def __repr__(self) -> str:
        return f"Project<{self.title} | ({self.id})>"

    def to_console_print(self, index: int) -> str:
        index_str = f"[black]{str(index + 1).zfill(2).rjust(3)}. [/black]"
        title = f"[bold white]{self.title}[/bold white]"
        client_side = (
            "[blue] [Client][/blue]" if self.client_side == ClientSideType.REQUIRED else ""
        )
        server_side = (
            "[magenta] [Server][/magenta]" if self.server_side == ServerSideType.REQUIRED else ""
        )

        return index_str + title + client_side + server_side


@dataclass
class Version:
    author_id: str
    changelog: str
    changelog_url: str | None
    date_published: datetime
    dependencies: list[Dependency]
    downloads: int
    featured: bool
    files: list[File]
    game_versions: list[str]
    id: str
    loaders: list[str]
    name: str
    project_id: str
    requested_status: VersionRequestedStatus | None
    status: VersionStatus
    version_number: str
    version_type: VersionType

    required_by: list[str] = field(
        default_factory=list[str]
    )  # Used to store project ids who require this version

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented

        return self.id == other.id

    def __repr__(self) -> str:
        return f"Version<{self.name} | ({self.project_id} / {self.id})>"

    def version_type_to_console_print(self) -> str:
        text = self.version_type.capitalize().ljust(7)

        if self.version_type == VersionType.ALPHA:
            return f"[red]{text}[/red]"

        if self.version_type == VersionType.BETA:
            return f"[yellow]{text}[/yellow]"

        return f"[green]{text}[/green]"

    def to_console_print(self, projects: list[Project]) -> str:
        required_by = ", ".join(
            [project.title for project in projects if project.id in self.required_by]
        )
        if required_by:
            required_by = f" | Required by: {required_by}"
        return f"     {self.version_type_to_console_print()}[black] | {self.version_number.ljust(32)}{required_by}[/black]"


@dataclass
class Collection:  # Defined by me until supported by Labyrinth.
    id: str
    projects: list[str]
    title: str

    def __repr__(self) -> str:
        return f"Collection<{self.title} | ({self.id})>"
