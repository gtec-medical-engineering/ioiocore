from typing import Union
from .node import Node
from .o_node import ONode
from .i_node import INode
from .processing_element import ProcessingElement
from .constants import Constants
from .interface import Interface

import ioiocore.imp as imp  # type: ignore


class Pipeline(Interface):
    """
    A class representing a pipeline, inheriting from Interface.
    Manages nodes and their connections within the pipeline.

    Supports both Node types (INode, ONode, IONode) and Chain types
    (IChain, OChain, IOChain).
    """

    _imp: imp.PipelineImp  # for type hinting

    def __init__(self, directory: str = None):
        """
        Initializes the pipeline.

        Parameters
        ----------
        directory : str, optional
            Directory to be used for the pipeline (default is None).
        """
        self._imp = imp.PipelineImp(directory=directory)

    def add_node(self, node: ProcessingElement):
        """
        Adds a node or chain to the pipeline.

        Parameters
        ----------
        node : ProcessingElement
            The node or chain to add to the pipeline.
        """
        self._imp.add_node(node)

    def connect(self,
                source: 'ONode | dict',
                target: 'INode | dict'):
        """
        Connect a source element to a target element.

        Parameters
        ----------
        source : ONode, OChain, IOChain, or dict
            The source element with output ports, or a dict with
            'node' and 'port' keys.
        target : INode, IChain, IOChain, or dict
            The target element with input ports, or a dict with
            'node' and 'port' keys.
        """
        self._imp.connect(source, target)

    def start(self):
        """
        Starts the pipeline.
        """
        self._imp.start()

    def stop(self):
        """
        Stops the pipeline.
        """
        self._imp.stop()

    def close(self):
        """
        Dispose the pipeline and release logging resources.

        Stops the pipeline if it is still running, then shuts down the
        logger (flushing pending entries, closing the log file and joining
        its writer thread). The logger survives ordinary start()/stop()
        cycles, so call close() (or use the pipeline as a context manager)
        once the pipeline is no longer needed. Safe to call more than once.
        """
        self._imp.close()

    def is_logging_persistent(self) -> bool:
        """
        Whether the pipeline writes a persistent log file.

        Returns
        -------
        bool
            False if the log file could not be created and logging is
            in-memory only (no persistent audit trail).
        """
        return self._imp.is_logging_persistent()

    def __enter__(self) -> 'Pipeline':
        """Enter the runtime context, returning the pipeline itself."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Exit the runtime context, disposing the pipeline."""
        self.close()
        return False

    def get_state(self) -> Constants.States:
        """
        Returns the current state of the pipeline.

        Returns
        -------
        Constants.States
            The current state of the pipeline.
        """
        return self._imp.get_state()

    def get_condition(self) -> Constants.Conditions:
        """
        Returns the current condition of the pipeline.

        Returns
        -------
        Constants.Conditions
            The current condition of the pipeline.
        """
        return self._imp.get_condition()

    def get_last_error(self):
        """
        Returns the last error recorded by the pipeline.

        Returns
        -------
        LogEntry or None
            The failing entry, carrying the message, the node and the
            source location, or None if nothing has failed. Note this is
            an entry rather than a string: the annotation previously said
            `str`, which was wrong and hid the node and location a reader
            needs.
        """
        return self._imp.get_last_error()

    def add_error_handler(self, handler) -> None:
        """
        Register a callable invoked once when the run fails.

        A failure is detected asynchronously, after `start()` has already
        returned, so there is nothing for `start()` to raise. Without a
        handler the only report is printed to the console -- which a GUI
        application may never show. Use this to put the failure in front
        of the user, and `raise_if_failed()` where an exception is wanted
        instead.

        The handler runs on the monitoring thread, so it should hand the
        news to whatever owns the user interface rather than doing work
        itself. An exception raised inside it is logged and swallowed:
        that thread is the only channel that reports failures and must
        not die reporting one.

        Parameters
        ----------
        handler : Callable
            Called with the failing log entry.
        """
        self._imp.add_error_handler(handler)

    def raise_if_failed(self) -> None:
        """
        Raise if the run has failed, naming the node and the cause.

        For a script that would otherwise carry on past a dead pipeline.

        Raises
        ------
        RuntimeError
            If the pipeline is in an error condition.
        """
        self._imp.raise_if_failed()

    def get_elapsed_time(self) -> float:
        """
        Returns the elapsed time since the pipeline started.

        Returns
        -------
        float
            The elapsed time in seconds.
        """
        return self._imp.get_elapsed_time()

    def get_backlog(self) -> int:
        """
        Returns the maximum input-queue backlog across the pipeline.

        This is the number of items queued on the most-backed-up input
        port of any element (including nodes inside chains). A steadily
        growing value indicates a consumer that cannot keep up with its
        input rate.

        Returns
        -------
        int
            The maximum number of queued items on any input port.
        """
        return self._imp.get_backlog()

    def serialize(self) -> dict:
        """
        Serializes the pipeline to a dictionary.

        Returns
        -------
        dict
            A dictionary representing the serialized pipeline.
        """
        return self._imp.serialize()

    @staticmethod
    def deserialize(data: dict) -> 'Pipeline':
        """
        Deserializes the pipeline from a dictionary.

        Parameters
        ----------
        data : dict
            A dictionary containing the serialized pipeline data.

        Returns
        -------
        Pipeline
            The deserialized pipeline object.
        """
        return imp.PipelineImp.deserialize(data)

    def log(self, msg: Union[str, Exception],
            type: Constants.LogTypes = None):
        """
        Writes a log entry to the pipeline.

        Parameters
        ----------
        entry : str
            The log entry to write.
        """
        self._imp.log(msg=msg, type=type)
