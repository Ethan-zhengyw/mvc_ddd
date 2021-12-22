# -*- coding: utf-8 -*-
# TODO: 待优化
# 考虑优化事件与事件处理函数的注册机制，通过在事件处理函数上使用辅助订阅的装饰器进行装饰
# 考虑优化事件对象的生成机制，不需要让用户为每个事件定义一个类，可以在辅助订阅的装饰器中完成

from typing import Optional

from common.util.event import EventBase
from .entity import OriginalBill, LedgerBill, Bill, SplitRule
from .iface import IBillPeriodAggr


BillPeriodAggr: Optional[IBillPeriodAggr] = None


class EventBasedOnBillPeriod(EventBase):
    def __init__(self, bill_period_id: int):
        super().__init__()
        self.__bill_period_id = bill_period_id

    @property
    def aggr(self) -> IBillPeriodAggr:
        return BillPeriodAggr.get_by_id_or_raise_404(self.__bill_period_id)


class EventBasedOnBill(EventBasedOnBillPeriod):
    def __init__(self, bill_id: int):
        self.__bill_id = bill_id
        EventBasedOnBillPeriod.__init__(self, self.bill.bill_period_id)

    @property
    def bill(self) -> OriginalBill:
        return Bill.query.filter_by(id=self.__bill_id).first()


class BillPeriodCreated(EventBasedOnBillPeriod):
    name = 'bill_period_created'

    def __init__(self, bill_period_id: int):
        EventBasedOnBillPeriod.__init__(self, bill_period_id)


class BillPeriodDeleted(EventBasedOnBillPeriod):
    name = 'bill_period_deleted'

    def __init__(self, bill_period_id: int):
        EventBasedOnBillPeriod.__init__(self, bill_period_id)


class BillPeriodOriginBillsReady(EventBasedOnBillPeriod):
    name = 'bill_period_original_bills_ready'

    def __init__(self, bill_period_id: int):
        EventBasedOnBillPeriod.__init__(self, bill_period_id)


class OriginalBillCreated(EventBasedOnBill):
    name = 'original_bill_created'

    def __init__(self, original_bill_id: int):
        EventBasedOnBill.__init__(self, original_bill_id)

    @property
    def original_bill(self) -> OriginalBill:
        return self.bill


class LedgerBillCreated(EventBasedOnBill):
    name = 'ledger_bill_created'

    def __init__(self, ledger_bill_id: int):
        EventBasedOnBill.__init__(self, ledger_bill_id)

    @property
    def ledger_bill(self) -> LedgerBill:
        return self.bill


class OriginalBillUpdated(EventBasedOnBill):
    name = 'original_bill_updated'

    def __init__(self, original_bill_id: int):
        EventBasedOnBill.__init__(self, original_bill_id)

    @property
    def original_bill(self) -> OriginalBill:
        return self.bill


class LedgerBillUpdated(EventBasedOnBill):
    name = 'ledger_bill_updated'

    def __init__(self, ledger_bill_id: int):
        EventBasedOnBill.__init__(self, ledger_bill_id)

    @property
    def ledger_bill(self) -> LedgerBill:
        return self.bill


class EventBasedOnSplitRule(EventBasedOnBillPeriod):
    def __init__(self, split_rule_id: int):
        self.__split_rule_id = split_rule_id
        EventBasedOnBillPeriod.__init__(self, self.split_rule.bill_period_id)

    @property
    def raise_on_exception(self):
        return True

    @property
    def split_rule(self) -> SplitRule:
        return SplitRule.query.filter_by(id=self.__split_rule_id).first()


class SplitRuleCreated(EventBasedOnSplitRule):
    name = 'split_rule_created'

    def __init__(self, split_rule_id: int):
        EventBasedOnSplitRule.__init__(self, split_rule_id)


class SplitRuleUpdated(EventBasedOnSplitRule):
    name = 'split_rule_updated'

    def __init__(self, split_rule_id: int):
        EventBasedOnSplitRule.__init__(self, split_rule_id)
