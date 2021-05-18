# -*- coding: utf-8 -*-

"""
test_nat_mch_web
~~~~~~~~~~~~~~~~~~~

Unit test for the NATMCHWeb module.
"""
import pytest

from gendev_tools.nat_mch.nat_mch_web import NATMCHWeb
from gendev_tools.gendev_err import NoRouteToDevice
from pytest_testconfig import config

__author__ = "Ross Elliot"
__copyright__ = "Copyright 2021, ESS GenDev Tools"
__license__ = "GPL-3.0"
__version__ = "0.1"
__maintainer__ = "Ross Elliot"
__email__ = "ross.elliot@ess.eu"
__status__ = "Development"


class TestNATMCHWeb:
    def setup(self):
        self.valid_web = NATMCHWeb(config["valid_ip_address"])

    def test_check_is_mch(self):
        """Test for an incorrect IP address"""
        with pytest.raises(NoRouteToDevice):
            self.invalid_web = NATMCHWeb(config["invalid_ip_address"])

    def test_device_info(self):
        """Test that the device info is scraped from the web interface"""
        device_info = self.valid_web.device_info()
        assert config["device_info"] == device_info
