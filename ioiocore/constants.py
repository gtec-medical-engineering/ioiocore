class KeyValueContainer:
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
            dunder attributes.
        """
        return [v for k, v in vars(cls).items() if not k.startswith("__")]

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


class Constants(KeyValueContainer):
    """
    A collection of categorized constants used in the system.
    """

    class Defaults(KeyValueContainer):
        """
        Default values for various system components.
        """
        PORT_OUT: str = "out"
        PORT_IN: str = "in"
        NODE_NAME: str = "default"

    class Keys(KeyValueContainer):
        """
        Keys used for system configuration and metadata.
        """
        SAMPLING_RATE: str = "sampling_rate"
        CHANNEL_COUNT: str = "channel_count"
        INPUT_PORTS: str = "input_ports"
        OUTPUT_PORTS: str = "output_ports"

    class Timing(KeyValueContainer):
        """
        Timing modes available in the system.
        """
        SYNC: str = "Sync"
        ASYNC: str = "Async"
        INHERITED: str = "Inherited"

    class States(KeyValueContainer):
        """
        Possible states of a pipeline.
        """
        STOPPED: str = "Stopped"
        RUNNING: str = "Running"

    class Conditions(KeyValueContainer):
        """
        System conditions indicating operational status.
        """
        HEALTHY: str = "Healthy"
        ERROR: str = "Error"
