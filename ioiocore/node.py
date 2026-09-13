from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

from .processing_element import ProcessingElement
from .logging import Logger
from .constants import Constants
from .context import Context

import ioiocore.imp as imp  # type: ignore


class Node(ProcessingElement):
    """
    Abstract base class representing a concrete processing node in a pipeline.

    Extends ProcessingElement with setup() and step() methods that define
    the node's initialization and processing logic.

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

    class Configuration(ProcessingElement.Configuration):
        """
        Configuration class for the Node

        Attributes
        ----------
        Keys
            The configuration keys.
        """

        class Keys(ProcessingElement.Configuration.Keys):
            """Configuration keys."""
            pass

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
        self._imp.pre_setup_handler = self.pre_setup
        self._imp.pre_step_handler = self.pre_step

        # A node declares which execution modes it supports by which of
        # the two it overrides -- step() for a frame at a time, process()
        # for the whole record at once. Derived from structure rather than
        # from a flag, so a node cannot claim a mode it has no body for.
        #
        # step() is bound either way, because it is the default path and
        # the base implementation raises a message naming the class and
        # the mode -- a better failure than calling None. process() is
        # bound only when it is declared, because that is exactly what
        # the implementation asks in order to dispatch: a handler bound
        # to the raising base would send every node down the batch path.
        if type(self).process is not Node.process:
            self._imp.process_handler = self.process

        if (type(self).step is Node.step
                and type(self).process is Node.process):
            raise TypeError(
                f"{type(self).__name__} implements neither step() nor "
                f"process(). A node needs step() to run in a realtime "
                f"pipeline, process() to run in a batch pipeline, or "
                f"both."
            )
        # Record this node's concrete type so start() can hand it to an
        # authorization provider, if a consuming package installed one.
        # Recorded rather than derived at start() so no call-stack walk is
        # needed. Note this identifies the node; it does not authorize it.
        self._imp._auth_key = repr(type(self))

    def start(self):
        """
        Start the Node.
        """
        self._imp.start()

    def stop(self):
        """
        Stop the Node.
        """
        self._imp.stop()

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

    def is_externally_fed(self) -> bool:
        """
        Report whether this node's inputs come from outside the pipeline.

        A chain refuses an IONode at its inlet, because an IONode there
        would leave its input ports with nothing connected to them and
        the chain could never be fed. That is the right default: it
        catches a real authoring mistake.

        It is wrong for one kind of node -- one whose input is satisfied
        from outside the graph entirely, such as a bridge receiving from
        a socket. Its unconnected input port is not a dangling port; it
        is the point where external data arrives. Such a node says so by
        returning True here, and the chain then admits it.

        Declared rather than inferred, and False by default, so nothing
        existing changes and no mistake is silently accepted.

        Returns
        -------
        bool
            True if the inputs are satisfied externally.
        """
        return False

    def is_externally_drained(self) -> bool:
        """
        Report whether this node's outputs leave the pipeline.

        The outlet counterpart of :meth:`is_externally_fed`: a chain
        refuses an IONode at its outlet because its output would be
        silently dropped. A node that sends its output somewhere outside
        the graph returns True, and the chain admits it.

        Returns
        -------
        bool
            True if the outputs are consumed externally.
        """
        return False

    def pre_setup(self, data: dict, port_context_in: dict) -> None:
        """
        Adapt the input contexts before setup() sees them.

        Called once, immediately before ``setup``, with the input port
        contexts that ``setup`` is about to receive. Modify them in
        place; the return value is ignored.

        The setup-time counterpart of :meth:`pre_step`. Together they let
        a consuming package present every node with uniform inputs: this
        one settles what the inputs *are* -- how many channels, at what
        rate, with what timing -- and ``pre_step`` supplies frames that
        match on every cycle. Adapting only the frames would not be
        enough, because a node decides its own output shape here, from
        exactly these contexts.

        The default does nothing.

        Parameters
        ----------
        data : dict
            Initial data, as passed to ``setup``.
        port_context_in : dict
            Input port contexts keyed by port name, to be modified in
            place.
        """
        pass

    def pre_step(self, data: dict) -> bool:
        """
        Adapt the input frames before step() sees them.

        Called once per cycle, immediately before ``step``, with the
        dictionary that ``step`` is about to receive. Modify it in place.

        Return True to withhold the cycle: ``step`` is not called and
        nothing is emitted. A hook that holds frames back needs this --
        without it, the only way to keep the cycle going is to fabricate
        a frame, which puts invented samples at the head of the stream
        and shifts every later one by however many were held. Returning
        None or False runs the cycle as usual, which is what every hook
        that does not hold anything back does.

        This exists so that a consuming package can make the inputs of
        *every* node uniform without every node author having to know
        about it. The engine deliberately holds no opinion about what
        "uniform" means: it delivers whatever arrived, and this is where
        a domain layer may reshape it -- resample a stream that arrives
        irregularly onto the grid of one that does not, substitute a
        value for a port that produced nothing, or reject a combination
        it cannot express.

        The default does nothing, which is the behaviour of every node
        that does not override it.

        Notes
        -----
        This runs on the per-cycle path, so an override should do as
        little as possible and decide as much as it can once, in
        ``setup``, rather than on every frame.

        Parameters
        ----------
        data : dict
            Input frames keyed by port name, to be modified in place. A
            port that produced nothing this cycle may be absent.
        """
        pass

    def step(self, data: dict) -> dict:
        """
        Process one frame. Override for a node that runs in realtime.

        Not abstract, because a node may instead implement
        :meth:`process` and run only in a batch pipeline. Exactly one of
        the two is required, checked in ``__init__``.

        Parameters
        ----------
        data : dict
            The input data to process.

        Returns
        -------
        dict
            The processed data after applying the step logic.

        Raises
        ------
        NotImplementedError
            If the node implements only :meth:`process`. Reaching this
            means a batch-only node was driven frame by frame.
        """
        raise NotImplementedError(
            f"{type(self).__name__} implements process() and not step(), "
            f"so it can only run in a batch pipeline, where the whole "
            f"record arrives in one call."
        )

    def process(self, data: dict) -> dict:
        """
        Process the whole record at once. Override for a batch node.

        Called once, with every sample the node will ever see, in place
        of :meth:`step`. This is what a non-causal operation needs -- a
        zero-phase filter, a whole-record statistic -- and it is why the
        node needs no buffering of its own: a batch pipeline delivers one
        block.

        Parameters
        ----------
        data : dict
            The complete input data, keyed by port name.

        Returns
        -------
        dict
            The processed data.

        Raises
        ------
        NotImplementedError
            If the node implements only :meth:`step`. Reaching this means
            the caller asked for whole-record processing from a node that
            declares none, which the pipeline should have refused first.
        """
        raise NotImplementedError(
            f"{type(self).__name__} implements step() and not process()."
        )
