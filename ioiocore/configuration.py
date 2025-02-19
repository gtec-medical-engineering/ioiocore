class Configuration(dict):

    class ReservedKeys:
        METADATA = 'metadata'

    class Keys:
        pass

    _metadata_set: bool

    def __init__(self,
                 **kwargs):
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
        dict.__setitem__(self, Configuration.ReservedKeys.METADATA, None)
        self._metadata_set = False

    def __deepcopy__(self, memo):
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
        raise ValueError("Configuration object is read-only. To "
                         "store user data, use set_metadata().")

    def delitem(self, key):
        raise ValueError("Configuration object is read-only. To "
                         "store user data, use set_metadata().")

    def set_metadata(self, metadata: dict):
        dict.__setitem__(self, Configuration.ReservedKeys.METADATA, metadata)
        self._metadata_set = True

    def get_metadata(self) -> dict:
        return self[Configuration.ReservedKeys.METADATA]

    def has_metadata(self) -> bool:
        return self._metadata_set
