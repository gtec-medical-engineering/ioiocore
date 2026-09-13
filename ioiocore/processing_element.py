from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from .portable import Portable
from .logging import Logger
from .constants import Constants
from .context import Context

import ioiocore.imp as imp


class ProcessingElement(ABC, Portable):
    """
    Abstract base class for all processing elements in a pipeline.

    This is the common base for both Node (concrete processing nodes)
    and Chain (containers of nodes). It provides the shared interface
    that Pipeline uses to manage elements.

    Attributes
    ----------
    _IMP_CLASS : type
        The implementation class for the ProcessingElement.
    _imp : _IMP_CLASS
        The instance of the implementation class.
    config : Configuration
        The configuration object for the ProcessingElement.
    """

    _IMP_CLASS = imp.ProcessingElementImp

    class Configuration(Portable.Configuration):
        """
        Configuration class for the ProcessingElement.

        Attributes
        ----------
        Keys
            The configuration keys.
        """

        class Keys(Portable.Configuration.Keys):
            """Configuration keys."""
            NAME = "name"

        def __init__(self,
                     name: str = None,
                     **kwargs):
            """
            Initialize the ProcessingElement configuration.

            Parameters
            ----------
            name : str, optional
                The name of the ProcessingElement (default is the class name).
            kwargs : additional keyword arguments
                Other configuration parameters passed to the base class.
            """
            if name is None:
                name = self.__class__.__qualname__.split('.')[0]
            super().__init__(name=name, **kwargs)

    _imp: _IMP_CLASS  # for type hinting  # type: ignore
    config: Configuration  # for type hinting

    def create_config(self, **kwargs):
        """
        Factory method to create the configuration for the ProcessingElement.

        Sets name to the interface class name if not provided. This ensures
        that concrete subclasses that don't define their own Configuration
        class still get the correct name (e.g., a concrete OChain subclass
        will be named after itself, not "OChain").

        Parameters
        ----------
        **kwargs
            Additional keyword arguments for configuring the ProcessingElement.
        """
        if 'name' not in kwargs or kwargs.get('name') is None:
            kwargs['name'] = self.__class__.__name__
        super().create_config(**kwargs)

    @abstractmethod
    def start(self):
        """Start the processing element."""
        pass  # pragma: no cover

    @abstractmethod
    def stop(self):
        """Stop the processing element."""
        pass  # pragma: no cover

    def set_logger(self, logger: Logger):
        """Set the logger for this processing element."""
        self._imp.set_logger(logger)

    def log(self, msg: str, type: Constants.LogTypes = None):
        """Write a log message."""
        self._imp.log(msg=msg, type=type)

    @property
    def name(self) -> str:
        """Get the name of this processing element."""
        return self._imp.name

    def get_counter(self) -> int:
        """
        Get the current counter value.

        Returns
        -------
        int
            The counter value.
        """
        return self._imp.get_counter()

    def get_state(self) -> 'Constants.States':
        """
        Get the current state.

        Returns
        -------
        Constants.States
            The current state.
        """
        return self._imp.get_state()

    def get_condition(self) -> 'Constants.Conditions':
        """
        Get the current condition.

        Returns
        -------
        Constants.Conditions
            HEALTHY, WARNING or ERROR. An element sets ERROR on itself
            when its setup or its step raises, and only
            reset_run_state() clears it again.
        """
        return self._imp.get_condition()

    def setup_failed(self) -> bool:
        """
        Whether setup() raised, as opposed to a later cycle.

        Returns
        -------
        bool
            True if this element's setup() raised. Reported apart from
            the condition because the two mean different things to a
            caller: a step that raises is a run that died, while a setup
            that raises is an element that was never viable -- which the
            start() the caller is still inside can still refuse.
        """
        return self._imp.setup_failed()

    def failure(self) -> Exception:
        """
        The exception this element raised, kept whole.

        Returns
        -------
        Exception
            What setup() or a cycle raised, or None if nothing did.

            Reported alongside the log entry rather than instead of it,
            because the two serve different readers. The log is what a
            running system writes down; this is what a caller needs to
            raise `from`, so the element's own frames end up in front of
            the user instead of a sentence quoting them.

            The first failure is kept. A node that fails during setup
            returns from every later cycle without processing, and the
            condition it leaves behind makes the next cycle look like a
            fresh failure -- so overwriting would replace the cause with
            its consequence.
        """
        return self._imp.failure()

    def get_context(self) -> 'Context':
        """Get the context of this processing element."""
        return self._imp.get_context()

    def __getitem__(self, port_name: str):
        """Access a port by name for use in Pipeline.connect()."""
        return {"node": self, "port": port_name}
