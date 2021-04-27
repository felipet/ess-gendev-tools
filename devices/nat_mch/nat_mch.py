# -*- coding: utf-8 -*-

"""
nat_mch.py
~~~~~~~~~~

Implementation of the GenDev interface for NAT MCHs.

This module fully implements the GenDev interface. This is achieved by the use
of several sub-modules which implement different ways to access an NAT MCH.
This device doesn't allow a simple and straightforward implementation using an
only interface, so that, multiple communication ways are used. The golden rule
is achieving a reliable solution with the best performance.
"""

import logging
from ..gendev_interface import GenDevInterface, ConnType
from ..gendev_err import ConnNotImplemented, FeatureNotSupported
# from .nat_mch_web import NATMCHWeb
from .nat_mch_telnet import NATMCHTelnet

__author__ = "Felipe Torres González"
__copyright__ = "Copyright 2021, ESS MCH Tools"
__credits__ = ["Felipe Torres González", "Ross Elliot", "Jeong Han Lee"]
__license__ = "GPL-3.0"
__version__ = "0.1"
__maintainer__ = "Felipe Torres González"
__email__ = "felipe.torresgonzalez@ess.eu"
__status__ = "Development"


class NATMCH(GenDevInterface):
    """NAT MCH device.

    This class is connection-agnostic, which means there are no internal
    details about the particular implementation attending to the chosen
    connection type. This class should call child subclasses depending on
    the chosen connection type and format the information properly.

    When two interfaces could be used for the same purpose, the most reliable
    should be used. That is auto managed by the class when all the supported
    communication interfaces are properly specified to the module.

    Within the interface module, an enumerated type is provided defining all
    the allowed communication methods. Specify what are supported by the
    MCH when instantiating this class. As a rule of thumb, if the MCH is able
    to get a valid IP address, all the interfaces relying on the network are
    available, the regular ETHER communication type is the best option, as it
    directly access the resources from the web server of the MCH (fastest and
    most reliable method), but ETHER doesn't support the execution of all the
    methods offered by the API, check the documentation of each method to
    check what type of connection is required.
    """

    def __init__(self,
                 ip_address: str,
                 allowed_conn: list,
                 device_model: str = "MCH",
                 manufacturer: str = "NAT",
                 serial_num: str = None,
                 hostname: str = None,
                 vlan: str = None,
                 mac_address: str = None,
                 logger: logging.Logger = None):
        """Class constructor.

        The attributes that allow to be skipped will be auto filled once the
        device_info method is called the first time. In order to enable
        logging, specify a valid reference to a Logger.

        Args:
            device_model: string identifying the device.
            manufacturer: name of the manufacturer.
            serial_num: serial number of the device.
            ip_addr: the given IP to the MCH in CSEntry.
            allowed_conn: list of connections supported by the MCH.
            hostname: the registered hostname in CSEntry for the MCH.
            vlan: the registered VLAN in CSEntry for the MCH.
            mac_address: the MAC address of the network interface.
            logger: reference to a Logger instance.

        Raises:
            gendev_err.ConnNotImplemented if a communication interface that
            is not supported by the implementation was included in the
            *allowed_con* argument.
        """
        self.ip_address = ip_address
        self.device_model = device_model
        self.manufacturer = manufacturer
        self.serial_num = serial_num
        self.allowed_conn = allowed_conn
        self.hostname = hostname
        self.vlan = vlan
        self.mac_address = mac_address
        self.logger = logger
        self._eth_conn = None
        self._tel_conn = None
        self._ser_conn = None
        self._mox_conn = None
        self._ssh_conn = None

        # Open the valid connections
        # if ConnType.ETHER in self.allowed_conn:
        #     self._eth_conn = NATMCHWeb(self.ip_address)
        if ConnType.TELNET in self.allowed_conn:
            self._tel_conn = NATMCHTelnet(self.ip_address)
        if ConnType.SERIAL in self.allowed_conn:
            raise ConnNotImplemented("The serial interface is not implemented"
                                     " for NAT MCHs.")
        if ConnType.MOXA in self.allowed_conn:
            raise ConnNotImplemented("The MOXA interface is not implemented"
                                     " for NAT MCHs.")
        if ConnType.SSH in self.allowed_conn:
            raise ConnNotImplemented("The SSH interface is not implemented"
                                     " for NAT MCHs.")

        # TBD: support logging
        # if self.logger is not None:
        #     self.logger.info(
        #         'GenDev::Constructor - A new device has been registered'
        #         '\tDevice model: {}'.format(self.device_model)
        #         )

    def device_info(self) -> dict:
        """Retrieve the main information about the device.

        The information is returned in a dictionary with 2 categories:
        *board* and *network*.
        This feature is supported by all the implemented communication
        interfaces, so the best is chosen when multiple are allowed.

        Returns:
            If success, a dictionary with the device information.
            If failure, an empty dictionary on failure.

        Raises:
            gendev_err.FeatureNotSupported if the given allowed communication
            interfaces don't allow running this method.
        """
        # if ConnType.ETHER in self.allowed_conn:
        #     response = self._eth_conn.device_info()
        # elif ConnType.TELNET in self.allowed_conn:
        if ConnType.TELNET in self.allowed_conn:
            response = self._tel_conn.device_info()
        else:
            raise FeatureNotSupported("Impossible to retrieve the device"
                                      "information with the given allowed"
                                      "communication interfaces to the MCH.")

        return response

    def set_dhcp_mode(self):
        """Enables DHCP mode in the network configuration of the device.

        Raises:
            ConnectionError: If the device is not accessible.
            NoValidConn: If no valid connection types supporting this feature
                         are used by the device.
        """
        raise NotImplementedError("This feature is not implemented yet")

    def update_fw(self, fw_version: str, part: str):
        """Update the firmware of the device.

        This feature is only supported by the Telnet communication interface.

        This method expects the firmware binary pointed by the value of the
        argument *fw_version* to be available in the TFTP server.
        Mainly, this method injects the command *update_firmware* to an NAT
        MCH.

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
        if ConnType.TELNET in self.allowed_conn:
            response = self._tel_conn.update_fw(fw_version)
        else:
            raise FeatureNotSupported("Impossible to update the fw of the"
                                      " device with the given allowed"
                                      "communication interfaces to the MCH.")
        return response

    def set_configuration(self, category, data, verify=True):
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

    def _reboot(self, sleep: int = 50):
        """Internal method to reboot the MCH after a timeout.

        Args:
            sleep: Number of seconds to wait after rebooting the device.
        """
        if ConnType.TELNET in self.allowed_conn:
            self._tel_conn._reboot(sleep)
        else:
            raise FeatureNotSupported("Impossible to reboot the device"
                                      "with the given allowed"
                                      "communication interfaces to the MCH.")

    def _parse_config(self):
        """Internal method to parse the configuration of the MCH.

        When pulling content from the MCH, it might be needed to clean it and
        structure it properly so the rest of the logic can use the data
        efficiently or it can be presented to an user in a meaningful way.

        Raises:
            ConnectionError: If the device is not accessible.
        """
        raise NotImplementedError
