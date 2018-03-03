"""
LitecoinAddressValidationService
"""

import waves_gateway as wg
from bitcoinrpc.authproxy import AuthServiceProxy


class LitecoinAddressValidationService(wg.AddressValidationService):
    """
    Validates an Litecoin address by using an RPC service.
    """

    def __init__(self, ltc_proxy: AuthServiceProxy) -> None:
        self._ltc_proxy = ltc_proxy

    def validate_address(self, address: str) -> bool:
        validation_result = self._ltc_proxy.validateaddress(address)
        return validation_result['isvalid']
