# -*- coding:utf-8 -*-
from base.login_base import LoginBase


class LiveSendGift(LoginBase):
    """
    送礼物
    """
    url = '/ajax/live/newSendGift'

    def build_custom_param(self, data):
        return {'room_id': data['room_id'], 'anchor_id': data['anchor_id'], 'gift_id': data['gift_id'],
                'gift_count': data['gift_count'], 'currency': data['currency']}
