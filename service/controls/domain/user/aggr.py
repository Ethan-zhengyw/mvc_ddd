# -*- coding: utf-8 -*-

from typing import List, Optional

from .entity import User
from .exception import *


class UserAggr:
    def __init__(self, user: User):
        self.__user = user

    @property
    def is_admin(self):
        return self.__user.is_admin

    @property
    def is_commercial(self):
        return self.__user.is_commercial

    @property
    def is_financial(self):
        return self.__user.is_financial

    @property
    def is_business(self):
        return self.__user.is_business

    @classmethod
    def get_by_email(cls, email: str) -> Optional["UserAggr"]:
        user = User.query.filter_by(email=email).first()
        if user:
            return cls(user)
        else:
            return None

    @classmethod
    def get_by_email_or_404(cls, email: str) -> "UserAggr":
        aggr = cls.get_by_email(email)
        if aggr:
            return aggr
        else:
            cls.raise_401()

    def assure_has_permission_of_all_given_business_ids(self, business_ids: List[int]) -> bool:
        """ 检查用户是否具有所有给定业务的权限，如果没有，则抛出权限异常 """
        if self.is_admin or self.is_commercial or self.is_financial:
            return True
        elif self.__has_permission_of_all_given_business_ids(business_ids):
            return True
        else:
            self.raise_403()

    @staticmethod
    def raise_401():
        raise common_401_exception

    @staticmethod
    def raise_403():
        raise common_403_exception

    def __has_permission_of_all_given_business_ids(self, business_ids: List[int]) -> bool:
        return self.__user.has_permission_of_all_given_business_ids(business_ids)
