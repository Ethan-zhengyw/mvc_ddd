# -*- coding: utf-8 -*-

import pytest
from .bill.aggr import BillPeriodAggr


class TestEvent:
    # @classmethod
    # def setup_class(cls):
    #     print('setting up TestEvent...')
    #     from service.controls.domain.event import EventManager
    #     EventManager.register_events()

    #     from common.util.event import event_manager
    #     from app import MyApp
    #     MyApp.thread_pool_submit(event_manager.start_listen_loop, db_commit=False)
    #     print('TestEvent set.')

    def test_on_bill_period_created(self, bill_period_aggr_factory, split_rule):
        aggr1: BillPeriodAggr = bill_period_aggr_factory(year=2021, month=11)
        aggr1.set_split_rules([split_rule])
        assert len(aggr1.split_rules) == 1

        aggr2: BillPeriodAggr = bill_period_aggr_factory(year=2021, month=12)
        assert len(aggr2.split_rules) == 1

    def test_on_original_bill_created(self, bill_period_aggr, original_bill):
        aggr: BillPeriodAggr = bill_period_aggr
        aggr.set_original_bills([original_bill])
        assert original_bill.exception is not None

    def test_on_ledger_bill_created(self, bill_period_aggr, ledger_bill):
        aggr: BillPeriodAggr = bill_period_aggr
        aggr.set_ledger_bills([ledger_bill])
        assert ledger_bill.exception is not None

    def test_on_original_bill_updated(self, bill_period_aggr, original_bill, business, provider, bill_subject):
        aggr: BillPeriodAggr = bill_period_aggr
        aggr.set_original_bills([original_bill])
        assert original_bill.exception is not None

        original_bill.business_modelx_code = None
        original_bill.bill_subject_name = 'b1'
        original_bill.provider_name = 'p1'
        aggr.update_original_bill(original_bill)
        assert original_bill.exception is None

    def test_on_ledger_bill_updated(self, bill_period_aggr, ledger_bill, business, provider, bill_subject):
        aggr: BillPeriodAggr = bill_period_aggr
        aggr.set_ledger_bills([ledger_bill])
        assert ledger_bill.exception is not None

        ledger_bill.business_modelx_code = 'b1_modelx_code'
        ledger_bill.bill_subject_name = 'b1'
        ledger_bill.provider = 'p1'
        aggr.update_ledger_bill(ledger_bill)
        assert ledger_bill.exception is None
