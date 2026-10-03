"""PyInstaller hook for ioiocore.

Registered through the ``pyinstaller40`` entry point, so it applies to
every application frozen with ioiocore in it (gpype-docs E-PKG-07).

PyInstaller finds imports by reading bytecode, and every module under
``imp/`` ships compiled, so what those modules import is invisible to
it. A frozen application then works only while something else happens
to import the same modules. ``COMPILED_IMPORTS`` names them, and
``test/test_pyinstaller_hook.py`` keeps it equal to what the compiled
sources import.
"""

from PyInstaller.utils.hooks import collect_submodules

#: Every module the compiled sources import from outside ioiocore.
COMPILED_IMPORTS = [
    "asyncio",
    "atexit",
    "collections",
    "contextlib",
    "copy",
    "datetime",
    "importlib",
    "inspect",
    "os",
    "platform",
    "queue",
    "random",
    "sys",
    "tempfile",
    "threading",
    "time",
    "traceback",
    "typing",
    "weakref",
]

# A compiled module importing another is just as invisible.
hiddenimports = collect_submodules("ioiocore") + COMPILED_IMPORTS
