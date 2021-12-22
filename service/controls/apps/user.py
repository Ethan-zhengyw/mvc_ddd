# -*- coding: utf-8 -*-

# 提供以下两种方法以及对应的装饰器
# 1. 用于校验用户是否为指定的角色之一或为管理员
# 2. 用于校验用户是否具有所有指定业务的权限或为管理员

from typing import List
import common.static as const
from ..domain.user.aggr import UserAggr
from common.util.auth import get_user_info
from common.util.api import *****Api, UcUser


def assure_is_admin_or_is_one_of_given_roles(roles: List[const.UserType]):
    """ 校验用户是否为管理员或者为指定的角色之一，不是时抛出异常 """
    user_info = get_user_info()

    if user_info.is_admin:
        return

    uc_user = *****Api.uc_get_user(user_info.id)

    if not uc_user:
        UserAggr.raise_401()

    user_aggr = UserAggr.get_by_email(uc_user.email)
    if not user_aggr:
        UserAggr.raise_401()

    if user_aggr.is_admin:
        return

    # 检查是否为指定的角色之一
    if const.USER_ROLE_COMMERCIAL in roles and user_aggr.is_commercial:
        return

    if const.USER_ROLE_FINANCIAL in roles and user_aggr.is_financial:
        return

    if const.USER_ROLE_BUSINESS in roles and user_aggr.is_business:
        return

    # 用户非管理员，也非指定的角色之一，抛出异常
    user_aggr.raise_403()


def assure_is_admin_or_is_commercial():
    roles = [const.USER_ROLE_COMMERCIAL]
    assure_is_admin_or_is_one_of_given_roles(roles)


def assure_is_admin_or_is_any_roles():
    roles = [const.USER_ROLE_COMMERCIAL, const.USER_ROLE_FINANCIAL, const.USER_ROLE_BUSINESS]
    assure_is_admin_or_is_one_of_given_roles(roles)


def wrap_assure_is_admin_or_is_commercial(func):
    def wrapped(*args, **kwargs):
        assure_is_admin_or_is_commercial()
        return func(*args, **kwargs)
    return wrapped


def wrap_assure_is_admin_or_is_any_roles(func):
    def wrapped(*args, **kwargs):
        assure_is_admin_or_is_any_roles()
        return func(*args, **kwargs)
    return wrapped


class UserApp:
    @classmethod
    def get_uc_org_users(cls) -> List[UcUser]:
        return *****Api.uc_get_users()
