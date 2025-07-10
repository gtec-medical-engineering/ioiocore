from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

from .portable import Portable
from .logging import Logger
from .constants import Constants
from .context import Context

import ioiocore.imp as imp  # type: ignore


class Node(ABC, Portable):
    """
    Abstract base class representing a node in a signal processing pipeline.

    Inherits from ABC and Portable, and provides the core structure for
    setting up and running the Node, including managing its configuration,
    implementation, logger, and state.

    Attributes
    ----------
    _IMP_CLASS : type
        The implementation class for the Node.
    _imp : _IMP_CLASS
        The instance of the implementation class for the Node.
    config : Configuration
        The configuration object for the Node.
    """

    _IMP_CLASS = imp.NodeImp

    class Configuration(Portable.Configuration):
        """
        Configuration class for the Node

        Attributes
        ----------
        Keys
            The configuration keys.
        """

        class Keys(Portable.Configuration.Keys):
            """Configuration keys."""
            NAME = "name"

        def __init__(self,
                     name: str = None,
                     **kwargs):
            """
            Initialize the Node configuration.

            Parameters
            ----------
            name : str, optional
                The name of the Node (default is the class name).
            kwargs : additional keyword arguments
                Other configuration parameters passed to the base class.
            """
            if name is None:
                name = self.__class__.__qualname__.split('.')[0]
            super().__init__(name=name, **kwargs)

    _imp: _IMP_CLASS  # for type hinting  # type: ignore
    config: Configuration  # for type hinting

    def __init__(self,
                 name: str = None,
                 **kwargs):
        """
        Initialize the Node.

        Parameters
        ----------
        name : str, optional
            The name of the Node (default is None).
        kwargs : additional keyword arguments
            Other parameters passed to create the Node configuration.
        """
        self.create_config(name=name, **kwargs)
        self.create_implementation()
        self._imp.setup_handler = self.setup
        self._imp.step_handler = self.step
        super().__init__(**self.config)

    def start(self):
        """
        Start the Node.

        Starts the internal implementation of the Node.
        """
        self._imp.start()

    def stop(self):
        """
        Stop the Node.

        Stops the internal implementation of the Node.
        """
        self._imp.stop()

    def set_logger(self, logger: Logger):
        self._imp.set_logger(logger)

    def log(self, msg: str, type: Constants.LogTypes = None):
        self._imp.log(msg=msg, type=type)

    @property
    def name(self) -> str:
        return self._imp.name

    def get_load(self) -> float:
        """
        Get the current load of the Node.

        Returns
        -------
        float
            The load value of the Node.
        """
        return self._imp.get_load()

    def get_counter(self) -> int:
        """
        Get the current counter value of the Node.

        Returns
        -------
        int
            The counter value of the Node.
        """
        return self._imp.get_counter()

    def get_state(self) -> 'Constants.States':
        """
        Get the current state of the Node.

        Returns
        -------
        Constants.States
            The current state of the Node.
        """
        return self._imp.get_state()

    def get_context(self) -> 'Context':
        return self._imp.get_context()

    def __getitem__(self, port_name: str):
        return {"node": self, "port": port_name}

    @abstractmethod
    def setup(self,
              data: dict,
              port_context_in: dict) -> dict:
        """
        Abstract method to setup the Node.

        This method should be implemented to define the setup logic for the
        Node.

        Parameters
        ----------
        data : dict
            The input data to configure the Node.
        port_context_in : dict
            Context for the input ports.

        Returns
        -------
        dict
            The configuration of the output ports.
        """
        pass  # pragma: no cover

    @abstractmethod
    def step(self, data: dict) -> dict:
        """
        Abstract method for the Node's step function.

        This method should be implemented to define the processing logic for
        each step of the Node.

        Parameters
        ----------
        data : dict
            The input data to process.

        Returns
        -------
        dict
            The processed data after applying the step logic.
        """
        pass  # pragma: no cover
