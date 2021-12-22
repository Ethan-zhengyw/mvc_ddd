# -*- coding: utf-8 -*-
# TODO 待优化：
# 分账子领域内的计费周期聚合依赖了账单子领域的计费周期聚合
# 考虑通过事件机制移除依赖

from typing import List, Optional

from ..bill.aggr import BillPeriodAggr as AggrFromSubdomainOfBill
from .entity import *


class BillPeriodAggr:
    def __init__(self, aggr_from_subdomain_of_bill: AggrFromSubdomainOfBill):
        self.__aggr_from_subdomain_of_bill = aggr_from_subdomain_of_bill

    @property
    def bill_period(self) -> BillPeriod:
        return self.__aggr_from_subdomain_of_bill.bill_period

    @property
    def original_bills(self) -> List[OriginalBill]:
        return self.__aggr_from_subdomain_of_bill.original_bills

    @property
    def ledger_bills(self) -> List[LedgerBill]:
        return self.__aggr_from_subdomain_of_bill.ledger_bills

    @property
    def split_rules(self) -> List[SplitRule]:
        return self.__aggr_from_subdomain_of_bill.split_rules

    @classmethod
    def create(cls, year: int, month: int) -> "BillPeriodAggr":
        obj = AggrFromSubdomainOfBill.create(year, month)
        return cls(obj)

    @classmethod
    def get_by_id(cls, bill_period_id: int) -> Optional["BillPeriodAggr"]:
        aggr_from_subdomain_of_bill = AggrFromSubdomainOfBill.get_by_id_or_raise_404(bill_period_id)
        return cls(aggr_from_subdomain_of_bill)

    def delete(self):
        self.__aggr_from_subdomain_of_bill.delete()

    def set_ledger_bills(self, ledger_bills: List[LedgerBill]):
        self.__aggr_from_subdomain_of_bill.set_ledger_bills(ledger_bills)

    def split_ledger_bill(self, ledger_bill: LedgerBill, ledger_bills: List[LedgerBill]):
        """ 拆分总账账单

        :param ledger_bill: 待拆分的总账账单
        :param ledger_bills: 拆分得到的一条或多条总账账单
        """
        self.__remove_ledger_bill(ledger_bill)

        for item in ledger_bills:
            item.bill_period_id = ledger_bill.bill_period_id
            item.parent_id = ledger_bill.parent_id

        self.__create_ledger_bills(ledger_bills)

    def set_original_bills(self, original_bills: List[OriginalBill]):
        self.__aggr_from_subdomain_of_bill.set_original_bills(original_bills)

    def set_split_rules(self, split_rules: List[SplitRule]):
        self.__aggr_from_subdomain_of_bill.set_split_rules(split_rules)

    def __create_ledger_bills(self, ledger_bills: List[LedgerBill]):
        for ledger_bill in ledger_bills:
            self.__create_ledger_bill(ledger_bill)

    def __create_ledger_bill(self, ledger_bill: LedgerBill):
        self.__aggr_from_subdomain_of_bill.create_ledger_bill(ledger_bill)

    def __remove_ledger_bill(self, ledger_bill: LedgerBill):
        self.bill_period.bills.remove(ledger_bill)
