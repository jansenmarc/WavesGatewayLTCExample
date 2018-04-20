import unittest
from unittest.mock import MagicMock

from waves_gateway import Transaction, TransactionReceiver

from waves_litecoin_gateway import LitecoinChainQueryService


class LitecoinChainQueryServiceTest(unittest.TestCase):
    def setUp(self):
        self._ltc_proxy = MagicMock()
        self._ltc_factor = pow(10, 8)
        self._chain_query_service = LitecoinChainQueryService(self._ltc_proxy)

    def test_get_transactions_of_block_at_height(self):
        block = {
            'tx': [
                '345fe8a6c9cfc992f5fa8982ec39f0a4f64a2b99f88a00fdbe6556dd784bfa53',
                '9506013d4253a4678d662cf2dfb54403e49a9754e6ecb6cc1584dbe274755f29'
            ],
            'hash':
            '5e7875bdf45e3c0cfe54a1c467ffe06ea2998f489376e421eefbc123abc345f6'
        }

        raw_first_tx = MagicMock()
        raw_sec_tx = MagicMock()
        decoded_first_tx = {
            'vout': [{
                'scriptPubKey': {
                    'addresses': ['n4UtgQSUHQUTDgiDkEmgYJvFqNBrcmQYc2'],
                    'hex': '76a914fbe70b337c1d2c233b46575fbf75ae9bd10c889688ac',
                    'type': 'pubkeyhash',
                    'reqSigs': 1,
                    'asm': 'OP_DUP OP_HASH160 fbe70b337c1d2c233b46575fbf75ae9bd10c8896 OP_EQUALVERIFY OP_CHECKSIG'
                },
                'value': 50.00100000,
                'n': 0
            }],
            'size':
            161,
            'locktime':
            0,
            'txid':
            '345fe8a6c9cfc992f5fa8982ec39f0a4f64a2b99f88a00fdbe6556dd784bfa53',
            'version':
            1,
            'hash':
            '345fe8a6c9cfc992f5fa8982ec39f0a4f64a2b99f88a00fdbe6556dd784bfa53'
        }

        decoded_sec_tex = {
            'version':
            1,
            'locktime':
            0,
            'vout': [{
                'value': 2.24400000,
                'n': 0,
                'scriptPubKey': {
                    'addresses': ['QWShbV2woggL1X1DHSHc5Aamv7NsZKuKFn'],
                    'reqSigs': 1,
                    'type': 'scripthash',
                    'hex': 'a9146befba9c6c8f76638dc402a6c6d16ebcdf3e1dc387',
                    'asm': 'OP_HASH160 6befba9c6c8f76638dc402a6c6d16ebcdf3e1dc3 OP_EQUAL'
                }
            }, {
                'value': 0.00100000,
                'n': 1,
                'scriptPubKey': {
                    'addresses': ['QYe3T35wXfYTNqgYw6DmaLrQ9ARUUfLTX2'],
                    'reqSigs': 1,
                    'type': 'scripthash',
                    'hex': 'a91484052132913c64c7a52e5836d70201b419e042f087',
                    'asm': 'OP_HASH160 84052132913c64c7a52e5836d70201b419e042f0 OP_EQUAL'
                }
            }]
        }

        expected_first_transaction = Transaction(
            tx='345fe8a6c9cfc992f5fa8982ec39f0a4f64a2b99f88a00fdbe6556dd784bfa53',
            receivers=[TransactionReceiver('n4UtgQSUHQUTDgiDkEmgYJvFqNBrcmQYc2', 50.00100000)])

        expected_sec_transaction = Transaction(
            tx='9506013d4253a4678d662cf2dfb54403e49a9754e6ecb6cc1584dbe274755f29',
            receivers=[
                TransactionReceiver('QWShbV2woggL1X1DHSHc5Aamv7NsZKuKFn', 2.24400000),
                TransactionReceiver('QYe3T35wXfYTNqgYw6DmaLrQ9ARUUfLTX2', 0.00100000)
            ])

        height = MagicMock()

        self._ltc_proxy.getblockhash.return_value = block['hash']
        self._ltc_proxy.getblock.return_value = block

        def getrawtransaction(tx: str):
            if tx == block['tx'][0]:
                return raw_first_tx
            elif tx == block['tx'][1]:
                return raw_sec_tx
            else:
                raise KeyError('called with unknown tx')

        def decoderawtransaction(raw_tx: str):
            if raw_tx == raw_first_tx:
                return decoded_first_tx
            elif raw_tx == raw_sec_tx:
                return decoded_sec_tex
            else:
                raise KeyError('called with unknown tx')

        self._ltc_proxy.getrawtransaction.side_effect = getrawtransaction
        self._ltc_proxy.decoderawtransaction.side_effect = decoderawtransaction

        transactions = self._chain_query_service.get_transactions_of_block_at_height(height)

        self.assertEqual(transactions[0], expected_first_transaction)
        self.assertEqual(transactions[1], expected_sec_transaction)

        self._ltc_proxy.decoderawtransaction.assert_any_call(raw_first_tx)
        self._ltc_proxy.decoderawtransaction.assert_any_call(raw_sec_tx)
        self.assertEqual(2, self._ltc_proxy.decoderawtransaction.call_count)
        self._ltc_proxy.getrawtransaction.assert_any_call(block['tx'][0])
        self._ltc_proxy.getrawtransaction.assert_any_call(block['tx'][1])
        self.assertEqual(2, self._ltc_proxy.getrawtransaction.call_count)
        self._ltc_proxy.getblock.assert_called_once_with(block['hash'])
        self._ltc_proxy.getblockhash.assert_called_once_with(height)

    def test_get_amount_of_transaction(self):
        tx = MagicMock()
        expected_result = MagicMock()
        transaction = {'amount': MagicMock()}

        self._ltc_proxy.gettransaction.return_value = transaction

        self.assertEqual(self._chain_query_service.get_amount_of_transaction(tx), transaction['amount'])

        self._ltc_proxy.gettransaction.assert_called_once_with(tx)

    def test_get_height_of_highest_block(self):
        info = {'blocks': MagicMock()}
        self._ltc_proxy.getinfo.return_value = info
        self.assertEqual(self._chain_query_service.get_height_of_highest_block(), info['blocks'])
