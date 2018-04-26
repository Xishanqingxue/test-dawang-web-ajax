# -*- coding:utf-8 -*-
import os
import time

ENV = 'test'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTING_LOCAL = os.path.join(BASE_DIR, "settings_local.py")
if os.path.exists(SETTING_LOCAL):
    with open(SETTING_LOCAL, 'r') as f:
        exec(f.read())

AJAX_TEST_BASE_URL = 'http://n.www.dwtv.tv'
PIC_TEST_BASE_URL = 'http://pic.t.dwtv.tv/files'
USER_TEST_BASE_URL = 'http://n.user.dwtv.tv'

# 请求HEADERS配置
AJAX_HEADERS = {'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest'}

# 日志配置
now_time = time.strftime("%Y_%m_%d_%H_%M_%S")
LOG_DIR_PATH = os.path.join(BASE_DIR,'log')
if not os.path.exists(LOG_DIR_PATH):
    os.mkdir('../log')
LOG_FILE_NAME = './log/{0}_log.txt'.format(now_time)
LOG_FORMATTER = "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"

# 测试报告配置
REPORT_DIR_PATH = os.path.join(BASE_DIR,'result')
if not os.path.exists(REPORT_DIR_PATH):
    os.mkdir('../result')
REPORT_FILE_NAME = './result/' + time.strftime("%Y%m%d%H%M%S") + '_result.html'
REPORT_TITLE = 'Web接口自动化测试报告'
REPORT_DESCRIPTION = '用例执行情况详情如下:'
REPORT_TESTER = '大王直播测试组'

# 邮件配置
MAIL_SERVER = 'smtp.163.com'
MAIL_FROM = '13501077762@163.com'
MAIL_FROM_PASSWORD = 'yinglong123'
MAIL_HEADER = 'Automated test report'
MAIL_TO = 'gaoyinglong@kong.net'

# Mysql配置
TEST_MYSQL_CONFIG = {'host': 'master.db.dawang.tv', 'port': 3306, 'user': 'live', 'password': '1oRKgbLB9AnLK'}
TEST_DEFAULT_DB = 'live_core'
LOCAL_MYSQL_CONFIG = {'host': '127.0.0.1', 'port': 3306, 'user': 'root', 'password': 'admin'}
LOCAL_DEFAULT_DB = 'auto_test'

# Redis配置
REDIS_CONFIG = {'host': '172.23.15.10', 'port': 6379}
HOLD_REDIS_CONFIG = {'host': 'hold.redis.dawang.tv', 'port': 6379}

# 测试账户配置
PUBLIC_PASSWORD = '123abc'
PUBLIC_PASSWORD_MD5 = 'eb4f76fecca2893c1036dd0779698cd9'

TEST_USER_MOBILE = '13308080808'
TEST_USER_ID = '22017475'
TEST_ANCHOR_MOBILE = '18611050220'
TEST_ANCHOR_ID = '20000442'
TEST_ROOM = '123176'
