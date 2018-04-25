# -*- coding:utf-8 -*-
from base.login_api import LoginApi
from base.base_ajax import BaseAjax
from base.base_log import BaseLogger
import settings
import requests

logger = BaseLogger(__name__).get_logger()

class LoginBaseApi(BaseAjax):

    def __init__(self, login_name,password=settings.PUBLIC_PASSWORD ,*args, **kwargs):
        super(LoginBaseApi, self).__init__(*args,**kwargs)
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
        identity = self.get_identity()
        request_data = self.format_param(data)
        logger.info('Data:{0}'.format(request_data))
        s = requests.session()
        s.cookies.set('identity', identity)
        self.response = s.get(url=self.api_url(), params=request_data, headers=self.headers)
        logger.info('Headers:{0}'.format(self.response.request.headers))
        logger.info('Response:{0}'.format(self.response.text))
        return self.response



