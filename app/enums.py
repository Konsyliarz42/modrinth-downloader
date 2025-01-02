from enum import StrEnum, auto


class DependencyType(StrEnum):
    REQUIRED = auto()
    OPTIONAL = auto()
    INCOMPATIBLE = auto()
    EMBEDDED = auto()


class ProjectType(StrEnum):
    MOD = auto()
    MODPACK = auto()
    RESOURCEPACK = auto()
    SHADER = auto()
