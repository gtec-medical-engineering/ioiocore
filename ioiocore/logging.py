from enum import Enum
from typing import Optional, Union

import ioiocore.imp as imp
from .interface import Interface
from .constants import Constants


class LogEntry(Interface):
    """
    Represents a log entry containing type, source trace, and message.
    """

    _IMP_CLASS = imp.LogEntryImp
    _imp: _IMP_CLASS  # for type hinting  # type: ignore

    def __init__(self, type: Constants.LogTypes, source: dict, message: str):
        """
        Initialize a log entry.

        Parameters
        ----------
        type : LogType
            Type of the log entry.
        source : str
            source trace information.
        message : str
            Log message.
        """
        self.create_implementation(type=type,
                                   source=source,
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

    def write(self,
              type: Constants.LogTypes,
              message: Union[str, Exception]) -> LogEntry:
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

    def stop(self):
        """
        Stop the logger: flush pending entries, close the log file and
        join the writer thread. Safe to call more than once.
        """
        self._imp.stop()

    def is_persistent(self) -> bool:
        """
        Whether log entries are written to a file.

        Returns
        -------
        bool
            True if a log file is being written, False if the logger is
            operating in memory only (e.g. the log directory could not be
            created).
        """
        return self._imp.is_persistent()

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

    def get_last(self, type: Constants.LogTypes,
                 opaque: bool = False) -> Optional[LogEntry]:
        """
        Retrieve the last logged entry of a specific type.

        Parameters
        ----------
        type : LogType
            The log type to filter by.
        opaque : bool, optional
            Whether to return the last log entry only once (returning
            None on repeated calls).

        Returns
        -------
        Optional[LogEntry]
            The last log entry of the specified type, if available.
        """
        return self._imp.get_last(type=type, opaque=opaque)

    def get_incident(self, type: Constants.LogTypes,
                     opaque: bool = False) -> Optional[LogEntry]:
        """
        Retrieve the last ERROR or WARNING from the never-evicted record.

        Unlike :meth:`get_last`, this is unaffected by ring-buffer
        eviction, so a burst of log traffic cannot hide an incident.

        Parameters
        ----------
        type : LogType
            The incident type to retrieve (ERROR or WARNING).
        opaque : bool, optional
            Whether to return a given incident only once.

        Returns
        -------
        Optional[LogEntry]
            The last incident of the given type, if any.
        """
        return self._imp.get_incident(type=type, opaque=opaque)

    @property
    def file_name(self) -> str:
        """
        Retrieve the log file name.

        Returns
        -------
        str
            The log file name, or None when file logging is unavailable.
        """
        return self._imp.file_name

    @property
    def file_error(self) -> str:
        """
        Why file logging is unavailable.

        File logging is optional -- an unwritable directory must not stop
        a pipeline -- but without the reason a reader is left guessing
        between a permissions problem, a missing drive and a bad path.

        Returns
        -------
        str
            A description including the exception type, or None when the
            log file was created successfully.
        """
        return self._imp.file_error

    @property
    def attempted_file(self) -> str:
        """
        The path file logging was attempted at, when it failed.

        Returns
        -------
        str
            The path, or None when the log file was created.
        """
        return self._imp.attempted_file
