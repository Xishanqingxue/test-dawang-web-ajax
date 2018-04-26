# -*- coding:utf-8 -*-
from base.login_base import LoginBase


class BuyNobleAjax(LoginBase):
    """
    购买贵族
    """
    url = '/ajax/live/purchaseNoble'

    def build_custom_param(self, data):
        return {'room_id': data['room_id'], 'anchor_id': data['anchor_id'], 'noble_id': data['noble_id'],
                'num': data['num'], 'currency': data['currency']}
