# -*- coding: utf-8 -*-

from werkzeug.exceptions import Forbidden, Unauthorized

common_401_exception = Unauthorized("系统未查询到您的用户信息，如有疑问，请联系管理员处理。")
common_403_exception = Forbidden("您缺少执行该操作所需的权限，如有疑问，请联系管理员处理。")
