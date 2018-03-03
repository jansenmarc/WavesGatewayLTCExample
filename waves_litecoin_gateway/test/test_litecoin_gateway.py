import unittest
from unittest.mock import patch, MagicMock

from decimal import Decimal

from waves_gateway import KeyPair

from waves_litecoin_gateway import LitecoinGateway


class LitecoinGatewayTest(unittest.TestCase):
    def setUp(self):
        self._config_file = """
[node]
coin = http://bla:test@345.234.23.234:20000
waves = http://342.234.234.253:6869

[fee]
coin = 0.02000000
gateway = 0.01000000

[gateway_address]
owner = akgsjfhsjkghweg
waves_public_key = hjskgfj234786hfjk
waves_private_key = 698473256icz7zftj
coin_public_key = cgi34zvci7

[mongodb]
host = localhost
port = 27017
database = ltc-gateway

[other]
environment = test
        """
        self._gateway_waves_address = KeyPair(public="hjskgfj234786hfjk", secret="698473256icz7zftj")
        self._ltc_fee = Decimal("0.02000000")
        self._gateway_fee = Decimal("0.01000000")
        self._gateway_owner_address = "akgsjfhsjkghweg"
        self._ltc_node = "http://bla:test@345.234.23.234:20000"
        self._waves_node = "http://342.234.234.253:6869"
        self._gateway_ltc_address = KeyPair(public="cgi34zvci7", secret=None)
        self._mongo_host = "localhost"
        self._mongo_port = 27017
        self._mongo_database = "ltc-gateway"

    @patch('waves_gateway.Gateway', autospec=True)
    @patch('waves_litecoin_gateway.lib.LitecoinAddressFactory', autospec=True)
    @patch('waves_litecoin_gateway.lib.LitecoinChainQueryService', autospec=True)
    @patch('waves_litecoin_gateway.lib.LitecoinTransactionService', autospec=True)
    @patch('waves_litecoin_gateway.lib.LitecoinIntegerConverterService', autospec=True)
    @patch('pymongo.MongoClient', autospec=True)
    @patch('bitcoinrpc.authproxy.AuthServiceProxy', autospec=True)
    @patch('waves_gateway.ConstantFeeServiceImpl', autospec=True)
    @patch('waves_gateway.IntegerConverterService', autospec=True)
    @patch('waves_litecoin_gateway.lib.LitecoinAddressValidationService', autospec=True)
    @patch('waves_gateway.ProxyGuard', autospec=True)
    def test_from_config_file(self, mock_proxy_guard: MagicMock, mock_ltc_address_validation_service: MagicMock,
                              mock_integer_converter_service, mock_constant_fee_service: MagicMock,
                              mock_auth_service_proxy: MagicMock, mock_mongo_client: MagicMock,
                              mock_ltc_integer_converter_service: MagicMock, mock_ltc_transaction_service: MagicMock,
                              mock_ltc_chain_query_service: MagicMock, mock_ltc_address_factory: MagicMock,
                              mock_gateway: MagicMock):

        mock_proxy_guard_instance = MagicMock()
        mock_proxy_guard.return_value = mock_proxy_guard_instance

        mock_ltc_proxy_instance = MagicMock()
        mock_auth_service_proxy.return_value = mock_ltc_proxy_instance

        mock_ltc_address_factory_instance = MagicMock()
        mock_ltc_address_factory.return_value = mock_ltc_address_factory_instance

        mock_ltc_chain_query_service_instance = MagicMock()
        mock_ltc_chain_query_service.return_value = mock_ltc_chain_query_service_instance

        mock_ltc_transaction_service_instance = MagicMock()
        mock_ltc_transaction_service.return_value = mock_ltc_transaction_service_instance

        mock_ltc_integer_converter_service_instance = MagicMock()
        mock_ltc_integer_converter_service.return_value = mock_ltc_integer_converter_service_instance

        mock_integer_converter_service_instance = MagicMock()
        mock_integer_converter_service.return_value = mock_integer_converter_service_instance

        mock_gateway_instance = MagicMock()
        mock_gateway.return_value = mock_gateway_instance

        mock_constant_fee_service_instance = MagicMock()
        mock_constant_fee_service.return_value = mock_constant_fee_service_instance

        mock_mongo_client_instance = MagicMock()
        mock_mongo_client.return_value = mock_mongo_client_instance
        mock_mongo_database_instance = MagicMock()
        mock_mongo_client_instance.get_database.return_value = mock_mongo_database_instance

        mock_ltc_address_validation_service_instance = MagicMock()
        mock_ltc_address_validation_service.return_value = mock_ltc_address_validation_service_instance

        ltc_gateway = LitecoinGateway.from_config_file(self._config_file)
        ltc_gateway.run()

        self.assertEqual(mock_gateway_instance.run.call_count, 1)
        self.assertEqual(mock_gateway.call_count, 1)
        mock_auth_service_proxy.assert_called_once_with("http://bla:test@345.234.23.234:20000")
        mock_ltc_address_factory.assert_called_once_with(mock_proxy_guard_instance)
        mock_ltc_chain_query_service.assert_called_once_with(mock_proxy_guard_instance)
        mock_ltc_transaction_service.assert_called_once_with(mock_proxy_guard_instance,
                                                             mock_ltc_chain_query_service_instance)
        mock_ltc_integer_converter_service.assert_called_once_with(LitecoinGateway.DEFAULT_LTC_FACTOR,
                                                                   LitecoinGateway.DEFAULT_LTC_ROUND_PRECISION)
        mock_mongo_client.assert_called_once_with(host="localhost", port=27017)
        mock_constant_fee_service.assert_called_once_with(Decimal("0.01000000"), Decimal("0.02000000"))
        mock_proxy_guard.assert_called_once_with(mock_ltc_proxy_instance, max_parallel_access=1)
        mock_gateway.assert_called_once_with(
            coin_address_factory=mock_ltc_address_factory_instance,
            coin_chain_query_service=mock_ltc_chain_query_service_instance,
            coin_transaction_service=mock_ltc_transaction_service_instance,
            gateway_waves_address_secret=self._gateway_waves_address,
            gateway_coin_address_secret=self._gateway_ltc_address,
            mongo_database=mock_mongo_database_instance,
            managed_loggers=["BitcoinRPC"],
            logging_handlers=[],
            custom_currency_name=LitecoinGateway.WEB_CURRENCY_NAME,
            coin_integer_converter_service=mock_ltc_integer_converter_service_instance,
            asset_integer_converter_service=mock_integer_converter_service_instance,
            waves_chain=LitecoinGateway.DEFAULT_WAVES_CHAIN,
            waves_asset_id=LitecoinGateway.WAVES_ASSET_ID,
            waves_node=self._waves_node,
            host=LitecoinGateway.DEFAULT_HOST,
            port=LitecoinGateway.DEFAULT_PORT,
            gateway_owner_address=self._gateway_owner_address,
            fee_service=mock_constant_fee_service_instance,
            only_one_transaction_receiver=False,
            coin_transaction_web_link=LitecoinGateway.DEFAULT_TRANSACTION_WEB_LINK,
            coin_address_validation_service=mock_ltc_address_validation_service_instance,
            coin_address_web_link=LitecoinGateway.DEFAULT_ADDRESS_WEB_LINK,
            coin_last_block_distance=5)
