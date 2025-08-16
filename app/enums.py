from enum import StrEnum, auto


class ClientSideType(StrEnum):
    OPTIONAL = auto()
    REQUIRED = auto()
    UNKNOWN = auto()
    UNSUPPORTED = auto()


class ServerSideType(StrEnum):
    OPTIONAL = auto()
    REQUIRED = auto()
    UNKNOWN = auto()
    UNSUPPORTED = auto()


class ProjectStatus(StrEnum):
    APPROVED = auto()
    ARCHIVED = auto()
    DRAFT = auto()
    PRIVATE = auto()
    PROCESSING = auto()
    REJECTED = auto()
    SCHEDULED = auto()
    UNKNOWN = auto()
    UNLISTED = auto()
    WITHHELD = auto()


class ProjectRequestedStatus(StrEnum):
    APPROVED = auto()
    ARCHIVED = auto()
    DRAFT = auto()
    PRIVATE = auto()
    UNLISTED = auto()


class ProjectType(StrEnum):
    MOD = auto()
    MODPACK = auto()
    RESOURCEPACK = auto()
    SHADER = auto()


class MonetizationStatus(StrEnum):
    DEMONETIZED = auto()
    FORCE_DEMONETIZED = "force-demonetized"
    MONETIZED = auto()


class DependencyType(StrEnum):
    EMBEDDED = auto()
    INCOMPATIBLE = auto()
    OPTIONAL = auto()
    REQUIRED = auto()


class VersionType(StrEnum):
    ALPHA = auto()
    BETA = auto()
    RELEASE = auto()


class VersionStatus(StrEnum):
    ARCHIVED = auto()
    DRAFT = auto()
    LISTED = auto()
    SCHEDULED = auto()
    UNKNOWN = auto()
    UNLISTED = auto()


class VersionRequestedStatus(StrEnum):
    ARCHIVED = auto()
    DRAFT = auto()
    LISTED = auto()
    UNLISTED = auto()


class FileType(StrEnum):
    OPTIONAL_RESOURCE_PACK = "optional-resource-pack"
    REQUIRED_RESOURCE_PACK = "required-resource-pack"
