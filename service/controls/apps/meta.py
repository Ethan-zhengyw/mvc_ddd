# -*- coding: utf-8 -*-

import json
from typing import List

import common.static as const
from common.util.api import *****Api, ModelXBusiness
from ..domain.meta.entity import Business
from ..domain.meta.repo import repo
from common.util.log import get_logger


logger = get_logger('app:meta')


class BusinessApp:
    @classmethod
    def sync(cls):
        """ 执行同步操作 """
        logger.debug(f'start synchronizing business.')
        modelx_businesses = cls.__fetch_modelx_business()
        logger.debug(f'generated modelx businesses: {json.dumps(modelx_businesses)}.')

        business_entities = [
            cls.__convert_modelx_business_2_business_entity(modelx_business)
            for modelx_business in modelx_businesses]

        repo.set_businesses(business_entities)
        logger.debug(f'business synchronized.')

    @classmethod
    def __fetch_modelx_business(cls) -> List[ModelXBusiness]:
        """ 从modelx读取业务数据 """
        return *****Api.modelx_get_businesses()

    @staticmethod
    def __convert_modelx_business_2_business_entity(modelx_business: ModelXBusiness) -> Business:
        business_entity = Business()
        business_entity.type = const.META_TYPE_BUSINESS
        business_entity.other = dict(
            modelx_code=modelx_business.code,
            modelx_id=modelx_business.id)
        business_entity.name = modelx_business.name
        business_entity.full_name = modelx_business.full_name
        return business_entity
