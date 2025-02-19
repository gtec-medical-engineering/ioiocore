from enum import Enum
from typing import Dict, Any
from .i_port import IPort
from .node import Node

import ioiocore.imp as imp


class INode(Node):

    class UpdateRule(Enum):
        ALL_PORTS = 1
        ANY_PORT = 2

    class Configuration(Node.Configuration):
        class Keys(Node.Configuration.Keys):
            INPUT_PORTS = 'input_ports'

        def __init__(self,
                     input_ports: list[IPort.Configuration] = None,
                     **kwargs):
            if input_ports is None:
                input_ports = [IPort.Configuration()]
            super().__init__(input_ports=input_ports,
                             **kwargs)

    _IMP_CLASS = imp.INodeImp
    _imp: _IMP_CLASS  # for type hinting  # type: ignore
    config: Configuration  # for type hinting

    def __init__(self,
                 input_ports: list[IPort.Configuration] = None,
                 **kwargs):
        self.create_config(input_ports=input_ports,
                           **kwargs)
        self.create_implementation()
        super().__init__(**self.config)

    def start(self):
        self._imp.start()

    def stop(self):
        self._imp.stop()

    def setup(self,
              data: Dict[str, Any],
              port_metadata_in: Dict[str, dict]) -> Dict[str, dict]:
        pass
