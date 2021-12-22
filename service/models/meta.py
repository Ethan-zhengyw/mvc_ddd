# -*- coding: utf-8 -*-

from sqlalchemy import func
from *****_service.model.fields import DB_INDEX_MAX_SIZE, JSONEncodedDict
from .base import db, ModelBase
import common.static as const


class Meta(ModelBase):
    __tablename__ = 'meta'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    create_time = db.Column(db.TIMESTAMP, index=True, server_default=func.now())
    update_time = db.Column(db.TIMESTAMP, index=True, server_default=func.now(), onupdate=func.now())

    type = db.Column(db.Integer, index=True, comment='元数据类型，0-业务；1-计费主体；2-供应商')

    name = db.Column(db.String(DB_INDEX_MAX_SIZE), index=True, default='', comment='名称')
    full_name = db.Column(db.String(DB_INDEX_MAX_SIZE), index=True, comment='全称')

    other = db.Column(JSONEncodedDict(4096), comment='其余配置')

    @property
    def modelx_id(self) -> str:
        """ 当元数据类型为业务时，可以访问该属性 """
        if self.type == const.META_TYPE_BUSINESS:
            return self.other.get('modelx_id', '')
        else:
            raise AttributeError(f'元数据(type={self.type})无modelx_id属性：{self.to_dict()}')

    @property
    def modelx_code(self) -> str:
        """ 当元数据类型为业务时，可以访问该属性 """
        if self.type == const.META_TYPE_BUSINESS:
            return self.other.get('modelx_code', '')
        else:
            raise AttributeError(f'元数据(type={self.type})无modelx_code属性：{self.to_dict()}')
