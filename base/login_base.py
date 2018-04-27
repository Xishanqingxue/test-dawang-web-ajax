# -*- coding:utf-8 -*-
from base.login import LoginApi
from base.base_ajax import BaseAjax
from base.base_log import BaseLogger
import settings
import requests
import json

logger = BaseLogger(__name__).get_logger()

class LoginBase(BaseAjax):

    def __init__(self, login_name,password=settings.PUBLIC_PASSWORD ,*args, **kwargs):
        super(LoginBase, self).__init__(*args,**kwargs)
        self.password = password
        self.login_name = login_name

    def get_identity(self):
        identity = LoginApi().login(self.login_name, self.password, only_get_identity=True)
        return identity

    def get(self, data=None):
        """
        请求方式：GET
        :param data:
        :return:
        """
        num = 1
        while num <= 3:
            logger.info('The {0} request.'.format(num))
            identity = self.get_identity()
            request_data = self.format_param(data)
            s = requests.session()
            s.cookies.set('identity', identity)
            self.response = s.get(url=self.api_url(), params=request_data, headers=self.headers)
            if int(json.loads(self.response.text)['code']) != 100002:
                break
            else:
                num += 1
            logger.info('Headers:{0}'.format(self.response.request.headers))
            logger.info('Response:{0}'.format(self.response.text))
        return self.response

class UserLoginBase(LoginBase):
    base_url = settings.USER_TEST_BASE_URL

class H5LoginBase(LoginBase):
    base_url = settings.H5_TEST_BASE_URL



