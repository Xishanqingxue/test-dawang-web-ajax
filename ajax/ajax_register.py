# -*- coding:utf-8 -*-
from base.base_ajax import UserBaseAjax


class RegisterAjax(UserBaseAjax):
    """
    注册
    """
    url = '/ajax/head/register'

    def build_custom_param(self, data):
        return {'login_name':data['login_name'],'pass_word':data['pass_word'],'code':data['code'],'check_code':data['check_code'],'jsoncallback':'1'}

