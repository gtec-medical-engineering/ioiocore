from enum import Enum
from typing import List, Optional

import ioiocore.imp as imp
from .interface import Interface


class LogType(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class LogEntry(Interface):

    _IMP_CLASS = imp.LogEntryImp
    _imp: _IMP_CLASS  # for type hinting  # type: ignore

    def __init__(self, type: LogType, stack: str, message: str):
        self.create_implementation(type=type,
                                   stack=stack,
                                   message=message)

    def __getitem__(self, key):
        return self._imp[key]

    def __iter__(self):
        return iter(self._imp)

    def __len__(self):
        return len(self._imp)

    def keys(self):
        return self._imp.keys()

    def values(self):
        return self._imp.values()

    def __repr__(self):
        return f"LogEntry({self._imp})"

    def to_formatted_string(self) -> str:
        return self._imp.to_formatted_string()


class Logger(Interface):

    _IMP_CLASS = imp.LoggerImp
    _imp: _IMP_CLASS  # type: ignore

    def __init__(self, directory: Optional[str] = None):
        self.create_implementation(directory=directory)

    def write(self, type: LogType, message: str) -> LogEntry:
        return self._imp.write(type, message)

    def flush(self):
        self._imp.flush()

    def get_all(self) -> List[LogEntry]:
        return self._imp.get_all()

    def get_by_type(self, type: LogType) -> List[LogEntry]:
        return self._imp.get_by_type(type)

    def has_entries(self, type: LogType = None) -> bool:
        return self._imp.has_entries(type)

    def get_last_error(self) -> Optional[LogEntry]:
        return self._imp.get_last_error()

    def get_file_name(self) -> str:
        return self._imp.get_file_name()
