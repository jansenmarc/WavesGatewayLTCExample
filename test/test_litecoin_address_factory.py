import unittest
from unittest.mock import MagicMock

from waves_litecoin_gateway import LitecoinAddressFactory


class LitecoinAddressFactoryTest(unittest.TestCase):
    def setUp(self):
        self._ltc_proxy = MagicMock()
        self._address_factory = LitecoinAddressFactory(self._ltc_proxy)

    def test_create_address(self):
        expected_result = MagicMock()

        self._ltc_proxy.getnewaddress.return_value = expected_result

        self.assertEqual(self._address_factory.create_address(), expected_result)

        self._ltc_proxy.getnewaddress.assert_called_once_with()
