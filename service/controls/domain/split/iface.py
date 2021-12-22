# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod


class IBillPeriodSplitService(metaclass=ABCMeta):
    """ 计费周期分账服务

    根据分账规则，对计费周期内的原始账单进行分账，分账流程如下：

    1. 对于每一条原始账单，尝试与每一条分账规则进行匹配，根据匹配的分数高低，选择所要应用的分账规则
    2. 对于每一条原始账单，使用选中的分账规则进行分账，分账生成一条或多条总账账单
    3. 所有原始账单都处理完成后，汇总所有的总账账单，一次性覆盖计费周期的总账账单

    """
    @classmethod
    @abstractmethod
    def split_original_bills_of_bill_period(cls, bill_period_id: int):
        raise NotImplementedError
