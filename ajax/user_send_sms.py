# -*- coding:utf-8 -*-
from base.base_ajax import UserBaseAjax


class SendSmsAjax(UserBaseAjax):
    """
    短信验证码
    """
    url = '/ajax/head/sendSms'

    def build_custom_param(self, data):
        return {'phone':data['phone'],'type':data['type'],'check_code':data['check_code']}