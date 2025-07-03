class Configuration(dict):
    """
    A dictionary-based configuration class with validation and
    reserved metadata handling.
    """

    class ReservedKeys:
        """
        Reserved keys that cannot be used as configuration fields.
        """
        pass

    class Keys:
        """
        Placeholder for configuration keys. Should be extended by
        subclasses.
        """
        pass

    def __init__(self, **kwargs):
        """
        Initialize a configuration instance with validation.

        Parameters
        ----------
        **kwargs : dict
            Key-value pairs representing configuration fields.

        Raises
        ------
        ValueError
            If a required field is missing, None, or empty.
        """
        dict.__init__(self, **kwargs)
        for key in dir(self.Keys):
            if key.startswith('__'):
                continue
            val = getattr(self.Keys, key)
            if val in Configuration.ReservedKeys.__dict__.values():
                continue
            if val not in self.keys():
                raise ValueError(f"Field '{val}' is required.")
            if self[val] is None:
                raise ValueError(f"Field '{val}' must not be None.")
            if not isinstance(self[val], type):
                if hasattr(self[val], '__len__') and len(self[val]) == 0:  # noqa
                    raise ValueError(f"Field '{val}' must not be empty.")
        for key in Configuration.ReservedKeys.__dict__.values():
            if key in self.keys():
                if self[key] is not None:
                    raise ValueError(f"Field '{key}' is reserved.")
        self._metadata_set = False

    def __deepcopy__(self, memo):
        """
        Create a deep copy of the configuration, excluding reserved
        keys.

        Parameters
        ----------
        memo : dict
            Memoization dictionary for deepcopy.

        Returns
        -------
        Configuration
            A deep-copied instance of the configuration.
        """
        from copy import deepcopy
        reserved_keys = Configuration.ReservedKeys.__dict__.values()
        filtered_dict = deepcopy({k: v for k, v in self.items()
                                  if k not in reserved_keys})
        s = self.__class__(**filtered_dict)  # create new Configuration
        for key, value in {k: v for k, v in self.items()
                           if k in reserved_keys}.items():
            dict.__setitem__(s, key, deepcopy(value))
        return s

    def __setitem__(self, key, value):
        """
        Prevent modification of configuration fields.

        Raises
        ------
        ValueError
            If an attempt is made to modify the configuration.
        """
        raise ValueError("Configuration object is read-only. To "
                         "store user data, use contexts.")

    def delitem(self, key):
        """
        Prevent deletion of configuration fields.

        Raises
        ------
        ValueError
            If an attempt is made to delete a configuration field.
        """
        raise ValueError("Configuration object is read-only. To "
                         "store user data, use contexts.")
