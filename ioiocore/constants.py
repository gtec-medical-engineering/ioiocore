class KeyValueContainer:
    @classmethod
    def values(cls):
        return [v for k, v in vars(cls).items() if not k.startswith("__")]

    @classmethod
    def keys(cls):
        return [k for k, v in vars(cls).items() if not k.startswith("__")]


class Constants(KeyValueContainer):

    class Defaults(KeyValueContainer):
        PORT_OUT: str = "out"
        PORT_IN: str = "in"
        NODE_NAME: str = "default"

    class Keys(KeyValueContainer):
        SAMPLING_RATE: str = "sampling_rate"
        CHANNEL_COUNT: str = "channel_count"
        INPUT_PORTS: str = "input_ports"
        OUTPUT_PORTS: str = "output_ports"

    class Timing(KeyValueContainer):
        SYNC: str = "Sync"
        ASYNC: str = "Async"
        INHERITED: str = "Inherited"

    class States(KeyValueContainer):
        STOPPED: str = "Stopped"
        RUNNING: str = "Running"

    class Conditions(KeyValueContainer):
        HEALTHY: str = "Healthy"
        ERROR: str = "Error"
