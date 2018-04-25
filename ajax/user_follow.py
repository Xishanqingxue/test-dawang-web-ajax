# -*- coding:utf-8 -*-
from base.login_base import LoginBase


class AddFollowAjax(LoginBase):
    """
    关注主播
    """
    url = '/ajax/user/addFollowing'

    def build_custom_param(self, data):
        return {'room_id': data['room_id'], 'anchor_id': data['anchor_id']}


class RelieveFollowAjax(LoginBase):
    """
    取消关注
    """
    url = '/ajax/user/relieveFollowing'

    def build_custom_param(self, data):
        return {'room_id': data['room_id'], 'anchor_id': data['anchor_id']}
