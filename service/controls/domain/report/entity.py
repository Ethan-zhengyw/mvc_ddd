# -*- coding: utf-8 -*-

import common.static as const
from service.models import ReportBill, BillPeriod

__all__ = [
    "Report",
    "ReportBill",
    "BillPeriod"
]


class Report:
    def __init__(self, bill_period: BillPeriod):
        self.__bill_period = bill_period

    @property
    def id(self):
        return self.__bill_period.id

    @property
    def bill_period_id(self) -> int:
        return self.__bill_period.id

    @property
    def bill_period(self) -> BillPeriod:
        return self.__bill_period

    @property
    def update_time(self):
        return self.__bill_period.update_time

    @property
    def state(self) -> const.ReportStateTYPE:
        num_of_ledger_bill = len(self.__bill_period.ledger_bills)
        if self.__bill_period.is_locked:
            if num_of_ledger_bill > 0:
                return const.REPORT_STATE_GENERATED
            else:
                return const.REPORT_STATE_NOT_GENE
        else:
            if num_of_ledger_bill > 0:
                return const.REPORT_STATE_UPDATING
            else:
                return const.REPORT_STATE_NOT_GENE

    @property
    def is_generated(self):
        return self.state == const.REPORT_STATE_GENERATED

    def to_dict(self) -> dict:
        return dict(
            id=self.id,
            bill_period_id=self.bill_period_id,
            update_time=self.update_time,
            state=self.state,
            bill_period=self.bill_period.pretty_str)
