# -*- coding:utf-8 -*-
from base.login_base import LoginBase


class AddSupervisorAjax(LoginBase):
    """
    设置管理
    """
    url = '/ajax/live/addSupervisor'

    def build_custom_param(self, data):
        return {'room_id': data['room_id'], 'anchor_id': data['anchor_id'], 'user_id': data['user_id'],
                'type': data['type']}


class DelSupervisorAjax(LoginBase):
    """
    取消管理
    """
    url = '/ajax/live/delSupervisor'

    def build_custom_param(self, data):
        return {'room_id': data['room_id'], 'anchor_id': data['anchor_id'], 'user_id': data['user_id']}
