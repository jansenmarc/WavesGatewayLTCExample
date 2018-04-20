"""
LitecoinTransactionService
"""

from decimal import Decimal
from functools import cmp_to_key
from typing import Optional, List

import gevent.lock as lock
import waves_gateway as gw
from bitcoinrpc.authproxy import AuthServiceProxy

from .token import AUTH_PROXY, MIN_OPTIMIZED_AMOUNT
from .litecoin_chain_query_service import LitecoinChainQueryService
from .util import sum_unspents


@gw.Injectable(
    provides=gw.COIN_TRANSACTION_SERVICE, deps=[AUTH_PROXY, gw.COIN_CHAIN_QUERY_SERVICE, MIN_OPTIMIZED_AMOUNT])
class LitecoinTransactionService(gw.TransactionService):
    """
    Implements the sending of an TransactionAttempt on the Litecoin Blockchain.
    """

    def __init__(self, ltc_proxy: AuthServiceProxy, ltc_chain_query_service: LitecoinChainQueryService,
                 min_optimized_amount: Decimal) -> None:
        self._ltc_proxy = ltc_proxy
        self._min_optimized_amount = min_optimized_amount
        self._ltc_chain_query_service = ltc_chain_query_service
        self._lock = lock.Semaphore()

    def _fast_optimize_unspents(self, unspents: List[dict], dst_amount: Decimal) -> Optional[List]:
        res = list()  # type: List[dict]
        unspents = list(unspents)

        if sum_unspents(unspents) < dst_amount:
            return None

        for i in range(0, len(unspents)):

            diff_dst_amount = dst_amount - sum_unspents(res)

            def comparator(value: dict, other: dict) -> int:
                """
                Compares two unspents by their absolute difference to
                the required amount.
                """
                distance_a = value['amount'] - diff_dst_amount
                distance_b = other['amount'] - diff_dst_amount

                if abs(distance_a) != abs(distance_b):
                    return abs(distance_a) - abs(distance_b)
                else:
                    return distance_a - distance_b

            sorted_unspents = sorted(unspents, key=cmp_to_key(comparator))

            best_fit = sorted_unspents[0]

            res.append(best_fit)
            unspents.remove(best_fit)

            if sum_unspents(res) >= dst_amount:
                return res

        return None

    def send_coin(self, attempt: gw.TransactionAttempt, secret: Optional[str] = None) -> gw.Transaction:

        unspents = self._ltc_proxy.listunspent(None, None, [attempt.sender])

        outputs = dict()

        overall_amount = Decimal(attempt.overall_amount())

        optimized_unspents = self._fast_optimize_unspents(unspents, overall_amount + Decimal(attempt.fee))

        if optimized_unspents is None:
            raise Exception('Not suitable combination of unspent outputs found')

        for receiver in attempt.receivers:
            outputs[receiver.address] = receiver.amount

        unspents_amount = sum_unspents(optimized_unspents)

        outputs[attempt.sender] = unspents_amount - attempt.fee - overall_amount

        self._lock.acquire()

        raw_transaction = self._ltc_proxy.createrawtransaction(optimized_unspents, outputs)
        signed_transaction = self._ltc_proxy.signrawtransaction(raw_transaction)
        tx = self._ltc_proxy.sendrawtransaction(signed_transaction['hex'])

        self._lock.release()

        return self._ltc_chain_query_service.get_transaction(tx)
