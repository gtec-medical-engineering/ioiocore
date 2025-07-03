class Context(dict):
    """
    A dictionary-based context class.
    """

    class Keys:
        INPUT: str = "input"
        OUTPUT: str = "output"

    def __init__(self, input: dict, output: dict):
        dict.__init__(self,
                      {self.Keys.INPUT: input,
                       self.Keys.OUTPUT: output})

    def __setitem__(self, key, value):
        """
        Prevent modification of context fields.

        Raises
        ------
        ValueError
            If an attempt is made to modify the context.
        """
        raise ValueError("Context is read-only. To modify data, "
                         "override the setup() method.")

    def delitem(self, key):
        """
        Prevent deletion of context fields.

        Raises
        ------
        ValueError
            If an attempt is made to delete a context field.
        """
        raise ValueError("Context is read-only. To modify data, "
                         "override the setup() method.")

    @property
    def input(self):
        return self[self.Keys.INPUT]

    @property
    def output(self):
        return self[self.Keys.OUTPUT]
