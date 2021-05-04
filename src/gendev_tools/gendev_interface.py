# -*- coding: utf-8 -*-

"""
gendev_interface
~~~~~~~~~~~~~~~~

Public API offering some useful features for configuring/maintaining devices
supported by the ICSHWI WP4.

This is just an interface, which means it has to be implemented for a
particular device. Don't use this directly, look inside the project for a
module that implements this interface.

Main features supported by the API:
- FW update
- Setting configuration parameters
- Running dry checks against a golden configuration
"""

import abc
import enum
import logging

__author__ = "Felipe Torres González"
__copyright__ = "Copyright 2021, ESS MCH Tools"
__credits__ = ["Felipe Torres González", "Ross Elliot", "Jeong Han Lee"]
__license__ = "GPL-3.0"
__version__ = "0.1"
__maintainer__ = "Felipe Torres González"
__email__ = "felipe.torresgonzalez@ess.eu"
__status__ = "Development"


class ConnType(enum.Enum):
    """This enumeration specifies the allowed connection types.

    Any device implementing the GenDevInterface should allow using one or more
    of the following connection types:

    - ETHER: Ethernet connection using TCP/IP.
    - SERIAL: Serial connection.
    - MOXA: Serial connection through a MOXA Hub (accessible over Ethernet).
    - TELNET: Serial connection through Ethernet using Telnet.
    - SSH: Secure Shell connection through Ethernet.
    """

    ETHER = 0
    SERIAL = 1
    MOXA = 2
    TELNET = 3
    SSH = 4


class GenDevInterface(metaclass=abc.ABCMeta):
    """Interface for a Generic Device.

    This interface can be implemented to control any device that includes some
    sort of management interface: command line trough a serial port, a web
    interface, ...

    Details for particular devices should be handled on their implementation
    for this interface.
    """

    def __init__(
        self,
        device_model: str,
        manufacturer: str,
        serial_num: str,
        allowed_conn: list,
        hostname: str = None,
        vlan: str = None,
        mac_address: str = None,
        logger: logging.Logger = None,
    ):
        """Class constructor.

        Args:
            device_model: The device identifier
            manufacturer: The device manufacturer
            serial_num: Serial number of the device
            allowed_conn: A list containing the supported connection types for
                         the device. See the ConnType enum for details.
            hostname: given hostname by CSEntry.
            vlan: vlan in which the device is registered.
            mac_address: MAC address of the network interface connected to the
                         TN network.
            logger: Reference to a logger instance. When this is not None, the
                    code will add info to the main's program log.
        """
        pass

    @abc.abstractmethod
    def device_info(self) -> dict:
        """Retrieve the main information about the device.

        The information is returned in a dictionary with 2 categories:
        *board* and *network*.

        Returns:
            If success, a dictionary with the device information.
            If failure, an empty dictionary on failure.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def set_dhcp_mode(self):
        """Enables DHCP mode in the network configuration of the device.

        Raises:
            ConnectionError: If the device is not accessible.
            NoValidConn: If no valid connection types supporting this feature
                         are used by the device.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def update_fw(self, fw_version: str, part: str):
        """Update the firmware of the device.

        Args:
            fw_version: version release number for the new fw.
            part: modifier allowing the update of different parts within
                  the same device.

        Returns:
            If failure, it returns a tuple containing False, and a message
            about the failure.
            If success, it returns (True,)

        Raises:
            ConnectionError: If the device is not accessible.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def set_configuration(self, category: str, data, verify=True):
        """Change the configuration of the device.

        This method focuses on the configuration parameters that are not
        defined within a configuration script. Specifying the entire set of
        parameters is not mandatory, and also, a particular category of
        settings can be modified without affecting the rest.

        Args:
            category(str): settings category to be affected.
            data(dict): dictionary containing the values to be modified
            verify(bool): when True, the method performs a checking after
                          setting the new parameters.

        Returns:
            - 0 when successful or verify=False
            - A dictionary containing the values that are not matching the
              expectation. For each key, the expected and the given values are
              provided.

        Raises:
            ConnectionError: If the device is not accessible.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_configuration(self, category: str = None):
        """Get the configuration of the device.

        This method returns a dictionary containing the configuration
        parameters of the device implementing this interface. If the device
        has several configuration categories, keys from the dictionary might
        contain other dictionaries.
        This method can be used for checking the good configuration of a
        device.

        Args:
            category: points to a subset of the configuration parameters of
                      the device.

        Returns:
            A dictionary containing the configuration of the device.

        Raises:
            ConnectionError: If the device is not accessible.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _reboot(self, sleep: int = 50):
        """Internal method to reboot the MCH after a timeout.

        Args:
            timeout: Number of seconds to wait before rebooting the device.

        Raises:
            ConnectionError: If the device is not accessible.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _parse_config(self):
        """Internal method to parse the configuration of the MCH.

        When pulling content from the MCH, it might be needed to clean it and
        structure it properly so the rest of the logic can use the data
        efficiently or it can be presented to an user in a meaningful way.

        Raises:
            ConnectionError: If the device is not accessible.
        """
        raise NotImplementedError
