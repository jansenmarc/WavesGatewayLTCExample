"""
Utility methods
"""

from decimal import Decimal
from typing import List


def sum_unspents(unspents: List[dict]) -> Decimal:
    """
    Accumulates the amounts of the given list of unspents.
    """
    amount = Decimal(0)

    for vout in unspents:
        amount = amount + vout['amount']

    return amount
