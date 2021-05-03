# -*- coding: utf-8 -*-

"""
test_nat_mch_telnet
~~~~~~~~~~~~~~~~~~~

Unit test for the NATMCHTelnet module.
"""
import sys
import pytest
sys.path.append('../../gendev-tools')
try:
    from gendev_tools.nat_mch.nat_mch_telnet import NATMCHTelnet
    from gendev_tools.gendev_err import *
    from pytest_testconfig import config
except Exception as e:
    raise e

__author__ = "Felipe Torres González"
__copyright__ = "Copyright 2021, ESS GenDev Tools"
__license__ = "GPL-3.0"
__version__ = "0.1"
__maintainer__ = "Felipe Torres González"
__email__ = "felipe.torresgonzalez@ess.eu"
__status__ = "Development"


class TestNATMCHTelnet:
    def setup(self):
        self.valid_mch = NATMCHTelnet(config['valid_ip_address'])

    def test_timeout(self):
        """Test the access timeout to a device that is down"""
        with pytest.raises(ConnTimeout) as e:
            self.invalid_mch = NATMCHTelnet(config['invalid_ip_address'])

    def test_device_info(self):
        """Test the device_info feature when using Telnet"""
        device_info = self.valid_mch.device_info()
        assert config['device_info'] == device_info

    def test_update_fw(self):
        """Test the update_fw feature when using Telnet"""
        response = self.valid_mch.update_fw(config['update_fw']['invalid_fw'])
        assert response[0] is False
        response = self.valid_mch.update_fw(config['update_fw']['valid_fw'])
        assert response[0] is True
