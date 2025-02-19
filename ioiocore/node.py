from abc import ABC, abstractmethod
from typing import Dict, Any
from .portable import Portable
from .logger import Logger
from .constants import Constants

import ioiocore.imp as imp  # type: ignore


class Node(ABC, Portable):

    _IMP_CLASS = imp.NodeImp

    class Configuration(Portable.Configuration):
        class Keys(Portable.Configuration.Keys):
            NAME = "name"

        def __init__(self,
                     name: str = None,
                     **kwargs):
            if name is None:
                name = self.__class__.__qualname__.split('.')[0]
            super().__init__(name=name, **kwargs)

    _imp: _IMP_CLASS  # for type hinting  # type: ignore
    config: Configuration  # for type hinting

    def __init__(self,
                 name: str = None,
                 **kwargs):
        self.create_config(name=name, **kwargs)
        self.create_implementation()
        self._imp.set_setup_handler(self.setup)
        self._imp.set_step_handler(self.step)
        super().__init__(**self.config)

    def start(self):
        self._imp.start()

    def stop(self):
        self._imp.stop()

    def set_logger(self, logger: Logger):
        self._imp.set_logger(logger)

    def get_name(self) -> str:
        return self._imp.get_name()

    def get_load(self) -> float:
        return self._imp.get_load()

    def get_counter(self) -> int:
        return self._imp.get_counter()

    def get_state(self) -> 'Constants.STATE':
        return self._imp.get_state()

    @abstractmethod
    def setup(self,
              data: Dict[str, Any],
              port_metadata_in: Dict[str, dict]) -> Dict[str, dict]:
        pass

    @abstractmethod
    def step(self, data: Dict[str, Any]) -> Dict[str, Any]:
        pass
