# -*- coding: utf-8 -*-

"""
gendev_err.py
~~~~~~~~~~

Custom exeception types for the GenDev Tools library.
"""

__all__ = ['ConnNotImplemented', 'ConnTimeout', 'NoRouteToDevice',
           'FeatureNotSupported']
__author__ = "Felipe Torres González"
__copyright__ = "Copyright 2021, ESS MCH Tools"
__credits__ = ["Felipe Torres González", "Ross Elliot", "Jeong Han Lee"]
__license__ = "GPL-3.0"
__version__ = "0.1"
__maintainer__ = "Felipe Torres González"
__email__ = "felipe.torresgonzalez@ess.eu"
__status__ = "Development"


class ConnNotImplemented(Exception):
    """Connection Not Implemented Exception.

    This exeception is raised when an operation relies on a particular
    connection type that is not implemented for the given device.
    """

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'ConnNotImplemented, {0} '.format(self.message)
        else:
            return 'ConnNotImplemented has been raised'


class ConnTimeout(Exception):
    """Connection timeout Exception.
    """

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'ConnTimeout, {0} '.format(self.message)
        else:
            return 'ConnTimeout has been raised'


class NoRouteToDevice(Exception):
    """Connection timeout Exception.
    """

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'NoRouteToDevice, {0} '.format(self.message)
        else:
            return 'NoRouteToDevice has been raised'


class FeatureNotSupported(Exception):
    """Feature not supported exception.

    This exception is raised when a feature is not possible with the given
    valid communication interfaces to the MCH.
    """

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'ConnTimeout, {0} '.format(self.message)
        else:
            return 'ConnTimeout has been raised'
