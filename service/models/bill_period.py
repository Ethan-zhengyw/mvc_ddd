# -*- coding: utf-8 -*-

from sqlalchemy import func
from sqlalchemy.orm import RelationshipProperty

import common.static as const
from .base import db, ModelBase


class BillPeriod(ModelBase):
    __tablename__ = 'bill_period'
    id = db.Column(db.Integer, primary_key=True)
    create_time = db.Column(db.TIMESTAMP, index=True, server_default=func.now())
    update_time = db.Column(db.TIMESTAMP, index=True, server_default=func.now(), onupdate=func.now())

    timestamp = db.Column(db.TIMESTAMP, index=True, comment='账期，精确到月')
    year = db.Column(db.Integer, index=True, comment='年份')
    month = db.Column(db.Integer, index=True, comment='月份')

    is_locked = db.Column(db.Boolean, default=False, comment='锁定状态')

    split_rules = db.relationship('SplitRule', lazy='select', cascade='all')
    bills: RelationshipProperty = db.relationship('Bill', lazy='dynamic', cascade='all')

    @property
    def original_bills(self):
        return self.bills.filter_by(type=const.BILL_TYPE_ORIGINAL).all()

    @property
    def ledger_bills(self):
        return self.bills.filter_by(type=const.BILL_TYPE_LEDGER).all()

    @property
    def pretty_str(self):
        """ 返回XXXX-XX形式的字符串表示 """
        return f'{self.year}-{self.month}'

    @property
    def abnormal_original_bill_cnt(self):
        return len([original_bill
                    for original_bill in self.original_bills
                    if original_bill.exception is not None])

    @property
    def abnormal_ledger_bill_cnt(self):
        return len([ledger_bill
                    for ledger_bill in self.ledger_bills
                    if ledger_bill.exception is not None])
