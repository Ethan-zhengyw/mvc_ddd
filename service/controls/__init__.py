# -*- coding: utf-8 -*-

from *****_service.web.controls import ModelCtlMixin
from .apps import *


class ModelCtlBase(ModelCtlMixin):
    def patch(self, **kwargs):
        kwargs.pop('create_time', None)
        kwargs.pop('update_time', None)
        return self.model.patch(**kwargs)


class MetaCtl(BusinessApp, ModelCtlBase):
    model_cls = Meta

    @classmethod
    def sync_businesses(cls):
        BusinessApp.sync()


class UserCtl(UserApp, ModelCtlBase):
    model_cls = User


class BillPeriodCtl(BillPeriodApp, ModelCtlBase):
    model_cls = BillPeriod


class SplitRuleCtl(ModelCtlBase):
    model_cls = SplitRule

    @classmethod
    def create(cls, **kwargs):
        bill_period_id = kwargs.pop('bill_period_id')

        aggr = BillPeriodAggr.get_by_id_or_raise_404(bill_period_id)
        split_rule_ = SplitRule.create(**kwargs)

        aggr.create_split_rule(split_rule_)

        return cls(split_rule_)

    def patch(self, **kwargs):
        bill_period_id = self.model.bill_period_id

        aggr = BillPeriodAggr.get_by_id_or_raise_404(bill_period_id)
        super(SplitRuleCtl, self).patch(**kwargs)

        aggr.update_split_rule(self.model)

        return self


class OriginalBillCtl(OriginalBillApp, ModelCtlBase):
    model_cls = OriginalBill

    @classmethod
    def create(cls, **kwargs):
        bill_period_id = kwargs.pop('bill_period_id')
        kwargs['type'] = const.BILL_TYPE_ORIGINAL

        aggr = BillPeriodAggr.get_by_id_or_raise_404(bill_period_id)
        original_bill = OriginalBill.create(**kwargs)
        aggr.create_original_bill(original_bill)

        return cls(original_bill)

    def patch(self, **kwargs):
        bill_period_id = self.model.bill_period_id
        kwargs['type'] = const.BILL_TYPE_ORIGINAL

        aggr = BillPeriodAggr.get_by_id_or_raise_404(bill_period_id)
        super(OriginalBillCtl, self).patch(**kwargs)
        aggr.update_original_bill(self.model)

        return self


class LedgerBillCtl(LedgerBillApp, ModelCtlBase):
    model_cls = LedgerBill

    @classmethod
    def create(cls, **kwargs):
        bill_period_id = kwargs.pop('bill_period_id')
        kwargs['type'] = const.BILL_TYPE_LEDGER

        aggr = BillPeriodAggr.get_by_id_or_raise_404(bill_period_id)
        ledger_bill = LedgerBill.create(**kwargs)
        aggr.create_ledger_bill(ledger_bill)

        return cls(ledger_bill)

    def patch(self, **kwargs):
        bill_period_id = self.model.bill_period_id
        kwargs['type'] = const.BILL_TYPE_LEDGER

        aggr = BillPeriodAggr.get_by_id_or_raise_404(bill_period_id)
        super(LedgerBillCtl, self).patch(**kwargs)
        aggr.update_ledger_bill(self.model)

        return self
