# -*- coding:utf-8 -*-
from base.login_base import LoginBase


class BuyGuardAjax(LoginBase):
    """
    购买守护
    """
    url = '/ajax/live/purchaseGuard'

    def build_custom_param(self, data):
        return {'room_id': data['room_id'], 'guard_id': data['guard_id'], 'currency': data['currency']}
