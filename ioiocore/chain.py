from typing import List
from abc import abstractmethod

from .processing_element import ProcessingElement
from .node import Node
from .portable import Portable

import ioiocore.imp as imp


class Chain(ProcessingElement):
    """
    Base class for all chain types.

    A chain is a processing element that contains a sequence of
    internal nodes connected together. Chains expose ports from
    their boundary nodes (first and/or last) to the outside world.

    Subclasses:
    - IChain: Input chain (exposes input ports from first node)
    - OChain: Output chain (exposes output ports from last node)
    - IOChain: Input/Output chain (exposes both)

    Inheriting classes must implement:
    - create_internal_nodes(): Returns the list of internal nodes
    """

    class Configuration(ProcessingElement.Configuration):
        """Configuration class for Chain."""

        class Keys(ProcessingElement.Configuration.Keys):
            """Keys for the Chain configuration."""
            pass

    _IMP_CLASS = imp.ChainImp
    _imp: _IMP_CLASS  # for type hinting  # type: ignore
    config: Configuration  # for type hinting

    _internal_nodes: List[Node]

    #: Whether the internal nodes are *derived* from this chain's
    #: configuration rather than being state of their own.
    #:
    #: When True -- the default -- ``serialize()`` omits them and a
    #: loader rebuilds them with ``create_internal_nodes()``. That is the
    #: honest description of a chain whose composition is a function of
    #: its configuration, and it is the only arrangement that lets the
    #: *loading* process decide the composition.
    #:
    #: Why that matters: a chain may legitimately build itself
    #: differently depending on where it is running. A consuming package
    #: that splits one pipeline across two hosts builds an acquisition
    #: node on the host that has the device and a network bridge on the
    #: host that does not. Embedding the internals defeats it exactly:
    #: the receiving side restores the sender's composition and rebuilds
    #: the sender's half, so the two ends are copies rather than
    #: complements.
    #:
    #: Set it False on a chain whose internals cannot be rebuilt from
    #: configuration alone -- one whose ``create_internal_nodes`` is not
    #: a function of ``config``. Then the internals travel, and the
    #: loading process's own view is overridden, which is the trade.
    INTERNALS_ARE_DERIVED: bool = True

    def _init_internal_nodes(self, **kwargs):
        """
        Initialize internal nodes from kwargs or by creation.

        Call this at the start of subclass __init__ methods.

        Parameters
        ----------
        **kwargs : dict
            May contain '_internal_nodes' for deserialization.

        Returns
        -------
        dict
            kwargs with '_internal_nodes' removed.
        """
        _internal_nodes = kwargs.pop("_internal_nodes", None)
        if _internal_nodes is not None and self.INTERNALS_ARE_DERIVED:
            # A document written before internals became derived still
            # carries them. Discarding them is the point rather than a
            # tolerance: restoring them would replay the writing
            # process's composition here, which is precisely what a
            # chain that builds itself per host must not do. The
            # configuration is what describes this node, and it survived.
            _internal_nodes = None
        if _internal_nodes is not None:
            restored = [Portable.deserialize(n) for n in _internal_nodes]
            # The subclass __init__ has already eagerly built its own
            # internal nodes and stored them as attributes (e.g.
            # self.multiplier). Those built nodes are NOT part of the
            # deserialized chain. Rebind any attribute that references one
            # of them to the corresponding restored node, so named handles
            # resolve to the real internal nodes after a round-trip.
            eager = self.create_internal_nodes()
            if len(eager) == len(restored):
                replacement = {id(e): r for e, r in zip(eager, restored)}
                for attr, value in list(self.__dict__.items()):
                    if id(value) in replacement:
                        setattr(self, attr, replacement[id(value)])
            else:
                # The stored composition is a different shape from what
                # this build makes, so the named handles cannot be
                # matched up and are left pointing at nodes that are not
                # in the chain. Previously silent, which made a
                # version-skewed document look like it had loaded
                # cleanly.
                import warnings

                warnings.warn(
                    f"{type(self).__name__} stored "
                    f"{len(restored)} internal node(s) but this build "
                    f"makes {len(eager)}. The stored ones are used, and "
                    f"any named handle on this chain still refers to a "
                    f"node that is not part of it.",
                    RuntimeWarning,
                    stacklevel=3,
                )
            self._internal_nodes = restored
        else:
            self._internal_nodes = self.create_internal_nodes()
        return kwargs

    def create_implementation(self, **kwargs):
        """Create the chain implementation with internal nodes."""
        if not hasattr(self, '_imp'):
            self._imp = self._IMP_CLASS(config=self.config,
                                        internal_nodes=self._internal_nodes,
                                        **kwargs)

    @abstractmethod
    def create_internal_nodes(self) -> List[Node]:
        """
        Create and return the list of internal nodes.

        Returns
        -------
        List[Node]
            List of internal nodes forming the processing chain.
        """
        pass  # pragma: no cover

    def _validate_user_ports(self, key: str, user_ports):
        """Reject explicitly supplied ports that a chain cannot honour.

        A chain exposes its boundary node's ports; it cannot expose ports
        of its own. If the caller passed an explicit port configuration
        whose names do not match the boundary node's actual ports, fail
        fast here instead of silently discarding them (which would later
        surface as a misleading "port not found" on connect).

        Parameters
        ----------
        key : str
            Either "input_ports" or "output_ports".
        user_ports : list or None
            The port configuration the caller passed (None if omitted).
        """
        if user_ports is None:
            return
        from .port import Port
        name_key = Port.Configuration.Keys.NAME
        actual = self.config[key]
        user_names = sorted(p[name_key] for p in user_ports)
        actual_names = sorted(p[name_key] for p in actual)
        if user_names != actual_names:
            raise ValueError(
                f"A chain's '{key}' are derived from its boundary internal "
                f"node (ports: {actual_names}); the supplied {key} "
                f"({user_names}) do not match. Configure the boundary "
                f"node's ports instead of passing {key} to the chain.")

    def start(self):
        """Start the chain and all internal nodes."""
        self._imp.start()

    def stop(self):
        """Stop the chain and all internal nodes."""
        self._imp.stop()

    @property
    def internal_nodes(self) -> List[Node]:
        """Get the list of internal nodes."""
        return self._internal_nodes

    def serialize(self) -> dict:
        """
        Serialize the chain.

        The internal nodes are included only when this chain declares
        that they are *not* derived from its configuration -- see
        :attr:`INTERNALS_ARE_DERIVED`. Omitting them is what lets the
        loading process build the composition it needs rather than
        replaying the writer's.

        Returns
        -------
        dict
            The serialized chain.
        """
        result = self._imp.serialize(interface=self)
        if self.INTERNALS_ARE_DERIVED:
            return result
        config = dict(result["config"])
        config["_internal_nodes"] = [node.serialize()
                                     for node in self._internal_nodes]
        result["config"] = config
        return result
