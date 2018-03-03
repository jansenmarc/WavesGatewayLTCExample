"""
LitecoinChainQueryService
"""

import waves_gateway as gw
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from typing import List, Optional
import gevent.pool as pool

from decimal import Decimal

from waves_gateway import Transaction

from .util import sum_unspents


class LitecoinChainQueryService(gw.ChainQueryService):
    """
    Implementation of an ChainQueryService on the Litecoin Blockchain.
    """

    def get_transaction_by_tx(self, tx: str) -> Optional[Transaction]:
        try:
            return self.get_transaction(tx)
        except JSONRPCException:
            raise gw.InvalidTransactionIdentifier()

    def __init__(self, ltc_proxy: AuthServiceProxy) -> None:
        self._ltc_proxy = ltc_proxy

    def _extract_receivers(self, transaction: dict) -> List[gw.TransactionReceiver]:
        """Extracts the receivers of an unparsed LTC transaction."""
        results = list()  # type: List[gw.TransactionReceiver]

        for vout in transaction['vout']:
            if 'addresses' not in vout['scriptPubKey']:
                continue

            for address in vout['scriptPubKey']['addresses']:
                ltc_transaction_receiver = gw.TransactionReceiver(address=address, amount=vout['value'])
                results.append(ltc_transaction_receiver)

        return results

    def _filter_sender_duplicates(self, senders: List[gw.TransactionSender]) -> List[gw.TransactionSender]:
        results = list()  # type: List[gw.TransactionSender]

        for sender in senders:
            if sender not in results:
                results.append(sender)

        return results

    def _resolve_senders(self, transaction: dict) -> List[gw.TransactionSender]:
        """Extracts the senders of an unparsed LTC transaction"""

        if 'vin' not in transaction:
            return list()

        results = list()  # type: List[gw.TransactionSender]

        for vin in transaction['vin']:

            if ('txid' not in vin) or ('vout' not in vin):
                continue

            vin_transaction_raw = self._ltc_proxy.getrawtransaction(vin['txid'])
            vin_transaction = self._ltc_proxy.decoderawtransaction(vin_transaction_raw)

            if 'addresses' not in vin_transaction['vout'][vin['vout']]['scriptPubKey']:
                continue

            for address in vin_transaction['vout'][vin['vout']]['scriptPubKey']['addresses']:
                ltc_transaction_sender = gw.TransactionSender(address=address)
                results.append(ltc_transaction_sender)

        return self._filter_sender_duplicates(results)

    def get_transaction(self, tx: str) -> gw.Transaction:
        raw_transaction = self._ltc_proxy.getrawtransaction(tx)
        transaction = self._ltc_proxy.decoderawtransaction(raw_transaction)

        transaction_receivers = self._extract_receivers(transaction)
        transaction_sender = self._resolve_senders(transaction)

        return gw.Transaction(tx, transaction_receivers, transaction_sender)

    def get_transactions_of_block_at_height(self, height: gw.CoinBlockHeight) -> List[gw.Transaction]:
        block_hash = self._ltc_proxy.getblockhash(height)
        block = self._ltc_proxy.getblock(block_hash)

        get_transaction_tasks = pool.Pool()  # litecoin server does not accept more than one parallel connection

        return [a for a in get_transaction_tasks.map(self.get_transaction, block['tx'])]

    def get_amount_of_transaction(self, transaction: str) -> Decimal:
        transaction = self._ltc_proxy.gettransaction(transaction)
        return transaction['amount']  # type: ignore

    def get_height_of_highest_block(self) -> gw.CoinBlockHeight:
        info = self._ltc_proxy.getinfo()
        return info['blocks']
