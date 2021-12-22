# -*- coding: utf-8-

import pytest

import common.static as const
import common.util.decimal as decimal
from .aggr import BillPeriodAggr
from .service import BillPeriodSplitService, LedgerBillSplitService


@pytest.fixture
def original_bills(original_bill_factory):
    res = list()
    res.append(original_bill_factory(provider_name='p1', actually_paid=1000000))
    return res


@pytest.fixture
def split_rules(split_rule_factory, provider):
    res = list()
    res.append(
        split_rule_factory(
            bill_matchers=dict(provider_name='p1'),
            split_policy=dict(
                type=const.SPLIT_TYPE_COMP,
                configs=[
                    dict(
                        type=const.SPLIT_TYPE_FIXED,
                        configs=dict(
                            business='*****',
                            value=500000
                        )
                    ),
                    dict(
                        type=const.SPLIT_TYPE_PROP,
                        configs=dict(
                            business='********',
                            percent=0.2
                        )
                    ),
                    dict(
                        type=const.SPLIT_TYPE_PROP,
                        configs=dict(
                            business='payment',
                            percent=0.8
                        )
                    )
                ]
            )
        )
    )
    return res


@pytest.fixture
def bill_period_aggr_with_original_bills_and_split_rules(bill_period_aggr, original_bills, split_rules):
    aggr = bill_period_aggr
    aggr.set_original_bills(original_bills)
    aggr.set_split_rules(split_rules)
    return aggr


class TestBillPeriodSplitService:
    def test_split_original_bills_of_bill_period(self, bill_period_aggr_with_original_bills_and_split_rules):
        aggr = bill_period_aggr_with_original_bills_and_split_rules

        assert len(aggr.original_bills) == 1
        assert len(aggr.split_rules) == 1
        assert len(aggr.ledger_bills) == 0

        BillPeriodSplitService.split_original_bills_of_bill_period(aggr.bill_period.id)

        assert len(aggr.ledger_bills) == 3

        total = decimal.quantize(sum([ledger_bill.actually_paid for ledger_bill in aggr.ledger_bills]))
        assert total == aggr.original_bills[0].actually_paid


@pytest.fixture
def ledger_bill_on_bill_period(bill_period_aggr, ledger_bill):
    bill_period_aggr.create_ledger_bill(ledger_bill)
    return ledger_bill


class TestLedgerBillSplitService:
    def test_split_ledger_bill(self, ledger_bill_on_bill_period, ledger_bill_factory):
        ledger_bill = ledger_bill_on_bill_period

        aggr = BillPeriodAggr.get_by_id(ledger_bill.bill_period_id)

        assert len(aggr.ledger_bills) == 1

        ledger_bills = [
            ledger_bill_factory(actually_paid=500000.0),
            ledger_bill_factory(actually_paid=300000.0),
            ledger_bill_factory(actually_paid=200000.0),
        ]

        LedgerBillSplitService.split_ledger_bill(ledger_bill.id, ledger_bills)

        assert len(aggr.ledger_bills) == 3
        assert sum([ledger_bill.actually_paid for ledger_bill in ledger_bills]) == ledger_bill.actually_paid
