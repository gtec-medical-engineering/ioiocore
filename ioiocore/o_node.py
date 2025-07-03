from typing import Any
from .o_port import OPort
from .node import Node
from .i_node import INode
from copy import deepcopy
from .constants import Constants

import ioiocore.imp as imp


class ONode(Node):

    """
    A class representing an output node, inheriting from Node.
    """

    class Configuration(Node.Configuration):
        """
        Configuration class for ONode.
        """

        class Keys(Node.Configuration.Keys):
            """
            Keys for the ONode configuration.
            """
            OUTPUT_PORTS = "output_ports"
            DECIMATION_FACTOR = Constants.Keys.DECIMATION_FACTOR  # "decimation_factor"  # noqa: E501

        def __init__(self, **kwargs):
            """
            Initializes the configuration for ONode.

            Parameters
            ----------
            **kwargs : additional keyword arguments
                Other configuration options, including output ports.
            """
            # remove output_ports from kwargs;
            # if not present, assign a default value. This avoids errors when
            # deserialization is performed.
            op_key = self.Keys.OUTPUT_PORTS
            output_ports: list = kwargs.pop(op_key,
                                            [OPort.Configuration()])  # noqa: E501

            M_key = self.Keys.DECIMATION_FACTOR
            decimation_factor: int = kwargs.pop(M_key, 1)

            if decimation_factor is None:
                decimation_factor = 1
            if type(decimation_factor) is not int:
                raise TypeError("decimation_factor must be an integer.")
            if decimation_factor < 1:
                raise ValueError("decimation_factor must be an integer "
                                 "multiple of 1.")

            super().__init__(output_ports=output_ports,
                             decimation_factor=decimation_factor,
                             **kwargs)

    _IMP_CLASS = imp.ONodeImp
    _imp: _IMP_CLASS  # for type hinting  # type: ignore
    config: Configuration  # for type hinting

    def __init__(self,
                 output_ports: list = None,
                 decimation_factor: int = None,
                 **kwargs):
        """
        Initializes the ONode.

        Parameters
        ----------
        output_ports : list of OPort.Configuration, optional
            A list of output port configurations (default is None).
        **kwargs : additional keyword arguments
            Other configuration options.
        """
        self.create_config(output_ports=output_ports,
                           decimation_factor=decimation_factor,
                           **kwargs)
        self.create_implementation()
        super().__init__(**self.config)

    def connect(self,
                output_port: str,
                target: INode,
                input_port: str):
        """
        Connects an output port to an input port of a target node.

        Parameters
        ----------
        output_port : str
            The name of the output port.
        target : INode
            The target node to which the output port will be connected.
        input_port : str
            The name of the input port on the target node.
        """
        self._imp.connect(output_port, target._imp, input_port)

    def disconnect(self,
                   output_port: str,
                   target: INode,
                   input_port: str):
        """
        Disconnects an output port from an input port of a target node.

        Parameters
        ----------
        output_port : str
            The name of the output port.
        target : INode
            The target node from which the output port will be disconnected.
        input_port : str
            The name of the input port on the target node.
        """
        self._imp.disconnect(output_port, target._imp, input_port)

    def setup(self,
              data: dict,
              port_context_in: dict) -> dict:
        """
        Sets up the ONode.

        Parameters
        ----------
        data : dict
            A dictionary containing setup data.
        port_context_in : dict
            A dictionary containing input port context.

        Returns
        -------
        dict
            A dictionary containing output port context.
        """
        port_context_out: dict = {}
        op_config = self.config[self.config.Keys.OUTPUT_PORTS]
        for port_idx in range(len(op_config)):
            port_name = op_config[port_idx][self.Configuration.Keys.NAME]
            port_context_out[port_name] = deepcopy(dict(op_config[port_idx]))
            del port_context_out[port_name][self.Configuration.Keys.NAME]
            del port_context_out[port_name][self.Configuration.Keys.ID]
        return port_context_out

    def cycle(self, data: dict = {}):
        """
        Performs a cycle operation on the ONode.

        Parameters
        ----------
        data : dict, optional
            A dictionary containing the data for the cycle operation (default
            is an empty dictionary).
        """
        self._imp._cycle(data)

    def is_decimation_step(self):
        return self._imp.is_decimation_step()
