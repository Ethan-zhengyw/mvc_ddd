# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from typing import List, Optional

from .entity import BillPeriod, OriginalBill, LedgerBill, SplitRule


class IBillPeriodAggr(metaclass=ABCMeta):
    @property
    @abstractmethod
    def is_locked(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def bill_period(self) -> BillPeriod:
        raise NotImplementedError

    @property
    @abstractmethod
    def original_bills(self) -> List[OriginalBill]:
        raise NotImplementedError

    @property
    @abstractmethod
    def ledger_bills(self) -> List[LedgerBill]:
        raise NotImplementedError

    @property
    @abstractmethod
    def split_rules(self) -> List[SplitRule]:
        raise NotImplementedError

    @property
    @abstractmethod
    def previous(self) -> Optional["IBillPeriodAggr"]:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get_by_id(cls, bill_period_id: int) -> Optional["IBillPeriodAggr"]:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get_by_id_or_raise_404(cls, bill_period_id: int) -> "IBillPeriodAggr":
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def create(cls, year: int, month: int) -> "IBillPeriodAggr":
        raise NotImplementedError

    @abstractmethod
    def delete(self):
        raise NotImplementedError

    @abstractmethod
    def lock(self):
        raise NotImplementedError

    @abstractmethod
    def unlock(self):
        raise NotImplementedError

    @abstractmethod
    def create_original_bill(self, original_bill: OriginalBill):
        """  创建原始账单 """
        raise NotImplementedError

    @abstractmethod
    def update_original_bill(self, original_bill: OriginalBill):
        """ 更新原始账单 """
        raise NotImplementedError

    @abstractmethod
    def create_ledger_bill(self, ledger_bill: LedgerBill):
        """ 创建总账账单 """
        raise NotImplementedError

    @abstractmethod
    def update_ledger_bill(self, ledger_bill: LedgerBill):
        """ 更新总账账单 """
        raise NotImplementedError

    @abstractmethod
    def create_split_rule(self, split_rule: SplitRule):
        raise NotImplementedError

    @abstractmethod
    def set_original_bills(self, original_bills: List[OriginalBill]):
        """ 设置计费周期的原始账单

        计费周期内还未有原始账单时，直接设置即可；若计费周期内已有原始账单，则清空原有原始账单，再设置

        """
        raise NotImplementedError

    @abstractmethod
    def set_ledger_bills(self, ledger_bills: List[LedgerBill]):
        raise NotImplementedError

    @abstractmethod
    def set_split_rules(self, split_rules: List[SplitRule]):
        raise NotImplementedError

    @abstractmethod
    def notify_original_bills_ready(self):
        raise NotImplementedError
