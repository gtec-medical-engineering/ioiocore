from .portable import Portable
from .constants import Constants

import ioiocore.imp as imp


class Port(Portable):
    """
    A class representing a port, inheriting from Portable.
    Manages configuration and implementation details of the port.
    """

    class Configuration(Portable.Configuration):
        """
        Configuration class for the Port.

        Attributes
        ----------
        NAME : str
            The key for the port name.
        TYPE : str
            The key for the port type.
        TIMING : str
            The key for the port timing.
        """

        class Keys(Portable.Configuration.Keys):
            """
            Keys for the port configuration.
            """
            NAME = "name"
            TYPE = "type"
            TIMING = "timing"

        def __init__(self,
                     name: str = None,
                     type: str = 'Any',
                     timing: Constants.Timing = Constants.Timing.SYNC,
                     **kwargs):
            """
            Initializes the port configuration.

            Parameters
            ----------
            name : str, optional
                The name of the port (default is None).
            type : str, optional
                The type of the port (default is 'Any').
            timing : Constants.Timing, optional
                The timing of the port (default is Constants.Timing.SYNC).
            **kwargs
                Additional keyword arguments for further configuration.

            Raises
            ------
            ValueError
                If the provided timing is not in Constants.Timing values.
            """
            if timing not in Constants.Timing.values():
                raise ValueError(f"Unknown timing: {timing}.")
            super().__init__(name=name,
                             type=type,
                             timing=timing,
                             **kwargs)

    _IMP_CLASS = imp.PortImp
    _imp: _IMP_CLASS  # for type hinting  # type: ignore
    config: Configuration  # for type hinting

    def __init__(self,
                 name: str = None,
                 type: str = 'Any',
                 timing: Constants.Timing = Constants.Timing.SYNC,
                 **kwargs):
        """
        Initializes the Port.

        Parameters
        ----------
        name : str, optional
            The name of the port (default is None).
        type : str, optional
            The type of the port (default is 'Any').
        timing : Constants.Timing, optional
            The timing of the port (default is Constants.Timing.SYNC).
        **kwargs
            Additional keyword arguments for further configuration.
        """
        self.create_config(name=name,
                           type=type,
                           timing=timing,
                           **kwargs)
        self.create_implementation()
