# -*- coding:utf-8 -*-
from base.login_base import LoginBase



class LiveAjax(LoginBase):
    """
    房间信息
    """
    url = '/ajax/live/newServer'


    def build_custom_param(self, data):
        return {'room_id':data['room_id']}