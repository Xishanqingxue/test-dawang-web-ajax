# -*- coding:utf-8 -*-
from base.login_base import LoginBase


class UserGetSunAjax(LoginBase):
    """
    获取太阳
    """
    url = '/ajax/live/userGetSun'

    def build_custom_param(self, data):
        return {'room_id':data['room_id'],'anchor_id':data['anchor_id']}