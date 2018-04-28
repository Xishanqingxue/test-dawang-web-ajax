# -*- coding:utf-8 -*-
from ajax.user_image_code import ImageCodeAjax
from utilities.redis_helper import Redis
from base.base_case import BaseCase
import settings


class TestImageCodeAjax(BaseCase):
    """
    图形验证码
    """


    def test_get_image_code_success(self):
        """
        测试获取图形验证码成功
        :return:
        """
        image_code_ajax = ImageCodeAjax()
        image_code_ajax.get()

        image_code = Redis().get_image_captcha(settings.CLIENT_IDENTITY)
        self.assertEqual(len(image_code),4)