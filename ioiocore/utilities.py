class _ImmutableClass(type):
    def __setattr__(cls, name, value):
        raise AttributeError(f"Cannot modify constant '{name}'")


class KeyValueContainer(metaclass=_ImmutableClass):
    """
    A container class that provides methods to retrieve all keys
    and values defined in subclasses.
    """
    @classmethod
    def values(cls):
        """
        Retrieve all values defined in the class.

        Returns
        -------
        list
            A list of all values in the class that are not
            dunder attributes or private attributes.
        """
        return [v for k, v in vars(cls).items()
                if not k.startswith("__") and not k.startswith("_")]

    @classmethod
    def keys(cls):
        """
        Retrieve all keys defined in the class.

        Returns
        -------
        list
            A list of all keys in the class that are not
            dunder attributes.
        """
        return [k for k, v in vars(cls).items() if not k.startswith("__")]
