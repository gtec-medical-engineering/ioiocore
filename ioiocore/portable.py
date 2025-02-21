from .configuration import Configuration
from .interface import Interface
import ioiocore.imp as imp


class Portable(Interface):
    """
    A class representing a portable object, inheriting from Interface.
    Handles configuration, implementation, and serialization of the portable
    object.
    """

    class Configuration(Configuration):
        """
        Configuration class for the Portable.

        Attributes
        ----------
        ID : str
            The key for the portable object ID.
        """

        class Keys(Configuration.Keys):
            """
            Keys for the Portable configuration.
            """
            ID = 'id'

        def __init__(self,
                     id: str = imp.ConstantsImp.ID_TO_BE_GENERATED,
                     **kwargs):
            """
            Initializes the portable configuration.

            Parameters
            ----------
            id : str, optional
                The ID of the portable object (default is ID_TO_BE_GENERATED).
            **kwargs
                Additional keyword arguments for further configuration.
            """
            super().__init__(id=id, **kwargs)

    _IMP_CLASS = imp.PortableImp
    _imp: _IMP_CLASS  # for type hinting  # type: ignore
    config: Configuration  # for type hinting

    def __init__(self, **kwargs):
        """
        Initializes the Portable object.

        Parameters
        ----------
        **kwargs
            Additional keyword arguments for further configuration.
        """
        self.create_config(**kwargs)
        self.create_implementation()

    def create_config(self, **kwargs):
        """
        Factory method to create the configuration for the Portable object.

        Parameters
        ----------
        **kwargs
            Additional keyword arguments for configuring the Portable object.
        """
        if not hasattr(self, 'config'):
            self.config = self.Configuration(**kwargs)

    def create_implementation(self, **kwargs):
        """
        Factory method to create the implementation for the Portable object.

        Parameters
        ----------
        **kwargs
            Additional keyword arguments for implementing the Portable object.
        """
        if not hasattr(self, '_imp'):
            self._imp = self._IMP_CLASS(config=self.config,
                                        **kwargs)

    def serialize(self) -> dict:
        """
        Serializes the Portable object.

        Returns
        -------
        dict
            A dictionary representation of the Portable object.
        """
        return self._imp.serialize(interface=self)

    @staticmethod
    def deserialize(data: dict) -> 'Portable':
        """
        Deserializes a Portable object from a dictionary.

        Parameters
        ----------
        data : dict
            The dictionary containing the serialized data.

        Returns
        -------
        Portable
            The deserialized Portable object.
        """
        return imp.PortableImp.deserialize(data)

    @staticmethod
    def get_by_id(id: str) -> 'Portable':
        """
        Retrieves a Portable object by its ID.

        Parameters
        ----------
        id : str
            The ID of the Portable object.

        Returns
        -------
        Portable
            The Portable object with the given ID.
        """
        return imp.PortableImp.get_by_id(id)

    @staticmethod
    def reset():
        """
        Resets the Portable object.

        This static method calls the reset method on the PortableImp.
        """
        imp.PortableImp.reset()

    @staticmethod
    def add_preinstalled_module(module: str):
        """
        Adds a preinstalled module for the Portable object.

        Parameters
        ----------
        module : str
            The name of the module to be added.
        """
        imp.PortableImp.add_preinstalled_module(module)
