# -*- coding:utf-8 -*-
from base.login_base import UserLoginBase


class ConsumptionAjax(UserLoginBase):
    """
    消费记录
    """
    url = '/ajax/user/consumption'