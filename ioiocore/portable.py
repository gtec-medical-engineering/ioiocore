from .configuration import Configuration
from .interface import Interface
import ioiocore.imp as imp


class Portable(Interface):

    class Configuration(Configuration):

        class Keys(Configuration.Keys):
            ID = 'id'

        def __init__(self,
                     id: str = imp.ConstantsImp.ID_TO_BE_GENERATED,
                     **kwargs):
            super().__init__(id=id, **kwargs)

    _IMP_CLASS = imp.PortableImp
    _imp: _IMP_CLASS  # for type hinting  # type: ignore
    config: Configuration  # for type hinting

    def __init__(self,
                 **kwargs):
        self.create_config(**kwargs)
        self.create_implementation()

    # factory method for config
    def create_config(self,
                      **kwargs):
        if not hasattr(self, 'config'):
            self.config = self.Configuration(**kwargs)

    # factory method for implementation
    def create_implementation(self,
                              **kwargs):
        if not hasattr(self, '_imp'):
            self._imp = self._IMP_CLASS(config=self.config,
                                        **kwargs)

    def serialize(self) -> dict:
        return self._imp.serialize(interface=self)

    @staticmethod
    def deserialize(data: dict) -> 'Portable':
        return imp.PortableImp.deserialize(data)

    @staticmethod
    def get_by_id(id: str) -> 'Portable':
        return imp.PortableImp.get_by_id(id)

    @staticmethod
    def reset():
        imp.PortableImp.reset()

    @staticmethod
    def add_preinstalled_module(module: str):
        imp.PortableImp.add_preinstalled_module(module)
