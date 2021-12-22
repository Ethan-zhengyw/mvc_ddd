# -*- coding: utf-8 -*-
# App负责编排领域服务或者聚合根，实现业务功能
# 在MVC框架下DDD：
#   * 视图依然只调用控制器
#   * App组合到MVC框架中的控制器中
#   * 视图通过控制器间接调用APP


from .bill import *
from .meta import *
from .bill_period import *
from .user import *
