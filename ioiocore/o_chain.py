from typing import List, TYPE_CHECKING
from abc import abstractmethod

from .chain import Chain
from .o_port import OPort
from .node import Node

import ioiocore.imp as imp

if TYPE_CHECKING:
    from .i_node import INode  # pragma: no cover


class OChain(Chain):
    """
    A chain that generates output through a sequence of internal nodes.

    Structure: ONode => IONode => ... => IONode => <output>

    The output ports are exposed from the last internal node,
    making this chain usable anywhere an output element is expected.

    Inheriting classes must implement ``create_internal_nodes()``, which
    returns the list of internal nodes.

    Example
    -------
    .. code-block:: python

        class MyGenerator(OChain):
            def create_internal_nodes(self) -> List[Node]:
                return [
                    SourceNode(),    # ONode (generator)
                    FilterNode(),    # IONode
                    TransformNode()  # IONode (output exposed)
                ]
    """

    class Configuration(Chain.Configuration):
        """Configuration class for OChain."""

        class Keys(Chain.Configuration.Keys):
            """Keys for the OChain configuration."""
            OUTPUT_PORTS = "output_ports"

        def __init__(self,
                     output_ports: list = None,
                     **kwargs):
            """
            Initialize the OChain configuration.

            Parameters
            ----------
            output_ports : list of OPort.Configuration, optional
                A list of output port configurations. If None, ports
                will be inherited from the last internal node.
            **kwargs : additional keyword arguments
                Other configuration options.
            """
            if output_ports is None:
                output_ports = [OPort.Configuration()]
            super().__init__(output_ports=output_ports, **kwargs)

    _IMP_CLASS = imp.OChainImp
    _imp: _IMP_CLASS  # for type hinting  # type: ignore
    config: Configuration  # for type hinting

    def __init__(self,
                 output_ports: list = None,
                 **kwargs):
        """
        Initialize the OChain.

        Parameters
        ----------
        output_ports : list of OPort.Configuration, optional
            A list of output port configurations (default is None).
        **kwargs : additional keyword arguments
            Other configuration options.
        """
        kwargs = self._init_internal_nodes(**kwargs)
        self.create_config(output_ports=output_ports, **kwargs)
        self.create_implementation()
        self._validate_user_ports("output_ports", output_ports)

    @abstractmethod
    def create_internal_nodes(self) -> List[Node]:
        """
        Create and return the list of internal nodes.

        The first node must be an ONode.
        The last node must have output ports (ONode or IONode).
        Intermediate nodes should be IONodes.

        Returns
        -------
        List[Node]
            List of internal nodes forming the processing chain.
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

    def get_output_port(self, port_name: str):
        """Get an output port by name."""
        return self._imp.get_port(port_name)

    def get_port(self, port_name: str):
        """Deprecated: use :meth:`get_output_port` instead."""
        import warnings
        warnings.warn("Chain.get_port() is deprecated; use "
                      "get_output_port() instead.",
                      DeprecationWarning, stacklevel=2)
        return self.get_output_port(port_name)
