# -*- coding: utf-8 -*-

from typing import List, Optional, Type
from abc import ABCMeta, abstractmethod

from sqlalchemy import desc

from .entity import Report, BillPeriod


class IReportRepo(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def get_reports(cls) -> List[Report]:
        """ 获取报表列表

        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get_report_by_bill_period_id(cls, bill_period_id: int) -> Optional[Report]:
        """ 获取指定计费周期的报表

        当且仅当计费周期处于锁定状态时，能够获取到报表，否则返回None

        """
        raise NotImplementedError


class ReportRepo(IReportRepo):
    @classmethod
    def get_reports(cls) -> List[Report]:
        return [Report(bill_period) for bill_period in BillPeriod.query.order_by(desc(BillPeriod.timestamp))]

    @classmethod
    def get_report_by_bill_period_id(cls, bill_period_id: int) -> Optional[Report]:
        bill_period = BillPeriod.query.filter_by(id=bill_period_id).first()
        if bill_period:
            return Report(bill_period)
        else:
            return None


repo: Type[IReportRepo] = ReportRepo
