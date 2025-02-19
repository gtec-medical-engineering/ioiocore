from typing import Any, Dict
from copy import deepcopy
from .i_node import INode
from .o_node import ONode
from .i_node import IPort
from .o_node import OPort

import ioiocore.imp as imp


class IONode(INode, ONode):

    class Configuration(INode.Configuration, ONode.Configuration):

        class Keys(INode.Configuration.Keys, ONode.Configuration.Keys):
            pass

        def __init__(self,
                     input_ports: list[IPort.Configuration] = None,
                     output_ports: list[OPort.Configuration] = None,
                     update_rule: INode.UpdateRule = INode.UpdateRule.ALL_PORTS,  # noqa: E501
                     **kwargs):
            if input_ports is None:
                input_ports = [IPort.Configuration()]
            if output_ports is None:
                output_ports = [OPort.Configuration()]

            INode.Configuration.__init__(self,
                                         input_ports=input_ports,
                                         output_ports=output_ports,
                                         update_rule=update_rule,
                                         **kwargs)
            ONode.Configuration.__init__(self,
                                         input_ports=input_ports,
                                         output_ports=output_ports,
                                         update_rule=update_rule,
                                         **kwargs)

    _IMP_CLASS = imp.IONodeImp
    _imp: _IMP_CLASS  # for type hinting  # type: ignore
    config: Configuration  # for type hinting

    def __init__(self,
                 input_ports: list[IPort.Configuration] = None,
                 output_ports: list[OPort.Configuration] = None,
                 update_rule: INode.UpdateRule = INode.UpdateRule.ALL_PORTS,
                 **kwargs):
        self.create_config(input_ports=input_ports,
                           output_ports=output_ports,
                           update_rule=update_rule,
                           **kwargs)
        self.create_implementation()
        super().__init__(**self.config)

    def setup(self,
              data: Dict[str, Any],
              port_metadata_in: Dict[str, dict]) -> Dict[str, dict]:
        if len(port_metadata_in) != 1:
            raise ValueError("Default implementation of setup() requires "
                             "exactly one input port. Please overload this "
                             "method appropriately.")
        port_metadata_out: Dict[str, dict] = {}
        ip_config = self.config[self.config.Keys.INPUT_PORTS]
        ip_names = [s[self.Configuration.Keys.NAME] for s in ip_config]
        op_config = self.config[self.config.Keys.OUTPUT_PORTS]
        op_names = [s[self.Configuration.Keys.NAME] for s in op_config]
        for ip_name in ip_names:
            for op_name in op_names:
                port_metadata_out[op_name] = deepcopy(port_metadata_in[ip_name])  # noqa: E501
        return port_metadata_out
