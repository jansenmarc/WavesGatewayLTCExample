import unittest
from decimal import Decimal
from unittest.mock import MagicMock, patch

from waves_litecoin_gateway.lib import LitecoinIntegerConverterService


class LitecoinIntegerConverterServiceTest(unittest.TestCase):
    def setUp(self):
        self._ltc_factor = pow(10, 2)
        self._ltc_round_precision = 2
        self._integer_converter_service = LitecoinIntegerConverterService(
            ltc_factor=self._ltc_factor, ltc_round_precision=self._ltc_round_precision)

    @patch('waves_gateway.convert_to_int', autospec=True)
    def test_convert_amount_to_int(self, mock_convert_to_int: MagicMock):
        mock_result = 23
        mock_arg = Decimal("0.23")
        mock_convert_to_int.return_value = mock_result
        actual_result = self._integer_converter_service.convert_amount_to_int(mock_arg)
        self.assertEqual(actual_result, mock_result)
        mock_convert_to_int.assert_called_once_with(mock_arg, self._ltc_factor)

    @patch('waves_gateway.convert_to_decimal')
    def test_revert_amount_conversion(self, mock_convert_to_decimal: MagicMock):
        mock_arg = 23
        mock_result = Decimal("0.23")
        mock_convert_to_decimal.return_value = mock_result
        actual_result = self._integer_converter_service.revert_amount_conversion(mock_arg)
        self.assertEqual(actual_result, mock_result)
        mock_convert_to_decimal.assert_called_once_with(mock_arg, self._ltc_factor, self._ltc_round_precision)
