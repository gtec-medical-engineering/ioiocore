from typing import List, TYPE_CHECKING
from abc import abstractmethod

from .chain import Chain
from .i_port import IPort
from .o_port import OPort
from .node import Node

import ioiocore.imp as imp

if TYPE_CHECKING:
    from .i_node import INode  # pragma: no cover


class IOChain(Chain):
    """
    A chain with both input and output ports, processing
    data through a sequence of internal nodes.

    Structure: IONode => IONode => ... => IONode

    Input ports are exposed from the first internal node,
    and output ports are exposed from the last internal node,
    making this chain usable anywhere an IONode-like element is expected.

    Inheriting classes must implement ``create_internal_nodes()``, which
    returns the list of internal nodes.

    Example
    -------
    .. code-block:: python

        class MyProcessor(IOChain):
            def create_internal_nodes(self) -> List[Node]:
                return [
                    PreFilterNode(),   # IONode (input exposed)
                    TransformNode(),   # IONode
                    PostFilterNode()   # IONode (output exposed)
                ]
    """

    class Configuration(Chain.Configuration):
        """Configuration class for IOChain."""

        class Keys(Chain.Configuration.Keys):
            """Keys for the IOChain configuration."""
            INPUT_PORTS = "input_ports"
            OUTPUT_PORTS = "output_ports"

        def __init__(self,
                     input_ports: list = None,
                     output_ports: list = None,
                     **kwargs):
            """
            Initialize the IOChain configuration.

            Parameters
            ----------
            input_ports : list of IPort.Configuration, optional
                A list of input port configurations. If None, ports
                will be inherited from the first internal node.
            output_ports : list of OPort.Configuration, optional
                A list of output port configurations. If None, ports
                will be inherited from the last internal node.
            **kwargs : additional keyword arguments
                Other configuration options.
            """
            if input_ports is None:
                input_ports = [IPort.Configuration()]
            if output_ports is None:
                output_ports = [OPort.Configuration()]
            super().__init__(input_ports=input_ports,
                             output_ports=output_ports,
                             **kwargs)

    _IMP_CLASS = imp.IOChainImp
    _imp: _IMP_CLASS  # for type hinting  # type: ignore
    config: Configuration  # for type hinting

    def __init__(self,
                 input_ports: list = None,
                 output_ports: list = None,
                 **kwargs):
        """
        Initialize the IOChain.

        Parameters
        ----------
        input_ports : list of IPort.Configuration, optional
            A list of input port configurations (default is None).
        output_ports : list of OPort.Configuration, optional
            A list of output port configurations (default is None).
        **kwargs : additional keyword arguments
            Other configuration options.
        """
        kwargs = self._init_internal_nodes(**kwargs)
        self.create_config(input_ports=input_ports,
                           output_ports=output_ports,
                           **kwargs)
        self.create_implementation()
        self._validate_user_ports("input_ports", input_ports)
        self._validate_user_ports("output_ports", output_ports)

    @abstractmethod
    def create_internal_nodes(self) -> List[Node]:
        """
        Create and return the list of internal nodes.

        All nodes must be IONodes (have both input and output ports).

        Returns
        -------
        List[Node]
            List of internal IONodes forming the processing chain.
        """
        pass  # pragma: no cover

    def connect(self,
                output_port: str,
                target: 'INode',
                input_port: str):
        """
        Connect an output port to an input port of a target node.

        Parameters
        ----------
        output_port : str
            The name of the output port on this chain.
        target : INode
            The target node to connect to.
        input_port : str
            The name of the input port on the target node.
        """
        self._imp.connect(output_port, target, input_port)

    def disconnect(self,
                   output_port: str,
                   target: 'INode',
                   input_port: str):
        """
        Disconnect an output port from an input port of a target node.

        Parameters
        ----------
        output_port : str
            The name of the output port on this chain.
        target : INode
            The target node to disconnect from.
        input_port : str
            The name of the input port on the target node.
        """
        self._imp.disconnect(output_port, target, input_port)

    def get_input_port(self, port_name: str):
        """Get an input port by name from the first internal node."""
        return self._imp.get_port(port_name)

    def get_port(self, port_name: str):
        """Deprecated: use :meth:`get_input_port` instead."""
        import warnings
        warnings.warn("Chain.get_port() is deprecated; use "
                      "get_input_port() instead.",
                      DeprecationWarning, stacklevel=2)
        return self.get_input_port(port_name)

    def get_output_port(self, port_name: str):
        """Get an output port by name from the last internal node."""
        return self._imp.get_output_port(port_name)
