from .portable import Portable
from .constants import Constants

import ioiocore.imp as imp


class Port(Portable):

    class Configuration(Portable.Configuration):
        class Keys(Portable.Configuration.Keys):
            NAME = "name"
            TYPE = "type"
            TIMING = "timing"

        def __init__(self,
                     name: str = None,
                     type: str = 'Any',
                     timing: Constants.Timing = Constants.Timing.SYNC,
                     **kwargs):
            if timing not in Constants.Timing.values():
                raise ValueError(f"Unknown timing: {timing}.")
            super().__init__(name=name,
                             type=type,
                             timing=timing,
                             **kwargs)

    _IMP_CLASS = imp.PortImp
    _imp: _IMP_CLASS  # for type hinting  # type: ignore

    def __init__(self,
                 name: str = None,
                 type: str = 'Any',
                 timing: Constants.Timing = Constants.Timing.SYNC,
                 **kwargs):
        self.create_config(name=name,
                           type=type,
                           timing=timing,
                           **kwargs)
        self.create_implementation()
