# -*- coding:utf-8 -*-
from base.login_base import LoginBase


class BuySunAjax(LoginBase):
    """
    购买太阳
    """
    url = '/ajax/live/buySun'

    def build_custom_param(self, data):
        return {'room_id':data['room_id'],'anchor_id':data['anchor_id']}