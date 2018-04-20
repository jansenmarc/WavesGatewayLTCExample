"""
LitecoinIntegerConverterService
"""

from numbers import Number

import waves_gateway as gw
from decimal import Decimal
from .token import LTC_FACTOR, LTC_ROUND_PRECISION


@gw.Injectable(provides=gw.COIN_INTEGER_CONVERTER_SERVICE, deps=[LTC_FACTOR, LTC_ROUND_PRECISION])
class LitecoinIntegerConverterService(gw.IntegerConverterService):
    """
    Implementation of an IntegerConverterService.
    Converts the Decimal values provided by the bitcoinrpc package into integers that can be processed
    by the Gateway.
    """

    def __init__(self, ltc_factor: int, ltc_round_precision: int) -> None:
        self._ltc_factor = ltc_factor
        self._ltc_round_precision = ltc_round_precision

    def convert_amount_to_int(self, amount: Decimal) -> int:
        return gw.convert_to_int(amount, self._ltc_factor)

    def revert_amount_conversion(self, amount: int) -> Number:
        return gw.convert_to_decimal(amount, self._ltc_factor, self._ltc_round_precision)
