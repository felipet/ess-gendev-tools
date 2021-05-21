# -*- coding: utf-8 -*-

"""
nat_mch_web.py
~~~~~~~~~~~~~~

Incomplete implementation fo the GenDev interface. The ultimate purpose
of this module is to be encapsulated within another module that really
implements that interface.
Unfortunately, NAT MCHs don't allow to go for a full implementation of the
GenDev interface based on an only communication interface.
This module aims to provide a fast but reliable mechanism to change the
configuration parameters of the MCH. Rely on this implementation whenever
possible for interfacing an NAT MCH.
"""

import re
import requests as rq
from logging import Logger
from collections import OrderedDict
from bs4 import BeautifulSoup
from ..gendev_err import FeatureNotSupported, NoRouteToDevice, WebChanged

__author__ = ["Felipe Torres González", "Ross Elliot"]
__copyright__ = "Copyright 2021, ESS MCH Tools"
__license__ = "GPL-3.0"
__version__ = "0.3"
__maintainer__ = "Felipe Torres González"
__email__ = "felipe.torresgonzalez@ess.eu"
__status__ = "Development"


class NATMCHWeb:
    """NATMCHWeb access an NAT MCH via the web interface.

    This module uses the Web interface provided by NAT MCHs to access and change
    the values for the configuration of the device. This interface is the most
    reliable among all the offered communication interfaces to an MCH. The
    only caveat is that the interface is not designed to be used by sw but an
    human. That means, some particular features are not easy to support or they
    seem impossible to do.
    The main requirement for using this module is having the Web interface
    enabled in the MCH configuration.

    Supported operations:
    - Retrieve the general information of the MCH.
    - Change/Access the general configuration of the MCH.
    - Change/Access the backplane configuration of the MCH.
    """

    def __init__(self, ip_address: str, logger: Logger = None):
        """Class constructor.

        Args:
            ip_address: the IP address of the MCH.
        """
        self.ip_address = ip_address

        # Header for the HTML methods, the most important variable is the
        # Authorization because NAT MCHs need to login using Root:NAT.
        self._http_headers = {
            "Accept-Language": "en-GB,en;q=0.5",
            "Authorization": "Basic cm9vdDpuYXQ=",
            "Connection": "keep-alive",
        }

        is_mch = self._check_is_mch()
        if not is_mch[0]:
            raise NoRouteToDevice(is_mch[1])

        # Regular expresions for parsing data
        self._match_fw_ver = re.compile(
            r"Firmware Version\n(V\d{1,2}\.\d{1,2}\.\d{1,2})"
        )
        self._match_fpga_ver = re.compile(r"FPGA Version\n(V\d{1,2}\.\d{1,2})")
        self._match_mcu_ver = re.compile(
            r"Microcontroller Version\n(V\d{1,2}\.\d{1,2})"
        )
        self._match_board_sn = re.compile(r"Board Serial Number\n(\d{6}-\d{4})")
        self._match_ip_addr = re.compile(r"IP Address\n((\d{1,3}\.?){4})")
        self._match_mac_addr = re.compile(r"IEEE Address\n(([\d\D]{2}:?){6})")
        self._match_subnet_mask = re.compile(r"Subnet Mask\n((\d{1,3}\.?){4})")
        self._match_gateway_addr = re.compile(r"Gateway Address\n((\d{1,3}\.?){4})")

    def _check_is_mch(self):
        """Method to check that the device associated with the IP address
        is an MCH.

        Returns:
            False, if not an MCH.
            True, if is an MCH.
        """
        is_mch = True
        message = None

        try:
            response = rq.get(
                "http://{}/index.asp".format(self.ip_address),
                headers=self._http_headers,
                timeout=2,
            )
        except Exception as e:
            if isinstance(e, rq.exceptions.ConnectionError):
                raise NoRouteToDevice(
                    "Error connecting to MCH web interface at {0}:".format(
                        self.ip_address
                    )
                )

        if not response.ok:
            is_mch = False
            message = "Unable to reach device at {0}, status code {1}:".format(
                self.ip_address, response.status_code
            )
        else:
            html_content = BeautifulSoup(response.text, "html.parser")
            title = html_content.head.title.text

            if not title == "MCH Configuration":
                is_mch = False
                message = (
                    "Device at IP {0} is not an MCH. Retrieved description"
                    " of device: ''{1}''".format(self.ip_address, title)
                )

        return is_mch, message

    def _parse_basecfg(self, response):
        """Internal method to parse the HTML content for the base configuration.

        Args:
            response: The output from the requests.get call.

        Returns:
            A OrderedDict containing the settings for the base configuration
            page in the MCH webpage.
        """
        mch_config = OrderedDict()
        html_content = BeautifulSoup(response.text, "html.parser")
        tables = html_content.body.find_all("table")

        # Each subsection of the MCH Configuration is a different HTML
        # table. Each table will add a child dictionary to the main one,
        # indexed by the tr tag label from the HTML code.
        for table in tables:
            # Each section has a th tag. Then a set of parameters are included
            # within the section.
            table_title = table.th.text.strip()
            # Set the table heather as the dict key
            mch_config[table_title] = OrderedDict()

            for row in table.find_all("tr"):
                # Now, we're inside a section. Two kinds of parameters:
                # - parameters with a numeric value
                # - parameters with a select

                select_params = row.find("select")
                if select_params:
                    # Form with select values
                    # 1. First get the name attribute (should use find_all?)
                    name = select_params["name"].strip()
                    # 2. Look for the selected value for the given parameter
                    subrows = row.find_all("option")
                    value = [r["value"] for r in subrows if "selected" in str(r)][0]

                    # Rough check, but better than nothing
                    if name is None or value is None:
                        continue

                    mch_config[table_title][name] = value
                    # No more stuff to parse for this row
                    continue

                # Form with input values
                input_params = row.find_all("input")

                if not input_params:
                    continue

                # How many fields does this setting have?
                if len(input_params) > 1:
                    name = input_params[0]["name"]
                    value = [v["value"] for v in input_params]
                else:
                    name = input_params[0]["name"]
                    value = input_params[0]["value"]

                if name is None or value is None:
                    continue
                mch_config[table_title][name] = value
                # No more stuff to parse for this row
                continue

        # The previous set of parameters will be encapsulated so
        # a global dictionary can contain other set of parameters
        globalcfg = OrderedDict()
        globalcfg["Base MCH parameter"] = mch_config

        return globalcfg

    def _parse_pcie(self, response):
        """Internal method to parse the HTML content for the PCIe configuration.

        This method receives the content of the page /goform/pcie_vs_config* and
        extracts the information from the Link width and Virtual swith tables.

        Args:
            response: The output from the requests.get call.

        Returns:
            A OrderedDict containing the settings for the PCIe configuration
            page in the MCH webpage.
        """
        mch_config = OrderedDict()
        # Use lxml as parser, html.parser doesn't parse this web properly!
        html_content = BeautifulSoup(response.text, "lxml")
        # Divide the content by forms
        forms = html_content.body.find_all("form")

        # The first form contains the Link with configuration
        cfgtitle = "Link Width Configuration"
        if (
            forms[0].attrs["action"] != "/goform/pcie_width_link_ctrl"
            or forms[1].attrs["action"] != "/goform/pcie_vs_cfg_refresh"
        ):
            raise WebChanged("The PCIe configuration page has changed its format")

        # There're 3 tables, each one configures a pair of adjacent AMC slots.
        # From each table, get the value selecting a link with for each pair
        # of AMC slots.
        link_inputs = forms[0].find_all("input")
        mch_config[cfgtitle] = OrderedDict()
        curr_station = "Station_0"

        for input in link_inputs:
            if input["name"] == curr_station:
                if "checked" in input.attrs:
                    mch_config[cfgtitle][curr_station] = input["value"]
                    next_station = int(curr_station[-1]) + 1
                    curr_station = "Station_{}".format(next_station)

        # Now, extract the information from the table with the Virtual Switch
        # Configuration.
        cfgtitle = "PCIe Virtual Switch configurationt"
        mch_config[cfgtitle] = OrderedDict()

        # The first kind of rows are indexed by the index.
        indexes = [str(i) for i in range(6)]
        indexes = ["none"] + indexes
        indexes.append("Max. Link Speed")

        # Now, iterate over the rows of the table
        rows = forms[1].find_all("tr")

        for row in rows:
            # Let's skip all the initial rows with no data to be collected
            # Only the first th field is properly parsed, so this dirty trick
            # came up to cope with the issue:
            title = row.find("b")
            if title is None or (title is not None and title.text not in indexes):
                continue

            # Check whether the first select field is enabled in the row
            selects = row.find_all("select")

            # The row tagged with "none" has not select input fields
            if selects != []:
                # First, parse the Upstream option
                for s in selects:
                    for option in s.find_all("option"):
                        if "selected" in option.attrs:
                            mch_config[cfgtitle][s["name"]] = option["value"]

            # Now, iterate over the columns and check what radio buttons
            # are checked.

            for input in row.find_all("input"):
                if "checked" in input.attrs and "disabled" not in input.attrs:
                    name = input["name"]
                    mch_config[cfgtitle][name] = input["value"]

        # The previous set of parameters will be encapsulated so
        # a global dictionary can contain other set of parameters
        pciecfg = OrderedDict()
        pciecfg["PCIe parameter"] = mch_config

        return pciecfg

    def device_info(self) -> dict:
        """Device info method."""
        response = rq.get(
            "http://{}/goform/GetInfo".format(self.ip_address),
            headers=self._http_headers,
        )

        if response.ok:
            html_content = BeautifulSoup(response.text, "html.parser")
            raw_info = html_content.get_text()
            resp_dict = dict()
            resp_dict["Board"] = dict()

            resp_dict["Board"]["fw_ver"] = self._match_fw_ver.search(raw_info).group(1)
            resp_dict["Board"]["fpga_ver"] = self._match_fpga_ver.search(
                raw_info
            ).group(1)
            # The web interface returns the version number with the prefix 'V',
            # while the other interfaces have no prefix.
            # Remove the prefix for consistency
            resp_dict["Board"]["mcu_ver"] = (
                self._match_mcu_ver.search(raw_info).group(1).strip("V")
            )
            resp_dict["Board"]["serial_num"] = self._match_board_sn.search(
                raw_info
            ).group(1)

            resp_dict["Network"] = dict()
            resp_dict["Network"]["ip_address"] = self._match_ip_addr.search(
                raw_info
            ).group(1)
            resp_dict["Network"]["mac_address"] = self._match_mac_addr.search(
                raw_info
            ).group(1)
            resp_dict["Network"]["subnet_address"] = self._match_subnet_mask.search(
                raw_info
            ).group(1)
            resp_dict["Network"]["gateway_address"] = self._match_gateway_addr.search(
                raw_info
            ).group(1)

        else:
            resp_dict = dict()

        return resp_dict

    def update_fw(self, fw_path: str, part: str) -> bool:
        """Update the firmware of the device.

        This module doesn't support this featrue. The main problem is that the
        process is divided in two stages. First, the binary is sent via post to
        the MCH. Then, the MCH analyses it and decides whether is a valid MCH
        firmware image or not. If so, it provides a checkbox and a new form so
        an user can click and proceed with the udpate. Automatizing this process
        produces an error in the MCH (*multiple access error*).
        I couldn't find a solution for that, which doesn't means it doesn't
        exists because my experience with web programming is quite limited.
        """
        raise FeatureNotSupported(
            "The firmware update is not supported by this module."
        )

    def set_configuration(self, category: str, data, verify=True):
        """Change the configuration of the device.

        This method focuses on the configuration parameters that are not
        defined within a configuration script. Specifying the entire set of
        parameters is not mandatory, and also, a particular category of
        settings can be modified without affecting the rest.

        This method supports the following configuration categories (taken
        from the webpage names):

        - Base Configuration [basecfg]

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
        """
        raise FeatureNotSupported("Method not implemented yet.")

    def get_configuration(self, category: str = None) -> OrderedDict:
        """Get the configuration of the device.

        This method returns a dictionary containing the configuration
        parameters of the device implementing this interface. If the device
        has several configuration categories, keys from the dictionary might
        contain other dictionaries.
        This method can be used for checking the right configuration of a
        device.

        This method supports the following configuration categories (taken
        from the webpage names):

        - Base Configuration [basecfg]

        Args:
            category: points to a subset of the configuration parameters of
                      the device. Use the values given between brackets from
                      the previous item list.

        Returns:
            OrderedDict: An ordered dict containing the settings in the same
            ordered as they are found in the web page. When *category* =
            **backplane**, the dictionary conatins only one key (*Backplane
            Configuration*) and the whole configuration file as value for that
            key.
        """
        # Check the input parameter
        if category == "basecfg":
            cfgword = "change_mch_cfg"
        elif category == "pcie":
            cfgword = "pcie_width_link_ctrl"
        elif category == "backplane":
            # Request the generation of the script file to the MCH
            cfgword = "web_cfg_backup_show_menu"
        else:
            cfgword = ""

        mch_config: OrderedDict = OrderedDict()

        if cfgword == "":
            return mch_config

        response = rq.get(
            "http://{}/goform/{}".format(self.ip_address, cfgword),
            headers=self._http_headers,
        )

        if response.ok:
            if category != "backplane":
                # Let's parse the content
                parse_method = getattr(self, "_parse_{}".format(category))
                mch_config = parse_method(response)
            else:
                cfgword = "nat_mch_startup_cfg.txt"
                response = rq.get(
                    "http://{}/{}".format(self.ip_address, cfgword),
                    headers=self._http_headers,
                )
                mch_config["Backplane Configuration"] = (
                    response.text if response.ok else ""
                )

        return mch_config
