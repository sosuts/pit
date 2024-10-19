from enum import StrEnum, auto


class ObjectType(StrEnum):
    BLOB = auto()
    TREE = auto()
    COMMIT = auto()
    TAG = auto()


class ProjectFileType(StrEnum):
    FETCH_HEAD = auto()
    HEAD = auto()
    BRANCHES = auto()
    CONFIG = auto()
    DESCRIPTION = auto()
    HOOKS = auto()
    INDEX = auto()
    INFO = auto()
    OBJECTS = auto()
    REFS = auto()
