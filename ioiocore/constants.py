from .utilities import KeyValueContainer


class Constants:
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
        Keys used for system configuration.
        """
        INPUT_PORTS: str = "input_ports"
        OUTPUT_PORTS: str = "output_ports"
        DECIMATION_FACTOR: str = "decimation_factor"

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

    class LogTypes(KeyValueContainer):
        """
        Log message types.
        """
        INFO: str = "INFO"
        WARNING: str = "WARNING"
        ERROR: str = "ERROR"
