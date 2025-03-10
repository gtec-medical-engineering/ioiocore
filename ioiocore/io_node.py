from typing import Any, Dict
from copy import deepcopy
from .i_node import INode
from .o_node import ONode
from .i_node import IPort
from .o_node import OPort

import ioiocore.imp as imp


class IONode(INode, ONode):
    """
    A class representing a node with input and output ports, inheriting from
    both INode and ONode.
    """

    class Configuration(INode.Configuration, ONode.Configuration):
        """
        Configuration class for IONode.
        """

        class Keys(INode.Configuration.Keys, ONode.Configuration.Keys):
            """
            Keys for the IONode configuration (none except the inherited ones).
            """
            pass

        def __init__(self,
                     input_ports: list[IPort.Configuration] = None,
                     output_ports: list[OPort.Configuration] = None,
                     **kwargs):
            """
            Initializes the configuration for IONode.

            Parameters
            ----------
            input_ports : list of IPort.Configuration, optional
                A list of input port configurations (default is None).
            output_ports : list of OPort.Configuration, optional
                A list of output port configurations (default is None).
            **kwargs : additional keyword arguments
                Other configuration options.
            """
            if input_ports is None:
                input_ports = [IPort.Configuration()]
            if output_ports is None:
                output_ports = [OPort.Configuration()]

            INode.Configuration.__init__(self,
                                         input_ports=input_ports,
                                         output_ports=output_ports,
                                         **kwargs)
            ONode.Configuration.__init__(self,
                                         input_ports=input_ports,
                                         output_ports=output_ports,
                                         **kwargs)

    _IMP_CLASS = imp.IONodeImp
    _imp: _IMP_CLASS  # for type hinting  # type: ignore
    config: Configuration  # for type hinting

    def __init__(self,
                 input_ports: list[IPort.Configuration] = None,
                 output_ports: list[OPort.Configuration] = None,
                 **kwargs):
        """
        Initializes the IONode.

        Parameters
        ----------
        input_ports : list of IPort.Configuration, optional
            A list of input port configurations (default is None).
        output_ports : list of OPort.Configuration, optional
            A list of output port configurations (default is None).
        **kwargs : additional keyword arguments
            Other configuration options.
        """
        self.create_config(input_ports=input_ports,
                           output_ports=output_ports,
                           **kwargs)
        self.create_implementation()
        super().__init__(**self.config)

    def setup(self,
              data: Dict[str, Any],
              port_metadata_in: Dict[str, dict]) -> Dict[str, dict]:
        """
        Standard implementation of the setup method. Only allowed for
        one input port. If subclasses have more than one input port, they
        must overload this method.

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

        Raises
        ------
        ValueError
            If the number of input ports is not exactly one.
        """
        if len(port_metadata_in) != 1:
            raise ValueError("Default implementation of setup() requires "
                             "exactly one input port. Please overload this "
                             "method appropriately.")
        port_metadata_out: Dict[str, dict] = {}
        ip_config = self.config[self.config.Keys.INPUT_PORTS]
        ip_names = [s[self.Configuration.Keys.NAME] for s in ip_config]
        op_config = self.config[self.config.Keys.OUTPUT_PORTS]
        op_names = [s[self.Configuration.Keys.NAME] for s in op_config]
        for ip_name in ip_names:
            for op_name in op_names:
                port_metadata_out[op_name] = deepcopy(port_metadata_in[ip_name])  # noqa: E501
        return port_metadata_out
