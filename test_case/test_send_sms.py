# -*- coding:utf-8 -*-
from ajax.user_image_code import ImageCodeAjax
from ajax.user_send_sms import SendSmsAjax
from utilities.redis_helper import Redis
from utilities.mysql_helper import MysqlOperation
from base.base_case import BaseCase
import settings
import random


class TestSendSmsAjax(BaseCase):
    """
    短信验证码
    """
    mobile = '1330606' + str(random.randint(1111,9999))


    def test_get_sms_code_success(self):
        """
        测试获取短信验证码成功
        :return:
        """
        image_code_ajax = ImageCodeAjax()
        image_code_ajax.get()

        image_code = Redis().get_image_captcha(settings.CLIENT_IDENTITY)
        sms_code_ajax = SendSmsAjax()
        sms_code_ajax.get({'phone':self.mobile,'type':'register','check_code':image_code})
        self.assertEqual(sms_code_ajax.get_resp_code(),0)

        sms_code = MysqlOperation(mobile=self.mobile).get_sms_code()
        self.assertEqual(len(sms_code),4)

    def test_get_sms_code_mobile_null(self):
        """
        测试获取短信验证码手机号为空
        :return:
        """
        image_code_ajax = ImageCodeAjax()
        image_code_ajax.get()

        image_code = Redis().get_image_captcha(settings.CLIENT_IDENTITY)
        sms_code_ajax = SendSmsAjax()
        sms_code_ajax.get({'phone':None,'type':'register','check_code':image_code})
        self.assertEqual(sms_code_ajax.get_resp_code(),400101)
        self.assertEqual(sms_code_ajax.get_resp_message(),'手机号不能为空')

    def test_get_sms_code_mobile_error(self):
        """
        测试获取短信验证码手机号格式错误
        :return:
        """
        image_code_ajax = ImageCodeAjax()
        image_code_ajax.get()

        image_code = Redis().get_image_captcha(settings.CLIENT_IDENTITY)
        sms_code_ajax = SendSmsAjax()
        sms_code_ajax.get({'phone':'1234','type':'register','check_code':image_code})
        self.assertEqual(sms_code_ajax.get_resp_code(),400126)
        self.assertEqual(sms_code_ajax.get_resp_message(),'手机号格式不合法')

    def test_get_sms_code_type_null(self):
        """
        测试获取短信验证码类型为空
        :return:
        """
        image_code_ajax = ImageCodeAjax()
        image_code_ajax.get()

        image_code = Redis().get_image_captcha(settings.CLIENT_IDENTITY)
        sms_code_ajax = SendSmsAjax()
        sms_code_ajax.get({'phone':self.mobile,'type':None,'check_code':image_code})
        self.assertEqual(sms_code_ajax.get_resp_code(),400111)
        self.assertEqual(sms_code_ajax.get_resp_message(),'短信类型不能为空')


    def test_get_sms_code_type_error(self):
        """
        测试获取短信验证码类型为空
        :return:
        """
        image_code_ajax = ImageCodeAjax()
        image_code_ajax.get()

        image_code = Redis().get_image_captcha(settings.CLIENT_IDENTITY)
        sms_code_ajax = SendSmsAjax()
        sms_code_ajax.get({'phone':self.mobile,'type':'123','check_code':image_code})
        self.assertEqual(sms_code_ajax.get_resp_code(),400136)
        self.assertEqual(sms_code_ajax.get_resp_message(),'请求参数错误')

    def test_get_sms_code_image_code_null(self):
        """
        测试获取短信验证码图形验证码为空
        :return:
        """
        sms_code_ajax = SendSmsAjax()
        sms_code_ajax.get({'phone':self.mobile,'type':'register','check_code':None})
        self.assertEqual(sms_code_ajax.get_resp_code(),801002)
        self.assertEqual(sms_code_ajax.get_resp_message(),'验证码错误,请重新输入')


    def test_get_sms_code_image_code_error(self):
        """
        测试获取短信验证码图形验证码错误
        :return:
        """
        image_code_ajax = ImageCodeAjax()
        image_code_ajax.get()

        sms_code_ajax = SendSmsAjax()
        sms_code_ajax.get({'phone':self.mobile,'type':'register','check_code':'1234'})
        self.assertEqual(sms_code_ajax.get_resp_code(),422107)
        self.assertEqual(sms_code_ajax.get_resp_message(),'验证码错误,请重新输入')
