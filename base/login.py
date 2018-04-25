# -*- coding:utf-8 -*-
import json, requests
from base.base_ajax import BaseApi
from settings import PUBLIC_PASSWORD
from base.base_log import BaseLogger
from base.base_helper import md5
import settings

logging = BaseLogger(__name__).get_logger()


class LoginApi(BaseApi):
    """
    登录接口
    """
    url = '/home/login'

    def login(self, login_name, password=PUBLIC_PASSWORD, only_get_identity=True,channel_id=settings.CHANNEL_ID,device_id=settings.DEVICE_ID):
        sign = md5("platform=android&device_id={0}&channel_id={1}&login_name={2}&password={3}&key=b557936d2fccd9e".format(device_id,channel_id,login_name, password))

        data = {'login_name': login_name, 'password': password, 'device_id': device_id, 'is_debug': '1', 'sign':sign,'channel_id':channel_id,'platform':'android'}

        self.response = requests.get(url=self.api_url(), params=data, headers=settings.AJAX_HEADERS)
        if only_get_identity:
            identity = json.loads(self.response.content)['result']['identity_obj']['identity']
            return identity
        else:
            return self.response