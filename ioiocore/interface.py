import ioiocore.imp as imp


class Interface:

    _IMP_CLASS = imp.Implementation
    _imp: _IMP_CLASS  # type: ignore

    # factory method
    def create_implementation(self,
                              **kwargs):
        if not hasattr(self, '_imp'):
            self._imp = self._IMP_CLASS(**kwargs)
