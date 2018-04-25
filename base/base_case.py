# -*- coding:utf-8 -*-
from unittest import TestCase
from base.base_log import BaseLogger
from base.base_helper import generate_random_nickname


logger = BaseLogger(__name__).get_logger()


class BaseCase(TestCase):
    """
    1、手机号在上层继承该类时重新定义
    2、随机生成一个默认5个汉字的用户昵称，也可重新定义指定昵称
    """
    union_id = ''
    # init_user=False
    # nickname = generate_random_nickname(words=5)
    # api_id = ''
    # test_module = ''
    #
    # @classmethod
    # def setUpClass(cls):
    #     """
    #     类方法：初始化新用户信息(注册流程)
    #     :param init:
    #     :return:
    #     """
    #     # count = 1
    #     # max_count = 10
    #     # if cls.init_user:
    #     #     logger.info('Initializing the user.')
    #     #     ImageCodeApi().get()
    #     #     image_code = Redis().get_image_captcha()
    #     #     logger.info('Image code is {0}.'.format(image_code))
    #     #
    #     #     send_sms_code_api = SendSmsCodeApi()
    #     #     resp = send_sms_code_api.get({'type': 'register', 'phone': cls.user_mobile,'check_code': image_code})
    #     #     try:
    #     #         assert send_sms_code_api.get_resp_code() == 0
    #     #     except AssertionError:
    #     #         logger.error('Send sms code failed.')
    #     #         logger.error('Send sms api response:{0}'.format(json.loads(resp.content)))
    #     #     logger.info('Send sms code successful.')
    #     #     sms_code = None
    #     #     while count < max_count:
    #     #         sms_code = MysqlOperation(mobile=cls.user_mobile).get_sms_code()
    #     #         if sms_code:
    #     #             break
    #     #         else:
    #     #             time.sleep(0.5)
    #     #             count+=1
    #     #     assert count < max_count
    #     #     logger.info('Sms code is {0}.'.format(sms_code))
    #     #
    #     #     try:
    #     #         register_api = RegisterApi()
    #     #         resp = register_api.get({'login_name': cls.user_mobile, 'code': sms_code,'nickname': cls.nickname})
    #     #         assert register_api.get_resp_code() == 0
    #     #         logger.info('User initialization is successful.')
    #     #     except AssertionError:
    #     #         logger.error('User initialization failed.')
    #     #         logger.error('Register api response:{0}'.format(json.loads(resp.content)))
    #     # else:
    #     #     logger.info('There is no need to initialize user information.')
    #     # time.sleep(0.5)
    #     pass
    #
    # @classmethod
    # def tearDownClass(cls):
    #     """
    #     类方法：清除用户信息
    #     :return:
    #     """
    #     # logger.info('Deleting user information.')
    #     # user_id = MysqlOperation(mobile=cls.user_mobile).get_user_id()
    #     # MysqlOperation(user_id=user_id,mobile=cls.user_mobile).delete_user()
    #     # RedisHold().clean_redis_user_detail(user_id)
    #     # logger.info('Delete user information complete.')
    #     # time.sleep(0.5)
    #     pass