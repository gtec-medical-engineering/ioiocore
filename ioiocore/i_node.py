from enum import Enum
from typing import Any

from .i_port import IPort
from .node import Node

import ioiocore.imp as imp


class INode(Node):
    """
    Represents a node that has only input ports.
    """

    class Configuration(Node.Configuration):
        """
        Configuration class for INode.
        """

        class Keys(Node.Configuration.Keys):
            """
            Keys for the INode configuration.
            """
            INPUT_PORTS = 'input_ports'

        def __init__(self,
                     input_ports: list = None,
                     **kwargs):
            """
            Initializes the configuration for INode.

            Parameters
            ----------
            input_ports : list of IPort.Configuration, optional
                A list of input port configurations (default is None).
            **kwargs : additional keyword arguments
                Other configuration options.
            """
            if input_ports is None:
                input_ports = [IPort.Configuration()]
            super().__init__(input_ports=input_ports,
                             **kwargs)

    _IMP_CLASS = imp.INodeImp
    _imp: _IMP_CLASS  # for type hinting  # type: ignore
    config: Configuration  # for type hinting

    def __init__(self,
                 input_ports: list = None,
                 **kwargs):
        """
        Initializes the INode.

        Parameters
        ----------
        input_ports : list of IPort.Configuration, optional
            A list of input port configurations (default is None).
        **kwargs : additional keyword arguments
            Other configuration options.
        """
        self.create_config(input_ports=input_ports,
                           **kwargs)
        self.create_implementation()
        super().__init__(**self.config)

    def start(self):
        """
        Starts the node.
        """
        self._imp.start()

    def stop(self):
        """
        Stops the node.
        """
        self._imp.stop()

    def setup(self,
              data: dict,
              port_context_in: dict) -> dict:
        """
        Sets up the INode.

        Parameters
        ----------
        data : dict
            A dictionary containing the data.
        port_context_in : dict
            A dictionary containing port context.

        Returns
        -------
        dict
            An empty dictionary, because INode has no output ports.
        """
        return {}
