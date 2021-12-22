# -*- coding: utf-8 -*-

from sqlalchemy import ForeignKey, func
from *****_service.model.fields import JSONEncodedDict
from .base import db, ModelBase


class SplitRule(ModelBase):
    __tablename__ = 'split_rule'
    id = db.Column(db.Integer, primary_key=True)
    create_time = db.Column(db.TIMESTAMP, index=True, server_default=func.now())
    update_time = db.Column(db.TIMESTAMP, index=True, server_default=func.now(), onupdate=func.now())

    bill_period_id = db.Column(db.Integer, ForeignKey('bill_period.id'), index=True, comment='所属计费周期ID')

    bill_matchers = db.Column(JSONEncodedDict(4096), comment='匹配规则')
    split_policy = db.Column(JSONEncodedDict(4096), comment='分摊策略')

    desc = db.Column(db.String(1024), comment='备注')
