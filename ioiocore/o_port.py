from .port import Port
from .constants import Constants
import ioiocore.imp as imp


class OPort(Port):

    """
    A class representing an output port, inheriting from Port.
    """

    class Configuration(Port.Configuration):
        """
        Configuration class for OPort.
        """

        class Keys(Port.Configuration.Keys):
            """
            Keys for the OPort configuration (none).
            """
            pass

        def __init__(self,
                     name: str = Constants.Defaults.PORT_OUT,
                     type: str = 'Any',
                     timing: Constants.Timing = Constants.Timing.SYNC,
                     **kwargs):
            """
            Initializes the configuration for OPort.

            Parameters
            ----------
            name : str, optional
                The name of the port (default is Constants.Defaults.PORT_OUT).
            type : str, optional
                The type of the port (default is `'Any'`).
            timing : Constants.Timing, optional
                The timing of the port (default is Constants.Timing.SYNC).
            **kwargs : additional keyword arguments
                Other configuration options.

            Raises
            ------
            ValueError
                If the timing is set to Constants.Timing.INHERITED.
            """
            if timing == Constants.Timing.INHERITED:
                raise ValueError("OPort does not support inherited timing.")
            super().__init__(name=name,
                             type=type,
                             timing=timing,
                             **kwargs)

    _IMP_CLASS = imp.OPortImp
    _imp: _IMP_CLASS  # for type hinting  # type: ignore
    config: Configuration  # for type hinting

    def __init__(self,
                 name: str = Constants.Defaults.PORT_OUT,
                 type: str = 'Any',
                 timing: Constants.Timing = Constants.Timing.SYNC,
                 **kwargs):
        """
        Initializes the OPort.

        Parameters
        ----------
        name : str, optional
            The name of the port (default is `Constants.Defaults.PORT_OUT`).
        type : str, optional
            The type of the port (default is `'Any'`).
        timing : Constants.Timing, optional
            The timing of the port (default is `Constants.Timing.SYNC`).
        **kwargs : additional keyword arguments
            Other configuration options.
        """
        self.create_config(name=name,
                           type=type,
                           timing=timing,
                           **kwargs)
        self.create_implementation()
        super().__init__(**self.config)
