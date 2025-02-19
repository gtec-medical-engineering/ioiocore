from .node import Node
from .o_node import ONode
from .i_node import INode
from .constants import Constants
from .interface import Interface

import ioiocore.imp as imp  # type: ignore


class Pipeline(Interface):

    _imp: imp.PipelineImp  # for type hinting

    def __init__(self, directory: str = None):
        self._imp = imp.PipelineImp(directory=directory)

    def add_node(self, node: Node):
        self._imp.add_node(node)

    def remove_node(self, node: Node):
        self._imp.remove_node(node)

    def connect_ports(self,
                      output_node: ONode,
                      output_node_port: str,
                      input_node: INode,
                      input_node_port: str):
        self._imp.connect_ports(output_node,
                                output_node_port,
                                input_node,
                                input_node_port)

    def connect(self,
                output_node: ONode,
                input_node: INode):
        self._imp.connect(output_node, input_node)

    def disconnect_ports(self,
                         output_node: ONode,
                         output_node_port: str,
                         input_node: INode,
                         input_node_port: str):
        self._imp.disconnect_ports(output_node,
                                   output_node_port,
                                   input_node,
                                   input_node_port)

    def disconnect(self,
                   output_node: ONode,
                   input_node: INode):
        self._imp.disconnect(output_node, input_node)

    def start(self):
        self._imp.start()

    def stop(self):
        self._imp.stop()

    def get_state(self) -> Constants.States:
        return self._imp.get_state()

    def get_condition(self) -> Constants.Conditions:
        return self._imp.get_condition()

    def get_last_error(self) -> str:
        return self._imp.get_last_error()

    def get_elapsed_time(self) -> float:
        return self._imp.get_elapsed_time()

    def get_load(self) -> float:
        return self._imp.get_load()

    def serialize(self) -> dict:
        return self._imp.serialize()

    @staticmethod
    def deserialize(data: dict) -> 'Pipeline':
        return imp.PipelineImp.deserialize(data)

    def write_log(self, entry: str):
        self._imp.write_log(entry)
