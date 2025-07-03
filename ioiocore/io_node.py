from typing import Any
from copy import deepcopy
from .i_node import INode
from .o_node import ONode
from .i_node import IPort
from .o_node import OPort
from .constants import Constants

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
                     input_ports: list = None,
                     output_ports: list = None,
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
                 input_ports: list = None,
                 output_ports: list = None,
                 **kwargs):
        """
        Initializes the IONode.

        Parameters
        ----------
        input_ports : list of IPort.Configuration, optional
            A list of input port configurations (default is None).
        output_ports : list of OPort.Configuration, optional
            A list of output port configurations (default is None).
        decimation_factor : factor by which the output data is decimated
            (default is 1).
        **kwargs : additional keyword arguments
            Other configuration options.
        """
        self.create_config(input_ports=input_ports,
                           output_ports=output_ports,
                           **kwargs)
        self.create_implementation()
        super().__init__(**self.config)

    def setup(self,
              data: dict,
              port_context_in: dict) -> dict:
        """
        Standard implementation of the setup method. Only allowed for
        one input port. If subclasses have more than one input port, they
        must overload this method.

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

        Raises
        ------
        ValueError
            If the number of input ports is not exactly one.
        """
        if len(port_context_in) != 1:
            raise ValueError("Default implementation of setup() requires "
                             "exactly one input port. Please overload this "
                             "method appropriately.")
        port_context_out: dict = {}
        ip_config = self.config[self.config.Keys.INPUT_PORTS]
        ip_names = [s[self.Configuration.Keys.NAME] for s in ip_config]
        op_config = self.config[self.config.Keys.OUTPUT_PORTS]
        op_names = [s[self.Configuration.Keys.NAME] for s in op_config]
        for ip_name in ip_names:
            for op_name in op_names:
                md = deepcopy(port_context_in[ip_name])
                port_context_out[op_name] = md
        return port_context_out
