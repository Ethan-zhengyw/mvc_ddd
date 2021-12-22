# -*- coding: utf-8 -*-

import datetime
from dateutil.relativedelta import relativedelta
from abc import ABCMeta, abstractmethod
from typing import Optional, Type, List

from sqlalchemy import desc

from service.models import db_session
from .entity import BillPeriod

__all__ = [
    "db_session",
    "repo"
]


class IBillPeriodRepo(object, metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def get_previous(cls, bill_period: BillPeriod) -> Optional[BillPeriod]:
        """ 获取指定计费周期的前一个计费周期，按照时间戳排序，而非创建时间

        例如有以下三个计费周期（按创建时间顺序，从上往下，越下方的计费周期，创建时间越早）：

        2021-10
        2021-11
        2021-9
        2021-8

        获取2021-11计费周期的前一个计费周期，将得到2021-10

        """
        raise NotImplementedError


class BillPeriodRepo(IBillPeriodRepo):
    @classmethod
    def get_previous(cls, bill_period: BillPeriod) -> Optional[BillPeriod]:
        return BillPeriod.query.filter(BillPeriod.timestamp <= bill_period.timestamp) \
                               .filter(BillPeriod.id != bill_period.id) \
                               .order_by(desc(BillPeriod.timestamp)).first()


repo: Type[IBillPeriodRepo] = BillPeriodRepo
