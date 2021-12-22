# -*- coding: utf-8 -*-

from typing import List

from *****_service.model.fields import JSONEncodedDict, DB_INDEX_MAX_SIZE
from sqlalchemy import func

import common.static as const
from .base import db, ModelBase


class User(ModelBase):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    create_time = db.Column(db.TIMESTAMP, index=True, server_default=func.now())
    update_time = db.Column(db.TIMESTAMP, index=True, server_default=func.now(), onupdate=func.now())

    email = db.Column(db.String(DB_INDEX_MAX_SIZE), index=True, comment='用户邮箱')

    is_admin = db.Column(db.Boolean, default=False, comment='是否管理员')
    role = db.Column(db.String(50), index=True, comment='角色，BUSINESS-业务方、COMMERCIAL-商务、FINANCIAL-财务')
    business_ids = db.Column(JSONEncodedDict(4096), comment='业务ID列表')

    @property
    def is_commercial(self):
        return self.role == const.USER_ROLE_COMMERCIAL

    @property
    def is_financial(self):
        return self.role == const.USER_ROLE_FINANCIAL

    @property
    def is_business(self):
        return self.role == const.USER_ROLE_BUSINESS

    def has_permission_of_all_given_business_ids(self, business_ids: List[int]) -> bool:
        return set(business_ids).issubset(set(self.business_ids))
