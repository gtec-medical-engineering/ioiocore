from enum import Enum
from typing import Optional

import ioiocore.imp as imp
from .interface import Interface

from .constants import Constants


class LogEntry(Interface):
    """
    Represents a log entry containing type, stack trace, and message.
    """

    _IMP_CLASS = imp.LogEntryImp
    _imp: _IMP_CLASS  # for type hinting  # type: ignore

    def __init__(self, type: Constants.LogTypes, stack: str, message: str):
        """
        Initialize a log entry.

        Parameters
        ----------
        type : LogType
            Type of the log entry.
        stack : str
            Stack trace information.
        message : str
            Log message.
        """
        self.create_implementation(type=type,
                                   stack=stack,
                                   message=message)

    def __getitem__(self, key):
        """
        Retrieve an item from the log entry.

        Parameters
        ----------
        key : Any
            The key to retrieve.

        Returns
        -------
        Any
            The corresponding value.
        """
        return self._imp[key]

    def __iter__(self):
        """
        Iterate over the log entry fields.
        """
        return iter(self._imp)

    def __len__(self):
        """
        Get the number of fields in the log entry.

        Returns
        -------
        int
            The number of fields.
        """
        return len(self._imp)

    def keys(self):
        """
        Retrieve all keys in the log entry.

        Returns
        -------
        Iterable
            An iterable of keys.
        """
        return self._imp.keys()

    def values(self):
        """
        Retrieve all values in the log entry.

        Returns
        -------
        Iterable
            An iterable of values.
        """
        return self._imp.values()

    def __repr__(self):
        """
        Represent the log entry as a string.

        Returns
        -------
        str
            String representation of the log entry.
        """
        return f"LogEntry({self._imp})"

    def to_formatted_string(self) -> str:
        """
        Retrieve a formatted string representation of the log entry.

        Returns
        -------
        str
            Formatted log entry string.
        """
        return self._imp.to_formatted_string()


class Logger(Interface):
    """
    Logger interface for writing and retrieving log entries.
    """

    _IMP_CLASS = imp.LoggerImp
    _imp: _IMP_CLASS  # type: ignore

    def __init__(self, directory: Optional[str] = None):
        """
        Initialize a logger instance.

        Parameters
        ----------
        directory : Optional[str], optional
            Directory for log storage, by default None.
        """
        self.create_implementation(directory=directory)

    def write(self, type: Constants.LogTypes, message: str) -> LogEntry:
        """
        Write a log entry.

        Parameters
        ----------
        type : LogType
            Type of the log entry.
        message : str
            Log message.

        Returns
        -------
        LogEntry
            The created log entry.
        """
        return self._imp.write(type, message)

    def flush(self):
        """
        Flush the log buffer.
        """
        self._imp.flush()

    def get_all(self) -> list:
        """
        Retrieve all log entries.

        Returns
        -------
        list
            A list of all log entries.
        """
        return self._imp.get_all()

    def get_by_type(self, type: Constants.LogTypes) -> list:
        """
        Retrieve log entries of a specific type.

        Parameters
        ----------
        type : LogType
            The log type to filter by.

        Returns
        -------
        list
            A list of matching log entries.
        """
        return self._imp.get_by_type(type)

    def has_entries(self, type: Constants.LogTypes = None) -> bool:
        """
        Check if there are log entries of a specific type.

        Parameters
        ----------
        type : LogType, optional
            The log type to check, by default None.

        Returns
        -------
        bool
            True if there are matching log entries, False otherwise.
        """
        return self._imp.has_entries(type)

    def get_last_error(self) -> Optional[LogEntry]:
        """
        Retrieve the last logged error entry.

        Returns
        -------
        Optional[LogEntry]
            The last error log entry, if available.
        """
        return self._imp.get_last_error()

    @property
    def file_name(self) -> str:
        """
        Retrieve the log file name.

        Returns
        -------
        str
            The log file name.
        """
        return self._imp.file_name
