"""
test_nat_mch_moxa
~~~~~~~~~~~~~~~~~

Unit test for the NATMCHMOXA module.
"""

from gendev_tools.nat_mch.nat_mch_moxa import NATMCHMoxa
from pytest_testconfig import config

__author__ = "Felipe Torres González"
__copyright__ = "Copyright 2021, ESS GenDev Tools"
__license__ = "GPL-3.0"
__version__ = "0.1"
__maintainer__ = "Felipe Torres González"
__email__ = "felipe.torresgonzalez@ess.eu"
__status__ = "Development"


class TestNATMCHMOXA:
    def setup(self):
        self.valid_mch = NATMCHMoxa(
            mch_ip_address=config["valid_ip_address"],
            moxa_ip_address=config["moxa_valid_ip_address"],
            port=config["moxa_valid_port"],
        )

    def test_device_info(self):
        """Test the device_info feature when using a MOXA to connect to the MCH"""
        device_info = self.valid_mch.device_info()
        assert config["device_info"] == device_info

    def test_set_dhcp_mode(self):
        dhcp_enabled = self.valid_mch.set_dhcp_mode()
        assert dhcp_enabled == (True, "")

    def test_update_fw(self):
        """Test the update_fw feature when using a MOXA to connect to the MCH"""
        response = self.valid_mch.update_fw(config["update_fw"]["invalid_fw"])
        assert response[0] is False
        # response = self.valid_mch.update_fw(config["update_fw"]["valid_fw"])
        # assert response[0] is True
