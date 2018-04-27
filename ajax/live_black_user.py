# -*- coding:utf-8 -*-
from base.login_base import LoginBase


class AddBlackUserAjax(LoginBase):
    """
    添加黑名单
    """
    url = '/ajax/live/addBlackUser'

    def build_custom_param(self, data):
        return {'room_id': data['room_id'], 'anchor_id': data['anchor_id'], 'user_id': data['user_id'],
                'blacker_type': data['blacker_type']}


class DelBlackUserAjax(LoginBase):
    """
    解除黑名单
    """
    url = '/ajax/live/delBlackUser'

    def build_custom_param(self, data):
        return {'room_id': data['room_id'], 'anchor_id': data['anchor_id'], 'user_id': data['user_id'],
                'blacker_type': data['blacker_type']}