from typing import List, TYPE_CHECKING
from abc import abstractmethod

from .chain import Chain
from .i_port import IPort
from .node import Node

import ioiocore.imp as imp

if TYPE_CHECKING:
    pass  # pragma: no cover


class IChain(Chain):
    """
    A chain that receives input and processes it through
    a sequence of internal nodes.

    Structure: <input> => IONode => ... => IONode => INode

    The input ports are exposed from the first internal node,
    making this chain usable anywhere an input element is expected.

    Inheriting classes must implement ``create_internal_nodes()``, which
    returns the list of internal nodes.

    Example
    -------
    .. code-block:: python

        class MyProcessor(IChain):
            def create_internal_nodes(self) -> List[Node]:
                return [
                    FilterNode(),    # IONode
                    TransformNode(), # IONode
                    SinkNode()       # INode (terminal)
                ]
    """

    class Configuration(Chain.Configuration):
        """Configuration class for IChain."""

        class Keys(Chain.Configuration.Keys):
            """Keys for the IChain configuration."""
            INPUT_PORTS = "input_ports"

        def __init__(self,
                     input_ports: list = None,
                     **kwargs):
            """
            Initialize the IChain configuration.

            Parameters
            ----------
            input_ports : list of IPort.Configuration, optional
                A list of input port configurations. If None, ports
                will be inherited from the first internal node.
            **kwargs : additional keyword arguments
                Other configuration options.
            """
            if input_ports is None:
                input_ports = [IPort.Configuration()]
            super().__init__(input_ports=input_ports, **kwargs)

    _IMP_CLASS = imp.IChainImp
    _imp: _IMP_CLASS  # for type hinting  # type: ignore
    config: Configuration  # for type hinting

    def __init__(self,
                 input_ports: list = None,
                 **kwargs):
        """
        Initialize the IChain.

        Parameters
        ----------
        input_ports : list of IPort.Configuration, optional
            A list of input port configurations (default is None).
        **kwargs : additional keyword arguments
            Other configuration options.
        """
        kwargs = self._init_internal_nodes(**kwargs)
        self.create_config(input_ports=input_ports, **kwargs)
        self.create_implementation()
        self._validate_user_ports("input_ports", input_ports)

    @abstractmethod
    def create_internal_nodes(self) -> List[Node]:
        """
        Create and return the list of internal nodes.

        The first node must have input ports (IONode or INode).
        The last node must be an INode.
        Intermediate nodes should be IONodes.

        Returns
        -------
        List[Node]
            List of internal nodes forming the processing chain.
        """
        pass  # pragma: no cover

    def get_input_port(self, port_name: str):
        """Get an input port by name."""
        return self._imp.get_port(port_name)

    def get_port(self, port_name: str):
        """Deprecated: use :meth:`get_input_port` instead."""
        import warnings
        warnings.warn("Chain.get_port() is deprecated; use "
                      "get_input_port() instead.",
                      DeprecationWarning, stacklevel=2)
        return self.get_input_port(port_name)
