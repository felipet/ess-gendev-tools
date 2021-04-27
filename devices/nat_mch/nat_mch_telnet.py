# -*- coding: utf-8 -*-

"""
nat_mch_telnet.py
~~~~~~~~~~~~~~~~~

This is a lazy implementation of the GenDev interface. The ultimate purpose
of this module is to be encapsulated within another module that really
implements that interface.
Unfortunately, NAT MCHs don't allow to go for a full implementation of the
GenDev interface based on an only communication interface.
The main operation that is only supported by the command line interface is the
firmware update. So that, this module based on Telnet, as access way, and the
command line interface of the MCH, shall only be used to perform a firmware
update and nothing else. For other operations, better use the module based on
the communication via the MHC web interface.
"""

import re
import time
import socket
from ..gendev_err import ConnTimeout
from telnetlib import Telnet
from logging import Logger

__author__ = "Felipe Torres González"
__copyright__ = "Copyright 2021, ESS MTCA Tools"
__credits__ = ["Felipe Torres González", "Ross Elliot", "Jeong Han Lee"]
__license__ = "GPL-3.0"
__version__ = "0.1"
__maintainer__ = "Felipe Torres González"
__email__ = "felipe.torresgonzalez@ess.eu"
__status__ = "Development"


class NATMCHTelnet():
    """NATMCTelnet access an NAT MCH via Telnet.

    This module implements some operations using the command line interface
    via Telnet. Thus, the MCH has to be accessible in the network.
    The firmware update relies on **the mchconfig-server** to serve the
    firmware image using the FTP protocol.

    Supported operations:
    - Retrieve the general information of the MCH.
    - Firmware update of the MCH.
    """

    def __init__(self,
                 ip_address: str,
                 port: int = 23,
                 logger: Logger = None):
        """Class constructor.

        Args:
            ip_address: the IP address of the MCH.
            port: port of the Telnet service (usually, 23)
            logger: reference to a logger that is being used

        Raises:
            gendev_err.ConnTimeout if the device is not reachable.
        """
        self._server_ip = '172.30.4.69'
        self._fw_path = 'fw/'

        try:
            self._session = Telnet(ip_address, port, timeout=10)
        except Exception as e:
            if isinstance(e, socket.timeout):
                raise ConnTimeout(
                    "Timeout while opening the link to the MCH using Telnet")

        # Regular expresions for extracting the infomration relative to the
        # MCH from the version command.
        self._match_fw_ver = re.compile(
            r'Firmware (V\d{1,2}\.\d{1,2}\.\d{1,2})'
        )
        # Search for the first occurrence of the token FPGA
        self._match_fpga_ver = re.compile(
            r'FPGA (V\d{1,2}\.\d{1,2})'
        )
        self._match_mcu_ver = re.compile(
            r'AVR (\d{1,2}\.\d{1,2})'
        )
        self._match_board_sn = re.compile(
            r'sn: (\d{6}-\d{4})'
        )
        self._match_ip_addr = re.compile(
            r'ip address +: +((\d{1,3}\.?){4})'
        )
        self._match_mac_addr = re.compile(
            r'ieee address +: +(([\d\D]{2}:?){6})'
        )
        self._match_subnet_mask = re.compile(
            r'network mask +: +((\d{1,3}\.?){4})'
        )
        self._match_gateway_addr = re.compile(
            r'default gateway +: +((\d{1,3}\.?){4})'
        )

    def _send_command(self,
                      command: str,
                      sleep: int = 1,
                      clear_buffer: bool = True):
        """Internal method for sending a low level command to the MCH.

        This command allows forgetting about the particular details of using
        a Telnet session behind the scenes. A regular command from the MCH
        command line interface can be sent through this interface without
        worrying about the underlying communication.

        Args:
            command: command to be sent to the MCH.
            sleep: amount of seconds to wait after sending a command.
            clear_buffer: send a carriage return before the command. This
            helps clearing previous garbage from the buffer, but
            it should be used with caution because there are
            commands that doesn't expect a carriage return after.
        """
        # clean up
        if clear_buffer:
            self._session.write(b'\r')
            self._session.read_until(b'nat> ')
            time.sleep(sleep)
        self._session.write(command.encode('ascii') + b'\r')
        time.sleep(sleep)

    def _reboot(self, sleep: int = 50):
        """Internal command to send a reboot to the MCH.

        Args:
            sleep: indicates how many seconds to wait after returning from the
            method. Write a 0 to avoid it.
        """
        self._send_command("reboot")

    def _read_command(self) -> str:
        """Internal command to read the Telnet Rx buffer.

        This method attempts to read the content from the buffer without I/O
        blocking.

        Returns:
            A string containing the content of the Rx buffer.
        """
        response = self._session.read_very_eager()
        return response.decode('ascii')

    def device_info(self) -> dict:
        """Retrieve the main information about the device.

        The information is returned in a dictionary with 2 categories:
        *board* and *network*.

        Returns:
            If success, a dictionary with the device information.
            If failure, an empty dictionary on failure.
        """
        self._send_command("version")
        raw_info_version = self._read_command()
        self._send_command("ni")
        raw_info_network = self._read_command()

        if raw_info_version != "" and raw_info_network != "":
            resp_dict = dict()
            resp_dict['board'] = dict()

            resp_dict['board']['fw_ver'] = self._match_fw_ver.search(
                raw_info_version).group(1)
            resp_dict['board']['fpga_ver'] = self._match_fpga_ver.search(
                raw_info_version).group(1)
            resp_dict['board']['mcu_ver'] = self._match_mcu_ver.search(
                raw_info_version).group(1)
            resp_dict['board']['serial_num'] = self._match_board_sn.search(
                raw_info_version).group(1)

            resp_dict['network'] = dict()
            resp_dict['network']['ip_address'] = self._match_ip_addr.search(
                raw_info_network).group(1)
            resp_dict['network']['mac_address'] = self._match_mac_addr.search(
                raw_info_network).group(1)
            resp_dict['network']['subnet_address'] = self._match_subnet_mask.search(
                raw_info_network).group(1)
            resp_dict['network']['gateway_address'] = self._match_gateway_addr.search(
                raw_info_network).group(1)

        else:
            resp_dict = dict()

        return resp_dict

    def update_fw(self, fw_version: str, part: str = "MCH") -> tuple:
        """Update the firmware of the device.

        This method expect the firmware binary pointed by the value of the
        argument *fw_version* to be available in the TFTP server.
        Mainly, this method injects the command *update_firmware* to an NAT MCH.

        Args:
            fw_version: version release number for the new fw.
            part: not used

        Returns:
            If failure, it returns a tuple containing False, and a message
            about the failure.
            If success, it returns True,
        """
        self._send_command("update_firmware")
        # Avoid clearing the buffer bewteen these commands because it would
        # skip the update mode in the MCH.
        self._send_command("{}:{}{}/mch_fw_{}.bin".format(
                self._server_ip,
                self._fw_path,
                fw_version,
                fw_version
            ),
            clear_buffer=False)
        # Erasing the internal memory. If it is attempted to read now from the
        # buffer, it will get the promt.
        time.sleep(30)
        # There's a useless promt which is received first, get rid of it, and
        # wait for the good one that should come when the flashing is finished.
        response = self._session.read_until(b'nat> ')
        response = self._session.read_until(b'nat> ')
        response = response.decode('ascii')

        # Let's see if the update was successful. The MCH prints the word
        # "successful" at the end of the process, just before the prompt.
        if 'successful' in response:
            success = True,
            self._reboot()
            # Finally, wait for the MCH to complete the reboot process
            time.sleep(50)
        else:
            # Something went wrong, let's check it!
            if 'TFTP: could not get file' in response:
                # This error is mainly caused when the target fw_version
                # is not available in the TFTP server.
                success = False, 'The fw version {} couldn\'t be found in the'\
                    ' TFTP server'.format(fw_version)
            else:
                success = False, 'Unknown error. Check the debug log.'

        return success
