# -*- coding: utf-8 -*-

import pytest

from .bill import LedgerBillApp
from ..domain.bill.aggr import BillPeriodAggr


@pytest.fixture
def ledger_bill_on_bill_period(bill_period_aggr, ledger_bill):
    bill_period_aggr.create_ledger_bill(ledger_bill)
    return ledger_bill


class TestLedgerBillApp:
    def test_split(self, ledger_bill_on_bill_period, ledger_bill_factory):
        ledger_bill = ledger_bill_on_bill_period

        aggr = BillPeriodAggr.get_by_id_or_raise_404(ledger_bill.bill_period_id)

        assert len(aggr.ledger_bills) == 1

        ledger_bills = [
            ledger_bill_factory(actually_paid=500000.0),
            ledger_bill_factory(actually_paid=300000.0),
            ledger_bill_factory(actually_paid=200000.0),
        ]

        LedgerBillApp.split(ledger_bill.id, ledger_bills)

        assert len(aggr.ledger_bills) == 3
        assert sum([ledger_bill.actually_paid for ledger_bill in ledger_bills]) == ledger_bill.actually_paid
