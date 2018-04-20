import unittest
from decimal import Decimal
from typing import cast
from unittest.mock import MagicMock, patch

from bitcoinrpc.authproxy import AuthServiceProxy
from waves_gateway import TransactionAttempt, TransactionAttemptReceiver

from waves_litecoin_gateway import LitecoinTransactionService, LitecoinChainQueryService


class LitecoinTransactionServiceSpec(unittest.TestCase):
    def setUp(self):
        self._ltc_proxy = MagicMock()
        self._ltc_factor = MagicMock()
        self._ltc_chain_query_service = MagicMock()
        self._transaction_service = LitecoinTransactionService(
            ltc_proxy=cast(AuthServiceProxy, self._ltc_proxy),
            ltc_chain_query_service=cast(LitecoinChainQueryService, self._ltc_chain_query_service), min_optimized_amount=Decimal(0.0000001))

    def test_fast_optimize_unspents_no_result(self):
        unspents = list()
        unspents.append({'amount': Decimal("0.4")})
        unspents.append({'amount': Decimal("0.1")})

        res = self._transaction_service._fast_optimize_unspents(unspents, Decimal("0.6"))

        self.assertIsNone(res)

    def test_fast_optimize_unspents_empty_unspents(self):
        unspents = list()

        res = self._transaction_service._fast_optimize_unspents(unspents, Decimal("0.6"))

        self.assertIsNone(res)

    def test_fast_optimize_unspents_exact_match(self):
        unspents = list()

        unspents.append({'amount': Decimal("0.4")})
        unspents.append({'amount': Decimal("0.2")})
        unspents.append({'amount': Decimal("0.6")})

        res = self._transaction_service._fast_optimize_unspents(unspents, Decimal("0.6"))

        self.assertEqual(res, [unspents[2]])

    def test_fast_optimize_unspents_needs_all(self):
        unspents = list()

        unspents.append({'amount': Decimal("0.4")})
        unspents.append({'amount': Decimal("0.2")})
        unspents.append({'amount': Decimal("0.6")})

        res = self._transaction_service._fast_optimize_unspents(unspents, Decimal("1.2"))

        self.assertTrue(unspents[0] in res)
        self.assertTrue(unspents[1] in res)
        self.assertTrue(unspents[2] in res)
        self.assertTrue(len(unspents), 3)

    def test_fast_optimize_unspents_needs_all_little_higher_than_dst(self):
        unspents = list()

        unspents.append({'amount': Decimal("0.4")})
        unspents.append({'amount': Decimal("0.2")})
        unspents.append({'amount': Decimal("0.7")})

        res = self._transaction_service._fast_optimize_unspents(unspents, Decimal("1.2"))

        self.assertTrue(unspents[0] in res)
        self.assertTrue(unspents[1] in res)
        self.assertTrue(unspents[2] in res)
        self.assertTrue(len(unspents), 3)

    def test_send_coin(self):
        mock_unspents = [{'amount': Decimal("2")}, {'amount': Decimal("3")}]
        mock_attempt = TransactionAttempt(
            currency="coin",
            fee=Decimal("0.02"),
            receivers=[
                TransactionAttemptReceiver(address="2195378", amount=Decimal("1")),
                TransactionAttemptReceiver(address="2396478", amount=Decimal("2"))
            ],
            sender="29873587235")
        mock_raw_transaction = MagicMock()
        mock_signed_raw_transaction = {"hex": MagicMock}
        mock_tx = "9716235875"
        mock_optimized_unspents = list(mock_unspents)
        mock_transaction = MagicMock()

        expected_outputs = {"2195378": Decimal("1"), "2396478": Decimal("2"), "29873587235": Decimal("1.98")}

        self._ltc_proxy.listunspent.return_value = mock_unspents
        self._ltc_proxy.createrawtransaction.return_value = mock_raw_transaction
        self._ltc_proxy.signrawtransaction.return_value = mock_signed_raw_transaction
        self._ltc_proxy.sendrawtransaction.return_value = mock_tx
        self._ltc_chain_query_service.get_transaction.return_value = mock_transaction

        with patch.object(self._transaction_service, '_fast_optimize_unspents'):
            self._transaction_service._fast_optimize_unspents.return_value = mock_optimized_unspents

            res = self._transaction_service.send_coin(mock_attempt, None)

            self._ltc_proxy.listunspent.assert_called_once_with(None, None, [mock_attempt.sender])
            self._ltc_proxy.createrawtransaction.assert_called_once_with(mock_optimized_unspents, expected_outputs)
            self._ltc_proxy.signrawtransaction.assert_called_once_with(mock_raw_transaction)
            self._ltc_proxy.sendrawtransaction.assert_called_once_with(mock_signed_raw_transaction['hex'])
            self.assertEqual(res, mock_transaction)
            self._ltc_chain_query_service.get_transaction.assert_called_once_with(mock_tx)
