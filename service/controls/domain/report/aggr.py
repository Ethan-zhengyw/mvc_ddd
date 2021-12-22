# -*- coding: utf-8 -*-

from typing import List, Optional
from .entity import Report, ReportBill, BillPeriod
import common.static as const
from .repo import repo


class ReportAggr:
    def __init__(self, report: Report):
        self.__report = report

    @property
    def bill_period(self) -> BillPeriod:
        return self.__report.bill_period

    @property
    def report_bills(self) -> List[ReportBill]:
        return self.__report.bill_period.ledger_bills

    @property
    def state(self) -> const.ReportStateTYPE:
        return self.__report.state

    @property
    def is_generated(self):
        return self.__report.is_generated

    @classmethod
    def get_by_bill_period_id(cls, bill_period_id: int) -> Optional["ReportAggr"]:
        report = repo.get_report_by_bill_period_id(bill_period_id)
        if report:
            return cls(report)
        else:
            return None

    def get_report_bills_by_business_modelx_codes(self, business_modelx_codes: List[Optional[str]]) -> List[ReportBill]:
        return [report_bill for report_bill in self.report_bills if report_bill.business_modelx_code in business_modelx_codes]
