from .node import Node
from .o_node import ONode
from .i_node import INode
from .constants import Constants
from .interface import Interface

import ioiocore.imp as imp  # type: ignore


class Pipeline(Interface):
    """
    A class representing a pipeline, inheriting from Interface.
    Manages nodes and their connections within the pipeline.
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

    def add_node(self, node: Node):
        """
        Adds a node to the pipeline.

        Parameters
        ----------
        node : Node
            The node to add to the pipeline.
        """
        self._imp.add_node(node)

    def connect(self,
                source: 'ONode | dict',
                target: 'INode | dict'):
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

    def get_last_error(self) -> str:
        """
        Returns the last error message from the pipeline.

        Returns
        -------
        str
            The last error message.
        """
        return self._imp.get_last_error()

    def get_elapsed_time(self) -> float:
        """
        Returns the elapsed time since the pipeline started.

        Returns
        -------
        float
            The elapsed time in seconds.
        """
        return self._imp.get_elapsed_time()

    def get_load(self) -> float:
        """
        Returns the current load of the pipeline.

        Returns
        -------
        float
            The current load as a percentage.
        """
        return self._imp.get_load()

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

    def log(self, msg: str, type: Constants.LogTypes = None):
        """
        Writes a log entry to the pipeline.

        Parameters
        ----------
        entry : str
            The log entry to write.
        """
        self._imp.log(msg=msg, type=type)
