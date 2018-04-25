# -*- coding:utf-8 -*-
import time

TEST_ENV = 'test'

# APP版本号
APP_VERSION = '2.6.3'
CHANNEL_ID = '10180001'
DEVICE_ID = 'Auto-Test-Device-ID'
# Case失败后重试次数
CASE_FAILED_RETRY_TIMES = 1

# 请求HEADERS配置
API_HEADERS = {'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'}
AJAX_HEADERS = {'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest'}

# 测试地址域名
WEB_TEST_BASE_URL = "http://www.t.dwtv.tv"
USER_TEST_BASE_URL = "http://user.t.dwtv.tv"
PAY_TEST_BASE_URL = "http://pay.t.dwtv.tv"
HELPER_TEST_BASE_URL = 'http://helper.t.dwtv.tv'
CMS_TEST_BASE_URL = 'http://cms-api.dwtv.tv'
GAME_CENTER_TEST_BASE_URL = 'https://hall.game.dwtv.tv'

API_TEST_BASE_URL = "https://yl.t.dwtv.tv"
AJAX_TEST_BASE_URL = "http://n.www.dwtv.tv/"

# 测试环境Redis配置信息
REDIS_CONFIG = {'host': '172.23.15.10', 'port': 6379}
HOLD_REDIS_CONFIG = {'host': 'hold.redis.dawang.tv', 'port': 6379}
# 测试环境Mysql配置
DB_CONFIG = {'host': 'master.db.dawang.tv', 'port': 3306, 'user': 'live', 'password': '1oRKgbLB9AnLK'}

# 邮件配置
MAIL_SERVER = 'smtp.163.com'
MAIL_FROM = '13501077762@163.com'
MAIL_FROM_PASSWORD = 'yinglong123'
MAIL_HEADER = '自动化测试结果'
MAIL_TO = ['gaoyinglong@kong.net','liulei@kong.net']
# MAIL_TO = ['gaoyinglong@kong.net', 'liulei@kong.net', 'xiongliyao@kong.net', 'liuxiwang@kong.net', 'wangqun@kong.net']

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


SETTING_LOCAL_DIR = os.path.join(BASE_DIR, "settings_local.py")
if os.path.exists(SETTING_LOCAL_DIR):
    execfile(SETTING_LOCAL_DIR)

# 测试报告配置
RESULT_HTML_DIR = './result'
RESULT_TITLE = '大王娱乐接口自动化测试报告'
RESULT_FILE_NAME = 'result.html'
RESULT_DESCRIPTION = '用例执行情况详情如下(已将错误用例数计算到失败用例数中，并隐藏错误用例查询):'

DOLL_RESULT_TITLE = '大王娱乐娃娃机接口自动化测试报告'
DOLL_RESULT_FILE_NAME = 'result_doll.html'

# 测试目录配置
API_TEST_CASE_DIR = ['./test_case/api_test_case/']
GAME_TEST_CASE_DIR = ['./test_case/game/']
TOP_LEVEL_DIR = os.path.abspath('./test_case')
DOLL_TOP_LEVEL_DIR = os.path.abspath('./test_case/test_doll_api')
DOLL_TEST_CASE_DIR = ['./test_case/test_doll_api/']

# local debugging config
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTING_LOCAL_DIR = os.path.join(BASE_DIR, "settings_local.py")
if os.path.exists(SETTING_LOCAL_DIR):
    execfile(SETTING_LOCAL_DIR)


# 测试账户配置
PUBLIC_PASSWORD = '123abc'
PUBLIC_PASSWORD_MD5 = 'eb4f76fecca2893c1036dd0779698cd9'

YULE_TEST_USER_LOGIN_NAME = '13877777777'
YULE_TEST_USER_ID = '22013877'
YULE_TEST_ANCHOR_LOGIN_NAME = '13199067061'
YULE_TEST_ANCHOR_ID = '20001795'
YULE_TEST_ROOM = '123200'
YULE_TEST_GAME_ANCHOR_LOGIN_NAME = '15710607010'
YULE_TEST_GAME_ANCHOR_ID = '20059012'
YULE_TEST_GAME_ROOM = '123484'
YULE_DOLL_TEST_ROOM = '125092'
# 日志配置
SNAPSHOT_DIRECTORY = os.path.abspath('./logs')
LOG_FILE_PATH = SNAPSHOT_DIRECTORY + time.strftime("%Y_%m_%d_%H_%M_%S") +'_' + 'api.log'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'
