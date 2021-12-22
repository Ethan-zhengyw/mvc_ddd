# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from typing import List, Type

from service.models import db_session
from .entity import *
import common.static as const
from common.util.log import get_logger


logger = get_logger('domain:meta:repo')


__all__ = [
    "db_session",
    "repo"
]


class IMetaRepo(object, metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def get_businesses(cls) -> List[Business]:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get_bill_subjects(cls) -> List[BillSubject]:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get_providers(cls) -> List[Provider]:
        raise NotImplementedError

    @classmethod
    def set_businesses(cls, businesses: List[Business]):
        raise NotImplementedError


class MetaRepo(IMetaRepo):
    @classmethod
    def get_businesses(cls) -> List[Business]:
        return Meta.query.filter_by(type=const.META_TYPE_BUSINESS).all()

    @classmethod
    def get_bill_subjects(cls) -> List[BillSubject]:
        return Meta.query.filter_by(type=const.META_TYPE_BILL_SUBJECT).all()

    @classmethod
    def get_providers(cls) -> List[Provider]:
        return Meta.query.filter_by(type=const.META_TYPE_PROVIDER).all()

    @classmethod
    def set_businesses(cls, businesses: List[Business]):
        code_2_businesses = dict((business.modelx_code, business) for business in businesses)
        code_2_current_businesses = dict((business.modelx_code, business) for business in cls.get_businesses())

        for code, business in code_2_businesses.items():
            current = code_2_current_businesses.get(code)
            if current:
                if current.name != business.name:
                    # 名称有变化时进行更新
                    logger.info(f'updating name of business({current.id}): '
                                f'{current.name} --> {business.name}.')
                    current.name = business.name

                if current.full_name != business.full_name:
                    # 全称有变化时进行更新
                    logger.info(f'updating fullname of business({current.id}): '
                                f'{current.full_name} --> {business.full_name}.')
                    current.full_name = business.full_name

                if current.modelx_id != business.modelx_id:
                    # 全称有变化时进行更新
                    logger.info(f'updating modelx_id of business({current.id}): '
                                f'{current.modelx_id} --> {business.modelx_id}.')
                    current.other = business.other
            else:
                # 创建新的业务
                created = Business.create(
                    type=const.META_TYPE_BUSINESS,
                    other=business.other,
                    name=business.name,
                    full_name=business.full_name)
                logger.info(f'business created: {created.to_dict()}')

        # 删除不再存在的业务
        for code, current_business in code_2_current_businesses.items():
            if code not in code_2_businesses:
                logger.info(f'deleting business: {current_business.to_dict()}')
                current_business.delete()


repo: Type[IMetaRepo] = MetaRepo
