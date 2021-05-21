# -*- coding: utf-8 -*-

"""
test_nat_mch_web
~~~~~~~~~~~~~~~~

Unit test for the NATMCHWeb module.
"""
import pytest
from collections import OrderedDict
from gendev_tools.nat_mch.nat_mch_web import NATMCHWeb
from gendev_tools.gendev_err import NoRouteToDevice, FeatureNotSupported
from pytest_testconfig import config

__author__ = ["Ross Elliot", "Felipe Torres González"]
__copyright__ = "Copyright 2021, ESS GenDev Tools"
__license__ = "GPL-3.0"
__version__ = "0.2"
__maintainer__ = "Ross Elliot"
__email__ = "ross.elliot@ess.eu"
__status__ = "Development"


class TestNATMCHWeb:
    def setup(self):
        self.valid_web = NATMCHWeb(config["Metadata"]["valid_ip_address"])

    def test_check_is_mch(self):
        """Test for an incorrect IP address"""
        with pytest.raises(NoRouteToDevice):
            self.invalid_web = NATMCHWeb(config["Metadata"]["invalid_ip_address"])

    def test_device_info(self):
        """Test that the device info is scraped from the web interface"""
        device_info = self.valid_web.device_info()
        assert config["Board"] == device_info["Board"]
        assert config["Network"] == device_info["Network"]

    def test_update_fw(self):
        """Test the firmware update feature."""
        with pytest.raises(FeatureNotSupported):
            self.valid_web.update_fw("", "")

    def test_get_configuration(self):
        """Test the get_configuration method for all the possible category types."""
        empty_dict = OrderedDict()
        assert empty_dict == self.valid_web.get_configuration()
        assert empty_dict == self.valid_web.get_configuration("deadbeef")
        cfgdict = self.valid_web.get_configuration("basecfg")
        assert cfgdict["Base MCH parameter"] == config["Base MCH parameter"]
        pciedict = self.valid_web.get_configuration("pcie")
        assert pciedict["PCIe parameter"] == config["PCIe parameter"]
