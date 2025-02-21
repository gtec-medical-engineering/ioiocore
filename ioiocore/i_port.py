from .port import Port
from .constants import Constants
import ioiocore.imp as imp


class IPort(Port):
    """
    Inherits from Port and represents an input port receiveing data.
    """

    class Configuration(Port.Configuration):
        """
        Configuration class for IPort.
        """

        class Keys(Port.Configuration.Keys):
            """
            Keys for the IPort configuration (none).
            """
            pass

        def __init__(self,
                     name: str = Constants.Defaults.PORT_IN,
                     type: str = 'Any',
                     timing: Constants.Timing = Constants.Timing.SYNC,
                     **kwargs):
            """
            Initializes the configuration for IPort.

            Parameters
            ----------
            name : str, optional
                The name of the port (default is Constants.Defaults.PORT_IN).
            type : str, optional
                The type of the port (default is 'Any').
            timing : Constants.Timing, optional
                The timing of the port (default is Constants.Timing.SYNC).
            **kwargs : additional keyword arguments
                Other configuration options.
            """
            super().__init__(name=name, type=type, timing=timing, **kwargs)

    _IMP_CLASS = imp.IPortImp
    _imp: _IMP_CLASS  # for type hinting  # type: ignore
    config: Configuration  # for type hinting

    def __init__(self,
                 name: str = Constants.Defaults.PORT_IN,
                 type: str = 'Any',
                 timing: Constants.Timing = Constants.Timing.SYNC,
                 **kwargs):
        """
        Initializes the IPort.

        Parameters
        ----------
        name : str, optional
            The name of the port (default is Constants.Defaults.PORT_IN).
        type : str, optional
            The data type of the port (default is 'Any').
        timing : Constants.Timing, optional
            The timing of the port (default is Constants.Timing.SYNC).
        **kwargs : additional keyword arguments
            Other configuration options.
        """
        self.create_config(name=name, type=type, timing=timing, **kwargs)
        self.create_implementation()
        super().__init__(**self.config)
