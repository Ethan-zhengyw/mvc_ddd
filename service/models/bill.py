# -*- coding: utf-8 -*-

from sqlalchemy import ForeignKey, func
from *****_service.model.fields import DB_INDEX_MAX_SIZE
from .base import db, ModelBase


class Bill(ModelBase):
    __tablename__ = 'bill'
    id = db.Column(db.Integer, primary_key=True)
    create_time = db.Column(db.TIMESTAMP, index=True, server_default=func.now())
    update_time = db.Column(db.TIMESTAMP, index=True, server_default=func.now(), onupdate=func.now())

    bill_period_id = db.Column(db.Integer, ForeignKey('bill_period.id'), index=True, comment='账单所属计费周期ID')

    type = db.Column(db.Integer, index=True, comment='账单类型，0-原始账单；1-总账账单')

    parent_id = db.Column(db.Integer, index=True, nullable=True, comment='当账单类型为总账账单时，表示该总账账单归属的原始账单ID')

    contract_id = db.Column(db.String(DB_INDEX_MAX_SIZE), index=True, comment='合同编号')
    provider_name = db.Column(db.String(DB_INDEX_MAX_SIZE), index=True, comment='供应商名称')
    bill_subject_name = db.Column(db.String(DB_INDEX_MAX_SIZE), index=True, comment='计费主体名称')

    service_type = db.Column(db.String(DB_INDEX_MAX_SIZE), index=True, comment='服务类型')
    service_name = db.Column(db.String(DB_INDEX_MAX_SIZE), index=True, comment='服务名称')
    service_details = db.Column(db.String(250), comment='服务细项')

    unit_price = db.Column(db.Float, comment='单价')
    bill_unit = db.Column(db.String(250), comment='计费单位')
    statistic_cnt = db.Column(db.Float, comment='统计量')
    statistic_unit = db.Column(db.String(250), comment='统计单位')
    total = db.Column(db.Float, comment='总计')
    discount = db.Column(db.Float, comment='折扣')
    actually_paid = db.Column(db.DECIMAL(precision=11, scale=2), comment='实付金额')

    type_level_1 = db.Column(db.String(DB_INDEX_MAX_SIZE), index=True, comment='一级类型')
    business_modelx_code = db.Column(db.String(DB_INDEX_MAX_SIZE), index=True, comment='业务在ModelX的code')
    business_name = db.Column(db.String(DB_INDEX_MAX_SIZE), index=True, comment='业务名称')
    department_name = db.Column(db.String(DB_INDEX_MAX_SIZE), index=True, comment='部门名称')

    desc = db.Column(db.String(250), comment='备注')
    exception = db.Column(db.String(250), nullable=True, comment='异常信息')

    tag1 = db.Column(db.String(250), index=True, comment='标签一')
    tag2 = db.Column(db.String(250), index=True, comment='标签二')
    tag3 = db.Column(db.String(250), index=True, comment='标签三')
    tag4 = db.Column(db.String(250), index=True, comment='标签四')
    tag5 = db.Column(db.String(250), index=True, comment='标签五')

    def append_exception(self, msg: str):
        if self.exception is None:
            self.exception = ''
        self.exception = f'{self.exception}{msg}\n'

    @classmethod
    def filter_by_is_exception(cls, is_exception: str, query=None):
        query = query or cls.query
        if is_exception == 'true':
            query = query.filter(Bill.exception.isnot(None))
        return query
