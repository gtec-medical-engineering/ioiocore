# -*- coding: utf-8 -*-
"""
ioiocore
-------

A realtime data processing framework for python

:copyright: (c) 2024 g.tec medical engineering GmbH

"""

# compatibility
from __future__ import absolute_import, division, print_function

# get version
from .__version__ import __version__  # noqa: F401, E402

# allow lazy loading
from .constants import Constants  # noqa: F401
from .configuration import Configuration  # noqa: F401
from .i_port import IPort  # noqa: F401
from .o_port import OPort  # noqa: F401
from .node import Node  # noqa: F401
from .i_node import INode  # noqa: F401
from .o_node import ONode  # noqa: F401
from .io_node import IONode  # noqa: F401
from .logger import Logger, LogType, LogEntry  # noqa: F401
from .pipeline import Pipeline  # noqa: F401
from .portable import Portable

Portable.add_preinstalled_module('ioiocore')
