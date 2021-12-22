# -*- coding: utf-8 -*-

from typing import List, Optional
from .repo import repo


class MetaSpec:
    def __init__(self, businesses: List[str], bill_subjects: List[str], providers: List[str]):
        self.__businesses = businesses
        self.__bill_subjects = bill_subjects
        self.__providers = providers

    @property
    def businesses(self) -> List[str]:
        return self.__businesses

    def is_business_valid(self, business: str) -> (bool, Optional[str]):
        if not business:
            return True, None
        elif business in self.__businesses:
            return True, None
        else:
            return False, f'业务名称"{business}"非法，参考值：{"、".join(self.__businesses[:3])}...'

    def is_bill_subject_valid(self, bill_subject: str) -> (bool, Optional[str]):
        if bill_subject in self.__bill_subjects:
            return True, None
        else:
            return False, f'计费主体名称"{bill_subject}"非法，参考值：{"、".join(self.__bill_subjects[:3])}...'

    def is_provider_valid(self, provider: str) -> (bool, Optional[str]):
        if provider in self.__providers:
            return True, None
        else:
            return False, f'供应商名称"{provider}"非法，参考值：{"、".join(self.__providers[:3])}...'


def meta_spec() -> MetaSpec:
    businesses = [o.modelx_code for o in repo.get_businesses()]
    bill_subjects = [o.name for o in repo.get_bill_subjects()]
    providers = [o.name for o in repo.get_providers()]
    return MetaSpec(businesses, bill_subjects, providers)
