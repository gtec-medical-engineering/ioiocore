from typing import Any
from .o_port import OPort
from .node import Node
from .i_node import INode

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
            super().__init__(output_ports=output_ports,
                             **kwargs)

    _IMP_CLASS = imp.ONodeImp
    _imp: _IMP_CLASS  # for type hinting  # type: ignore
    config: Configuration  # for type hinting

    def __init__(self,
                 output_ports: list = None,
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
                           **kwargs)
        self.create_implementation()
        super().__init__(**self.config)
        self.create_config(output_ports=output_ports,
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
              port_metadata_in: dict) -> dict:
        """
        Sets up the ONode.

        Parameters
        ----------
        data : dict
            A dictionary containing setup data.
        port_metadata_in : dict
            A dictionary containing input port metadata.

        Returns
        -------
        dict
            A dictionary containing output port metadata.
        """
        port_metadata_out: dict = {}
        op_config = self.config[self.config.Keys.OUTPUT_PORTS]
        op_names = [s[self.Configuration.Keys.NAME] for s in op_config]
        md = self.config.get_metadata()
        for port_name in op_names:
            port_metadata_out[port_name] = md
        return port_metadata_out

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
