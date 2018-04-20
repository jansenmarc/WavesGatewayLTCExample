"""
Litecoin Gateway
"""
from decimal import Decimal
from waves_gateway import run, define, ProxyGuard, COIN_NODE, Factory, LOG_FILE_NAME
from waves_litecoin_gateway import *
import bitcoinrpc.authproxy as authproxy


@Factory(provides=AUTH_PROXY, deps=[COIN_NODE])
def auth_proxy_factory(coin_node):
    return ProxyGuard(authproxy.AuthServiceProxy(coin_node), max_parallel_access=1)


define(LTC_FACTOR, pow(10, 8))
define(LTC_ROUND_PRECISION, 8)
define(MIN_OPTIMIZED_AMOUNT, Decimal(0.0000001))
define(LOG_FILE_NAME, "ltc-gateway.log")

run()
