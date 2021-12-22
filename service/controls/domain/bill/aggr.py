# -*- coding: utf-8 -*-

import datetime
from typing import List, Optional

from werkzeug.exceptions import Conflict

from common.util.log import get_logger
from .iface import IBillPeriodAggr
from .entity import BillPeriod, OriginalBill, LedgerBill, SplitRule
from .event import \
    BillPeriodDeleted, BillPeriodCreated, \
    OriginalBillCreated, LedgerBillCreated, \
    BillPeriodOriginBillsReady, \
    OriginalBillUpdated, LedgerBillUpdated, \
    SplitRuleCreated, SplitRuleUpdated
from .repo import repo
from ..event import EventManager

logger = get_logger('domain:BillPeriodAggr')


class BillPeriodAggr(IBillPeriodAggr):
    def __init__(self, bill_period: BillPeriod):
        self.__bill_period: BillPeriod = bill_period

    @property
    def is_locked(self):
        return self.bill_period.is_locked

    @property
    def bill_period(self) -> BillPeriod:
        return self.__bill_period

    @property
    def original_bills(self) -> List[OriginalBill]:
        return self.bill_period.original_bills

    @property
    def ledger_bills(self) -> List[LedgerBill]:
        return self.bill_period.ledger_bills

    @property
    def split_rules(self) -> List[SplitRule]:
        return self.bill_period.split_rules

    @property
    def previous(self) -> Optional["BillPeriodAggr"]:
        previous_bill_period = repo.get_previous(self.bill_period)
        if previous_bill_period:
            return BillPeriodAggr(previous_bill_period)
        else:
            return None

    @classmethod
    def get_by_id(cls, bill_period_id: int) -> Optional["BillPeriodAggr"]:
        bill_period = BillPeriod.query.filter_by(id=bill_period_id).first()
        if not bill_period:
            return None
        else:
            return cls(bill_period)

    @classmethod
    def get_by_id_or_raise_404(cls, bill_period_id: int) -> "BillPeriodAggr":
        aggr = cls.get_by_id(bill_period_id)
        if aggr:
            return aggr
        else:
            BillPeriod.raise_not_found(id=bill_period_id)

    @classmethod
    def create(cls, year: int, month: int) -> "BillPeriodAggr":
        cls.__raise_403_if_exist(year, month)

        dt = datetime.datetime(year=year, month=month, day=1)
        bill_period = BillPeriod.create(year=year, month=month, timestamp=dt)
        aggr = cls(bill_period)
        aggr.__notify_created()
        return aggr

    def patch(self, year: int, month: int, is_locked: bool):
        self.__raise_403_if_exist_and_not_same(year, month, self.bill_period.id)

        dt = datetime.datetime(year=year, month=month, day=1)
        self.bill_period.year = year
        self.bill_period.month = month
        self.bill_period.timestamp = dt
        self.bill_period.is_locked = is_locked

    def delete(self):
        self.bill_period.delete()
        # self.__notify_deleted()

    def lock(self):
        self.bill_period.is_locked = True

    def unlock(self):
        self.bill_period.is_locked = False

    def create_original_bill(self, original_bill: OriginalBill):
        """  创建原始账单 """
        self.bill_period.bills.append(original_bill)
        self.__notify_original_bill_created(original_bill.id)

    def update_original_bill(self, original_bill: OriginalBill):
        """ 更新原始账单 """
        new = original_bill
        current = self.bill_period.bills.filter_by(id=new.id).first()
        if not current:
            OriginalBill.raise_not_found(id=new.id)
        else:
            self.bill_period.bills.remove(current)
            self.bill_period.bills.append(new)
            self.__notify_original_bill_updated(new.id)

    def create_ledger_bill(self, ledger_bill: LedgerBill):
        """ 创建总账账单 """

        # 潜在风险：不清楚为何需要执行以下两行代码才可修复总账账单分账的测试用例
        # 单独执行其中一行代码则会出现异常
        ledger_bill.bill_period_id = self.bill_period.id
        self.bill_period.bills.append(ledger_bill)

        self.__notify_ledger_bill_created(ledger_bill.id)

    def update_ledger_bill(self, ledger_bill: LedgerBill):
        """ 更新总账账单 """
        new = ledger_bill
        current = self.bill_period.bills.filter_by(id=new.id).first()
        if not current:
            LedgerBill.raise_not_found(id=new.id)
        else:
            self.bill_period.bills.remove(current)
            self.bill_period.bills.append(new)
            self.__notify_ledger_bill_updated(new.id)

    def create_split_rule(self, split_rule: SplitRule):
        self.bill_period.split_rules.append(split_rule)
        self.__notify_split_rule_created(split_rule.id)

    def update_split_rule(self, split_rule: SplitRule):
        """ 更新分账规则 """
        new = split_rule
        current = None
        for item in self.bill_period.split_rules:
            if item.id == new.id:
                current = item

        if not current:
            SplitRule.raise_not_found(id=new.id)

        else:
            self.__notify_split_rule_updated(new.id)

    def set_original_bills(self, original_bills: List[OriginalBill]):
        """ 设置计费周期的原始账单

        计费周期内还未有原始账单时，直接设置即可；若计费周期内已有原始账单，则清空原有原始账单，再设置

        """
        if len(self.original_bills) > 0:
            self.__clean_original_bills()

        for original_bill in original_bills:
            self.create_original_bill(original_bill)

    def set_ledger_bills(self, ledger_bills: List[LedgerBill]):
        if len(self.ledger_bills) > 0:
            self.__clean_ledger_bills()
        self.__create_ledger_bills(ledger_bills)

    def set_split_rules(self, split_rules: List[SplitRule]):
        if len(self.split_rules) > 0:
            self.__clean_split_rules()

        for split_rule in split_rules:
            self.create_split_rule(split_rule)

    def notify_original_bills_ready(self):
        e = BillPeriodOriginBillsReady(self.bill_period.id)
        EventManager.emit(e)

    def __clean_original_bills(self):
        for original_bill in self.original_bills:
            self.bill_period.bills.remove(original_bill)

    def __clean_split_rules(self):
        for split_rule in self.split_rules:
            self.bill_period.split_rules.remove(split_rule)

    def __notify_created(self):
        e = BillPeriodCreated(self.bill_period.id)
        EventManager.emit(e)

    def __notify_deleted(self):
        # 使用级联删除
        # 事件依然发出去，但是，不再需要在事件处理函数里删除分账规则
        # 不只是分账规则，此外，依赖计费周期存在的原始账单和总账账单也需要一同删除
        # 删除，使用标记法，而不真的将这条记录真的从数据库里删除
        #
        # 依然在事件处理函数中编写清除代码，这样可以让业务逻辑更清晰
        #     代码上将分账规则、原始账单、总账账单设置为空列表即可
        #     虽然代码是这么写，但是请知道在底层数据库、orm框架其实已经帮我们做了级联删除
        e = BillPeriodDeleted(self.bill_period.id)
        EventManager.emit(e)

    @staticmethod
    def __notify_original_bill_created(original_bill_id: int):
        e = OriginalBillCreated(original_bill_id)
        EventManager.emit(e)

    @staticmethod
    def __notify_ledger_bill_created(ledger_bill_id: int):
        e = LedgerBillCreated(ledger_bill_id)
        EventManager.emit(e)

    @staticmethod
    def __notify_split_rule_created(split_rule_id: int):
        e = SplitRuleCreated(split_rule_id)
        EventManager.emit(e)

    @staticmethod
    def __notify_original_bill_updated(original_bill_id: int):
        e = OriginalBillUpdated(original_bill_id)
        EventManager.emit(e)

    @staticmethod
    def __notify_ledger_bill_updated(ledger_bill_id: int):
        e = LedgerBillUpdated(ledger_bill_id)
        EventManager.emit(e)

    @staticmethod
    def __notify_split_rule_updated(split_rule_id: int):
        e = SplitRuleUpdated(split_rule_id)
        EventManager.emit(e)

    @staticmethod
    def __raise_403_if_exist(year: int, month: int):
        bill_period: BillPeriod = BillPeriod.query.filter_by(year=year, month=month).first()
        if bill_period:
            raise Conflict(f'计费周期({bill_period.pretty_str})已存在。')

    @staticmethod
    def __raise_403_if_exist_and_not_same(year: int, month: int, bill_period_id: int):
        bill_period: BillPeriod = BillPeriod.query.filter_by(year=year, month=month).first()
        if bill_period and bill_period.id != bill_period_id:
            raise Conflict(f'计费周期({bill_period.pretty_str})已存在。')

    def __clean_ledger_bills(self):
        for ledger_bill in self.bill_period.ledger_bills:
            self.__remove_ledger_bill(ledger_bill)

    def __create_ledger_bills(self, ledger_bills: List[LedgerBill]):
        for ledger_bill in ledger_bills:
            self.__create_ledger_bill(ledger_bill)

    def __create_ledger_bill(self, ledger_bill: LedgerBill):
        self.create_ledger_bill(ledger_bill)

    def __remove_ledger_bill(self, ledger_bill: LedgerBill):
        self.bill_period.bills.remove(ledger_bill)
