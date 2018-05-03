# -*- coding:utf-8 -*-
from ajax.user_image_code import ImageCodeAjax
from base.login import LoginApi
from ajax.user_send_sms import SendSmsAjax
from ajax.ajax_register import RegisterAjax
from utilities.redis_helper import Redis,RedisHold
from utilities.mysql_helper import MysqlOperation
from base.base_case import BaseCase
import settings
import random


class TestRegisterAjax(BaseCase):
    """
    注册
    """
    mobile = '1330606' + str(random.randint(1111,9999))


    def test_register_success(self):
        """
        测试注册成功
        :return:
        """
        image_code_ajax = ImageCodeAjax()
        image_code_ajax.get()

        image_code = Redis().get_image_captcha(settings.CLIENT_IDENTITY)
        sms_code_ajax = SendSmsAjax()
        sms_code_ajax.get({'phone':self.mobile,'type':'register','check_code':image_code})
        self.assertEqual(sms_code_ajax.get_resp_code(),0)

        sms_code = MysqlOperation(mobile=self.mobile).get_sms_code()
        register_ajax = RegisterAjax()
        register_ajax.get({'login_name':self.mobile,'pass_word':'eJwrSS0uMTQyNgEADVUCiw==','code':sms_code,'check_code':image_code})

        login_identity = LoginApi().login(login_name=self.mobile,password='test1234',only_get_identity=True)
        self.assertEqual(len(login_identity),236)


    def tearDown(self, user_id=None, anchor_id=None):
        super(TestRegisterAjax,self).tearDown()
        RedisHold().clean_redis_user_detail(MysqlOperation(mobile=self.mobile).get_user_id())
        Redis().clean_user_bean(MysqlOperation(mobile=self.mobile).get_user_id())
        MysqlOperation(mobile=self.mobile).delete_user()