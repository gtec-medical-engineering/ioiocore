from typing import Dict, Any
from .o_port import OPort
from .node import Node
from .i_node import INode

import ioiocore.imp as imp


class ONode(Node):

    class Configuration(Node.Configuration):
        class Keys(Node.Configuration.Keys):
            OUTPUT_PORTS = "output_ports"

        def __init__(self,
                     **kwargs):
            # remove output_ports from kwargs;
            # if not present, assign a default value. This avoids errors when
            # deserialization is performed.
            op_key = self.Keys.OUTPUT_PORTS
            output_ports: list[OPort.Configuration] = kwargs.pop(op_key,
                                                                 [OPort.Configuration()])  # noqa: E501
            super().__init__(output_ports=output_ports,
                             **kwargs)

    _IMP_CLASS = imp.ONodeImp
    _imp: _IMP_CLASS  # for type hinting  # type: ignore
    config: Configuration  # for type hinting

    def __init__(self,
                 output_ports: list[OPort.Configuration] = None,
                 **kwargs):
        self.create_config(output_ports=output_ports,
                           **kwargs)
        self.create_implementation()
        super().__init__(**self.config)

    def connect(self,
                output_port: str,
                target: INode,
                input_port: str):
        self._imp.connect(output_port, target._imp, input_port)

    def disconnect(self,
                   output_port: str,
                   target: INode,
                   input_port: str):
        self._imp.disconnect(output_port, target._imp, input_port)

    def setup(self,
              data: Dict[str, Any],
              port_metadata_in: Dict[str, dict]) -> Dict[str, dict]:
        port_metadata_out: Dict[str, dict] = {}
        op_config = self.config[self.config.Keys.OUTPUT_PORTS]
        op_names = [s[self.Configuration.Keys.NAME] for s in op_config]
        md = self.config.get_metadata()
        for port_name in op_names:
            port_metadata_out[port_name] = md
        return port_metadata_out

    def cycle(self, data: Dict[str, Any] = {}):
        self._imp._cycle(data)
