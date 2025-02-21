import ioiocore.imp as imp


class Interface:
    """
    A base interface class that provides a factory method for
    creating an implementation instance.
    """

    _IMP_CLASS = imp.Implementation
    _imp: _IMP_CLASS  # type: ignore

    # factory method
    def create_implementation(self, **kwargs):
        """
        Factory method to create an instance of the implementation
        class.

        This method ensures that the implementation instance is only
        created once per object.

        Parameters
        ----------
        **kwargs : dict
            Keyword arguments to be passed to the implementation
            class constructor.
        """
        if not hasattr(self, '_imp'):
            self._imp = self._IMP_CLASS(**kwargs)
