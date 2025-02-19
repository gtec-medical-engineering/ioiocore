from .port import Port
from .constants import Constants
import ioiocore.imp as imp


class IPort(Port):

    class Configuration(Port.Configuration):
        class Keys(Port.Configuration.Keys):
            pass

        def __init__(self,
                     name: str = Constants.Defaults.PORT_IN,
                     type: str = 'Any',
                     timing: Constants.Timing = Constants.Timing.SYNC,
                     **kwargs):
            super().__init__(name=name,
                             type=type,
                             timing=timing,
                             **kwargs)

    _IMP_CLASS = imp.IPortImp
    _imp: _IMP_CLASS  # for type hinting  # type: ignore
    config: Configuration  # for type hinting

    def __init__(self,
                 name: str = Constants.Defaults.PORT_IN,
                 type: str = 'Any',
                 timing: Constants.Timing = Constants.Timing.SYNC,
                 **kwargs):
        self.create_config(name=name,
                           type=type,
                           timing=timing,
                           **kwargs)
        self.create_implementation()
        super().__init__(**self.config)
